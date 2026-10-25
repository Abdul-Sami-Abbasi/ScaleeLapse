"""Opt-in YOLO adapter. Generic object weights are not a brand logo detector."""

from pathlib import Path


def detect(image_path, weights, class_name, confidence=0.5):
    if not Path(weights).is_file():
        raise ValueError("Validated logo detector weights required.")
    from ultralytics import YOLO

    model = YOLO(weights)
    if class_name not in model.names.values():
        raise ValueError("Brand class is absent from detector mapping.")
    result = model.predict(str(image_path), conf=confidence, verbose=False)[0]
    return [
        {
            "box": box.xyxy[0].tolist(),
            "confidence": float(box.conf[0]),
            "class": model.names[int(box.cls[0])],
        }
        for box in result.boxes
        if model.names[int(box.cls[0])] == class_name
    ]
