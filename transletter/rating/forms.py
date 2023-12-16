from django import forms

from rating.models import Rating

__all__ = ()


class RatingAdminForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = (
            model.user.field.name,
            model.translator.field.name,
            model.translation_request.field.name,
            model.text.field.name,
            model.rating.field.name,
        )
