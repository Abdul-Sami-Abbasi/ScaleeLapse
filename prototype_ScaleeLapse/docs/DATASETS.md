# Dataset audit

Original archive: `project_context/ScaleeLapse-main.zip`. It is retained byte-for-byte. Extracted originals remain under `project_context/archive_original`; useful resources are copied under `data/raw`. `resource_inventory.json` contains every file, size and SHA-256. `raw_manifest.json` protects the working raw copies.

| Dataset | Rows / files | Exact duplicate rows | Status | License |
|---|---:|---:|---|---|
| `data\raw\captions_hashtags\train_nlp.csv` | 4004 | 66 | Supplied, unverified provenance | UNKNOWN |
| `data\raw\captions_hashtags\val_nlp.csv` | 1001 | 9 | Supplied, unverified provenance | UNKNOWN |
| `data\raw\engagement\Instagram_Analytics.csv` | 29999 | 0 | Supplied, unverified provenance | UNKNOWN |
| `data\raw\provided_forecasting\engagement_time_series.csv` | 29999 | 101 | Supplied, unverified provenance | UNKNOWN |
| Brand images | 538 in 36 folders | One byte-identical pair | 532 decode; 6 invalid | UNKNOWN |

Image folder names are collection categories, not verified brand labels or compliance ground truth. No owner-provided palettes, logo boxes, font annotations, or consent records are supplied. `bata` has 13 images; other folders have 15 each. The duplicate pair crosses hemani and tapal. See the inventory for paths of all failures.

NLP supplied extraction script names `kkcosmos/instagram-images-with-captions` as its upstream source. This is a provenance clue, not proof of license or consent. The provided rows have original captions, cleaned captions and extracted hashtag targets. These are observational tags, not expert judgments of relevance. They include non-English content and celebrity/general-domain posts. The raw train/validation files share 33 normalized captions. New splits remove caption duplicates and cross-split leakage, preserving 3,889 training and 956 validation rows. The original 5,005 rows do not satisfy the proposal's >10,000 target.

Engagement data contains 29,999 rows and multiple account IDs. Its generator/source/license is UNKNOWN; it must not be described as real SME participation. The supplied forecasting preprocessing script can fall back to the first numeric column and ignores account boundaries. Its output loses account identity, so it is preserved but superseded. Forecasting uses the richer original CSV, explicit metric selection and account filtering.

The image scraper is retained for inspection only and was not executed. Its searches do not establish ownership or permission. Archived cookies are excluded from the app, source-control candidates and documentation content. No new scraping occurs.

Raw integrity: run `python scripts/verify_raw.py`. Processed palettes and deduplicated NLP splits are separate. Research reuse and redistribution require license/consent confirmation.
