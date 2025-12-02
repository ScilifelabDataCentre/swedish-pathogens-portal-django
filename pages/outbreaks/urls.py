from django.urls import path
from .views import OutbreakListView, OutbreakDetailView

app_name = "outbreaks"

urlpatterns = [
    path("", OutbreakListView.as_view(), name="index"),
    path("<slug:slug>/", OutbreakDetailView.as_view(), name="detail"),
]
