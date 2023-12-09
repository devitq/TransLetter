from betterforms.multiform import MultiModelForm

from resume.forms import FilesForm, ResumeCreateForm

__all__ = ()


class RequestTranslatorForm(MultiModelForm):
    form_classes = {
        "resume_form": ResumeCreateForm,
        "files_form": FilesForm,
    }
