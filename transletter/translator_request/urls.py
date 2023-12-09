from django.urls import path

import translator_request.views

app_name = "translator_request"

urlpatterns = [
    path(
        "request_translator/",
        translator_request.views.RequestTranslatorView.as_view(),
        name="request_translator",
    ),
]
