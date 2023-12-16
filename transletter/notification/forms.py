from django import forms

from notification.models import Notification

__all__ = ()


class EditNotificationAdminForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = (
            model.user.field.name,
            model.title.field.name,
            model.content.field.name,
        )


class CreateNotificationAdminForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = (
            model.user.field.name,
            model.title.field.name,
            model.content.field.name,
        )
