import shutil

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError, models
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import pgettext_lazy
from django.views.generic import CreateView, FormView, ListView, View
import jwt

import accounts.models
from projects.decorators import (
    can_access_project_decorator,
    project_admin_decorator,
    project_owner_decorator,
)
from projects.forms import (
    AddLanguageForm,
    AddProjectMemberForm,
    CreateProjectForm,
    ProjectAvatarChangeForm,
    ProjectChangeForm,
    TranslationFileForm,
    TranslationRowEditForm,
    UpdateProjectMemberForm,
    UpdateTranslationFileForm,
)
import projects.models
from projects.tokens import decode_token, generate_token
from projects.utils import (
    export_json_file,
    export_po_file,
    parse_file_and_create_translations,
)
from transletter.email import EmailThread


__all__ = ()


class ProjectsListView(LoginRequiredMixin, ListView):
    template_name = "projects/projects_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return (
            projects.models.Project.objects.filter(
                projectmembership__user=self.request.user,
            )
            .order_by("-projectmembership__role")
            .all()
        )


class CreateProjectView(LoginRequiredMixin, CreateView):
    template_name = "projects/create_project.html"
    form_class = CreateProjectForm

    def form_valid(self, form):
        project = form.save(commit=False)
        project.save()
        projects.models.ProjectMembership.objects.create(
            user=self.request.user,
            project=project,
            role="owner",
        )
        projects.models.ProjectLanguage.objects.create(
            project=project,
            lang_code=project.source_lang,
        )
        return redirect("projects:project_page", slug=project.slug)


