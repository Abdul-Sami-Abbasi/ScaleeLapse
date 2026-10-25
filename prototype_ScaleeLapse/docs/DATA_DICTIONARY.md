# Data dictionary

## data\raw\captions_hashtags\train_nlp.csv

| Column | Missing values | Meaning |
|---|---:|---|
| caption | 0 | Original supplied caption |
| clean_caption | 0 | Caption after supplied hashtag/URL removal |
| target_hashtags | 0 | Space-delimited observed hashtag labels |

## data\raw\captions_hashtags\val_nlp.csv

| Column | Missing values | Meaning |
|---|---:|---|
| caption | 0 | Original supplied caption |
| clean_caption | 0 | Caption after supplied hashtag/URL removal |
| target_hashtags | 0 | Space-delimited observed hashtag labels |

## data\raw\engagement\Instagram_Analytics.csv

| Column | Missing values | Meaning |
|---|---:|---|
| post_id | 0 | Supplied post id field; provenance not independently verified |
| account_id | 0 | Account grouping identifier; filter before forecasting |
| account_type | 0 | Supplied account type field; provenance not independently verified |
| follower_count | 0 | Supplied follower count field; provenance not independently verified |
| media_type | 0 | Supplied media type field; provenance not independently verified |
| content_category | 0 | Supplied content category field; provenance not independently verified |
| traffic_source | 0 | Supplied traffic source field; provenance not independently verified |
| has_call_to_action | 0 | Supplied has call to action field; provenance not independently verified |
| post_datetime | 0 | Posting timestamp; parsed UTC |
| post_date | 0 | Supplied post date field; provenance not independently verified |
| post_hour | 0 | Supplied post hour field; provenance not independently verified |
| day_of_week | 0 | Supplied day of week field; provenance not independently verified |
| likes | 0 | Supplied likes field; provenance not independently verified |
| comments | 0 | Supplied comments field; provenance not independently verified |
| shares | 0 | Supplied shares field; provenance not independently verified |
| saves | 0 | Supplied saves field; provenance not independently verified |
| reach | 0 | Supplied reach field; provenance not independently verified |
| impressions | 0 | Supplied impressions field; provenance not independently verified |
| engagement_rate | 0 | Provided rate; denominator/source not verified |
| followers_gained | 0 | Supplied followers gained field; provenance not independently verified |
| caption_length | 0 | Supplied caption length field; provenance not independently verified |
| hashtags_count | 0 | Supplied hashtags count field; provenance not independently verified |
| performance_bucket_label | 0 | Provided bucket, not independently validated |

## data\raw\provided_forecasting\engagement_time_series.csv

| Column | Missing values | Meaning |
|---|---:|---|
| ds | 0 | Date supplied by legacy preprocessing |
| y | 0 | Legacy engagement target; use original CSV instead |

## Application records

`BrandColor.hex`: six-digit sRGB HEX. `role`: PRIMARY, SECONDARY or BACKGROUND. `tolerance`: normalized circular-HSV distance in [0.01, 0.5]. `kit_source`: owner guideline provenance, not automatically verified. `fonts`: names for human checking.

`Post.status`: DRAFT, ANALYZING, READY_FOR_REVIEW, CHANGES_REQUIRED, APPROVED, READY_TO_PUBLISH. `scheduled_at` is a planning timestamp, not an API publishing instruction. `Media.sha256` supports exact-image reuse flags. Image bytes are validated and re-encoded.

Analysis JSON retains palette weights, score, methods, warnings and coverage. A null score means no approved colors. NOT_EVALUATED is not a detection result. MODEL_REQUIRED denotes keyword-only assistance. Rules preserve source, severity, platform, explanation and review timestamp. Forecast imports retain a source hash and provenance plus aggregated history; synthetic provenance is explicitly recorded.
