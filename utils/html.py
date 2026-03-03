"""HTML utility functions for building safe markup in view contexts."""

from django.utils.safestring import mark_safe


def safe_link(*pairs: tuple[str, str], sep: str = " / ") -> str:
    """Build one or more external links joined by *sep*, marked safe.

    Each argument is a `(url, label)` tuple.

    Examples:
        safe_link(("https://example.org", "Example"))
        safe_link(("https://a.com", "A"), ("https://b.com", "B"))
    """
    return mark_safe(
        sep.join(
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>'
            for url, label in pairs
        )
    )
