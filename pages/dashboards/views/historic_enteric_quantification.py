"""Views for enteric virus in wastewater (GU) dashboard dashboard page."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class HistoricEntericQuantification(View):
    """Amount of enteric virus in wastewater (GU) dashboard page.

    This view class renders the template of (historic) dashboard of Amount of
    enteric virus in wastewater (GU).

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/historic_enteric_quantification.html"
    title = "Amount of enteric virus in wastewater (GU)"
    description = (
        "Enteric virus levels in Gothenburg’s wastewater, including "
        "norovirus and adenovirus. Data from the Norder group’s weekly "
        "analysis at Ryaverket WWTP helps predict outbreaks and includes "
        "samples from surrounding municipalities."
    )

    def get(self, request: HttpRequest) -> HttpResponse:
        """Fetch the compiled plot data (JSON) and generate plot html string."""

        context = {
            "title": self.title,
            "description": self.description,
        }

        vaccine_related_blobs = [
            "enteric_graph_gu",
        ]

        for blob in vaccine_related_blobs:
            # TODO: plot data to be fetch from DB
            blob_data = fetch_plot_json_blobserver(f"{blob}.json")
            if blob_data is not None:
                context[blob] = plot_html_from_json(
                    blob_data,
                    height="500px",
                    skip_invalid=True,
                )

        return render(request, self.template_name, context)
