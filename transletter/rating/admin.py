from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from rating import models
from rating.forms import RatingAdminForm

__all__ = ()


class RatingAdmin(admin.ModelAdmin):
    form = RatingAdminForm

    list_display = [
        "title",
        models.Rating.user.field.name,
        models.Rating.translator.field.name,
        models.Rating.translation_request.field.name,
        models.Rating.rating.field.name,
        models.Rating.created_at.field.name,
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + (
                models.Rating.created_at.field.name,
            )
        return self.readonly_fields

    def title(self, obj):
        return obj

    title.short_description = _("Title")


admin.site.register(models.Rating, RatingAdmin)
