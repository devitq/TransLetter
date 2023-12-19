from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.translation import pgettext_lazy
from django.views.generic import DetailView, ListView, View

from resume.models import ResumeFile
from translator_request.forms import (
    RejectRequestForm,
    RequestTranslatorForm,
    RequestTranslatorFormDisabled,
)
from translator_request.models import (
    TranslatorRequest,
    TranslatorRequestStatusLog,
)
from transletter.email import EmailThread

__all__ = ()

STATUS_CHOICES = {
    "SE": "Sent",
    "UR": "Under review",
    "AC": "Accepted",
    "RJ": "Rejected",
}


class RequestTranslatorView(LoginRequiredMixin, View):
    template_name = "translator_request/request_translator.html"
    success_url = reverse_lazy("translator_request:request_translator")

    def get(self, request):
        initial_languages = request.user.account.languages
        try:
            request_status = request.user.translator_request.status
            resume = request.user.resume
        except Exception:
            request_status = "NN"
            resume = None
        if request_status in "SERJACNN":
            form = RequestTranslatorForm(
                instance={
                    "user_form": request.user,
                    "account_form": request.user.account,
                    "resume_form": resume,
                },
                initial={
                    "account_form": {"languages": initial_languages},
                    "resume_form": {
                        "about": resume.about
                        if resume
                        else request.user.account.about or None,
                    },
                },
            )
        else:
            form = RequestTranslatorFormDisabled(
                instance={
                    "user_form": request.user,
                    "account_form": request.user.account,
                    "resume_form": resume or None,
                },
                initial={
                    "account_form": {"languages": initial_languages},
                    "resume_form": {
                        "about": resume.about
                        if resume
                        else request.user.account.about or None,
                    },
                },
            )
        return render(
            request,
            template_name=self.template_name,
            context={
                "form": form,
                "request_status": request_status,
                "resume": resume,
            },
        )

    def post(self, request):
        form = RequestTranslatorForm(request.POST, request.FILES)

        try:
            request_status = request.user.translator_request.status
        except Exception:
            request_status = "NN"

        if form.is_valid() and request_status in "SERJACNN":
            resume = form["resume_form"]
            files = request.FILES.getlist("files_form-file")

            request.user.first_name = form["user_form"].cleaned_data[
                "first_name"
            ]
            request.user.last_name = form["user_form"].cleaned_data[
                "last_name"
            ]
            request.user.save()

            if hasattr(request.user, "resume"):
                request.user.resume.about = resume.cleaned_data[
                    "about"
                ]
                request.user.resume.save()
                resume = request.user.resume
            else:
                resume.instance.user = request.user
                resume = resume.save()

            account_form = form["account_form"]
            request.user.resume = resume
            request.user.save()
            request.user.account.languages = account_form.cleaned_data[
                "languages"
            ]
            request.user.account.native_lang = account_form.cleaned_data[
                "native_lang"
            ]
            request.user.account.save()

            if hasattr(request.user, "translator_request"):
                if request_status != "AC":
                    request.user.translator_request.status = "SE"
                request.user.translator_request.save()
                messages.success(
                    request,
                    pgettext_lazy(
                        "translator request update success",
                        "Your request to become a translator has been updated",
                    ),
                )
            else:
                TranslatorRequest.objects.create(
                    user=request.user,
                )
                messages.success(
                    request,
                    pgettext_lazy(
                        "translator request create success",
                        "Your request to become a translator has been sent",
                    ),
                )

            for file in files:
                ResumeFile.objects.create(
                    resume=request.user.resume,
                    file=file,
                )

            return redirect(reverse("translator_request:request_translator"))

        messages.error(
            request,
            pgettext_lazy(
                "translator request on review error",
                "Your request is currently under review.",
            ),
        )

        return render(
            request,
            template_name=self.template_name,
            context={"form": form},
        )


