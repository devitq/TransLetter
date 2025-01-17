from django.urls import path

import translator_request.views

app_name = "translator_request"

urlpatterns = [
    path(
        "my/",
        translator_request.views.RequestTranslatorView.as_view(),
        name="request_translator",
    ),
    path(
        "all/",
        translator_request.views.TranslatorRequestsView.as_view(),
        name="translator_requests",
    ),
    path(
        "<int:pk>/",
        translator_request.views.TranslatorRequestView.as_view(),
        name="translator_request",
    ),
    path(
        "<int:pk>/accept/",
        translator_request.views.AcceptRequestView.as_view(),
        name="accept_request",
    ),
    path(
        "<int:pk>/reject/",
        translator_request.views.RejectRequestView.as_view(),
        name="reject_request",
    ),
]
