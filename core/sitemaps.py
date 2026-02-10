"""Sitemaps used by Pa11y CI.

Auto-includes named, static URLs.
Dynamic URLs are a TODO / up for discussion, as are nested namespaces.
"""

from collections.abc import Iterable

from django.contrib.sitemaps import Sitemap
from django.urls import URLPattern, URLResolver, get_resolver, reverse


def _iter_static_named_urls(
    url_patterns: Iterable[URLPattern | URLResolver],
    namespace: str | None = None,
) -> Iterable[str]:
    """Find all static, named pages.

    Args:
        url_patterns: Iterable containing URLPattern and/or URLResolver objects.
            URLPattern = concrete route (i.e. path(...))
            URLResolver = include(...) block --> need to recurse into it
        namespace: Current namespace (if any)

    Yields:
        str: Fully namespaced URL name for each static named URL found (e.g. "about:index").
    """
    for entry in url_patterns:
        # Top-level URL configs will resolve true, e.g. about, articles, etc.
        if isinstance(entry, URLResolver):
            # Get all namespaces e.g. about:index/partners/funders/nodes
            # Single-level namespaces only for now
            child_namespace = entry.namespace or namespace
            yield from _iter_static_named_urls(
                url_patterns=entry.url_patterns, namespace=child_namespace
            )
            continue

        # Skip anything that is not a concrete route
        if not isinstance(entry, URLPattern):
            continue

        # Only include named, static paths
        if entry.name and not entry.pattern.converters:
            yield f"{namespace}:{entry.name}" if namespace else entry.name


class SPPAutoSitemap(Sitemap):
    """Sitemap for Pa11y (static URLs only).

    Can potentially be used for other purposes beyond Pa11y.
    """

    PUBLIC_APPS = [
        "about",
        "articles",
        "available_data",
        "citation",
        "contact",
        "dashboards",
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

        # Only include URLs under the defined namespaces
        allowed_prefixes = tuple(f"{ns}:" for ns in self.PUBLIC_APPS)
        return sorted(name for name in all_names if name.startswith(allowed_prefixes))

    def location(self, item: str) -> str:
        """Resolve a URL name to a path."""
        return reverse(item)


sitemaps = {"pa11y": SPPAutoSitemap}
