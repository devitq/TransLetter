from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
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

    def get_initial(self):
        translation_request = get_object_or_404(
            TranslationRequest.objects.select_related("translator"),
            pk=self.kwargs.get("pk"),
        )
        rating = Rating.objects.filter(translation_request=translation_request)
        if rating:
            raise Http404()
        return {
            "user": self.request.user,
            "translator": translation_request.translator,
            "translation_request": translation_request,
        }

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
            return redirect(
                reverse(
                    "translation_request:translation_request_detail",
                    {"pk": self.kwargs.get("pk")},
                ),
            )
        messages.success(
            self.request,
            pgettext_lazy(
                "success message in rating create view",
                "Rating successfully created",
            ),
        )
        form.instance.user = self.request.user
        form.instance.translator = translation_request.translator
        form.instance.translation_request = translation_request
        return super().form_valid(form)
