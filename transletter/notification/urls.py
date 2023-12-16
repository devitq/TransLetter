from django.urls import path

import notification.views

app_name = "notification"

urlpatterns = [
    path(
        "all/",
        notification.views.NotificationsView.as_view(),
        name="notifications",
    ),
]
