from http import HTTPStatus
import os
from time import sleep

from bs4 import BeautifulSoup
from django.conf import settings
from django.core import mail
from django.test import Client, override_settings, TestCase
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time

import accounts.models

__all__ = ()


class AuthenticationTests(TestCase):
    @override_settings(RECAPTCHA_ENABLED=False)
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
            "accounts:activate_account",
            args=["token"],
        )

    @override_settings(RECAPTCHA_ENABLED=False)
    def test_login_by_username(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.username, "password": self.password},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    @override_settings(RECAPTCHA_ENABLED=False)
    def test_login_by_email(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.email, "password": self.password},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    @override_settings(RECAPTCHA_ENABLED=False)
    def test_account_deactivation_and_late_reactivation(self):
        for _ in range(settings.MAX_AUTH_ATTEMPTS):
            self.client.post(
                reverse("login"),
                {"username": self.username, "password": "wrong_pass"},
            )
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        sleep(0.5)
        soup = BeautifulSoup(mail.outbox[0].body, "html.parser")
        links = soup.find_all("a")

        with freeze_time(
            self.time_now + timezone.timedelta(hours=1, minutes=1),
        ):
            response = self.client.get(
                links[0].get("href"),
                follow=True,
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.user.refresh_from_db()
            self.assertFalse(self.user.is_active)

    @override_settings(RECAPTCHA_ENABLED=False)
    def test_account_deactivation_and_on_time_reactivation(self):
        for _ in range(settings.MAX_AUTH_ATTEMPTS):
            self.client.post(
                reverse("login"),
                {"username": self.username, "password": "wrong_pass"},
            )
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        soup = BeautifulSoup(mail.outbox[0].body, "html.parser")
        links = soup.find_all("a")

        with freeze_time(
            self.time_now + timezone.timedelta(minutes=59),
        ):
            response = self.client.get(
                links[0].get("href"),
                follow=True,
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.user.refresh_from_db()
            self.assertTrue(self.user.is_active)
