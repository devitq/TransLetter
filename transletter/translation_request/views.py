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
from projects.models import Project
from translation_request.forms import CreateTranslationRequestForm, MessageForm
from translation_request.models import TranslationRequest

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
            .order_by("created_at")
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
        if form.is_valid():
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
                        "You have already sent simillar translation"
                        " request to this translator"
                    ),
                ),
            )
            return redirect(self.request.path)
        if form.instance.project not in owned_projects:
            messages.error(
                self.request,
                pgettext_lazy(
                    "error message in views",
                    "You do not own the selected project.",
                ),
            )
            return redirect(self.request.path)
        form.instance.status = "SE"
        return super().form_valid(form)

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
        if request.GET.get("to_status", None) is not None:
            translation_request.status = request.GET.get("to_status")
            translation_request.save()
        return redirect(
            reverse_lazy(
                "translation_request:translation_request_detail",
                kwargs={"pk": pk},
            ),
        )
