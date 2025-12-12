"""View for COVID Quantification KTH dashboard page."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class CovidQuantificationKth(View):
    """COVID Quantification KTH dashboard page.

    Displays information about the SEEC-KTH wastewater monitoring project,
    including visualizations of SARS-CoV-2 levels in wastewater from Stockholm
    and Malmö. Combines both historic (April 2020 - August 2021) and recent
    (September 2021 - June 2023) data into a single dashboard.

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.

    """

    template_name = "dashboards/covid_quantification_kth.html"
    title = "Amount of SARS-CoV-2 in wastewater (SEEC-KTH)"
    description = (
        "SEEC-KTH wastewater monitoring project led by associate professor "
        "Zeynep Cetecioglu Gurol at KTH Royal Institute of Technology. "
        "Visualizations of SARS-CoV-2 levels in wastewater from Stockholm "
        "and Malmö, including both historic and recent data."
    )

    def get(self, request: HttpRequest) -> HttpResponse:
        """Fetch the compiled plot data (JSON) and generate plot HTML strings.

        Fetches Plotly JSON data from blobserver for each chart, converts it to HTML
        using plot_html_from_json, and adds it to the context for template rendering.

        Returns:
            Rendered template with plot HTML strings in context.

        """
        context = {"title": self.title, "description": self.description}

        # Map chart IDs to blobserver blob names
        plot_sources = {
            "historic_stockholm": "wastewater_data_stockholm.json",
            "stockholm_recent": "wastewater_combined_stockholm.json",
            "malmo": "wastewater_kthmalmo.json",
        }

        # Fetch and convert each plot
        for chart_id, blob_name in plot_sources.items():
            blob_data = fetch_plot_json_blobserver(blob_name)
            if blob_data is not None:
                height = "550px"  # Standard height for these plots
                context[chart_id] = plot_html_from_json(
                    blob_data,
                    height=height,
                    skip_invalid=True,
                )

        return render(request, self.template_name, context)
