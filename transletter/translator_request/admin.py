from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

from translator_request import models

__all__ = ()

STATUS_CHOICES = {
    "SE": "Sent",
    "UR": "Under review",
    "AC": "Accepted",
    "RJ": "Rejected",
}


class TranslatorRequestAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        models.TranslatorRequest.user.field.name,
        models.TranslatorRequest.resume.field.name,
        models.TranslatorRequest.status.field.name,
    ]

    def save_model(self, request, obj, form, change):
        original_status = None

        if obj.pk:
            original_status = models.TranslatorRequest.objects.get(
                pk=obj.pk,
            ).status

        super().save_model(request, obj, form, change)

        if original_status and original_status != obj.status:
            models.TranslatorRequestStatusLog.objects.create(
                user=request.user,
                translator_request=obj,
                from_status=original_status,
                to=obj.status,
            )
            fr_status = STATUS_CHOICES[original_status]
            to_status = STATUS_CHOICES[obj.status]
            text = f"Status was change from '{fr_status}' to '{to_status}'"
            send_mail(
                "Change Translator Request Status",
                text,
                settings.EMAIL,
                [request.user.email],
                fail_silently=False,
            )

    def title(self, obj):
        return obj

    title.short_description = _("Title")


class TranslatorRequestStatusLogAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        models.TranslatorRequestStatusLog.user.field.name,
        models.TranslatorRequestStatusLog.from_status.field.name,
        models.TranslatorRequestStatusLog.to.field.name,
    ]
    readonly_fields = [
        models.TranslatorRequestStatusLog.translator_request.field.name,
        models.TranslatorRequestStatusLog.user.field.name,
        models.TranslatorRequestStatusLog.from_status.field.name,
        models.TranslatorRequestStatusLog.to.field.name,
    ]

    def title(self, obj):
        return obj

    title.short_description = _("Title")


admin.site.register(models.TranslatorRequest, TranslatorRequestAdmin)
admin.site.register(
    models.TranslatorRequestStatusLog,
    TranslatorRequestStatusLogAdmin,
)
