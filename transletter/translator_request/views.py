from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import pgettext_lazy
from django.views.generic import DetailView, ListView, View

from resume.models import ResumeFile
from translator_request.forms import RequestTranslatorForm
from translator_request.models import TranslatorRequest

__all__ = ()


class RequestTranslatorView(View):
    template_name = "translator_request/request_translator.html"
    success_url = reverse_lazy("dashboard:edit_account")

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, "translator_request"):
            if request.user.translator_request.status in ["UR", "AC"]:
                messages.error(
                    request,
                    pgettext_lazy(
                        "RequestTranslator under review error message",
                        "The request is currently under review",
                    ),
                )
                return redirect(reverse("dashboard:edit_account"))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        initial_languages = request.user.account.languages
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
        return render(
            request,
            template_name=self.template_name,
            context={"form": form},
        )

    def post(self, request):
        form = RequestTranslatorForm(request.POST, request.FILES)
        if form.is_valid():
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
                request.user.translator_request.status = "SE"
                request.user.translator_request.save()
            else:
                TranslatorRequest.objects.create(
                    user=request.user,
                    resume=resume,
                )
            messages.success(
                request,
                pgettext_lazy(
                    "RequestTranslator create success",
                    "Your request to become a translator has been sent",
                ),
            )
            return redirect(reverse("dashboard:edit_account"))

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


class TranslatorRequestView(LoginRequiredMixin, DetailView):
    template_name = "translator_request/translator_request.html"
    model = TranslatorRequest
    context_object_name = "translator_request"

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        if item.status == "SE":
            item.status = "UR"
            item.save()
        return render(
            request,
            template_name=self.template_name,
            context={"translator_request": item},
        )


class AcceptRequestView(LoginRequiredMixin, DetailView):
    model = TranslatorRequest
    context_object_name = "translator_request"

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(
                request,
                pgettext_lazy(
                    "User is not staff",
                    "You do not have enough permissions",
                ),
            )
            return redirect(reverse("translator_request:translator_requests"))
        item = self.get_object()
        item.status = "AC"
        item.save()
        return redirect(reverse("translator_request:translator_requests"))


class RejectRequestView(LoginRequiredMixin, DetailView):
    model = TranslatorRequest
    context_object_name = "translator_request"

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(
                request,
                pgettext_lazy(
                    "User is not staff",
                    "You do not have enough permissions",
                ),
            )
            return redirect(reverse("translator_request:translator_requests"))
        item = self.get_object()
        item.status = "RJ"
        item.save()
        return redirect(reverse("translator_request:translator_requests"))
