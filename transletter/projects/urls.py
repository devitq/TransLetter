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
    path(
        "<slug:slug>/",
        projects.views.ProjectPageView.as_view(),
        name="project_page",
    ),
    path(
        "<slug:slug>/members/",
        projects.views.ProjectMembersView.as_view(),
        name="project_members",
    ),
    path(
        "<slug:slug>/members/invite/",
        projects.views.AddProjectMemberView.as_view(),
        name="add_project_member",
    ),
    path(
        "<slug:slug>/members/invite/activate/<str:token>/",
        projects.views.ActivateProjectMemberView.as_view(),
        name="activate_project_member",
    ),
    path(
        "<slug:slug>/members/delete_member/<int:user_id>/",
        projects.views.DeleteProjectMemberView.as_view(),
        name="delete_project_member",
    ),
    path(
        "<slug:slug>/members/<int:user_id>/update_role/",
        projects.views.UpdateProjectMemberView.as_view(),
        name="update_project_member",
    ),
    path(
        "<slug:slug>/files/",
        projects.views.ProjectFilesView.as_view(),
        name="project_files",
    ),
    path(
        "<slug:slug>/files/upload_file/",
        projects.views.ProjectFilesUploadView.as_view(),
        name="project_files_upload",
    ),
    path(
        "<slug:slug>/files/<int:pk>/",
        projects.views.ProjectFileRowsView.as_view(),
        name="project_files_translate",
    ),
    path(
        "<slug:slug>/files/<int:file_pk>/<int:row_pk>/",
        projects.views.ProjectRowsTranslateView.as_view(),
        name="project_rows_translate",
    ),
]
