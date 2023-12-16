from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, View

from accounts.models import User
from resume.models import ResumeFile

__all__ = ()


class TranslatorsView(LoginRequiredMixin, ListView):
    template_name = "burse/translators.html"
    context_object_name = "translators"

    def get_queryset(self):
        return User.objects.translators()


class TranslatorView(LoginRequiredMixin, View):
    template_name = "burse/translator.html"

    def get(self, request, username, *args, **kwargs):
        translator = get_object_or_404(
            User.objects.select_related("account")
            .select_related("account__resume")
            .prefetch_related(
                models.Prefetch(
                    "account__resume__files",
                    queryset=ResumeFile.objects.all(),
                ),
            ),
            username=username,
            account__is_translator=True,
        )
        context = {"translator": translator}
        return render(request, self.template_name, context)
