from django.urls import path

import projects.views

app_name = "projects"

urlpatterns = [
    path(
        "",
        projects.views.ProjectsListView.as_view(),
        name="projects_list",
    ),
    path(
        "create/",
        projects.views.CreateProjectView.as_view(),
        name="create_project",
    ),
]
