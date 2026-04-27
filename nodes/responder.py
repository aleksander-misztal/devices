import json
from pathlib import Path

from langfuse import get_client
from openai import OpenAI

from prompts.responder import RESPONDER_HEAVY_PROMPT, RESPONDER_NORMAL_PROMPT
from settings import OPENAI_API_KEY, OPENAI_MODEL
from state import State

client = OpenAI(api_key=OPENAI_API_KEY)
langfuse = get_client()

VDB_DIR = Path("data/vdb")


def _fetch(clipper_ids: list[str]) -> list[dict]:
    docs = []
    for cid in clipper_ids:
        path = VDB_DIR / f"{cid}.json"
        if path.exists():
            docs.append(json.loads(path.read_text(encoding="utf-8")))
    return docs


def node_responder_normal(state: State) -> dict:
    with langfuse.start_as_current_observation(name="responder_normal", as_type="generation") as obs:
        docs = _fetch(state["devices"])
        user_message = json.dumps({
            "question": state["question"],
            "devices": docs,
        }, ensure_ascii=False)

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": RESPONDER_NORMAL_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
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
    return {"response": content, "mode": "normal"}


def node_responder_heavy(state: State) -> dict:
    with langfuse.start_as_current_observation(name="responder_heavy", as_type="generation") as obs:
        card_devices = state.get("devices", [])
        specs = state.get("specs") or {}
        context = {k: v for k, v in specs.items() if v is not None and k not in ("limit",)}
        user_message = json.dumps({
            "question": state["question"],
            "total_found": len(card_devices),
            "filters": context,
        }, ensure_ascii=False)

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": RESPONDER_HEAVY_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
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
    return {"response": content, "mode": "heavy", "card_devices": card_devices}
