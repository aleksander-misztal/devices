import json
import random

# --- Phones ---
phone_brands = {
    "Apple": [
        "iPhone 11", "iPhone 11 Pro", "iPhone 11 Pro Max",
        "iPhone 12", "iPhone 12 Mini", "iPhone 12 Pro", "iPhone 12 Pro Max",
        "iPhone 13", "iPhone 13 Mini", "iPhone 13 Pro", "iPhone 13 Pro Max",
        "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max",
        "iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max",
        "iPhone 16", "iPhone 16 Plus", "iPhone 16 Pro", "iPhone 16 Pro Max",
        "iPhone SE 2022", "iPhone SE 2023",
    ],
    "Samsung": [
        "Galaxy S20", "Galaxy S20+", "Galaxy S20 Ultra",
        "Galaxy S21", "Galaxy S21+", "Galaxy S21 Ultra",
        "Galaxy S22", "Galaxy S22+", "Galaxy S22 Ultra",
        "Galaxy S23", "Galaxy S23+", "Galaxy S23 Ultra",
        "Galaxy S24", "Galaxy S24+", "Galaxy S24 Ultra",
        "Galaxy S24 FE",
        "Galaxy A13", "Galaxy A23", "Galaxy A33 5G", "Galaxy A34 5G",
        "Galaxy A52s 5G", "Galaxy A53 5G", "Galaxy A54 5G", "Galaxy A55 5G",
        "Galaxy A73 5G",
        "Galaxy M34 5G", "Galaxy M54 5G",
        "Galaxy Z Fold 3", "Galaxy Z Fold 4", "Galaxy Z Fold 5", "Galaxy Z Fold 6",
        "Galaxy Z Flip 3", "Galaxy Z Flip 4", "Galaxy Z Flip 5", "Galaxy Z Flip 6",
        "Galaxy Note 20", "Galaxy Note 20 Ultra",
    ],
    "Google": [
        "Pixel 6", "Pixel 6 Pro", "Pixel 6a",
        "Pixel 7", "Pixel 7 Pro", "Pixel 7a",
        "Pixel 8", "Pixel 8 Pro", "Pixel 8a",
        "Pixel 9", "Pixel 9 Pro", "Pixel 9 Pro XL", "Pixel 9 Pro Fold",
        "Pixel Fold",
    ],
    "Xiaomi": [
        "Redmi 10", "Redmi 10 2022", "Redmi 12", "Redmi 12C",
        "Redmi Note 11", "Redmi Note 11 Pro", "Redmi Note 11 Pro+",
        "Redmi Note 12", "Redmi Note 12 Pro", "Redmi Note 12 Pro+",
        "Redmi Note 13", "Redmi Note 13 Pro", "Redmi Note 13 Pro+",
        "Xiaomi 12", "Xiaomi 12 Pro", "Xiaomi 12T", "Xiaomi 12T Pro",
        "Xiaomi 13", "Xiaomi 13 Pro", "Xiaomi 13T", "Xiaomi 13T Pro",
        "Xiaomi 14", "Xiaomi 14 Pro", "Xiaomi 14T", "Xiaomi 14T Pro",
        "POCO X4 Pro 5G", "POCO X5", "POCO X5 Pro",
        "POCO F4", "POCO F5", "POCO F6",
        "POCO M4 Pro", "POCO M5",
    ],
    "OnePlus": [
        "OnePlus 9", "OnePlus 9 Pro",
        "OnePlus 10 Pro", "OnePlus 10T",
        "OnePlus 11", "OnePlus 11R",
        "OnePlus 12", "OnePlus 12R",
        "OnePlus Nord 2T", "OnePlus Nord 3", "OnePlus Nord 4",
        "OnePlus Nord CE 2 Lite", "OnePlus Nord CE 3", "OnePlus Nord CE 3 Lite",
        "OnePlus Open",
    ],
    "Motorola": [
        "Moto G52", "Moto G53", "Moto G54", "Moto G62", "Moto G73", "Moto G84",
        "Moto G Power 2024", "Moto G Stylus 2024",
        "Edge 30", "Edge 30 Pro", "Edge 30 Ultra",
        "Edge 40", "Edge 40 Pro", "Edge 40 Neo",
        "Edge 50 Pro", "Edge 50 Ultra",
        "Razr 40", "Razr 40 Ultra",
        "Razr 2023", "Razr+ 2023", "Razr 2024",
    ],
    "Sony": [
        "Xperia 1 IV", "Xperia 5 IV", "Xperia 10 IV",
        "Xperia 1 V", "Xperia 5 V", "Xperia 10 V",
        "Xperia 1 VI", "Xperia 5 VI", "Xperia 10 VI",
        "Xperia Pro-I",
    ],
    "OPPO": [
        "OPPO Reno 8", "OPPO Reno 8 Pro", "OPPO Reno 8 Pro+",
        "OPPO Reno 10", "OPPO Reno 10 Pro", "OPPO Reno 10 Pro+",
        "OPPO Reno 11", "OPPO Reno 11 Pro",
        "OPPO Find X5", "OPPO Find X5 Pro",
        "OPPO Find X6", "OPPO Find X6 Pro",
        "OPPO A78 5G", "OPPO A98 5G",
    ],
    "Huawei": [
        "P50 Pro", "P60 Pro",
        "Mate 40 Pro", "Mate 50 Pro", "Mate 60 Pro",
        "Nova 9", "Nova 10", "Nova 11 Pro",
        "P70 Pro", "Mate X3",
    ],
    "Nothing": [
        "Nothing Phone 1", "Nothing Phone 2", "Nothing Phone 2a", "Nothing Phone 2a Plus",
    ],
    "Realme": [
        "Realme 9 Pro", "Realme 9 Pro+",
        "Realme 10 Pro", "Realme 10 Pro+",
        "Realme 11 Pro", "Realme 11 Pro+",
        "Realme 12 Pro", "Realme 12 Pro+",
        "Realme GT 3", "Realme GT 5", "Realme GT 6",
        "Realme GT Neo 5", "Realme GT Neo 6",
    ],
    "Fairphone": [
        "Fairphone 4", "Fairphone 5",
    ],
    "Nokia": [
        "Nokia G21", "Nokia G22", "Nokia G42 5G", "Nokia G60 5G",
        "Nokia X30 5G", "Nokia XR21",
        "Nokia C32", "Nokia C22",
        "Nokia 8210 4G",
    ],
    "vivo": [
        "vivo V27", "vivo V27 Pro", "vivo V29", "vivo V29 Pro",
        "vivo V30", "vivo V30 Pro",
        "vivo X90 Pro", "vivo X100 Pro",
        "vivo Y76 5G", "vivo Y100",
    ],
    "Honor": [
        "Honor 90", "Honor 90 Pro",
        "Honor Magic5 Pro", "Honor Magic6 Pro",
        "Honor X8", "Honor X9b",
        "Honor 200", "Honor 200 Pro",
    ],
    "Asus": [
        "Zenfone 9", "Zenfone 10",
        "ROG Phone 6", "ROG Phone 7", "ROG Phone 8", "ROG Phone 8 Pro",
    ],
    "Infinix": [
        "Infinix Note 30", "Infinix Note 30 Pro",
        "Infinix Hot 30", "Infinix Zero 30 5G",
    ],
    "Tecno": [
        "Tecno Camon 20 Pro", "Tecno Phantom X2 Pro",
        "Tecno Spark 20 Pro",
    ],
}

