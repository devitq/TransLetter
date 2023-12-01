from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
import parameterized


__all__ = ()


class StaticUrlTests(TestCase):
    @parameterized.parameterized.expand(
        ("landing:index",),
    )
    def test_endpoints(self, url):
        response = Client().get(reverse(url))
        self.assertEqual(response.status_code, HTTPStatus.OK)
