from django.urls import path

import translation_request.views

app_name = "translation_request"

urlpatterns = [
    path(
        "all/",
        translation_request.views.TranslationRequestListView.as_view(),
        name="translation_request_list",
    ),
    path(
        "<int:pk>/",
        translation_request.views.TranslationRequestView.as_view(),
        name="translation_request_detail",
    ),
    path(
        "new/<int:translator_id>",
        translation_request.views.CreateTranslationRequest.as_view(),
        name="create_translation_request",
    ),
    path(
        "<int:pk>/update/status/",
        translation_request.views.UpdateTranslationRequestStatusView.as_view(),
        name="update_translation_request_status",
    ),
]
