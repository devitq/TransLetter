from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.translation import pgettext_lazy
from django.views.generic import CreateView

from rating.forms import RatingForm
from rating.models import Rating
from translation_request.models import TranslationRequest

__all__ = ()


class RatingCreateView(LoginRequiredMixin, CreateView):
    template_name = "rating/create_rating.html"
    form_class = RatingForm
    success_url = reverse_lazy("translation_request:translation_request_list")

    def dispatch(self, request, *args, **kwargs):
        translation_request = get_object_or_404(
            TranslationRequest.objects.select_related("translator"),
            pk=self.kwargs.get("pk"),
        )
        if translation_request.status != "CL":
            raise Http404()
        rating = Rating.objects.filter(translation_request=translation_request)
        if rating:
            raise Http404()
        if request.user != translation_request.author:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        translation_request = get_object_or_404(
            TranslationRequest.objects.select_related("translator"),
            pk=self.kwargs.get("pk"),
        )
        rating = Rating.objects.filter(translation_request=translation_request)
        if rating:
            messages.error(
                self.request,
                pgettext_lazy(
                    "error message rating is created",
                    "Rating already exists",
                ),
            )
            return self.render_form(form)
        form.instance.translation_request = translation_request
        messages.success(
            self.request,
            pgettext_lazy(
                "success message in rating create view",
                "Rating successfully created",
            ),
        )
        return super().form_valid(form)

    def render_form(self, form):
        return render(
            self.request,
            template_name=self.template_name,
            context={"form": form},
        )
