from django.conf import settings
from django.http import HttpRequest


def plotlyjs(request: HttpRequest) -> dict:
    """Make plotly JS url and hash available in all template's context by default"""
    return {
        "plotlyjs_url": settings.PLOTLYJS_URL,
        "plotlyjs_hash": settings.PLOTLYJS_HASH,
    }
