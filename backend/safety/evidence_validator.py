"""Evidence sufficiency and citation validation."""

from __future__ import annotations

import re


def has_sufficient_evidence(
    evidence: list[dict],
) -> bool:
    """Return True only when retrieval produced accepted evidence."""
    return bool(evidence)


def normalize_citation(citation: str | None) -> str:
    if citation is None:
        return ""
    return " ".join(
        str(citation).strip().strip("[]").split()
    )


def _citation_document_id(citation: str) -> str:
    """
    Extract the document-id prefix from a citation string.

    Examples
    --------
    "breast-cancer-screening-final-rec - page unknown"
        -> "breast-cancer-screening-final-rec"
    "WHO_GBCI - page 36"
        -> "WHO_GBCI"
    "breast-cancer-screening-final-rec"
        -> "breast-cancer-screening-final-rec"

    The LLM sometimes omits the " - page N" suffix when it
    writes the citation key in its JSON output.  We therefore
    match a claim citation against BOTH the full citation string
    AND just its document-id prefix so the check is robust to
    that truncation.
    """
    # Strip everything from " - page" onwards.
    return re.sub(r"\s*-\s*page\s*\S+$", "", citation).strip()


def validate_citations(
    result: dict,
    evidence: list[dict],
) -> dict:
    """Ensure every generated claim cites accepted evidence.

    Matching is done at two levels:
      1. Full normalized citation  (exact match — preferred).
      2. Document-id prefix only   (fallback for LLM truncation).

    Either match is sufficient to consider the citation valid.
    """
    # Build both lookup sets from accepted evidence.
    valid_full: set[str] = set()
    valid_doc_ids: set[str] = set()

    for item in evidence:
        raw = item.get("citation")
        if not raw:
            continue
        full = normalize_citation(raw)
        valid_full.add(full)
        valid_doc_ids.add(_citation_document_id(full))

    claims = result.get("claims", [])
    invalid = []

    for claim in claims:
        raw_claim_citation = claim.get("citation")
        citation = normalize_citation(raw_claim_citation)
        doc_id = _citation_document_id(citation)

        # Accept if EITHER the full string OR the doc-id matches.
        if citation in valid_full or doc_id in valid_doc_ids:
            continue

        invalid.append(
            {
                "text": claim.get("text", ""),
                "citation": citation,
            }
        )

    return {
        "status": "PASS" if not invalid else "FAIL",
        "total_claims": len(claims),
        "invalid_claims": len(invalid),
        "invalid_claim_details": invalid,
    }