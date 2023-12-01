from betterforms.multiform import MultiModelForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    View,
)

from accounts.forms import (
    UserAccountChangeForm,
    UserChangeForm,
    UserSignupForm,
)
import accounts.models


__all__ = ()


class ActivateAccountView(View):
    def get(self, request, token):
        signer = TimestampSigner()
        try:
            username = signer.unsign(
                token,
                max_age=timezone.timedelta(hours=12),
            )
            user = accounts.models.User.objects.get(username=username)
            user.is_active = True
            user.save()
            messages.success(
                request,
                "Аккаунт успешно активирован",
            )
        except SignatureExpired:
            messages.error(
                request,
                "Срок действия ссылки истёк :(",
            )
        except BadSignature:
            messages.error(
                request,
                "Сломанная ссылка!",
            )

        return redirect("accounts:login")


class ReactivateAccountView(View):
    def get(self, request, token):
        signer = TimestampSigner()
        try:
            username = signer.unsign(
                token,
                max_age=timezone.timedelta(days=7),
            )
            user = accounts.models.User.objects.get(username=username)
            user.is_active = True
            user.save()
            messages.success(
                request,
                "Аккаунт успешно активирован",
            )
        except SignatureExpired:
            messages.error(
                request,
                "Срок действия ссылки истёк :(",
            )
        except BadSignature:
            messages.error(
                request,
                "Сломанная ссылка!",
            )

        return redirect("accounts:login")


class UserSignupView(CreateView):
    template_name = "accounts/signup.html"
    form_class = UserSignupForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            user = form.save(commit=False)
            user.is_active = settings.DEFAULT_USER_IS_ACTIVE
            user.save()
            self.object = user
            signer = TimestampSigner()
            token = signer.sign(user.username)
            url = self.request.build_absolute_uri(
                reverse(
                    "accounts:activate_account",
                    kwargs={"token": token},
                ),
            )
            send_mail(
                "Activate Your Account",
                url,
                settings.EMAIL,
                [form.cleaned_data.get("email")],
                fail_silently=False,
            )

            messages.success(
                self.request,
                "Please check your email to activate your account.",
            )

            return super().form_valid(form)
        return super().form_invalid(form)

    def get_success_url(self):
        if self.request.user.is_authenticated:
            return reverse_lazy("landing:index")
        return None


class UserAccountMultiForm(MultiModelForm):
    form_classes = {
        "user_form": UserChangeForm,
        "account_form": UserAccountChangeForm,
    }


class AccountEditView(LoginRequiredMixin, View):
    template_name = "accounts/account.html"

    def get(self, request, *args, **kwargs):
        user_form = UserChangeForm(instance=request.user)
        account_form = UserAccountChangeForm(instance=request.user.account)
        return render(
            request,
            self.template_name,
            {"user_form": user_form, "account_form": account_form},
        )

    def post(self, request, *args, **kwargs):
        user_form = UserChangeForm(request.POST, instance=request.user)
        account_form = UserAccountChangeForm(
            request.POST,
            request.FILES,
            instance=request.user.account,
        )

        if user_form.is_valid() and account_form.is_valid():
            user_form.save()
            account_form.save()
            messages.success(request, "Account updated successfully!")
            return redirect("accounts:account")

        return render(
            request,
            self.template_name,
            {"user_form": user_form, "account_form": account_form},
        )
