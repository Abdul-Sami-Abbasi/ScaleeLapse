import cv2
import numpy as np


def load_and_preprocess(image_path, size=(224, 224)):
    """
    Load an image and preprocess it.

    Steps:
    1. Read image
    2. Resize to 224x224
    3. Convert BGR to RGB
    4. Normalize pixel values
    5. Convert RGB to HSV
    """

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Resize
    image = cv2.resize(image, size)

    # OpenCV loads images as BGR
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Normalize pixel values from 0-255 to 0-1
    normalized = rgb_image.astype(np.float32) / 255.0

    # Convert normalized RGB back to 8-bit
    normalized_uint8 = (normalized * 255).astype(np.uint8)

    # RGB -> HSV
    hsv_image = cv2.cvtColor(normalized_uint8, cv2.COLOR_RGB2HSV)

    return rgb_image, hsv_image