# Requirements traceability

Approved source: `project_context/print final.pdf`, objectives pp.5–6 and scope/methodology pp.6–8. Status separates implemented behavior from academic evidence.

| Proposal requirement | Implementation / file | Test / evidence | Evaluation | Status |
|---|---|---|---|---|
| O1 OpenCV HSV K-Means audit | ai/brand_audit/engine.py; Brand Kit UI | tests/test_engines.py palette/score/batch | Labels/kits absent; 90% on 500 not claimed | Functional; evaluation blocked |
| O1 logo/text regions, IoU | ai/brand_audit/logo.py; evaluate.py::iou | IoU unit test | Weights/boxes missing | Adapter only; blocked |
| Font flags/design fatigue | fonts list/manual review; Media.sha256 reuse | Visual response fields, browser review | No validated recognizer/fatigue labels | Partial heuristic/manual scope |
| O2 fine-tuned transformer | train_hashtags.py; ai/nlp/engine.py | Actual training artifact, clean split manifest and browser inference | Precision@10 1.18%; recall/F1/coverage recorded in EXPERIMENTS | Functional experimental model; relevance target not established |
| >10,000 captions, ≥10 tags, BLEU≥0.45 | Ranked head top 10 when model exists | Supplied data only 5,005 original rows | BLEU vs set formulation unresolved | Data/academic blocker |
| ResNet-50 multimodal extension | ai/nlp/multimodal.py; scripts/training/train_multimodal.py | Offline training code with group/hash separation; unrun | Actual pairs absent | Blocked |
| O3 restricted hashtag database | ComplianceRule; ai/compliance/engine.py | Rule/normalization/API tests | No sourced ground-truth corpus | Functional architecture; target pending |
| Weekly n8n refresh; recall≥95% | automation/n8n disabled reminder; import API | JSON workflow, rule import tests | Authorized source missing | Blocked |
| O4 ARIMA/Prophet; MAE≤15% | ai/forecasting/engine.py; Forecasting UI | Chronology/validation tests; forecasting.json | Normalized MAE 40.45% / 40.84%; denominator needs approval | Functional; target not met under implemented definition |
| React + Django + PostgreSQL | frontend; backend; migrations; Compose | Build, API/browser tests and PG checks | Integration evidence, not ML accuracy | See readiness |
| Scheduling, Instagram/Facebook | Post.platform and scheduled_at | Serializer and browser form | Manual planned queue only | Implemented planning scope |
| No direct publishing | No publishing endpoints | Source/API inspection | Not applicable | Enforced |
| Auth and independent approval | Membership; Post transitions; Approval; AuditLog | tests/test_api.py | Functional tests | Implemented |
| Five SMEs; SUS≥70 | SUS template and evaluate.py::sus | Scoring unit test | No real responses | Blocked |
| Raw integrity/reproducibility | audit_resources.py; verify_raw.py; manifests | SHA-256 verification | No raw transformations | Implemented |

Metric targets are requirements, not results. See MISSING_DATA for precise schemas and collection needs.
