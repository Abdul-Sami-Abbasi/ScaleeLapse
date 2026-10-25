import argparse, csv, json, sys, hashlib, time, platform
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ai.brand_audit.engine import analyze
from scripts.evaluation.evaluate import classification


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--kits", type=Path, required=True)
    p.add_argument("--threshold", type=float, default=90)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    kits = json.loads(a.kits.read_text())
    truth = []
    pred = []
    records = []
    with a.labels.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["split"] != "test":
                continue
            kit = kits[row["brand_id"]]
            if (
                not kit.get("kit_source")
                or not kit.get("colors")
                or not row["consent_reference"]
            ):
                raise ValueError("Owner kit and consent provenance required.")
            path = (ROOT / row["image_path"]).resolve()
            if not path.is_relative_to(ROOT / "data"):
                raise ValueError("Images must be inside data/.")
            result = analyze(
                path.read_bytes(), kit["colors"], kit.get("tolerance", 0.15)
            )
            truth.append(int(row["is_consistent"]))
            pred.append(int(result["score"] >= a.threshold))
            records.append(
                {
                    "image": row["image_path"],
                    "score": result["score"],
                    "truth": truth[-1],
                    "prediction": pred[-1],
                }
            )
    report = {
        "model": "HSV circular K-Means palette coverage",
        "dataset": str(a.labels),
        "dataset_version": hashlib.sha256(a.labels.read_bytes()).hexdigest(),
        "parameters": {"score_threshold": a.threshold},
        "split": "provided test only",
        "seed": 42,
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "metrics": classification(truth, pred),
        "environment": platform.python_version(),
        "records": records,
        "notes": [
            "Threshold must be fixed before inspecting test labels.",
            "Official kit authenticity/label quality require independent review.",
        ],
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
