from betterforms.multiform import MultiModelForm
from django import forms

from accounts.models import Account, User
from resume import forms as resume_forms
from translator_request.models import TranslatorRequestStatusLog
from transletter.mixins import BaseFormMixin
from transletter.utils import get_available_langs

__all__ = ()


class RequestAccountForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[Account.native_lang.field.name].required = True
        self.fields[Account.languages.field.name].required = True
        self.set_field_attributes()

    class Meta:
        model = Account
        fields = (
            Account.native_lang.field.name,
            Account.languages.field.name,
        )

    languages = forms.MultipleChoiceField(
        choices=get_available_langs(),
        required=True,
    )


class RequestUserForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.set_field_attributes()

    class Meta:
        model = User
        fields = ("first_name", "last_name")


class RequestUserFormDisabled(RequestUserForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.disabled = True
            field.field.widget.attrs["disabled"] = True
            field.required = False


class RequestAccountFormDisabled(RequestAccountForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.disabled = True
            field.field.widget.attrs["disabled"] = True
            field.required = False


class RejectRequestForm(forms.Form):
    class Meta:
        model = TranslatorRequestStatusLog
        fields = ("comment",)


class RequestTranslatorForm(MultiModelForm):
    form_classes = {
        "user_form": RequestUserForm,
        "account_form": RequestAccountForm,
        "resume_form": resume_forms.ResumeCreateForm,
        "files_form": resume_forms.FilesForm,
    }


class RequestTranslatorFormDisabled(MultiModelForm):
    form_classes = {
        "user_form": RequestUserFormDisabled,
        "account_form": RequestAccountFormDisabled,
        "resume_form": resume_forms.ResumeCreateFormDisabled,
        "files_form": resume_forms.FilesFormDisabled,
    }
