from django import forms
from django.utils.translation import pgettext_lazy

from resume.models import Resume, ResumeFile
from transletter.mixins import BaseFormMixin

__all__ = ()


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)


class FilesForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(FilesForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    file = MultipleFileField(
        label=pgettext_lazy(
            "files form file label",
            "Files",
        ),
        help_text=pgettext_lazy(
            "files form file help_text",
            "Add resume files",
        ),
        required=False,
    )

    class Meta:
        model = ResumeFile
        fields = "__all__"
        exclude = [
            ResumeFile.resume.field.name,
        ]


class FilesFormDisabled(FilesForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.disabled = True
            field.field.widget.attrs["disabled"] = True
            field.required = False


class ResumeCreateForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, disable_fields=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if disable_fields:
            for field in self.fields:
                self[field].disabled = True
        self.fields[Resume.about.field.name].required = True
        self.set_field_attributes()

    class Meta:
        model = Resume
        fields = (Resume.about.field.name,)


class ResumeCreateFormDisabled(ResumeCreateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.disabled = True
            field.field.widget.attrs["disabled"] = True
            field.required = False
