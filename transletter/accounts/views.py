from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.views.generic import (
    CreateView,
    FormView,
    View,
)

from accounts.forms import RequestAccountActivationForm, UserSignupForm
import accounts.models

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
            email.send(fail_silently=False)

            messages.success(
                self.request,
                pgettext_lazy(
                    "success message in views",
                    (
                        "You have successfully registered! Check your "
                        "email with for further instructions."
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
            activation_url = self.request.build_absolute_uri(
                reverse("accounts:activate_account", kwargs={"token": token}),
            )

            send_mail(
                "Account Activation Request",
                (
                    "Please click the following link to activate"
                    f"your account: {activation_url}"
                ),
                settings.EMAIL,
                [user_email],
                fail_silently=False,
            )

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
