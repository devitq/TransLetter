import asyncio
import sys

from asgiref.sync import async_to_sync
import django.contrib.auth.models
from django.db import models
from django.utils.translation import pgettext_lazy
from djmoney.models.fields import MoneyField
import email_normalize

from notifications.models import Notification
from resume.models import ResumeFile
from transletter.utils import get_available_langs

__all__ = ("User",)


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class UserManager(django.contrib.auth.models.UserManager):
    def get_queryset(self):
        return super().get_queryset().select_related("account")

    def by_mail(self, email):
        return self.get_queryset().get(email=email)

    def active(self):
        return self.get_queryset().filter(is_active=True)

    def translators(self):
        return self.get_queryset().filter(account__is_translator=True)

    def translator(self, username):
        return (
            self.get_queryset()
            .select_related("account")
            .select_related("resume")
            .prefetch_related(
                models.Prefetch(
                    "resume__files",
                    queryset=ResumeFile.objects.all(),
                ),
            )
            .filter(
                username=username,
                account__is_translator=True,
            )
        )

    def normalize_email(self, email):
        domains_replacement = {
            "yandex.ru": [
                "ya.ru",
                "yandex.by",
                "yandex.com",
                "yandex.kz",
                "яндекс.рф",
            ],
            "protonmail.com": ["pm.me", "protonmail.ch"],
            "gmail.com": ["googlemail.com"],
        }
        if email:

            async def normalize_inner(email: str):
                normalizer = email_normalize.Normalizer()
                return await normalizer.normalize(email)

            email = email.lower()
            sync_normalize = async_to_sync(normalize_inner)
            email = sync_normalize(email).normalized_address

            login, domain = email.split("@")

            for key, replacements in domains_replacement.items():
                if domain in replacements:
                    domain = key
                    break
            if domain == "yandex.ru":
                login = login.replace(".", "-")
            elif domain == "protonmail.com":
                login = (
                    login.replace(".", "").replace("-", "").replace("_", "")
                )
            email = f"{login}@{domain}"

            return super().normalize_email(email)

        return super().normalize_email(email)


class Account(models.Model):
    def get_path_for_file(self, filename):
        return f"avatars/{self.user_id}/{filename}"

    LANGUAGES = get_available_langs()

    user = models.OneToOneField(
        django.contrib.auth.models.User,
        related_name="account",
        on_delete=models.CASCADE,
    )
    avatar = models.ImageField(
        pgettext_lazy("avatar field name", "avatar"),
        null=True,
        blank=True,
        upload_to=get_path_for_file,
    )
    attempts_count = models.PositiveIntegerField(
        pgettext_lazy("attemps count field name", "attemps count"),
        editable=False,
        default=0,
        blank=True,
    )
    is_translator = models.BooleanField(
        pgettext_lazy("is translator count field name", "is translator"),
        default=False,
    )
    blocked = models.BooleanField(
        verbose_name=pgettext_lazy("blocked field name", "blocked"),
        default=False,
    )
    blocked_reason = models.TextField(
        verbose_name=pgettext_lazy(
            "blocked reason field name",
            "blocked reason",
        ),
        null=True,
        blank=True,
    )
    native_lang = models.CharField(
        pgettext_lazy("native lang field name", "native language"),
        max_length=10,
        choices=LANGUAGES,
        null=True,
        blank=True,
    )
    languages = models.JSONField(
        pgettext_lazy("languages field name", "languages"),
        default=list,
        blank=True,
    )
    balance = MoneyField(
        pgettext_lazy("balance field name", "balance"),
        max_digits=19,
        decimal_places=4,
        default_currency="USD",
        currency_choices=(("USD", "Dollar"),),
        default=0,
    )
    website = models.URLField(
        pgettext_lazy("website count field name", "website"),
        null=True,
        blank=True,
    )
    github = models.SlugField(
        pgettext_lazy("github count field name", "github"),
        null=True,
        blank=True,
    )
    about = models.TextField(
        pgettext_lazy("about field name", "about"),
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.user.username

    class Meta:
        verbose_name = pgettext_lazy("verbose name for accounts", "account")
        verbose_name_plural = pgettext_lazy(
            "verbose name plural for accounts",
            "accounts",
        )


class User(django.contrib.auth.models.User):
    class Meta:
        proxy = True

    def add_notification(self, title, content):
        Notification.objects.create(
            user=self,
            title=title,
            content=content,
        )

    objects = UserManager()


def create_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)


def normalize_user_email(sender, instance, **kwargs):
    instance.email = User.objects.normalize_email(instance.email)


models.signals.post_save.connect(create_account, sender=User)
models.signals.post_save.connect(
    create_account,
    sender=django.contrib.auth.models.User,
)
models.signals.pre_save.connect(normalize_user_email, sender=User)
models.signals.pre_save.connect(
    normalize_user_email,
    sender=django.contrib.auth.models.User,
)

if "makemigrations" not in sys.argv and "migrate" not in sys.argv:
    User._meta.get_field("email")._unique = True
    User._meta.get_field("email").blank = False
    User._meta.get_field("email").null = False
