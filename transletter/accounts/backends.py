from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.mail import send_mail
from django.core.signing import TimestampSigner
from django.urls import reverse

import accounts.models

__all__ = ("AuthenticationBackend",)


class AuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()

        if username is None:
            username = kwargs.get(user_model.USERNAME_FIELD)
        if password is None or username is None:
            return None

        try:
            if "@" in username:
                email = accounts.models.User.objects.normalize_email(username)
                user = accounts.models.User.objects.by_mail(
                    email=email,
                )
            else:
                user = accounts.models.User.objects.get(username=username)
        except accounts.models.User.DoesNotExist:
            user_model().set_password(password)
            return None

        if user.check_password(password):
            user.account.attempts_count = 0
            user.account.save()
            return user

        user.account.attempts_count += 1
        user.account.save()

        if (
            user.account.attempts_count >= settings.MAX_AUTH_ATTEMPTS
            and user.is_active is True
        ):
            self._deactivate_user(request, user)

        return None

    def _deactivate_user(self, request, user):
        user.is_active = False
        user.save()

        signer = TimestampSigner()
        token = signer.sign(user.username)
        url = request.build_absolute_uri(
            reverse(
                "accounts:reactivate_account",
                kwargs={"token": token},
            ),
        )
        send_mail(
            "Reactivate Your Account",
            url,
            settings.EMAIL,
            [user.email],
            fail_silently=False,
        )
