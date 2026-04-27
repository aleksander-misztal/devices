import json
import uuid
from contextlib import contextmanager

from langfuse import get_client, observe, propagate_attributes
from langgraph.graph import END, StateGraph

from nodes.aggregate import node_aggregate
from nodes.extract import node_extract
from nodes.extract_specs import node_extract_specs
from nodes.filter_search import node_filter_search
from nodes.name_search import node_name_search
from nodes.responder import node_responder_heavy, node_responder_normal
from state import State

langfuse = get_client()

NORMAL_THRESHOLD = 10


@contextmanager
def _noop():
    yield


def _route(state: State) -> str:
    devices = state.get("devices", [])
    if len(devices) <= NORMAL_THRESHOLD:
        return "normal"
    return "heavy"


def _build_graph():
    g = StateGraph(State)
    g.add_node("extract", node_extract)
    g.add_node("name_search", node_name_search)
    g.add_node("extract_specs", node_extract_specs)
    g.add_node("filter_search", node_filter_search)
    g.add_node("aggregate", node_aggregate)
    g.add_node("responder_normal", node_responder_normal)
    g.add_node("responder_heavy", node_responder_heavy)

    g.set_entry_point("extract")
    g.add_edge("extract", "name_search")
    g.add_edge("extract", "extract_specs")
    g.add_edge("name_search", "aggregate")
    g.add_edge("extract_specs", "filter_search")
    g.add_edge("filter_search", "aggregate")
    g.add_conditional_edges("aggregate", _route, {
        "normal": "responder_normal",
        "heavy": "responder_heavy",
    })
    g.add_edge("responder_normal", END)
    g.add_edge("responder_heavy", END)

    return g.compile()


graph = _build_graph()


def run(question: str, session_id: str | None = None) -> dict:
    with propagate_attributes(session_id=session_id) if session_id else _noop():
        return _run(question)


@observe(name="device_pipeline", as_type="agent")
def _run(question: str) -> dict:
    langfuse.update_current_span(input=question)
    result = graph.invoke({"question": question})
    output = {
        "mode": result.get("mode"),
        "response": result.get("response"),
        "devices": result.get("devices", []),
        "card_devices": result.get("card_devices", []),
        "filters": result.get("filters"),
    }
    langfuse.update_current_span(output=output)
    return output


if __name__ == "__main__":
    from settings import FILTER_QUESTIONS, NAME_QUESTIONS

    sessions = [
        ("name-search", NAME_QUESTIONS),
        ("filter-search", FILTER_QUESTIONS),
    ]

    for session_name, questions in sessions:
        session_id = str(uuid.uuid4())
        print(f"\n{'='*60}")
        print(f"Session: {session_name}  |  {session_id}")
        print(f"{'='*60}\n")

        for q in questions:
            print(f">>> {q}")
            result = run(q, session_id=session_id)
            print(f"  mode: {result['mode']}")
            print(f"  devices: {result['devices']}")
            print(f"  response: {result['response'][:120] if result['response'] else None}")
            print()

    langfuse.flush()
    print("Done.")
