import json
import re
import unicodedata

from langfuse import get_client
from rapidfuzz import fuzz

from settings import DEVICES_PATH
from state import State

with open(DEVICES_PATH, encoding="utf-8") as f:
    DEVICES = json.load(f)

langfuse = get_client()

TOKEN_OVERLAP_MIN = 0.6
FUZZY_MIN = 82


def _normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _tokenize(text: str) -> set[str]:
    return set(_normalize(text).split())


def _match_exact(query_norm: str, device_norm: str) -> bool:
    return query_norm == device_norm


def _match_token_overlap(query_tokens: set, device_tokens: set) -> bool:
    if not query_tokens:
        return False
    query_nums = {t for t in query_tokens if t.isdigit()}
    if query_nums and not query_nums.issubset(device_tokens):
        return False
    return len(query_tokens & device_tokens) / len(query_tokens) >= TOKEN_OVERLAP_MIN


def _match_fuzzy(query_norm: str, device_norm: str) -> bool:
    return fuzz.token_sort_ratio(query_norm, device_norm) >= FUZZY_MIN


def _find_candidates(extracted_device: dict, obs) -> list[dict]:
    parts = [p for p in [extracted_device.get("brand"), extracted_device.get("model")] if p]
    if not parts:
        obs.update(input=extracted_device, output={"candidates_count": 0})
        return []

    query = " ".join(parts)
    query_norm = _normalize(query)
    query_tokens = _tokenize(query)

    category = extracted_device.get("type")
    pool = [d for d in DEVICES if d["category"] == category] if category else DEVICES

    seen = {}
    for device in pool:
        device_norm = _normalize(device["name"])
        device_tokens = _tokenize(device["name"])
        matched_by = []

        if _match_exact(query_norm, device_norm):
            matched_by.append("exact")
        if _match_token_overlap(query_tokens, device_tokens):
            matched_by.append("token_overlap")
        if _match_fuzzy(query_norm, device_norm):
            matched_by.append("fuzzy")

        if matched_by:
            cid = device["clipper_id"]
            if cid not in seen:
                seen[cid] = {**device, "matched_by": matched_by}
            else:
                seen[cid]["matched_by"] = list(set(seen[cid]["matched_by"]) | set(matched_by))

    results = list(seen.values())
    obs.update(
        input={"query": query, "category": category},
        output={"candidates_count": len(results)},
    )
    return results


def node_name_search(state: State) -> dict:
    with langfuse.start_as_current_observation(name="name_search", as_type="retriever") as outer:
        seen = {}
        for extracted in state["extracted_devices"]:
            with langfuse.start_as_current_observation(name="search_one", as_type="span") as inner:
                for c in _find_candidates(extracted, inner):
                    cid = c["clipper_id"]
                    if cid not in seen:
                        seen[cid] = c
                    else:
                        seen[cid]["matched_by"] = list(
                            set(seen[cid]["matched_by"]) | set(c["matched_by"])
                        )

        candidates = list(seen.values())
        outer.update(
            input=state["extracted_devices"],
            output={"total_candidates": len(candidates)},
        )
    return {"candidates": candidates}
