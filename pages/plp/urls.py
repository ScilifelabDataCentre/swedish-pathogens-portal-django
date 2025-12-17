from django.urls import path

from .views import PlpListView, PlpProjectDetail

app_name = "plp"

urlpatterns = [
    path("", PlpListView.as_view(), name="index"),
    path("<slug:slug>/", PlpProjectDetail.as_view(), name="detail"),
]
