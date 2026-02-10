"""Configuration for the highlights and editorials app."""

from django.apps import AppConfig


class HighlightsAndEditorialsConfig(AppConfig):
    """Configuration for the highlights and editorials app.

    This app manages highlights and editorials for the Swedish
    Pathogens Portal, providing a way to showcase important
    research findings, data insights, and editorial content.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.highlights_and_editorials"
    verbose_name = "Highlights and Editorials"
