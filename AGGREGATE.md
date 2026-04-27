# Agregacja wyników wyszukiwania

Węzeł `node_aggregate` scala wyniki dwóch równoległych wyszukiwań (name_search i filter_search) w jedną, uporządkowaną listę urządzeń. Jest ostatnim krokiem przed routingiem do respondera.

---

## Wejście ze stanu

**`devices_name_search_results`**
Wynik name_search. Lista obiektów — każdy to jedno urządzenie dopasowane po nazwie.
```json
[
  {"clipper_id": "abc123", "name": "Apple MacBook Air 13 M3", "matched_by": ["fuzzy"]},
  {"clipper_id": "def456", "name": "Apple MacBook Air M1",    "matched_by": ["token_overlap"]}
]
```

**`devices_filter_search_results`**
Wynik filter_search. Lista samych ID urządzeń które przeszły przez filtry specyfikacji (RAM, cena, kategoria itp.).
```json
["ghi789", "jkl012"]
```

**`devices_extracted_from_query`**
Wynik extract: lista urządzeń wyciągniętych z pytania przez LLM. Potrzebna do sprawdzenia czy pytanie dotyczy konkretnego modelu.
```json
[{"brand": "Apple", "model": "MacBook Air M3", "type": "laptop"}]
```

**`specs_extracted_from_query`**
Wynik extract_specs: słownik z filtrami i opcjami sortowania.
```json
{"sort_by": "price_pln", "sort_order": "asc", "limit": 1}
```

**`question`**
Oryginalne pytanie użytkownika (string). Przekazywane do LLM pickera.

---

## Logika krok po kroku

**Krok 1 — Wyciągnięcie obu list ze stanu**

```python
name_ids = [c["clipper_id"] for c in (state.get("candidates") or [])]
filter_ids = state.get("filter_devices") or []
```

Z `candidates` (name_search) bierzemy samo `clipper_id`. Z `filter_devices` (filter_search) mamy już same ID.

---

**Krok 2 — Early return jeśli brak wyników**

```python
all_ids = name_ids + [fid for fid in filter_ids if fid not in set(name_ids)]

if not all_ids:
    return {"devices": []}
```

Robimy tymczasowy union obu list żeby sprawdzić czy cokolwiek znaleziono. Jeśli pusty — zwracamy pustą listę i kończymy.

---

**Krok 3 — Czy pytanie dotyczy konkretnego modelu?**

```python
has_specific_model = any(d.get("model") for d in state.get("extracted_devices") or [])
```

Sprawdzamy czy extract wyciągnął pole `model` z pytania. Jeśli tak: pytanie jest konkretne ("MacBook Air M3"). Jeśli nie: pytanie jest ogólne ("zegarki samsung") i LLM picker jest pomijany.

---

**Krok 4 — Warunek wejścia do LLM pickera**

```python
if name_ids and len(name_ids) <= MAX_CANDIDATES and has_specific_model:
    ...  # kroki 5-6
else:
    final = all_ids  # union z kroku 2 idzie bezpośrednio jako wynik
```

Trzy warunki jednocześnie:
- name_search cokolwiek znalazł
- znalazł maksymalnie 30 kandydatów (`MAX_CANDIDATES` z settings) — powyżej tego progu LLM nie ma sensu
- pytanie dotyczy konkretnego modelu (krok 3)

Jeśli którykolwiek warunek nie jest spełniony, pomijamy LLM. `final` to union z kroku 2: name_ids pierwsze, filter_ids doklejone bez duplikatów.

---

**Krok 5 — LLM picker** *(tylko gdy krok 4 przeszedł)*

```python
candidates_payload = [{"clipper_id": c["clipper_id"], "name": c["name"]} for c in candidates]
user_message = json.dumps({"question": state["question"], "candidates": candidates_payload})

response = client.chat.completions.create(model=OPENAI_MODEL, ...)
content = response.choices[0].message.content
llm_ids = json.loads(content).get("devices", [])
```

Do LLM wysyłane są pytanie użytkownika i lista kandydatów z name_search (samo ID i nazwa, bez speców). LLM odsiewa urządzenia które nie pasują do konkretnej generacji lub wersji.

Przykład: pytanie "MacBook Air M3", name_search zwrócił M3 + M2 + M1 (wspólne tokeny), LLM zostawia tylko M3.

LLM zwraca:
```json
{"devices": ["abc123"]}
```

---

**Krok 6 — Doklejanie filter_ids po pickerze**

```python
if llm_ids and filter_ids:
    llm_categories = {_category(cid) for cid in llm_ids} - {None}
    final = llm_ids + [fid for fid in filter_ids if fid not in seen2 and _category(fid) not in llm_categories]
else:
    final = llm_ids + [fid for fid in filter_ids if fid not in seen2]
```

Do wyniku pickera doklejamy filter_ids których jeszcze nie ma na liście. Zabezpieczenie: jeśli LLM wybrał urządzenia z kategorii "laptop", nie doklejamy innych laptopów z filter_search — filter_search mógł znaleźć 50 laptopów Apple tylko dlatego że marka pasowała, a użytkownik pytał o konkretny model. Doklejamy wyłącznie urządzenia z innych kategorii.

Wyjątek: jeśli LLM nie zwrócił żadnych ID, category guard jest pomijany i wszystkie filter_ids są dołączone.

---

**Krok 7 — Re-sort**

```python
if sort_by and final:
    final.sort(key=_sort_key, reverse=not ascending)
```

Merge z name_search zaburzył kolejność z filter_search. Jeśli `sort_by` jest w specs, sortujemy całą finalną listę od nowa — dla każdego ID czytamy wartość pola z pliku na dysku. Urządzenia bez tej wartości trafiają zawsze na koniec, niezależnie od kierunku sortowania.

---

**Krok 8 — Limit**

```python
if limit and sort_by:
    final = final[:limit]
```

Jeśli specs zawiera `limit`, lista jest ucinana. Limit działa **tylko jeśli jednocześnie jest `sort_by`** — bez sortowania lista jest w nieokreślonej kolejności i ucięcie do 1 zwróciłoby losowe urządzenie.

---

## Wyjście

**`devices_aggregated`**
Lista `clipper_id`, posortowana i przycięta, bez duplikatów.
```json
["abc123", "def456", "ghi789"]
```

Samo ID — bez nazw, speców ani matched_by. Responder na podstawie tych ID pobiera pełne dane urządzeń i generuje odpowiedź.
