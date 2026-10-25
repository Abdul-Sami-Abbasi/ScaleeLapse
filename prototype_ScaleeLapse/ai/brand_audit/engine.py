"""Deterministic HSV palette auditing. Scores measure color coverage, not accuracy."""

import colorsys
import io
import re
import threading
import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

LOCK = threading.Lock()
MAX_BYTES = 10 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 20_000_000


def hex_hsv(value):
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError("Colors must use six-digit HEX notation, e.g. #14B8A6.")
    return np.array(
        colorsys.rgb_to_hsv(*(int(value[i : i + 2], 16) / 255 for i in (1, 3, 5)))
    )


def decode_image(data):
    if len(data) > MAX_BYTES:
        raise ValueError("Image exceeds the 10 MB limit.")
    try:
        with Image.open(io.BytesIO(data)) as im:
            if im.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValueError("Use a JPEG, PNG or WebP image.")
            if im.width * im.height > 20_000_000:
                raise ValueError("Image exceeds 20 megapixels.")
            im = ImageOps.exif_transpose(im)
            if im.mode in {"RGBA", "LA"} or "transparency" in im.info:
                im = im.convert("RGBA")
                background = Image.new("RGBA", im.size, "white")
                background.alpha_composite(im)
                im = background
            im = im.convert("RGB")
            im.thumbnail((256, 256))
            return np.asarray(im).copy()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as e:
        raise ValueError("Image is corrupted or unsupported.") from e


def hsv_distance(a, b):
    # Circular hue distance; hue contributes less for near-neutral pixels.
    dh = (
        np.minimum(np.abs(a[..., 0] - b[..., 0]), 1 - np.abs(a[..., 0] - b[..., 0])) * 2
    )
    return np.sqrt(
        (dh * np.minimum(a[..., 1], b[..., 1])) ** 2
        + (a[..., 1] - b[..., 1]) ** 2
        + (a[..., 2] - b[..., 2]) ** 2
    ) / np.sqrt(3)


def analyze(data, colors, threshold=0.15, clusters=6):
    if not 0.01 <= threshold <= 0.5:
        raise ValueError("Color tolerance must be between 0.01 and 0.5.")
    rgb = decode_image(data)
    hsv = cv2.cvtColor(rgb.astype(np.float32) / 255, cv2.COLOR_RGB2HSV)
    hsv[..., 0] /= 360
    pixels = hsv.reshape(-1, 3)
    # Circular embedding avoids treating hues around 0 and 360 as distant.
    embedded = np.column_stack(
        (
            pixels[:, 1] * np.cos(pixels[:, 0] * 2 * np.pi),
            pixels[:, 1] * np.sin(pixels[:, 0] * 2 * np.pi),
            pixels[:, 2],
        )
    ).astype(np.float32)
    k = min(clusters, len(np.unique(embedded, axis=0)))
    with LOCK:
        cv2.setRNGSeed(42)
        _, labels, _ = cv2.kmeans(
            embedded,
            k,
            None,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 60, 0.001),
            3,
            cv2.KMEANS_PP_CENTERS,
        )
    palette = []
    approved = [(c, hex_hsv(c["hex"])) for c in colors]
    for idx in range(k):
        mask = labels.ravel() == idx
        sample = pixels[mask]
        angle = np.arctan2(
            np.mean(np.sin(sample[:, 0] * 2 * np.pi) * sample[:, 1]),
            np.mean(np.cos(sample[:, 0] * 2 * np.pi) * sample[:, 1]),
        ) % (2 * np.pi)
        center = np.array(
            [angle / (2 * np.pi), sample[:, 1].mean(), sample[:, 2].mean()]
        )
        rr = colorsys.hsv_to_rgb(*center)
        hexcode = "#" + "".join(f"{round(c * 255):02X}" for c in rr)
        matches = sorted(
            [(float(hsv_distance(center, v)), c) for c, v in approved],
            key=lambda x: x[0],
        )
        distance, match = matches[0] if matches else (None, None)
        palette.append(
            {
                "hex": hexcode,
                "hsv": center.tolist(),
                "percentage": round(float(mask.mean() * 100), 3),
                "matched": bool(match and distance <= threshold),
                "approved_color": match["hex"] if match else None,
                "role": match.get("role") if match and distance <= threshold else None,
                "distance": distance,
            }
        )
    palette.sort(key=lambda x: -x["percentage"])
    coverage = sum(p["percentage"] for p in palette if p["matched"])
    return {
        "score": round(min(100, coverage), 1) if colors else None,
        "off_brand_percentage": round(max(0, 100 - coverage), 1) if colors else None,
        "palette": palette,
        "roles_present": {
            role: any(p["matched"] and p["role"] == role for p in palette)
            for role in {c["role"] for c in colors}
        },
        "tolerance": threshold,
        "method": "HSV circular K-Means; palette coverage score",
        "logo": {
            "status": "NOT_EVALUATED",
            "reason": "Requires validated logo detector weights and brand-to-class mapping.",
        },
        "fonts": {
            "status": "MANUAL_REVIEW",
            "reason": "Approved-font list can be checked by a reviewer; automated font recognition is unavailable.",
        },
        "warnings": (
            [] if colors else ["Brand Kit colors are required before scoring."]
        )
        + (
            ["Off-brand palette coverage exceeds 10%."]
            if colors and coverage < 90
            else []
        ),
    }


def batch(items, colors):
    results = []
    for name, data in items:
        try:
            results.append({"filename": name, "result": analyze(data, colors)})
        except ValueError as e:
            results.append({"filename": name, "error": str(e)})
    return results
