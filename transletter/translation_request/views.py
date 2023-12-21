from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.translation import pgettext_lazy
from django.views.generic import CreateView, DetailView, ListView, View

from accounts.models import User
from projects.models import Project, ProjectLanguage, ProjectMembership
from translation_request.forms import CreateTranslationRequestForm, MessageForm
from translation_request.models import (
    TranslationRequest,
    TranslationRequestMessage,
)

__all__ = ()


class TranslationRequestListView(LoginRequiredMixin, ListView):
    template_name = "translation_request/translation_request_list.html"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        return (
            TranslationRequest.objects.get_queryset()
            .filter(
                models.Q(author=user) | models.Q(translator=user),
            )
            .order_by("-created_at")
            .all()
        )


class TranslationRequestView(LoginRequiredMixin, DetailView):
    template_name = "translation_request/translation_request.html"
    model = TranslationRequest
    context_object_name = "translation_request"

    def get(self, request, pk, *args, **kwargs):
        translation_request = self.get_translation_request(pk)
        self.check_permissions(request.user, translation_request)
        form = MessageForm()
        return render(
            template_name=self.template_name,
            context={"translation_request": translation_request, "form": form},
            request=request,
        )

    def post(self, request, pk, *args, **kwargs):
        translation_request = self.get_translation_request(pk)
        self.check_permissions(request.user, translation_request)
        form = MessageForm(request.POST)
        if form.is_valid() and translation_request.status not in "RJCL":
            form.instance.author = request.user
            form.instance.translation_request = translation_request
            form.instance.save()
            form = MessageForm()
        translation_request.refresh_from_db()
        return render(
            template_name=self.template_name,
            context={"translation_request": translation_request, "form": form},
            request=request,
        )

    def get_translation_request(self, pk):
        translation_request = (
            TranslationRequest.objects.get_translation_request_detail(pk)
        )
        if translation_request is None:
            raise Http404()
        return translation_request

    def check_permissions(self, user, translation_request):
        if (
            user != translation_request.author
            and user != translation_request.translator
        ):
            raise PermissionDenied()


