# Tasks

## 1. Baza danych (pgvector)

- [ ] Schemat tabeli: `clipper_id`, `brand`, `category`, `price`, `specs` (JSONB), `embedding` (vector)
- [ ] Indeksy na `brand`, `category`, `price`
- [ ] Skrypt inicjalizujący tabelę
- [ ] Populacja z `devices.json` (dane testowe bez speców — same nazwy)
- [ ] Docelowo: mapper Clipper → schemat przy scrapowaniu (poza scope tego grafu)

---

## 2. Session state

- [ ] Struktura: `session_id`, `device_pool`, `history` (ostatnie N turnów)
- [ ] Storage: Redis lub in-memory dict (na start)
- [ ] Zapis poolu po każdym turnie
- [ ] Przekazywanie history do grafu przy każdym wywołaniu `run()`

---

## 3. Node: `intent_classifier`

- [ ] Prompt: dostaje `history` + `question`, zwraca:
  ```json
  {
    "is_followup": bool,
    "pool_action": "reuse | filter | extend | reset"
  }
  ```
- [ ] Jeśli `reset` → czyści pool, fresh start
- [ ] Wchodzi jako pierwszy node przed `extract`

---

## 4. Node: `extract_specs` — rozgałęzienie per kategoria

- [ ] Wykrycie kategorii z `extracted_devices` lub `intent`
- [ ] Osobne prompty per kategoria: `phone`, `laptop`, `watch`, `etui`
- [ ] Pola per kategoria:
  - phone: `battery_mah`, `ram_gb`, `camera_mpx`, `screen_inch`, `refresh_rate_hz`, `connectivity_5g`, `price_max`
  - laptop: `ram_gb`, `storage_gb`, `screen_inch`, `screen_type`, `price_max`
  - watch: `battery_days`, `gps`, `heart_rate`, `case_mm`, `price_max`
  - etui: `case_type`, `compatible_with`

---

## 5. Node: `filter_search`

- [ ] Zapytanie do pgvector po metadanych JSONB na podstawie `specs` z extract_specs
- [ ] Obsługa `device_pool` — gdy `pool_action != reset` filtruje tylko po poolu
- [ ] Zwraca listę `clipper_id`

---

## 6. Node: `router`

- [ ] Liczy union `name_search` + `filter_search` (deduplikacja)
- [ ] Rozdziela na `llm_devices` i `card_devices` wg progów:
  - name_search zawsze → `llm_devices` (max 4)
  - reszta ≤10 łącznie → `llm_devices`
  - reszta >10 → `card_devices`
- [ ] Ustawia `mode: normal | heavy`

---

## 7. Node: `responder`

- [ ] **Normal mode:** fetch pełnych danych dla `llm_devices` → LLM generuje odpowiedź
- [ ] **Heavy mode:** LLM generuje tylko intro (bez speków) → zwraca `card_devices` do renderowania
- [ ] Prompt responder dostaje: pytanie + history + dane urządzeń

---

## 8. Graf — aktualizacja

- [ ] Dodać do StateGraph: `intent_classifier` → `extract` → (`name_search` || `extract_specs`) → `filter_search` → `router` → `responder`
- [ ] State rozszerzyć o: `intent`, `pool_action`, `specs`, `llm_devices`, `card_devices`, `mode`
- [ ] `run()` przyjmuje `session_id` i ładuje/zapisuje session state

---

## Kolejność wykonania

1. Baza danych (pgvector) — odblokuje filter_search
2. Session state — odblokuje intent + follow-upy
3. intent_classifier
4. filter_search
5. router
6. responder
7. extract_specs per kategoria
8. Testy end-to-end wszystkich use case'ów z USECASES.md
