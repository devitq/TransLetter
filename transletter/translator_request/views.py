from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import redirect, render
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
        except Exception:
            request_status = "NN"
        if request_status in "SERJACNN":
            form = RequestTranslatorForm(
                instance={
                    "account_form": request.user.account,
                    "resume_form": request.user.account.resume or None,
                },
                initial={
                    "account_form": {"languages": initial_languages},
                    "resume_form": {
                        "about": request.user.account.resume.about
                        if request.user.account.resume
                        else request.user.account.about or None,
                    },
                },
            )
        else:
            form = RequestTranslatorFormDisabled(
                instance={
                    "account_form": request.user.account,
                    "resume_form": request.user.account.resume or None,
                },
                initial={
                    "account_form": {"languages": initial_languages},
                    "resume_form": {
                        "about": request.user.account.resume.about
                        if request.user.account.resume
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
            },
        )

    def post(self, request):
        form = RequestTranslatorForm(request.POST, request.FILES)
        try:
            request_status = request.user.translator_request.status
        except Exception:
            request_status = "NN"
        if form.is_valid() and request_status in "SERJACNN":
            resume = form["resume_form"].save()
            files = request.FILES.getlist("files_form-file")
            for file in files:
                ResumeFile.objects.create(resume=resume, file=file)
            if request.user.account.resume:
                request.user.account.resume.delete()
            account_form = form["account_form"]
            request.user.account.resume = resume
            request.user.account.languages = account_form.cleaned_data[
                "languages"
            ]
            request.user.account.native_lang = account_form.cleaned_data[
                "native_lang"
            ]
            request.user.account.save()
            if hasattr(request.user, "translator_request"):
                request.user.translator_request.resume = resume
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
                    resume=resume,
                )
                messages.success(
                    request,
                    pgettext_lazy(
                        "translator request create success",
                        "Your request to become a translator has been sent",
                    ),
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
    context_object_name = "translator_requests"

    def get_queryset(self):
        return TranslatorRequest.objects.for_staff()

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
        item = self.get_object()
        form = RejectRequestForm(request.POST)
        if not request.user.has_perm(
            "translator_request.view_translatorrequest",
        ):
            raise PermissionDenied()
        if item.status == "SE":
            item.status = "UR"
            TranslatorRequestStatusLog.objects.create(
                user=request.user,
                translator_request=item,
                from_status="SE",
                to="UR",
            )
            fr_status = STATUS_CHOICES["SE"]
            to_status = STATUS_CHOICES["UR"]
            text = f"""Status was change from '{fr_status}' to '{to_status}'
Your request is currently under review"""
            send_mail(
                "Change Translator Request Status",
                text,
                settings.EMAIL,
                [request.user.email],
                fail_silently=False,
            )
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
        fr_status = STATUS_CHOICES[item.status]
        to_status = STATUS_CHOICES["AC"]
        text = f"""Status was change from '{fr_status}' to '{to_status}'
Your request has been accepted"""
        send_mail(
            "Change Translator Request Status",
            text,
            settings.EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        item.status = "AC"
        item.user.account.is_translator = True
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
        fr_status = STATUS_CHOICES[item.status]
        to_status = STATUS_CHOICES["RJ"]
        text = f"""Status was change from '{fr_status}' to '{to_status}'
Your request was rejected"""
        send_mail(
            "Change Translator Request Status",
            text,
            settings.EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        item.status = "RJ"
        item.user.account.is_translator = False
        if blocked:
            item.user.account.blocked = True
            item.user.account.blocked_reason = "Spam"
        item.user.account.save()
        item.save()
        return redirect(reverse("translator_request:translator_requests"))
