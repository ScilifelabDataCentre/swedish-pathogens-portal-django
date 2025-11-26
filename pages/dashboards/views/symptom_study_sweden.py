from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class SymptomStudySweden(View):
    """COVID Symptom Study Sweden dashboard page.

    Displays information about the COVID Symptom Study Sweden (CSSS), including
    prevalence estimates, data access information, and publications. The project
    collects data on COVID-19 prevalence, symptoms, and vaccinations through a
    smartphone app with over 200,000 users in Sweden.

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/symptom_study_sweden.html"
    title = "COVID Symptom Study Sweden"
    description = (
        "The COVID Symptom Study Sweden (CSSS) collects data on COVID-19 "
        "prevalence, symptoms, and vaccinations through a smart phone app with "
        "over 200.000 users in Sweden. Raw data can be requested for use in "
        "research projects."
    )

    def get(self, request):
        """Fetch the compiled plot data (JSON) and generate plot HTML strings.

        Fetches Plotly JSON data from blobserver for the prevalence map,
        converts it to HTML using plot_html_from_json, and adds it to the
        context for template rendering.

        Returns:
            Rendered template with plot HTML strings in context.
        """

        context = dict(title=self.title, description=self.description)

        # Fetch prevalence map visualization
        blob_data = fetch_plot_json_blobserver("symptoms_map_english.json")
        if blob_data is not None:
            context["prevalence_map"] = plot_html_from_json(
                blob_data,
                height="500px",
                skip_invalid=True,
            )

        return render(request, self.template_name, context)
