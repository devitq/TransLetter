from django.db import models
from django.utils.translation import pgettext_lazy
from djmoney.models.fields import MoneyField

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


class TranslationRequestManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("author")
            .select_related("translator")
            .select_related("author__account")
            .select_related("translator__account")
        )

    def get_translation_request_detail(self, pk):
        return (
            self.get_queryset()
            .prefetch_related(
                models.Prefetch(
                    "messages",
                    queryset=TranslationRequestMessage.objects.select_related(
                        "author",
                    )
                    .select_related("author__account")
                    .order_by("timestamp"),
                ),
            )
            .filter(pk=pk)
            .first()
        )


class TranslationRequest(models.Model):
    objects = TranslationRequestManager()

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
        auto_now_add=True,
        blank=True,
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
    price = MoneyField(
        pgettext_lazy("translation request price field name", "price"),
        max_digits=19,
        decimal_places=4,
        default_currency="USD",
        currency_choices=(("USD", "Dollar"),),
    )

    class Meta:
        verbose_name = pgettext_lazy(
            "translation request verbose name",
            "translation request",
        )
        verbose_name_plural = pgettext_lazy(
            "translation request verbose name plural",
            "translation requests",
        )


class TranslationRequestMessage(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    translation_request = models.ForeignKey(
        TranslationRequest,
        related_name="messages",
        related_query_name="translation_request",
        on_delete=models.CASCADE,
    )
    content = models.TextField(
        pgettext_lazy("message content field name", "content"),
    )
    timestamp = models.DateTimeField(
        pgettext_lazy("translation request timestamp field name", "timestamp"),
        auto_now_add=True,
        blank=True,
    )

    class Meta:
        verbose_name = pgettext_lazy(
            "translation request message verbose name",
            "translation request message",
        )
        verbose_name_plural = pgettext_lazy(
            "translation request message verbose name plural",
            "translation request messages",
        )
