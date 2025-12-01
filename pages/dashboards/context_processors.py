"""Context processors for dashboards page."""

from django.http import HttpRequest

from pages.dashboards.visualisation.utils import get_plotlyjs_cdn_param


def plotlyjs(request: HttpRequest) -> dict:
    """Make plotly JS url and hash available in all template's context by default."""
    return {
        "plotlyjs_url": get_plotlyjs_cdn_param("url"),
        "plotlyjs_hash": get_plotlyjs_cdn_param("hash"),
    }
