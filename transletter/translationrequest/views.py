from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import pgettext_lazy
from django.views.generic import View

from resume.models import ResumeFile
from translationrequest.forms import RequestTranslatorForm
from translationrequest.models import TranslatorRequest

__all__ = ()


class RequestTranslatorView(View):
    template_name = "translation_request/request_translator.html"
    success_url = reverse_lazy("dashboard:edit_account")

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, "translator_request"):
            raise Http404("TranslatorRequest already exists for this user")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        try:
            form = RequestTranslatorForm(
                instance={
                    "resume_form": request.user.account.resume,
                },
            )
        except Exception:
            form = RequestTranslatorForm()
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
            request.user.account.resume = resume
            request.user.account.save()
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
