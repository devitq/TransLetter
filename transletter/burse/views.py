from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from accounts.models import User

__all__ = ()


class TranslatorsView(LoginRequiredMixin, ListView):
    template_name = "burse/translators.html"
    context_object_name = "translators"

    def get_queryset(self):
        return User.objects.translators()
