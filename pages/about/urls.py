"""URL configuration for the About section."""

from django.urls import path

from .views import About, Funders, NationalNodes, Partners

app_name = "about"

urlpatterns = [
    path("", About.as_view(), name="index"),
    path("partners/", Partners.as_view(), name="partners"),
    path("funders/", Funders.as_view(), name="funders"),
    path("pathogens-portal-nodes/", NationalNodes.as_view(), name="nodes"),
]
