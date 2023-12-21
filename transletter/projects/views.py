from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import pgettext_lazy
from django.views.generic import CreateView, ListView, View
import jwt

import accounts.models
from projects.decorators import (
    can_access_project_decorator,
    project_admin_decorator,
    project_owner_decorator,
)
from projects.forms import (
    AddProjectMemberForm,
    CreateProjectForm,
    ProjectAvatarChangeForm,
    ProjectChangeForm,
    UpdateProjectMemberForm,
)
import projects.models
from projects.tokens import decode_token, generate_token
from projects.utils import export_po_file, parse_file_and_create_translations
from transletter.email import EmailThread


__all__ = ()


class ProjectsListView(LoginRequiredMixin, ListView):
    template_name = "projects/projects_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return projects.models.Project.objects.filter(
            projectmembership__user=self.request.user,
        ).all()


class CreateProjectView(LoginRequiredMixin, CreateView):
    template_name = "projects/create_project.html"

    def get(self, request):
        form = CreateProjectForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = CreateProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            return redirect("projects:project_page", slug=project.slug)
        return render(request, self.template_name, {"form": form})


@method_decorator(can_access_project_decorator, name="dispatch")
class ProjectMembersView(LoginRequiredMixin, ListView):
    template_name = "projects/project_members.html"

    def get(self, request, slug):
        members = (
            projects.models.ProjectMembership.objects.filter(
                project__slug=slug,
            )
            .prefetch_related("user")
            .select_related("project")
            .select_related("user__account")
        )
        active_user_role = members.filter(
            user_id=request.user.id,
            project__slug=slug,
        ).first()
        return render(
            request,
            self.template_name,
            context={
                "members": members,
                "active_user_role": active_user_role,
                "slug": slug,
            },
        )


@method_decorator(project_admin_decorator, name="dispatch")
class ChangeProjectView(LoginRequiredMixin, View):
    template_name = "projects/edit_project.html"

    def get(self, request, slug, *args, **kwargs):
        project = get_object_or_404(
            projects.models.Project,
            slug=slug,
        )
        project_form = ProjectChangeForm(instance=project)
        avatar_form = ProjectAvatarChangeForm(instance=project)
        return render(
            request,
            self.template_name,
            {
                "project_form": project_form,
                "avatar_form": avatar_form,
            },
        )

    def post(self, request, slug, *args, **kwargs):
        project = get_object_or_404(
            projects.models.Project,
            slug=slug,
        )
        project_form = ProjectChangeForm(request.POST, instance=project)
        avatar_form = ProjectAvatarChangeForm(
            request.POST,
            request.FILES,
            instance=project,
        )

        if project_form.is_valid() and avatar_form.is_valid():
            project_form.save()
            avatar_form.save()

            messages.success(
                request,
                pgettext_lazy(
                    "success message in views",
                    "Project updated successfully!",
                ),
            )
            return redirect("projects:edit_project", project.slug)

        return render(
            request,
            self.template_name,
            {
                "project_form": project_form,
                "avatar_form": avatar_form,
            },
        )


@method_decorator(project_admin_decorator, name="dispatch")
class AddProjectMemberView(LoginRequiredMixin, CreateView):
    template_name = "projects/add_project_member.html"

    def get(self, request, slug):
        form = AddProjectMemberForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, slug):
        form = AddProjectMemberForm(request.POST)
        project = get_object_or_404(
            projects.models.Project,
            slug=slug,
        )
        if form.is_valid():
            data = form.cleaned_data
            try:
                user = accounts.models.User.objects.get(
                    email=data["email_address"],
                )
            except accounts.models.User.DoesNotExist:
                messages.error(
                    request,
                    pgettext_lazy(
                        "error message in views",
                        "There is no user with this email address",
                    ),
                )
            else:
                token = generate_token(user.username, project.id)
                link = self.request.build_absolute_uri(
                    reverse(
                        "projects:activate_project_member",
                        kwargs={"slug": slug, "token": token},
                    ),
                )
                email_body = render_to_string(
                    "projects/email/invitation.html",
                    {
                        "header": data["mail_header"],
                        "text": data["mail_text"],
                        "link": link,
                    },
                )
                email = EmailMultiAlternatives(
                    subject="Invitation to project - TransLetter",
                    body=email_body,
                    from_email=settings.EMAIL,
                    to=[data["email_address"]],
                )
                email.attach_alternative(email_body, "text/html")
                EmailThread(email).start()
                messages.success(
                    request,
                    pgettext_lazy(
                        "success message in views",
                        "The invitation has been sent",
                    ),
                )
        return redirect("projects:project_members", slug)


