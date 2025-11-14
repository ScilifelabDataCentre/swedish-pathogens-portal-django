"""
URL configuration for Pathogens Portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def healthz(_request):
    """Health check endpoint.
    
    Used for monitoring uptime of the service.
    Always returns a JSON object indicating that the service is running.
    
    Args: 
        _request: Incoming HTTP request object (not used)
    
    Returns:
        JsonResponse: A JSON response indicating service status. 
            Always returns 200 OK with {"status": "ok"} unless there is a server issue.
    """
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls, name="admin"),
    path("healthz/", healthz, name="healthz"),
    path("", include("pages.home.urls")),
    path("articles/", include("pages.articles.urls")),
    path("about/", include("pages.about.urls")),
    path("citation/", include("pages.citation.urls")),
    path("dashboards/", include("pages.dashboards.urls")),
    path("data-management/", include("pages.data_management.urls")),
    path("news/", include("pages.news.urls")),
    path("privacy/", include("pages.privacy.urls")),
    path("topics/", include("pages.topics.urls")),
]

# Auto browser reload addition for local development
if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
