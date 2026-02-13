"""URLs for the Share Data page."""

from django.urls import path

from .views import ShareData

app_name = "share_data"

urlpatterns = [
    path("", ShareData.as_view(), name="index"),
]