@method_decorator(project_admin_decorator, name="dispatch")
class DeleteProjectMemberView(LoginRequiredMixin, ListView):
    def get(self, request, slug, user_id):
        user = projects.models.ProjectMembership.objects.filter(
            user_id=request.user.id,
            project__slug=slug,
        ).first()
        if not user:
            messages.error(
                request,
                pgettext_lazy(
                    "error message in views",
                    "You don't have permission to do this",
                ),
            )
            return redirect("projects:project_members", slug)
        user_for_delete = projects.models.ProjectMembership.objects.get(
            user_id=user_id,
        ).role
        if user_for_delete not in ["hired_translator", "owner"]:
            if (
                (not user_for_delete == "admin" and user.role == "admin")
                or user_for_delete == "static_translator"
                or (user_for_delete == "admin" and user.role == "owner")
            ):
                projects.models.ProjectMembership.objects.filter(
                    project__slug=slug,
                    user_id=user_id,
                ).delete()
            elif user_for_delete == "admin" and user.role == "admin":
                messages.error(
                    request,
                    pgettext_lazy(
                        "error message in views",
                        "You don't have permission to do delete other admins",
                    ),
                )
        elif user_for_delete == "hired_translator":
            messages.error(
                request,
                pgettext_lazy(
                    "error message in views",
                    "Deleting hired only via TranslationRequest",
                ),
            )
        elif user_for_delete == "owner":
            messages.error(
                request,
                pgettext_lazy(
                    "error message in views",
                    "It is forbidden to delete the owner",
                ),
            )
        return redirect("projects:project_members", slug)


@method_decorator(project_owner_decorator, name="dispatch")
class UpdateProjectMemberView(LoginRequiredMixin, ListView):
    template_name = "projects/update_project_member.html"

    def get(self, request, slug, user_id):
        membership = get_object_or_404(
            projects.models.ProjectMembership,
            project__slug=slug,
            user_id=user_id,
        )
        form = UpdateProjectMemberForm(
            initial={
                "role": membership.role,
            },
        )
        return render(request, self.template_name, {"form": form, "slug": slug})

    def post(self, request, slug, user_id):
        form = UpdateProjectMemberForm(request.POST or None)
        if form.is_valid():
            data = form.cleaned_data
            user = projects.models.ProjectMembership.objects.filter(
                project__slug=slug,
                user_id=user_id,
            ).first()
            user.role = data["role"]
            user.save()
        return redirect("projects:project_members", slug)


class ActivateProjectMemberView(LoginRequiredMixin, ListView):
    def get(self, request, token):
        try:
            username, project_id = decode_token(token)
            user = get_object_or_404(
                accounts.models.User,
                username=username,
            )
            project = get_object_or_404(
                projects.models.Project,
                pk=project_id,
            )
            if request.user != user:
                raise PermissionDenied()
            membership = projects.models.ProjectMembership.objects.filter(
                user_id=user.id,
                project=project,
            ).first()
            if membership is None:
                member = projects.models.ProjectMembership(
                    project=project,
                    user_id=user.id,
                    role="static_translator",
                )
                member.save()
                messages.success(
                    request,
                    pgettext_lazy(
                        "success message in views",
                        "User successfully added to project",
                    ),
                )
            else:
                messages.error(
                    request,
                    pgettext_lazy(
                        "error message in views",
                        "Existing member.",
                    ),
                )
        except jwt.InvalidTokenError:
            messages.error(
                request,
                pgettext_lazy("error message in views", "Invalid link!"),
            )
        return redirect("projects:project_members", project.slug)


