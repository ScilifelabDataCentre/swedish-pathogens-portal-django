"""URLs for catalogue pages."""

from django.urls import path
from django.views.generic.base import RedirectView

from .views import DataRepositoriesListView, DataSourcesListView, ToolsCatalogueListView

app_name = "catalogue"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="home:index")),
    path("tools-catalogue/", ToolsCatalogueListView.as_view(), name="tools_catalogue"),
    path("data-repositories/", DataRepositoriesListView.as_view(), name="data_repositories"),
    path("data-sources/", DataSourcesListView.as_view(), name="data_sources"),
]
