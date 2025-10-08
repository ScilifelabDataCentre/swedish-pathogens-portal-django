from __future__ import annotations

from typing import Any, Dict, List

from utils.views import BaseTemplateView
from pages.dashboards.utils.blobserver import fetch_excel_first_sheet_as_records


KTH_XLSX_URL = "https://blobserver.dc.scilifelab.se/blob/KTH-produced-antigens.xlsx"
EXTERNAL_XLSX_URL = "https://blobserver.dc.scilifelab.se/blob/External-PLP-proteinlist.xlsx"

# Explicit column orders for deterministic display
KTH_HEADERS: List[str] = ["Virus type", "Variant", "Protein", "Details", "Host"]
EXTERNAL_HEADERS: List[str] = ["Pathogen", "Variant", "Protein", "Details", "Host"]


class MultiDiseaseSerology(BaseTemplateView):
    """
    Interim dashboard page:
    - Fetch two Excel sheets from blobserver on each request.
    - Parse into records server-side.
    - Normalise into row lists aligned to headers to keep the template simple.
    - No 'last updated' yet (will come from DB later).
    """

    template_name = "dashboards/multidisease_serology.html"
    title = "Multi-disease serology"

    def _normalise_records_to_rows(self, records: List[Dict[str, Any]], headers: List[str]) -> List[List[Any]]:
        """
        Convert a list of record dicts into a list of row lists aligned to the provided headers.
        Missing keys become empty strings to keep rendering safe and consistent.
        """
        normalised_rows: List[List[Any]] = []
        for record in records:
            row: List[Any] = []
            for header in headers:
                row.append(record.get(header, ""))
            normalised_rows.append(row)
        return normalised_rows

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # KTH-produced antigens (server-side parsed)
        try:
            kth_records = fetch_excel_first_sheet_as_records(KTH_XLSX_URL)
        except Exception:
            kth_records = []
        kth_rows_aligned = self._normalise_records_to_rows(kth_records, KTH_HEADERS)

        # Externally produced antigens (server-side parsed)
        try:
            external_records = fetch_excel_first_sheet_as_records(EXTERNAL_XLSX_URL)
        except Exception:
            external_records = []
        external_rows_aligned = self._normalise_records_to_rows(external_records, EXTERNAL_HEADERS)

        context.update(
            {
                "kth_headers": KTH_HEADERS,
                "kth_rows": kth_rows_aligned,
                "external_headers": EXTERNAL_HEADERS,
                "external_rows": external_rows_aligned,
            }
        )
        return context
