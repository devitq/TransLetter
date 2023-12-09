from django.urls import path

import translationrequest.views

app_name = "translation_request"

urlpatterns = [
    path(
        "request_translator/",
        translationrequest.views.RequestTranslatorView.as_view(),
        name="request_translator",
    ),
]
