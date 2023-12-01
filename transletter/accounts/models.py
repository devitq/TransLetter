import sys

import django.contrib.auth.models
from django.db import models

__all__ = ()


class UserManager(django.contrib.auth.models.UserManager):
    def get_queryset(self):
        return super().get_queryset().select_related("account")

    def by_mail(self, email):
        return self.get_queryset().get(email=email)

    def active(self):
        return self.get_queryset().filter(is_active=True)

    def normalize_email(self, email):
        if email:
            email = email.lower()
            login, domain = email.split("@")
            if "+" in login:
                login = login.split("+")[0]
            domain = domain.replace("ya.ru", "yandex.ru")
            if domain == "yandex.ru":
                login = login.replace(".", "-")
            elif domain == "gmail.com":
                login = login.replace(".", "")
            email = f"{login}@{domain}"

        return super().normalize_email(email)


class Account(models.Model):
    def get_path_for_file(self, filename):
        return f"avatars/{self.user_id}/{filename}"

    user = models.OneToOneField(
        django.contrib.auth.models.User,
        related_name="account",
        on_delete=models.CASCADE,
    )
    avatar = models.ImageField(
        "аватарка",
        null=True,
        blank=True,
        upload_to=get_path_for_file,
    )
    attempts_count = models.PositiveIntegerField(
        "количество попыток входа",
        editable=False,
        default=0,
        blank=True,
    )

    class Meta:
        verbose_name = "профиль"
        verbose_name_plural = "профили"


class User(django.contrib.auth.models.User):
    class Meta:
        proxy = True

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
