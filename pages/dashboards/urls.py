from django.urls import path
from .views import DashboardsIndex, LineageCompetition, VariantsRegionUppsala

app_name = "dashboards"

urlpatterns = [
    path("", DashboardsIndex.as_view(), name="index"),
    path("lineage-competition/", LineageCompetition.as_view(), name="lineage_competition"),
    path("variants-region-uppsala/", VariantsRegionUppsala.as_view(), name="variants_region_uppsala"),
]
