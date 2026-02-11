"""Views for the Available Data page (dataset counts and query links)."""

import json
import logging
import urllib.request
from typing import Any

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.text import slugify

from utils.views import BaseTemplateView

logger = logging.getLogger(__name__)

# EMBL-EBI EBIsearch REST API base URL and Sweden filter (URL-encoded).
# Request URL is built as EBI_BASE_URL + path + EBI_SUFFIX; each path
# includes its own query parameters.
EBI_BASE_URL = "https://www.ebi.ac.uk/ebisearch/ws/rest/"
EBI_SUFFIX = "%20((country%3A%22Sweden%22))&size=0&format=JSON&facetcount=0"
CACHE_TTL_SECONDS = 6 * 60 * 60  # 6 hours

# EBI index paths used to fetch hit counts. Dictionary keys are the
# context variable names passed to the template.
EBI_QUERY_PATHS: dict[str, str] = {
    # Outbreaks (priority pathogens)
    "outbreak_sequences": "embl-pathogen/?query=(tag%3A(%22pathogen%3Apriority%22))",
    "outbreak_analysis": "sra-analysis/?query=(tag%3A(%22pathogen%3Apriority%22))",
    "outbreak_reads": "sra-experiment/?&query=(tag%3A(%22pathogen%3Apriority%22))",
    "outbreak_samples": "sra-sample/?query=(tag%3A(%22pathogen%3Apriority%22))",
    "outbreak_assembly": "genome_assembly/?query=(tag%3A(%22pathogen%3Apriority%22))",
    # Pathogens sequences
    "pathogens_sequence": "embl-pathogen/?&query=(id%3A%5B*%20TO%20*%5D)",
    "pathogens_analysis": (
        "sra-analysis/?query=((tag%3A%22pathogen%22)%20AND%20(tag%3A(*%3A*%20NOT%20%22covid19%22)))"
    ),
    "pathogens_reads": "sra-experiment/?&query=(tag%3Apathogen%20AND%20NOT%20tag%3Acovid19)",
    "pathogens_assembly": (
        "genome_assembly/?query=((tag%3A%22pathogen%22)%20AND%20(tag%3A(*%3A*%20NOT%20%22covid19%22)))"
    ),
    # Samples
    "samples_total": (
        "sra-sample/?&query=((tag%3A%22pathogen%22)%20AND%20(tag%3A(*%3A*%20NOT%20%22covid19%22)))"
    ),
}


def _build_ebi_counts_context() -> dict[str, int]:
    """Fetch EBI hit counts and return context dict for template."""
    view = _EBICountsMixin()
    counts: dict[str, int] = {}
    for key, path in EBI_QUERY_PATHS.items():
        counts[key] = view._fetch_ebi_hit_count(path)
    counts["outbreak_total"] = (
        counts["outbreak_sequences"]
        + counts["outbreak_analysis"]
        + counts["outbreak_reads"]
        + counts["outbreak_samples"]
        + counts["outbreak_assembly"]
    )
    counts["pathogens_total"] = (
        counts["pathogens_sequence"]
        + counts["pathogens_analysis"]
        + counts["pathogens_reads"]
        + counts["pathogens_assembly"]
    )
    return counts


class _EBICountsMixin:
    """Mixin that provides _fetch_ebi_hit_count for use when building counts context."""

    def _fetch_ebi_hit_count(self, path: str) -> int:
        """Return hit count from EMBL-EBI EBIsearch API for the given path.

        Results are cached for CACHE_TTL_SECONDS. Returns 0 on request
        or parse errors.
        """
        cache_key = f"available_data_ebi_{slugify(path)}"
        cached = cache.get(cache_key)
        if cached is not None:
            return int(cached)

        query_url = f"{EBI_BASE_URL}{path}{EBI_SUFFIX}"
        try:
            with urllib.request.urlopen(query_url, timeout=10) as response:  # noqa: S310
                data = json.loads(response.read().decode("utf-8"))
            hit_count = int(data.get("hitCount", 0))
            cache.set(cache_key, hit_count, CACHE_TTL_SECONDS)
            return hit_count
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            logger.warning("EBI request failed for %s: %s", path[:50], e)
            return 0
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.warning("EBI response parse error for %s: %s", path[:50], e)
            return 0
        except OSError as e:
            logger.warning("EBI request error for %s: %s", path[:50], e)
            return 0


class AvailableDataView(BaseTemplateView):
    """Renders the Available Data page; counts are loaded lazily via htmx."""

    template_name = "available_data/index.html"
    title = "Available datasets"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        """Return counts fragment for htmx when get_counts=true; otherwise full page."""
        if request.htmx and request.GET.get("get_counts"):
            context = _build_ebi_counts_context()
            return render(
                request,
                "available_data/fragments/counts_sections.html",
                context,
            )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Do not fetch EBI here; htmx loads counts via GET ?get_counts=true."""
        return super().get_context_data(**kwargs)
