from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
import django.contrib.auth.urls
from django.urls import include, path

from landing import views

__all__ = ()

handler404 = views.Handler404View.as_view()
handler403 = views.Handler403View.as_view()
handler500 = views.Handler500View.as_view()

urlpatterns = [
    path("", include("landing.urls")),
    path("burse/", include("burse.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("translator_request/", include("translator_request.urls")),
    path("projects/", include("projects.urls")),
    path("translation_request/", include("translation_request.urls")),
    path("rating/", include("rating.urls")),
    path("resume/", include("resume.urls")),
    path("auth/", include("accounts.urls")),
    path("auth/", include(django.contrib.auth.urls), name="auth_default"),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
]

if settings.MEDIA_ROOT:
    urlpatterns += static(
        settings.MEDIA_URL + "avatars",
        document_root=settings.MEDIA_ROOT / "avatars",
    )
    urlpatterns += static(
        settings.MEDIA_URL + "cache",
        document_root=settings.MEDIA_ROOT / "cache",
    )

if settings.DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
