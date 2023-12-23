from pathlib import Path
import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import pgettext_lazy

from accounts.models import User
from transletter.utils import get_available_langs
from transletter.validators import validate_translation_file

__all__ = ()


class Project(models.Model):
    def get_path_for_file(self, filename):
        return f"projects/{self.pk}/avatar/{filename}"

    avatar = models.ImageField(
        pgettext_lazy("avatar field name", "avatar"),
        upload_to=get_path_for_file,
        null=True,
        blank=True,
    )
    name = models.CharField(
        pgettext_lazy("name field name", "name"),
        max_length=255,
    )
    description = models.TextField(
        pgettext_lazy("description field name", "description"),
        null=True,
        blank=True,
    )
    slug = models.SlugField(
        pgettext_lazy("slug field name", "slug"),
        max_length=200,
        unique=True,
        help_text="a-z, 0-9, _, -",
    )
    created_at = models.DateTimeField(
        pgettext_lazy("created at field name", "created at"),
        auto_now_add=True,
        null=True,
    )
    last_activity = models.DateTimeField(
        pgettext_lazy("last activity field name", "last activity"),
        auto_now_add=True,
        null=True,
    )
    public = models.BooleanField(
        pgettext_lazy("public field name", "public"),
        default=False,
    )
    source_lang = models.CharField(
        pgettext_lazy("source language field name", "source language"),
        max_length=10,
        choices=get_available_langs(),
    )
    members = models.ManyToManyField(
        User,
        through="ProjectMembership",
        related_name="projects",
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = pgettext_lazy("verbose name for project", "project")
        verbose_name_plural = pgettext_lazy(
            "verbose name plural for projects",
            "projects",
        )


class ProjectMembership(models.Model):
    ROLES = (
        ("owner", pgettext_lazy("role name", "Owner")),
        ("admin", pgettext_lazy("role name", "Administrator")),
        ("static_translator", pgettext_lazy("role name", "Static translator")),
        ("hired_translator", pgettext_lazy("role name", "Hired translator")),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)

    def __str__(self) -> str:
        return f"{self.project} -> {self.user.username}"


class ProjectLanguage(models.Model):
    LANGUAGES = get_available_langs()

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="languages",
    )
    lang_code = models.CharField(
        pgettext_lazy("project languge lang code field name", "language"),
        max_length=10,
        choices=LANGUAGES,
    )

    def __str__(self) -> str:
        language_dict = dict(self.LANGUAGES)
        return language_dict.get(self.lang_code, "")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "lang_code"],
                name="unique_lang",
            ),
        ]


class TranslationFile(models.Model):
    def get_path_for_file(self, filename):
        return (
            f"projects/{self.project_language.project_id}"
            f"/{self.project_language.lang_code}/"
            f"{str(uuid.uuid4())}/{filename}"
        )

    project_language = models.ForeignKey(
        ProjectLanguage,
        on_delete=models.CASCADE,
        related_name="files",
    )
    metadata = models.JSONField(null=True, blank=True)
    file = models.FileField(
        upload_to=get_path_for_file,
        validators=[
            FileExtensionValidator(
                allowed_extensions=settings.TRANSLATION_FILE_FORMATS,
            ),
            validate_translation_file,
        ],
    )

    def filename(self):
        return Path(self.file.name).name

    def __str__(self) -> str:
        return self.filename()


class TranslationRow(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    msg_context = models.TextField(null=True, blank=True)
    msg_id = models.TextField()
    msg_str = models.TextField()
    occurrences = models.JSONField(default=list, null=True, blank=True)
    translation_file = models.ForeignKey(
        TranslationFile,
        on_delete=models.CASCADE,
        related_name="rows",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "msg_id",
                    "msg_context",
                    "translation_file",
                ],
                name="unique_row",
            ),
        ]


class TranslationComment(models.Model):
    translation_row = models.ForeignKey(
        TranslationRow,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    comment = models.TextField(
        pgettext_lazy("comment field name", "comment"),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="translation_comments",
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
