from django.urls import path

import burse.views

app_name = "burse"

urlpatterns = [
    path(
        "translators/",
        burse.views.TranslatorsView.as_view(),
        name="translators",
    ),
]
