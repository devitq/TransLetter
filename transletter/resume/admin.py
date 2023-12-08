from django.contrib import admin

from resume import models

__all__ = ()


class FilesInline(admin.TabularInline):
    model = models.ResumeFile
    extra = 1


class ResumeAdmin(admin.ModelAdmin):
    list_display = [
        models.Resume.about.field.name,
    ]
    inlines = [
        FilesInline,
    ]


admin.site.register(models.Resume, ResumeAdmin)
admin.site.register(models.ResumeFile)
