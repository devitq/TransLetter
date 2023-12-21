from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
import parameterized

from accounts.models import User

__all__ = ()


class StaticURLTests(TestCase):
    fixtures = ["notifications/fixtures/initdata.json"]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(
            username="testuser",
        )

    def setUp(self):
        self.client.force_login(self.user)

    @parameterized.parameterized.expand(
        [
            ("notifications:all", {}),
        ],
    )
    def test_correct_urls(self, url, kwargs):
        response = self.client.get(reverse(url, kwargs=kwargs))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @parameterized.parameterized.expand(
        [
            ("notifications:read_notifications", {}),
        ],
    )
    def test_urls_405(self, url, kwargs):
        response = self.client.get(reverse(url, kwargs=kwargs))
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)


class UnauthorizedURLTests(TestCase):
    @parameterized.parameterized.expand(
        [
            ("notifications:all", {}),
        ],
    )
    def test_unauthorized_urls_302(self, url, kwargs):
        response = self.client.get(reverse(url, kwargs=kwargs))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