class CreateTranslationRequest(LoginRequiredMixin, CreateView):
    template_name = "translation_request/create_translation_request.html"
    form_class = CreateTranslationRequestForm
    success_url = reverse_lazy("translation_request:translation_request_list")

    def dispatch(self, request, translator_id, *args, **kwargs):
        translator = get_object_or_404(
            User.objects.filter(account__is_translator=True),
            pk=translator_id,
        )
        if translator == request.user:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.translator = get_object_or_404(
            User.objects.filter(account__is_translator=True),
            pk=self.kwargs["translator_id"],
        )
        form.instance.author = self.request.user

        owned_projects = Project.objects.filter(
            projectmembership__user=self.request.user,
            projectmembership__role="owner",
        )
        if form.instance.project not in owned_projects:
            messages.error(
                self.request,
                pgettext_lazy(
                    "error message in views",
                    "You do not own the selected project.",
                ),
            )
            return self.render_form(form)

        translation_request_exist = TranslationRequest.objects.filter(
            author=self.request.user,
            status__in=["SE", "AC", "IP", "FN"],
            project=form.instance.project,
            translator=form.instance.translator,
        ).exists()
        if translation_request_exist:
            messages.error(
                self.request,
                pgettext_lazy(
                    "error message in views",
                    (
                        "You have already sent a similar "
                        "translation request to this translator"
                    ),
                ),
            )
            return self.render_form(form)

        form.instance.languages = form.cleaned_data["languages"]
        translator_languages = set(form.instance.translator.account.languages)
        project_languages = set(
            ProjectLanguage.objects.filter(
                project__in=owned_projects,
            ).values_list("lang_code", flat=True),
        )
        selected_languages = set(form.instance.languages)
        if not selected_languages.issubset(
            translator_languages,
        ) or not selected_languages.issubset(project_languages):
            messages.error(
                self.request,
                pgettext_lazy(
                    "error message in views",
                    (
                        "The translator does not translate into these "
                        "languages, or they do not exist in your project"
                    ),
                ),
            )
            return self.render_form(form)

        form.instance.status = "SE"

        if form.instance.price > self.request.user.account.balance:
            messages.error(
                self.request,
                pgettext_lazy(
                    "error message in views",
                    "Insufficient funds on the account.",
                ),
            )
            return self.render_form(form)
        self.request.user.account.balance -= form.instance.price
        self.request.user.account.save()
        form.instance.translator.add_notification(
            "Invitation to the Project",
            f"{form.instance.translator.username}, you have been invited to"
            f' join the project "{form.instance.project.name}"'
            "as a translator.",
        )
        return super().form_valid(form)

    def render_form(self, form):
        return render(
            self.request,
            template_name=self.template_name,
            context={"form": form},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class UpdateTranslationRequestStatusView(LoginRequiredMixin, View):
    def dispatch(self, request, pk, *args, **kwargs):
        translation_request = get_object_or_404(
            TranslationRequest,
            pk=pk,
        )
        if (
            translation_request.translator != request.user
            and translation_request.author != request.user
        ):
            raise PermissionDenied()
        return super().dispatch(
            request,
            pk,
            translation_request,
            *args,
            **kwargs,
        )

    def get(
        self,
        request,
        pk,
        translation_request,
        *args,
        **kwargs,
    ):
        to_status = request.GET.get("to_status", None)
        if to_status is not None:
            if request.user == translation_request.translator:
                if translation_request.status == "SE" and to_status == "AC":
                    translation_request.status = to_status
                    translation_request.save()
                    TranslationRequestMessage.objects.create(
                        translation_request=translation_request,
                        author=None,
                        content="The translator has accepted request",
                    )
                elif translation_request.status == "SE" and to_status == "RJ":
                    translation_request.status = to_status
                    translation_request.save()
                    translation_request.author.account.balance += (
                        translation_request.price
                    )
                    translation_request.author.account.save()
                    TranslationRequestMessage.objects.create(
                        translation_request=translation_request,
                        author=None,
                        content="The translator has rejected request",
                    )
                elif translation_request.status == "AC" and to_status == "IP":
                    translation_request.status = to_status
                    translation_request.save()
                    ProjectMembership.objects.create(
                        user=translation_request.translator,
                        project=translation_request.project,
                        role="hired_translator",
                    )
                    TranslationRequestMessage.objects.create(
                        translation_request=translation_request,
                        author=None,
                        content=(
                            "The translator has been added to the "
                            '<a href="#">project</a> and can begin work'
                        ),
                    )
                elif translation_request.status == "AC" and to_status == "RJ":
                    translation_request.status = to_status
                    translation_request.save()
                    translation_request.author.account.balance += (
                        translation_request.price
                    )
                    translation_request.author.account.save()
                    TranslationRequestMessage.objects.create(
                        translation_request=translation_request,
                        author=None,
                        content="The translator has rejected request",
                    )
                elif translation_request.status == "IP" and to_status == "FN":
                    translation_request.status = to_status
                    translation_request.save()
                    TranslationRequestMessage.objects.create(
                        translation_request=translation_request,
                        author=None,
                        content="The translator marked his work as completed",
                    )
            else:
                if translation_request.status == "AC" and to_status == "RJ":
                    translation_request.status = to_status
                    translation_request.save()
                    translation_request.author.account.balance += (
                        translation_request.price
                    )
                    translation_request.author.account.save()
                    TranslationRequestMessage.objects.create(
                        translation_request=translation_request,
                        author=None,
                        content="The author rejected the request",
                    )
                elif translation_request.status == "FN" and to_status == "IP":
                    translation_request.status = to_status
                    translation_request.save()
                    TranslationRequestMessage.objects.create(
                        translation_request=translation_request,
                        author=None,
                        content=(
                            "The author sent the translator's "
                            "work for revision"
                        ),
                    )
                elif translation_request.status == "FN" and to_status == "CL":
                    translation_request.status = to_status
                    translation_request.save()
                    translation_request.translator.account.balance += (
                        translation_request.price
                    )
                    translation_request.translator.account.save()
                    try:
                        ProjectMembership.objects.get(
                            project=translation_request.project,
                            user=translation_request.translator,
                        ).delete()
                    except ProjectMembership.DoesNotExist:
                        pass
                    TranslationRequestMessage.objects.create(
                        translation_request=translation_request,
                        author=None,
                        content=(
                            "The author closed the request,"
                            " the translator was rewarded"
                        ),
                    )
        return redirect(
            reverse_lazy(
                "translation_request:translation_request_detail",
                kwargs={"pk": pk},
            ),
        )
