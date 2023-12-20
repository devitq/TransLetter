from django.conf import settings
from django.db import models
from django.utils.translation import (
    gettext_lazy as _,
    pgettext_lazy,
)

from resume.models import ResumeFile

__all__ = ()


STATUS_CHOICES = [
    ("SE", _("Sent")),
    ("UR", _("Under review")),
    ("AC", _("Accepted")),
    ("RJ", _("Rejected")),
]


class TranslatorRequestManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("user")
            .select_related("user__account")
            .prefetch_related(
                models.Prefetch(
                    "user__resume__files",
                    ResumeFile.objects.only(ResumeFile.file.field.name),
                ),
            )
        )

    def for_staff(self):
        return self.get_queryset().filter(
            status__in=["SE", "UR"],
        )


class TranslatorRequest(models.Model):
    objects = TranslatorRequestManager()

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="translator_request",
        verbose_name=pgettext_lazy("user field name", "user"),
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default="SE",
        verbose_name=pgettext_lazy("status field name", "status"),
    )

    def __str__(self) -> str:
        verbose = _(
            (f"{self.user.username}'s" " translator request"),
        )
        return str(verbose)


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
        choices=STATUS_CHOICES,
        verbose_name=pgettext_lazy("from field name", "from status"),
    )
    to = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        verbose_name=pgettext_lazy("to field name", "to status"),
    )
    comment = models.TextField(
        verbose_name=pgettext_lazy("comment field name", "comment"),
        null=True,
        blank=True,
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=pgettext_lazy("timestamp field name", "timestamp"),
    )

    def __str__(self) -> str:
        verbose = _(
            (
                "Status update for "
                f"{self.translator_request.user.username}'s"
                " translator request"
            ),
        )
        return str(verbose)
