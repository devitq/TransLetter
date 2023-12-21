from django.apps import AppConfig
from django.utils.translation import pgettext_lazy as pgettext_lazy

__all__ = ()


class ProjectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "projects"
    verbose_name = pgettext_lazy("app name", "Projects")
