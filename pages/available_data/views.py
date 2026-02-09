"""Views for the Available Data (query links) page."""

import json
import logging
import urllib.request
from typing import Any

from django.core.cache import cache
from django.utils.text import slugify

from utils.views import BaseTemplateView

logger = logging.getLogger(__name__)

# EBI EBIsearch REST API base and Sweden filter (URL-encoded).
# Full URL: BASE_URL + path + SUFFIX; path already contains query params.
EBI_BASE_URL = "https://www.ebi.ac.uk/ebisearch/ws/rest/"
EBI_SUFFIX = "%20((country%3A%22Sweden%22))&size=0&format=JSON&facetcount=0"
CACHE_TTL_SECONDS = 6 * 60 * 60  # 6 hours, same as legacy JS

# EBI path strings for hit-count requests (from legacy query_data.html).
# Keys match context names used in templates.
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


class AvailableDataView(BaseTemplateView):
    """A template view that renders the Available Data (query links) page."""

    template_name = "available_data/index.html"
    title = "Data query links"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add EBI hit counts to template context."""
        context = super().get_context_data(**kwargs)
        for key, path in EBI_QUERY_PATHS.items():
            context[key] = self._fetch_ebi_hit_count(path)
        context["outbreak_total"] = (
            context["outbreak_sequences"]
            + context["outbreak_analysis"]
            + context["outbreak_reads"]
            + context["outbreak_samples"]
            + context["outbreak_assembly"]
        )
        context["pathogens_total"] = (
            context["pathogens_sequence"]
            + context["pathogens_analysis"]
            + context["pathogens_reads"]
            + context["pathogens_assembly"]
        )
        return context

    def _fetch_ebi_hit_count(self, path: str) -> int:
        """Fetch hit count from EBI EBIsearch API for the given query path.

        Uses Django cache with 6-hour TTL. Returns 0 on any error.
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
