from django.urls import path
<<<<<<< HEAD
from .views import DashboardsIndex, LineageCompetition, VariantsRegionUppsala
=======
from .views import DashboardsIndex, LineageCompetition, SerologyStatistics
>>>>>>> origin/main

app_name = "dashboards"

urlpatterns = [
    path("", DashboardsIndex.as_view(), name="index"),
<<<<<<< HEAD
    path("lineage-competition/", LineageCompetition.as_view(), name="lineage_competition"),
    path("variants-region-uppsala/", VariantsRegionUppsala.as_view(), name="variants_region_uppsala"),
=======
    path(
        "lineage-competition/", LineageCompetition.as_view(), name="lineage_competition"
    ),
    path(
        "serology-statistics/", SerologyStatistics.as_view(), name="serology_statistics"
    ),
>>>>>>> origin/main
]
