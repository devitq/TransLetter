from django.contrib import admin

from translation_request.models import (
    TranslationRequest,
    TranslationRequestMessage,
)

admin.site.register(TranslationRequest)
admin.site.register(TranslationRequestMessage)
