"""Views for the Citation page."""

from utils.views import BaseTemplateView


class Citation(BaseTemplateView):
    """A template view class to render Citation page."""

    template_name = "citation/index.html"
    title = "How to cite the Portal"
