from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

__all__ = ()


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"