# --- Laptops ---
laptop_brands = {
    "Apple": [
        "MacBook Air 13 M1",
        "MacBook Air 13 M2", "MacBook Air 15 M2",
        "MacBook Air 13 M3", "MacBook Air 15 M3",
        "MacBook Air 13 M4", "MacBook Air 15 M4",
        "MacBook Pro 13 M2",
        "MacBook Pro 14 M3", "MacBook Pro 16 M3",
        "MacBook Pro 14 M3 Pro", "MacBook Pro 14 M3 Max",
        "MacBook Pro 16 M3 Pro", "MacBook Pro 16 M3 Max",
        "MacBook Pro 14 M4", "MacBook Pro 16 M4",
        "MacBook Pro 14 M4 Pro", "MacBook Pro 14 M4 Max",
        "MacBook Pro 16 M4 Pro", "MacBook Pro 16 M4 Max",
    ],
    "Dell": [
        "XPS 13 9310", "XPS 13 9320", "XPS 13 9340",
        "XPS 13 Plus 9320",
        "XPS 15 9510", "XPS 15 9520", "XPS 15 9530",
        "XPS 17 9710", "XPS 17 9720", "XPS 17 9730",
        "Inspiron 14 5420", "Inspiron 14 5430", "Inspiron 14 5440",
        "Inspiron 15 3520", "Inspiron 15 3530",
        "Inspiron 16 5620", "Inspiron 16 5630",
        "Latitude 5530", "Latitude 5540",
        "Latitude 7430", "Latitude 7440",
        "Latitude 9430", "Latitude 9440",
        "Vostro 14 3445", "Vostro 15 3530",
        "Alienware m15 R7", "Alienware m16 R1", "Alienware m18 R2",
    ],
    "Lenovo": [
        "ThinkPad X1 Carbon Gen 10", "ThinkPad X1 Carbon Gen 11", "ThinkPad X1 Carbon Gen 12",
        "ThinkPad X1 Yoga Gen 7", "ThinkPad X1 Yoga Gen 8",
        "ThinkPad T14 Gen 3", "ThinkPad T14 Gen 4",
        "ThinkPad T14s Gen 3", "ThinkPad T14s Gen 4",
        "ThinkPad T16 Gen 1", "ThinkPad T16 Gen 2",
        "ThinkPad E14 Gen 4", "ThinkPad E14 Gen 5",
        "ThinkPad E15 Gen 4", "ThinkPad E16 Gen 1",
        "ThinkPad L14 Gen 4", "ThinkPad L15 Gen 4",
        "IdeaPad 5 14 2023", "IdeaPad 5 15 2023",
        "IdeaPad 5 Pro 14 2023", "IdeaPad 5 Pro 16 2023",
        "IdeaPad Flex 5 14 2023",
        "Yoga 7 14 2023", "Yoga 7 16 2023",
        "Yoga 9 14 2023", "Yoga 9 14 2024",
        "Yoga Slim 6 14 2023",
        "Legion 5 15 2023", "Legion 5 15 2024",
        "Legion 5 Pro 16 2023", "Legion 5 Pro 16 2024",
        "Legion 7 16 2023", "Legion 7 16 2024",
        "LOQ 15 2023", "LOQ 15 2024",
    ],
    "HP": [
        "EliteBook 840 G9", "EliteBook 840 G10",
        "EliteBook 860 G9", "EliteBook 860 G10",
        "EliteBook 1040 G9", "EliteBook 1040 G10",
        "ProBook 440 G9", "ProBook 440 G10",
        "ProBook 450 G9", "ProBook 450 G10",
        "ProBook 455 G10",
        "Spectre x360 13 2023", "Spectre x360 14 2023",
        "Spectre x360 16 2023",
        "Envy x360 13 2023", "Envy x360 15 2023",
        "Envy 16 2023",
        "Pavilion 15 2023", "Pavilion Plus 14 2023",
        "Pavilion Aero 13 2023",
        "OMEN 16 2023", "OMEN 16 2024",
        "OMEN 17 2023",
        "Victus 15 2023", "Victus 16 2023",
        "Dragonfly G4", "Dragonfly Elite G1",
        "ZBook Fury 16 G10",
    ],
    "ASUS": [
        "ZenBook 14 UM3402YA", "ZenBook 14 UM3406HA",
        "ZenBook 14 OLED UM3406",
        "ZenBook 14X OLED UN5401",
        "ZenBook 15 UM3504",
        "ZenBook Pro 16X OLED UX7602",
        "VivoBook 14 X1404", "VivoBook 15 X1504", "VivoBook 16 X1605",
        "VivoBook 16X K3605",
        "VivoBook S 14 S5406",
        "ExpertBook B9 B9403CVA",
        "ExpertBook B5 B5404CVA",
        "ROG Zephyrus G14 2023", "ROG Zephyrus G14 2024",
        "ROG Zephyrus G16 2024",
        "ROG Zephyrus M16 2023",
        "ROG Strix G16 G614 2023", "ROG Strix G16 G614 2024",
        "ROG Strix G18 G814 2023",
        "ROG Strix SCAR 16 2024",
        "TUF Gaming A15 2023", "TUF Gaming A15 2024",
        "TUF Gaming F16 2024",
        "TUF Gaming F15 2023",
        "ProArt Studiobook 16 OLED",
    ],
    "Acer": [
        "Swift 3 SF314-512", "Swift 3 SF314-55",
        "Swift Go 14 SFG14-41", "Swift Go 14 SFG14-72",
        "Swift Go 16 SFG16-72",
        "Swift X 14 SFX14-51G", "Swift X 16 SFX16-61G",
        "Aspire 3 A315-58", "Aspire 3 A315-59",
        "Aspire 5 A514-54", "Aspire 5 A514-55",
        "Aspire 5 A517-58",
        "Aspire Lite 15 2023",
        "Predator Helios 16 PH16-71",
        "Predator Helios 18 PH18-71",
        "Predator Triton 500 SE",
        "Nitro 5 AN515-58", "Nitro 5 AN515-46",
        "Nitro 16 AN16-41",
        "ConceptD 5 Pro",
        "Extensa 15 EX215-55",
    ],
    "Microsoft": [
        "Surface Laptop 4 13.5", "Surface Laptop 4 15",
        "Surface Laptop 5 13.5", "Surface Laptop 5 15",
        "Surface Laptop 6 13.5", "Surface Laptop 6 15",
        "Surface Laptop Studio", "Surface Laptop Studio 2",
        "Surface Pro 8", "Surface Pro 9", "Surface Pro 10",
        "Surface Pro X",
        "Surface Go 3",
    ],
    "MSI": [
        "Prestige 13 Evo A12M", "Prestige 14 Evo A12M",
        "Prestige 14 H B13", "Prestige 15 A12UC",
        "Modern 14 B11MOU", "Modern 14 C12M",
        "Modern 15 B12M", "Modern 15 H B13M",
        "Raider GE68 HX 13V", "Raider GE78 HX 13V",
        "Stealth 14 Studio A13V", "Stealth 16 Studio A13V",
        "Stealth 16 Mercedes-AMG",
        "Katana 15 B13V", "Katana 17 B13V",
        "Sword 15 A12U", "Sword 16 HX B14V",
        "Vector GP68HX 13V",
        "Titan GT77 HX 13V", "Titan GT76",
        "Creator Z16 HX B13V",
    ],
    "Huawei": [
        "MateBook D 14 2022", "MateBook D 14 2023",
        "MateBook D 16 2022", "MateBook D 16 2023",
        "MateBook 14s 2022", "MateBook 14s 2023",
        "MateBook 16s 2022", "MateBook 16s 2023",
        "MateBook X Pro 2022", "MateBook X Pro 2023", "MateBook X Pro 2024",
        "MateBook E 2022",
    ],
    "LG": [
        "Gram 14 14Z90P", "Gram 14 14Z90R",
        "Gram 16 16Z90P", "Gram 16 16Z90R",
        "Gram 17 17Z90P", "Gram 17 17Z90R",
        "Gram Pro 14 14Z90SP", "Gram Pro 16 16Z90SP",
        "Gram SuperSlim 15 15Z90RT",
        "Gram 360 14 14T90P",
    ],
    "Samsung": [
        "Galaxy Book 2 Pro 13", "Galaxy Book 2 Pro 15",
        "Galaxy Book 2 Pro 360 13", "Galaxy Book 2 Pro 360 15",
        "Galaxy Book 3 Pro 14", "Galaxy Book 3 Pro 16",
        "Galaxy Book 3 Pro 360 13", "Galaxy Book 3 Pro 360 15",
        "Galaxy Book 3 360 13", "Galaxy Book 3 360 15",
        "Galaxy Book 3 Ultra 16",
        "Galaxy Book 4 Pro 14", "Galaxy Book 4 Pro 16",
        "Galaxy Book 4 360 14",
        "Galaxy Book 4 Edge 14",
    ],
    "Razer": [
        "Razer Blade 14 2022", "Razer Blade 14 2023", "Razer Blade 14 2024",
        "Razer Blade 15 2022", "Razer Blade 15 2023", "Razer Blade 15 2024",
        "Razer Blade 16 2023", "Razer Blade 16 2024",
        "Razer Blade 18 2023", "Razer Blade 18 2024",
        "Razer Book 13",
    ],
    "Gigabyte": [
        "Aero 16 XE5", "Aero 16 YE5",
        "AORUS 15 XE5", "AORUS 15 BKF", "AORUS 17X AZF",
        "G6X 9MG", "G5 KF",
    ],
    "Framework": [
        "Framework Laptop 13 AMD", "Framework Laptop 13 Intel",
        "Framework Laptop 16",
    ],
}

