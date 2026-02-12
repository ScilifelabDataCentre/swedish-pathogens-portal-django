"""Views for News page."""

from utils.views import BaseDetailView, BaseListView

from .models import News


class NewsIndex(BaseListView):
    """Display a list of all active news.

    List all active news, sorted by creation date.

    Attributes:
        model: News model to display.
        template_name: Template for rendering the list.
        context_object_name: Name for news in template context.
        title: Page title displayed in template.
    """

    model = News
    template_name = "news/index.html"
    context_object_name = "news_list"
    title = "News and Updates"


class NewsDetail(BaseDetailView):
    """Display detailed information about a specific news.

    Shows the full news content, uses slug-based URL lookup.

    Attributes:
        model: News model to display.
        template_name: Template for rendering the detail view.
        context_object_name: Name for news in template context.
    """

    model = News
    template_name = "news/detail.html"
    context_object_name = "news"
    page_heading = "News and Updates"
