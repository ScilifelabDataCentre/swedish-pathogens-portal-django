from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class Vaccines(View):
    """Covid-19 vaccine adminstration dashboard page.

    This view class renders the template of (historic) dashboard of Covid-19
    vaccine adminisatration in Sweden.

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/vaccines.html"
    title = "The Administration and Study of COVID-19 Vaccines in Sweden"
    description = (
        "The Swedish Health Agency (Folkhälsomyndigheten) provide data and information "
        "related to COVID-19 in Sweden. Visualisations are shown on multiple aspects "
        "of vaccination coverage, like coverage in different counties."
    )

    def get(self, request: HttpRequest) -> HttpResponse:
        """Fetch the compiled plot data (JSON) and generate plot html string"""

        context = dict(title=self.title, description=self.description)

        vaccine_related_blobs = [
            "Total_vaccinated_barchart",
            "vaccine_timeseries_pop_barchart",
            "onedose_pop_map",
            "twodoses_pop_map",
            "threedoses_pop_map",
            "fourdoses_pop_map",
            "fivedoses_pop_map",
            "fivedoses_elig_map",
            "vaccine_heatmap",
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
