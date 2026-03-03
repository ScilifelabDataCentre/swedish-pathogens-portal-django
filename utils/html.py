"""HTML utility functions for building safe markup in view contexts."""

from django.utils.html import format_html_join
from django.utils.safestring import SafeString


def safe_link(*pairs: tuple[str, str], sep: str = " / ") -> SafeString:
    """Build one or more external links joined by *sep*, marked safe.

    Each argument is a `(url, label)` tuple. Both values are escaped
    via `format_html` so dynamic data (e.g. from a database) is safe.

    Examples:
        safe_link(("https://example.org", "Example"))
        safe_link(("https://a.com", "A"), ("https://b.com", "B"))
    """
    return format_html_join(
        sep,
        '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
        pairs,
    )
