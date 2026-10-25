import re
import unicodedata
from collections import Counter


def normalize(value):
    return unicodedata.normalize("NFKC", value).casefold().strip().lstrip("#")


def assess(caption, hashtags, rules):
    tags = [normalize(t) for t in hashtags if normalize(t)]
    text = unicodedata.normalize("NFKC", caption).casefold()
    findings = []
    for r in rules:
        term = normalize(r["term"])
        hit = (
            term in tags
            if r["kind"] == "HASHTAG"
            else bool(re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text))
        )
        if hit:
            findings.append(
                {
                    "term": r["term"],
                    "severity": r["severity"],
                    "explanation": r["explanation"],
                    "source": r["source"],
                    "recommendation": "Review this content against the cited source before approval.",
                }
            )
    duplicates = [t for t, c in Counter(tags).items() if c > 1]
    if duplicates:
        findings.append(
            {
                "severity": "MEDIUM",
                "explanation": "Repeated hashtags: " + ", ".join(duplicates),
                "source": "Local editorial heuristic; not a platform restriction",
                "recommendation": "Remove repeated hashtags.",
            }
        )
    if re.search(r"(.)\1{6,}", text) or len(tags) > 30:
        findings.append(
            {
                "severity": "MEDIUM",
                "explanation": "Spam-like repetition or excessive hashtag count.",
                "source": "Local editorial heuristic; not a platform restriction",
                "recommendation": "Reduce repetition and review relevance.",
            }
        )
    severity = max(
        [{"LOW": 0, "MEDIUM": 1, "HIGH": 2}[f["severity"]] for f in findings] or [0]
    )
    return {
        "level": ["LOW", "MEDIUM", "HIGH"][severity],
        "findings": findings,
        "rules_checked": len(rules),
        "coverage": "CONFIGURED_RULES_ONLY" if rules else "NO_SOURCED_RULES",
        "toxicity": "NOT_EVALUATED: no validated toxicity model supplied",
        "disclaimer": "Pre-Publish Risk Assessment; not a guarantee of compliance.",
        "recommendation": "Manual review before publication.",
    }
