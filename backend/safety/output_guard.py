"""Fail-closed output validation."""

from __future__ import annotations

from backend.safety.claim_verifier import verify_claims
from backend.safety.evidence_validator import validate_citations


def validate_grounded_output(
    result: dict,
    evidence: list[dict],
) -> dict:
    """Require citation validity and claim support before output."""
    citation_validation = validate_citations(
        result,
        evidence,
    )

    if citation_validation["status"] != "PASS":
        return {
            "passed": False,
            "citation_validation": citation_validation,
            "claim_verification": None,
        }

    claim_verification = verify_claims(
        result,
        evidence,
    )

    return {
        "passed": bool(
            claim_verification["passed"]
        ),
        "citation_validation": citation_validation,
        "claim_verification": claim_verification,
    }
