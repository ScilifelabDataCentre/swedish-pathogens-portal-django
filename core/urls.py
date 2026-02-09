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
    path("", include("pages.home.urls")),
    path("about/", include("pages.about.urls")),
    path("catalogue/", include("pages.catalogue.urls")),
    path("citation/", include("pages.citation.urls")),
    path("contact/", include("pages.contact.urls")),
    path("dashboards/", include("pages.dashboards.urls")),
    path("highlights-and-editorials/", include("pages.highlights_and_editorials.urls")),
    path("news/", include("pages.news.urls")),
    path("outbreaks/", include("pages.outbreaks.urls")),
    path("plp-program/", include("pages.plp.urls")),
    path("portal-data/", include("pages.portal_data.urls")),
    path("privacy/", include("pages.privacy.urls")),
    path("publications/", include("pages.publications.urls")),
    path("register-based-research/", include("pages.register_based_research.urls")),
    path("share-data/", include("pages.share_data.urls")),
    path("topics/", include("pages.topics.urls")),
]

urlpatterns = core_urls + page_urls

# Auto browser reload addition for local development
if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
