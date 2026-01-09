from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from .services import query_data_backend, build_export_tsv, build_export_json

SUPPORTED_TYPES = {
    "metabolomics": {
        "label": "Metabolomics",
        "default_facets": ["pathogen", "matrix", "instrument", "country", "year"],
    },
    # Future: "proteomics": {...}, etc.
}

def homepage_jump(request):
    # For now redirect to metabolomics; later this route can show a hub
    return redirect("pages_portal_data:data_type_list", datatype="metabolomics")

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
        facets = self.request.GET.getlist("facet") or SUPPORTED_TYPES[datatype]["default_facets"]

        filter_fields = ["pathogen","matrix","instrument","country","year","repository"]
        filters = {f: self.request.GET.getlist(f) for f in filter_fields if self.request.GET.get(f)}

        results = query_data_backend(
            datatype=datatype,
            query=q,
            page=page,
            size=size,
            filters=filters,
            facets=facets,
            topic=self.request.GET.get("topic")  # optional: used by Topics widget
        )

        ctx.update({
            "datatype": datatype,
            "datatype_label": SUPPORTED_TYPES[datatype]["label"],
            "query": q,
            "filters": filters,
            "facets": results["facets"],
            "items": results["items"],
            "total": results["total"],
            "page": page,
            "size": size,
        })
        return ctx

def export_selected(request, datatype):
    if datatype not in SUPPORTED_TYPES:
        return HttpResponseBadRequest("Unknown data type")

    ids = request.POST.getlist("ids[]") or request.GET.getlist("ids")
    fmt = (request.GET.get("format") or request.POST.get("format") or "tsv").lower()

    if not ids:
        return HttpResponseBadRequest("No IDs selected")

    payload = query_data_backend(datatype=datatype, ids=ids, page=1, size=len(ids))
    items = payload["items"]

    if fmt == "json":
        content, filename, ctype = build_export_json(items, f"{datatype}_selection.json")
    else:
        content, filename, ctype = build_export_tsv(items, f"{datatype}_selection.tsv")

    resp = HttpResponse(content, content_type=ctype)
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp

