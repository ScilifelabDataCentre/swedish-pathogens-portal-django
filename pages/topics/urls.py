"""URL configurations for the topics page."""

from django.urls import path

from .views import TopicDetailView, TopicListView

app_name = "topics"

urlpatterns = [
    path("", TopicListView.as_view(), name="index"),
    path("<slug:slug>/", TopicDetailView.as_view(), name="detail"),
]
