"""App configuration for the outbreaks app."""

from django.apps import AppConfig


class OutbreaksConfig(AppConfig):
    """Configuration for the outbreaks app.

    This app manages disease outbreaks affecting Sweden, providing information
    about current and historical outbreaks with comprehensive details about
    pathogens, transmission, timelines, and data visualizations.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.outbreaks"
    verbose_name = "Outbreaks"
