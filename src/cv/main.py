import os
import json

from preprocessing import load_and_preprocess
from palette_extraction import extract_palette


DATASET_PATH = "data/raw/brandimages"
OUTPUT_PATH = "data/processed/cv/palettes"


def process_dataset():

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    total_images = 0
    successful_images = 0

    for brand in sorted(os.listdir(DATASET_PATH)):

        brand_path = os.path.join(DATASET_PATH, brand)

        if not os.path.isdir(brand_path):
            continue

        print(f"\nProcessing brand: {brand}")

        brand_results = []

        for filename in sorted(os.listdir(brand_path)):

            image_path = os.path.join(brand_path, filename)

            # Only process image files
            if not filename.lower().endswith(
                (".jpg", ".jpeg", ".png", ".webp")
            ):
                continue

            total_images += 1

            try:

                rgb_image, hsv_image = load_and_preprocess(
                    image_path
                )

                palette, counts = extract_palette(
                    hsv_image,
                    k=5
                )

                result = {
                    "image": filename,
                    "palette_hsv": palette.tolist(),
                    "pixel_counts": counts.tolist()
                }

                brand_results.append(result)

                successful_images += 1

                print(f"  ✓ {filename}")

            except Exception as e:

                print(f"  ✗ {filename}")
                print(f"    Error: {e}")

        # Save brand results
        output_file = os.path.join(
            OUTPUT_PATH,
            f"{brand}.json"
        )

        with open(output_file, "w") as file:
            json.dump(
                brand_results,
                file,
                indent=4
            )

    print("\n==============================")
    print("PHASE 2 - PALETTE EXTRACTION")
    print("==============================")
    print(f"Total images: {total_images}")
    print(f"Successful: {successful_images}")
    print(f"Failed: {total_images - successful_images}")


if __name__ == "__main__":
    process_dataset()