"""Views for the Articles page."""

from typing import Any

from django.urls import reverse
from django.utils.html import strip_tags
from utils.views import BaseDetailView, BaseListView

from .models import Article


class ArticleListView(BaseListView):
    """Display a list of all active articles.

    Shows all active articles (data highlights and editorials) in a grid layout
    with featured images, titles, summaries, and publication information.
    Articles are sorted by creation date (newest first) and filtered to show
    only active content.

    Attributes:
        model: Article model to display.
        template_name: Template for rendering the list.
        context_object_name: Name for articles in template context.
        title: Page title displayed in template.
        ordering: Field to sort articles by (newest first).
    """

    model = Article
    template_name = "articles/index.html"
    context_object_name = "articles"
    title = "Articles"
    ordering = "-created_at"

    def get_queryset(self):
        """Prefetch topics for article cards."""
        return super().get_queryset().prefetch_related("topics")

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add article_cards for the content_card partial and search."""
        context = super().get_context_data(**kwargs)
        # Use full queryset so all articles are shown (no pagination)
        articles = self.get_queryset()

        cards = []
        for article in articles:
            search_parts = [article.title.lower(), strip_tags(article.summary).lower()]
            search_parts.extend(t.name.lower() for t in article.topics.all())
            cards.append({
                "url": reverse("articles:detail", kwargs={"slug": article.slug}),
                "image": article.featured_image.url if article.featured_image else "",
                "title": article.title,
                "description": strip_tags(article.summary),
                "date": article.created_at,
                "badge_text": article.get_type_display(),
                "badge_variant": article.type,
                "topics": [
                    {"name": t.name, "url": reverse("topics:topic_detail", kwargs={"slug": t.slug})}
                    for t in article.topics.all()
                ],
                "cta_text": "Read more",
                "search_text": " ".join(search_parts),
            })
        context["article_cards"] = cards
        return context


class ArticleDetailView(BaseDetailView):
    """Display detailed information about a specific article.

    Shows the full article content including summary, markdown content,
    and publication details. Uses slug-based URL lookup and includes related
    articles based on tag similarity.

    Attributes:
        model: Article model to display.
        template_name: Template for rendering the detail view.
        context_object_name: Name for article in template context.
    """

    model = Article
    template_name = "articles/article_detail.html"
    context_object_name = "article"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add related articles to the context.

        Retrieves articles with similar tags using Jaccard similarity
        algorithm and adds them to the template context for display.

        Returns:
            dict: Context data with related_articles added
        """
        context = super().get_context_data(**kwargs)
        article = self.get_object()

        # Get related articles using Jaccard similarity algorithm
        related_articles = article.get_related_articles(limit=4, threshold=0.02)

        context["related_articles"] = related_articles
        return context