# --- Smartwatches ---
watch_brands = {
    "Apple": [
        "Watch Series 6 40mm", "Watch Series 6 44mm",
        "Watch Series 7 41mm", "Watch Series 7 45mm",
        "Watch Series 8 41mm", "Watch Series 8 45mm",
        "Watch Series 9 41mm", "Watch Series 9 45mm",
        "Watch Series 10 42mm", "Watch Series 10 46mm",
        "Watch Ultra 49mm", "Watch Ultra 2 49mm",
        "Watch SE 40mm 2022", "Watch SE 44mm 2022",
        "Watch SE 40mm 2023", "Watch SE 44mm 2023",
    ],
    "Samsung": [
        "Galaxy Watch 4 40mm", "Galaxy Watch 4 44mm",
        "Galaxy Watch 4 Classic 42mm", "Galaxy Watch 4 Classic 46mm",
        "Galaxy Watch 5 40mm", "Galaxy Watch 5 44mm",
        "Galaxy Watch 5 Pro 45mm",
        "Galaxy Watch 6 40mm", "Galaxy Watch 6 44mm",
        "Galaxy Watch 6 Classic 43mm", "Galaxy Watch 6 Classic 47mm",
        "Galaxy Watch 7 40mm", "Galaxy Watch 7 44mm",
        "Galaxy Watch Ultra 47mm",
        "Galaxy Watch FE 40mm",
        "Galaxy Fit 2", "Galaxy Fit 3",
    ],
    "Garmin": [
        "Fenix 6 Pro", "Fenix 7", "Fenix 7 Pro", "Fenix 7X Pro", "Fenix 7S Pro",
        "Fenix 8 Solar 47mm", "Fenix 8 Solar 51mm",
        "Epix Gen 2 42mm", "Epix Pro 42mm", "Epix Pro 47mm", "Epix Pro 51mm",
        "Forerunner 55", "Forerunner 155", "Forerunner 255", "Forerunner 265",
        "Forerunner 745", "Forerunner 945", "Forerunner 965",
        "Venu 2", "Venu 2 Plus", "Venu 2S",
        "Venu 3", "Venu 3S",
        "Vivoactive 4", "Vivoactive 4S", "Vivoactive 5",
        "Instinct 2", "Instinct 2 Solar", "Instinct 2S",
        "Instinct Crossover",
        "Descent Mk3i 43mm", "Descent Mk3i 51mm",
        "MARQ Gen 2",
    ],
    "Fitbit": [
        "Sense 2", "Versa 4", "Versa 3",
        "Charge 5", "Charge 6",
        "Inspire 3", "Inspire 2",
        "Luxe",
    ],
    "Google": [
        "Pixel Watch 41mm", "Pixel Watch 2 41mm", "Pixel Watch 2 45mm",
        "Pixel Watch 3 41mm", "Pixel Watch 3 45mm",
    ],
    "Huawei": [
        "Watch GT 3 42mm", "Watch GT 3 46mm", "Watch GT 3 Pro 43mm", "Watch GT 3 Pro 46mm",
        "Watch GT 4 41mm", "Watch GT 4 46mm",
        "Watch 3", "Watch 3 Pro",
        "Watch 4", "Watch 4 Pro",
        "Band 7", "Band 8", "Band 9",
    ],
    "Xiaomi": [
        "Mi Band 6", "Mi Band 7", "Mi Band 7 Pro", "Mi Band 8", "Mi Band 8 Pro", "Mi Band 9",
        "Watch S1", "Watch S1 Active", "Watch S2 42mm", "Watch S2 46mm",
        "Watch S3",
        "Redmi Watch 2 Lite", "Redmi Watch 3", "Redmi Watch 3 Active", "Redmi Watch 4",
    ],
    "Amazfit": [
        "GTR 3", "GTR 3 Pro", "GTR 4",
        "GTS 3", "GTS 4", "GTS 4 Mini",
        "GTR Mini",
        "T-Rex Pro", "T-Rex 2", "T-Rex Ultra",
        "Bip 3", "Bip 3 Pro", "Bip 5", "Bip 5 Unity",
        "Balance", "Falcon",
        "Cheetah Pro",
    ],
    "Polar": [
        "Grit X2 Pro", "Vantage V3", "Vantage M2",
        "Pacer Pro", "Pacer",
        "Ignite 3", "Ignite 2",
        "Unite",
    ],
    "Suunto": [
        "Race", "Race S", "Race Titanium",
        "Vertical", "Vertical Titanium Solar",
        "9 Peak Pro",
        "5 Peak", "3 Fitness",
    ],
    "Withings": [
        "ScanWatch 2 38mm", "ScanWatch 2 42mm",
        "ScanWatch Nova 43mm",
        "ScanWatch Light",
        "Steel HR 36mm", "Steel HR 40mm",
        "Move ECG",
    ],
    "Coros": [
        "Apex 2", "Apex 2 Pro",
        "Vertix 2", "Vertix 2S",
        "Pace 2", "Pace 3",
    ],
    "Mobvoi": [
        "TicWatch Pro 5", "TicWatch Pro 3 Ultra",
        "TicWatch E3",
        "TicWatch GTH 2",
    ],
    "Fossil": [
        "Gen 6 44mm", "Gen 6 Slim 42mm",
        "Gen 6 Wellness Edition",
        "Hybrid HR",
    ],
    "Casio": [
        "G-SHOCK GBD-H2000", "G-SHOCK GBD-200",
        "G-SHOCK GBA-900", "G-SHOCK DW-H5600",
        "Pro Trek WSD-F21HR",
    ],
    "OnePlus": [
        "Watch 2", "Watch 2R", "Nord Watch",
    ],
    "Oppo": [
        "Watch 3 Pro", "Watch X",
        "Band 2",
    ],
    "Honor": [
        "Watch GS Pro", "Watch 4 Pro",
        "Band 8",
    ],
}

