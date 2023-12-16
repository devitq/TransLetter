from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from accounts.models import User
from translation_request.forms import CreateTranslationRequestForm
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
        translation_request = (
            TranslationRequest.objects.get_translation_request_detail(pk)
        )
        if translation_request is None:
            raise Http404()

        user = request.user
        if (
            user != translation_request.author
            and user != translation_request.translator
        ):
            raise PermissionDenied()

        return render(
            template_name=self.template_name,
            context={"translation_request": translation_request},
            request=request,
        )


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
        form.instance.author = self.request.user
        form.instance.translator = get_object_or_404(
            User.objects.filter(account__is_translator=True),
            pk=self.kwargs["translator_id"],
        )
        form.instance.status = "SE"
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
