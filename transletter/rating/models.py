from django.conf import settings
from django.db import models
from django.utils.translation import (
    gettext_lazy as _,
    pgettext_lazy,
)

from translation_request.models import TranslationRequest

__all__ = ()


class RatingManager(models.Manager):
    def by_translator(self, username):
        return (
            self.get_queryset()
            .filter(
                translator__username=username,
            )
            .select_related("user")
            .select_related("user__account")
            .select_related(
                "translation_request",
                "translation_request__project",
            )
            .order_by("translation_request__project", "-created_at")
        )

    def by_translation_request(self, translation_request_id):
        return self.get_queryset().filter(
            translation_request__id=translation_request_id,
        )


class Rating(models.Model):
    objects = RatingManager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=pgettext_lazy("user field name", "user"),
    )
    translator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name=pgettext_lazy("translator field name", "translator"),
    )
    translation_request = models.ForeignKey(
        TranslationRequest,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name=pgettext_lazy(
            "translation_request field name",
            "translation request",
        ),
    )
    text = models.TextField(
        pgettext_lazy("text field name", "text"),
    )
    rating = models.IntegerField(
        verbose_name=pgettext_lazy(
            "rating field name",
            "rating",
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=pgettext_lazy("created_at field name", "created at"),
    )

    class Meta:
        verbose_name = pgettext_lazy(
            "verbose name for rating",
            "rating",
        )
        verbose_name_plural = pgettext_lazy(
            "verbose name plural for rating",
            "ratings",
        )

    def __str__(self):
        verbose = _(
            (
                "Translation request №"
                f"{self.translation_request.id}"
                " rating by "
                f"{self.user}"
            ),
        )
        return str(verbose)
