import io
import numpy as np
import pandas as pd

METRICS = {
    "likes",
    "comments",
    "shares",
    "saves",
    "reach",
    "impressions",
    "follower_count",
    "engagement_rate",
}


def read_history(data, metric="likes", account=None):
    if metric not in METRICS:
        raise ValueError("Choose a supported engagement metric.")
    if len(data) > 10 * 1024 * 1024:
        raise ValueError("CSV exceeds 10 MB.")
    try:
        df = pd.read_csv(io.BytesIO(data))
    except Exception as e:
        raise ValueError("Could not read CSV. Use UTF-8 with a header row.") from e
    if len(df) > 100000:
        raise ValueError("CSV exceeds 100,000 rows.")
    df.columns = df.columns.str.strip().str.lower()
    date = next(
        (c for c in ["post_datetime", "post_date", "ds", "date"] if c in df), None
    )
    if not date or metric not in df:
        raise ValueError(f"CSV needs post_datetime or date, and {metric}.")
    if "account_id" in df:
        if account is not None:
            df = df[df.account_id.astype(str) == str(account)].copy()
        elif df.account_id.nunique() > 1:
            raise ValueError(
                "CSV contains multiple accounts. Specify account_id to avoid mixing unrelated histories."
            )
    if df.empty:
        raise ValueError("No rows for the selected account.")
    df["ds"] = pd.to_datetime(df[date], errors="coerce", utc=True, format="mixed")
    df["y"] = pd.to_numeric(df[metric], errors="coerce")
    invalid = df.ds.isna() | df.y.isna() | ~np.isfinite(df.y) | (df.y < 0)
    if invalid.any():
        raise ValueError(
            f"{int(invalid.sum())} rows have invalid dates, missing, negative or non-finite values; correct them before importing."
        )
    if df.duplicated().any():
        df = df.drop_duplicates()
    df = df.sort_values("ds")
    # Mean per observed day avoids assuming zero engagement on missing days.
    daily = df.groupby(df.ds.dt.floor("D")).y.mean().sort_index()
    if len(daily) < 20:
        raise ValueError("At least 20 distinct observed days are required.")
    series = daily.asfreq("D")
    if len(series) > 3660:
        raise ValueError("History exceeds the 10-year daily range limit.")
    categories = (
        df.groupby("content_category")
        .y.agg(["mean", "count"])
        .reset_index()
        .to_dict("records")
        if "content_category" in df
        else []
    )
    periods = (
        df.groupby(df.ds.dt.hour)
        .y.agg(["mean", "count"])
        .reset_index()
        .rename(columns={"ds": "hour"})
        .to_dict("records")
    )
    return series, {
        "source_rows": len(df),
        "observed_days": len(daily),
        "missing_days": int(series.isna().sum()),
        "categories": categories,
        "periods": periods,
    }


def forecast(data, metric="likes", account=None, model="arima", horizon=7):
    if model not in {"arima", "prophet"}:
        raise ValueError("Model must be arima or prophet.")
    if not 1 <= horizon <= 60:
        raise ValueError("Forecast horizon must be 1 to 60 days.")
    series, eda = read_history(data, metric, account)
    cut = int(len(series) * 0.8)
    train = series.iloc[:cut]
    test = series.iloc[cut:]
    if train.notna().sum() < 10 or test.notna().sum() < 3:
        raise ValueError("Need at least 10 observed training days and 3 held-out days.")

    # Training-only forward fill prevents look-ahead leakage.
    def fit_predict(s, n):
        if model == "arima":
            from statsmodels.tsa.arima.model import ARIMA

            fit = ARIMA(s.ffill(), order=(1, 1, 1), enforce_stationarity=False).fit()
            pred = fit.get_forecast(n)
            ci = np.asarray(pred.conf_int())
            return np.asarray(pred.predicted_mean), ci[:, 0], ci[:, 1]
        try:
            from prophet import Prophet
        except ImportError as e:
            raise ValueError(
                "Prophet is optional and is not installed. Install requirements-ml.txt or choose ARIMA."
            ) from e
        frame = pd.DataFrame({"ds": s.index.tz_localize(None), "y": s.values}).dropna()
        fit = Prophet(daily_seasonality=False, yearly_seasonality=False).fit(frame)
        pred = fit.predict(
            pd.DataFrame(
                {
                    "ds": pd.date_range(
                        s.index[-1].tz_localize(None) + pd.Timedelta(days=1), periods=n
                    )
                }
            )
        )
        return pred.yhat.values, pred.yhat_lower.values, pred.yhat_upper.values

    prediction, _, _ = fit_predict(train, len(test))
    mask = test.notna().values
    residual = test.values[mask] - prediction[mask]
    mean_abs = float(np.abs(test.values[mask]).mean())
    metrics = {
        "mae": float(np.abs(residual).mean()),
        "rmse": float(np.sqrt((residual**2).mean())),
        "normalized_mae_percent": float(np.abs(residual).mean() / mean_abs * 100)
        if mean_abs
        else None,
        "test_observations": int(mask.sum()),
        "split_date": str(test.index[0].date()),
    }
    values, low, high = fit_predict(series, horizon)
    if not np.all(np.isfinite(values)):
        raise ValueError("Model failed to produce finite forecasts; review history.")
    return {
        "model": model,
        "metric": metric,
        "aggregation": "Mean per observed day; training-only forward fill",
        "eda": eda,
        "evaluation": metrics,
        "history": [
            {"date": str(d.date()), "value": None if pd.isna(v) else float(v)}
            for d, v in series.items()
        ],
        "holdout": [
            {
                "date": str(d.date()),
                "actual": None if pd.isna(v) else float(v),
                "predicted": float(p),
            }
            for (d, v), p in zip(test.items(), prediction)
        ],
        "forecast": [
            {
                "date": str(d.date()),
                "value": float(v),
                "lower": float(l),
                "upper": float(u),
            }
            for d, v, l, u in zip(
                pd.date_range(series.index[-1] + pd.Timedelta(days=1), periods=horizon),
                values,
                low,
                high,
            )
        ],
        "notes": "Associations are descriptive, not causal. Intervals are model-based uncertainty and may extend below zero.",
    }
