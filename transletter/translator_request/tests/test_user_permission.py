from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
import parameterized

import accounts.models

__all__ = ()


class UnauthorizedURLTests(TestCase):
    fixtures = ["translator_request/fixtures/initdata.json"]

    @parameterized.parameterized.expand(
        [
            ("translator_request:request_translator", {}),
            ("translator_request:translator_request", {"pk": 1}),
            ("translator_request:accept_request", {"pk": 1}),
            ("translator_request:reject_request", {"pk": 1}),
        ],
    )
    def test_unauthorize_urls_302(self, url, kwargs):
        response = self.client.get(reverse(url, kwargs=kwargs))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    @parameterized.parameterized.expand(
        [
            ("translator_request:translator_requests", {}),
        ],
    )
    def test_unauthorize_urls_403(self, url, kwargs):
        response = self.client.get(reverse(url, kwargs=kwargs))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class NoPermissionsURLTests(TestCase):
    fixtures = ["translator_request/fixtures/initdata.json"]

    def setUp(self):
        self.user = accounts.models.User.objects.get(username="testuser")
        self.client.force_login(self.user)

    @parameterized.parameterized.expand(
        [
            ("translator_request:translator_requests", {}),
            ("translator_request:translator_request", {"pk": 1}),
            ("translator_request:accept_request", {"pk": 1}),
            ("translator_request:reject_request", {"pk": 1}),
        ],
    )
    def test_translator_urls(self, url, kwargs):
        response = self.client.get(reverse(url, kwargs=kwargs))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
