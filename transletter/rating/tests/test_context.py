from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from rating.models import Rating
import translation_request.models

__all__ = ()


class TranalatorViewContextTest(TestCase):
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
        cls.rating1 = Rating.objects.create(
            translation_request_id=1,
            text="Some rating text",
            rating=4,
        )
        cls.rating2 = Rating.objects.create(
            translation_request_id=2,
            text="Some other rating text",
            rating=3,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_page_context(self):
        response = self.client.get(
            reverse(
                "burse:translator",
                kwargs={"username": self.translator.username},
            ),
        )
        context = response.context

        self.assertIn("ratings", context)
        ratings = context["ratings"]

        self.assertIn(self.rating1, ratings)
        self.assertNotIn(self.rating2, ratings)

    def test_page_context_values(self):
        response = self.client.get(
            reverse(
                "burse:translator",
                kwargs={"username": self.translator.username},
            ),
        )
        rating = response.context["ratings"].first()
        list_in = ("id", "text", "rating")
        for el in list_in:
            self.assertIn(el, rating.__dict__)

    def test_page_context_types(self):
        response = self.client.get(
            reverse(
                "burse:translator",
                kwargs={"username": self.translator.username},
            ),
        )
        ratings = response.context["ratings"]
        for rating in ratings:
            self.assertIsInstance(rating, Rating)
            self.assertIsInstance(
                rating.translation_request,
                translation_request.models.TranslationRequest,
            )
