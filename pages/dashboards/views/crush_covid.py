"""Views for the CRUSH Covid dashboard page."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View


class CrushCovid(View):
    """CRUSH Covid dashboard page.

    Displays information about the CRUSH Covid research project in Uppsala County,
    including data visualizations, download links, and partner information.

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/crush_covid.html"
    title = "CRUSH Covid data and dashboard, Region Uppsala"
    description = (
        "CRUSH Covid maps outbreaks in Uppsala County by visualising the number "
        "of cases, test positivity, and geographic distribution, among other things. "
        "Data for each postal code is available for download and reuse."
    )

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render the CRUSH Covid dashboard page.

        Returns:
            Rendered template with context.

        """
        context = {"title": self.title, "description": self.description}

        return render(request, self.template_name, context)
