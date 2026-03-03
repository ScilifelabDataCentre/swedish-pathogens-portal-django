"""Views for listing and viewing PLP projects.

The PLP timeline table uses `DataTableMixin` to provide search, pagination,
and configurable entries per page via the reusable data table component.
"""

from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from core.mixins import DataTableMixin
from utils.html import safe_link
from utils.views import BaseDetailView, BaseListView

from .models import PlpProject

TIMELINE_TABLE_ID = "plp-timeline"
TIMELINE_HEADERS: list[str] = ["Date", "Milestone", "Description", "Status"]

# Each row is [Date, Milestone, Description, Status].
# safe_link() builds the HTML links for the template.
TIMELINE_ROWS: list[list[str]] = [
    [
        "2025-06-01",
        safe_link(
            (
                "https://www.scilifelab.se/news/call-for-grants-for-technology"
                "-development-projects-within-pandemic-laboratory-preparedness-plp-tdp/",
                "PLPTDP25 Call",
            )
        ),
        "Launch of new TDP funding to drive diagnostics and host response"
        " innovation that will support during outbreaks.",
        "Call open (as of Jun 2025)",
    ],
    [
        "2024-02-01",
        "PM TDP Call",
        "Call for clinical tech development in collaboration with Precision"
        " Medicine to address healthcare needs.",
        "Call closed (Apr 2024)",
    ],
    [
        "2023-09-01",
        safe_link(
            (
                "https://www.scilifelab.se/news/grants-for-testing-of-plp-capabilities-plp-test/",
                "PLP-Test Call",
            )
        ),
        "Support up to 9 projects to test and improve PLP capabilities.",
        "Ongoing",
    ],
    [
        "2023-02-01",
        safe_link(("https://anubis.scilifelab.se/call/REPLPCM", "REPLPCM Call")),
        "Extend funding for TDP projects until 2025.",
        "Ongoing (until 2025)",
    ],
    [
        "2022-09-01",
        safe_link(("https://anubis.scilifelab.se/call/REPLP1", "REPLP-1 Call")),
        "Extend funding for PLP1 projects until 2025.",
        "Ongoing (until 2025)",
    ],
    [
        "2022-04-01",
        "PLP2 Call",
        "To create nationally significant infrastructure capabilities with a"
        " functional expectation within a year.",
        "Completed",
    ],
    [
        "2021-12-01",
        "TDP Funding Call",
        "The intention with this call was to build closer connections between"
        " clinical microbiology laboratories in Sweden and to develop"
        " capabilities in major clinical microbiology labs in Sweden.",
        "Completed",
    ],
    [
        "2021-07-01",
        "PLP1: First 8 Capabilities Selected",
        "Focused on BSL3, biobanking, environmental detection,"
        " immunomonitoring, serology, sequencing.",
        "Completed",
    ],
    [
        "2021-02-01",
        "PLP National Open Call",
        "Call for letters of intent to detect/monitor COVID-19 and future pandemics.",
        "Completed",
    ],
    [
        "2020-12-01",
        safe_link(
            (
                "https://www.regeringen.se/rattsliga-dokument/proposition"
                "/2020/12/forskning-frihet-framtid--kunskap-och-innovation-for-sverige/",
                "Swedish government commissioned SciLifeLab",
            )
        ),
        "The assignment broadly involved supporting research related to"
        " infectious diseases (e.g. in diagnostics, analysis of infection,"
        " immunity, and the development of resistance to therapies in"
        " pathogens), and developing competence and technologies related to"
        " pandemic research (e.g. in sequencing, genetic analysis,"
        " immunology, and big data).",
        "Completed",
    ],
]


class PlpListView(DataTableMixin, BaseListView):
    """Display active PLP projects and an interactive timeline table.

    Shows all active pandemic preparedness capability projects in a grid layout
    with featured images, titles, summaries, and categories. Projects are
    sorted by creation date (newest first) by default.
    The programme timeline is rendered with the data table component with the
    pagination and search features hidden.

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

    # Show 20 timeline rows on one page by default
    per_page_default = 20

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        """Handle full-page and HTMX partial requests."""
        # HTMX request from the timeline table returns only the content partial
        if request.htmx:
            ctx = self.get_table_context(
                request,
                TIMELINE_ROWS,
                TIMELINE_HEADERS,
                request.path,
                table_id=TIMELINE_TABLE_ID,
                show_controls=False,
            )
            return render(request, "components/data_table_content.html", {"t": ctx})

        # Full-page render delegates to ListView.get
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add grouped projects by category and timeline table to context."""
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

        # Build the timeline table context
        context["timeline_table"] = self.get_table_context(
            self.request,
            TIMELINE_ROWS,
            TIMELINE_HEADERS,
            self.request.path,
            table_id=TIMELINE_TABLE_ID,
            show_controls=False,
        )
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
