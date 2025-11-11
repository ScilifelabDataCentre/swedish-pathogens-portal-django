"""Plotly visualization view class for dashboard pages.

This module provides the base view class for dashboard pages that need to fetch
and render Plotly visualizations from external data sources.
"""

import json
import logging
from urllib.error import URLError
from urllib.request import urlopen

from django.core.cache import cache
from utils.views import BaseTemplateView

logger = logging.getLogger(__name__)


class PlotlyDashboardView(BaseTemplateView):
    """Base dashboard view with Plotly data fetching capabilities.

    This class extends BaseTemplateView to provide common functionality for
    dashboard pages that fetch Plotly JSON data from external sources (e.g.,
    blobserver). It handles data fetching, caching, and error handling.

    Attributes:
        PLOTLY_SOURCES (dict): Dictionary mapping chart IDs to data source URLs.
            Chart IDs should use underscores (e.g., "plotly_lineage_six_recent").
        CACHE_TIMEOUT (int): Cache duration in seconds (default: 300 / 5 minutes).
        REQUEST_TIMEOUT (int): HTTP request timeout in seconds (default: 10).

    Example:
        For a dashboard with Plotly visualizations:

        .. code-block:: python

            from pages.dashboards.views.plotly import PlotlyDashboardView

            class MyDashboardView(PlotlyDashboardView):
                template_name = "dashboards/my_dashboard.html"
                title = "My Dashboard"
                PLOTLY_SOURCES = {
                    "plotly_chart_one": "https://example.com/data1.json",
                    "plotly_chart_two": "https://example.com/data2.json",
                }

        The view automatically:
        - Fetches data from all URLs in PLOTLY_SOURCES
        - Caches data for 5 minutes
        - Adds plotly_data dictionary to template context
        - Handles errors gracefully

        Template can access data via:
            plotly_data.plotly_chart_one
            plotly_data.plotly_chart_two
    """

    # Cache and request timeout constants
    CACHE_TIMEOUT = 300  # 5 minutes
    REQUEST_TIMEOUT = 10  # 10 seconds

    # Plotly data source URLs mapped to chart container IDs
    # Override this in subclasses with chart_id -> URL mappings
    PLOTLY_SOURCES = {}

    def _fetch_plotly_data(self, url: str, cache_key: str) -> dict | None:
        """Fetch Plotly JSON data from URL with caching.

        Attempts to retrieve data from cache first. If not cached, fetches from
        the external URL and caches the result. Handles network errors, timeouts,
        and JSON parsing errors gracefully.

        Args:
            url: URL to fetch JSON data from.
            cache_key: Cache key for storing/retrieving data.

        Returns:
            Parsed JSON data as dict, or None if fetch fails. Returns None on
            network errors, timeouts, or invalid JSON responses.

        Example:
            .. code-block:: python

                data = self._fetch_plotly_data(
                    "https://blobserver.dc.scilifelab.se/blob/data.json",
                    "plotly_data_chart1"
                )
                # Returns dict with 'data' and 'layout' keys, or None
        """
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        try:
            with urlopen(url, timeout=self.REQUEST_TIMEOUT) as response:
                data = json.loads(response.read().decode("utf-8"))
                # Cache for configured duration
                cache.set(cache_key, data, self.CACHE_TIMEOUT)
                return data
        except URLError as e:
            logger.warning(f"Network error fetching Plotly data from {url}: {e}")
            return None
        except TimeoutError as e:
            logger.warning(f"Timeout fetching Plotly data from {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON response from {url}: {e}")
            return None

    def get_context_data(self, **kwargs):
        """Add Plotly JSON data to template context.

        Fetches Plotly visualization data for all charts defined in PLOTLY_SOURCES.
        Adds data to context as a dictionary for both JavaScript initialization
        and direct template access.

        Returns:
            dict: Context data with plotly_data dictionary. Chart IDs use
            underscores to enable direct template access (e.g., plotly_data.plotly_lineage_six_recent).

        Example:
            Context includes:
            - plotly_data: {"plotly_lineage_six_recent": {...}, ...}

        Template access:
            plotly_data.plotly_lineage_six_recent
        """
        context = super().get_context_data(**kwargs)

        # Fetch Plotly data for each visualization
        plotly_data = {}
        for chart_id, url in self.PLOTLY_SOURCES.items():
            cache_key = f"plotly_data_{chart_id}"
            data = self._fetch_plotly_data(url, cache_key)
            plotly_data[chart_id] = data

        context["plotly_data"] = plotly_data

        return context

