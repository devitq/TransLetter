from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
import parameterized

from accounts.models import User

__all__ = ()


class StaticURLTests(TestCase):
    fixtures = ["rating/fixtures/initdata.json"]

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(
            username="testuser",
        )
        cls.translator = User.objects.get(
            username="translator1",
        )
        cls.translator.account.is_translator = True
        cls.translator.account.save()

    def setUp(self):
        self.client.force_login(self.user)

    @parameterized.parameterized.expand(
        [
            ("rating:create_rating", {"pk": 1}),
        ],
    )
    def test_correct_urls(self, url, kwargs):
        response = self.client.get(reverse(url, kwargs=kwargs))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class UnauthorizedURLTests(TestCase):
    @parameterized.parameterized.expand(
        [
            ("rating:create_rating", {"pk": 1}),
        ],
    )
    def test_unauthorized_urls_404(self, url, kwargs):
        response = self.client.get(reverse(url, kwargs=kwargs))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
