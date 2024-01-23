from django.contrib import admin

from projects import models


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
    list_display = ("lang_code", "project")


class TranslationFileAdmin(admin.ModelAdmin):
    list_display = ("filename", "project_language")


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
