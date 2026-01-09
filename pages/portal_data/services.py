import csv, io, json

def query_data_backend(datatype, query="", page=1, size=25, filters=None, facets=None, topic=None, ids=None):
    """
    Returns:
      {
        "items": [
          {id, title, pathogen, matrix, instrument, country, year, repository, repo_url, files:[{name,url}]},
          ...
        ],
        "total": int,
        "facets": { "pathogen": [{"value": "...", "count": n}, ...], ... }
      }
    """
    filters = filters or {}
    facets  = facets or []

    # TODO: Replace mock data with real upstream API calls (Pathogens Portal / EMBL).
    mock_items = [
        {
          "id": "MTBLS1234",
          "title": "Serum metabolomics of Orthoflavivirus denguei infection",
          "pathogen": "Orthoflavivirus denguei",
          "matrix": "serum",
          "instrument": "Orbitrap",
          "country": "Sweden",
          "year": 2024,
          "repository": "MetaboLights",
          "repo_url": "https://www.ebi.ac.uk/metabolights/MTBLS1234",
          "files": [{"name": "metadata.tsv", "url": "https://..."}, {"name": "peak_table.tsv", "url": "https://..."}],
        },
        # ...more from API...
    ]

    if ids:
        idset = set(ids)
        mock_items = [x for x in mock_items if x["id"] in idset]

    def include(x):
        if query and (query.lower() not in json.dumps(x).lower()):
            return False
        for k, vals in (filters or {}).items():
            if vals and str(x.get(k)) not in set(map(str, vals)):
                return False
        if topic and topic.lower() not in json.dumps(x).lower():
            return False
        return True

    filtered = [x for x in mock_items if include(x)]
    total = len(filtered)

    start = (page - 1) * size
    end   = start + size
    items = filtered[start:end]

    facet_data = {}
    for f in facets:
        buckets = {}
        for it in filtered:
            key = it.get(f) or "Unknown"
            buckets[key] = buckets.get(key, 0) + 1
        facet_data[f] = sorted(
            [{"value": k, "count": v} for k, v in buckets.items()],
            key=lambda x: (-x["count"], str(x["value"]))
        )

    return {"items": items, "total": total, "facets": facet_data}

def build_export_tsv(items, filename):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=[
        "id","title","pathogen","matrix","instrument","country","year","repository","repo_url"
    ], extrasaction="ignore", delimiter="\t")
    writer.writeheader()
    for it in items:
        writer.writerow(it)
    return buf.getvalue(), filename, "text/tab-separated-values"

def build_export_json(items, filename):
    return json.dumps(items, ensure_ascii=False, indent=2), filename, "application/json"

