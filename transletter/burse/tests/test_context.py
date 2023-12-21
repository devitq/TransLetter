from django.test import TestCase
from django.urls import reverse

from accounts.models import Account, User

__all__ = ()


class TranalatorsViewContextTest(TestCase):
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
        cls.translator2 = User.objects.create_user(
            username="translator2",
        )
        cls.translator2.account.is_translator = True
        cls.translator2.account.save()

    def setUp(self):
        self.client.force_login(self.user)

    def test_translators_page_context(self):
        response = self.client.get(
            reverse("burse:translators"),
        )
        context = response.context

        self.assertIn("translators", context)
        translators = context["translators"]

        self.assertIn(self.translator1, translators)
        self.assertIn(self.translator2, translators)
        self.assertNotIn(self.user, translators)

    def test_context_types(self):
        response = self.client.get(reverse("burse:translators"))
        translators = response.context["translators"]
        for translator in translators:
            self.assertIsInstance(translator, User)
            self.assertIsInstance(translator.account, Account)


class TranalatorViewContextTest(TestCase):
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

    def test_translator_page_context(self):
        response = self.client.get(
            reverse(
                "burse:translator",
                kwargs={"username": self.translator1.username},
            ),
        )
        context = response.context

        self.assertIn("translator", context)
        translator = context["translator"]

        self.assertEqual(self.translator1, translator)

    def test_page_context_values(self):
        response = self.client.get(
            reverse(
                "burse:translator",
                kwargs={"username": self.translator1.username},
            ),
            follow=True,
        )
        translator = response.context["translator"]
        list_in = ("id", "username", "email")
        for el in list_in:
            self.assertIn(el, translator.__dict__)
