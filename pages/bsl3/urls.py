"""URL configurations for BSL3 page."""

from django.urls import path

from .views import Bsl3Network

app_name = "bsl3"

urlpatterns = [
    path("", Bsl3Network.as_view(), name="index"),
]
