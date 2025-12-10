"""Views for the multi-disease serology dashboard.

This module defines the `MultiDiseaseSerology` view which renders a dashboard
by fetching two Excel files from blobserver, parsing them server-side, and
exposing normalised table data to the template.
"""

from __future__ import annotations

import logging
from io import BytesIO
from typing import Any
from urllib.request import Request, urlopen

import polars as pl
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

KTH_XLSX_URL = "https://blobserver.dc.scilifelab.se/blob/KTH-produced-antigens.xlsx"
EXTERNAL_XLSX_URL = "https://blobserver.dc.scilifelab.se/blob/External-PLP-proteinlist.xlsx"
REQUEST_TIMEOUT_SECONDS = 10
USER_AGENT = "pathogens-portal/multidisease-serology"

# Explicit column orders for deterministic display
KTH_HEADERS: list[str] = ["Virus type", "Variant", "Protein", "Details", "Host"]
EXTERNAL_HEADERS: list[str] = ["Pathogen", "Variant", "Protein", "Details", "Host"]

logger = logging.getLogger(__name__)


class MultiDiseaseSerology(View):
    """Render the multidisease serology dashboard.

    The view performs three lightweight steps on every request: download the two
    XLSX blobs, parse the first worksheet of each with Polars, and normalise the
    tables into ordered rows so the template can render simple loops.

    Attributes:
        template_name: Template that renders the descriptive copy and tables.
        title: Page title that appears in the shared layout.

    """

    template_name = "dashboards/multidisease_serology.html"
    title = "Multi-disease serology"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Render the dashboard template with the computed serology context."""
        context = self._build_context()
        return render(request, self.template_name, context)

    def _build_context(self) -> dict[str, Any]:
        """Build template context with normalised serology tables."""
        kth_rows_aligned = self._load_rows(KTH_XLSX_URL, KTH_HEADERS, "kth")
        external_rows_aligned = self._load_rows(EXTERNAL_XLSX_URL, EXTERNAL_HEADERS, "external")

        logger.debug(
            "serology_context_built",
            extra={
                "kth_rows": len(kth_rows_aligned),
                "external_rows": len(external_rows_aligned),
                "kth_headers": len(KTH_HEADERS),
                "external_headers": len(EXTERNAL_HEADERS),
            },
        )
        return {
            "title": self.title,
            "kth_headers": KTH_HEADERS,
            "kth_rows": kth_rows_aligned,
            "external_headers": EXTERNAL_HEADERS,
            "external_rows": external_rows_aligned,
        }

    def _load_rows(self, url: str, headers: list[str], source: str) -> list[list[Any]]:
        """Helper to fetch, parse, and normalise table data."""
        try:
            logger.info("serology_fetch_start", extra={"source": source, "url": url})
            frame = self._read_excel_frame(url)
            logger.info("serology_fetch_success", extra={"source": source, "records": frame.height})
        except Exception:
            logger.exception("serology_fetch_failed", extra={"source": source, "url": url})
            return []
        return self._frame_to_rows(frame, headers)

    def _read_excel_frame(self, url: str) -> pl.DataFrame:
        """Fetch an Excel sheet using urllib and parse it with Polars."""
        request = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
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
