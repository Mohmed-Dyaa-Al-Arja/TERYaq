"""Evidence sufficiency and citation validation."""

from __future__ import annotations


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


def validate_citations(
    result: dict,
    evidence: list[dict],
) -> dict:
    """Ensure every generated claim cites accepted evidence."""
    valid_citations = {
        normalize_citation(item.get("citation"))
        for item in evidence
        if item.get("citation")
    }

    claims = result.get("claims", [])
    invalid = []

    for claim in claims:
        citation = normalize_citation(
            claim.get("citation")
        )
        if citation not in valid_citations:
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
