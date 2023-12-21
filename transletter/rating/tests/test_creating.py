from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
import parameterized

from accounts.models import User
from rating.models import Rating

__all__ = ()


class RatingCreatingTests(TestCase):
    test_order = "defined"
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

    def test_valid_creation_form(self):
        form_data = {
            "text": "Some rating text",
            "rating": 3,
        }
        count = Rating.objects.count()
        url = reverse("rating:create_rating", kwargs={"pk": 1})
        response = self.client.post(url, form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Rating.objects.count(), count + 1)

    @parameterized.parameterized.expand(
        [
            (
                {
                    "text": "Some rating text",
                    "rating": 0,
                },
            ),
            (
                {
                    "text": "Some rating text",
                    "rating": 0,
                },
            ),
            (
                {
                    "text": "Some rating text",
                },
            ),
            (
                {
                    "text": "",
                    "rating": 3,
                },
            ),
        ],
    )
    def test_no_valid_form(self, form_data):
        count = Rating.objects.count()
        url = reverse("rating:create_rating", kwargs={"pk": 1})
        response = self.client.post(url, form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Rating.objects.count(), count)
