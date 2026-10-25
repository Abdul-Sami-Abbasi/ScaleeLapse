# Approved-source update workflow

Weekly refresh is BLOCKED on an authorized source and provenance review. No scraping is enabled and no account cookies are consumed.

The application supports an authenticated owner/admin JSON import at `POST /api/rules/import_rules/`. The body is an array of `{term, kind, severity, platform, explanation, source, active}`. Session authentication and CSRF are required; do not put passwords in exported workflows.

Once a source and access method are approved, configure an n8n schedule trigger, fetch from that approved source, normalize its terms, retain its URL/version/date, and route proposed changes to an owner for review. Import only accepted changes. Existing decisions should be rechecked after policy changes. The provided disabled workflow creates a weekly review reminder with no network fetch or publishing action. An unattended authenticated ingestion integration remains future work until the source contract is known.
