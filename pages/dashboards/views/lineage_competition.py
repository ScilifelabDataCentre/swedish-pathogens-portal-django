"""Views for the SARS-CoV-2 Variant Competition dashboard page."""

from utils.views import BaseTemplateView


class LineageCompetition(BaseTemplateView):
    """SARS-CoV-2 Variant Competition dashboard page.

    This dashboard view class renders the given template in which the plots are
    directly fetched from researchers Github repository.

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "dashboards/lineage_competition.html"
    title = "SARS-CoV-2 Variant Competition"
    page_heading = "Dashboards"
    description = (
        "Estimates of SARS-CoV-2 variant frequencies and growth rate advantages from "
        "global SARS-CoV-2 genotype sequencing data"
    )
