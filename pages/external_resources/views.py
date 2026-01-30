"""Views for external resources pages."""

from utils.views import BaseListView

from .models import ExternalResource


class ToolsCatalogueListView(BaseListView):
    """Display a list of tools catalogue resources."""

    model = ExternalResource
    template_name = "external_resources/tools_catalogue.html"
    context_object_name = "resources"
    title = "Tools catalogue"
    ordering = "name"
    filter_category = ExternalResource.CategoryChoices.TOOLS_CATALOGUE


class DataRepositoriesListView(BaseListView):
    """Display a list of data repositories resources."""

    model = ExternalResource
    template_name = "external_resources/data_repositories.html"
    context_object_name = "resources"
    title = "Data repositories"
    ordering = "name"
    filter_category = ExternalResource.CategoryChoices.DATA_REPOSITORIES


class DataSourcesListView(BaseListView):
    """Display a list of data sources resources."""

    model = ExternalResource
    template_name = "external_resources/data_sources.html"
    context_object_name = "resources"
    title = "Data sources"
    ordering = "name"
    filter_category = ExternalResource.CategoryChoices.DATA_SOURCES
