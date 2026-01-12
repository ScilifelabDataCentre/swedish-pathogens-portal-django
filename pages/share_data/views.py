"""Views for the Share Data page."""

from utils.views import BaseTemplateView


class ShareData(BaseTemplateView):
    """A template view class to render Share Data page."""

    template_name = "share_data/index.html"
    title = "Share Data"
