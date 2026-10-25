import sys, json, hashlib, platform, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ai.forecasting.engine import forecast

if __name__ == "__main__":
    path = ROOT / "data/raw/engagement/Instagram_Analytics.csv"
    data = path.read_bytes()
    reports = []
    for model in ["arima", "prophet"]:
        try:
            result = forecast(data, "likes", "7", model, 7)
            reports.append(
                {
                    "model": model,
                    "dataset": str(path.relative_to(ROOT)),
                    "dataset_version": hashlib.sha256(data).hexdigest(),
                    "parameters": {
                        "account_id": "7",
                        "metric": "likes",
                        "horizon": 7,
                        "aggregation": "daily observed mean",
                    },
                    "split": "chronological 80/20",
                    "seed": None,
                    "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "metrics": result["evaluation"],
                    "environment": platform.python_version(),
                    "notes": [
                        "Dataset provenance and license UNKNOWN. Results describe this supplied file only.",
                        "No claim of real SME data or proposal target achieved.",
                    ],
                    "result": result,
                }
            )
        except Exception as e:
            reports.append({"model": model, "status": "BLOCKED", "reason": str(e)})
    out = ROOT / "artifacts/experiments/forecasting.json"
    out.write_text(json.dumps(reports, indent=2))
    print(
        json.dumps(
            [{k: v for k, v in r.items() if k != "result"} for r in reports], indent=2
        )
    )
