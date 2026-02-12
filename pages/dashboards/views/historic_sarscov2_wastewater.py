"""Views for the historic SARS-CoV-2 wastewater dashboard page."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class HistoricSarsCov2Wastewater(View):
    """Historic SEEC-SLU wastewater dashboard for SARS-CoV-2.

    Combines the legacy SLU national wastewater time series with the
    Örebro and Umeå historic visualisations.

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        page_heading: Heading for the page, used in the banner and as the main heading.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/historic_sarscov2_wastewater.html"
    title = "Historic SARS-CoV-2 wastewater data (SEEC-SLU)"
    page_heading = "Dashboards"
    description = (
        "Historic visualisations of SARS-CoV-2 levels in Swedish wastewater "
        "produced by SEEC-SLU, including combined national data and focused "
        "plots for Umeå and Örebro."
    )

    plot_blobs: dict[str, tuple[str, str]] = {
        "slu_sites_table": ("wastewater_sluCOVIDsites.json", "840px"),
        "slu_combined_timeseries": ("historic_wastewater_combined_slu_regular.json", "800px"),
        "umea_timeseries": ("wastewater_graph_Umea.json", "550px"),
        "orebro_timeseries": ("wastewater_graph_Orebro.json", "550px"),
    }

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render the combined historic wastewater dashboard."""

        context: dict[str, str] = {
            "title": self.title,
            "description": self.description,
            "page_heading": self.page_heading,
        }

        for context_key, (blob_name, height) in self.plot_blobs.items():
            blob_data = fetch_plot_json_blobserver(blob_name)
            if blob_data is not None:
                context[context_key] = plot_html_from_json(
                    blob_data,
                    height=height,
                    skip_invalid=True,
                )

        return render(request, self.template_name, context)
