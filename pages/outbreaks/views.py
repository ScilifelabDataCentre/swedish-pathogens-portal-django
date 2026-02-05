"""Views for the outbreaks app."""

from typing import Any

from django.urls import reverse
from utils.views import BaseDetailView, BaseListView

from .models import Outbreak


class OutbreakListView(BaseListView):
    """Display a list of all active outbreaks.

    Shows all active outbreaks organized by status (current vs historical)
    in a grid layout with thumbnails, names, descriptions, and status badges.
    Outbreaks are sorted by creation date (newest first) and filtered to show
    only active content.

    Attributes:
        model: Outbreak model to display.
        template_name: Template for rendering the list.
        context_object_name: Name for outbreaks in template context.
        title: Page title displayed in template.
        ordering: Field to sort outbreaks by (newest first by created_at).

    """

    model = Outbreak
    template_name = "outbreaks/index.html"
    context_object_name = "outbreaks"
    title = "Outbreaks"
    ordering = "-created_at"

    def get_context_data(self, **kwargs) -> dict[str, Any]:  # noqa: ANN003
        """Add current and historical outbreaks to context.

        Separates outbreaks into current and historical categories
        for display in different sections on the index page.

        Returns:
            dict: Context data with current_outbreaks and historical_outbreaks

        """
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        current = queryset.filter(status="current")
        historical = queryset.filter(status="historical")
        context["current_outbreaks"] = current
        context["historical_outbreaks"] = historical

        def make_cards(outbreaks):
            return [
                {
                    "url": reverse("outbreaks:detail", kwargs={"slug": o.slug}),
                    "image": o.thumbnail_image.url if o.thumbnail_image else "",
                    "title": o.name,
                    "description": f"{o.description} Location: {o.location}." if o.location and o.location.strip() else o.description,
                    "date": o.updated_at,
                    "cta_text": "Read more \u2192",
                }
                for o in outbreaks
            ]

        context["current_outbreak_cards"] = make_cards(current)
        context["historical_outbreak_cards"] = make_cards(historical)

        return context


class OutbreakDetailView(BaseDetailView):
    """Display detailed information about a specific outbreak.

    Shows the full outbreak content including background information,
    brief history, timeline, and data visualization links. Uses slug-based
    URL lookup.

    Attributes:
        model: Outbreak model to display.
        template_name: Template for rendering the detail view.
        context_object_name: Name for outbreak in template context.

    """

    model = Outbreak
    template_name = "outbreaks/outbreak_detail.html"
    context_object_name = "outbreak"
