from utils.views import BaseTemplateView


class LineageCompetition(BaseTemplateView):
    """SARS-CoV-2 Variant Competition dashboard page."""

    template_name = "dashboards/lineage_competition.html"
    title = "SARS-CoV-2 Variant Competition"
    description = (
        "Estimates of SARS-CoV-2 variant frequencies and growth rate advantages from "
        "global SARS-CoV-2 genotype sequencing data"
    )
