from django.urls import path

import resume.views

app_name = "resume"

urlpatterns = [
    path(
        "<int:pk>/file/<int:file_id>/download/",
        resume.views.DownloadView.as_view(),
        name="download_file",
    ),
    path(
        "<int:pk>/file/<int:file_id>/delete/",
        resume.views.DeleteView.as_view(),
        name="delete_file",
    ),
]
