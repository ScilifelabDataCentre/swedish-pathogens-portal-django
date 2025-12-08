from __future__ import annotations
import re
import os
import shutil
import tempfile
import mimetypes

from pathlib import Path
from urllib.parse import unquote
from typing import List, Dict

from django.conf import settings
from django.http import Http404, FileResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from .services import build_export_tsv, build_export_json


SUPPORTED_TYPES = {
    "metabolomics": {
        "label": "Metabolomics",
        "default_facets": ["pathogen", "instrument", "country", "year"],
    },
}

# Root where the PVC is mounted in the web container
DATA_ROOT: Path = Path(
    getattr(settings, "PORTAL_DATA_ROOT", "/datasets")
).resolve()

ACCESSION_RE = re.compile(r"^MTBLS\d+$")


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

    if not DATA_ROOT.exists():
        return []

    candidates: Dict[str, Path] = {}
    for p in DATA_ROOT.iterdir():
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


def _load_all_items(datatype: str) -> list[dict]:
    """
    Load all public metabolomics datasets from the PVC.

    Each item dict keeps the old keys (id, repository, repo_url, etc.)
    so facets/export keep working, but now also has richer metadata.
    """
    if datatype != "metabolomics":
        return []

    if not DATA_ROOT.is_dir():
        return []

    items: list[dict] = []

    for study_dir in sorted(DATA_ROOT.iterdir(), key=lambda p: p.name):
        if not study_dir.is_dir():
            continue

        accession = study_dir.name
        if not ACCESSION_RE.match(accession):
            # Skip helper dirs like MTBLS_data, fetch_metabolights.sh, targets.txt
            continue

        inv_path = _find_investigation_file(study_dir)
        meta = _parse_investigation_file(inv_path)

        title = meta.get("study_title") or accession
        description = meta.get("study_description") or ""
        public_release = meta.get("study_public_release_date")
        year = None
        if isinstance(public_release, str) and len(public_release) >= 4:
            year = public_release[:4]

        item = {
            # IDs used by bulk selection / export
            "id": accession,
            "accession": accession,

            # Old fields the template already uses
            "title": title,
            "pathogen": "",        # not available in ISA; left empty for now
            "matrix": "",
            "instrument": "",
            "country": "",
            "year": year,
            "repository": "MetaboLights",
            "repo_accession": accession,
            "repo_url": f"https://www.ebi.ac.uk/metabolights/{accession}",

            # New metadata from i_Investigation.txt
            "description": description,
            "public_release_date": public_release,
            "submission_date": meta.get("study_submission_date"),
            "license": meta.get("license"),
            "factors": meta.get("factors", []),
            "design_types": meta.get("design_types", []),
            "platforms": meta.get("platforms", []),
            "publication_title": meta.get("publication_title"),
            "publication_doi": meta.get("publication_doi"),
            "publication_authors": meta.get("publication_authors"),

            # Local PVC location (useful for debugging or later features)
            "local_path": str(study_dir),
        }

        items.append(item)

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

        buckets = list(counts.items())

        # For the "year" facet prefer numeric descending (most recent first),
        # but only if all keys look like integers; otherwise fall back to
        # string-based descending sort. All other facets are sorted ascending.
        if facet == "year" and buckets:
            def _is_integer_string(s: str) -> bool:
                # match optional leading minus and digits (covers negative years if any)
                return re.fullmatch(r"-?\d+", s) is not None

            if all(_is_integer_string(k) for k, _ in buckets):
                buckets.sort(key=lambda kv: int(kv[0]), reverse=True)
            else:
                buckets.sort(key=lambda kv: kv[0], reverse=True)
        else:
            buckets.sort(key=lambda kv: kv[0])

        facets[facet] = [{"value": value, "count": count} for value, count in buckets]

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


