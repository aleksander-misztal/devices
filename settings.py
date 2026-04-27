import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")

DEVICES_PATH = "data/devices.json"
MAX_CANDIDATES = 30

# --- Session 1: name-based ---
# Pokrycie: exact match, partial, typos, slang, mixed lang, comparisons,
# wrong brand+model, accessory, unrelated, edge cases z numerami i skrótami
NAME_QUESTIONS = [
    # Exact / oczywiste
    "Szukam etui do iPhone 15 Pro",
    "czy macie Samsung Galaxy S24 Ultra?",
    "Apple Watch Series 10 46mm - ile kosztuje?",

    # Partial / tylko model bez marki
    "szukam ThinkPad X1 Carbon Gen 12",
    "mam pytanie o Zenfone 10",
    "Pixel 9 Pro XL jest dostępny?",

    # Odmiana / potoczny zapis / literówki
    "macie cos do iphone'a 14 pro max?",
    "appel wacz siries 10 ile kosztuje",
    "galaksy s22 ultra, macie?",

    # Skróty i slang
    "s24u ile kasy",
    "ip16pm etui",
    "jabłuszko 15 pro",

    # Porównania (2+ urządzenia)
    "co jest lepsze: MacBook Air M3 czy Dell XPS 15?",
    "porównaj Galaxy Watch 7 z Apple Watch Series 10",
    "który szybszy: Pixel 9 Pro czy iPhone 16 Pro?",

    # Pomylona marka z modelem
    "chce kupic iphone galaxy s23",
    "mam samsunga iPhone 14, szukam etui",

    # Nieistniejące urządzenie
    "macie Samsung UltraBlast X9000 Pro?",

    # Urządzenie wspomniane w kontekście
    "mam galaxy z23 i szukam do niego etui pancernego",

    # Totalnie niezwiązane
    "kiedy przyjdzie moja paczka nr 8821?",
]

# --- Session 2: filter-based ---
# Pokrycie: aparat mpx, bateria mah, ekran, RAM, storage, ładowarka bool,
# budżet, cechy ogólne, kombinacje filtrów, szum i edge cases
FILTER_QUESTIONS = [
    # Aparat
    "szukam telefonu z aparatem co najmniej 108 mpx",
    "który samsung ma najlepszy aparat do zdjęć nocnych?",
    "chcę coś z dobrym zoomem optycznym, najlepiej 10x",

    # Bateria
    "telefon z baterią powyżej 5000 mAh, najlepiej samsung",
    "jaki zegarek garmin ma najdłuższy czas pracy?",
    "szukam laptopa który wytrzyma cały dzień bez ładowania",

    # Ekran
    "chcę laptop z ekranem OLED przynajmniej 14 cali",
    "telefon z ekranem 120hz i jasnym wyświetlaczem",
    "zegarek z dużą tarczą, minimum 46mm",

    # RAM / storage
    "szukam laptopa z 32GB RAM do programowania",
    "telefon z przynajmniej 256GB pamięci wewnętrznej",
    "laptop do video editingu, potrzebuję dużo RAM i dysk SSD",

    # Ładowarka / akcesoria (bool)
    "czy do Galaxy S24 jest ładowarka w zestawie?",
    "szukam telefonu który ma ładowarkę w pudełku",

    # Budżet
    "mam 1500 zł co polecacie na telefon?",
    "szukam laptopa do 4000 zł dla studenta",

    # Kombinacje filtrów z szumem
    "hej, szukam telefonu 5G z min 8GB RAM i aparatem 50mpx, budżet max 3k",
    "potrzebuję zegarka sportowego GPS z pulsometrem i co najmniej 7 dni baterii",

    # Edge: błędne wartości / bez sensu
    "telefon z baterią 500 mAh i 1TB RAM",

    # Edge: ogólne bez filtrów
    "który samsung jest najlepszy w ogóle?",
]
