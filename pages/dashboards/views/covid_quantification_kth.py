from django.shortcuts import render
from django.views import View


class CovidQuantificationKth(View):
    """COVID Quantification KTH dashboard page.

    Displays information about the SEEC-KTH wastewater monitoring project,
    including visualizations of SARS-CoV-2 levels in wastewater from Stockholm
    and Malmö. Combines both historic (April 2020 - August 2021) and recent
    (September 2021 - June 2023) data into a single dashboard.

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/covid_quantification_kth.html"
    title = "Amount of SARS-CoV-2 in wastewater (SEEC-KTH)"
    description = (
        "SEEC-KTH wastewater monitoring project led by associate professor "
        "Zeynep Cetecioglu Gurol at KTH Royal Institute of Technology. "
        "Visualizations of SARS-CoV-2 levels in wastewater from Stockholm "
        "and Malmö, including both historic and recent data."
    )

    def get(self, request):
        """Render the COVID Quantification KTH dashboard page.

        Returns:
            Rendered template with context.
        """
        context = dict(title=self.title, description=self.description)

        return render(request, self.template_name, context)
