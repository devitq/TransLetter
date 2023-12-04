from django.apps import AppConfig
from django.utils.translation import pgettext_lazy

__all__ = ()


class ResumeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "resume"
    verbose_name = pgettext_lazy("app name", "Resume")
