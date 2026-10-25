# Missing data and academic decisions

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
