"""Views for the About app."""

from utils.views import BaseTemplateView


class About(BaseTemplateView):
    """A template view class to render About page."""

    template_name = "about/index.html"
    title = "About"


class Partners(BaseTemplateView):
    """A template view class to render Partners page."""

    template_name = "about/partners.html"
    title = "Partners"


class Funders(BaseTemplateView):
    """A template view class to render Funders page."""

    template_name = "about/funders.html"
    title = "Funders"


class NationalNodes(BaseTemplateView):
    """A template view class to render PPN page."""

    template_name = "about/nodes.html"
    title = "Pathogens Portal Nodes"
