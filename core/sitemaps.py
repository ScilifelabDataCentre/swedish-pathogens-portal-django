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
            # Keep this list small and stable for fast, reliable CI.
            "home",  # may need "home:index"
            "about",  # may need "about:index"
            "citation",  # may need "citation:index"
            "contact",  # may need "contact:index"
            "privacy",  # may need "privacy:index"
            # Add more index pages once confirmed:
            # "news:index",
            # "topics:index",
            # "outbreaks:index",
            # "dashboards:index",
        ]

    def location(self, item: str) -> str:
        """Resolve URL names to real URLs."""
        return reverse(item)
