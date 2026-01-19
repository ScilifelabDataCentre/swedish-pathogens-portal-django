"""Views for COVID Quantification GU dashboard dashboard page."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class CovidQuantificationGu(View):
    """Amount of enteric virus in wastewater (GU) dashboard page.

    This view class renders the template of (historic) dashboard of COVID Quantification 
    GU in wastewater (GU).

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/covid_quantification_gu.html"
    title = "Amount of SARS-CoV-2 in wastewater (GU)"
    description = (
        "This project is led by Professor Helene Norder (University of Gothenburg, "
        "GU), and supported by co-workers from the University of Gothenburg and "
        "Sahlgrenska University Hospital (Hao Wang, Marianela Patzi Churqui, Timur "
        "Tunovic, Fredy Saguti, and Kristina Nyström). The wastewater sample collections "
        "were performed by Lucica Enache at Ryaverket, Gryaab AB, Gothenburg."
    )

    def get(self, request: HttpRequest) -> HttpResponse:
        """Fetch the compiled plot data (JSON) and generate plot html string."""

        context = {
            "title": self.title,
            "description": self.description,
        }

        vaccine_related_blobs = [
            "wastewater_gothenburg",
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