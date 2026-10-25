# Verification record

Verified on 2026-10-01 in the prepared Windows workspace. Test fixtures and browser demo records are synthetic and do not estimate academic model quality.

## Automated checks

| Check | Observed result | Evidence |
|---|---|---|
| Python application/engine suite on PostgreSQL 17 | 18 passed | `artifacts/tests-postgresql.xml` |
| Fresh Python 3.12 core environment | Requirements installation, SQLite migrations and 18 tests passed without optional transformer/Prophet packages | `artifacts/tests-clean-install.xml` |
| Frontend API/component tests | 7 passed, including preserving a planned instant during caption edits | `frontend/src/api.test.js`, `workflow.test.jsx` |
| Frontend production build | Passed; application and chart bundles generated | `frontend/dist/` (local generated output) |
| Migration drift | No changes detected | `manage.py makemigrations --check --dry-run` |
| Python syntax and undefined-name check | Passed | `compileall`; Ruff E9/F821 |
| npm dependency audit | 0 reported vulnerabilities at verification time | `npm audit` |
| Raw integrity | 545 of 545 resources matched recorded SHA-256 hashes | `scripts/verify_raw.py`, `project_context/raw_manifest.json` |

The core lock pins direct dependencies; frontend `package-lock.json` includes resolved transitive dependencies. The clean Python verification uses `.venv-verify`, while the prepared ML environment uses `.venv312`. The final PostgreSQL run reports 13 warnings: NumPy/statsmodels deprecations and initial ARIMA parameter warnings. All assertions passed; these warnings are not suppressed or evidence of forecast reliability.

The Python tests cover palette coverage/hue wrap/missing kits, invalid images and isolated batch errors, Unicode policy matching, repetition warnings, missing-model fallback, chronological forecast errors, invalid histories, evaluation calculations, registration/session/CSRF, tenant separation, upload roles, full review transitions, exports, change requests, and invalidation after kit/policy edits. They are functional tests, not an exhaustive penetration or load test.

## Browser verification

At `http://127.0.0.1:5173`, with the actual Django server and PostgreSQL:

1. Signed in with the synthetic owner account and opened the dashboard.
2. Created a synthetic post, uploaded `data/demo/synthetic-post.png`, and ran real palette, local transformer and rule assessment.
3. Confirmed color coverage, ten experimental model predictions, the measured model-quality notice, duplicate-hashtag risk, and explicit missing logo/font/toxicity evidence.
4. Submitted the post. Signed out, signed in as the independent reviewer, recorded a review comment, approved it, and marked it ready to publish. Review history retained all decisions. No publishing integration was called.
5. Signed back in as the owner; imported `data/demo/synthetic-engagement.csv` with provenance and the synthetic flag. ARIMA produced a saved forecast, history/interval chart, 60 observed days, 12 held-out dates, and metrics. Those demo metrics are excluded from experiment results.

Screenshots are local evidence under ignored `artifacts/browser/`. Full-HD (1920×1080) dashboard/forecast and mobile (390×844) dashboard/navigation were inspected. Mobile document width equaled the viewport client width, with no page overflow. Services and saved records were restored after a desktop restart using `scripts/start.ps1`. Final state is recorded in `FINAL_READINESS_REPORT.md`.

## Re-run

```powershell
.venv312\Scripts\python.exe -m pytest -q --junitxml=artifacts/tests.xml
npm --prefix frontend test
npm --prefix frontend run build
.venv312\Scripts\python.exe scripts/verify_raw.py
```

Default tests use SQLite. To run on PostgreSQL, set `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` in the process environment first; never commit or print the password. Tests create and destroy a separate test database and require the local test role to have database-creation permission. Use a dedicated environment, never a production database.

## Limits

Docker execution is unverified because Docker is absent. No public HTTPS deployment, real social-account integration, production load test, external policy refresh, logo detector evaluation, multimodal experiment, independent research test set, or real SME usability pilot was executed. Browser checks cover the central demo flow rather than every possible interaction.
