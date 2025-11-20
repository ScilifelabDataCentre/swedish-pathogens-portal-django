from django.urls import path
from .views import (
    DashboardsIndex,
    LineageCompetition,
    NpcStatistics,
    PostCovid,
    SerologyStatistics,
    SymptomStudySweden,
    Vaccines,
    VariantsRegionUppsala,
)

app_name = "dashboards"

urlpatterns = [
    # Dashboard index URL
    path("", DashboardsIndex.as_view(), name="index"),
    # Individual dashboards URLs
    path(
        "lineage-competition/",
        LineageCompetition.as_view(),
        name="lineage_competition",
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
        "serology-statistics/",
        SerologyStatistics.as_view(),
        name="serology_statistics",
    ),
    path(
        "vaccines/",
        Vaccines.as_view(),
        name="vaccines",
    ),
    path(
        "variants-region-uppsala/",
        VariantsRegionUppsala.as_view(),
        name="variants_region_uppsala",
    ),
    path(
        "symptom-study-sweden/",
        SymptomStudySweden.as_view(),
        name="symptom_study_sweden",
    ),
]
