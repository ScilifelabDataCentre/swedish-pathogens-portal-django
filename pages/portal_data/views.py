from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .services import build_export_tsv, build_export_json


SUPPORTED_TYPES = {
    "metabolomics": {
        "label": "Metabolomics",
        "default_facets": ["pathogen", "matrix", "instrument", "country", "year"],
    },
    # Future: "proteomics": {...}, etc.
}

# Root on the PVC where MetaboLights studies live
DATA_ROOT: Path = getattr(settings, "PORTAL_DATA_ROOT", Path("/datasets/")


def homepage_jump(request):
    # For now redirect to metabolomics; later this route can show a hub
    return redirect("pages_portal_data:data_type_list", datatype="metabolomics")


# -------------------------------------------------------------------
# Helpers to read real data from the PVC
# -------------------------------------------------------------------

def _load_all_items(datatype: str) -> list[dict]:
    if datatype != "metabolomics":
        return []

    # Prefer /datasets/MTBLS_data if it exists, otherwise /datasets
    root = BASE_DATA_ROOT
    mtbls_data = root / "MTBLS_data"
    if mtbls_data.is_dir():
        root = mtbls_data

    if not root.exists():
        return []

    items: list[dict] = []

    for study_dir in sorted(root.iterdir()):
        if not study_dir.is_dir():
            continue

        acc = study_dir.name  # e.g. "MTBLS2017"

        # Only accept IDs like MTBLS1234
        if not (acc.startswith("MTBLS") and acc[5:].isdigit()):
            continue

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
    items: list[dict],
    query: str,
    filters: dict[str, list[str]],
) -> list[dict]:
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


def _build_facets(items: list[dict], facet_names: list[str]) -> dict[str, list[dict]]:
    """
    Build facet buckets like:
        {
          "country": [{"value": "Sweden", "count": 5}, ...],
          "year": [{"value": "2023", "count": 3}, ...],
        }
    """
    facets: dict[str, list[dict]] = {}
    items = list(items)

    for facet in facet_names:
        counts: dict[str, int] = {}
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

        # Same filter fields as before
        filter_fields = ["pathogen", "matrix", "instrument", "country", "year", "repository"]
        filters = {f: self.request.GET.getlist(f) for f in filter_fields if self.request.GET.get(f)}

        # 1) Load all items from PVC
        all_items = _load_all_items(datatype)

        # 2) Build facets from the full set
        facets = _build_facets(all_items, facet_names)

        # 3) Apply text search & facet filters
        filtered_items = _apply_search_and_filters(all_items, q, filters)

        # Optional paging (simple slice, since we have everything in memory)
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

    # Load all items and keep only the selected IDs
    all_items = _load_all_items(datatype)
    items = [it for it in all_items if it["id"] in ids]

    if fmt == "json":
        content, filename, ctype = build_export_json(items, f"{datatype}_selection.json")
    else:
        content, filename, ctype = build_export_tsv(items, f"{datatype}_selection.tsv")

    resp = HttpResponse(content, content_type=ctype)
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp

