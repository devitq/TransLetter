from django.apps import AppConfig
from django.utils.translation import pgettext_lazy

__all__ = ()


class NotificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notification"
    verbose_name = pgettext_lazy("app name", "Notification")
