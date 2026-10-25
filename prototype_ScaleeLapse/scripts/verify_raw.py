from pathlib import Path
import json, hashlib

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "project_context/raw_manifest.json").read_text())
errors = [
    name
    for name, sha in manifest.items()
    if not (root / name).exists()
    or hashlib.sha256((root / name).read_bytes()).hexdigest() != sha
]
if errors:
    raise SystemExit("Raw integrity failure: " + str(errors))
print(f"PASS: {len(manifest)} raw resources match the preserved SHA-256 manifest.")
