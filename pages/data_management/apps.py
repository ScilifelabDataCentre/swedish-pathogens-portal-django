from django.apps import AppConfig


class DataManagementConfig(AppConfig):
    """Configuration for the data management app.

    This app handles the research data management (RDM) page,
    which provides advice and links to RDM-relevant resources.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.data_management"
    verbose_name = "Data Management"
