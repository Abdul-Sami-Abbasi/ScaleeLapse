# Material limitations

No proposal target is claimed from synthetic fixtures or file counts. 538 image files are not 500 independently labeled valid evaluation examples. Official kits, logo boxes, paired images/captions, sourced risk labels and SME SUS responses are absent. All dataset licenses are UNKNOWN.

The color score measures dominant whole-image palette coverage. It does not identify which pixels are part of a logo, layout background or product. HSV tolerance needs calibration. Alpha is composited on white. Automated font recognition is not implemented; fonts are checked manually. Exact file-hash reuse is a limited design-fatigue review cue.

NLP defaults to explicit keyword assistance without a fine-tuned artifact. Training uses a small supplied general-domain corpus; even a successful run does not satisfy >10,000 pairs or establish SME-domain relevance. Rare-label filtering needs vocabulary-coverage reporting. Multimodal architecture exists but no paired-data experiment is valid yet. Unordered hashtag classification does not meet a BLEU generation claim; seek supervisor resolution.

Risk is limited to configured sourced rules and local repetition heuristics. No toxicity clearance is asserted. Policy freshness cannot be established without an authorized maintained source. n8n reminder workflow is disabled and does not scrape or ingest automatically.

Forecast errors on the supplied CSV are valid computations but not verified real-world SME evidence. Date parsing assumes UTC, metrics are daily means, missing-day semantics are unknown, and a single chronological split is not robust backtesting. ARIMA convergence/model assumptions may fail; inspect warnings and intervals. Negative lower bounds are shown rather than hidden. Historical category/hour associations are not causal recommendations.

Analysis is synchronous and sized for an FYP demo. SQLite does not implement PostgreSQL row locks; use PostgreSQL for concurrent reviews. No background queue, email/password recovery, MFA, public deployment, automatic social publishing or production load test is claimed. Planned dates only support manual scheduling. Large datasets should be processed in offline research scripts.

Deployment artifacts require runtime verification on the destination. DEBUG=1/local HTTP is not production security. Archived cookies are intentionally not reused. Original data should not be redistributed until permission is confirmed.
