from django.urls import path

from .views import PlpProgram

app_name = "plp"

urlpatterns = [
    path("", PlpProgram.as_view(), name="index"),
]
