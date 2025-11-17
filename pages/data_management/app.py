from django.apps import AppConfig


class DataManagementConfig(AppConfig):
    """Configuration for the data management app.
    
    TODO: Some description about the app can go here.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pages.data_management'
    verbose_name = "Data Management"
