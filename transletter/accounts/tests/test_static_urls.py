from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
import parameterized

__all__ = ()


class StaticURLTests(TestCase):
    @parameterized.parameterized.expand(
        [
            ("accounts:login",),
            ("accounts:signup",),
            ("accounts:password_reset"),
            ("accounts:request_activation"),
        ],
    )
    def test_urls(self, url):
        response = Client().get(reverse(url))
        self.assertEqual(response.status_code, HTTPStatus.OK)
