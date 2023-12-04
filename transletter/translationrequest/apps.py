from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ()


class TranslationrequestConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "translationrequest"
    verbose_name = pgettext_lazy("app name", "TranslationRequest")
