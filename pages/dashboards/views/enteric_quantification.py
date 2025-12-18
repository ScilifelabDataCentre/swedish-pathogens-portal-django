from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class EntericQuantification(View):
    """Amount of enteric virus in wastewater (GU) dashboard page.

    This view class renders the template of (historic) dashboard of Amount of 
    enteric virus in wastewater (GU).

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/enteric_quantification.html"
    title = "Amount of enteric virus in wastewater (GU)"
    description = (
        "The Swedish Health Agency (Folkhälsomyndigheten) provide data and information "
        "related to COVID-19 in Sweden. Visualisations are shown on multiple aspects "
        "of vaccination coverage, like coverage in different counties."
    )

    def get(self, request: HttpRequest) -> HttpResponse:
        """Fetch the compiled plot data (JSON) and generate plot html string"""

        context = dict(title=self.title, description=self.description)

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
