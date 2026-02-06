"""URL configurations for dashboards page."""

from django.urls import path
from django.utils.text import slugify

from .views import (
    CovidQuantificationKth,
    CrushCovid,
    DashboardsIndex,
    ExternalDashboards,
    HistoricCovidPublications,
    HistoricCovidQuantificationGu,
    HistoricEntericQuantificationGu,
    HistoricInfluenza,
    HistoricSarsCov2Wastewater,
    LineageCompetition,
    MultiDiseaseSerology,
    NpcStatistics,
    PostCovid,
    Recovac,
    SerologyStatistics,
    SLUsync,
    SluWasteWater,
    SymptomStudySweden,
    Vaccines,
    VariantsRegionUppsala,
)

app_name = "dashboards"

urlpatterns = [
    path("", DashboardsIndex.as_view(), name="index"),
    path("external-dashboards", ExternalDashboards.as_view(), name="external_dashboards"),
    path(
        "lineage-competition/",
        LineageCompetition.as_view(),
        name="lineage_competition",
    ),
    path(
        "multidisease-serology/",
        MultiDiseaseSerology.as_view(),
        name="multidisease_serology",
    ),
    path(
        "serology-statistics/",
        SerologyStatistics.as_view(),
        name="serology_statistics",
    ),
    path(
        "variants-region-uppsala/",
        VariantsRegionUppsala.as_view(),
        name="variants_region_uppsala",
    ),
    path(
        "historic-covid-publications/",
        HistoricCovidPublications.as_view(),
        name="historic_covid_publications",
    ),
    path(
        "historic-covid-quantification-gu/",
        HistoricCovidQuantificationGu.as_view(),
        name="historic_covid_quantification_gu",
    ),
    path(
        "covid-quantification-kth/",
        CovidQuantificationKth.as_view(),
        name="covid_quantification_kth",
    ),
    path(
        "crush-covid/",
        CrushCovid.as_view(),
        name="crush_covid",
    ),
    path(
        "historic-enteric-quantification-gu/",
        HistoricEntericQuantificationGu.as_view(),
        name="historic_enteric_quantification_gu",
    ),
    path(
        "historic-sarscov2-wastewater/",
        HistoricSarsCov2Wastewater.as_view(),
        name="historic_sarscov2_wastewater",
    ),
    path(
        "historic-influenza/",
        HistoricInfluenza.as_view(),
        name="historic_influenza",
    ),
    path(
        "npc-statistics/",
        NpcStatistics.as_view(),
        name="npc_statistics",
    ),
    path(
        "post-covid/",
        PostCovid.as_view(),
        name="post_covid",
    ),
    path(
        "recovac/",
        Recovac.as_view(),
        name="recovac",
    ),
    path(
        "symptom-study-sweden/",
        SymptomStudySweden.as_view(),
        name="symptom_study_sweden",
    ),
    path(
        "vaccines/",
        Vaccines.as_view(),
        name="vaccines",
    ),
]

# SLU wastewater URLs
for page in SluWasteWater.pages:
    urlpatterns.append(
        path(
            "slu-wastewater/" + ("" if page == "Overview" else f"{slugify(page)}/"),
            SluWasteWater.as_view(active_page=page),
            name=f"slu_{slugify(page)}",
        )
    )

# temp workaround, it should be removed when researcher data upload page is ready
urlpatterns.append(
    path(
        "slu-wastewater/data-sync",
        SLUsync.as_view(),
        name="slu_data_sync",
    )
)
