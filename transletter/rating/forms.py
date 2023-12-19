from django import forms

from rating.models import Rating
from transletter.mixins import BaseFormMixin

__all__ = ()


class RatingAdminForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = (
            model.translation_request.field.name,
            model.text.field.name,
            model.rating.field.name,
        )


class RatingForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(RatingForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta:
        model = Rating
        fields = ["text", "rating"]
