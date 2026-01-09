from django.urls import path
from .views import DataTypeListView, export_selected, homepage_jump

app_name = "pages_portal_data"

urlpatterns = [
    path("", homepage_jump, name="index"),
    path("<slug:datatype>/", DataTypeListView.as_view(), name="data_type_list"),
    path("<slug:datatype>/export/", export_selected, name="data_export"),
]

