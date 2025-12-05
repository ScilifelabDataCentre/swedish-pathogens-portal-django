"""Views for the Publications page."""

import json
import logging
import urllib
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.text import slugify
from django.views import View

from .models import PublicationPathogens

logger = logging.getLogger(__name__)


class Publications(View):
    """Publications page view.

    Handles the display of Sweden affiliated research papers in Europe PMC.
    It fetches 10 recent publications for the pathogens added in the DB.

    Attributes:
        template_name: Template for rendering the dashboard.
        title: Title displayed in the rendered page's banner section.
        description: Description to be used in the HTML's head.
    """

    template_name = "publications/index.html"
    title = "Publications"
    description = "A collection of Sweden affiliated research papers in Europe PMC."

    def get(self, request: HttpRequest) -> HttpResponse:
        """To render the publications page."""

        pathogens_list = PublicationPathogens.objects.filter(is_active=True).order_by("name")
        pathogen = request.GET.get("pathogen", "")
        context = {"pathogens": pathogens_list}
        # Determine the active pathogen
        if pathogen:
            try:
                active_pathogen = pathogens_list.get(name=pathogen)
            except PublicationPathogens.DoesNotExist:
                logger.warning(f"Pathogen '{pathogen}' not found in the database.")
                context["no_query_pathogen"] = pathogen
                active_pathogen = None
        else:
            active_pathogen = pathogens_list.first()

        # Get publications for the active pathogen
        if active_pathogen:
            context["europe_pmc_full_list"] = (
                f'{settings.EUROPE_PMC_WEB_URL}?query={active_pathogen.query_string} AND AFF:"Sweden"'
            )
            context["active_pathogen"] = active_pathogen.name

        # if HTMX request, return only the publications list
        if request.htmx:
            context["publications"] = (
                self._get_pathogen_publications(active_pathogen.name, active_pathogen.query_string)
                if active_pathogen
                else []
            )
            return render(request, "publications/list.html", context)

        # Full page render
        context["title"] = self.title
        context["description"] = self.description

        return render(request, self.template_name, context)

    def _get_pathogen_publications(self, pathogen: str, query_string: str) -> list:
        """Fetch publications for a given pathogen from Europe PMC API.

        First, it checks if cached data is available. If not, it fetches
        fresh data using the API and caches it. Caches are valid for 30 minutes.
        """

        # Build the Europe PMC API query URL
        now = datetime.now()
        past_year = f"{now.year - 1}-{now.month:02d} TO {now.year}-{now.month:02d}"
        query_string += f' AND AFF:"Sweden" AND PUB_YEAR:[{past_year}]'
        formatted_query = urllib.parse.quote(query_string)

        # Check for cached data
        cache_key = slugify(f"publications_{pathogen}_{query_string}")
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        # Try to fetch data from the Europe PMC API
        publications = []
        europe_pmc_api_query_url = f"{settings.EUROPE_PMC_API_URL}&query={formatted_query}"
        try:
            # TODO: When a common HTTP utility is available, the following code should be replaced.
            with urllib.request.urlopen(europe_pmc_api_query_url, timeout=10) as response:  # noqa: S310
                data = response.read().decode("utf-8")
                json_data = json.loads(data)
                pubs = json_data.get("resultList", {}).get("result", [])
                for pub in pubs:
                    publication = {
                        "title": pub.get("title"),
                        "authors": pub.get("authorString"),
                        "journal": pub.get("journalInfo", {}).get("journal", {}).get("title"),
                        "doi": pub.get("doi"),
                        "url": f"https://doi.org/{pub.get('doi')}",
                    }
                    publications.append(publication)
        except Exception as e:
            logger.error(
                f"Error fetching publications for pathogen '{pathogen}' with '{query_string}': {e}"
            )
            return []

        # Cache the fetched data for 30 minutes
        cache.set(cache_key, publications, 30 * 60)

        return publications
