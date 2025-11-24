from __future__ import annotations

from pathlib import Path
from typing import List, Dict

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .services import build_export_tsv, build_export_json


SUPPORTED_TYPES = {
    "metabolomics": {
        "label": "Metabolomics",
        "default_facets": ["pathogen", "matrix", "instrument", "country", "year"],
    },
}

# Root where the PVC is mounted in the web container
PVC_ROOT = Path("/datasets")


def homepage_jump(request):
    return redirect("pages_portal_data:data_type_list", datatype="metabolomics")


# -------------------------------------------------------------------
# Helpers to read real data from the PVC
# -------------------------------------------------------------------


def _iter_study_dirs(datatype: str) -> List[Path]:
    """
    Yield directories that look like MetaboLights studies.

    With your current layout this will hit:
        /datasets/MTBLS1051
        /datasets/MTBLS1464
        ...
    """
    if datatype != "metabolomics":
        return []

    if not PVC_ROOT.exists():
        return []

    candidates: Dict[str, Path] = {}
    for p in PVC_ROOT.iterdir():
        if not p.is_dir():
            continue
        name = p.name
        if not name.startswith("MTBLS"):
            continue
        # Only accept IDs like MTBLS1234, MTBLS690, etc.
        suffix = name[5:]
        if not suffix.isdigit():
            continue
        candidates[name] = p

    return [candidates[name] for name in sorted(candidates)]


def _load_all_items(datatype: str) -> List[dict]:
    items: List[dict] = []

    for study_dir in _iter_study_dirs(datatype):
        acc = study_dir.name  # e.g. "MTBLS2017"

        # TODO: later parse real ISA-Tab metadata here
        title = acc
        pathogen = ""
        matrix = ""
        instrument = ""
        country = ""
        year = None

        repo_url = f"https://www.ebi.ac.uk/metabolights/{acc}"

        items.append(
            {
                "id": acc,
                "title": title,
                "pathogen": pathogen,
                "matrix": matrix,
                "instrument": instrument,
                "country": country,
                "year": year,
                "repository": "MetaboLights",
                "repo_url": repo_url,
                "local_path": study_dir,
            }
        )

    return items


def _apply_search_and_filters(
    items: List[dict],
    query: str,
    filters: Dict[str, List[str]],
) -> List[dict]:
    # Text search
    if query:
        q = query.lower()
        items = [
            it
            for it in items
            if q in str(it.get("title", "")).lower()
            or q in str(it.get("id", "")).lower()
        ]

    # Facet filters
    for field, values in filters.items():
        if not values:
            continue
        values_set = {str(v) for v in values}
        items = [
            it
            for it in items
            if it.get(field) is not None and str(it.get(field)) in values_set
        ]

    return items


def _build_facets(items: List[dict], facet_names: List[str]) -> Dict[str, List[dict]]:
    facets: Dict[str, List[dict]] = {}
    items = list(items)

    for facet in facet_names:
        counts: Dict[str, int] = {}
        for it in items:
            value = it.get(facet)
            if value in (None, "", [], {}):
                continue
            key = str(value)
            counts[key] = counts.get(key, 0) + 1

        facets[facet] = [
            {"value": value, "count": count}
            for value, count in sorted(counts.items(), key=lambda kv: kv[0])
        ]

    return facets


# -------------------------------------------------------------------
# Views
# -------------------------------------------------------------------


class DataTypeListView(TemplateView):
    template_name = "portal_data/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        datatype = kwargs["datatype"]

        if datatype not in SUPPORTED_TYPES:
            ctx["error"] = f"Unknown data type: {datatype}"
            return ctx

        q = self.request.GET.get("q", "").strip()
        page = max(int(self.request.GET.get("page", "1")), 1)
        size = max(int(self.request.GET.get("size", "25")), 1)
        facet_names = (
            self.request.GET.getlist("facet")
            or SUPPORTED_TYPES[datatype]["default_facets"]
        )

        filter_fields = ["pathogen", "matrix", "instrument", "country", "year", "repository"]
        filters = {f: self.request.GET.getlist(f) for f in filter_fields if self.request.GET.get(f)}

        # Load from PVC
        all_items = _load_all_items(datatype)

        # Build facets from full set
        facets = _build_facets(all_items, facet_names)

        # Apply filters + search
        filtered_items = _apply_search_and_filters(all_items, q, filters)

        # Simple paging
        start = (page - 1) * size
        end = start + size
        page_items = filtered_items[start:end]

        ctx.update(
            {
                "datatype": datatype,
                "datatype_label": SUPPORTED_TYPES[datatype]["label"],
                "query": q,
                "filters": filters,
                "facets": facets,
                "items": page_items,
                "total": len(filtered_items),
                "page": page,
                "size": size,
            }
        )
        return ctx


def export_selected(request, datatype):
    if datatype not in SUPPORTED_TYPES:
        return HttpResponseBadRequest("Unknown data type")

    fmt = request.GET.get("format", "tsv")
    ids = request.GET.getlist("ids")

    if not ids:
        return HttpResponseBadRequest("No IDs selected")

    all_items = _load_all_items(datatype)
    items = [it for it in all_items if it["id"] in ids]

    if fmt == "json":
        content, filename, ctype = build_export_json(items, f"{datatype}_selection.json")
    else:
        content, filename, ctype = build_export_tsv(items, f"{datatype}_selection.tsv")

    resp = HttpResponse(content, content_type=ctype)
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp

