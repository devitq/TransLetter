from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ()


class TranslationRequestConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "translation_request"
    verbose_name = pgettext_lazy("app name", "Translation Request")
