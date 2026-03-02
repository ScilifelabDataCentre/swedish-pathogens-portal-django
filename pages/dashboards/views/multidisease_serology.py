"""Views for the multi-disease serology dashboard.

This module defines the `MultiDiseaseSerology` view which renders a dashboard
by fetching two Excel files from blobserver, parsing them server-side, and
exposing normalised table data to the template. The view uses `DataTableMixin`
to provide search, pagination, and configurable entries per page via the
reusable data table component.
"""

from __future__ import annotations

import logging
from io import BytesIO
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import polars as pl
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from core.mixins import DataTableMixin

KTH_XLSX_URL = "https://blobserver.dc.scilifelab.se/blob/KTH-produced-antigens.xlsx"
EXTERNAL_XLSX_URL = "https://blobserver.dc.scilifelab.se/blob/External-PLP-proteinlist.xlsx"
REQUEST_TIMEOUT_SECONDS = 10
USER_AGENT = "pathogens-portal/multidisease-serology"
CACHE_TTL_SECONDS = 15 * 60  # cache XLSX-derived rows for 15 minutes

KTH_TABLE_ID = "kth-proteins"
EXTERNAL_TABLE_ID = "external-antigens"

# Explicit column orders for deterministic display
KTH_HEADERS: list[str] = ["Virus type", "Variant", "Protein", "Details", "Host"]
EXTERNAL_HEADERS: list[str] = ["Pathogen", "Variant", "Protein", "Details", "Host"]

logger = logging.getLogger(__name__)


class MultiDiseaseSerology(DataTableMixin, View):
    """Render the multidisease serology dashboard.

    On a full-page GET the view fetches two XLSX blobs (KTH-produced and external antigens),
    parses them with Polars, and passes each dataset through `DataTableMixin.get_table_context()`
    so the template renders them as interactive, searchable, paginated tables.

    On an HTMX request (search / pagination / entries-per-page change) only the affected
    table's content partial is returned for an in-place swap.

    Attributes:
        template_name: Template that renders the descriptive copy and tables.
        title: Page title that appears in the shared layout.
        page_heading: Heading that appears in the shared layout.

    """

    template_name = "dashboards/multidisease_serology.html"
    title = "Multi-disease serology"
    page_heading = "Dashboards"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        """Handle both full-page and HTMX partial requests."""
        # HTMX controls on the table send requests back to this same URL
        table_url = request.path

        # HTMX request: return only the content partial for the table the
        # user interacted with (identified by the hidden table_id field)
        if request.htmx:
            return self._htmx_response(request, table_url)

        # Full-page request: load both datasets and build table contexts
        return self._full_page_response(request, table_url)

    def _full_page_response(self, request: HttpRequest, table_url: str) -> HttpResponse:
        """Load both datasets and render the complete page."""
        kth_rows = self._load_rows(KTH_XLSX_URL, KTH_HEADERS, "kth")
        external_rows = self._load_rows(EXTERNAL_XLSX_URL, EXTERNAL_HEADERS, "external")

        context = {
            "title": self.title,
            "page_heading": self.page_heading,
            "kth_table": self.get_table_context(
                request,
                kth_rows,
                KTH_HEADERS,
                table_url,
                table_id=KTH_TABLE_ID,
            ),
            "external_table": self.get_table_context(
                request,
                external_rows,
                EXTERNAL_HEADERS,
                table_url,
                table_id=EXTERNAL_TABLE_ID,
            ),
        }
        return render(request, self.template_name, context)

    def _htmx_response(self, request: HttpRequest, table_url: str) -> HttpResponse:
        """Return only the swappable content partial for the requested table.

        The hidden `table_id` field sent via `hx-include` tells us which table the
        user interacted with. Only that table's data is loaded and paginated.
        """
        requested_id = request.GET.get("table_id")

        if requested_id == KTH_TABLE_ID:
            rows = self._load_rows(KTH_XLSX_URL, KTH_HEADERS, "kth")
            ctx = self.get_table_context(
                request,
                rows,
                KTH_HEADERS,
                table_url,
                table_id=KTH_TABLE_ID,
            )
        elif requested_id == EXTERNAL_TABLE_ID:
            rows = self._load_rows(EXTERNAL_XLSX_URL, EXTERNAL_HEADERS, "external")
            ctx = self.get_table_context(
                request,
                rows,
                EXTERNAL_HEADERS,
                table_url,
                table_id=EXTERNAL_TABLE_ID,
            )
        else:
            # Unexpected or missing table_id falls back to full-page render
            return self._full_page_response(request, table_url)

        # Render the content partial under the "t" namespace expected by
        # data_table_content.html (e.g. {{ t.page_obj }}, {{ t.headers }})
        return render(request, "components/data_table_content.html", {"t": ctx})

    def _load_rows(self, url: str, headers: list[str], source: str) -> list[list[Any]]:
        """Fetch, parse, normalise, and cache table data."""
        cache_key = f"multidisease_serology_rows_{source}"
        cached_rows = cache.get(cache_key)
        if cached_rows is not None:
            logger.debug("serology_fetch_cache_hit", extra={"source": source})
            return cached_rows

        try:
            logger.info("serology_fetch_start", extra={"source": source, "url": url})
            frame = self._read_excel_frame(url)
            logger.info("serology_fetch_success", extra={"source": source, "records": frame.height})
        except Exception:
            logger.exception("serology_fetch_failed", extra={"source": source, "url": url})
            return []
        rows = self._frame_to_rows(frame, headers)
        cache.set(cache_key, rows, CACHE_TTL_SECONDS)
        return rows

    def _read_excel_frame(self, url: str) -> pl.DataFrame:
        """Fetch an Excel sheet using urllib and parse it with Polars."""
        parsed_url = urlparse(url)
        if parsed_url.scheme not in {"http", "https"}:
            raise ValueError(f"Unsupported URL scheme for serology XLSX fetch: {parsed_url.scheme}")
        request = Request(url, headers={"User-Agent": USER_AGENT})  # noqa: S310 - already validated above and temporary
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:  # noqa: S310 - already validated above and temporary
            payload = BytesIO(response.read())
        payload.seek(0)
        # Polars read_excel uses Rust calamine engine which requires fastexcel for performance.
        # This dependency is not installed by default, so it was added manually.
        # TODO: Remove it once we have a proper data pipeline.
        frame = pl.read_excel(source=payload, sheet_id=0)
        # Polars returns a dict when the backend loads multiple worksheets; grab the first sheet.
        return next(iter(frame.values())) if isinstance(frame, dict) else frame

    def _frame_to_rows(self, frame: pl.DataFrame, headers: list[str]) -> list[list[Any]]:
        """Project a Polars frame onto expected columns and normalise values."""
        if frame.is_empty():
            return []

        projected = frame.select(
            [
                (pl.col(header).cast(pl.String, strict=False).fill_null("").alias(header))
                if header in frame.columns
                else pl.lit("").alias(header)
                for header in headers
            ]
        )
        return [list(row) for row in projected.rows()]
