from betterforms.multiform import MultiModelForm
from django import forms

from accounts.models import Account
from resume import forms as resume_forms
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


class RequestAccountFormDisabled(RequestAccountForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.disabled = True
            field.field.widget.attrs["disabled"] = True
            field.required = False


class RequestTranslatorForm(MultiModelForm):
    form_classes = {
        "account_form": RequestAccountForm,
        "resume_form": resume_forms.ResumeCreateForm,
        "files_form": resume_forms.FilesForm,
    }


class RequestTranslatorFormDisabled(MultiModelForm):
    form_classes = {
        "account_form": RequestAccountFormDisabled,
        "resume_form": resume_forms.ResumeCreateFormDisabled,
        "files_form": resume_forms.FilesFormDisabled,
    }
