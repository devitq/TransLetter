from django.conf import settings
from django.contrib import admin
import django.contrib.auth.urls
from django.urls import include, path

from landing import views

__all__ = ()

handler404 = views.Handler404View.as_view()
handler403 = views.Handler403View.as_view()
urlpatterns = [
    path("", include("landing.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("translator/request/", include("translator_request.urls")),
    path("auth/", include("accounts.urls")),
    path("auth/", include(django.contrib.auth.urls), name="auth_default"),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
