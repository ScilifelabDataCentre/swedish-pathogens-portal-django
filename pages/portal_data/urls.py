"""URL configuration for the portal data page."""

from django.urls import path

from .views import (
    DataTypeListView,
    download_study,
    download_study_file,
    export_selected,
    homepage_jump,
    study_files,
)

app_name = "pages_portal_data"

urlpatterns = [
    path("", homepage_jump, name="index"),
    path("<slug:datatype>/export/", export_selected, name="data_export"),
    path(
        "<slug:datatype>/<slug:accession>/download/",
        download_study,
        name="data_download",
    ),
    # Per-study file browser (lists files under the study)
    path(
        "<slug:datatype>/<slug:accession>/files/",
        study_files,
        name="data_files",
    ),
    # Download an individual file from a study (relpath may contain slashes)
    path(
        "<slug:datatype>/<slug:accession>/files/<path:relpath>/",
        download_study_file,
        name="data_file",
    ),
    path("<slug:datatype>/", DataTypeListView.as_view(), name="data_type_list"),
]
