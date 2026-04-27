h1. Ekstrakcja danych z pytania

Po wykryciu intencji pipeline startuje od węzła {{extract}}. Jego wynik uruchamia dwie równoległe gałęzie: {{name_search}} (szukanie po nazwie) i {{extract_specs}} który zasila {{filter_search}} (szukanie po filtrach). Oba węzły opisane są poniżej.

----

h2. Węzeł 1: extract

Wyciąga z pytania konkretne urządzenia wymienione przez użytkownika.

h3. Wejście

*question*
Surowe pytanie użytkownika (string).
{code}
"co jest lepsze: MacBook Air M3 czy Dell XPS 15?"
{code}

h3. Logika

{code:python}
response = client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=[
        {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
        {"role": "user", "content": state["question"]},
    ],
    response_format={"type": "json_object"},
    temperature=0,
)
result = json.loads(response.choices[0].message.content)
return {"extracted_devices": result.get("devices", [])}
{code}

LLM dostaje pytanie i zwraca listę urządzeń. Dla każdego urządzenia wyciąga:
* *brand* — marka, ale *tylko* gdy użytkownik napisał dosłownie nazwę producenta ("Samsung Galaxy S24" → brand: "Samsung", "MacBook Air M3" → brand: null bo słowo "Apple" nie padło)
* *model* — pełna nazwa produktu po korekcie literówek i odmiany
* *type* — kategoria: "phone", "laptop", "watch", "etui" lub null

Jeśli pytanie jest ogólne i nie zawiera konkretnego modelu ("zegarki Samsung", "najtańszy laptop"), LLM zwraca pustą listę.

h3. Wyjście

*devices_extracted_from_query*
{code:json}
[
  {"brand": null,   "model": "MacBook Air M3", "type": "laptop"},
  {"brand": "Dell", "model": "XPS 15",         "type": "laptop"}
]
{code}

Pusta lista gdy pytanie nie zawiera konkretnych urządzeń:
{code:json}
[]
{code}

----

h2. Węzeł 2: extract_specs

Działa równolegle z {{name_search}}. Wyciąga z pytania parametry techniczne i preferencje sortowania — zasila {{filter_search}}.

h3. Wejście

*question*
To samo pytanie użytkownika (string).

h3. Logika

{code:python}
response = client.chat.completions.create(
    model=OPENAI_MODEL,
    messages=[
        {"role": "system", "content": EXTRACT_SPECS_PROMPT},
        {"role": "user", "content": state["question"]},
    ],
    response_format={"type": "json_object"},
    temperature=0,
)
specs = json.loads(response.choices[0].message.content)
filters = {"brand": specs.get("brand"), "category": specs.get("category")}
return {"specs": specs, "filters": filters}
{code}

LLM wyciąga wszystkie parametry techniczne z pytania. Pola których użytkownik nie wymienił zwracane są jako null. Rozróżnia wartości dokładne od minimalnych:
* "laptop z 16GB RAM" → {{ram_gb: 16}} (exact match)
* "laptop z minimum 16GB RAM" → {{ram_min_gb: 16}} (filtr >= )

Osobno buduje słownik {{filters}} z samym brand i category — używany downstream do zawężenia puli urządzeń przed filtrowaniem.

h3. Wyjście

*specs_extracted_from_query*
{code:json}
{
  "category": "phone",
  "brand": "Samsung",
  "price_max_pln": 3000,
  "battery_min_mah": 5000,
  "camera_min_mpx": null,
  "ram_min_gb": 8,
  "ram_gb": null,
  "storage_min_gb": null,
  "storage_gb": null,
  "screen_min_inch": null,
  "screen_type": null,
  "refresh_rate_min_hz": null,
  "connectivity_5g": true,
  "has_charger_in_box": null,
  "gps": null,
  "sort_by": "price_pln",
  "sort_order": "asc",
  "limit": 1
}
{code}

*filters*
{code:json}
{"brand": "Samsung", "category": "phone"}
{code}
