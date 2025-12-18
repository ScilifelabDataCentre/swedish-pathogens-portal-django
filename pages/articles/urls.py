"""URL configuration for the articles page."""

from django.urls import path

from .views import ArticleDetailView, ArticleListView

app_name = "articles"

urlpatterns = [
    path("", ArticleListView.as_view(), name="index"),
    path("<slug:slug>/", ArticleDetailView.as_view(), name="detail"),
]
