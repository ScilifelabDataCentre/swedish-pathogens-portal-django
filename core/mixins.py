"""Reusable mixins for Django class-based views."""

from __future__ import annotations

from typing import Any

from django.core.paginator import Paginator
from django.http import HttpRequest


class DataTableMixin:
    """Mixin that extracts table parameters, filters, paginates, and builds template context.

    Class attributes can be overridden per-view to customise defaults:
        table_id:          HTML id prefix used by the template and HTMX targets.
        per_page_default:  Number of rows shown when the user hasn't chosen.
        per_page_options:  Choices offered in the "entries per page" select.
    """

    table_id: str = "data-table"
    per_page_default: int = 10
    per_page_options: list[int] = [10, 25, 50]

    def get_table_context(
        self,
        request: HttpRequest,
        rows: list[list[Any]],
        headers: list[str],
        table_url: str,
        *,
        table_id: str | None = None,
    ) -> dict[str, Any]:
        """Build the context dict that both table templates expect.

        Args:
            request:   The current HTTP request (GET params are read from it).
            rows:      Full dataset as a list-of-lists (one inner list per row).
            headers:   Column header strings, same length as each row.
            table_url: The URL that HTMX controls will call for updates.
            table_id:  Optional override for self.table_id (useful when a
                       single view renders more than one table).

        Returns:
            A dict ready to pass (or nest) into a template context.
        """
        # Allow per-call override so one view can serve multiple tables
        resolved_id = table_id or self.table_id

        # --- Read and sanitise query parameters from the request ----------

        search = request.GET.get("search", "").strip()

        # Fall back to default if the value is missing or not a valid integer
        try:
            per_page = int(request.GET.get("per_page", self.per_page_default))
        except (TypeError, ValueError):
            per_page = self.per_page_default

        # Reject values that aren't in the allowed options
        if per_page not in self.per_page_options:
            per_page = self.per_page_default

        try:
            page_number = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            page_number = 1

        # --- Filter rows by the search term (case-insensitive) ------------

        # Keep a row if any cell contains the search term
        if search:
            term = search.lower()
            rows = [row for row in rows if any(term in str(cell).lower() for cell in row)]

        # --- Paginate the (possibly filtered) rows ------------------------

        paginator = Paginator(rows, per_page)
        page_obj = paginator.get_page(page_number)

        # Build an elided page range for the pagination template.
        # Replace the ELLIPSIS sentinel with None so the template can
        # simply test ``{% if not page_num %}`` for gaps.
        page_range = [
            None if p == Paginator.ELLIPSIS else p
            for p in paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
        ]

        # --- Assemble the template context --------------------------------

        return {
            "table_id": resolved_id,
            "table_url": table_url,
            "headers": headers,
            "page_obj": page_obj,  # Django Page with iterable rows
            "page_range": page_range,  # list of ints and None (ellipsis gaps)
            "search": search,  # echoed back to populate the input
            "per_page": per_page,  # currently active "entries per page"
            "per_page_options": self.per_page_options,
            "total_count": paginator.count,
            "start_index": page_obj.start_index(),  # 1-based first visible row
            "end_index": page_obj.end_index(),  # 1-based last visible row
        }
