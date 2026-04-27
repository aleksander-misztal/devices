h1. Intencja: wyszukiwanie urządzeń

Intencja decyduje czy pytanie użytkownika dotyczy urządzeń i powinno trafić do pipeline'u wyszukiwania. Jest bramą wejściową — bez niej pipeline nie jest w ogóle uruchamiany.

----

h2. Wejście

*message*
Surowa wiadomość użytkownika (string).

----

h2. Logika

h3. Krok 1 - Wykrycie intencji

Na podstawie treści wiadomości określamy czy użytkownik pyta o urządzenie lub jego specyfikację. Intencja powinna być aktywowana gdy pytanie dotyczy:
* konkretnego urządzenia (telefon, laptop, zegarek, etui) — po nazwie lub modelu
* parametrów technicznych (bateria, RAM, aparat, cena, ekran itp.)
* porównania urządzeń
* dostępności lub ceny produktu

Intencja *nie* powinna być aktywowana gdy pytanie dotyczy:
* statusu zamówienia
* zwrotów i reklamacji
* ogólnych pytań niezwiązanych z produktami

h3. Krok 2 - Routing

Jeśli intencja wykryta: przekazujemy wiadomość do węzła {{extract}} jako pole {{question}} w stanie grafu.

Jeśli intencja nie wykryta: obsługa przez standardowy flow chatbota (poza pipeline'em).

----

h2. Wyjście

*question*
Oryginalna wiadomość użytkownika przekazana do stanu grafu jako pole {{question}}.
{code:json}
{"question": "szukam telefonu z baterią powyżej 5000 mAh, budżet max 2000 zł"}
{code}