class TranslatorRequestsView(LoginRequiredMixin, ListView):
    template_name = "translator_request/translator_requests.html"
    paginate_by = 10
    model = TranslatorRequest

    def get_queryset(self):
        return TranslatorRequest.objects.for_staff().order_by("-id")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm(
            "translator_request.view_translatorrequest",
        ):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class TranslatorRequestView(LoginRequiredMixin, DetailView):
    template_name = "translator_request/translator_request.html"
    model = TranslatorRequest
    context_object_name = "translator_request"

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm(
            "translator_request.view_translatorrequest",
        ):
            raise PermissionDenied()
        item = self.get_object()
        form = RejectRequestForm(request.POST)
        if item.status == "SE":
            item.status = "UR"
            TranslatorRequestStatusLog.objects.create(
                user=request.user,
                translator_request=item,
                from_status="SE",
                to="UR",
            )
            text = (
                f"Hello, {item.user.username}, our team has taken your "
                "request under review, expect further updates soon."
            )
            link = request.build_absolute_uri(
                reverse(
                    "translator_request:request_translator",
                ),
            )
            email_body = render_to_string(
                "translator_request/email/status_change.html",
                {
                    "text": text,
                    "link": link,
                },
            )
            email = EmailMultiAlternatives(
                subject="Translator Request Status Change - TransLetter",
                body=email_body,
                from_email=settings.EMAIL,
                to=[item.user.email],
            )
            email.attach_alternative(email_body, "text/html")
            EmailThread(email).start()
            item.save()
        return render(
            request,
            template_name=self.template_name,
            context={"translator_request": item, "form": form},
        )


class AcceptRequestView(LoginRequiredMixin, DetailView):
    model = TranslatorRequest
    context_object_name = "translator_request"

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm(
            "translator_request.edit_translatorrequest",
        ):
            raise PermissionDenied()
        item = self.get_object()
        TranslatorRequestStatusLog.objects.create(
            user=request.user,
            translator_request=item,
            from_status=item.status,
            to="AC",
        )
        text = (
            f"Hello, {item.user.username}, your translator "
            "request has been successfully accepted! "
        )
        link = request.build_absolute_uri(
            reverse(
                "translator_request:request_translator",
            ),
        )
        email_body = render_to_string(
            "translator_request/email/status_change.html",
            {
                "text": text,
                "link": link,
            },
        )
        email = EmailMultiAlternatives(
            subject="Translator Request Status Change - TransLetter",
            body=email_body,
            from_email=settings.EMAIL,
            to=[item.user.email],
        )
        email.attach_alternative(email_body, "text/html")
        EmailThread(email).start()
        item.status = "AC"
        item.user.account.is_translator = True
        item
        item.user.account.save()
        item.save()
        return redirect(reverse("translator_request:translator_requests"))


class RejectRequestView(LoginRequiredMixin, DetailView):
    model = TranslatorRequest
    context_object_name = "translator_request"

    def get(self, request, *args, **kwargs):
        if not request.user.has_perm(
            "translator_request.edit_translatorrequest",
        ):
            raise PermissionDenied()
        item = self.get_object()
        blocked = request.GET.get("block", False)
        TranslatorRequestStatusLog.objects.create(
            user=request.user,
            translator_request=item,
            from_status=item.status,
            to="RJ",
        )
        text = (
            f"Hello, {item.user.username}, your request has been "
            "rejected, our team has deemed you incompetent."
        )
        link = request.build_absolute_uri(
            reverse(
                "translator_request:request_translator",
            ),
        )
        email_body = render_to_string(
            "translator_request/email/status_change.html",
            {
                "text": text,
                "link": link,
            },
        )
        email = EmailMultiAlternatives(
            subject="Translator Request Status Change - TransLetter",
            body=email_body,
            from_email=settings.EMAIL,
            to=[item.user.email],
        )
        email.attach_alternative(email_body, "text/html")
        EmailThread(email).start()
        item.status = "RJ"
        item.user.account.is_translator = False
        if blocked:
            item.user.account.blocked = True
            item.user.account.blocked_reason = "Spam"
        item.user.account.save()
        item.save()
        return redirect(reverse("translator_request:translator_requests"))
