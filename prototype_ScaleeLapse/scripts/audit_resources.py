"""Read and inventory provided resources; copy raw bytes without transformations."""

from pathlib import Path
import csv, hashlib, json, shutil, collections
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "project_context/archive_original/ScaleeLapse-main"


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    inventory = []
    for p in sorted(SOURCE.rglob("*")):
        if not p.is_file():
            continue
        inventory.append(
            {
                "path": str(p.relative_to(SOURCE)),
                "bytes": p.stat().st_size,
                "sha256": digest(p),
            }
        )
    mappings = [
        ("data/raw/brandimages", "data/raw/brand_visual"),
        (
            "data/raw/Instagram_Analytics.csv",
            "data/raw/engagement/Instagram_Analytics.csv",
        ),
        ("data/processed/nlp", "data/raw/captions_hashtags"),
        ("data/processed/forecasting", "data/raw/provided_forecasting"),
    ]
    for src, dst in mappings:
        p, q = SOURCE / src, ROOT / dst
        if p.is_dir():
            shutil.copytree(p, q, dirs_exist_ok=True)
        else:
            q.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, q)
    audit = {"files": inventory, "csv": {}, "images": {}, "licenses": "UNKNOWN"}
    for p in (ROOT / "data/raw").rglob("*.csv"):
        with p.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            cols = reader.fieldnames
        audit["csv"][str(p.relative_to(ROOT))] = {
            "rows": len(rows),
            "bytes": p.stat().st_size,
            "columns": cols,
            "nulls": {c: sum(not r[c] for r in rows) for c in cols},
            "duplicate_rows": len(rows) - len({tuple(r.values()) for r in rows}),
            "sha256": digest(p),
        }
        if "target_hashtags" in cols:
            audit["csv"][str(p.relative_to(ROOT))]["label_counts"] = dict(
                collections.Counter(
                    t.lower() for r in rows for t in r["target_hashtags"].split()
                ).most_common()
            )
    hashes = collections.defaultdict(list)
    bad = []
    counts = collections.Counter()
    for p in (ROOT / "data/raw/brand_visual").rglob("*"):
        if p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        counts[p.parent.name] += 1
        hashes[digest(p)].append(str(p.relative_to(ROOT)))
        try:
            with Image.open(p) as im:
                im.verify()
        except Exception as e:
            bad.append({"file": str(p.relative_to(ROOT)), "error": str(e)})
    audit["images"] = {
        "count": sum(counts.values()),
        "classes": dict(counts),
        "invalid": bad,
        "duplicate_groups": [v for v in hashes.values() if len(v) > 1],
    }
    sets = []
    for name in ["train_nlp.csv", "val_nlp.csv"]:
        with (ROOT / "data/raw/captions_hashtags" / name).open(encoding="utf-8") as f:
            sets.append({r["clean_caption"].strip().lower() for r in csv.DictReader(f)})
    audit["nlp_caption_overlap"] = len(sets[0] & sets[1])
    (ROOT / "project_context/resource_inventory.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    (ROOT / "project_context/raw_manifest.json").write_text(
        json.dumps(
            {
                str(p.relative_to(ROOT)): digest(p)
                for p in (ROOT / "data/raw").rglob("*")
                if p.is_file()
            },
            indent=2,
        )
    )
    print(
        json.dumps(
            {k: v for k, v in audit.items() if k not in ["files", "csv"]}, indent=2
        )
    )
    print([(k, v["rows"], v["duplicate_rows"]) for k, v in audit["csv"].items()])


if __name__ == "__main__":
    main()
