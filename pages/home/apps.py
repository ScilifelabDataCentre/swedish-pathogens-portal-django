from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the home app.
    
    This app serves as the home page for the Swedish Pathogens Portal.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.home"
    verbose_name = "Home"
