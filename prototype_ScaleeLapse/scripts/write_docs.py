"""Generate factual documentation from the preserved inventory and implementation."""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs"
DOC.mkdir(exist_ok=True)


def write(name, text):
    (DOC / name).write_text(text.strip() + "\n", encoding="utf-8")


audit = json.loads(
    (ROOT / "project_context/resource_inventory.json").read_text(encoding="utf-8")
)
write(
    "DATASETS.md",
    """# Dataset audit

Original archive: `project_context/ScaleeLapse-main.zip`. It is retained byte-for-byte. Extracted originals remain under `project_context/archive_original`; useful resources are copied under `data/raw`. `resource_inventory.json` contains every file, size and SHA-256. `raw_manifest.json` protects the working raw copies.

| Dataset | Rows / files | Exact duplicate rows | Status | License |
|---|---:|---:|---|---|
"""
    + "\n".join(
        f"| `{name}` | {v['rows']} | {v['duplicate_rows']} | Supplied, unverified provenance | UNKNOWN |"
        for name, v in audit["csv"].items()
    )
    + """
| Brand images | 538 in 36 folders | One byte-identical pair | 532 decode; 6 invalid | UNKNOWN |

Image folder names are collection categories, not verified brand labels or compliance ground truth. No owner-provided palettes, logo boxes, font annotations, or consent records are supplied. `bata` has 13 images; other folders have 15 each. The duplicate pair crosses hemani and tapal. See the inventory for paths of all failures.

NLP supplied extraction script names `kkcosmos/instagram-images-with-captions` as its upstream source. This is a provenance clue, not proof of license or consent. The provided rows have original captions, cleaned captions and extracted hashtag targets. These are observational tags, not expert judgments of relevance. They include non-English content and celebrity/general-domain posts. The raw train/validation files share 33 normalized captions. New splits remove caption duplicates and cross-split leakage, preserving 3,889 training and 956 validation rows. The original 5,005 rows do not satisfy the proposal's >10,000 target.

Engagement data contains 29,999 rows and multiple account IDs. Its generator/source/license is UNKNOWN; it must not be described as real SME participation. The supplied forecasting preprocessing script can fall back to the first numeric column and ignores account boundaries. Its output loses account identity, so it is preserved but superseded. Forecasting uses the richer original CSV, explicit metric selection and account filtering.

The image scraper is retained for inspection only and was not executed. Its searches do not establish ownership or permission. Archived cookies are excluded from the app, source-control candidates and documentation content. No new scraping occurs.

Raw integrity: run `python scripts/verify_raw.py`. Processed palettes and deduplicated NLP splits are separate. Research reuse and redistribution require license/consent confirmation.
""",
)
write(
    "DATA_DICTIONARY.md",
    "# Data dictionary\n\n"
    + "\n\n".join(
        "## "
        + name
        + "\n\n| Column | Missing values | Meaning |\n|---|---:|---|\n"
        + "\n".join(
            f"| {c} | {v['nulls'][c]} | "
            + (
                {
                    "caption": "Original supplied caption",
                    "clean_caption": "Caption after supplied hashtag/URL removal",
                    "target_hashtags": "Space-delimited observed hashtag labels",
                    "ds": "Date supplied by legacy preprocessing",
                    "y": "Legacy engagement target; use original CSV instead",
                    "account_id": "Account grouping identifier; filter before forecasting",
                    "post_datetime": "Posting timestamp; parsed UTC",
                    "engagement_rate": "Provided rate; denominator/source not verified",
                    "performance_bucket_label": "Provided bucket, not independently validated",
                }.get(
                    c,
                    "Supplied "
                    + c.replace("_", " ")
                    + " field; provenance not independently verified",
                )
            )
            + " |"
            for c in v["columns"]
        )
        for name, v in audit["csv"].items()
    )
    + """

## Application records

`BrandColor.hex`: six-digit sRGB HEX. `role`: PRIMARY, SECONDARY or BACKGROUND. `tolerance`: normalized circular-HSV distance in [0.01, 0.5]. `kit_source`: owner guideline provenance, not automatically verified. `fonts`: names for human checking.

`Post.status`: DRAFT, ANALYZING, READY_FOR_REVIEW, CHANGES_REQUIRED, APPROVED, READY_TO_PUBLISH. `scheduled_at` is a planning timestamp, not an API publishing instruction. `Media.sha256` supports exact-image reuse flags. Image bytes are validated and re-encoded.

Analysis JSON retains palette weights, score, methods, warnings and coverage. A null score means no approved colors. NOT_EVALUATED is not a detection result. MODEL_REQUIRED denotes keyword-only assistance. Rules preserve source, severity, platform, explanation and review timestamp. Forecast imports retain a source hash and provenance plus aggregated history; synthetic provenance is explicitly recorded.
""",
)
write(
    "MISSING_DATA.md",
    """# Missing data and academic decisions

| Missing item | Objective / purpose | Schema / minimum guidance | Collection path |
|---|---|---|---|
| Official owner-approved Brand Kits | O1 palette ground truth | brand ID, kit version, HEX colors by role, logo, approved fonts, owner approval | Ask participating SMEs for written guidelines; never infer a kit from a name |
| Labeled visual evaluation | O1 90% target on 500 images | image path, kit ID/version, binary consistency label, annotator, split; 500 independently reviewed examples per proposal | Consent and double annotation; adjudicate disagreements; separate near duplicates before splitting |
| Logo/text boxes and valid detector weights | O1 YOLO/IoU | image, class, xyxy boxes, annotator, split; amount depends on variation | Annotate enough independent positive/negative cases; generic YOLO weights cannot validate SME logos |
| More English caption/hashtag pairs | O2 training | text, observed tags, source, consent, account/group IDs; >10,000 proposal target | Licensed or owner-consented exports; retain grouping identifiers to prevent author leakage |
| Image-caption pairing | O2 multimodal experiment | image_path, caption, tags, source/group ID, consent, split | Export the actual image paired with each caption; don't pair unrelated supplied corpora |
| Relevance references and formulation approval | O2 BLEU ≥0.45 | Human ordered generated sequences if generation is retained; or supervisor approval for set-based Precision@K/Recall@K/F1 | Multilabel sets have no meaningful reference word order. Do not present set metrics as satisfying BLEU |
| Sourced policy terms and labeled examples | O3 recall ≥95% | term, kind, severity, platform, explanation, source URL/version, review date; caption/tags and expert labels | Use authorized published sources and policy reviewers, including positives and negatives; select sample size for desired confidence intervals |
| Authorized refresh source | O3 weekly n8n updates | Approved endpoint/source contract, access method and review process | Owner/supervisor approves source and collection permissions before automation activation |
| Verified SME engagement exports | O4 | account ID, timestamp, metric, category, provenance; ≥20 observed days computational minimum, preferably months of regular data | Consented account exports; 20 days is not evidence of forecasting reliability |
| Meaning of MAE ≤15% | O4 target interpretation | Supervisor-approved denominator | This implementation reports MAE in metric units and normalized MAE = MAE / mean absolute held-out value ×100 |
| Five SME pilot participants | Usability | consent, anonymized organization/participant ID, 10 SUS answers, task notes | Recruit at least five real SMEs/agencies per proposal; never create responses |

Annotation/import templates are in `data/annotations`. All unresolved academic target claims: **RESULT PENDING REAL EVALUATION**. Source citations in the proposal are not independently validated; reference [4] contains an author placeholder and must be repaired by the student with a verifiable source.
""",
)
write(
    "ARCHITECTURE.md",
    """# Actual architecture

React + Vite renders a responsive workspace. Same-origin `/api` calls proxy to Django REST Framework. Django session cookies and CSRF protect mutations. Each user has one organization membership; role checks protect brand/rule/team administration and independent review. Every query scopes tenant-owned data.

Django ORM models support PostgreSQL in Compose and SQLite for local fallback. UUID-named media is served through authenticated organization-scoped endpoints. Analyses are synchronous Python services for this FYP; large-scale deployment would need a task queue, cancellation and job status polling. ANALYZING occurs within the transaction, so it is not a durable background job status.

OpenCV extracts HSV palettes. Local transformer inference activates only when a saved trained artifact exists. Keyword-only assistance is labeled when it does not. Rules apply to supplied and generated hashtags; flagged recommendations are withheld. ARIMA/Prophet run on account-specific chronological history. Human decisions are recorded separately from computed findings.

Brand edits invalidate post analyses and reset workflow to draft. Content/image edits invalidate results. Independent reviewers approve or request changes. APPROVED is explicitly moved to READY_TO_PUBLISH; nothing is sent to Meta APIs. Scheduled dates are planning fields.

See `diagrams` for architecture, ERD, sequence, activity, use case, deployment, ML and workflow diagrams. External model adapters and missing datasets are described in LIMITATIONS and MISSING_DATA.
""",
)
write(
    "IMPLEMENTATION_PLAN.md",
    """# Implementation and verification plan

1. Preserve and hash supplied archive, inspect proposal, inventory all members, validate images and CSVs.
2. Copy useful raw resources, preserve legacy scripts, quarantine cookies from application/source control.
3. Implement priority OpenCV/HSV palette auditing with deterministic clustering and null score without a kit.
4. Build Django schema, migrations, tenant permissions, validated uploads and state transitions.
5. Integrate caption preprocessing, local transformer artifact loading, compliance rule matching and forecasting.
6. Build React pages and a clearly labeled synthetic organization for demo workflows.
7. Execute engine/API tests, frontend tests, production build and browser checks; fix discovered issues.
8. Run computational experiments only on provided records with explicit provenance limitations; preserve manifests.
9. Prepare deployment, data-collection templates, traceability, report evidence and viva documentation.
10. Obtain missing owner data, annotations, authorized sources and academic formulation decisions before claiming targets.

Current evidence and pending work live in BUILD_STATUS and FINAL_READINESS_REPORT. Existence of code alone does not count as verified completion.
""",
)
write(
    "METHODOLOGY.md",
    """# Implemented methodology

## Visual auditing
Validate file signature with Pillow, accept JPEG/PNG/WebP, enforce 10 MB and 20 megapixels, orient image, composite transparency on white, and convert RGB floats to OpenCV HSV. Downsample for palette analysis. Represent hue circularly using saturation-weighted sine/cosine, with value as a third clustering component. Use seeded OpenCV K-Means (up to six distinct clusters). Circular means recover representative HSV and HEX values.

Distance combines wrapped hue scaled by the smaller saturation, saturation difference and value difference, normalized by sqrt(3). Nearest approved colors within tolerance match. Score = sum of matched cluster percentages; off-brand = 100 minus score. This score is a descriptive color-coverage heuristic, not predictive accuracy. Whole-image colors include products, skin and background; poor masking can flag legitimate photography. Threshold calibration requires labeled owner-specific examples.

Logo detection is not inferred from palette or uploaded logo. A YOLO adapter requires appropriate weights and class mapping. Fonts remain a manual reviewer check. Design-fatigue assistance identifies identical file hashes, not broader visual similarity or human fatigue.

## NLP
Preserve original CSVs; deduplicate normalized caption text across train and validation. Build a multilabel vocabulary from training frequencies only. DistilBERT predicts sigmoid scores, ranked for top-k tags. CPU training defaults to final-block and classification-head fine-tuning; full fine-tuning is configurable. Report Precision@10, Recall@10 and micro-F1 on retained vocabulary, plus all-reference recall and vocabulary coverage. Rare/out-of-vocabulary tags are a major limitation.

BLEU measures n-gram overlap in ordered generation and is not interchangeable with set relevance. The approved proposal's BLEU target requires supervisor resolution if the multilabel formulation is used. The multimodal architecture concatenates ResNet-50 image embeddings with masked transformer text means and learns a multilabel head; evaluation is blocked without paired examples.

## Risk
Normalize Unicode and case; match exact normalized hashtags or bounded literal caption terms. Aggregate HIGH over MEDIUM over LOW. Add transparent editorial heuristics for repeated tags, long repeated characters and >30 tags. These are not claims about current platform policy. No toxicity claim is made without a validated classifier. Generated tags matching configured rules are withheld.

## Forecasting
Validate explicit date and metric, filter one account, reject missing/nonfinite/negative values, drop exact duplicate records, and sort chronologically. Aggregate means per observed UTC day. Missing days are retained; only forward fill within training is used for ARIMA. Training is the first 80% of daily range, validation the final 20%; score only observed held-out targets. ARIMA(1,1,1) and optional Prophet produce forecasts with intervals. Refit on full history for future forecasts. Report MAE, RMSE and clearly defined normalized MAE. Descriptive category/hour means are associations, not causal effects.

## Usability
Collect ten SUS items from real consenting participants. Odd responses contribute x−1; even responses 5−x; multiply their sum by 2.5. No participant responses have been supplied. A score on the 0–100 SUS scale is not a percentage of correct tasks.
""",
)
write(
    "API.md",
    """# API reference

All routes use `/api/`. Obtain `GET auth/csrf/` before a mutation and send its csrfToken as `X-CSRFToken` with the session cookie. The frontend refreshes the token before writes. JSON errors use HTTP 400; authorization failures 403; tenant-inaccessible resources 404. Protected media uses the same session.

| Method | Route | Purpose / restrictions |
|---|---|---|
| POST | auth/register/ | username, password, organization, optional email; creates OWNER in a new organization |
| POST | auth/login/ | username/password; rotates session |
| POST | auth/logout/ | clears session |
| GET/PATCH | auth/me/ | current user; email/password update |
| GET/POST/PATCH | team/ | list members; owner/admin create members or update role; owner role immutable |
| GET/POST | brands/ | list; owner/admin create with nested colors |
| GET/PATCH/DELETE | brands/{id}/ | tenant-scoped; mutation owner/admin; delete blocked if posts reference it |
| POST | brands/{id}/logo/ | multipart image, validated and re-encoded |
| POST | brands/{id}/batch/ | multipart images, 1–20 files; per-image result/errors |
| GET | assets/{id}/ | authorized logo bytes |
| GET/POST | posts/ | list/create; brand, title, caption, platform, optional scheduled_at |
| GET/PATCH/DELETE | posts/{id}/ | edit/delete only editable drafts; creators only their own |
| GET/POST | posts/{id}/image/ | authorized bytes / upload image |
| POST | posts/{id}/analyze/ | orchestrate visual, NLP, rule assessment; results stay DRAFT until submission |
| POST | posts/{id}/transition/ | decision: SUBMIT, APPROVE, REQUEST_CHANGES, MARK_READY, REOPEN; comments for review |
| GET | posts/{id}/export/ | JSON analysis |
| GET | posts/{id}/export/?export=csv | palette CSV download |
| GET/POST/PATCH/DELETE | rules/ or rules/{id}/ | list/configure sourced policy; owner/admin mutations |
| POST | rules/import_rules/ | JSON array, max 500; atomic import |
| GET | dashboard/ | counts, recent content and audit activity |
| GET/POST | forecasts/ | saved runs / multipart file, brand, metric, account_id, model, horizon, provenance, is_demo |

Brand color example: `{"hex":"#184F40","role":"PRIMARY"}`. This is a syntax example, not an official Brand Kit. Rule fields: term, kind (TEXT/HASHTAG), severity (LOW/MEDIUM/HIGH), platform (ALL/INSTAGRAM/FACEBOOK), explanation, source, active.

No direct publishing endpoint, public media URL, or paid LLM call exists. Default per-user and anonymous throttles are FYP-grade, not a distributed abuse-defense system.
""",
)
write(
    "DEPLOYMENT.md",
    """# Deployment

## Docker target
Install Docker with Compose. Copy `.env.example` to `.env`, set unique secrets/passwords, and keep DEBUG=1 only for local HTTP demos. Run `docker compose up --build`, then open http://localhost:8080. PostgreSQL persists in `pgdata`; uploads persist in `uploads`. Backend waits for PostgreSQL health and runs migrations. Optional demo: `docker compose exec backend python backend/manage.py seed_demo` with DEMO_PASSWORD set in `.env`.

Docker does not include optional heavy ML libraries by default. Install `requirements-ml.txt` in a derived backend image and mount validated model artifacts for transformer/Prophet operation. Without them the UI reports the limitation and ARIMA/keyword assistance work. Do not mount the archive/cookies into containers.

## Local Windows development
Python 3.12 is recommended. `python -m venv .venv`, activate it, then `python -m pip install -r requirements.txt`. Run `python backend/manage.py migrate` and `python backend/manage.py runserver 127.0.0.1:8000`. In another terminal run `npm --prefix frontend ci` and `npm --prefix frontend run dev`.

With no POSTGRES_HOST, SQLite is an explicit local fallback. For PostgreSQL set POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER and POSTGRES_PASSWORD in the process environment. Django does not automatically load `.env` outside Compose.

## Production preparation
Set DEBUG=0, a random SECRET_KEY, exact ALLOWED_HOSTS and HTTPS CORS/CSRF origins. Terminate TLS in a configured reverse proxy; secure cookies require HTTPS. Back up database and uploads together. Use a secret store or protected environment file, a managed database user, and private model volumes. Run `manage.py check --deploy` and address infrastructure-specific warnings. Hosting credentials, DNS, TLS and production deployment are not supplied or performed.

Do not run n8n source collection until source authorization is established. No scraping credentials or stored cookies are used.
""",
)
write(
    "USER_MANUAL.md",
    """# User manual

1. Register an organization or sign into the local synthetic demo. Registration creates an owner. Owners add creators and reviewers under Team.
2. Open Brand Kit. Enter owner-approved colors as HEX plus role, fonts, guideline source and reviewer rules. Upload a logo. No colors means no numeric brand score.
3. Create & Analyze: choose brand and Instagram/Facebook, give a title, write an English caption, choose a JPEG/PNG/WebP, then Analyze. Save draft works without an image. If analysis fails, the saved draft remains accessible.
4. Read dominant colors, matched coverage and warnings. Logo and font checks show their actual availability. Read the NLP status before interpreting tags. Review all pre-publish findings and coverage limitations.
5. Edit in Post Details; changes invalidate analysis. Re-analyze, then Submit for review. A different reviewer/owner/admin records approval comments or requests changes. Approved content can be marked Ready to publish. Publish manually outside this application.
6. Planned date/time is a queue field, not an automatic publishing trigger. Returning an approved post to draft invalidates prior analysis.
7. In Forecasting choose one account, metric, model and horizon, then upload a CSV with source/provenance. Check synthetic/demo if appropriate. The screen shows history, prediction intervals and held-out metrics. Analytics opens saved imports. Low errors on an unverified file do not demonstrate real SME reliability.
8. Compliance owners/admins add sourced rules. Repeated hashtags produce editorial warnings even without configured rules. No findings does not mean guaranteed compliance.
9. Batch audit is in each Brand Kit. Export per-image JSON or a post palette CSV. Team members cannot access another organization's images or posts.

Troubleshooting: check Brand Kit ownership, upload size/format, account selection for multi-account CSVs, ≥20 observed days and supported metric names. Missing models remain explicit. Do not fill research gaps with demo records.
""",
)
write(
    "DEVELOPER_GUIDE.md",
    """# Developer guide

Entry points: `backend/manage.py`, `backend/config/settings.py`, `frontend/src/main.jsx`. Domain ORM lives in `backend/core/models.py`, validation in `serializers.py`, orchestration/permissions in `views.py`. AI engines are pure service modules under `ai/`.

Run migrations before starting. Test Python with `python -m pytest -q`; frontend with `npm --prefix frontend test`; bundle with `npm --prefix frontend run build`. Windows sandbox process restrictions may require approved execution of Node build workers. Do not weaken application permissions to work around an execution sandbox.

Prepare captions with `python scripts/preprocessing/prepare_nlp.py`. Install optional requirements before `python scripts/training/train_hashtags.py`. Model output is `models/hashtag_transformer`; provenance/metrics go to `artifacts/experiments/nlp_transformer.json`. Never build vocabulary from validation. Paired-image experiments use `ai/nlp/multimodal.py` and the annotation manifest template.

`scripts/evaluation/run_forecasting.py` evaluates account 7, likes, chronological split on supplied data and records limitations. `scripts/evaluation/audit_images.py` extracts palettes with null brand scores. `scripts/evaluation/evaluate.py` accepts real truth/prediction labels with provenance and rejects missing/demo provenance. `scripts/verify_raw.py` verifies protected raw copies.

Never log passwords, caption bodies, image bytes or cookies. Audit events record actor/action/object/time. Adding new endpoints requires organization scoping and explicit role tests. Any material content/kit/policy change must invalidate stale review decisions or require reassessment.

The original archive contains legacy preprocessing and a scraper. Preserve them as evidence; do not execute the scraper or reuse cookies. The original forecasting projection loses account identity and is superseded by `ai/forecasting/engine.py`.
""",
)
write(
    "SME_DATA_COLLECTION_GUIDE.md",
    """# SME data collection

Recruit at least five real SMEs/agencies for the proposal pilot, explain that the system provides decision support, and obtain consent for each use: local testing, research evaluation, report figures and any redistribution. Participation may be withdrawn according to the agreed retention plan. Use pseudonymous organization/participant IDs and store consent separately.

Ask each owner for approved colors, logo files, fonts, exceptions (e.g. product photography) and dated written approval. Capture kit versions. Collect social images with rights/permission, not arbitrary search results. Ask two reviewers to label brand consistency independently against the same kit and adjudicate disagreements.

For NLP collect original English image-caption-tag pairs and source/account/group identifiers. Remove private contacts and credentials before sharing. Keep original observational tags separate from human relevance references. Split by account/campaign or duplicate group before training. Meet the >10,000-pair target with actual licensed/consented records.

For compliance obtain an approved policy source and dated expert labels, including both violations and benign examples. Do not assume a popular online banned-tag list is official or current. Record disagreement and policy versions. Weekly updates need source authorization and human review.

Export timestamped engagement by account. Retain metric definitions and missing-value semantics, especially reach/impressions and rate denominators. Prefer multiple months; never fill future values into training or randomly shuffle time series. Do not claim causal posting-time effects.

For usability let participants perform the same tasks without coaching: kit setup, upload, analysis interpretation, review, CSV import. Record task success/time separately from ten SUS answers. Do not substitute developer-generated answers for participants. Use `data/annotations` templates and aggregate only consenting real responses.
""",
)
write(
    "SUS_QUESTIONNAIRE.md",
    """# System Usability Scale collection template

Participant ID: ____  Organization ID: ____  Consent reference: ____  Date: ____

After completing the same defined workflow, rate each standard SUS statement from 1 (strongly disagree) to 5 (strongly agree):

1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to be able to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

Scoring implementation: `scripts/evaluation/evaluate.py::sus`. Subtract 1 from odd answers; subtract even answers from 5; sum and multiply by 2.5. Do not calculate a pilot mean until actual responses are supplied. Target ≥70 in the proposal is not an observed score. Source instrument attribution should be verified for the final report: John Brooke, SUS (1996).
""",
)
write(
    "VIVA_GUIDE.md",
    """# Viva guide — explain what actually exists

**What problem does ScaleeLapse solve? Why SMEs?** Small teams often review visual identity, captions, risk and engagement separately. This workspace brings those checks into one human approval flow. Affordability is a design aim, not a measured economic result.

**What are the four objectives?** Brand visual auditing, caption/hashtag assistance, pre-publish compliance risk, and engagement forecasting. The proposal also requires a unified interface and real SME usability evaluation.

**Why OpenCV, HSV and K-Means?** OpenCV handles images efficiently. HSV separates hue, saturation and brightness. K-Means repeatedly assigns pixels to nearest centers then updates centers until convergence. The implementation uses a circular hue embedding to avoid a discontinuity at red's hue wrap.

**How is Brand Score calculated?** It is the percentage of clustered image pixels whose representative color is close enough to an approved kit color. It is not accuracy. Without a kit, the score is null. Backgrounds and legitimate photography can cause false warnings.

**Why YOLO? Is logo detection working?** YOLO predicts object bounding boxes. A weights/class adapter exists, but the supplied files do not contain validated logo weights or annotations. The default UI says NOT_EVALUATED. A generic object detector would not prove a specific SME logo is present. IoU measures overlap of predicted and ground-truth boxes.

**How do font/fatigue checks work?** Approved fonts are recorded for human review. Exact repeated-image hashes flag reuse. Neither is presented as validated font recognition or a psychological fatigue model.

**Why DistilBERT/RoBERTa?** They are transformer text encoders in the approved direction. The training script uses DistilBERT with a multilabel sigmoid head and supports full fine-tuning. Default CPU mode tunes its final transformer block plus head. Check the experiment artifact for whether a run actually completed. Without a model, suggestions are explicitly keyword-only.

**What is ResNet-50? Multimodal AI?** ResNet-50 is a residual convolutional image encoder. Multimodal learning combines image features with text features. Here a module concatenates ResNet features and transformer text representations, but unpaired image/caption corpora cannot train this experiment responsibly.

**How are hashtags predicted? What are Precision/Recall/F1?** Rank multilabel scores. Precision@K counts correct tags among K recommendations; Recall@K counts recovered reference tags; F1 balances precision and recall. Also report vocabulary coverage so excluded rare tags do not disappear from the evidence.

**What is BLEU?** An n-gram overlap metric for ordered text generation. Hashtag sets have arbitrary order, so set metrics are more appropriate for this formulation. The proposal's BLEU target needs supervisor resolution, not relabeling another metric as BLEU.

**What is compliance risk? Why no guarantee?** The engine checks sourced terms and local spam heuristics, records evidence and aggregates severity. Rules may be incomplete/outdated and language contextual. No configured match means only that these checks found no match. Toxicity is not evaluated without a validated model.

**Why ARIMA and Prophet?** They are the proposal's time-series methods. ARIMA models autocorrelation/differencing; Prophet fits trend and seasonal components. Both need relevant historical data and evaluation. They do not guarantee future engagement.

**Why chronological splitting?** Future data must not inform past prediction. This system trains on the earlier 80% and evaluates on the later 20%, with no random shuffling and no backward fill. MAE is mean absolute error in metric units; RMSE emphasizes large errors. A percentage MAE needs an explicit denominator.

**Why React, Django and PostgreSQL?** React structures interactive screens; Django handles authentication, validation and ORM; PostgreSQL is the deployment relational database. SQLite is only the local fallback when PostgreSQL is unavailable. REST exposes resources through HTTP endpoints.

**How does authentication work?** Django hashes passwords and issues a session cookie. CSRF protects writes. Membership scopes data to an organization. Creators edit their own drafts; reviewers independently approve; owners/admins manage kits and members.

**What is the dataset? How was it cleaned?** The supplied archive has 538 images, 5,005 caption rows, and 29,999 engagement rows. Six images are unreadable; one image pair is duplicated. NLP removes duplicate caption text across splits, leaving 3,889/956. Engagement stays account-specific. Provenance/licenses remain unverified.

**What are the limitations and your contribution?** The engineering contribution is an integrated, permissioned workflow with working palette/rule/forecast pipelines and reproducible data handling. Academic target achievement, real SME generalization, multimodal evaluation, logo detection and SUS evidence remain dependent on genuine data and completed experiments. Improve annotations, calibration, group-based splits, multilingual handling and asynchronous jobs after current scope is validated.
""",
)
write(
    "REPORT_EVIDENCE.md",
    """# Report-ready evidence index

| Chapter | Factual material | Limits |
|---|---|---|
| 1 Introduction | Approved proposal introduction/problem/objectives in project_context | Do not extend its market claims without verified citations |
| 2 Background | HSV/K-Means, transformers, ARIMA/Prophet in METHODOLOGY and VIVA_GUIDE | Proposal bibliography is not independently verified; [4] has an author placeholder |
| 3 Methodology | METHODOLOGY, DATASETS, DATA_DICTIONARY, split manifest | Unknown licenses/provenance and no supervised visual/risk labels |
| 4 Design | ORM migrations and eight Mermaid diagrams | Distinguish optional adapters from running services |
| 5 Implementation | backend/core, ai, frontend/src, API reference | No auto-publishing; fonts manual; fatigue exact-duplicate heuristic |
| 6 Testing | tests/, artifacts/tests.xml, browser verification records, frontend tests/build | Unit fixtures are synthetic and prove behavior, not model accuracy |
| 7 Results | Only completed artifacts/experiments files and their actual metrics | Missing evidence is RESULT PENDING REAL EVALUATION; no invented targets |
| 8 Limitations | LIMITATIONS, MISSING_DATA, FINAL_READINESS_REPORT | Supervisor decisions and consenting SME study still required |

This is an evidence package, not a fabricated final thesis. Copy actual experiment configurations, dataset hashes, evaluated splits, warnings and limitations alongside any reported numbers. Screenshots from the demo are labeled synthetic and cannot establish model accuracy or real SME participation.
""",
)
print("Documentation written from audit and implementation.")
