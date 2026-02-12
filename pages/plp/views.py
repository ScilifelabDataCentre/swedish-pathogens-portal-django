"""Views for listing and viewing PLP projects."""

from typing import Any

from utils.views import BaseDetailView, BaseListView

from .models import PlpProject


class PlpListView(BaseListView):
    """Display a list of all active PLP projects.

    Shows all active pandemic preparedness capability projects in a grid layout
    with featured images, titles, summaries, and categories. Projects are
    sorted by creation date (newest first) by default.

    Attributes:
        model: PlpProject model to display.
        template_name: Template for rendering the list.
        context_object_name: Name for projects in template context.
        title: Page title displayed in template.
        ordering: Field to sort projects by (newest first).
    """

    model = PlpProject
    template_name = "plp/index.html"
    context_object_name = "projects"
    title = "Pandemic Laboratory Preparedness Program"
    ordering = "-created_at"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add grouped projects by category to context."""
        context = super().get_context_data(**kwargs)
        projects = context.get("projects", PlpProject.objects.none())

        # Group projects by category
        category_map = {}
        for project in projects:
            if project.category not in category_map:
                category_map[project.category] = []
            category_map[project.category].append(project)

        # Convert category map to category groups in CATEGORY_CHOICES order
        category_groups = []
        for value, _label in PlpProject.CATEGORY_CHOICES:
            if value in category_map:
                category_groups.append(
                    {
                        "value": value,
                        "label": category_map[value][0].get_category_group_label(),
                        "projects": category_map[value],
                    }
                )

        context["category_groups"] = category_groups
        return context


class PlpProjectDetailView(BaseDetailView):
    """Display detailed information about a specific PLP project.

    Shows the full project content rendered from markdown, including
    featured image and category information. Uses slug-based URL lookup.

    Attributes:
        model: PlpProject model to display.
        template_name: Template for rendering the detail view.
        context_object_name: Name for project in template context.
    """

    model = PlpProject
    template_name = "plp/project_detail.html"
    context_object_name = "project"
    page_heading = "Pandemic Laboratory Preparedness Program"
