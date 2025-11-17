from django.apps import AppConfig


class DashboardsConfig(AppConfig):
    """Configuration for the dashboards app.
    
    This app provides interactive dashboards for visualizing and exploring
    pathogen-related data on the Swedish Pathogens Portal. It enables users to
    gain insights through dynamic charts, graphs, and maps.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.dashboards"
    verbose_name = "Dashboards"
