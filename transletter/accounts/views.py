from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import pgettext_lazy
from django.views.generic import (
    CreateView,
    View,
)

from accounts.forms import UserSignupForm
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
                pgettext_lazy("error message in views", "Broken link!"),
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
                pgettext_lazy("error message in views", "Broken link!"),
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
