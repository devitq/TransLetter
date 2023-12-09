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
    path(
        "translator_request/<int:pk>/",
        translator_request.views.TranslatorRequestView.as_view(),
        name="translator_request",
    ),
    path(
        "accept_request/<int:pk>/",
        translator_request.views.AcceptRequestView.as_view(),
        name="accept_request",
    ),
    path(
        "reject_request/<int:pk>/",
        translator_request.views.RejectRequestView.as_view(),
        name="reject_request",
    ),
]