devices = []
device_id = 1

def add_device(category, brand, model):
    global device_id
    devices.append({
        "clipper_id": f"DEV-{device_id:04d}",
        "name": f"{brand} {model}",
        "category": category,
    })
    device_id += 1

# Generate phones
for brand, models in phone_brands.items():
    for model in models:
        add_device("phone", brand, model)

# Generate laptops
for brand, models in laptop_brands.items():
    for model in models:
        add_device("laptop", brand, model)

# Generate watches
for brand, models in watch_brands.items():
    for model in models:
        add_device("watch", brand, model)

# Generate cases (etui) — for phones and watches only
case_sources = [
    (d["name"].split()[0], " ".join(d["name"].split()[1:]))
    for d in devices if d["category"] in ("phone", "watch")
]

case_types = ["silikonowe", "skórzane", "pancerne", "przezroczyste", "portfelowe", "magnetyczne", "z klapką", "matowe", "brokatowe", "z podstawką"]

for brand, model in case_sources:
    num_cases = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
    chosen_types = random.sample(case_types, num_cases)
    for ctype in chosen_types:
        devices.append({
            "clipper_id": f"DEV-{device_id:04d}",
            "name": f"Etui do {brand} {model}",
            "category": "etui",
        })
        device_id += 1

# Stats
phones = sum(1 for d in devices if d["category"] == "phone")
laptops = sum(1 for d in devices if d["category"] == "laptop")
watches = sum(1 for d in devices if d["category"] == "watch")
cases = sum(1 for d in devices if d["category"] == "etui")

print(f"Phones:  {phones}")
print(f"Laptops: {laptops}")
print(f"Watches: {watches}")
print(f"Cases:   {cases}")
print(f"Total:   {len(devices)}")

with open("devices.json", "w", encoding="utf-8") as f:
    json.dump(devices, f, ensure_ascii=False, indent=2)

print("\nSaved to devices.json")
