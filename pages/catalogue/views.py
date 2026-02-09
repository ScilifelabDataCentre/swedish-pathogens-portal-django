"""Views for catalogue pages."""

from utils.views import BaseListView

from .models import Catalogue


class ToolsCatalogueListView(BaseListView):
    """Display a list of tools catalogue resources."""

    model = Catalogue
    template_name = "catalogue/tools_catalogue.html"
    context_object_name = "resources"
    title = "Tools catalogue"
    ordering = "name"
    filter_category__contains = [Catalogue.CategoryChoices.TOOLS_CATALOGUE]


class DataRepositoriesListView(BaseListView):
    """Display a list of data repositories resources."""

    model = Catalogue
    template_name = "catalogue/data_repositories.html"
    context_object_name = "resources"
    title = "Data repositories"
    ordering = "name"
    filter_category__contains = [Catalogue.CategoryChoices.DATA_REPOSITORIES]


class DataSourcesListView(BaseListView):
    """Display a list of data sources resources."""

    model = Catalogue
    template_name = "catalogue/data_sources.html"
    context_object_name = "resources"
    title = "Data sources"
    ordering = "name"
    filter_category__contains = [Catalogue.CategoryChoices.DATA_SOURCES]
