from http import HTTPStatus

from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse
import parameterized

import accounts.models

__all__ = ()


class StaticURLTests(TestCase):
    fixtures = ["translator_request/fixtures/data.json"]

    def setUp(self):
        self.admin = accounts.models.User.objects.get(username="admin")
        self.user = accounts.models.User.objects.get(username="testuser")
        permission = Permission.objects.get(codename="view_translatorrequest")
        self.user.user_permissions.add(permission)
        self.client = Client()
        self.client.force_login(self.user)
        self.client_admin = Client()
        self.client_admin.force_login(self.admin)

    @parameterized.parameterized.expand(
        [
            ("translator_request:request_translator", {}),
            ("translator_request:translator_requests", {}),
            ("translator_request:translator_request", {"pk": 1}),
        ],
    )
    def test_translator_urls(self, url, kwargs):
        response = self.client.get(reverse(url, kwargs=kwargs))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @parameterized.parameterized.expand(
        [
            ("translator_request:accept_request", {"pk": 1}),
            ("translator_request:reject_request", {"pk": 1}),
        ],
    )
    def test_admin_urls(self, url, kwargs):
        response = self.client_admin.get(
            reverse(url, kwargs=kwargs),
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
