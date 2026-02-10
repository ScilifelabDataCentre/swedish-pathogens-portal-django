"""URL configuration for the highlights and editorials page."""

from django.urls import path

from .views import HighlightsAndEditorialsDetailView, HighlightsAndEditorialsListView

app_name = "highlights_and_editorials"

urlpatterns = [
    path("", HighlightsAndEditorialsListView.as_view(), name="index"),
    path("<slug:slug>/", HighlightsAndEditorialsDetailView.as_view(), name="detail"),
]
