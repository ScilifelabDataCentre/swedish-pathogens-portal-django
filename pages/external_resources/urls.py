"""URLs for external resources pages."""

from django.urls import path

from . import views

app_name = "external_resources"

urlpatterns = [
    path("tools-catalogue/", views.ToolsCatalogueListView.as_view(), name="tools_catalogue"),
    path("data-repositories/", views.DataRepositoriesListView.as_view(), name="data_repositories"),
    path("data-sources/", views.DataSourcesListView.as_view(), name="data_sources"),
]
