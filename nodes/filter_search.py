import json
from pathlib import Path

from langfuse import get_client

from settings import DEVICES_PATH
from state import State

VDB_DIR = Path("data/vdb")

with open(DEVICES_PATH, encoding="utf-8") as f:
    _ALL_DEVICES = {d["clipper_id"]: d for d in json.load(f)}

langfuse = get_client()

# Maps spec filter keys → vdb spec field + comparison
FILTERS_MAP = {
    "battery_min_mah":    ("battery_mah",       "gte"),
    "camera_min_mpx":     ("camera_mpx",         "gte"),
    "ram_gb":             ("ram_gb",              "eq"),
    "ram_min_gb":         ("ram_gb",              "gte"),
    "storage_gb":         ("storage_gb",          "eq"),
    "storage_min_gb":     ("storage_gb",          "gte"),
    "screen_min_inch":    ("screen_inch",         "gte"),
    "refresh_rate_min_hz":("refresh_rate_hz",     "gte"),
    "battery_min_days":   ("battery_days",        "gte"),
    "price_max_pln":      ("price_pln",           "lte"),
    "screen_type":        ("screen_type",         "eq"),
    "connectivity_5g":    ("connectivity_5g",     "eq"),
    "has_charger_in_box": ("has_charger_in_box",  "eq"),
    "gps":                ("gps",                 "eq"),
}


def _passes(specs: dict, filters: dict) -> bool:
    for filter_key, (spec_field, op) in FILTERS_MAP.items():
        required = filters.get(filter_key)
        if required is None:
            continue
        actual = specs.get(spec_field)
        if actual is None:
            return False
        if op == "gte" and actual < required:
            return False
        if op == "lte" and actual > required:
            return False
        if op == "eq" and actual != required:
            return False
    return True


def node_filter_search(state: State) -> dict:
    specs = state.get("specs") or {}

    with langfuse.start_as_current_observation(name="filter_search", as_type="retriever") as obs:
        category = specs.get("category")
        brand = specs.get("brand")
        sort_by = specs.get("sort_by")
        sort_order = specs.get("sort_order", "desc")

        # Require meaningful filters: brand alone, specific spec filters,
        # or category combined with brand/specs. Category alone is too broad.
        # sort_by alone is not a filter (caused all-1418 bug on unrelated questions).
        has_spec_filters = any(specs.get(k) is not None for k in FILTERS_MAP)
        has_filters = brand or has_spec_filters or (category and (brand or has_spec_filters or sort_by))
        if not has_filters:
            obs.update(input=specs, output={"found": 0, "reason": "no filters"})
            return {"filter_devices": []}

        # Pre-filter by category and brand
        pool = []
        for cid, device in _ALL_DEVICES.items():
            if category and device["category"] != category:
                continue
            path = VDB_DIR / f"{cid}.json"
            if not path.exists():
                continue
            doc = json.loads(path.read_text(encoding="utf-8"))
            if brand and doc.get("brand", "").lower() != brand.lower():
                continue
            pool.append(doc)

        # Filter by specs
        results = [doc for doc in pool if _passes(doc.get("specs", {}), specs)]

        # Sort — nulls always last regardless of direction
        if sort_by and results:
            ascending = sort_order == "asc"
            results.sort(
                key=lambda d: (
                    v := d.get("specs", {}).get(sort_by),
                    float("inf") if v is None and ascending
                    else float("-inf") if v is None
                    else v
                )[-1],
                reverse=not ascending,
            )

        ids = [d["clipper_id"] for d in results]
        obs.update(
            input={"category": category, "brand": brand, "filters": specs, "sort_by": sort_by},
            output={"found": len(ids)},
        )

    return {"filter_devices": ids}