@method_decorator(can_access_project_decorator, name="dispatch")
class ProjectPageView(LoginRequiredMixin, ListView):
    template_name = "projects/project_page.html"

    def get(self, request, slug):
        project = get_object_or_404(
            projects.models.Project.objects.prefetch_related(
                models.Prefetch(
                    "languages",
                    projects.models.ProjectLanguage.objects.all(),
                ),
            ).prefetch_related("members"),
            slug=slug,
        )
        return render(
            request,
            self.template_name,
            context={
                "project_info": project,
            },
        )


@method_decorator(can_access_project_decorator, name="dispatch")
class ProjectFilesView(LoginRequiredMixin, ListView):
    template_name = "projects/project_files.html"

    def get(self, request, slug):
        project_files = projects.models.TranslationFile.objects.filter(
            project_language__project__slug=slug,
        )
        return render(
            request,
            self.template_name,
            context={
                "project_files": project_files,
                "slug": slug,
            },
        )


@method_decorator(project_admin_decorator, name="dispatch")
class ProjectFilesUploadView(LoginRequiredMixin, ListView):
    template_name = "projects/project_files_upload.html"

    def get(self, request, slug):
        project_files = projects.models.TranslationFile.objects.filter(
            project_language__project__slug=slug,
        )
        project_languages = projects.models.ProjectLanguage.objects.filter(
            project__slug=slug,
        )
        return render(
            request,
            self.template_name,
            context={
                "project_files": project_files,
                "project_languages": project_languages,
            },
        )

    def post(self, request, slug):
        if request.FILES:
            file = request.FILES["filename"]
            lang_object = projects.models.ProjectLanguage.objects.filter(
                lang_code=request.POST["lang"],
                project__slug=slug,
            ).first()
            file_object = projects.models.TranslationFile.objects.create(
                file=file,
                project_language_id=lang_object.id,
            )
            parse_file_and_create_translations(
                file_object,
                str(file_object.file),
            )
        return redirect("projects:project_files", slug)


@method_decorator(can_access_project_decorator, name="dispatch")
class ProjectFileRowsView(LoginRequiredMixin, ListView):
    template_name = "projects/project_file_translate.html"

    def get(self, request, slug, pk):
        project_rows = projects.models.TranslationRow.objects.filter(
            translation_file_id=pk,
        )
        return render(
            request,
            self.template_name,
            context={
                "project_rows": project_rows,
                "slug": slug,
            },
        )


@method_decorator(can_access_project_decorator, name="dispatch")
class ProjectRowsTranslateView(LoginRequiredMixin, ListView):
    template_name = "projects/project_row_translate.html"

    def get(self, request, slug, file_pk, row_pk):
        try:
            row = projects.models.TranslationRow.objects.get(
                translation_file_id=file_pk,
                id=row_pk,
            )
        except projects.models.TranslationRow.DoesNotExist:
            return redirect("projects:project_files_translate", slug, file_pk)
        return render(
            request,
            self.template_name,
            context={
                "row_info": row,
            },
        )

    def post(self, request, slug, file_pk, row_pk):
        msg_str = request.POST["msg_str"]
        row_object = projects.models.TranslationRow.objects.get(
            translation_file_id=file_pk,
            id=row_pk,
        )
        row_object.msg_str = msg_str
        row_object.save()
        return redirect("projects:project_files_translate", slug, file_pk)


@method_decorator(can_access_project_decorator, name="dispatch")
class ProjectFileExportView(LoginRequiredMixin, ListView):
    def get(self, request, slug, file_pk):
        file_object = projects.models.TranslationFile.objects.get(id=file_pk)
        rows = projects.models.TranslationRow.objects.filter(
            translation_file_id=file_object.id,
        ).all()
        filename = projects.models.TranslationFile.objects.get(id=file_pk).file
        export_filename = export_po_file(
            rows,
            str(file_object.file),
            slug,
            filename,
        )
        return FileResponse(open(export_filename, "rb"), as_attachment=True)
