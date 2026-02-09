"""Views for the Available Data (query links) page."""

from utils.views import BaseTemplateView


class AvailableDataView(BaseTemplateView):
    """A template view that renders the Available Data (query links) page."""

    template_name = "available_data/index.html"
    title = "Data query links"
