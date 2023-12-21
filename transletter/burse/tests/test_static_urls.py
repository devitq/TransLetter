from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
import parameterized

from accounts.models import User

__all__ = ()


class StaticURLTests(TestCase):
    test_order = "defined"

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
        )
        cls.translator1 = User.objects.create_user(
            username="translator1",
        )
        cls.translator1.account.is_translator = True
        cls.translator1.account.save()

    def setUp(self):
        self.client.force_login(self.user)

    @parameterized.parameterized.expand(
        [
            ("burse:translators", {}),
            ("burse:translator", {"username": "translator1"}),
        ],
    )
    def test_correct_urls(self, url, kwargs):
        response = self.client.get(reverse(url, kwargs=kwargs))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @parameterized.parameterized.expand(
        [
            ("burse:translator", {"username": "1"}),
            ("burse:translator", {"username": "asfawefa"}),
            ("burse:translator", {"username": "testuser"}),
        ],
    )
    def test_uncorrect_urls(self, url, kwargs):
        response = self.client.get(reverse(url, kwargs=kwargs))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
