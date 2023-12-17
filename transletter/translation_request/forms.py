from django import forms

from projects.models import Project
from translation_request.models import (
    TranslationRequest,
    TranslationRequestMessage,
)
from transletter.mixins import BaseFormMixin

__all__ = ()


class CreateTranslationRequestForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, user, *args, **kwargs):
        super(CreateTranslationRequestForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()
        self.fields["project"].queryset = Project.objects.filter(
            projectmembership__user=user,
            projectmembership__role="owner",
        )

    class Meta:
        model = TranslationRequest
        fields = (
            "project",
            "text",
            "price",
        )


class MessageForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta:
        model = TranslationRequestMessage
        fields = ("content",)
        widgets = {
            "content": forms.TextInput(attrs={"placeholder": "Your message"}),
        }
