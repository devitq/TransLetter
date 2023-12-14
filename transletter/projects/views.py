from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import CreateView, ListView

from projects.forms import CreateProjectForm
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
            return redirect("project_detail", pk=project.pk)
        return render(request, self.template_name, {"form": form})
