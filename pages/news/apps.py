from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Configuration for the news app.
    
    TODO: Add short description of news app here.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.news"
    verbose_name = "News"