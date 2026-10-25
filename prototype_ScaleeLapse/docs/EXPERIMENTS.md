# Executed experiments and pending evidence

## DistilBERT multilabel run
Artifact: `artifacts/experiments/nlp_transformer.json`; model: `models/hashtag_transformer`; date 2026-10-01 UTC. Seed 42; one epoch; batch 16; maximum text length 64; minimum training-label frequency 5. Encoder frozen except final transformer block, plus trained classification head. Raw duplicate captions removed across splits: 3,889 train, 956 validation. Exact hashes are in the manifest.

Observed Precision@10 = 0.0118201; retained-vocabulary Recall@10 = 0.0876046; micro-F1 = 0.0224741. Recall@10 across all reference labels = 0.0600780. Validation label coverage = 0.265383. These results are poor and expose general-domain/rare-label limitations. No untouched test set, SME generalization, 10,000-pair target, BLEU target, or relevant-ten-tag guarantee is established. Loss reduction alone is not recommendation quality.

Recorded wall time includes the overnight paused/sleep interval in this desktop session; it must not be reported as pure compute time. Use the recorded environment and configurations for reproducibility, not a runtime-performance claim.

## Forecasting on supplied records
Artifact: `artifacts/experiments/forecasting.json`. Account 7, likes, daily observed means, earlier 80% train/later 20% test, 72 observed held-out dates beginning 2025-09-07. Seven-day future forecast refits on full history.

| Model | MAE (likes) | RMSE (likes) | Normalized MAE |
|---|---:|---:|---:|
| ARIMA(1,1,1) | 119.8618 | 163.7431 | 40.4533% |
| Prophet | 121.0151 | 164.1050 | 40.8425% |

Normalized MAE divides MAE by mean absolute held-out likes. The proposal's ≤15% target is not met by this run under that definition; the supervisor must approve the percentage interpretation. Data source/license and real-world origin remain UNKNOWN. These are actual computations, not verified SME impact results.

## Visual processing run
`data/processed/brand_palettes.json`: all 538 supplied files attempted; 520 processed, 18 rejected by validation/size limits. This is pipeline coverage, not accuracy. No official kits or labels were supplied. Palette accuracy/confusion matrix/YOLO IoU: **RESULT PENDING REAL EVALUATION**.

## Compliance and usability
Unit tests exercise synthetic terms and decisions. They do not estimate recall on platform violations. No real labeled compliance corpus or SUS participants supplied: **RESULT PENDING REAL EVALUATION**.

## Reproduction and recording
Run scripts in `scripts/preprocessing`, `scripts/training`, `scripts/evaluation`. Preserve input hashes, model version, parameters, split, seed, date, metrics, environment and notes. Do not overwrite earlier configurations when comparing experiments; copy or name each run distinctly. Keep demo imports outside research artifacts. Templates do not count as collected data.
