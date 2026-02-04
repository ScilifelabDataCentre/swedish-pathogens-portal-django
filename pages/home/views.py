"""Views for the home page."""

import structlog

from utils.views import BaseTemplateView

logger = structlog.get_logger(__name__)


class Home(BaseTemplateView):
    """A template view class to render Home page."""

    template_name = "home/index.html"
    title = "Swedish Pathogens Portal: supporting pandemic preparedness"

    logger.info("Home view initialized")
