"""Configuration for the news app."""

from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Configuration for the news app.

    This app handles and displays news, updates and announcements for the portal.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.news"
    verbose_name = "News"
