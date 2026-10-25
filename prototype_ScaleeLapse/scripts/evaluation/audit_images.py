import sys, json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ai.brand_audit.engine import analyze

rows = []
for p in sorted((ROOT / "data/raw/brand_visual").rglob("*")):
    if p.suffix.lower() not in {".jpg", ".png", ".webp", ".jpeg"}:
        continue
    try:
        result = analyze(p.read_bytes(), [])
        rows.append(
            {
                "file": str(p.relative_to(ROOT)),
                "brand_folder": p.parent.name,
                "palette": result["palette"],
                "score": None,
            }
        )
    except ValueError as e:
        rows.append({"file": str(p.relative_to(ROOT)), "error": str(e)})
(ROOT / "data/processed/brand_palettes.json").write_text(json.dumps(rows, indent=2))
print(
    json.dumps(
        {
            "processed": len(rows),
            "valid": sum("palette" in r for r in rows),
            "errors": sum("error" in r for r in rows),
            "evaluation": "RESULT PENDING REAL EVALUATION: no official kits or labels.",
        }
    )
)
