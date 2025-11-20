from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    """Configuration for the articles app.

    This app manages articles (data highlights and editorials) for the Swedish
    Pathogens Portal, providing a way to showcase important research findings,
    data insights, and editorial content.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.articles"
    verbose_name = "Articles"
