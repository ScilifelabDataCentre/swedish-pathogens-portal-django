"""Apps for the Publications page."""

from django.apps import AppConfig


class PublicationsConfig(AppConfig):
    """Configuration for the publications app.

    This app handles the publications section. Publications are used to
    display Sweden affiliated research papers in Europe PMC.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.publications"
    verbose_name = "Publications"
