from django.urls import path

from rating.views import RatingCreateView

app_name = "rating"

urlpatterns = [
    path("<int:pk>/new/", RatingCreateView.as_view(), name="create_rating"),
]
