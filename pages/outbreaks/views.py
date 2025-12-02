from utils.views import BaseListView, BaseDetailView
from .models import Outbreak


class OutbreakListView(BaseListView):
    """Display a list of all active outbreaks.

    Shows all active outbreaks organized by status (current vs historical)
    in a grid layout with thumbnails, names, descriptions, and status badges.
    Outbreaks are sorted by start date (newest first) and filtered to show
    only active content.

    Attributes:
        model: Outbreak model to display.
        template_name: Template for rendering the list.
        context_object_name: Name for outbreaks in template context.
        title: Page title displayed in template.
        ordering: Field to sort outbreaks by (newest first by start_date).
    """

    model = Outbreak
    template_name = "outbreaks/index.html"
    context_object_name = "outbreaks"
    title = "Outbreaks"
    ordering = "-start_date"

    def get_context_data(self, **kwargs):
        """Add current and historical outbreaks to context.

        Separates outbreaks into current and historical categories
        for display in different sections on the index page.

        Returns:
            dict: Context data with current_outbreaks and historical_outbreaks
        """
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        # Separate outbreaks by status
        context["current_outbreaks"] = queryset.filter(status="current")
        context["historical_outbreaks"] = queryset.filter(status="historical")

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
