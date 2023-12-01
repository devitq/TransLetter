from django import forms
from django.contrib import auth

from accounts.models import Account, User
from transletter.mixins import BaseFormMixin


__all__ = ()


class UserChangeForm(auth.forms.UserChangeForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta(auth.forms.UserChangeForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")


class UserAccountChangeForm(forms.ModelForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(UserAccountChangeForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta:
        model = Account
        fields = (Account.avatar.field.name,)


class UserSignupForm(auth.forms.UserCreationForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()

    class Meta(auth.forms.UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")


class EditUserAdminForm(auth.admin.UserChangeForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        email = User.objects.normalize_email(
            email,
        )
        user_exist = (
            User.objects.filter(email=email)
            .exclude(pk=self.instance.id)
            .exists()
        )
        if user_exist:
            raise forms.ValidationError(
                "Пользователь с такой электронной почтой уже существует",
            )
        return self.cleaned_data["email"]


class CreateUserAdminForm(auth.admin.UserCreationForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        email = User.objects.normalize_email(
            email,
        )
        user_exist = (
            User.objects.filter(email=email)
            .exclude(pk=self.instance.id)
            .exists()
        )
        if user_exist:
            raise forms.ValidationError(
                "Пользователь с такой электронной почтой уже существует",
            )
        return self.cleaned_data["email"]


class MyLoginForm(auth.forms.AuthenticationForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(MyLoginForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()


class MyPasswordChangeForm(auth.forms.PasswordChangeForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(MyPasswordChangeForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()


class MyPasswordResetForm(auth.forms.PasswordResetForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(MyPasswordResetForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()


class MyPasswordConfirmForm(auth.forms.SetPasswordForm, BaseFormMixin):
    def __init__(self, *args, **kwargs):
        super(MyPasswordConfirmForm, self).__init__(*args, **kwargs)
        self.set_field_attributes()
