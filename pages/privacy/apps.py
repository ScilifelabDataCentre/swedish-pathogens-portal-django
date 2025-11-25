from django.apps import AppConfig


class PrivacyConfig(AppConfig):
    """Configuration for the privacy app.

    This app handles the privacy page, which informs users
    about what data is collected about them when using the site,
    and how it is handled.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.privacy"
    verbose_name = "Privacy"
