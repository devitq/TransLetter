from django import forms
from django.utils.translation import pgettext_lazy

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


class AddProjectMemberForm(forms.Form, BaseFormMixin):
    email = forms.EmailField(
        label=pgettext_lazy("add member form", "Email"),
        help_text=pgettext_lazy(
            "add member form",
            "Enter the user's email address",
        ),
    )
    email_header = forms.CharField(
        label=pgettext_lazy("add member form", "Email header"),
        help_text=pgettext_lazy(
            "add member form",
            "Enter the title of the email",
        ),
        max_length=50,
    )
    email_text = forms.CharField(
        help_text=pgettext_lazy(
            "add member form",
            "Enter the text of the email",
        ),
        widget=forms.Textarea(),
    )

    def __init__(self, *args, **kwargs):
        super(AddProjectMemberForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta:
        model = models.Project
        fields = (
            "email_address",
            "email_header",
            "email_text",
        )


CHOICES = [
    (key, value)
    for key, value in models.ProjectMembership.ROLES
    if key not in ["owner", "hired_translator"]
]
blank_choice = [("", pgettext_lazy("add member form", "--- Choose role ---"))]


class UpdateProjectMemberForm(forms.Form, BaseFormMixin):
    role = forms.TypedChoiceField(choices=blank_choice + CHOICES)

    def __init__(self, *args, **kwargs):
        super(UpdateProjectMemberForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta:
        model = models.ProjectMembership
        fields = ("role",)


class ProjectChangeForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(ProjectChangeForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta:
        model = models.Project
        fields = (
            "name",
            "slug",
            "description",
        )


class ProjectAvatarChangeForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(ProjectAvatarChangeForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "file-upload"

    class Meta:
        model = models.Project
        fields = ("avatar",)


class TranslationFileForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(TranslationFileForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta:
        model = models.TranslationFile
        fields = ("file", "project_language")
        widgets = {
            "project_language": forms.Select(attrs={"class": "form-control"}),
        }


class UpdateTranslationFileForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(UpdateTranslationFileForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta:
        model = models.TranslationFile
        fields = ("file",)


class TranslationRowEditForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(TranslationRowEditForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta:
        model = models.TranslationRow
        fields = ("msg_str",)
        labels = {
            "msg_str": pgettext_lazy("translation edit label", "Translation"),
        }


class AddLanguageForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(AddLanguageForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta:
        model = models.ProjectLanguage
        fields = ("lang_code",)
