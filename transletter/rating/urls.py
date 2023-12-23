from django.urls import path

from rating.views import RatingCreateView

app_name = "rating"

urlpatterns = [
    path("<int:pk>/create/", RatingCreateView.as_view(), name="create_rating"),
]
