from http import HTTPStatus

from django.core import mail
from django.test import override_settings, TestCase
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time

import accounts.models

__all__ = ()


class RegistrationActivationTests(TestCase):
    def setUp(self):
        self.signup_url = reverse("accounts:signup")
        self.activation_url = reverse(
            "accounts:activate_account",
            args=["token"],
        )
        self.time_now = timezone.now()

    @override_settings(DEFAULT_USER_IS_ACTIVE=False)
    def test_user_registration_and_late_activation(self):
        response = self.client.post(
            self.signup_url,
            {
                "username": "testuser",
                "password1": "testpassword",
                "password2": "testpassword",
                "email": "testuser@example.com",
            },
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
        )
        user = accounts.models.User.objects.get(username="testuser")
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        link = mail.outbox[0].body

        with freeze_time(
            self.time_now + timezone.timedelta(hours=12, minutes=1),
        ):
            response = self.client.get(
                link,
                follow=True,
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)
            user.refresh_from_db()
            self.assertFalse(user.is_active)

    @override_settings(DEFAULT_USER_IS_ACTIVE=False)
    def test_user_registration_and_on_time_activation(self):
        response = self.client.post(
            self.signup_url,
            {
                "username": "testuser",
                "password1": "testpassword",
                "password2": "testpassword",
                "email": "testuser@example.com",
            },
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
        )
        user = accounts.models.User.objects.get(username="testuser")
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        link = mail.outbox[0].body

        with freeze_time(
            self.time_now + timezone.timedelta(hours=11, minutes=59),
        ):
            response = self.client.get(
                link,
                follow=True,
            )
            self.assertEqual(
                response.status_code,
                HTTPStatus.OK,
            )

            user.refresh_from_db()
            self.assertTrue(user.is_active)
