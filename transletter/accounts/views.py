from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.views.generic import (
    CreateView,
    FormView,
    View,
)

from accounts.forms import (
    AccountAvatarChangeForm,
    RequestAccountActivationForm,
    UserAccountChangeForm,
    UserChangeForm,
    UserSignupForm,
)
import accounts.models
from transletter.email import EmailThread

__all__ = ()


class ActivateAccountView(View):
    def get(self, request, token):
        signer = TimestampSigner()
        try:
            username = signer.unsign(
                token,
                max_age=timezone.timedelta(hours=1),
            )
            user = accounts.models.User.objects.get(username=username)
            user.is_active = True
            user.save()
            messages.success(
                request,
                pgettext_lazy(
                    "error message in views",
                    "Account successfully activated",
                ),
            )
        except SignatureExpired:
            messages.error(
                request,
                pgettext_lazy(
                    "error message in views",
                    "The link has expired",
                ),
            )
        except BadSignature:
            messages.error(
                request,
                pgettext_lazy("error message in views", "Invalid link!"),
            )

        return redirect("accounts:login")


class UserSignupView(CreateView):
    template_name = "accounts/signup.html"
    form_class = UserSignupForm
    success_url = reverse_lazy("accounts:login")

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            user = form.save(commit=False)
            user.is_active = settings.DEFAULT_USER_IS_ACTIVE
            user.save()
            self.object = user
            signer = TimestampSigner()
            token = signer.sign(user.username)
            link = self.request.build_absolute_uri(
                reverse(
                    "accounts:activate_account",
                    kwargs={"token": token},
                ),
            )
            email_body = render_to_string(
                "accounts/email/activate_account.html",
                {"username": user.username, "link": link},
            )
            email = EmailMultiAlternatives(
                subject="Account activation - TransLetter",
                body=email_body,
                from_email=settings.EMAIL,
                to=[user.email],
            )
            email.attach_alternative(email_body, "text/html")
            EmailThread(email).start()

            messages.success(
                self.request,
                pgettext_lazy(
                    "success message in views",
                    (
                        "You have successfully registered! Check your "
                        "email for further instructions."
                    ),
                ),
            )

            return super().form_valid(form)
        return super().form_invalid(form)


class AccountActivationRequestView(FormView):
    template_name = "accounts/request_activation.html"
    form_class = RequestAccountActivationForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user_email = accounts.models.User.objects.normalize_email(
            form.cleaned_data.get("email"),
        )
        try:
            user = accounts.models.User.objects.get(email=user_email)
        except accounts.models.User.DoesNotExist:
            messages.success(
                self.request,
                pgettext_lazy(
                    "success message in views",
                    (
                        "Your account activation request has been submitted. "
                        "Please check your email for further instructions."
                    ),
                ),
            )
            return redirect(self.success_url)

        if not user.is_active:
            signer = TimestampSigner()
            token = signer.sign(user.username)
            link = self.request.build_absolute_uri(
                reverse("accounts:activate_account", kwargs={"token": token}),
            )

            email_body = render_to_string(
                "accounts/email/activate_account_request.html",
                {"username": user.username, "link": link},
            )
            email = EmailMultiAlternatives(
                subject="Account activation - TransLetter",
                body=email_body,
                from_email=settings.EMAIL,
                to=[user.email],
            )
            email.attach_alternative(email_body, "text/html")
            EmailThread(email).start()

            messages.success(
                self.request,
                pgettext_lazy(
                    "success message in views",
                    (
                        "Your account activation request has been submitted. "
                        "Please check your email for further instructions."
                    ),
                ),
            )

            return super().form_valid(form)

        messages.warning(
            self.request,
            pgettext_lazy(
                "warning message in views",
                "Your account is already active. Please proceed to login.",
            ),
        )

        return super().form_invalid(form)


class AccountEditView(LoginRequiredMixin, View):
    template_name = "accounts/edit_account.html"

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
        old_email = request.user.email
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

            if old_email != request.user.email:
                request.user.is_active = False
                request.user.save()

            messages.success(
                request,
                pgettext_lazy(
                    "success message in views",
                    "Account updated successfully!",
                ),
            )
            return redirect("accounts:edit_account")

        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "account_form": account_form,
                "avatar_form": avatar_form,
            },
        )
