"""Evaluation against actual supplied labels. Reject demo data for research runs."""

import argparse, json, hashlib, platform, time
from pathlib import Path
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)


def classification(truth, prediction):
    if not truth or len(truth) != len(prediction):
        raise ValueError("Nonempty aligned labels required.")
    p, r, f, _ = precision_recall_fscore_support(
        truth, prediction, average="macro", zero_division=0
    )
    labels = sorted(set(truth) | set(prediction))
    return {
        "accuracy": accuracy_score(truth, prediction),
        "precision_macro": p,
        "recall_macro": r,
        "f1_macro": f,
        "labels": labels,
        "confusion_matrix": confusion_matrix(truth, prediction, labels=labels).tolist(),
    }


def iou(a, b):
    for box in [a, b]:
        if len(box) != 4 or box[2] < box[0] or box[3] < box[1]:
            raise ValueError("Boxes must be [x1,y1,x2,y2] with positive extent.")
    intersect = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(
        0, min(a[3], b[3]) - max(a[1], b[1])
    )
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - intersect
    return intersect / union if union else 0


def sus(answers):
    if len(answers) != 10 or any(type(x) != int or x < 1 or x > 5 for x in answers):
        raise ValueError("Provide ten integer answers from 1 to 5.")
    return sum(x - 1 if i % 2 == 0 else 5 - x for i, x in enumerate(answers)) * 2.5


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    data = json.loads(args.input.read_text())
    if data.get("is_demo", True) or not data.get("provenance"):
        raise ValueError("Research evaluation requires is_demo=false and provenance.")
    result = classification(data["truth"], data["prediction"])
    report = {
        "model": data["model"],
        "dataset": str(args.input),
        "dataset_version": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "parameters": data.get("parameters", {}),
        "split": data["split"],
        "seed": data.get("seed"),
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "metrics": result,
        "environment": platform.python_version(),
        "notes": data.get("notes", []),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
