"""URL configuration for Pathogens Portal project.

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

# Third-party imports
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

# Local imports
from core.sitemaps import sitemaps
from core.views import healthz

# not part of public scan - skipping namespace
core_urls = [
    path(settings.ADMIN_URL, admin.site.urls, name="admin"),
    path("healthz/", healthz, name="healthz"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

page_urls = [
    path("", include(("pages.home.urls", "home"), namespace="home")),
    path("articles/", include(("pages.articles.urls", "articles"), namespace="articles")),
    path("about/", include(("pages.about.urls", "about"), namespace="about")),
    path("citation/", include(("pages.citation.urls", "citation"), namespace="citation")),
    path("contact/", include(("pages.contact.urls", "contact"), namespace="contact")),
    path("dashboards/", include(("pages.dashboards.urls", "dashboards"), namespace="dashboards")),
    path(
        "data-management/",
        include(("pages.data_management.urls", "data_management"), namespace="data_management"),
    ),
    path("news/", include(("pages.news.urls", "news"), namespace="news")),
    path("outbreaks/", include(("pages.outbreaks.urls", "outbreaks"), namespace="outbreaks")),
    path("privacy/", include(("pages.privacy.urls", "privacy"), namespace="privacy")),
    path("topics/", include(("pages.topics.urls", "topics"), namespace="topics")),
]

urlpatterns = core_urls + page_urls

# Auto browser reload addition for local development
if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),  # skipping namespace
    ]
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
