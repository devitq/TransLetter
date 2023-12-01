from http import HTTPStatus
import os

from django.conf import settings
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time

import accounts.models

__all__ = ()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.email = "testuser@example.com"
        self.password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "1234")
        self.user = accounts.models.User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
        )
        self.time_now = timezone.now()
        self.reactivation_url = reverse(
            "accounts:reactivate_account",
            args=["token"],
        )

    def test_login_by_username(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.username, "password": self.password},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_login_by_email(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.email, "password": self.password},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_account_deactivation_and_late_reactivation(self):
        for _ in range(settings.MAX_AUTH_ATTEMPTS):
            self.client.post(
                reverse("login"),
                {"username": self.username, "password": "wrong_pass"},
            )
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        link = mail.outbox[0].body

        with freeze_time(
            self.time_now + timezone.timedelta(weeks=1, minutes=1),
        ):
            response = self.client.get(
                link,
                follow=True,
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.user.refresh_from_db()
            self.assertFalse(self.user.is_active)

    def test_account_deactivation_and_on_time_reactivation(self):
        for _ in range(settings.MAX_AUTH_ATTEMPTS):
            self.client.post(
                reverse("login"),
                {"username": self.username, "password": "wrong_pass"},
            )
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        link = mail.outbox[0].body

        with freeze_time(
            self.time_now + timezone.timedelta(days=6, hours=23, minutes=59),
        ):
            response = self.client.get(
                link,
                follow=True,
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.user.refresh_from_db()
            self.assertTrue(self.user.is_active)
