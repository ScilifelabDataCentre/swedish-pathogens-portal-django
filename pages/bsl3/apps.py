"""Apps for BSL3 page."""

from django.apps import AppConfig


class Bsl3Config(AppConfig):
    """App configuration for BSL3 page."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.bsl3"
    verbose_name = "BSL3 Network"
