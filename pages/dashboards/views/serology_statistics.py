from utils.views import BaseTemplateView


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
