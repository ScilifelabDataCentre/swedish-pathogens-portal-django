"""Configuration for the Share Data app."""

from django.apps import AppConfig


class ShareDataConfig(AppConfig):
    """Configuration for the Share Data app.

    This app handles the Share data page,
    which provides advice and links to data sharing information and resources.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.share_data"
    verbose_name = "Share Data"
