from django.shortcuts import render
from django.views import View

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class PostCovid(View):
    """Post COVID-19 condition dashboard page.

    Displays statistics, visualizations, and information about Post COVID-19
    condition in Sweden, including data from The Swedish Board of Health and
    Welfare (Socialstyrelsen).

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/post_covid.html"
    title = "Post COVID-19 condition in Sweden: statistics and available data"
    description = (
        "The Swedish Board of Health and Welfare (Socialstyrelsen) shares data "
        "on Post COVID-19 condition. Here, we show visualisations of data on "
        "symptoms, healthcare contacts, and geographic distribution, among other things."
    )

    def get(self, request):
        """Fetch the compiled plot data (JSON) and generate plot HTML strings.

        Fetches Plotly JSON data from blobserver for each chart, converts it to HTML
        using plot_html_from_json, and adds it to the context for template rendering.

        Returns:
            Rendered template with plot HTML strings in context.
        """
        context = dict(title=self.title, description=self.description)

        # Map chart IDs to blobserver blob names
        plot_sources = {
            "age_sex_u099": "U099_agesex_casedist.json",
            "age_sex_u089": "U089_agesex_casedist.json",
            "geographic_u099": "map_postcovid_percent_of_population_U099.json",
            "geographic_u089": "map_postcovid_percent_of_population_U089.json",
            "accomp_diag_table": "accompdiag_table.json",
            "healthcare_contacts": "weeklycontacts_healthcare.json",
            "healthcare_divsex_u099": "U099_healthcare_divsex.json",
            "healthcare_divsex_u089": "U089_healthcare_divsex.json",
        }

        # Fetch and convert each plot
        for chart_id, blob_name in plot_sources.items():
            blob_data = fetch_plot_json_blobserver(blob_name)
            if blob_data is not None:
                # Set height based on chart type
                if chart_id == "accomp_diag_table":
                    height = "527px"
                else:
                    height = "500px"
                context[chart_id] = plot_html_from_json(
                    blob_data,
                    height=height,
                    skip_invalid=True,
                )

        return render(request, self.template_name, context)
