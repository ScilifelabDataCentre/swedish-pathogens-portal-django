"""Views for the home page."""

from utils.views import BaseTemplateView


class Home(BaseTemplateView):
    """A template view class to render Home page."""

    template_name = "home/index.html"
    title = "Swedish Pathogens Portal: supporting pandemic preparedness"
