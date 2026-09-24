import time
import requests
from pathlib import Path
from ddgs import DDGS

BRAND_QUERIES = {
    
    "outfitters": "outfitters pk clothing product official",
    "khaadi": "khaadi store apparel collection photo",
    "cougar": "cougar casual wear clothing product",
    "rastah": "rastah streetwear fashion photo",
    "espresso": "espresso cafe coffee drink photo",
    "savour_foods": "savour foods food dish photo",
    "tapal": "tapal tea packaging product photo",
    
    
    "nike": "nike shoes official product",
    "starbucks": "starbucks coffee cup photo",
    "redbull": "red bull energy drink can"
}

TARGET_PER_BRAND = 50
FETCH_BUFFER = 65

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

print("\n--- DATASET EXTRACTION COMPLETE (500 IMAGES) ---")