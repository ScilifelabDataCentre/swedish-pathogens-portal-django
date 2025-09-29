from django.urls import path
from django.utils.text import slugify
from .views import DashboardsIndex, LineageCompetition, DashboardSLU, SLUsync

app_name = "dashboards"

urlpatterns = [
    path("", DashboardsIndex.as_view(), name="index"),
    path(
        "lineage-competition/", LineageCompetition.as_view(), name="lineage_competition"
    ),
]

# SLU wastewater URLs
for page in DashboardSLU.pages:
    urlpatterns.append(
        path(
            "wastewater-slu/" + ("" if page == "Overview" else f"{slugify(page)}/"),
            DashboardSLU.as_view(active_page=page),
            name=f"slu_{slugify(page)}",
        )
    )

# temp workaround, it should be removed when researcher data upload page is ready
urlpatterns.append(
    path("wastewater-slu/data-sync", SLUsync.as_view(), name="data_sync")
)
