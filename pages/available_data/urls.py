"""URL configuration for the available_data app."""

from django.urls import path

from .views import AvailableDataView

app_name = "available_data"

urlpatterns = [
    path("", AvailableDataView.as_view(), name="index"),
]
