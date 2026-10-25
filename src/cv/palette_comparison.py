import os
import json
import numpy as np
from sklearn.cluster import KMeans

PALETTE_PATH = "data/processed/cv/palettes"
REFERENCE_PATH = "data/processed/cv/reference_palettes"

# Number of colors in the final brand reference palette
K = 5


def calculate_reference_palette(brand_data):
    """
    Create a robust reference palette for a brand.

    Instead of averaging K-Means colors by their position,
    collect all dominant colors from all images and run
    K-Means again to find the brand's overall dominant colors.
    """

    all_colors = []

    for image_data in brand_data:

        palette = np.array(
            image_data["palette_hsv"],
            dtype=np.float32
        )

        counts = np.array(
            image_data["pixel_counts"],
            dtype=np.float32
        )

        # Add each color according to how important it was
        for color, count in zip(palette, counts):

            # Normalize the count so very large numbers
            # don't make the dataset unnecessarily huge
            repetitions = max(1, int(count / 1000))

            for _ in range(repetitions):
                all_colors.append(color)

    all_colors = np.array(all_colors, dtype=np.float32)

    # Make sure we have enough colors
    if len(all_colors) < K:
        raise ValueError(
            "Not enough colors available to create reference palette."
        )

    kmeans = KMeans(
        n_clusters=K,
        random_state=42,
        n_init=10
    )

    kmeans.fit(all_colors)

    reference_palette = kmeans.cluster_centers_

    # Sort colors by importance
    labels = kmeans.labels_
    counts = np.bincount(labels)

    order = np.argsort(counts)[::-1]

    reference_palette = reference_palette[order]

    return reference_palette


def create_reference_palettes():

    os.makedirs(
        REFERENCE_PATH,
        exist_ok=True
    )

    brand_files = [
        file
        for file in os.listdir(PALETTE_PATH)
        if file.endswith(".json")
    ]

    print("\nCreating improved brand reference palettes...\n")

    for filename in sorted(brand_files):

        brand_name = filename.replace(
            ".json",
            ""
        )

        file_path = os.path.join(
            PALETTE_PATH,
            filename
        )

        with open(file_path, "r") as file:
            brand_data = json.load(file)

        if not brand_data:
            continue

        reference_palette = calculate_reference_palette(
            brand_data
        )

        output = {
            "brand": brand_name,
            "number_of_images": len(brand_data),
            "reference_palette_hsv": reference_palette.tolist()
        }

        output_file = os.path.join(
            REFERENCE_PATH,
            filename
        )

        with open(output_file, "w") as file:
            json.dump(
                output,
                file,
                indent=4
            )

        print(
            f"✓ {brand_name}: "
            f"{len(brand_data)} images"
        )

    print(
        "\nImproved reference palette "
        "creation complete."
    )


if __name__ == "__main__":
    create_reference_palettes()