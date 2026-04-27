from typing import TypedDict


class State(TypedDict):
    question: str
    extracted_devices: list[dict]
    candidates: list[dict]
    specs: dict
    filters: dict
    filter_devices: list[str]
    devices: list[str]
    card_devices: list[str]
    mode: str
    response: str