@method_decorator(can_access_project_decorator, name="dispatch")
class ProjectMembersView(LoginRequiredMixin, ListView):
    template_name = "projects/project_members.html"
    context_object_name = "members"
    paginate_by = 10
    model = projects.models.ProjectMembership

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        return (
            projects.models.ProjectMembership.objects.filter(
                project__slug=slug,
            )
            .prefetch_related("user")
            .select_related("project")
            .select_related("user__account")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        active_user_role = (
            self.get_queryset()
            .filter(
                user_id=self.request.user.id,
                project__slug=slug,
            )
            .first()
        )
        context["active_user_role"] = active_user_role
        context["slug"] = slug
        return context


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
class AddProjectMemberView(LoginRequiredMixin, FormView):
    template_name = "projects/add_project_member.html"
    form_class = AddProjectMemberForm

    def form_valid(self, form):
        slug = self.kwargs.get("slug")
        project = get_object_or_404(projects.models.Project, slug=slug)

        data = form.cleaned_data
        try:
            user = accounts.models.User.objects.get(
                email=data["email"],
            )
        except accounts.models.User.DoesNotExist:
            messages.error(
                self.request,
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
                    kwargs={"token": token},
                ),
            )
            email_body = render_to_string(
                "projects/email/invitation.html",
                {
                    "header": data["email_header"],
                    "text": data["email_text"],
                    "link": link,
                },
            )
            email = EmailMultiAlternatives(
                subject="Invitation to project - TransLetter",
                body=email_body,
                from_email=settings.EMAIL,
                to=[data["email"]],
            )
            email.attach_alternative(email_body, "text/html")
            EmailThread(email).start()
            messages.success(
                self.request,
                pgettext_lazy(
                    "success message in views",
                    "The invitation has been sent",
                ),
            )
        return redirect("projects:project_members", slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        context["slug"] = slug
        return context


@method_decorator(project_admin_decorator, name="dispatch")
class DeleteProjectMemberView(LoginRequiredMixin, ListView):
    def get(self, request, slug, user_id):
        user = projects.models.ProjectMembership.objects.filter(
            user_id=request.user.id,
            project__slug=slug,
        ).first()

        user_for_delete = get_object_or_404(
            projects.models.ProjectMembership,
            project__slug=slug,
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
                        "You don't have permission to delete other admins",
                    ),
                )
        elif user_for_delete == "hired_translator":
            messages.error(
                request,
                pgettext_lazy(
                    "error message in views",
                    "Deleting hired translator only via TranslationRequest",
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
        messages.success(
            request,
            pgettext_lazy(
                "success message in views",
                "User successfully deleted from project",
            ),
        )
        return redirect("projects:project_members", slug)


@method_decorator(project_owner_decorator, name="dispatch")
class UpdateProjectMemberView(LoginRequiredMixin, ListView):
    template_name = "projects/update_project_member.html"
    form_class = UpdateProjectMemberForm

    def get(self, request, slug, user_id):
        membership = get_object_or_404(
            projects.models.ProjectMembership,
            project__slug=slug,
            user_id=user_id,
        )
        form = self.form_class(
            initial={
                "role": membership.role,
            },
        )
        return render(
            request,
            self.template_name,
            {"form": form, "slug": slug},
        )

    def post(self, request, slug, user_id):
        form = self.form_class(request.POST or None)
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
class ProjectLanguagesView(LoginRequiredMixin, ListView):
    template_name = "projects/project_languages.html"
    model = projects.models.ProjectLanguage
    context_object_name = "languages"

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        return (
            projects.models.ProjectLanguage.objects.filter(
                project__slug=slug,
            )
            .prefetch_related("files")
            .select_related("project")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        context["slug"] = slug
        return context


@method_decorator(project_admin_decorator, name="dispatch")
class AddProjectLangugeView(LoginRequiredMixin, CreateView):
    template_name = "projects/add_project_language.html"
    form_class = AddLanguageForm
    model = projects.models.ProjectLanguage

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        context["slug"] = slug
        return context

    def form_valid(self, form):
        try:
            slug = self.kwargs.get("slug")
            project = get_object_or_404(projects.models.Project, slug=slug)
            form.instance.project = project
            return super().form_valid(form)
        except IntegrityError:
            messages.error(
                self.request,
                pgettext_lazy(
                    "error message in views",
                    "This language is already exist!",
                ),
            )
            return render(
                self.request,
                self.template_name,
                {"form": form, "slug": slug},
            )

    def get_success_url(self):
        return reverse_lazy(
            "projects:project_languages",
            kwargs={"slug": self.kwargs.get("slug")},
        )


@method_decorator(can_access_project_decorator, name="dispatch")
class ProjectFilesView(LoginRequiredMixin, ListView):
    template_name = "projects/project_files.html"
    model = projects.models.TranslationFile
    context_object_name = "project_files"

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        return (
            projects.models.TranslationFile.objects.filter(
                project_language__project__slug=slug,
            )
            .select_related("project_language")
            .order_by("project_language__lang_code")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slug"] = self.kwargs.get("slug")
        return context


@method_decorator(project_admin_decorator, name="dispatch")
class ProjectFilesUploadView(LoginRequiredMixin, View):
    template_name = "projects/project_files_upload.html"
    form_class = TranslationFileForm

    def get(self, request, slug):
        project_languages = projects.models.ProjectLanguage.objects.filter(
            project__slug=slug,
        )
        form = self.form_class()
        form.fields["project_language"].queryset = project_languages
        return render(
            request,
            self.template_name,
            context={
                "form": form,
                "slug": slug,
            },
        )

    def post(self, request, slug):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            lang_object = form.cleaned_data["project_language"]
            file_object = projects.models.TranslationFile.objects.create(
                file=file,
                project_language=lang_object,
            )
            try:
                added, updated, deleted = parse_file_and_create_translations(
                    file_object,
                    str(file_object.file),
                )
            except Exception:
                messages.error(
                    request,
                    pgettext_lazy(
                        "error message in views",
                        "Failed to parse file!",
                    ),
                )
                file_object.delete()
                return redirect("projects:project_files_upload", slug)
            messages.success(
                request,
                pgettext_lazy(
                    "success message in views",
                    (
                        "File successfully parsed!\n"
                        f"Added: {added}\n"
                        f"Updated: {updated}\n"
                        f"Deleted: {deleted}\n"
                    ),
                ),
            )
            return redirect("projects:project_files", slug)

        project_languages = projects.models.ProjectLanguage.objects.filter(
            project__slug=slug,
        )
        return render(
            request,
            self.template_name,
            context={
                "project_languages": project_languages,
                "form": form,
                "slug": slug,
            },
        )


@method_decorator(project_admin_decorator, name="dispatch")
class UpdateTranslationFileView(LoginRequiredMixin, View):
    template_name = "projects/project_files_upload.html"
    form_class = UpdateTranslationFileForm

    def get(self, request, slug, file_id):
        file_object = get_object_or_404(
            projects.models.TranslationFile,
            id=file_id,
        )

        form = self.form_class(instance=file_object)
        return render(
            request,
            self.template_name,
            context={
                "form": form,
                "slug": slug,
                "file_id": file_id,
            },
        )

    def post(self, request, slug, file_id):
        file_object = get_object_or_404(
            projects.models.TranslationFile,
            id=file_id,
        )

        form = self.form_class(
            request.POST,
            request.FILES,
            instance=file_object,
        )
        if form.is_valid():
            form.save()
            try:
                added, updated, deleted = parse_file_and_create_translations(
                    file_object,
                    str(file_object.file),
                )
            except Exception:
                messages.error(
                    request,
                    pgettext_lazy(
                        "error message in views",
                        "Failed to parse file!",
                    ),
                )
                return redirect(
                    "projects:update_translation_file",
                    slug,
                    file_id,
                )

            messages.success(
                request,
                pgettext_lazy(
                    "success message in views",
                    (
                        "File successfully parsed!\n"
                        f"Added: {added}\n"
                        f"Updated: {updated}\n"
                        f"Deleted: {deleted}\n"
                    ),
                ),
            )
            return redirect("projects:project_files", slug)

        return render(
            request,
            self.template_name,
            context={
                "form": form,
                "slug": slug,
                "file_id": file_id,
            },
        )


@method_decorator(can_access_project_decorator, name="dispatch")
class ProjectFileRowsView(LoginRequiredMixin, ListView):
    template_name = "projects/project_rows.html"
    model = projects.models.TranslationRow
    paginate_by = 12

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return projects.models.TranslationRow.objects.filter(
            translation_file_id=pk,
        ).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slug"] = self.kwargs.get("slug")
        return context


@method_decorator(can_access_project_decorator, name="dispatch")
class ProjectRowsTranslateView(LoginRequiredMixin, FormView):
    template_name = "projects/project_row_translate.html"
    form_class = TranslationRowEditForm

    def get(self, request, slug, file_pk, row_pk):
        row = get_object_or_404(
            projects.models.TranslationRow,
            translation_file_id=file_pk,
            id=row_pk,
        )
        form = TranslationRowEditForm(instance=row)
        return render(
            request,
            self.template_name,
            context={
                "form": form,
                "slug": slug,
            },
        )

    def post(self, request, slug, file_pk, row_pk):
        row = get_object_or_404(
            projects.models.TranslationRow,
            translation_file_id=file_pk,
            id=row_pk,
        )
        form = TranslationRowEditForm(request.POST, instance=row)
        form.save()
        # fmt: off
        (
            form.instance.
            translation_file
            .project_language
            .project.last_activity
        ) = timezone.now()
        # fmt: on
        form.instance.translation_file.project_language.project.save()
        return redirect("projects:project_files_translate", slug, file_pk)


@method_decorator(project_admin_decorator, name="dispatch")
class ProjectFileExportView(LoginRequiredMixin, ListView):
    def get(self, request, slug, file_pk):
        file_object = projects.models.TranslationFile.objects.get(id=file_pk)
        rows = projects.models.TranslationRow.objects.filter(
            translation_file_id=file_object.id,
        ).all()
        shutil.rmtree(
            settings.MEDIA_ROOT
            / f"projects/{str(file_object.project_language.project_id)}"
            / "export/",
            ignore_errors=True,
        )
        if str(file_object.file).endswith(".po"):
            export_filename = export_po_file(
                rows,
                file_object,
                slug,
            )
        elif str(file_object.file).endswith(".json"):
            export_filename = export_json_file(
                rows,
                file_object,
                slug,
            )
        return FileResponse(open(export_filename, "rb"), as_attachment=True)
