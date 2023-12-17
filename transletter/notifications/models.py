from django.conf import settings
from django.db import models
from django.utils.translation import pgettext_lazy

__all__ = ()


class NotificationManager(models.Manager):
    def by_user(self, user_id):
        return self.get_queryset().filter(
            user__id=user_id,
        )


class Notification(models.Model):
    objects = NotificationManager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=pgettext_lazy("user field name", "user"),
    )
    title = models.CharField(
        max_length=150,
        verbose_name=pgettext_lazy("title field name", "title"),
        null=False,
    )
    content = models.TextField(
        verbose_name=pgettext_lazy("content field name", "content"),
        null=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=pgettext_lazy("created_at field name", "created at"),
    )

    class Meta:
        verbose_name = pgettext_lazy(
            "verbose name for notification",
            "notification",
        )
        verbose_name_plural = pgettext_lazy(
            "verbose name plural for notification",
            "notifications",
        )

    def __str__(self):
        return self.title
