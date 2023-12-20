from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse
import parameterized

import accounts.models
from translator_request.models import TranslatorRequest

__all__ = ()


class TranslationRequestCreationTests(TestCase):
    fixtures = ["translator_request/fixtures/initdata.json"]

    def setUp(self):
        self.user_with_request = accounts.models.User.objects.get(
            username="with_translatorrequest_user",
        )
        self.account = accounts.models.Account.objects.get(
            user_id=self.user_with_request.id,
        )
        self.account.native_lang = "ru"
        self.account.languages = '["en", "pt"]'
        self.account.save()

        self.user = accounts.models.User.objects.get(
            username="no_translatorrequest_user",
        )
        permission = Permission.objects.get(codename="view_translatorrequest")
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)
        self.client_with_request = Client()
        self.client_with_request.force_login(self.user_with_request)

    @parameterized.parameterized.expand(
        [
            (
                {
                    "user_form-first_name": ["John"],
                    "user_form-last_name": ["Smith"],
                    "account_form-languages": ["en"],
                    "resume_form-about": ["Some about text"],
                },
            ),
            (
                {
                    "user_form-first_name": ["John"],
                    "user_form-last_name": ["Smith"],
                    "account_form-native_lang": ["ru"],
                    "resume_form-about": ["Some about text"],
                },
            ),
            (
                {
                    "user_form-first_name": ["John"],
                    "user_form-last_name": ["Smith"],
                    "account_form-native_lang": ["ru"],
                    "account_form-languages": ["en"],
                },
            ),
            (
                {
                    "account_form-native_lang": ["ru"],
                    "account_form-languages": ["en"],
                    "resume_form-about": ["Some about text"],
                },
            ),
        ],
    )
    def test_no_valid_form(self, form_data):
        url = "translator_request:request_translator"
        count = TranslatorRequest.objects.count()
        self.client.post(reverse(url), data=form_data)
        self.assertEqual(
            count,
            TranslatorRequest.objects.count(),
        )

    def test_valid_creation_form(self):
        form_data = {
            "user_form-first_name": ["John"],
            "user_form-last_name": ["Smith"],
            "account_form-native_lang": ["ru"],
            "account_form-languages": ["en"],
            "resume_form-about": ["Some about text"],
        }
        url = "translator_request:request_translator"
        count = TranslatorRequest.objects.count()
        self.client.post(reverse(url), data=form_data, follow=True)
        self.assertNotEqual(
            count,
            TranslatorRequest.objects.count(),
        )

    def test_valid_edit_form(self):
        url = "translator_request:request_translator"
        count = TranslatorRequest.objects.count()

        form_data = {
            "user_form-first_name": ["John"],
            "user_form-last_name": ["Smith"],
            "account_form-native_lang": ["fr"],
            "account_form-languages": ["en"],
            "resume_form-about": ["Some about text"],
        }
        self.client_with_request.post(
            reverse(url),
            data=form_data,
            follow=True,
        )
        self.account.refresh_from_db()
        self.assertEqual(
            self.account.native_lang,
            "fr",
        )
        self.assertEqual(count, TranslatorRequest.objects.count())

    def test_no_valid_edit_form(self):
        url = "translator_request:request_translator"

        user = accounts.models.User.objects.create_user(
            "man",
            "man@mail.ru",
            "111",
        )
        user.account.native_lang = "ru"
        user.account.save()
        TranslatorRequest.objects.create(user=user, status="UR")
        count = TranslatorRequest.objects.count()
        client = Client()
        client.force_login(user)
        form_data = {
            "user_form-first_name": ["John"],
            "user_form-last_name": ["Smith"],
            "account_form-native_lang": ["fr"],
            "account_form-languages": ["en"],
            "resume_form-about": ["Some about text"],
        }
        client.post(
            reverse(url),
            data=form_data,
            follow=True,
        )
        self.assertNotEqual(
            user.account.native_lang,
            "fr",
        )
        self.assertEqual(count, TranslatorRequest.objects.count())
