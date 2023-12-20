from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.translation import pgettext_lazy

from projects import models
from projects.utils import parse_file_and_create_translations


__all__ = ()


class ProjectTranslationFileInline(admin.TabularInline):
    model = models.TranslationFile
    extra = 1


class ProjectMembershipInline(admin.TabularInline):
    model = models.ProjectMembership
    extra = 1


class ProjectLanguageInline(admin.StackedInline):
    model = models.ProjectLanguage
    extra = 1


class ProjectLanguageAdmin(admin.ModelAdmin):
    inlines = (ProjectTranslationFileInline,)


class TranslationFileAdmin(admin.ModelAdmin):
    actions = ("create_translation_rows_from_file",)

    def create_translation_rows_from_file(self, request, queryset):
        for language_file in queryset:
            try:
                parse_file_and_create_translations(
                    language_file,
                    str(language_file.file),
                )
                self.message_user(
                    request,
                    f"{pgettext_lazy('TranslationRows created for')} "
                    f"{language_file.file}",
                    level="SUCCESS",
                )
            except ValidationError as e:
                self.message_user(
                    request,
                    f"{pgettext_lazy('Error:')} {str(e)}",
                    level="ERROR",
                )

    create_translation_rows_from_file.short_description = pgettext_lazy(
        "Create TranslationRows from file",
    )


class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProjectMembershipInline, ProjectLanguageInline]
    list_display = ("name",)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("name", "description", "slug", "source_lang"),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)


admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.ProjectMembership)
admin.site.register(models.TranslationRow)
admin.site.register(models.TranslationComment)
admin.site.register(models.TranslationFile, TranslationFileAdmin)
admin.site.register(models.ProjectLanguage, ProjectLanguageAdmin)
