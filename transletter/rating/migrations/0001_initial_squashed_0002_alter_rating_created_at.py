# Generated by Django 4.2.8 on 2023-12-21 22:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    replaces = [
        ("rating", "0001_initial"),
        ("rating", "0002_alter_rating_created_at"),
    ]

    dependencies = [
        (
            "translation_request",
            "0002_alter_translationrequest_options_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Rating",
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
                ("text", models.TextField(verbose_name="text")),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Very poor"),
                            (2, "Poor"),
                            (3, "Normal"),
                            (4, "Good"),
                            (5, "Very good"),
                        ],
                        verbose_name="rating",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, null=True, verbose_name="created at"
                    ),
                ),
                (
                    "translation_request",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rating",
                        to="translation_request.translationrequest",
                    ),
                ),
            ],
            options={
                "verbose_name": "rating",
                "verbose_name_plural": "ratings",
            },
        ),
    ]
