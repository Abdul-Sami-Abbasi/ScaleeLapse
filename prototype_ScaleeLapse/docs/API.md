# API reference

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
