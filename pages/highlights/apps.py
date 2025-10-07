from django.apps import AppConfig


class HighlightsConfig(AppConfig):
    """Configuration for the highlights app.

    This app manages data highlights for the Swedish Pathogens Portal,
    providing a way to showcase important research findings and data insights.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.highlights"
    verbose_name = "Data Highlights"
