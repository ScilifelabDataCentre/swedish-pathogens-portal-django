"""Sitemaps used by Pa11y CI.

Defines which public pages Pa11y should scan.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse  # Builds URLs from URL names (avoids hardcoding paths)


class Pa11ySitemap(Sitemap):
    """Pages scanned by Pa11y CI."""

    def items(self) -> list[str]:
        """URL names included in CI scans."""
        return [
            "about:index",
            "articles:index",
            "citation:index",
            "contact:index",
            "dashboards:index",
            "data_management:index",
            "home:index",
            "news:index",
            "outbreaks:index",
            "privacy:index",
            "topics:index",
        ]

    def location(self, item: str) -> str:
        """Resolve URL names to real URLs."""
        return reverse(item)


# Registry used by Django's sitemap view
sitemaps = {
    "pa11y": Pa11ySitemap,
}
