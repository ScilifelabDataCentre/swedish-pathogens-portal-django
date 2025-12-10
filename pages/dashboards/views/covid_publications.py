"""View for historic publications dashboard."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class CovidPublications(View):
    """Historic COVID-19 publications dashboard.

    Displays the (historic) publications trend related to COVID-19.

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/covid_publications.html"
    title = "Swedish COVID-19 publications over 5 years"
    description = "A dashboard showcasing the trend of historic publications related to COVID-19."

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render the COVID-19 publications dashboard."""

        context = {"title": self.title, "description": self.description}

        blob_data = fetch_plot_json_blobserver("COVID_publication_count.json")
        context["publication_plot"] = plot_html_from_json(blob_data, height=600, skip_invalid=True)

        return render(request, self.template_name, context)
