import argparse, csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.evaluation.evaluate import sus


def main():
    p = argparse.ArgumentParser()
    p.add_argument("responses", type=Path)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    with a.responses.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or any(not r["consent_reference"] for r in rows):
        raise ValueError("Actual consented participant responses are required.")
    ids = [r["participant_id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate participant IDs must be resolved.")
    scores = [sus([int(r[f"q{i}"]) for i in range(1, 11)]) for r in rows]
    result = {
        "participants": len(rows),
        "organizations": len({r["organization_id"] for r in rows}),
        "mean_sus": sum(scores) / len(scores),
        "scores": dict(zip(ids, scores)),
        "notes": "Verify recruitment and consent; no inference to all SMEs.",
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
