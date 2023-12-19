from django.apps import AppConfig
from django.utils.translation import pgettext_lazy

__all__ = ()


class RatingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rating"
    verbose_name = pgettext_lazy("app name", "Rating")
