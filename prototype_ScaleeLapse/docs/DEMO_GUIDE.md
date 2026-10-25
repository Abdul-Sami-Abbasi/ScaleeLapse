# Demo guide

Double-click `start.cmd` in the project folder, or run `.\start.cmd` from PowerShell; open http://127.0.0.1:5173. The launcher uses a process-only execution-policy setting and leaves persistent Windows settings unchanged. Prepared users are `demo.owner`, `demo.creator`, `demo.reviewer` with local demo password `ScaleeDemo!2026`. New installations use the password chosen in DEMO_PASSWORD when seeding. All demo data is synthetic and visibly marked.

1. Log in as owner. Show dashboard counts and the synthetic banner. Explain that these are database counts, not experiment results.
2. Open Brand Kit. Show Form & Field's three demonstration colors and font list. Explain that these were invented only for the demo and are not any real SME's official kit. Upload a logo if needed; explain that upload does not imply detection.
3. Log in as creator (or use the owner to create content that a different reviewer will approve). Create & Analyze → brand → Instagram/Facebook → title → caption → `data/demo/synthetic-post.png`.
4. Click Analyze. Show dominant swatches, percentages and color coverage. A score measures approved-palette coverage. Show missing detector/font limitations. Add a repeated hashtag to demonstrate a real editorial rule warning.
5. Explain the NLP status: the local DistilBERT is a real experimental trained model, but validation quality is low. Show its Precision@10 and separate caption keywords. Do not describe these as ten guaranteed relevant tags.
6. Show pre-publish risk coverage. With no sourced rules, low risk is not policy clearance. No toxicity model has been validated. Rule editing is available to owner/admin only.
7. Save/submit for review. Log in as reviewer. Open Approvals, inspect all findings, record comments and approve. Mark Ready to publish. There is no social-media API call.
8. Show review history with actor, decision, comments and time. Reopen/edit to demonstrate that analysis must be repeated. A creator cannot approve their own work.
9. Open Forecasting. Upload `data/demo/synthetic-engagement.csv`, metric likes, ARIMA, seven days, provenance `SYNTHETIC DEMO DATA`, checkbox enabled. Show historical chart, bounds and held-out MAE/RMSE. These are synthetic test errors, not academic results.
10. For actual supplied-file computation, discuss `artifacts/experiments/forecasting.json` separately. Account 7's normalized errors are around 40–41%, so the proposal target was not met. Dataset provenance is still unknown.
11. End with FINAL_READINESS_REPORT, MISSING_DATA and the proposal traceability table. State precisely which evidence is missing.

Allow extra time for the first transformer model load. Warm the model with one analysis before a live presentation. Keep a second browser session/profile for the reviewer if convenient; never bypass independent-review checks for a smoother demo.
