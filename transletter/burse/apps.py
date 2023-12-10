from django.apps import AppConfig
from django.utils.translation import pgettext_lazy

__all__ = ()


class BurseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "burse"
    verbose_name = pgettext_lazy("app name", "Burse")
