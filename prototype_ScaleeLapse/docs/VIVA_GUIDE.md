# Viva guide — explain what actually exists

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
