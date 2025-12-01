"""Views for the data management page."""

from utils.views import BaseTemplateView


class DataManagement(BaseTemplateView):
    """A template view class to render Data Management page."""

    template_name = "data_management/index.html"
    title = "Research Data Management"
