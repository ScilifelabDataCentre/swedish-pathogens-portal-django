"""Views for the Available Data page (dataset counts and query links)."""

import json
import logging
import urllib.request

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.text import slugify
from django.views.generic import View

logger = logging.getLogger(__name__)

# EMBL-EBI EBIsearch REST API base URL and Sweden filter (URL-encoded).
# Request URL is built as EBI_BASE_URL + path + EBI_SUFFIX; each path
# includes its own query parameters.
EBI_BASE_URL = "https://www.ebi.ac.uk/ebisearch/ws/rest/"
EBI_SUFFIX = "%20((country%3A%22Sweden%22))&size=0&format=JSON&facetcount=0"
CACHE_TTL_SECONDS = 6 * 60 * 60  # 6 hours

# EBI main path for each category. Not used directly for counts
# but passed to the template for query links.
EBI_WEB_PATHS = {
    "outbreaks": {"mpath": "priority-pathogens", "qpath": "priorityPathogens"},
    "pathogens sequences": {"mpath": "sequences", "qpath": "sequences"},
    "samples": {"mpath": "samples", "qpath": "samples"},
}

# EBI index paths used to fetch hit counts. Dictionary keys are the
# context variable names passed to the template.
EBI_QUERY_PATHS = {
    # Outbreaks (priority pathogens)
    "outbreaks": {
        "sequences": "embl-pathogen/?query=(tag%3A(%22pathogen%3Apriority%22))",
        "analysis": "sra-analysis/?query=(tag%3A(%22pathogen%3Apriority%22))",
        "raw reads": "sra-experiment/?&query=(tag%3A(%22pathogen%3Apriority%22))",
        "samples": "sra-sample/?query=(tag%3A(%22pathogen%3Apriority%22))",
        "assembly": "genome_assembly/?query=(tag%3A(%22pathogen%3Apriority%22))",
    },
    # Pathogens sequences
    "pathogens sequences": {
        "sequence": "embl-pathogen/?&query=(id%3A%5B*%20TO%20*%5D)",
        "analysis": (
            "sra-analysis/?query=((tag%3A%22pathogen%22)%20AND%20(tag%3A(*%3A*%20NOT%20%22covid19%22)))"
        ),
        "raw reads": "sra-experiment/?&query=(tag%3Apathogen%20AND%20NOT%20tag%3Acovid19)",
        "assembly": (
            "genome_assembly/?query=((tag%3A%22pathogen%22)%20AND%20(tag%3A(*%3A*%20NOT%20%22covid19%22)))"
        ),
    },
    # Samples
    "samples": {"samples": "sra-sample/?&query=(tag%3A%22pathogen%22%20AND%20NOT%20tag%3Acovid19)"},
}


class AvailableDataView(View):
    """Renders the Available Data page; counts are loaded lazily via htmx."""

    template_name = "available_data/index.html"
    title = "Available datasets"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        """Return counts fragment for htmx when get_counts=true; otherwise full page."""

        context = {"title": self.title}

        if request.htmx and request.GET.get("get_counts"):
            count_context = {}
            # Loop through EBI_QUERY_PATHS to fetch hit counts for each category and subcategory.
            for key, links in EBI_QUERY_PATHS.items():
                count_context[key] = {
                    "main_path": EBI_WEB_PATHS[key]["mpath"],
                    "query_path": EBI_WEB_PATHS[key]["qpath"],
                    "counts": {},
                    "total_count": 0,
                }
                for subkey, path in links.items():
                    count_context[key]["counts"][subkey] = {}
                    _count = self._fetch_ebi_hit_count(path)

                    count_context[key]["total_count"] += _count
                    count_context[key]["counts"][subkey]["count"] = _count

                    # Extract main path (first segment) for query link; this is used to determine
                    # which EBI index to query when the user clicks the link in the UI.
                    count_context[key]["counts"][subkey]["path"] = path.split("/")[0]

            return render(
                request,
                "available_data/counts_sections.html",
                {"count_context": count_context},
            )

        return render(request, self.template_name, context)

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
            # TODO: When a common HTTP utility is available, the following code should be replaced
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
