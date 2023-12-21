from django import forms
from django.utils.translation import pgettext

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
    email_address = forms.EmailField(
        help_text=pgettext(
            "add member form",
            "Enter the user's email address",
        ),
    )
    mail_header = forms.CharField(
        help_text=pgettext("add member form", "Enter a title for the mail"),
        max_length=50,
    )
    mail_text = forms.CharField(
        help_text=pgettext("add member form", "Enter the text of the email"),
        widget=forms.Textarea(),
    )

    def __init__(self, *args, **kwargs):
        super(AddProjectMemberForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta:
        model = models.Project
        fields = (
            "email_address",
            "mail_header",
            "mail_text",
        )


CHOICES = (
    ("admin", "Administrator"),
    ("static_translator", "Static translator"),
)
blank_choice = (("", pgettext("add member form", "--- Choose role ---")),)


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
