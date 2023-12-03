from django.urls import path

from landing import views

app_name = "landing"
urlpatterns = [
    path("", views.HomeView.as_view(), name="index"),
    path("about/", views.AboutView.as_view(), name="about"),
]
