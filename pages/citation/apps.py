from django.apps import AppConfig


class CitationConfig(AppConfig):
    """Configuration for the citation app.

    This app provides information on how to cite the Swedish Pathogens Portal
    when reusing data or referencing the platform in publications.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.citation"
    verbose_name = "Citation"
