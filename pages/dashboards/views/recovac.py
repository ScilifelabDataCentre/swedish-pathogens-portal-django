"""Views for RECOVAC dashboard page."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class Recovac(View):
    """Register-based COVID-19 vaccination study (RECOVAC) dashboard page.

    Renders the RECOVAC dashboard, which highlights data visualisations,
    publications, and contextual information coming from the RECOVAC and
    SCIFI-PEARL projects.
    """

    template_name = "dashboards/recovac.html"
    title = "Register-based COVID-19 vaccination study (RECOVAC)"
    description = (
        "Dedicated to the work of the register-based large-scale national "
        "population study to monitor COVID-19 vaccination effectiveness and "
        "safety (RECOVAC) project."
    )
    plot_sources = {
        "swedishpop_subplot_button": "swedishpop_subplot_button.json",
        "comorbs_subplot_button": "comorbs_subplot_button.json",
    }

    def get(self, request: HttpRequest) -> HttpResponse:
        """Fetch the compiled plot data (JSON) and generate plot HTML strings."""

        context = {
            "title": self.title,
            "description": self.description,
        }

        for chart_id, blob_name in self.plot_sources.items():
            blob_data = fetch_plot_json_blobserver(blob_name)
            if blob_data is not None:
                context[chart_id] = plot_html_from_json(
                    blob_data,
                    height="800px",
                    skip_invalid=True,
                )

        return render(request, self.template_name, context)
