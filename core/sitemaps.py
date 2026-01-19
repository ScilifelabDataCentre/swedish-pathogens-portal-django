"""Sitemaps used by Pa11y CI.

Auto-includes named, static URLs.
Dynamic URLs are a TODO / up for discussion.
"""

from collections.abc import Iterable

from django.contrib.sitemaps import Sitemap
from django.urls import URLPattern, URLResolver, get_resolver, reverse


def _iter_static_named_urls(
    url_patterns: Iterable[
        URLPattern | URLResolver
    ],  # url_patterns are a mix of URLPattern and URLResolver
    namespace: str | None = None,
) -> Iterable[str]:
    """Find all static, named pages."""
    for entry in url_patterns:
        # URLResolvers need to be recursed into to find their URLPatterns
        if isinstance(entry, URLResolver):  # example of entry: admin, home, about, etc.
            # Get all namespaces e.g. about:index/partners/funders/nodes
            ns = (
                entry.namespace or namespace
            )  # NOTE: Update this if we include nested namespaces (about:partners:...)
            yield from _iter_static_named_urls(url_patterns=entry.url_patterns, namespace=ns)
            continue

        if not isinstance(entry, URLPattern):
            continue

        # Only include named, static paths (no converters like <slug:...>)
        if entry.name and not entry.pattern.converters:
            yield f"{namespace}:{entry.name}" if namespace else entry.name


class Pa11yAutoSitemap(Sitemap):
    """Sitemap for Pa11y (static URLs only)."""

    APP_NAMESPACES = [
        "about",
        "articles",
        "citation",
        "contact",
        "dashboards",
        "data_management",
        "home",
        "news",
        "outbreaks",
        "privacy",
        "topics",
    ]

    def items(self) -> list[str]:
        """All static and named URLs found under the namespaces above."""
        # Get all named URLs
        # Set to avoid duplicates
        all_names = set(_iter_static_named_urls(url_patterns=get_resolver().url_patterns))

        allowed = tuple(f"{ns}:" for ns in self.APP_NAMESPACES)
        return sorted(name for name in all_names if name.startswith(allowed))

    def location(self, item: str) -> str:
        """Resolve a URL name to a path."""
        return reverse(item)


sitemaps = {"pa11y": Pa11yAutoSitemap}
