# Device RAG — Use Cases

## Typy pytań

### 1. Konkretne urządzenie
Użytkownik podaje nazwę lub model.

**Przykłady:**
- "etui do iPhone 15 Pro"
- "ile kosztuje Galaxy S24 Ultra"
- "ThinkPad X1 Carbon Gen 12"

**System:** name search → aggregate → LLM odpowiada z danymi urządzenia

---

### 2. Porównanie konkretnych urządzeń
Użytkownik wymienia 2+ urządzeń.

**Przykłady:**
- "MacBook Air M3 vs Dell XPS 15"
- "Galaxy Watch 7 czy Apple Watch Series 10"

**System:** name search dla każdego → aggregate → LLM porównuje (max 4 urządzenia w kontekście LLM)

---

### 3. Filtry bez konkretnego modelu
Użytkownik szuka po parametrach.

**Przykłady:**
- "telefon z baterią powyżej 5000 mAh"
- "laptop z 32GB RAM do programowania"
- "zegarek GPS z pulsometrem"

**System:** extract_specs → pgvector/SQL po filtrach → jeśli mało wyników (≤5): LLM odpowiada normalnie; jeśli dużo: LLM generuje intro + kod dokłada listę kart z guzikami

---

### 4. Marka bez modelu
Użytkownik podaje tylko markę lub kategorię.

**Przykłady:**
- "jakie macie etui do samsungów"
- "który Garmin polecacie"

**System:** filters (brand + category) → lista kart; LLM nie dostaje 100 urządzeń, generuje tylko intro

---

### 5. Mieszany (konkret + filtr)
Użytkownik podaje jedno konkretne urządzenie i jedno przez filtr.

**Przykłady:**
- "porównaj S24 z iPhonem który ma największą baterię"
- "Galaxy Watch Ultra vs najtańszy Garmin"

**System:** name search dla konkretnego + filter search dla parametrycznego → aggregate łączy → LLM porównuje

---

### 6. Follow-up z session pool
Użytkownik dopytuje w kontekście poprzednich wyników.

**Przykłady:**
- *(po liście 100 telefonów)* "który z nich ma najlepszy aparat"
- *(po liście)* "porównaj top 3 z nich"
- *(po liście)* "pokaż tylko te z 5G"

**System:** session state przechowuje `device_pool` z poprzedniego turnu → filter/name search działa tylko na poolu → jeśli "top 3" → LLM wybiera z poolu

---

### 7. Niezwiązane z urządzeniami
Pytanie nie dotyczy produktów.

**Przykłady:**
- "kiedy przyjdzie paczka"
- "gdzie jest sklep"

**System:** extract zwraca pustą listę → brak candidates → LLM odpowiada że nie obsługuje tego pytania

---

## Progi i limity

| Sytuacja | Akcja |
|---|---|
| candidates ≤ 5 | LLM dostaje pełne dane, odpowiada normalnie |
| candidates 6–30 | LLM dostaje listę nazw + ID, wybiera najlepsze |
| candidates > 30 | LLM generuje intro, kod renderuje listę kart |
| porównanie > 4 urządzeń | UI blokuje, prosi o zawężenie |
| follow-up pool > 100 | pool przechowywany, ale LLM pracuje na podzbiorze |

---

## Output pipeline i tryby renderowania

### Flow
```
name_search + filter_search
    → union ID (deduplikacja)
    → fetch danych z bazy
    → routing: normal / heavy
    → LLM / UI
```

### Normal mode (≤10 urządzeń łącznie)
- LLM dostaje pełne speki wszystkich urządzeń
- Generuje odpowiedź tekstową
- Frontend dołącza źródła (linki/karty) do urządzeń z odpowiedzi

### Heavy mode (>10 urządzeń)
- LLM dostaje tylko pytanie — **bez speków**
- Generuje krótkie intro ("Znalazłem X telefonów spełniających kryteria:")
- Kod renderuje listę kart; każda karta ma przycisk → po kliknięciu pobiera i wyświetla speki/opis

### Edge case: mieszany (konkret + filtr)
Urządzenia z name_search (konkretne) **zawsze** idą do LLM (max 4).
Nadmiar z filter_search idzie jako karty — nawet jeśli łącznie > 10.

```json
{
  "llm_devices": ["DEV-001", "DEV-002"],
  "card_devices": ["DEV-010", "DEV-011", "..."],
  "mode": "normal" | "heavy"
}
```

### Uzasadnienie
- LLM nie dostaje 50 speków bo przepełnia kontekst i halucynuje
- Karty rozwiązują UX dla dużych list bez degradacji jakości odpowiedzi
- Podział llm_devices/card_devices zapewnia że konkretne pytania zawsze dostają pełną odpowiedź

---

## Baza danych

### Schemat pgvector
- Dedykowane kolumny: `brand`, `category`, `price` — indeksowane, używane w WHERE
- JSONB: pozostałe speki (`battery_mah`, `ram_gb`, `camera_mpx` itp.)
- Embedding: na opisie + specach łącznie — używany do similarity search

### Uzasadnienie
Jedna baza zamiast relacyjna + wektorowa. Przy 2k urządzeń wydajność JSONB wystarczająca.
Osobna tabela relacyjna byłaby over-engineeringiem na tym etapie.

### Populacja
Dane ze scrapowania Clippera → normalizacja speców (LLM lub regex) → zapis z metadanymi → generowanie embeddingów on-write.
