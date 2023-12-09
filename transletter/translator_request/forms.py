from betterforms.multiform import MultiModelForm
from django import forms

from accounts.models import Account
from resume.forms import FilesForm, ResumeCreateForm
from transletter.utils import get_available_langs

__all__ = ()


class RequestAccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = (
            Account.native_lang.field.name,
            Account.languages.field.name,
        )

    languages = forms.MultipleChoiceField(
        choices=get_available_langs(),
        required=False,
    )


class RequestTranslatorForm(MultiModelForm):
    form_classes = {
        "account_form": RequestAccountForm,
        "resume_form": ResumeCreateForm,
        "files_form": FilesForm,
    }
