"""Configuration for the contact app."""

from django.apps import AppConfig


class ContactConfig(AppConfig):
    """Configuration for the contact app.

    This app provides a native contact form with built-in
    anti-spam measures for the Swedish Pathogens Portal.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.contact"
    verbose_name = "Contact"
