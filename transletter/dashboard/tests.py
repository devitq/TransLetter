from django.test import Client, TestCase
from django.urls import reverse

import accounts.models

__all__ = ()


class StaticURLTests(TestCase):
    fixtures = ["translator_request/fixtures/initdata.json"]

    def setUp(self):
        self.admin = accounts.models.User.objects.get(username="admin")
        self.client = Client()
        self.client.force_login(self.admin)

    def test_urls(self):
        self.client.get(reverse("dashboard:index"))
