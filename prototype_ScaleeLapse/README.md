# ScaleeLapse

AI-powered visual compliance and content operations workspace for SMEs. React frontend, Django REST backend, PostgreSQL, local Python ML and an independent human approval workflow. Instagram/Facebook planning only; no automatic social publishing.

**Readiness: functional local application; academic objectives are partially ready.** A real trained DistilBERT artifact and actual ARIMA/Prophet experiment results exist locally, but their quality does not establish the proposal targets. Official Brand Kits, labeled visual/risk datasets, paired multimodal inputs and real SME pilot responses are still required. Read `docs/FINAL_READINESS_REPORT.md` and `docs/MISSING_DATA.md` before presenting results.

## Open this prepared workspace

On this computer, Python dependencies, frontend packages and portable PostgreSQL have been installed inside the project. Double-click `start.cmd` in this folder, or start local services from PowerShell with:

```powershell
.\start.cmd
```

The launcher permits the included PowerShell script only in its child process; it does not change the machine or user execution policy and does not require an administrator account. If running `scripts/start.ps1` directly reports “running scripts is disabled,” use `start.cmd`, or run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

Organization-enforced Group Policy can override this process setting; on a managed computer, ask the administrator if the launcher is still blocked.

Open **http://127.0.0.1:5173**. The prepared database is PostgreSQL 17 on `127.0.0.1:55432`. Its local-only password is in ignored `.runtime/pgpass.txt`. Do not publish `.runtime`, `media`, or original datasets.

Synthetic demo accounts: `demo.owner`, `demo.creator`, `demo.reviewer`. The prepared demo password is `ScaleeDemo!2026`. These are deliberately public local test credentials, never production accounts. The workspace is visibly labeled **SYNTHETIC DEMO DATA**. Change or remove demo accounts before exposing the service beyond localhost. You can also register a separate empty organization.

## Fresh local setup

Use Python 3.12 and Node.js 22 or 24. In the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe backend/manage.py migrate
.\.venv\Scripts\python.exe backend/manage.py runserver 127.0.0.1:8000
```

In another terminal:

```powershell
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run dev
```

These Windows commands avoid PowerShell activation and npm script wrappers, so they also work with the default restricted script policy.

Without PostgreSQL environment variables this uses **SQLite for local fallback**. For PostgreSQL configure POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER and POSTGRES_PASSWORD before migrations. The normal Django command does not load `.env` automatically. `scripts/serve_backend.py` detects the prepared project-local PostgreSQL credentials; `SCALEELAPSE_SQLITE=1` opts out.

To add synthetic demo records on a fresh database:

```powershell
$env:DEMO_PASSWORD='choose-a-local-demo-password'
python backend/manage.py seed_demo
```

## Docker target

```powershell
Copy-Item .env.example .env
# Edit .env with unique secrets and passwords.
docker compose up --build
```

Open http://localhost:8080. Compose includes Nginx/React, Waitress/Django and PostgreSQL with persistent volumes. Docker was not available in the authoring environment, so its runtime verification is pending. See `docs/DEPLOYMENT.md` for HTTPS and production settings.

## ML and supplied resources

Core requirements run OpenCV, rule assessment and ARIMA. For local transformer training/inference and Prophet:

```powershell
python -m pip install -r requirements-ml.txt
python scripts/preprocessing/prepare_nlp.py
python scripts/training/train_hashtags.py --epochs 1
python scripts/evaluation/run_forecasting.py
```

The prepared `models/hashtag_transformer` contains the actual local trained artifact and evaluation manifest. It is ignored by Git and must be transferred separately with rights/provenance reviewed. Without a compatible artifact/runtime, the UI explicitly shows keyword-only assistance. CPU training defaults to the last DistilBERT block and head; `--full-finetune` enables full fine-tuning. The initial model has low validation quality and is experimental.

The original PDF/ZIP remain in `project_context`. The ZIP was safely extracted to `project_context/archive_original`, and raw bytes copied under `data/raw`. Archive cookies are never reused. Data licenses/provenance are UNKNOWN. Supplied scraping code is preserved but was not run. Cleaned NLP splits and palette outputs are separate.

```powershell
python scripts/verify_raw.py
python scripts/evaluation/audit_images.py
python -m pytest -q
npm --prefix frontend test
npm --prefix frontend run build
```

## What you can demonstrate

Register/login → manage Brand Kit → create/upload/analyze → inspect palette, experimental tags and sourced risk → submit → independent reviewer approves → mark ready to publish. Upload account-specific engagement CSVs to see history, forecast intervals, category associations and actual held-out errors. Planned dates support manual publishing. Brand/policy/content edits invalidate old analysis.

Use `data/demo/synthetic-post.png` and `data/demo/synthetic-engagement.csv` for application testing only. The real supplied CSV under `data/raw/engagement` contains multiple accounts; specify account ID (e.g. 7) and describe its unverified provenance. Never treat the demo as research evidence.

## Documentation

- `docs/DEMO_GUIDE.md`, `USER_MANUAL.md`, `API.md`, `DEVELOPER_GUIDE.md`
- `docs/DATASETS.md`, `DATA_DICTIONARY.md`, `MISSING_DATA.md`
- `docs/METHODOLOGY.md`, `EXPERIMENTS.md`, `TESTING.md`
- `docs/ARCHITECTURE.md`, `REQUIREMENTS_TRACEABILITY.md`, `diagrams/`
- `docs/BUILD_STATUS.md`, `FINAL_READINESS_REPORT.md`, `LIMITATIONS.md`
- `docs/SME_DATA_COLLECTION_GUIDE.md`, `SUS_QUESTIONNAIRE.md`, `REPORT_EVIDENCE.md`, `VIVA_GUIDE.md`

No accuracy, BLEU, compliance recall or SUS target is claimed without its required real evaluation.
