# Final readiness report

Date: 2026-10-01. Workspace: `C:\Users\prema\ScaleeLapse`.

**Overall: PARTIALLY READY.** The local application is runnable and the central demo workflow has been exercised with React, Django and PostgreSQL. The FYP's academic targets have not been established. READY below describes the stated implementation scope, not production certification or target accuracy.

| Major component | Classification | Verified scope / remaining dependency |
|---|---|---|
| Original-resource audit and preservation | READY | PDF and all 589 ZIP members inventoried; original archive preserved; 545 raw resources match hashes; cookies never reused. |
| Repository and local setup | READY | Python 3.12 core clean install/migrations/tests, npm installation/build and local startup script exercised. Source, fixtures, research artifacts and originals are separated. |
| PostgreSQL / Django REST | READY | PostgreSQL 17 running on loopback port 55432; migrations and 18 tests passed. SQLite fallback also verified. |
| Authentication, tenant access, roles | READY | Session auth, CSRF, hashed passwords, scoped resources, owner/admin/creator/reviewer permissions and protected uploads implemented. |
| Brand Kit and content management | READY | Kit CRUD, color roles, fonts, logos, validated image uploads, drafts, captions, manual planned dates and JSON/CSV exports. |
| O1 palette pipeline | READY | OpenCV/HSV/K-Means, color percentages, coverage score, batch processing and missing-kit status. 520/538 supplied image files processed; 18 rejected by validation/limits. This is coverage, not accuracy. |
| O1 research target / logo and font automation | BLOCKED | Official kits, 500 independently labeled images, logo/text boxes and trained detector weights absent. Font review is manual; image reuse is an exact-duplicate flag. No 90% accuracy or IoU claim. |
| O2 text transformer | PARTIALLY READY | Real DistilBERT fine-tuning completed and actual local inference/browser output verified. Deduplicated split: 3,889 train / 956 validation. Precision@10 is 1.18%; model is explicitly experimental and needs better data/training. |
| O2 proposal evaluation / multimodal extension | BLOCKED | More than 10,000 suitable pairs, SME relevance references and actual paired image/caption data missing. Offline ResNet-50/DistilBERT training code supplied but unrun. Supervisor must resolve hashtag classification versus BLEU generation scope. |
| O3 pre-publish risk assessment | PARTIALLY READY | Sourced-rule CRUD/import, normalization, severity, explanations, repetition heuristics and generated-tag filtering work. No sourced platform corpus was supplied; empty coverage and absent toxicity model are explicit. |
| O3 weekly refresh / 95% recall | BLOCKED | Authorized maintained policy source and independent violation labels required. Disabled n8n reminder is provided; automatic scraping/import and recall are not claimed. |
| O4 forecasting and analytics | PARTIALLY READY | Account isolation, ARIMA/Prophet, chronological holdout, chart/intervals, metrics and descriptive category/hour analysis work. Supplied-data normalized MAE: ARIMA 40.45%, Prophet 40.84%, above the proposed 15%. Provenance and denominator approval remain unresolved. |
| Independent human approval | READY | Draft → analysis → submission → separate review → approved → ready-to-publish verified in API tests and browser. Content/kit/policy changes invalidate evidence. Manual publishing only. |
| Frontend and integration | READY | Production build and seven tests passed. Browser image analysis, review decisions and forecast import completed against the real backend. |
| Synthetic demo | READY | Separate labeled organization/accounts and image/engagement fixtures. No synthetic metrics enter research evidence. |
| Documentation / report evidence | READY | Dataset dictionary, missing-data schemas, API/setup/user/developer/demo guides, methodology, experiments, eight Mermaid diagrams, viva notes and requirement traceability supplied. |
| Deployment beyond local environment | PARTIALLY READY | Docker/Compose/Nginx/Waitress definitions supplied. Docker runtime and public HTTPS deployment unverified; production hardening and operational testing remain. |
| Five-SME pilot / SUS ≥70 | BLOCKED | Real consented participants and responses missing. Questionnaire, collection guide and scorer exist; no participant or result fabricated. |

## Demonstration

Run `start.cmd`, then open `http://127.0.0.1:5173`. The Windows launcher was added on 2026-10-16 to support restricted PowerShell execution policies without persistent policy changes. The prepared demo accounts are `demo.owner`, `demo.creator`, and `demo.reviewer`, with local test password `ScaleeDemo!2026`. See `DEMO_GUIDE.md` for the sequence. Model weights and portable database are present locally but ignored by Git.

The browser-created post “SYNTHETIC DEMO · Browser workflow” was analyzed by `demo.owner`, submitted, approved by `demo.reviewer`, and marked ready. A synthetic forecast import is saved in the demo organization. These are demonstrations of application behavior only.

The desktop dashboard and forecast chart were inspected at 1920×1080. At a 390×844 mobile viewport, the dashboard had equal content and viewport widths (375 CSS pixels excluding the scrollbar), and the navigation opened correctly. Local screenshots are in `artifacts/browser/`. The services and saved PostgreSQL records were also recovered after the desktop session restarted, using the documented startup script.

## Actual experiment evidence

`artifacts/experiments/nlp_transformer.json` and `forecasting.json` contain measured results, configurations and dataset hashes. `EXPERIMENTS.md` explains low model quality and the forecasting target miss. The recorded transformer wall time includes an overnight pause and is not a compute-speed benchmark. Neither experiment has an untouched independent SME test set. Raw dataset source/license remains UNKNOWN.

## Inputs needed to complete academic claims

1. Owner-approved Brand Kits and independently annotated visual examples, including logo/text boxes.
2. Licensed/consented English caption-tag data meeting the proposal count, plus genuine image-caption pairs and SME relevance references.
3. Sourced policies, an authorized refresh source, and independent positive/negative violation labels.
4. Verified SME engagement exports and supervisor approval of the percentage-error definition.
5. Five real SME pilot participants, consent, completed SUS responses, and task notes.
6. Supervisor decision on the proposal's BLEU generation requirement versus multilabel hashtag classification; repair the proposal's incomplete citation.

Precise schemas and collection guidance are in `MISSING_DATA.md`. Templates are not collected evidence. Remaining progress depends on these inputs; presenting the existing demo as a fully validated academic system would be inaccurate.

## Delivery boundaries

No direct publishing, external messages, private account scraping or cloud deployment was performed. Local demo credentials are deliberately public test fixtures; the generated database password stays in ignored `.runtime/pgpass.txt`. Repository changes are local and uncommitted, with no remote publication. Original PDF/ZIP/raw data, model weights, uploads, runtime files and cookie archives are excluded from Git.
