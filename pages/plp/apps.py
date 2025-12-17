from django.apps import AppConfig


class PlpConfig(AppConfig):
    """Configuration for the PLP app.

    This app manages information about the Pandemic Laboratory Preparedness (PLP)
    program at SciLifeLab, including project listings and detailed information
    about preparedness capabilities.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.plp"
    verbose_name = "Pandemic Laboratory Preparedness"
