from django.contrib import admin

from projects import models


__all__ = ()


class ProjectLanguageFileInline(admin.TabularInline):
    model = models.ProjectLanguageFile
    extra = 1


class ProjectMembershipInline(admin.TabularInline):
    model = models.ProjectMembership
    extra = 1


class ProjectLanguageInline(admin.StackedInline):
    model = models.ProjectLanguage
    extra = 1


class ProjectLanguageAdmin(admin.ModelAdmin):
    inlines = (ProjectLanguageFileInline,)


class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProjectMembershipInline, ProjectLanguageInline]
    list_display = ("name",)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("name", "description", "slug"),
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)


admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.ProjectMembership)
admin.site.register(models.ProjectLanguage, ProjectLanguageAdmin)
