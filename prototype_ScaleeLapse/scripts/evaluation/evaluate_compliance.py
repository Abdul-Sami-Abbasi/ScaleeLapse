import argparse, json, sys, hashlib, time, platform
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ai.compliance.engine import assess
from scripts.evaluation.evaluate import classification


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dataset", type=Path)
    p.add_argument("--rules", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    dataset = json.loads(a.dataset.read_text())
    rules = json.loads(a.rules.read_text())
    if dataset.get("is_demo", True) or not dataset.get("provenance") or not rules:
        raise ValueError("Non-demo labeled data and sourced rules required.")
    rows = dataset["test"]
    pred = [assess(r["caption"], r["hashtags"], rules)["level"] for r in rows]
    report = {
        "model": "sourced rule engine",
        "dataset": str(a.dataset),
        "dataset_version": hashlib.sha256(a.dataset.read_bytes()).hexdigest(),
        "rules_version": hashlib.sha256(a.rules.read_bytes()).hexdigest(),
        "parameters": {},
        "split": "test",
        "seed": None,
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "metrics": classification([r["risk_label"] for r in rows], pred),
        "environment": platform.python_version(),
        "notes": [
            "Macro metrics by risk level; binary violation recall requires a predeclared positive class."
        ],
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
