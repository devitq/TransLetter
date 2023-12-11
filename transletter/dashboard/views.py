from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View

from accounts.forms import (
    AccountAvatarChangeForm,
    UserAccountChangeForm,
    UserChangeForm,
)

__all__ = ()


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"


class AccountEditView(LoginRequiredMixin, View):
    template_name = "dashboard/edit_account.html"

    def get(self, request, *args, **kwargs):
        user_form = UserChangeForm(instance=request.user)
        initial_languages = request.user.account.languages
        account_form = UserAccountChangeForm(
            instance=request.user.account,
            initial={"languages": initial_languages},
        )
        avatar_form = AccountAvatarChangeForm(instance=request.user.account)
        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "account_form": account_form,
                "avatar_form": avatar_form,
            },
        )

    def post(self, request, *args, **kwargs):
        user_form = UserChangeForm(request.POST, instance=request.user)
        account_form = UserAccountChangeForm(
            request.POST,
            instance=request.user.account,
        )
        avatar_form = AccountAvatarChangeForm(
            request.POST,
            request.FILES,
            instance=request.user.account,
        )

        if (
            user_form.is_valid()
            and account_form.is_valid()
            and avatar_form.is_valid()
        ):
            user_form.save()
            account_form.save()
            avatar_form.save()
            request.user.account.languages = account_form.cleaned_data[
                "languages"
            ]
            request.user.account.save()
            messages.success(request, "Account updated successfully!")
            return redirect("dashboard:edit_account")

        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "account_form": account_form,
                "avatar_form": avatar_form,
            },
        )
