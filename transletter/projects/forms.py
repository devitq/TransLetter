from django import forms

from projects import models
from transletter.mixins import BaseFormMixin


__all__ = ()


class CreateProjectForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(CreateProjectForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta:
        model = models.Project
        fields = (
            models.Project.name.field.name,
            models.Project.description.field.name,
            models.Project.slug.field.name,
            models.Project.source_lang.field.name,
        )
