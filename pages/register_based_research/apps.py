from django.apps import AppConfig


class RegisterBasedResearchConfig(AppConfig):
    """Configuration for the register based research app.

    This app handles the register based research page,
    which contains information on Swedish Registers with data for re-use.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.register_based_research"
    verbose_name = "Register Based Research"
