"""Views for BSL3 page."""

from utils.views import BaseTemplateView


class Bsl3Network(BaseTemplateView):
    """A template view class to render BSL3 page."""

    template_name = "bsl3/index.html"
    title = "BSL3 Network"
