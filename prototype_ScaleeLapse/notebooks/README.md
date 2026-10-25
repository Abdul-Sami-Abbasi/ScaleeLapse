# Research entry points

Experiments are executable scripts rather than notebooks with hidden cell state:

- `scripts/preprocessing/prepare_nlp.py`: deduplication and split hashes.
- `scripts/training/train_hashtags.py`: actual local transformer training and evaluation.
- `scripts/training/train_multimodal.py`: paired-data experiment, blocked until real pairs arrive.
- `scripts/evaluation/audit_images.py`: validation and palette processing.
- `scripts/evaluation/run_forecasting.py`: chronological ARIMA/Prophet comparison.
- `scripts/evaluation/evaluate_*.py`: real visual, compliance and SUS inputs.

Measured results are in `artifacts/experiments/` with interpretation in `docs/EXPERIMENTS.md`. Demo fixtures are never research observations. Optional exploratory notebooks can be added here when licensed, consented data is available.
