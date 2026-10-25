# Developer guide

Entry points: `backend/manage.py`, `backend/config/settings.py`, `frontend/src/main.jsx`. Domain ORM lives in `backend/core/models.py`, validation in `serializers.py`, orchestration/permissions in `views.py`. AI engines are pure service modules under `ai/`.

Run migrations before starting. Test Python with `python -m pytest -q`; frontend with `npm --prefix frontend test`; bundle with `npm --prefix frontend run build`. Windows sandbox process restrictions may require approved execution of Node build workers. Do not weaken application permissions to work around an execution sandbox.

Prepare captions with `python scripts/preprocessing/prepare_nlp.py`. Install optional requirements before `python scripts/training/train_hashtags.py`. Model output is `models/hashtag_transformer`; provenance/metrics go to `artifacts/experiments/nlp_transformer.json`. Never build vocabulary from validation. Paired-image experiments use `ai/nlp/multimodal.py` and the annotation manifest template.

`scripts/evaluation/run_forecasting.py` evaluates account 7, likes, chronological split on supplied data and records limitations. `scripts/evaluation/audit_images.py` extracts palettes with null brand scores. `scripts/evaluation/evaluate.py` accepts real truth/prediction labels with provenance and rejects missing/demo provenance. `scripts/verify_raw.py` verifies protected raw copies.

Never log passwords, caption bodies, image bytes or cookies. Audit events record actor/action/object/time. Adding new endpoints requires organization scoping and explicit role tests. Any material content/kit/policy change must invalidate stale review decisions or require reassessment.

The original archive contains legacy preprocessing and a scraper. Preserve them as evidence; do not execute the scraper or reuse cookies. The original forecasting projection loses account identity and is superseded by `ai/forecasting/engine.py`.