def download_study(request, datatype: str, accession: str):
    """
    Stream a zip of the local MetaboLights study directory from the PVC.
    """
    if datatype not in SUPPORTED_TYPES:
        raise Http404("Unknown data type")

    if not ACCESSION_RE.match(accession):
        raise Http404("Invalid accession")

    study_dir = DATA_ROOT / accession
    if not study_dir.is_dir():
        raise Http404("Study not found on this node")

    # Create the archive inside the PVC so we don't touch the read‑only root FS
    tmpdir = tempfile.mkdtemp(dir=str(DATA_ROOT))
    archive_base = os.path.join(tmpdir, accession)
    archive_path = shutil.make_archive(
        base_name=archive_base,
        format="zip",
        root_dir=str(study_dir),
    )

    f = open(archive_path, "rb")
    response = FileResponse(
        f,
        as_attachment=True,
        filename=f"{accession}.zip",
    )

    # Clean up the temp archive when the response is closed
    original_close = response.close

    def cleanup_close(*args, **kwargs):
        try:
            original_close(*args, **kwargs)
        finally:
            try:
                f.close()
            except Exception:
                pass
            try:
                os.remove(archive_path)
            except OSError:
                pass
            try:
                os.rmdir(tmpdir)
            except OSError:
                # Directory may not be empty or already gone; ignore
                pass

    response.close = cleanup_close
    return response


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


def _find_investigation_file(study_dir: Path) -> Path | None:
    """
    Prefer the latest file under METADATA_REVISIONS, fall back to top-level.
    """
    rev_root = study_dir / "METADATA_REVISIONS"
    if rev_root.is_dir():
        rev_dirs = sorted(
            [p for p in rev_root.iterdir() if p.is_dir()],
            key=lambda p: p.name,
        )
        for rev_dir in reversed(rev_dirs):
            candidate = rev_dir / "i_Investigation.txt"
            if candidate.is_file():
                return candidate

    candidate = study_dir / "i_Investigation.txt"
    if candidate.is_file():
        return candidate

    return None


def _parse_investigation_file(path: Path) -> dict:
    """
    Very simple ISA-tab parser focusing on the STUDY rows we care about.
    """
    meta: dict[str, object] = {}

    if path is None or not path.is_file():
        return meta

    try:
        with path.open(encoding="utf-8") as f:
            for raw in f:
                line = raw.rstrip("\n")
                if not line or "\t" not in line:
                    continue

                cols = [c.strip() for c in line.split("\t")]
                key = cols[0]
                values = [c for c in cols[1:] if c]

                if not values:
                    continue

                if key == "Study Title":
                    meta["study_title"] = values[0]
                elif key == "Study Description":
                    meta["study_description"] = values[0]
                elif key == "Study Submission Date":
                    meta["study_submission_date"] = values[0]
                elif key == "Study Public Release Date":
                    meta["study_public_release_date"] = values[0]
                elif key == "Comment[License]":
                    meta["license"] = values[0]
                elif key == "Study Publication Title":
                    meta["publication_title"] = values[0]
                elif key == "Study Publication DOI":
                    meta["publication_doi"] = values[0]
                elif key == "Study Publication Author List":
                    meta["publication_authors"] = values[0]
                elif key == "Study Factor Name":
                    meta["factors"] = values
                elif key == "Study Design Type":
                    meta["design_types"] = values
                elif key == "Study Assay Technology Platform":
                    meta["platforms"] = values
    except FileNotFoundError:
        pass

    return meta


#---- Download helper functions ---------------------------------------------------

def _list_study_files(study_dir: Path) -> List[dict]:
    """
    Walk the study_dir and return a list of files with their relative paths,
    sizes and mtime. Directories are not returned, only files.
    Robust to permission errors and skips files that can't be stat'ed.
    """
    files: List[dict] = []
    try:
        for root, _, filenames in os.walk(study_dir):
            for fn in filenames:
                full = Path(root) / fn
                try:
                    # produce a relative path with forward slashes
                    rel = str(full.relative_to(study_dir)).replace(os.sep, "/")
                    stat = full.stat()
                except (OSError, ValueError):
                    # skip files we can't access or relativize
                    logger.debug("Skipping file during listing: %s", full, exc_info=True)
                    continue

                files.append(
                    {
                        "relpath": rel,
                        "name": fn,
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                    }
                )
    except Exception:
        logger.exception("Error walking study_dir %s", study_dir)
    # sort by path for stable listing
    files.sort(key=lambda f: f["relpath"])
    return files


