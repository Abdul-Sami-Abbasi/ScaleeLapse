import numpy as np
from sklearn.cluster import KMeans


def extract_palette(hsv_image, k=5):
    """
    Extract dominant colors using K-Means clustering.

    Parameters:
        hsv_image: HSV image
        k: number of dominant colors

    Returns:
        palette: k dominant HSV colors
    """

    # Convert image into a list of pixels
    pixels = hsv_image.reshape((-1, 3))

    # Convert to float
    pixels = np.float32(pixels)

    # K-Means
    kmeans = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    kmeans.fit(pixels)

    # Dominant colors
    palette = kmeans.cluster_centers_

    # Number of pixels belonging to each cluster
    labels = kmeans.labels_

    counts = np.bincount(labels)

    # Sort colors from most dominant to least dominant
    order = np.argsort(counts)[::-1]

    palette = palette[order]
    counts = counts[order]

    return palette, counts