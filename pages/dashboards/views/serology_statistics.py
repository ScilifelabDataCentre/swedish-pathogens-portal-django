from utils.views import BaseTemplateView

from ..visualisation.utils import fetch_plot_json_blobserver, plot_html_from_json


class SerologyStatistics(BaseTemplateView):
    """SARS-CoV-2 serology tests dashboard page.

    WIP: Currently pulling the plots from blobserver, this is temparory way
    for the MVP. In next set of update this view will change

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/serology_statistics.html"
    title = (
        "SARS-CoV-2 serology tests by the SciLifeLab Autoimmunity and "
        "Serology Profiling unit"
    )
    description = (
        "A visualisation of the SARS-CoV-2 serology tests completed over "
        "time at the at SciLifeLab Autoimmunology and Serology Profiling unit."
    )
    plot_height = "550px"

    def get_context_data(self, **kwargs):
        """Add plot HTML string to the context"""

        context = super().get_context_data(**kwargs)
        context["plot_height"] = self.plot_height

        # TODO: plot data to be fetch from DB
        weekly_data = fetch_plot_json_blobserver("weekly_serology_tests.json")
        context["weekly_plot"] = plot_html_from_json(
            weekly_data,
            height=self.plot_height,
            skip_invalid=True,
        )
        # TODO: plot data to be fetch from DB
        cumulative_data = fetch_plot_json_blobserver("cumulative_serology_tests.json")
        context["cumulative_data"] = plot_html_from_json(
            cumulative_data,
            height=self.plot_height,
            include_plotlyjs=False,
            skip_invalid=True,
        )

        return context
