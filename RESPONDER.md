h1. Routing i formatowanie odpowiedzi

Po agregacji pipeline decyduje jak odpowiedzieć na pytanie. Wybór zależy od liczby znalezionych urządzeń. Są dwie ścieżki: normal (do 10 wyników) i heavy (powyżej 10).

----

h2. Wejście ze stanu

*devices_aggregated*
Lista {{clipper_id}} z węzła aggregate.
{code:json}
["abc123", "def456", "ghi789"]
{code}

*specs_extracted_from_query*
Słownik z filtrami i sortowaniem — używany w ścieżce heavy.

*question*
Oryginalne pytanie użytkownika (string).

----

h2. Routing

{code:python}
NORMAL_THRESHOLD = 10

def _route(state: State) -> str:
    devices = state.get("devices", [])
    if len(devices) <= NORMAL_THRESHOLD:
        return "normal"
    return "heavy"
{code}

Jeśli {{devices_aggregated}} zawiera 10 lub mniej ID: ścieżka *normal*.
Jeśli więcej niż 10: ścieżka *heavy*.

----

h2. Ścieżka normal (do 10 wyników)

h3. Logika

{code:python}
docs = _fetch(state["devices"])
user_message = json.dumps({
    "question": state["question"],
    "devices": docs,
})
response = client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=[
        {"role": "system", "content": RESPONDER_NORMAL_PROMPT},
        {"role": "user", "content": user_message},
    ],
    temperature=0.3,
)
return {"response": content, "mode": "normal"}
{code}

Dla każdego ID pobieramy pełny dokument urządzenia z dysku ({{data/vdb/{clipper_id}.json}}). Wszystkie dokumenty razem z pytaniem trafiają do LLM. LLM odpowiada naturalnie: porównuje jeśli pytanie o porównanie, odpowiada konkretnie jeśli pytanie o konkret. Nie wymyśla danych których nie ma w dokumentach, nie ujawnia wewnętrznych identyfikatorów.

h3. Wyjście

*response* — gotowa odpowiedź tekstowa dla użytkownika
*mode* — wartość "normal"

{code:json}
{
  "response": "MacBook Air M3 13\" to lżejsza opcja (1,24 kg) z ceną od 5 999 zł. Dell XPS 15 oferuje większy ekran i mocniejszą kartę graficzną, ale jest cięższy i droższy.",
  "mode": "normal"
}
{code}

----

h2. Ścieżka heavy (powyżej 10 wyników)

h3. Logika

{code:python}
card_devices = state.get("devices", [])
context = {k: v for k, v in specs.items() if v is not None and k not in ("limit",)}
user_message = json.dumps({
    "question": state["question"],
    "total_found": len(card_devices),
    "filters": context,
})
response = client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=[
        {"role": "system", "content": RESPONDER_HEAVY_PROMPT},
        {"role": "user", "content": user_message},
    ],
    temperature=0.3,
)
return {"response": content, "mode": "heavy", "card_devices": card_devices}
{code}

Przy dużej liczbie wyników *nie pobieramy* pełnych dokumentów urządzeń — za dużo tokenów. Do LLM trafia tylko pytanie, liczba znalezionych urządzeń i aktywne filtry (z {{specs}}, z pominięciem {{limit}}). LLM generuje krótkie 1-2 zdaniowe wprowadzenie: co znaleziono, czy lista jest posortowana i jak. Nie wymienia konkretnych modeli. Pełna lista ID trafia do {{card_devices}} — chatbot renderuje je jako karty produktów osobno.

h3. Wyjście

*response* — krótkie wprowadzenie tekstowe (1-2 zdania)
*mode* — wartość "heavy"
*card_devices* — lista {{clipper_id}} do wyrenderowania jako karty produktów

{code:json}
{
  "response": "Znalazłem 21 laptopów z ekranem OLED i 32 GB RAM, posortowanych od najtańszego.",
  "mode": "heavy",
  "card_devices": ["abc123", "def456", "..."]
}
{code}
