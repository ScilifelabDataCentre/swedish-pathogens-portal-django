"""Views for Register Based Research page."""

from utils.views import BaseTemplateView


class RegisterBasedResearch(BaseTemplateView):
    """A template view class to render Register Based Research page."""

    template_name = "register_based_research/index.html"
    title = "Register Based Research"
