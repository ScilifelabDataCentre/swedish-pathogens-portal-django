from django.urls import path

from .views import PlpProgram, PlpProjectDetail

app_name = "plp"

urlpatterns = [
    path("", PlpProgram.as_view(), name="index"),
    path("projects/<slug:slug>/", PlpProjectDetail.as_view(), name="project-detail"),
]
