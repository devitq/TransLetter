from django.conf import settings
from django.db import models
from django.utils.translation import (
    gettext_lazy as _,
    pgettext_lazy as pgettext_lazy,
)

from resume.models import Resume

__all__ = ()


STATUS_CHOICES = [
    ("SE", _("Sent")),
    ("UR", _("Under review")),
    ("AC", _("Accepted")),
    ("RJ", _("Rejected")),
]


class TranslatorRequest(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="translator_request",
        verbose_name=pgettext_lazy("user field name", "user"),
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.SET_NULL,
        related_name="translator_request",
        verbose_name=pgettext_lazy("resume field name", "resume"),
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default="SE",
        verbose_name=pgettext_lazy("status field name", "status"),
    )


class TranslatorRequestStatusLog(models.Model):
    translator_request = models.ForeignKey(
        TranslatorRequest,
        on_delete=models.CASCADE,
        related_name="status_logs",
        verbose_name=pgettext_lazy(
            "translator_request field name",
            "translator request",
        ),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="status_logs",
        verbose_name=pgettext_lazy("user field name", "user"),
    )
    from_status = models.CharField(
        max_length=2,
        db_column="from",
        verbose_name=pgettext_lazy("from field name", "from"),
    )
    to = models.CharField(
        max_length=2,
        verbose_name=pgettext_lazy("to field name", "to"),
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=pgettext_lazy("timestamp field name", "timestamp"),
    )
