from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class HistoricInfluenza(View):
    """Historic influenza data visualizations.

    In this view, we display various historic data visualizations related to influenza virus trends
    from SLU-SEEC. The data shown is not live and is intended for historical reference only.

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/historic_influenza.html"
    title = "Historic data of influenza virus in wastewater (SLU)"
    description = (
        "Historic data of Influenza A and B virus levels in wastewater across Sweden from SLU-SEEC"
    )

    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle GET requests to display the historic influenza dashboard."""

        context = dict(title=self.title, description=self.description)

        blobs = [
            "wastewater_sluINFsites",
            "historic_wastewater_slu_infA",
            "historic_wastewater_slu_infB",
        ]
        for blob in blobs:
            blob_data = fetch_plot_json_blobserver(f"{blob}.json")
            if blob.startswith("historic"):
                plot_height = "600px"
            else:
                plot_height = "750px"
            context[blob] = plot_html_from_json(blob_data, height=plot_height, skip_invalid=True)

        return render(request, self.template_name, context)
