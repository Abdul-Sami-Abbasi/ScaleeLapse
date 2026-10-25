# Implemented methodology

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
