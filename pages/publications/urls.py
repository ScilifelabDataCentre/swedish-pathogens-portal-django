"""URLs for the Publications page."""

from django.urls import path

from .views import Publications

app_name = "publications"

urlpatterns = [
    path("", Publications.as_view(), name="index"),
]
