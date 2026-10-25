"""Deduplicate supplied captions and remove cross-split leakage without changing raw files."""

import csv, json, hashlib, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    out = ROOT / "data/splits/nlp"
    out.mkdir(parents=True, exist_ok=True)
    seen = set()
    report = {}
    for split, source in [("train", "train_nlp.csv"), ("validation", "val_nlp.csv")]:
        rows = []
        removed = 0
        with (ROOT / "data/raw/captions_hashtags" / source).open(
            encoding="utf-8-sig"
        ) as f:
            for row in csv.DictReader(f):
                key = re.sub(r"\s+", " ", row["clean_caption"]).strip().casefold()
                if not key or key in seen:
                    removed += 1
                    continue
                seen.add(key)
                rows.append(
                    {
                        "text": row["clean_caption"].strip(),
                        "hashtags": sorted(
                            set(
                                x.casefold()
                                for x in re.findall(r"#\w+", row["target_hashtags"])
                            )
                        ),
                    }
                )
        path = out / f"{split}.jsonl"
        path.write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8"
        )
        report[split] = {
            "rows": len(rows),
            "removed_empty_or_duplicate": removed,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    (out / "manifest.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
