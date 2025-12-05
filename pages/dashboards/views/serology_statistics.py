"""Views for serology statistics dashboard page."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class SerologyStatistics(View):
    """SARS-CoV-2 serology tests dashboard page.

    WIP: Currently pulling the plots from blobserver, this is temporary way
    for the MVP. In next set of update this view will change

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.

    """

    template_name = "dashboards/serology_statistics.html"
    title = "SARS-CoV-2 serology tests by the SciLifeLab Autoimmunity and Serology Profiling unit"
    description = (
        "A visualisation of the SARS-CoV-2 serology tests completed over "
        "time at the SciLifeLab Autoimmunology and Serology Profiling unit."
    )

    def get(self, request: HttpRequest) -> HttpResponse:
        """Fetch the compiled plot data (JSON) and generate plot html string."""
        context = {"title": self.title, "description": self.description}

        for blob in ["weekly_serology_tests", "cumulative_serology_tests"]:
            # TODO: plot data to be fetch from DB
            blob_data = fetch_plot_json_blobserver(f"{blob}.json")
            if blob_data is not None:
                context[blob] = plot_html_from_json(
                    blob_data,
                    height="550px",
                    skip_invalid=True,
                )

        return render(request, self.template_name, context)
