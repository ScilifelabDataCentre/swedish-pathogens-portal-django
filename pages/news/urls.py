from django.urls import path
from .views import NewsIndex, NewsDetail

app_name = "news"

urlpatterns = [
    path("", NewsIndex.as_view(), name="index"),
    path("<slug:slug>/", NewsDetail.as_view(), name="detail"),
]
