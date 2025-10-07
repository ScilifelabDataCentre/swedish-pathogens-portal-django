from django.urls import path
from .views import HighlightListView, HighlightDetailView

app_name = "highlights"

urlpatterns = [
    path("", HighlightListView.as_view(), name="index"),
    path("<slug:slug>/", HighlightDetailView.as_view(), name="detail"),
]
