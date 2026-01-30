"""URL configuration for the portal data page."""

from django.urls import path

from .views import (
    DataTypeListView,
    download_study_file,
    export_selected,
    study_files,
)

app_name = "portal_data"

DEFAULT = {"datatype": "metabolomics"}

urlpatterns = [
    path("export/", export_selected, DEFAULT, name="data_export"),
    # Per-study file browser (lists files under the study)
    path(
        "<slug:accession>/files/",
        study_files,
        DEFAULT,
        name="data_files",
    ),
    # Download an individual file from a study (relpath may contain slashes)
    path(
        "<slug:accession>/files/<path:relpath>/",
        download_study_file,
        DEFAULT,
        name="data_file",
    ),
    # Root listing page: /portal-data/
    path("", DataTypeListView.as_view(), DEFAULT, name="data_type_list"),
]
