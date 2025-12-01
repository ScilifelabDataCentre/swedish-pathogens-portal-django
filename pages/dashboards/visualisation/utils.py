"""Common utility functions that can help with visualisation"""

import json
import logging
import re
from functools import lru_cache
from urllib.error import URLError
from urllib.request import urlopen

import plotly.io as pio
from django.core.cache import cache

logger = logging.getLogger(__name__)


# TODO: The following function might be removed in the following
# phases as the blobserver dependency will be removed
def fetch_plot_json_blobserver(blob: str) -> dict | None:
    """Fetch plot data from blobserver

    This is a temporary function to fetch plot related data
    (compiled plot in JSON format) from blobserver.

    Args:
    ----
        blob: Name of the plot file in blobserver

    Returns:
    -------
        Parsed JSON data as dict, or None if fetch fails. Returns None on
        network errors, timeouts, or invalid JSON responses.

    Example:
    -------
        .. code-block:: python

        data = fetch_plot_json_blobserver("some_plot.json")
        # Returns dict with 'data' and 'layout' keys, or None

    """
    cache_key = f"plotly_data_{blob}"
    # check and fetch cache if exists
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    # get data from blobserver if it didn't exist in cache
    url = f"https://blobserver.dc.scilifelab.se/blob/{blob}"
    try:
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        cache.set(cache_key, data, 300)  # 5 minutes
        return data
    except URLError as e:
        logger.warning(f"Network error fetching Plotly data from {url}:\n{e}")
    except TimeoutError as e:
        logger.warning(f"Timeout fetching Plotly data from {url}:\n{e}")
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON response from {url}:\n{e}")
    except Exception as e:
        logger.warning(f"Exception while fetching {url}:\n{e}")
    return None


def plot_html_from_json(
    data: dict | str | None,
    height: str | int = "100%",
    skip_invalid: bool = False,
    include_plotlyjs: str | bool = False,
) -> str | None:
    """Generate graph's HTML string

    Using plotly IO, generate figure from JSON plot data and return
    an HTML string of the plot.

    Args:
        data: Plotly graph's JSON object or string i.e. with "data" and "layout"
        height: Parameter passed to 'to_html' method, the height of the rendered
            plot will be of this value. It can either a int (pixels) or
            str (css notation like '500px' or '100%')
        include_plotlyjs: Parameter passed to 'to_html' method. Can be set to 'cdn'
            if Plotly JS is not available on global level.
        skip_invalid: A boolean parameter to be passed to pio's from_json
            method. If set to true, invalid properties in the JSON object
            will be ignored without raising an exception.

    Returns:
    -------
        An HTML string that can be embedded in the templates directly.
        Return None if the plot html generation failed.

    Example:
    -------
        .. code-block:: python

            graph_html = plot_html_from_json(data=data, height="500px")
            # Returns an HTML string or None if any exception

    """
    if data is not None:
        try:
            if isinstance(data, str):
                jstring = data
            else:
                jstring = json.dumps(data)
            fig = pio.from_json(jstring, skip_invalid=skip_invalid)
            return fig.to_html(
                full_html=False,
                default_height=height,
                include_plotlyjs=include_plotlyjs,
            )
        except ValueError as e:
            logger.warning(f"Invalid JSON data, kindly check the data.\nError: {e}")
        except Exception as e:
            logger.warning(f"Exception while creating plot HTML from JSON\nError: {e}")
    else:
        logger.warning("Provided JSON data should not be 'None'")
    return None


# Provided the value of output doesn't change after the app starts, we can cache
# the function call. This will drastically reduce re-run of the function
@lru_cache
def get_plotlyjs_cdn_param(param: str) -> str | None:
    """Get Plotly JS CDN URL or integrity hash for the current Plotly version.

    This function extracts the Plotly.js CDN URL and integrity hash by generating
    a dummy Plotly HTML output and parsing the script tag. This ensures the
    template uses the Plotly.js version that is compatible with the installed Plotly
    Python library.

    Args:
    ----
        param: Required string parameter. Must be either "url" to get the CDN URL,
            or "hash" to get the integrity hash. For any other values, returns None.

    Returns:
    -------
        If param is "url": Returns the CDN URL string or None if extraction fails.
        If param is "hash": Returns the integrity hash string or None if
            extraction fails.
        Returns None if param is not "url" or "hash", or if the regex pattern
            doesn't match the generated HTML.

    Example:
    -------
        Get the CDN URL:
        .. code-block:: python

            plotlyjs_url = get_plotlyjs_cdn_param("url")
            # Returns: "https://cdn.plot.ly/plotly-3.2.0.min.js"
            # Value may vary depending upon plotly python version

        Get the integrity hash:
        .. code-block:: python

            plotlyjs_hash = get_plotlyjs_cdn_param("hash")
            # Returns: "sha256-iZ2u/oU2wf/vDbl/ChcX93WgbBRSBvUO6N413hDz7xM="
            # Value may vary depending upon plotly python version

        Invalid parameter:
        .. code-block:: python

            result = get_plotlyjs_cdn_param("invalid")
            # Returns: None

    """
    expected_args = ["url", "hash"]
    if param not in expected_args:
        logger.warning("Param should be either 'url' or 'hash'")
        return None
    # generate dummy plot html to pattern search
    html_string = pio.to_html({}, full_html=False, include_plotlyjs="cdn")
    m = re.search(
        r'<script.*?src="([^"]+plotly[^"]+\.js)".*?integrity="(.*?)".*?</script>',
        html_string,
    )
    if m:
        param_match = m.group(expected_args.index(param) + 1)
        logger.info(f"Fetched Plotly JS cdn's {param}: {param_match}")
        return param_match
    else:
        logger.warning(f"Could not find matching pattern for '{param}'")
        return None
