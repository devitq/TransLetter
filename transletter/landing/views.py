from http import HTTPStatus

from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView


__all__ = ()


class HomeView(TemplateView):
    template_name = "landing/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        features = [
            {"title": _("feature_1_title"), "content": _("feature_1_content")},
            {"title": _("feature_2_title"), "content": _("feature_2_content")},
            {"title": _("feature_3_title"), "content": _("feature_3_content")},
            {"title": _("feature_4_title"), "content": _("feature_4_content")},
            {"title": _("feature_5_title"), "content": _("feature_5_content")},
            {"title": _("feature_6_title"), "content": _("feature_6_content")},
        ]
        context["features"] = features

        return context


class Handler404View(TemplateView):
    template_name = "errors/404.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=HTTPStatus.NOT_FOUND)
