from django.apps import AppConfig


class DashboardsConfig(AppConfig):
    """Configuration for the dashboards app.
    
    This app provides dashboards for visualizing and analyzing pathogen-related data.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.dashboards"
    verbose_name = "Dashboards"
