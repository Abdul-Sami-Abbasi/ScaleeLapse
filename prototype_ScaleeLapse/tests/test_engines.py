import io
import numpy as np
import pandas as pd
import pytest
from PIL import Image
from ai.brand_audit.engine import analyze, hex_hsv, hsv_distance, batch
from ai.compliance.engine import assess, normalize
from ai.nlp.engine import preprocess, recommend
from ai.forecasting.engine import forecast, read_history


def picture(color="red"):
    b = io.BytesIO()
    Image.new("RGB", (80, 80), color).save(b, "PNG")
    return b.getvalue()


def history(n=50):
    return (
        pd.DataFrame(
            {
                "post_datetime": pd.date_range("2025-01-01", periods=n),
                "likes": 100 + np.arange(n) * 2 + np.sin(np.arange(n)) * 3,
            }
        )
        .to_csv(index=False)
        .encode()
    )


def test_hex_and_hue_wrap():
    assert np.allclose(hex_hsv("#FF0000"), [0, 1, 1])
    assert hsv_distance(np.array([0.99, 1, 1]), np.array([0.01, 1, 1])) < 0.03
    with pytest.raises(ValueError):
        hex_hsv("red")


def test_color_coverage_and_missing_kit():
    r = analyze(picture(), [{"hex": "#FF0000", "role": "PRIMARY"}])
    assert r["score"] == 100
    assert r["palette"][0]["percentage"] == 100
    assert analyze(picture(), [{"hex": "#0000FF", "role": "PRIMARY"}])["score"] == 0
    assert analyze(picture(), [])["score"] is None
    assert analyze(picture(), [])["logo"]["status"] == "NOT_EVALUATED"


def test_mixed_palette():
    im = Image.new("RGB", (100, 100), "red")
    im.paste("blue", (0, 0, 50, 100))
    b = io.BytesIO()
    im.save(b, "PNG")
    result = analyze(b.getvalue(), [{"hex": "#FF0000", "role": "PRIMARY"}])
    assert result["score"] == 50
    assert len(result["palette"]) == 2


def test_batch_error_isolation():
    r = batch([("valid", picture()), ("invalid", b"not image")], [])
    assert "result" in r[0] and "error" in r[1]


def test_rules_normalize_and_boundaries():
    rule = {
        "term": "test",
        "kind": "HASHTAG",
        "severity": "HIGH",
        "explanation": "Test fixture only",
        "source": "Synthetic unit test",
    }
    assert assess("caption", ["#TEST"], [rule])["level"] == "HIGH"
    assert assess("caption", ["#testing"], [rule])["level"] == "LOW"
    assert normalize("＃ＴＥＳＴ") == "test"
    assert assess("caption", ["#ok", "#ok"], [])["level"] == "MEDIUM"
    assert assess("caption", [], [])["coverage"] == "NO_SOURCED_RULES"


def test_nlp_unavailable_is_explicit():
    assert preprocess("Hello #World https://example.com") == "Hello"
    r = recommend("Coffee roasting stories", "models/nonexistent_test_model")
    assert r["status"] == "MODEL_REQUIRED"
    assert "#coffee" in r["hashtags"]
    with pytest.raises(ValueError):
        recommend("#only", "models/nonexistent_test_model")


def test_forecast_real_holdout_calculation():
    r = forecast(history())
    assert len(r["forecast"]) == 7
    assert r["evaluation"]["test_observations"] == 10
    diffs = np.array([h["actual"] - h["predicted"] for h in r["holdout"]])
    assert r["evaluation"]["mae"] == pytest.approx(np.abs(diffs).mean())
    assert r["holdout"][0]["date"] > r["history"][39]["date"]


def test_csv_validation():
    with pytest.raises(ValueError):
        read_history(b"x,y\n1,2")
    with pytest.raises(ValueError):
        read_history(history(10))
    df = pd.read_csv(io.BytesIO(history()))
    df.loc[2, "likes"] = np.inf
    with pytest.raises(ValueError):
        read_history(df.to_csv(index=False).encode())
    df = pd.read_csv(io.BytesIO(history()))
    df["account_id"] = [1, 2] * 25
    with pytest.raises(ValueError, match="multiple accounts"):
        read_history(df.to_csv(index=False).encode())


def test_missing_dates_not_filled_with_future():
    df = pd.read_csv(io.BytesIO(history()))
    df = df.drop([5, 6, 44])
    r = forecast(df.to_csv(index=False).encode())
    assert r["eda"]["missing_days"] == 3
    assert r["history"][5]["value"] is None
