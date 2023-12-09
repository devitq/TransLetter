from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ()


class TranslatorRequestConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "translator_request"
    verbose_name = pgettext_lazy("app name", "TranslatorRequest")