def study_files(request, datatype: str, accession: str):
    """
    Render a simple file browser for a study directory on the PVC.
    Logs helpful debugging info if something goes wrong.
    """
    if datatype not in SUPPORTED_TYPES:
        raise Http404("Unknown data type")

    if not ACCESSION_RE.match(accession):
        raise Http404("Invalid accession")

    # Ensure DATA_ROOT exists on the cluster
    if not DATA_ROOT.is_dir():
        logger.error("DATA_ROOT does not exist or is not a directory: %s", DATA_ROOT)
        raise Http404("Study storage not available")

    study_dir = DATA_ROOT / accession
    if not study_dir.is_dir():
        logger.warning("Study directory not present: %s", study_dir)
        raise Http404("Study not found on this node")

    try:
        files = _list_study_files(study_dir)
    except Exception:
        logger.exception("Unexpected error listing files for %s/%s", datatype, accession)
        raise Http404("Could not list files")

    return render(
        request,
        "portal_data/study_files.html",
        {
            "datatype": datatype,
            "accession": accession,
            "files": files,
        },
    )


def download_study_file(request, datatype: str, accession: str, relpath: str):
    """
    Stream a single file from the study directory. Protect against path traversal
    by resolving and ensuring the requested path is inside the study directory.
    This implementation is defensive and logs errors to help diagnose cluster 500s.
    """
    if datatype not in SUPPORTED_TYPES:
        raise Http404("Unknown data type")

    if not ACCESSION_RE.match(accession):
        raise Http404("Invalid accession")

    # relpath may be URL-encoded in the URL; decode it once
    relpath = unquote(relpath)

    # Basic sanity: no absolute paths allowed
    if os.path.isabs(relpath):
        logger.warning("Rejecting absolute relpath request: %s", relpath)
        raise Http404("Invalid file path")

    # Ensure DATA_ROOT exists
    if not DATA_ROOT.is_dir():
        logger.error("DATA_ROOT not available: %s", DATA_ROOT)
        raise Http404("Study storage not available")

    study_dir = DATA_ROOT / accession
    if not study_dir.is_dir():
        logger.warning("Study directory missing for download: %s", study_dir)
        raise Http404("Study not found on this node")

    try:
        # Use resolve(strict=False) to avoid raising for strange mount points; then check containment
        candidate = (study_dir / relpath).resolve(strict=False)
        study_dir_resolved = study_dir.resolve(strict=False)
    except Exception:
        # If resolving fails for some reason, log and abort
        logger.exception("Path resolution failed for %s %s", study_dir, relpath)
        raise Http404("Invalid file path")

    # Ensure the requested file is under the study dir using commonpath
    try:
        # os.path.commonpath raises ValueError on different drives; catch that
        common = os.path.commonpath([str(study_dir_resolved), str(candidate)])
        if common != str(study_dir_resolved):
            logger.warning(
                "Path traversal or invalid path detected. study_dir=%s candidate=%s common=%s",
                study_dir_resolved,
                candidate,
                common,
            )
            raise Http404("Invalid file path")
    except ValueError:
        logger.exception(
            "Could not determine commonpath for study_dir=%s candidate=%s",
            study_dir_resolved,
            candidate,
        )
        raise Http404("Invalid file path")

    if not candidate.exists() or not candidate.is_file():
        logger.warning("Requested file not found or not a file: %s", candidate)
        raise Http404("File not found")

    # Determine content type
    content_type, _ = mimetypes.guess_type(str(candidate))
    if content_type is None:
        content_type = "application/octet-stream"

    try:
        f = open(candidate, "rb")
    except Exception:
        logger.exception("Failed to open file for streaming: %s", candidate)
        # Return 404 rather than 500 to avoid leaking details to users, but log the exception
        raise Http404("File not accessible")

    response = FileResponse(f, as_attachment=True, filename=candidate.name, content_type=content_type)

    # Ensure file closed when response is closed
    original_close = response.close

    def cleanup_close(*args, **kwargs):
        try:
            original_close(*args, **kwargs)
        finally:
            try:
                f.close()
            except Exception:
                logger.debug("Failed to close file handle for %s", candidate, exc_info=True)

    response.close = cleanup_close
    return response
# ---------------------------------------------------------------------------
