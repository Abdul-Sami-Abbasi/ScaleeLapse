
import os
import json
import itertools
import numpy as np

PALETTE_PATH = "data/processed/cv/palettes"
REFERENCE_PATH = "data/processed/cv/reference_palettes"
OUTPUT_PATH = "data/processed/cv/comparison"

# Keep this threshold unchanged for the first test.
THRESHOLD = 30.0


def color_distance(color1, color2):
    """Calculate HSV Euclidean distance with circular hue."""

    h1, s1, v1 = map(float, color1)
    h2, s2, v2 = map(float, color2)

    # OpenCV hue ranges from 0 to 179.
    hue_diff = abs(h1 - h2)
    hue_diff = min(hue_diff, 180.0 - hue_diff)

    return float(np.sqrt(
        hue_diff ** 2
        + (s1 - s2) ** 2
        + (v1 - v2) ** 2
    ))


def calculate_palette_distance(
    image_palette,
    reference_palette,
    pixel_counts
):
    """
    Match image colors one-to-one with reference colors.
    Weight each distance by the image color's pixel share.
    """

    image_palette = np.asarray(
        image_palette, dtype=np.float32
    )
    reference_palette = np.asarray(
        reference_palette, dtype=np.float32
    )
    pixel_counts = np.asarray(
        pixel_counts, dtype=np.float64
    )

    if len(image_palette) != len(reference_palette):
        raise ValueError(
            "Image and reference palettes must have "
            "the same number of colors."
        )

    if len(pixel_counts) != len(image_palette):
        raise ValueError(
            "Pixel counts must match the image palette."
        )

    if np.any(pixel_counts < 0) or pixel_counts.sum() <= 0:
        raise ValueError("Pixel counts must be non-negative "
                         "and have a positive total.")

    # Convert counts into proportions that sum to 1.
    weights = pixel_counts / pixel_counts.sum()

    number_of_colors = len(image_palette)

    # Build a matrix of distances between every pair.
    distance_matrix = np.zeros(
        (number_of_colors, number_of_colors),
        dtype=np.float64
    )

    for i, image_color in enumerate(image_palette):
        for j, reference_color in enumerate(reference_palette):
            distance_matrix[i, j] = color_distance(
                image_color, reference_color
            )

    # Try every one-to-one assignment.
    # For five colors, there are only 5! = 120 assignments.
    best_distance = float("inf")

    for assignment in itertools.permutations(
        range(number_of_colors)
    ):
        assigned_distances = np.array([
            distance_matrix[i, assignment[i]]
            for i in range(number_of_colors)
        ])

        weighted_distance = float(
            np.sum(assigned_distances * weights)
        )

        if weighted_distance < best_distance:
            best_distance = weighted_distance

    return best_distance


def compare_brand(brand_name):
    """Compare each image against its brand reference palette."""

    palette_file = os.path.join(
        PALETTE_PATH, f"{brand_name}.json"
    )
    reference_file = os.path.join(
        REFERENCE_PATH, f"{brand_name}.json"
    )

    with open(palette_file, "r", encoding="utf-8") as file:
        image_data = json.load(file)

    with open(reference_file, "r", encoding="utf-8") as file:
        reference_data = json.load(file)

    reference_palette = reference_data[
        "reference_palette_hsv"
    ]

    results = []

    for image in image_data:
        distance = calculate_palette_distance(
            image["palette_hsv"],
            reference_palette,
            image["pixel_counts"]
        )

        status = (
            "CONSISTENT"
            if distance <= THRESHOLD
            else "DEVIATION DETECTED"
        )

        results.append({
            "image": image["image"],
            "distance": round(distance, 2),
            "status": status
        })

    return results


def compare_all_brands():
    """Compare all available brand palettes and save results."""

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    brand_files = sorted(
        filename
        for filename in os.listdir(PALETTE_PATH)
        if filename.endswith(".json")
    )

    total_images = 0
    consistent_images = 0
    deviation_images = 0
    all_distances = []

    print("\n================================")
    print("ONE-TO-ONE WEIGHTED HSV COMPARISON")
    print("================================")

    for filename in brand_files:
        brand_name = filename[:-5]

        reference_file = os.path.join(
            REFERENCE_PATH, filename
        )

        if not os.path.exists(reference_file):
            print(f"Skipping {brand_name}: reference missing")
            continue

        results = compare_brand(brand_name)

        output_file = os.path.join(
            OUTPUT_PATH, filename
        )

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(results, file, indent=4)

        brand_consistent = sum(
            result["status"] == "CONSISTENT"
            for result in results
        )
        brand_deviations = len(results) - brand_consistent

        total_images += len(results)
        consistent_images += brand_consistent
        deviation_images += brand_deviations

        all_distances.extend(
            result["distance"] for result in results
        )

        print(
            f"{brand_name}: {brand_consistent} consistent, "
            f"{brand_deviations} deviations"
        )

    print("\n================================")
    print("COMPARISON SUMMARY")
    print("================================")
    print(f"Threshold: {THRESHOLD}")
    print(f"Total images: {total_images}")
    print(f"Consistent: {consistent_images}")
    print(f"Deviations: {deviation_images}")

    if total_images > 0:
        print(
            "Consistency classification rate: "
            f"{consistent_images / total_images * 100:.2f}%"
        )
        print(f"Minimum distance: {min(all_distances):.2f}")
        print(f"Maximum distance: {max(all_distances):.2f}")
        print(f"Mean distance: {np.mean(all_distances):.2f}")
        print(f"Median distance: {np.median(all_distances):.2f}")

    print(f"\nResults saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    compare_all_brands()
