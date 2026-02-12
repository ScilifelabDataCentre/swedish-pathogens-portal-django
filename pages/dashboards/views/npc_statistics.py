"""Views for NPC Statistics dashboard page."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class NpcStatistics(View):
    """National Pandemic Centre SARS-CoV-2 test statistics dashboard page.

    Displays statistics and visualizations of SARS-CoV-2 (COVID-19) tests
    conducted at the National Pandemic Centre (NPC) at Karolinska Institute.
    This dashboard is historic and no longer updated.

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        page_heading: Heading for the page, shown in the banner.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/npc_statistics.html"
    title = "National Pandemic Centre SARS-CoV-2 (COVID-19) test statistics"
    page_heading = "Dashboards"
    description = (
        "The national Pandemic Centre (NPC) conducted testing related to "
        "SARS-CoV-2 from the start of the pandemic. They show positive, "
        "negative, and inconclusive tests. This dashboard is historic, so "
        "no longer updated."
    )

    def get(self, request: HttpRequest) -> HttpResponse:
        """Fetch the compiled plot data (JSON) and generate plot HTML strings.

        Fetches Plotly JSON data from blobserver for each chart, converts it to HTML
        using plot_html_from_json, and adds it to the context for template rendering.

        Returns:
            Rendered template with plot HTML strings in context.
        """
        context = {
            "title": self.title,
            "description": self.description,
            "page_heading": self.page_heading,
        }

        # Map chart IDs to blobserver blob names
        plot_sources = {
            "total_tests": "npc_total_tests.json",
            "tests_daily": "npc_tests_daily.json",
            "tests_weekly": "npc_tests_weekly.json",
            "positive_fraction_daily": "npc_positiveTests_fraction_daily.json",
            "positive_fraction_weekly": "npc_positiveTests_fraction_weekly.json",
            "cumulative_tests": "npc_cumulative_tests.json",
        }

        # Fetch and convert each plot
        for chart_id, blob_name in plot_sources.items():
            blob_data = fetch_plot_json_blobserver(blob_name)
            if blob_data is not None:
                # Set height based on chart type
                if chart_id == "total_tests":
                    height = "200px"
                elif chart_id == "cumulative_tests":
                    height = "550px"
                else:
                    height = "350px"
                context[chart_id] = plot_html_from_json(
                    blob_data,
                    height=height,
                    skip_invalid=True,
                )

        return render(request, self.template_name, context)
