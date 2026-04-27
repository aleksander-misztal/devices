import json
from pathlib import Path

from langfuse import get_client
from openai import OpenAI

from prompts.aggregate import AGGREGATE_SYSTEM_PROMPT
from settings import MAX_CANDIDATES, OPENAI_API_KEY, OPENAI_MODEL
from state import State

client = OpenAI(api_key=OPENAI_API_KEY)
langfuse = get_client()
VDB_DIR = Path("data/vdb")


def _category(cid: str) -> str | None:
    p = VDB_DIR / f"{cid}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text()).get("category")


def node_aggregate(state: State) -> dict:
    with langfuse.start_as_current_observation(name="aggregate", as_type="generation") as obs:
        # name_search candidates (LLM-verified)
        name_ids = [c["clipper_id"] for c in (state.get("candidates") or [])]
        # filter_search results (spec-filtered, ordered)
        filter_ids = state.get("filter_devices") or []

        # Union preserving order: name_ids first, then filter_ids not already in name_ids
        seen = set(name_ids)
        all_ids = name_ids + [fid for fid in filter_ids if fid not in seen]

        if not all_ids:
            obs.update(input=state["question"], output="no candidates")
            return {"devices": []}

        # Run LLM picker only when user asked for a specific model (not generic brand/category).
        # For generic queries ("zegarki samsung"), filter_search already handles it correctly
        # and the LLM would arbitrarily drop valid candidates.
        extracted = state.get("extracted_devices") or []
        has_specific_model = any(d.get("model") for d in extracted)

        # If name_search had candidates, let LLM pick exact matches from those
        if name_ids and len(name_ids) <= MAX_CANDIDATES and has_specific_model:
            candidates_payload = [
                {"clipper_id": c["clipper_id"], "name": c["name"]}
                for c in (state.get("candidates") or [])
            ]
            user_message = json.dumps({
                "question": state["question"],
                "candidates": candidates_payload,
            }, ensure_ascii=False)

            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": AGGREGATE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            content = response.choices[0].message.content
            obs.update(
                model=OPENAI_MODEL,
                input=user_message,
                output=content,
                usage_details={
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                },
            )
            llm_ids = json.loads(content).get("devices", [])
            # Append filter_ids only if they add devices from a different category.
            # This prevents filter_search (triggered by brand/category in the device name)
            # from flooding name-specific results with all devices of the same brand.
            seen2 = set(llm_ids)
            if llm_ids and filter_ids:
                llm_categories = {_category(cid) for cid in llm_ids} - {None}
                final = llm_ids + [
                    fid for fid in filter_ids
                    if fid not in seen2 and _category(fid) not in llm_categories
                ]
            else:
                final = llm_ids + [fid for fid in filter_ids if fid not in seen2]
        else:
            # Only filter_search results
            obs.update(input=state["question"], output=f"filter_only: {len(all_ids)}")
            final = all_ids

    # Re-apply sort if filter_search had sort_by (name_search merge may have broken order)
    specs = state.get("specs") or {}
    sort_by = specs.get("sort_by")
    sort_order = specs.get("sort_order", "desc")
    ascending = sort_order == "asc"
    if sort_by and final:
        def _sort_key(cid):
            p = VDB_DIR / f"{cid}.json"
            if not p.exists():
                return float("inf") if ascending else float("-inf")
            val = json.loads(p.read_text())["specs"].get(sort_by)
            if val is None:
                return float("inf") if ascending else float("-inf")
            return val
        final.sort(key=_sort_key, reverse=not ascending)

    # Apply limit only when there's a sort criterion — otherwise "limit without sort"
    # would return an arbitrary device (e.g. "najlepszy" without any ranking field).
    limit = specs.get("limit")
    if limit and isinstance(limit, int) and limit > 0 and sort_by:
        final = final[:limit]

    return {"devices": final}
