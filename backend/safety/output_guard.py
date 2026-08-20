"""Fail-closed output validation — DEBUG VERSION (remove prints before prod)."""

from __future__ import annotations

from backend.safety.claim_verifier import verify_claims
from backend.safety.evidence_validator import validate_citations


def validate_grounded_output(
    result: dict,
    evidence: list[dict],
) -> dict:
    """Require citation validity and claim support before output."""

    # ----------------------------------------------------------
    # DEBUG — print claims and evidence citations
    # ----------------------------------------------------------
    print("\n" + "=" * 60)
    print("DEBUG OUTPUT GUARD")
    print("=" * 60)
    print(f"Answer: {result.get('answer', '')[:120]}")
    print(f"Claims count: {len(result.get('claims', []))}")

    for i, claim in enumerate(result.get("claims", []), 1):
        print(f"\n  Claim {i}:")
        print(f"    text     : {claim.get('text', '')[:100]}")
        print(f"    citation : {claim.get('citation', '')}")

    print(f"\nEvidence citations:")
    for ev in evidence:
        print(f"  - {ev.get('citation', 'N/A')}")
    print("=" * 60)
    # ----------------------------------------------------------

    citation_validation = validate_citations(
        result,
        evidence,
    )

    print(f"\nCitation validation: {citation_validation}")

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

    print(f"\nClaim verification passed: {claim_verification['passed']}")
    for c in claim_verification.get("claims", []):
        print(f"  supported={c['supported']} | reason={c['reason']}")
        print(f"  claim: {c['claim'][:80]}")

    return {
        "passed": bool(
            claim_verification["passed"]
        ),
        "citation_validation": citation_validation,
        "claim_verification": claim_verification,
    }