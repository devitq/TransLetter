from django.contrib import admin

from notification import models
from notification.forms import (
    CreateNotificationAdminForm,
    EditNotificationAdminForm,
)

__all__ = ()


class NotificationAdmin(admin.ModelAdmin):
    form = EditNotificationAdminForm
    add_form = CreateNotificationAdminForm
    list_display = [
        models.Notification.title.field.name,
        models.Notification.user.field.name,
        models.Notification.content.field.name,
        models.Notification.read.field.name,
        models.Notification.created_at.field.name,
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + (
                models.Notification.read.field.name,
                models.Notification.created_at.field.name,
            )
        return self.readonly_fields


admin.site.register(models.Notification, NotificationAdmin)
