from django.apps import AppConfig
from django.utils.translation import pgettext_lazy

__all__ = "AccountsConfig"


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = pgettext_lazy("app name", "Accounts")
