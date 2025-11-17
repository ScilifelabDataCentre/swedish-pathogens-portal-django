from django.apps import AppConfig


class CitationConfig(AppConfig):
    """Configuration for the citation app.
    
    This app handles citation information and guidelines for the Swedish
    Pathogens Portal, ensuring proper acknowledgment of the portal in academic
    and research publications."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.citation"
    verbose_name = "Citation"

