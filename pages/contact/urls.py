from django.urls import path
from .views import Contact

app_name = "contact"

urlpatterns = [
    path("", Contact.as_view(), name="contact"),
]
