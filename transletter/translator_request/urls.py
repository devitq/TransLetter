from django.urls import path

import translator_request.views

app_name = "translator_request"

urlpatterns = [
    path(
        "request_translator/",
        translator_request.views.RequestTranslatorView.as_view(),
        name="request_translator",
    ),
    path(
        "translator_requests/",
        translator_request.views.TranslatorRequestsView.as_view(),
        name="translator_requests",
    ),
]
