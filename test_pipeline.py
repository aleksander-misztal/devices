"""
Kompleksowe testy pipeline'u. Uruchomienie:
    .venv/bin/python test_pipeline.py
Wynik zapisywany do: test_results.md
"""
import json
import uuid
from datetime import datetime
from pathlib import Path

from graph import run, langfuse

SESSION_ID = str(uuid.uuid4())
OUTPUT = Path("test_results.md")

TESTS = [
    # ── Name search: konkretne modele ─────────────────────────────────────
    ("name: konkretny model",           "Samsung Galaxy S24 Ultra"),
    ("name: konkretny model",           "MacBook Air M3"),
    ("name: konkretny model",           "Apple Watch Series 9"),
    ("name: konkretny model",           "Garmin Fenix 7"),
    ("name: konkretny model",           "etui do iPhone 15 Pro"),
    ("name: porównanie dwóch",          "MacBook Air M3 czy Dell XPS 15 - które lepsze?"),
    ("name: slang/skrót",               "ip15p etui"),
    ("name: slang/skrót",               "s24u"),
    ("name: literówka",                 "Samsng Galaxy S24"),
    ("name: niepełna nazwa",            "Galaxy Watch Ultra"),

    # ── Filter search: brand + category ──────────────────────────────────
    ("filter: brand+category",          "zegarki Samsung"),
    ("filter: brand+category",          "telefony Apple"),
    ("filter: brand+category",          "laptopy Dell"),
    ("filter: brand+category",          "smartwatche Garmin"),

    # ── Filter search: sort + limit ───────────────────────────────────────
    ("filter: sort+limit najtańszy",    "najtańszy zegarek Samsung"),
    ("filter: sort+limit top3",         "top 3 najtańsze zegarki Samsung"),
    ("filter: sort desc",               "który Garmin ma najdłuższy czas pracy na baterii?"),
    ("filter: sort+limit najdroższy",   "najdroższy telefon Apple"),
    ("filter: sort+limit top5",         "5 laptopów z największą baterią wh"),

    # ── Filter search: parametry techniczne ──────────────────────────────
    ("filter: exact RAM",               "laptopy z 32GB RAM"),
    ("filter: min RAM",                 "laptop z co najmniej 32GB RAM"),
    ("filter: OLED + RAM",              "laptop OLED z 32GB RAM"),
    ("filter: 5G + cena max",           "telefon z 5G do 2000 zł"),
    ("filter: bateria min",             "telefon z baterią powyżej 5000mAh"),
    ("filter: GPS + cena max",          "zegarek z GPS do 1500 zł"),
    ("filter: cena max",                "laptop do 4000 zł"),
    ("filter: screen type",             "telefon z ekranem AMOLED"),

    # ── Zapytania ogólne / bez kryterium ─────────────────────────────────
    ("ogólne: brak kryterium",          "który samsung jest najlepszy?"),
    ("ogólne: brak kryterium",          "polecasz coś do gier?"),
    ("ogólne: brak kryterium",          "jaki telefon kupić?"),

    # ── Edge cases ────────────────────────────────────────────────────────
    ("edge: niezwiązane",               "kiedy przyjdzie paczka?"),
    ("edge: niezwiązane",               "jaka jest pogoda w Warszawie?"),
    ("edge: greeting",                  "hej"),
    ("edge: język angielski",           "cheapest Samsung watch"),
    ("edge: mieszany PL/EN",            "samsung galaxy best price"),
    ("edge: brak konkretów",            "coś fajnego"),
    ("edge: bardzo długie + szum",
        "hej no wiesz szukam czegoś do ogarniania swojego zdrowia, "
        "może zegarek albo opaska, coś z GPS bo chodzę na trekkingi, "
        "i żeby bateria wystarczyła na kilka dni, budżet mam około 1200 zł, "
        "najlepiej żeby miał pomiar pulsu, no i żeby nie ważył za dużo"),
]


def run_test(label: str, question: str) -> dict:
    result = run(question, session_id=SESSION_ID)
    return {
        "label": label,
        "question": question,
        "mode": result.get("mode", "?"),
        "devices": result.get("devices", []),
        "response": result.get("response") or "",
    }


def write_results(results: list[dict]) -> None:
    lines = [
        f"# Test results",
        f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Session:** `{SESSION_ID}`  ",
        f"**Łącznie:** {len(results)} testów",
        "",
    ]

    current_label = None
    for r in results:
        # Section header when label changes
        section = r["label"].split(":")[0].strip()
        if section != current_label:
            current_label = section
            lines += ["---", f"## {section}", ""]

        mode_tag = f"`{r['mode']}`"
        dev_count = f"**{len(r['devices'])} urządzeń**"
        lines += [
            f"### {r['label']} — _{r['question']}_",
            f"{mode_tag} · {dev_count}",
            "",
            r["response"].strip(),
            "",
        ]

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Zapisano → {OUTPUT}")


if __name__ == "__main__":
    results = []
    for i, (label, question) in enumerate(TESTS, 1):
        print(f"[{i:02d}/{len(TESTS)}] {question[:60]}")
        try:
            results.append(run_test(label, question))
        except Exception as e:
            results.append({
                "label": label,
                "question": question,
                "mode": "ERROR",
                "devices": [],
                "response": f"❌ {e}",
            })

    langfuse.flush()
    write_results(results)
