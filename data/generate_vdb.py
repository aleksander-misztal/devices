import json
import random
from pathlib import Path

random.seed(42)

VDB_DIR = Path("vdb")
VDB_DIR.mkdir(exist_ok=True)

with open("devices.json", encoding="utf-8") as f:
    devices = json.load(f)

# --- Spec ranges per category ---

def phone_specs(name):
    return {
        "battery_mah": random.choice([3000, 3500, 4000, 4500, 5000, 5500, 6000]),
        "ram_gb": random.choice([4, 6, 8, 12, 16]),
        "storage_gb": random.choice([64, 128, 256, 512]),
        "camera_mpx": random.choice([12, 48, 50, 64, 108, 200]),
        "screen_inch": round(random.uniform(5.8, 6.9), 1),
        "screen_type": random.choice(["OLED", "AMOLED", "LCD", "OLED", "AMOLED"]),
        "refresh_rate_hz": random.choice([60, 90, 120, 144]),
        "connectivity_5g": random.choice([True, True, False]),
        "price_pln": random.choice([799, 999, 1299, 1799, 2499, 3499, 4999, 5999]),
        "has_charger_in_box": random.choice([True, False]),
    }

def laptop_specs(name):
    return {
        "ram_gb": random.choice([8, 16, 32, 64]),
        "storage_gb": random.choice([256, 512, 1024, 2048]),
        "screen_inch": random.choice([13.3, 14.0, 15.6, 16.0, 17.3]),
        "screen_type": random.choice(["IPS", "OLED", "AMOLED", "IPS", "IPS"]),
        "battery_wh": random.choice([45, 54, 60, 72, 86, 100]),
        "weight_kg": round(random.uniform(0.9, 2.8), 1),
        "price_pln": random.choice([1999, 2999, 3999, 4999, 6999, 8999, 12999]),
        "has_touchscreen": random.choice([True, False, False]),
    }

def watch_specs(name):
    return {
        "battery_days": random.choice([1, 2, 5, 7, 14, 18, 21]),
        "case_mm": random.choice([40, 41, 42, 44, 45, 46, 47, 49]),
        "gps": random.choice([True, True, False]),
        "heart_rate": True,
        "nfc": random.choice([True, False]),
        "water_resistant_atm": random.choice([3, 5, 10]),
        "price_pln": random.choice([299, 499, 799, 999, 1499, 1999, 2999]),
    }

def etui_specs(name):
    return {
        "case_type": name.get("case_type", random.choice(
            ["silikonowe", "skórzane", "pancerne", "przezroczyste", "portfelowe"]
        )),
        "magsafe": random.choice([True, False]),
        "compatible_with": name.get("compatible_with", ""),
        "price_pln": random.choice([29, 49, 79, 99, 149]),
    }

SPEC_FN = {
    "phone": phone_specs,
    "laptop": laptop_specs,
    "watch": watch_specs,
    "etui": etui_specs,
}

# --- Text templates per category ---

TEMPLATES = {
    "phone": (
        "{name} to smartfon wyposażony w wyświetlacz {screen_inch} cali z odświeżaniem {refresh_rate_hz} Hz. "
        "Bateria o pojemności {battery_mah} mAh zapewnia całodniowe użytkowanie. "
        "Aparat główny {camera_mpx} Mpx pozwala na robienie zdjęć wysokiej jakości. "
        "Pamięć RAM {ram_gb} GB i {storage_gb} GB przestrzeni na dane. "
        "Łączność 5G: {'tak' if connectivity_5g else 'nie'}. "
        "Cena: {price_pln} zł."
    ),
    "laptop": (
        "{name} to laptop z ekranem {screen_inch}\" ({screen_type}), pamięcią RAM {ram_gb} GB "
        "i dyskiem {storage_gb} GB. "
        "Bateria {battery_wh} Wh, waga {weight_kg} kg. "
        "Cena: {price_pln} zł."
    ),
    "watch": (
        "{name} to smartwatch z kopertą {case_mm} mm. "
        "Bateria wytrzymuje do {battery_days} dni. "
        "GPS: {'tak' if gps else 'nie'}, NFC: {'tak' if nfc else 'nie'}, "
        "wodoodporność {water_resistant_atm} ATM. "
        "Cena: {price_pln} zł."
    ),
    "etui": (
        "{name} — etui {case_type} do {compatible_with}. "
        "MagSafe: {'tak' if magsafe else 'nie'}. "
        "Cena: {price_pln} zł."
    ),
}


def render_text(category, device_name, specs, raw_device):
    template = TEMPLATES[category]
    ctx = {"name": device_name, **specs}
    if category == "etui":
        ctx["compatible_with"] = raw_device.get("compatible_with", "")
        ctx["case_type"] = specs.get("case_type", "")
    # eval f-string style via format_map with fallback
    try:
        return eval(f'f"""{template}"""', ctx)
    except Exception:
        # fallback: plain format
        return f"{device_name} — {category}. Cena: {specs.get('price_pln', '?')} zł."


saved = 0
for device in devices:
    cid = device["clipper_id"]
    category = device["category"]
    name = device["name"]

    spec_fn = SPEC_FN.get(category)
    if not spec_fn:
        continue

    specs = spec_fn(device)
    text = render_text(category, name, specs, device)

    doc = {
        "clipper_id": cid,
        "name": name,
        "category": category,
        "brand": name.split()[0],
        "specs": specs,
        "text": text,
    }

    (VDB_DIR / f"{cid}.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    saved += 1

print(f"Saved {saved} documents to {VDB_DIR}/")
