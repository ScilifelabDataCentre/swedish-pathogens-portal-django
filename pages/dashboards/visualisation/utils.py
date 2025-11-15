"""Common utility functions that can help with visualisation"""

import json
import logging

from urllib.error import URLError
from urllib.request import urlopen

import plotly.io as pio

logger = logging.getLogger(__name__)


# TODO: The following function might be removed in the following
# phases as the blobserver depedancy will be removed
def fetch_plot_json_blobserver(blob):
    """Fetch plot data from blobserver

    This is a temporary function to fetch plot related data (compiled
    plot in JSON format)from blobserver.

    Args:
        blob: Name of the plot file in blobserver

    Returns:
        Parsed JSON data as dict, or None if fetch fails. Returns None on
        network errors, timeouts, or invalid JSON responses.

    Example:
        .. code-block:: python

        data = fetch_plot_json_blobserver("some_plot.json")
        # Returns dict with 'data' and 'layout' keys, or None
    """

    url = f"https://blobserver.dc.scilifelab.se/blob/{blob}"
    try:
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
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
    data, height="100%", include_plotlyjs="cdn", skip_invalid=False
):
    """Generate graph's HTML string

    Using plotly IO, generate figure from JSON plot data and return
    a HTML string of the plot.

    Args:
        data: Plotly graph's JSON object i.e. with "data" and "layout"
        height: Parameter passed to 'to_html' method, the height of the rendered
            plot will be of this value. It can either a int (pixels) or
            str (css notation like '500px' or '100%')
        include_plotlyjs: Parameter passed to 'to_html' method. Default value 'cdn',
            this will include <script> tag to load the plotly JS library in the
            generated HTML. If set to False, it will not be included.
        skip_invalid: A boolean paramater to be passed to pio's from_json
            method. If set to true, invaild properties in the JSON object
            will be ignored without raising an exception.

    Returns:
        A HTML string that can be embedded in the templates directly.
        if 'raise_exception' is set to 'True', then it returns 'None'
        when there is an exception.

    Example:
        .. code-block:: python

            graph_html = plot_html_from_json(data=data, height="500px")
            # Returns a HTML string or None if any exception
    """

    try:
        jstring = json.dumps(data)
        fig = pio.from_json(jstring, skip_invalid=skip_invalid)
        return fig.to_html(
            full_html=False, include_plotlyjs=include_plotlyjs, default_height=height
        )
    except ValueError as e:
        logger.warning(f"Invalid JSON data, kindly check the data.\nError: {e}")
    except Exception as e:
        logger.warning(f"Exception while generating plot HTML from JSON\nError: {e}")
    return None
