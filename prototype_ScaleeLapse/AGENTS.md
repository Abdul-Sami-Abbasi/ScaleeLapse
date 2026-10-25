# ScaleeLapse engineering rules

- Approved scope: `project_context/print final.pdf`, extracted as `project_context/proposal.txt`.
- Never modify `data/raw`, the original ZIP, or extracted archive. Check `scripts/verify_raw.py` after data work.
- Never read or reuse archived `cookies.txt`; exclude it and the original archive from Git.
- Do not invent Brand Kits, ground truth, citations, dataset licenses, results or SME participants.
- Keep synthetic application fixtures out of academic evaluation.
- Run `python -m pytest -q` and `npm --prefix frontend test` after substantive changes; build the frontend before delivery.
- Preserve tenant isolation, independent review, CSRF, upload validation, and analysis invalidation.
- No direct social publishing. Instagram and Facebook only. English NLP only.
- Document evidence gaps in `docs/MISSING_DATA.md` and readiness in `docs/BUILD_STATUS.md`.
