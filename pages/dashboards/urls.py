from django.urls import path
from .views import (
    DashboardsIndex,
    LineageCompetition,
    SerologyStatistics,
    PostCovid,
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
]
