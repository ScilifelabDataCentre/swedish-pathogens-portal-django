from django.urls import path
from .views import DashboardsIndex, LineageCompetition, SerologyStatistics

app_name = "dashboards"

urlpatterns = [
    path("", DashboardsIndex.as_view(), name="index"),
    path(
        "lineage-competition/", LineageCompetition.as_view(), name="lineage_competition"
    ),
    path(
        "serology-statistics/", SerologyStatistics.as_view(), name="serology_statistics"
    ),
]
