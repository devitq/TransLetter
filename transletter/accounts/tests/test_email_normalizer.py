from django.test import TestCase
import parameterized

import accounts.models

__all__ = ()


class EmailNormalizerTests(TestCase):
    @parameterized.parameterized.expand(
        (
            ("u_s.e-rname@pm.me", "username@protonmail.com"),
            ("user-name@protonmail.ch", "username@protonmail.com"),
            (
                "itqHfsdFE..W.Fs.fdev+fsdf@ya.ru",
                "itqhfsdfe--w-fs-fdev@yandex.ru",
            ),
            (
                "itqHfsdFE..W.Fs.fdev+fsdf@gmail.com",
                "itqhfsdfewfsfdev@gmail.com",
            ),
            ("User.namE+tag@gmail.com", "username@gmail.com"),
            ("u.sern.ame+tag+tag+tag@googlemail.com", "username@gmail.com"),
            ("username-tag@yahoo.com", "username@yahoo.com"),
            ("user.name@яндекс.рф", "user-name@yandex.ru"),
            ("user-name@yandex.com", "user-name@yandex.ru"),
            ("username@ya.ru", "username@yandex.ru"),
        ),
    )
    def test_email_normalizer(self, email, normalized_email_should):
        normalized_email = accounts.models.User.objects.normalize_email(
            email,
        )
        self.assertEqual(normalized_email, normalized_email_should)
