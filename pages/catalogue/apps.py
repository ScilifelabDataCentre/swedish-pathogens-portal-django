"""Configuration for the catalogue app."""

from django.apps import AppConfig


class CatalogueConfig(AppConfig):
    """Configuration for the catalogue app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.catalogue"
    verbose_name = "Catalogue"
