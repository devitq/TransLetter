from django.contrib import admin

from translation_request.models import (
    TranslationRequest,
    TranslationRequestMessage,
)


__all__ = ()


class TranslationRequestMessageInline(admin.StackedInline):
    model = TranslationRequestMessage
    extra = 0
    show_change_link = True


class TranslationRequestAdmin(admin.ModelAdmin):
    inlines = (TranslationRequestMessageInline,)


admin.site.register(TranslationRequest, TranslationRequestAdmin)
admin.site.register(TranslationRequestMessage)
