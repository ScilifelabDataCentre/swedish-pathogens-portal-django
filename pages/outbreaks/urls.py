"""URL configuration for the outbreaks app."""

from django.urls import path

from .views import OutbreakDetailView, OutbreakListView

app_name = "outbreaks"

urlpatterns = [
    path("", OutbreakListView.as_view(), name="index"),
    path("<slug:slug>/", OutbreakDetailView.as_view(), name="detail"),
]
