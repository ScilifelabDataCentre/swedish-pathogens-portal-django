"""URL configurations for Register Based Research page."""

from django.urls import path

from .views import RegisterBasedResearch

app_name = "register_based_research"

urlpatterns = [
    path("", RegisterBasedResearch.as_view(), name="index"),
]
