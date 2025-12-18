"""Views for Privacy page."""

from utils.views import BaseTemplateView


class Privacy(BaseTemplateView):
    """A template view class to render Privacy page."""

    template_name = "privacy/index.html"
    title = "Privacy Policy"
