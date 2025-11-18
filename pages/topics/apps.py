from django.apps import AppConfig


class TopicsConfig(AppConfig):
    """Configuration for the topics app.

    This app handles the topics section. Topics are used to 
    subdivide content (e.g. dashboards, available data) on the site.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.topics"
    verbose_name = "Topics"
