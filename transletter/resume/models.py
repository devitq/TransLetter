from django.db import models
from django.utils.translation import gettext_lazy as _, pgettext_lazy

__all__ = ()


class ResumeManager(models.Manager):
    def with_files(self):
        return (
            self.get_queryset()
            .prefetch_related(
                models.Prefetch(
                    Resume.files.field.name,
                    ResumeFile.objects.only(ResumeFile.file.field.name),
                ),
            )
            .only(
                Resume.about.field.name,
                f"{Resume.files.field.name}__{ResumeFile.file.field.name}",
            )
        )


class Resume(models.Model):
    objects = ResumeManager()

    about = models.TextField(
        pgettext_lazy("about field name", "about"),
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        verbose = _(
            (
                f"{self.user.username}"
            ),
        )
        return str(verbose)

    class Meta:
        verbose_name = pgettext_lazy("verbose name for resume", "resume")
        verbose_name_plural = pgettext_lazy(
            "verbose name plural for resume",
            "resumes",
        )


class ResumeFile(models.Model):
    def _get_upload_path(self, filename):
        return f"resume_files/{self.resume_id}/{filename}"

    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="files",
        related_query_name="files",
        verbose_name=pgettext_lazy("resume field name", "resume"),
    )
    file = models.FileField(
        pgettext_lazy("file field name", "file"),
        upload_to=_get_upload_path,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        verbose = _(
            (
                f"{self.resume.user.username}'s"
                " resume file"
            ),
        )
        return str(verbose)

    class Meta:
        verbose_name = pgettext_lazy(
            "verbose name for resume file",
            "resume file",
        )
        verbose_name_plural = pgettext_lazy(
            "verbose name plural for resume file",
            "resume files",
        )
