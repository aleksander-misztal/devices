import json
import uuid
from pathlib import Path

import streamlit as st

from graph import run, langfuse

VDB_DIR = Path("data/vdb")

st.set_page_config(page_title="Device RAG", page_icon="📱", layout="centered")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []


def _load(cid: str) -> dict:
    p = VDB_DIR / f"{cid}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _render_devices(devices: list[dict]) -> None:
    cols_per_row = 4
    for i in range(0, len(devices), cols_per_row):
        cols = st.columns(cols_per_row)
        for col, doc in zip(cols, devices[i : i + cols_per_row]):
            with col:
                name = doc.get("name", "?")
                with st.popover(name, use_container_width=True):
                    specs = doc.get("specs", {})
                    if specs:
                        st.dataframe(
                            {
                                "Parametr": list(specs.keys()),
                                "Wartość": list(specs.values()),
                            },
                            hide_index=True,
                            use_container_width=True,
                        )
                    text = doc.get("text", "")
                    if text:
                        st.caption(text[:300])


# ── render history ──────────────────────────────────────────────────────────
st.title("Device RAG")
st.caption(f"Session: `{st.session_state.session_id}`")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])
        if msg.get("devices"):
            _render_devices(msg["devices"])

# ── input ────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Pytanie o urządzenie..."):
    st.session_state.messages.append({"role": "user", "text": prompt})

    with st.spinner("Szukam..."):
        result = run(prompt, session_id=st.session_state.session_id)
        langfuse.flush()

    response_text = result.get("response") or "Brak odpowiedzi."
    mode = result.get("mode", "?")

    devices_data = []
    if mode == "heavy":
        for cid in result.get("card_devices", []):
            doc = _load(cid)
            if doc:
                devices_data.append(doc)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "text": response_text,
            "devices": devices_data,
            "mode": mode,
        }
    )
    st.rerun()
