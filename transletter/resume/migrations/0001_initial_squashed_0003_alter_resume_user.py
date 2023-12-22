# Generated by Django 4.2.8 on 2023-12-21 22:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import resume.models


class Migration(migrations.Migration):
    replaces = [
        ("resume", "0001_initial"),
        ("resume", "0002_resume_user"),
        ("resume", "0003_alter_resume_user"),
    ]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Resume",
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
                    "about",
                    models.TextField(
                        blank=True, null=True, verbose_name="about"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="resume",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "resume",
                "verbose_name_plural": "resumes",
            },
        ),
        migrations.CreateModel(
            name="ResumeFile",
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
                    "file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=resume.models.ResumeFile._get_upload_path,
                        verbose_name="file",
                    ),
                ),
                (
                    "resume",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="files",
                        related_query_name="files",
                        to="resume.resume",
                        verbose_name="resume",
                    ),
                ),
            ],
            options={
                "verbose_name": "resume file",
                "verbose_name_plural": "resume files",
            },
        ),
    ]