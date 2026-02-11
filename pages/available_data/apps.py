"""Configuration for the available_data app."""

from django.apps import AppConfig


class AvailableDataConfig(AppConfig):
    """App config for the Available Data page.

    Shows Swedish dataset counts from the Central Pathogens Portal (EMBL-EBI)
    and links to filtered results on pathogensportal.org.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.available_data"
    verbose_name = "Available Data"
