# Generated by Django 4.2.8 on 2023-12-21 22:28

from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields


class Migration(migrations.Migration):
    replaces = [
        ("translation_request", "0001_initial"),
        (
            "translation_request",
            "0002_alter_translationrequest_options_and_more",
        ),
        (
            "translation_request",
            "0003_alter_translationrequestmessage_timestamp",
        ),
        ("translation_request", "0004_translationrequest_languages_and_more"),
        (
            "translation_request",
            "0005_alter_translationrequest_created_at_and_more",
        ),
    ]

    dependencies = [
        ("projects", "0001_initial"),
        ("accounts", "0005_alter_account_native_lang"),
        (
            "accounts",
            "0006_alter_account_balance_alter_account_balance_currency",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="TranslationRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, null=True, verbose_name="created at"
                    ),
                ),
                (
                    "closed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="closed at"
                    ),
                ),
                ("text", models.TextField(verbose_name="text")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("SE", "Sent"),
                            ("AC", "Accepted"),
                            ("RJ", "Rejected"),
                            ("IP", "In progress"),
                            ("FN", "Finished"),
                            ("CL", "Closed"),
                        ],
                        max_length=2,
                        verbose_name="status",
                    ),
                ),
                (
                    "price",
                    djmoney.models.fields.MoneyField(
                        currency_choices=(("USD", "Dollar"),),
                        decimal_places=4,
                        default_currency="USD",
                        max_digits=19,
                        verbose_name="price",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translation_requests_authored",
                        to="accounts.user",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="projects.project",
                    ),
                ),
                (
                    "translator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translation_requests_translated",
                        to="accounts.user",
                    ),
                ),
                (
                    "price_currency",
                    djmoney.models.fields.CurrencyField(
                        choices=[("USD", "Dollar")],
                        default="USD",
                        editable=False,
                        max_length=3,
                    ),
                ),
                (
                    "languages",
                    models.JSONField(
                        blank=True, default=list, verbose_name="languages"
                    ),
                ),
            ],
            options={
                "verbose_name": "translation request",
                "verbose_name_plural": "translation requests",
            },
        ),
        migrations.CreateModel(
            name="TranslationRequestMessage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField(verbose_name="content")),
                (
                    "timestamp",
                    models.DateTimeField(
                        auto_now_add=True, null=True, verbose_name="timestamp"
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.user",
                    ),
                ),
                (
                    "translation_request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        related_query_name="translation_request",
                        to="translation_request.translationrequest",
                    ),
                ),
            ],
            options={
                "verbose_name": "translation request message",
                "verbose_name_plural": "translation request messages",
            },
        ),
    ]
