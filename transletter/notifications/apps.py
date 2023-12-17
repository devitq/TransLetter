from django.apps import AppConfig
from django.utils.translation import pgettext_lazy

__all__ = ()


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"
    verbose_name = pgettext_lazy("app name", "Notifications")
