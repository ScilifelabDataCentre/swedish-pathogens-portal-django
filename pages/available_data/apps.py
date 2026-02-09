"""Configuration for the available_data app."""

from django.apps import AppConfig


class AvailableDataConfig(AppConfig):
    """Configuration for the available_data app.

    This app provides the Available Data (query links) page, showing
    how many Swedish datasets there are in the Central Pathogens Portal
    and linking to query results on pathogensportal.org.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.available_data"
    verbose_name = "Available Data"
