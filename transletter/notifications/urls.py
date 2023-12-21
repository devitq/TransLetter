from django.urls import path

import notifications.api
import notifications.views

app_name = "notifications"

urlpatterns = [
    path(
        "",
        notifications.views.NotificationsView.as_view(),
        name="all",
    ),
    path(
        "read/",
        notifications.api.read_notifications,
        name="read_notifications",
    ),
]
