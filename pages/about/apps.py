from django.apps import AppConfig


class AboutConfig(AppConfig):
    """Configuration for the about app.
    
    This app provides information about the Swedish Pathogens Portal,
    including its mission, team, and contact details.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.about"
    verbose_name = "About"