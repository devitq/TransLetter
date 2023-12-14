from django.db import models
from django.utils.translation import pgettext_lazy

from accounts.models import User
from projects.models import Project


__all__ = ()

STATUS_CHOISES = [
    ("SE", "Sent"),
    ("AC", "Accepted"),
    ("RJ", "Rejected"),
    ("IP", "In progress"),
    ("FN", "Finished"),
    ("CL", "Closed"),
]


class TranslationRequest(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="translation_requests_authored",
    )
    translator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="translation_requests_translated",
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(
        pgettext_lazy(
            "translation request created at field name",
            "created at",
        ),
    )
    closed_at = models.DateTimeField(
        pgettext_lazy("translation request closed at field name", "closed at"),
        null=True,
        blank=True,
    )
    text = models.TextField(
        pgettext_lazy("translation request text field name", "text"),
    )
    status = models.CharField(
        pgettext_lazy("translation request status field name", "status"),
        max_length=2,
        choices=STATUS_CHOISES,
    )
    price = models.IntegerField(
        pgettext_lazy("translation request price field name", "price"),
    )


class TranslationRequestMessage(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    translation_request = models.ForeignKey(
        TranslationRequest,
        on_delete=models.CASCADE,
    )
    content = models.TextField(
        pgettext_lazy("message content field name", "content"),
    )
    timestamp = models.DateTimeField(
        pgettext_lazy("translation request timestamp field name", "timestamp"),
    )
