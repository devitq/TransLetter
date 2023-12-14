from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View
from django.shortcuts import get_object_or_404, render

from accounts.models import User

__all__ = ()


class TranslatorsView(LoginRequiredMixin, ListView):
    template_name = "burse/translators.html"
    context_object_name = "translators"

    def get_queryset(self):
        return User.objects.translators()


class TranslatorView(View):
    template_name = "burse/translator.html"

    def get(self, request, username, *args, **kwargs):
        translator = get_object_or_404(
            User.objects.select_related("account"),
            username=username,
            account__is_translator=True,
        )
        context = {"translator": translator}
        return render(request, self.template_name, context)
