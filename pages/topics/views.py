"""Views for topics page."""

from django.urls import reverse
from utils.views import BaseDetailView, BaseListView

from .models import Topic


class TopicListView(BaseListView):
    """Display a list of all active topics.

    Shows all active topics in a grid layout with thumbnails,
    names, and descriptions. Topics are sorted alphabetically.

    Attributes:
        model: Topic model to display.
        template_name: Template for rendering the list.
        context_object_name: Name for topics in template context.
        title: Page title displayed in template.
        ordering: Field to sort topics by (alphabetical by name).
    """

    model = Topic
    template_name = "topics/index.html"
    context_object_name = "topics"
    title = "Topics"
    ordering = "name"  # Topics are sorted alphabetically by name

    def get_context_data(self, **kwargs):
        """Add topic_cards for the content_card partial."""
        context = super().get_context_data(**kwargs)
        topics = context["topics"]
        context["topic_cards"] = [
            {
                "url": reverse("topics:topic_detail", kwargs={"slug": t.slug}),
                "image": t.thumbnail_image.url if t.thumbnail_image else "",
                "title": t.name,
                "description": t.description,
                "date": t.updated_at,
                "cta_text": "Read more \u2192",
            }
            for t in topics
        ]
        return context


class TopicDetailView(BaseDetailView):
    """Display detailed information about a specific topic.

    Shows the full topic content including description, markdown
    content, and optional alert messages. Uses slug-based URL lookup.

    Attributes:
        model: Topic model to display.
        template_name: Template for rendering the detail view.
        context_object_name: Name for topic in template context.
    """

    model = Topic
    template_name = "topics/topic_detail.html"
    context_object_name = "topic"
