from django.urls import path

import dashboard.views

app_name = "dashboard"

urlpatterns = [
    path("", dashboard.views.IndexView.as_view(), name="index"),
    path(
        "account/edit/",
        dashboard.views.AccountEditView.as_view(),
        name="edit_account",
    ),
    path(
        "account/avatar/edit/",
        dashboard.views.AccountEditView.as_view(),
        name="edit_avatar",
    ),
    path(
        "projects/",
        dashboard.views.ProjectsView.as_view(),
        name="projects",
    ),
]
