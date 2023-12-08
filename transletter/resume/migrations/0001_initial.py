# Generated by Django 4.2.8 on 2023-12-08 20:06

from django.db import migrations, models
import django.db.models.deletion
import resume.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

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