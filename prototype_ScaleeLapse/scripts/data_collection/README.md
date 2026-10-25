# Collecting additional data

No scraper is executed from this directory. The supplied scraper is preserved under `data/raw/brand_visual` and in the original archive; its cookies must never be reused.

Use `docs/SME_DATA_COLLECTION_GUIDE.md` and `data/annotations/` to collect consented kits, images, captions, engagement exports, policy references and pilot responses. Requirements and unresolved licenses are in `docs/MISSING_DATA.md`. Place immutable incoming records under a versioned raw directory and extend a separate manifest before preprocessing them. Never overwrite the current raw files or their manifest.

Policy JSON can be reviewed and imported through the Compliance page. The disabled n8n workflow is a review reminder only until an authorized source and ingestion contract are supplied.
