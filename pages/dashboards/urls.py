"""URL configurations for dashboards page."""

from django.urls import path

from .views import (
    HistoricCovidQuantificationGu,
    CovidQuantificationKth,
    CrushCovid,
    DashboardsIndex,
    HistoricCovidPublications,
    HistoricInfluenza,
    HistoricSarsCov2Wastewater,
    LineageCompetition,
    MultiDiseaseSerology,
    NpcStatistics,
    PostCovid,
    Recovac,
    SerologyStatistics,
    SymptomStudySweden,
    Vaccines,
    VariantsRegionUppsala,
)

app_name = "dashboards"

urlpatterns = [
    path("", DashboardsIndex.as_view(), name="index"),
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
