"""Views for the Register Based Research page.

The registers table uses `DataTableMixin` so it is rendered with the reusable
data table component for consistent styling and pagination / search features.
"""

from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from core.mixins import DataTableMixin
from utils.html import safe_link
from utils.views import BaseTemplateView

REGISTERS_TABLE_ID = "useful-registers"
REGISTERS_TABLE_LABEL = "Subset of useful registers"
REGISTERS_HEADERS: list[str] = ["Register name", "Register holder"]

REGISTERS_ROWS: list[list[str]] = [
    [
        safe_link(
            (
                "https://www.socialstyrelsen.se/statistik-och-data/register/dodsorsaksregistret/",
                "The Swedish Cause of Death Register",
            )
        ),
        safe_link(("https://www.socialstyrelsen.se/en/", "National Board of Health and Welfare")),
    ],
    [
        safe_link(
            (
                "https://www.socialstyrelsen.se/en/statistics-and-data/registers/national-patient-register/",
                "The National Patient Register",
            )
        ),
        safe_link(("https://www.socialstyrelsen.se/en/", "National Board of Health and Welfare")),
    ],
    [
        safe_link(
            (
                "https://www.folkhalsomyndigheten.se/smittskydd-beredskap/vaccinationer/nationella-vaccinationsregistret/",
                "National vaccination register",
            )
        ),
        safe_link(
            (
                "https://www.folkhalsomyndigheten.se/the-public-health-agency-of-sweden/",
                "Public Health Agency of Sweden",
            )
        ),
    ],
    [
        safe_link(
            (
                "https://childreg.carmona.se/",
                "National Quality Registry for Paediatric Rheumatology",
            )
        ),
        safe_link(("https://www.regionostergotland.se/", "Region Östergötland")),
    ],
    [
        safe_link(
            ("https://palliativregistret.se/", "National Quality Registry for Palliative Care")
        ),
        safe_link(("https://www.rjl.se/", "Region Jönköping")),
    ],
    [
        safe_link(("https://covid19register.se/", "Quality Registry for SARS-CoV-2 (COVID-19)")),
        safe_link(
            (
                "https://www.karolinska.se/en/karolinska-university-hospital",
                "Karolinska University Hospital",
            )
        ),
    ],
    [
        safe_link(("https://www.medscinet.com/gr/", "National Quality Registry for Pregnancy")),
        safe_link(
            (
                "https://www.karolinska.se/en/karolinska-university-hospital",
                "Karolinska University Hospital",
            )
        ),
    ],
    [
        safe_link(
            ("https://www.ucr.uu.se/swedvasc/", "National Quality Registry for Vascular Surgery")
        ),
        safe_link(("https://regionuppsala.se/en/", "Region Uppsala")),
    ],
    [
        safe_link(
            (
                "https://www.socialstyrelsen.se/statistik-och-data/register/kommunal-halso-och-sjukvard/",
                "Registret över insatser inom kommunal hälso och sjukvård",
            )
        ),
        safe_link(("https://www.socialstyrelsen.se/en/", "National Board of Health and Welfare")),
    ],
    [
        safe_link(
            (
                "https://www.socialstyrelsen.se/statistik-och-data/register/cancerregistret/",
                "The Swedish Cancer Register",
            )
        ),
        safe_link(("https://www.socialstyrelsen.se/en/", "National Board of Health and Welfare")),
    ],
    [
        safe_link(("https://www.icuregswe.org/en/", "The Swedish Intensive Care Registry")),
        safe_link(
            (
                "https://www.regionvarmland.se/regionvarmland/om-regionen/om-webbplatsen/information-in-english-engelska",
                "Region Värmland",
            )
        ),
    ],
    [
        safe_link(
            (
                "https://www.socialstyrelsen.se/en/statistics-and-data/registers/national-medical-birth-register/",
                "The Swedish Medical Birth Register",
            )
        ),
        safe_link(("https://www.socialstyrelsen.se/en/", "National Board of Health and Welfare")),
    ],
    [
        safe_link(
            (
                "https://lvr.registercentrum.se/in-english/the-swedish-national-airway-register/p/HJAjrgGPD",
                "The Swedish National Airway Register",
            )
        ),
        safe_link(("https://www.vgregion.se/en/", "Region Västra Götaland")),
    ],
    [
        safe_link(("https://www.medscinet.com/pnq/", "Swedish Neonatal Quality Register")),
        safe_link(
            (
                "https://www.karolinska.se/en/karolinska-university-hospital",
                "Karolinska University Hospital",
            )
        ),
    ],
    [
        safe_link(
            (
                "https://www.socialstyrelsen.se/en/statistics-and-data/registers/national-prescribed-drug-register/",
                "The Swedish Prescribed Drug Register",
            )
        ),
        safe_link(("https://www.socialstyrelsen.se/en/", "National Board of Health and Welfare")),
    ],
    [
        safe_link(("https://srq.nu/en/welcome/", "Swedish Rheumatology Quality Register")),
        safe_link(
            (
                "https://www.karolinska.se/en/karolinska-university-hospital",
                "Karolinska University Hospital",
            )
        ),
    ],
]


class RegisterBasedResearch(DataTableMixin, BaseTemplateView):
    """Render the Register Based Research page with a registers table."""

    template_name = "register_based_research/index.html"
    title = "Register Based Research"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        """Handle full-page and HTMX partial requests.

        The HTMX branch is currently defensive: show_controls=False means no
        HTMX controls are rendered, so no partial requests will be triggered
        by the client today.  The branch is kept so that enabling controls in
        the future does not require a view change.
        """
        if request.htmx:
            ctx = self.get_table_context(
                request,
                REGISTERS_ROWS,
                REGISTERS_HEADERS,
                request.path,
                table_id=REGISTERS_TABLE_ID,
                table_label=REGISTERS_TABLE_LABEL,
            )
            return render(request, "components/data_table_content.html", {"t": ctx})

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add the registers table context."""
        context = super().get_context_data(**kwargs)
        context["registers_table"] = self.get_table_context(
            self.request,
            REGISTERS_ROWS,
            REGISTERS_HEADERS,
            self.request.path,
            table_id=REGISTERS_TABLE_ID,
            table_label=REGISTERS_TABLE_LABEL,
        )
        return context
