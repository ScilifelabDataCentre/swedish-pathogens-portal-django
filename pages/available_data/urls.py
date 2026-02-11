"""URL configuration for the Available Data page."""

from django.urls import path

from .views import AvailableDataView

app_name = "available_data"

urlpatterns = [
    path("", AvailableDataView.as_view(), name="index"),
]
