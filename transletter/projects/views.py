from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.signing import BadSignature, TimestampSigner
from django.shortcuts import redirect, render
from django.views.generic import CreateView, ListView

import accounts.models
from projects.forms import (
    AddProjectMemberForm,
    CreateProjectForm,
    UpdateProjectMemberForm,
)
import projects.models

__all__ = ()


class ProjectsListView(LoginRequiredMixin, ListView):
    template_name = "projects/projects_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return projects.models.Project.objects.all()


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
            return redirect("projects:project_page", pk=project.pk)
        return render(request, self.template_name, {"form": form})


class ProjectMembersView(LoginRequiredMixin, ListView):
    template_name = "projects/project_members.html"

    def get(self, request, pk):
        members = projects.models.ProjectMembership.objects.filter(
            project_id=pk,
        )
        active_user_role = projects.models.ProjectMembership.objects.filter(
            user_id=request.user.id,
        ).first()
        return render(
            request,
            self.template_name,
            context={
                "members": members,
                "active_user_role": active_user_role,
                "pk": pk,
            },
        )


class AddProjectMemberView(LoginRequiredMixin, ListView):
    template_name = "projects/add_project_member.html"

    def get(self, request, pk):
        user = projects.models.ProjectMembership.objects.filter(
            user_id=request.user.id,
        ).first()
        if user.role not in ["owner", "admin"]:
            messages.error(
                request,
                "You don't have permission to do this",
            )
            return redirect("projects:project_members", pk)
        form = AddProjectMemberForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk):
        form = AddProjectMemberForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            signer = TimestampSigner()
            try:
                user = accounts.models.User.objects.get(
                    email=data["email_address"],
                )
            except accounts.models.User.DoesNotExist:
                messages.error(
                    request,
                    "There is no user with this email address",
                )
            else:
                link = (
                    "http://127.0.0.1:8000/projects/1/"
                    "members/add_member/activate/"
                )
                msg = (
                    f"{data['mail_header']}\n\n"
                    f"{data['mail_text']}\n\n"
                    f"{link}{signer.sign(user.username)}"
                )
                send_mail(
                    subject="Inviting to the project",
                    message=msg,
                    recipient_list=[data["email_address"]],
                    from_email=settings.EMAIL,
                    fail_silently=False,
                )
                messages.success(
                    request,
                    "The invitation has been sent",
                )
        return redirect("projects:project_members", pk)


class DeleteProjectMemberView(LoginRequiredMixin, ListView):
    def get(self, request, pk, user_id):
        user = projects.models.ProjectMembership.objects.filter(
            user_id=request.user.id,
        ).first()
        if user.role not in ["owner", "admin"]:
            messages.error(
                request,
                "You don't have permission to do this",
            )
            return redirect("projects:project_members", pk)
        user_for_delete = projects.models.ProjectMembership.objects.get(
            user_id=user_id,
        ).role
        if user_for_delete not in ["hired_translator", "owner"]:
            if not user_for_delete == "admin" and user.role == "admin":
                projects.models.ProjectMembership.objects.filter(
                    project_id=pk,
                    user_id=user_id,
                ).delete()
            else:
                messages.error(
                    request,
                    "You don't have permission to do delete other admins",
                )
        elif user_for_delete == "hired_translator":
            messages.error(
                request,
                "Deleting hired only via TransRequest",
            )
        elif user_for_delete == "owner":
            messages.error(
                request,
                "It is forbidden to delete the owner",
            )
        return redirect("projects:project_members", pk)


class UpdateProjectMemberView(LoginRequiredMixin, ListView):
    template_name = "projects/update_project_member.html"

    def get(self, request, pk, user_id):
        user = projects.models.ProjectMembership.objects.filter(
            user_id=request.user.id,
        ).first()
        if user.role != "owner":
            messages.error(
                request,
                "You don't have permission to do this",
            )
            return redirect("projects:project_members", pk)
        form = UpdateProjectMemberForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, pk, user_id):
        form = UpdateProjectMemberForm(request.POST or None)
        if form.is_valid():
            data = form.cleaned_data
            user = projects.models.ProjectMembership.objects.filter(
                project_id=pk,
                user_id=user_id,
            ).first()
            user.role = data["role"]
            user.save()
        return redirect("projects:project_members", pk)


class ActivateProjectMemberView(LoginRequiredMixin, ListView):
    def get(self, request, pk, token):
        signer = TimestampSigner()
        try:
            username = signer.unsign(
                token,
            )
        except BadSignature:
            messages.error(
                request,
                "Not correct link",
            )
        else:
            user = accounts.models.User.objects.get(username=username)
            try:
                projects.models.ProjectMembership.objects.get(
                    user_id=user.id,
                    project_id=pk,
                )
            except projects.models.ProjectMembership.DoesNotExist:
                member = projects.models.ProjectMembership(
                    project_id=pk,
                    user_id=user.id,
                    role="static_translator",
                )
                member.save()
                messages.success(
                    request,
                    "Account successfully activated",
                )
            else:
                messages.success(
                    request,
                    "Existing member",
                )
        return redirect("projects:project_members", pk)


class ProjectPageView(LoginRequiredMixin, ListView):
    template_name = "projects/project_page.html"

    def get(self, request, pk):
        project = projects.models.Project.objects.get(id=pk)
        return render(
            request,
            self.template_name,
            context={
                "project_info": project,
            },
        )
