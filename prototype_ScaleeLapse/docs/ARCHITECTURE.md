# Actual architecture

React + Vite renders a responsive workspace. Same-origin `/api` calls proxy to Django REST Framework. Django session cookies and CSRF protect mutations. Each user has one organization membership; role checks protect brand/rule/team administration and independent review. Every query scopes tenant-owned data.

Django ORM models support PostgreSQL in Compose and SQLite for local fallback. UUID-named media is served through authenticated organization-scoped endpoints. Analyses are synchronous Python services for this FYP; large-scale deployment would need a task queue, cancellation and job status polling. ANALYZING occurs within the transaction, so it is not a durable background job status.

OpenCV extracts HSV palettes. Local transformer inference activates only when a saved trained artifact exists. Keyword-only assistance is labeled when it does not. Rules apply to supplied and generated hashtags; flagged recommendations are withheld. ARIMA/Prophet run on account-specific chronological history. Human decisions are recorded separately from computed findings.

Brand edits invalidate post analyses and reset workflow to draft. Content/image edits invalidate results. Independent reviewers approve or request changes. APPROVED is explicitly moved to READY_TO_PUBLISH; nothing is sent to Meta APIs. Scheduled dates are planning fields.

See `diagrams` for architecture, ERD, sequence, activity, use case, deployment, ML and workflow diagrams. External model adapters and missing datasets are described in LIMITATIONS and MISSING_DATA.
