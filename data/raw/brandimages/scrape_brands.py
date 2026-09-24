import time
import requests
from pathlib import Path
from ddgs import DDGS

# 6 Sectors x 6 Brands (4 SME + 2 Global) = 36 Brands Total (540 Images)
BRAND_QUERIES = {
    # --- 1. APPAREL & STREETWEAR (4 SME + 2 Global) ---
    "outfitters": "outfitters pk clothing product official",
    "khaadi": "khaadi store apparel collection photo",
    "cougar": "cougar casual wear clothing product",
    "rastah": "rastah streetwear fashion photo",
    "nike": "nike official clothing shoes product",
    "adidas": "adidas apparel sneakers official photo",

    # --- 2. FOOD & DINING (4 SME + 2 Global) ---
    "espresso": "espresso cafe coffee drink photo",
    "savour_foods": "savour foods food dish photo",
    "kababjees": "kababjees restaurant food photo",
    "broadway_pizza": "broadway pizza food item photo",
    "mcdonalds": "mcdonalds food item photo",
    "starbucks": "starbucks coffee cup photo",

    # --- 3. CPG & PACKAGED GOODS (4 SME + 2 Global) ---
    "tapal": "tapal tea packaging product photo",
    "shan_foods": "shan foods recipe mix packaging",
    "mitchells": "mitchells food product packaging",
    "gourmet": "gourmet foods bakery product packaging",
    "redbull": "red bull energy drink can",
    "pepsi": "pepsi drink can packaging",

    # --- 4. COSMETICS & BEAUTY (4 SME + 2 Global) ---
    "saeed_ghani": "saeed ghani skincare product packaging",
    "jenpharm": "jenpharm skincare product photo",
    "conatural": "conatural organic beauty product packaging",
    "hemani": "hemani herbal beauty product packaging",
    "loreal": "loreal cosmetics official product photo",
    "nivea": "nivea skincare packaging product photo",

    # --- 5. FOOTWEAR & LEATHER (4 SME + 2 Global) ---
    "servis": "servis shoes footwear collection photo",
    "ndure": "ndure shoes casual footwear photo",
    "urban_sole": "urban sole leather shoes photo",
    "jafferjees": "jafferjees genuine leather product photo",
    "bata": "bata shoes footwear product photo",
    "puma": "puma sports footwear official photo",

    # --- 6. TECH & ELECTRONICS (4 SME + 2 Global) ---
    "audionic": "audionic sound speakers headphones product",
    "ronin": "ronin mobile accessories product photo",
    "zero_lifestyle": "zero lifestyle smartwatch product photo",
    "space_tech": "space tech mobile accessories product photo",
    "samsung": "samsung galaxy smartphone product photo",
    "apple": "apple iphone product official photo"
}

TARGET_PER_BRAND = 15
FETCH_BUFFER = 22

BASE_DIR = Path(__file__).resolve().parents[3]
OUTPUT_DIR = BASE_DIR / "data" / "raw" / "brandimages"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

ddgs = DDGS()

for brand, query in BRAND_QUERIES.items():
    print(f"\n--> Downloading images for: {brand}")
    
    brand_dir = OUTPUT_DIR / brand
    brand_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        results = list(ddgs.images(query, max_results=FETCH_BUFFER))
    except Exception as e:
        print(f"Skipping {brand} due to rate limit/error: {e}")
        time.sleep(5)
        continue
    
    saved_count = 0
    for idx, item in enumerate(results):
        if saved_count >= TARGET_PER_BRAND:
            break
            
        image_url = item.get("image")
        if not image_url:
            continue
        
        try:
            response = requests.get(image_url, timeout=5, headers=headers)
            if response.status_code == 200:
                ext = image_url.split('.')[-1].split('?')[0].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                    ext = 'jpg'
                
                file_path = brand_dir / f"{brand}_{saved_count + 1}.{ext}"
                with open(file_path, "wb") as f:
                    f.write(response.content)
                
                saved_count += 1
                time.sleep(0.2)
        except Exception:
            continue

    print(f"Done: Downloaded {saved_count}/{TARGET_PER_BRAND} images for {brand}.")
    time.sleep(2)

print("\n--- DATASET EXTRACTION COMPLETE (540 IMAGES) ---")