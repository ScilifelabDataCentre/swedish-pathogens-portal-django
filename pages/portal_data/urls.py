from django.urls import path
from .views import DataTypeListView, export_selected, homepage_jump, download_study

app_name = "pages_portal_data"

urlpatterns = [
    path("", homepage_jump, name="index"),
    path("<slug:datatype>/export/", export_selected, name="data_export"),
    path(
        "<slug:datatype>/<slug:accession>/download/",
        download_study,
        name="data_download",
    ),
    path("<slug:datatype>/", DataTypeListView.as_view(), name="data_type_list"),
]

