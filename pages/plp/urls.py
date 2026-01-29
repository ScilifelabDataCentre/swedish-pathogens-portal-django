"""URL routes for the PLP app."""

from django.urls import path

from .views import PlpListView, PlpProjectDetailView

app_name = "plp"

urlpatterns = [
    path("", PlpListView.as_view(), name="index"),
    path("<slug:slug>/", PlpProjectDetailView.as_view(), name="detail"),
]
