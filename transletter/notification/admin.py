from django.contrib import admin

from notification import models

__all__ = ()


class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        models.Notification.title.field.name,
        models.Notification.user.field.name,
        models.Notification.content.field.name,
        models.Notification.created_at.field.name,
    ]
    readonly_fields = [
        models.Notification.created_at.field.name,
    ]


admin.site.register(models.Notification, NotificationAdmin)
