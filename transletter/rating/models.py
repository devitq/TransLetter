from django.db import models
from django.utils.translation import (
    gettext_lazy as _,
    pgettext_lazy,
)

from translation_request.models import TranslationRequest

__all__ = ()


RATING_CHOISES = (
    (1, pgettext_lazy("rating rank", "Very poor")),
    (2, pgettext_lazy("rating rank", "Poor")),
    (3, pgettext_lazy("rating rank", "Normal")),
    (4, pgettext_lazy("rating rank", "Good")),
    (5, pgettext_lazy("rating rank", "Very good")),
)


class RatingManager(models.Manager):
    def by_translator(self, username):
        return (
            self.get_queryset()
            .select_related(
                "translation_request",
            )
            .select_related("translation_request__author")
            .select_related("translation_request__translator")
            .filter(
                translation_request__translator__username=username,
            )
            .order_by("-created_at")
        )

    def by_translation_request(self, translation_request_id):
        return self.get_queryset().filter(
            translation_request__id=translation_request_id,
        )


class Rating(models.Model):
    objects = RatingManager()

    translation_request = models.OneToOneField(
        TranslationRequest,
        on_delete=models.CASCADE,
        related_name="rating",
    )
    text = models.TextField(
        pgettext_lazy("text field name", "text"),
    )
    rating = models.PositiveSmallIntegerField(
        pgettext_lazy(
            "rating field name",
            "rating",
        ),
        choices=RATING_CHOISES,
    )
    created_at = models.DateTimeField(
        pgettext_lazy("created_at field name", "created at"),
        auto_now_add=True,
    )

    def __str__(self):
        verbose = _(
            (
                "Translation request №"
                f"{self.translation_request.id}"
                " rating by "
                f"{self.translation_request.author}"
            ),
        )
        return str(verbose)

    class Meta:
        verbose_name = pgettext_lazy(
            "verbose name for rating",
            "rating",
        )
        verbose_name_plural = pgettext_lazy(
            "verbose name plural for rating",
            "ratings",
        )
