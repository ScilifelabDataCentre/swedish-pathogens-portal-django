from utils.views import BaseListView, BaseDetailView
from .models import DataHighlight


class HighlightListView(BaseListView):
    """Display a list of all active data highlights.

    Shows all active data highlights in a grid layout with featured images,
    titles, summaries, and publication information. Highlights are sorted
    by creation date (newest first) and filtered to show only active content.

    Attributes:
        model: DataHighlight model to display.
        template_name: Template for rendering the list.
        context_object_name: Name for highlights in template context.
        title: Page title displayed in template.
        ordering: Field to sort highlights by (newest first).
    """
    model = DataHighlight
    template_name = "highlights/index.html"
    context_object_name = "highlights"
    title = "Data Highlights"
    ordering = "-created_at"


class HighlightDetailView(BaseDetailView):
    """Display detailed information about a specific data highlight.

    Shows the full data highlight content including summary, markdown content,
    and publication details. Uses slug-based URL lookup and includes related
    highlights based on tag similarity.

    Attributes:
        model: DataHighlight model to display.
        template_name: Template for rendering the detail view.
        context_object_name: Name for highlight in template context.
    """
    model = DataHighlight
    template_name = "highlights/highlight_detail.html"
    context_object_name = "highlight"
    
    def get_context_data(self, **kwargs):
        """Add related highlights to the context.
        
        Retrieves highlights with similar tags using Jaccard similarity
        algorithm and adds them to the template context for display.
        
        Returns:
            dict: Context data with related_highlights added
        """
        context = super().get_context_data(**kwargs)
        highlight = self.get_object()
        
        # Get related highlights using Jaccard similarity algorithm
        related_highlights = highlight.get_related_highlights(limit=4, threshold=0.02)
        
        context['related_highlights'] = related_highlights
        return context
