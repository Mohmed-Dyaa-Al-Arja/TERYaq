"""Deterministic claim-level grounding verification."""

from __future__ import annotations

import re

from backend.safety.evidence_validator import normalize_citation


def _normalize_text(text: str) -> str:
    """Normalize text for deterministic comparison."""
    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9%.\- ]+",
        " ",
        text,
    )

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def _tokenize(text: str) -> set[str]:
    """Convert text into normalized tokens."""
    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "of",
        "to",
        "and",
        "or",
        "in",
        "on",
        "for",
        "with",
        "that",
        "this",
        "shows",
        "show",
        "figure",
        "diagram",
        "visual",
    }

    return {
        token
        for token in _normalize_text(text).split()
        if token not in stop_words
        and len(token) > 1
    }


def _claim_supported(
    claim_text: str,
    evidence_text: str,
) -> tuple[bool, str]:
    """
    Determine whether a claim is grounded in evidence.

    This verifier intentionally does NOT call the LLM.
    """

    claim_normalized = _normalize_text(claim_text)
    evidence_normalized = _normalize_text(evidence_text)

    if not claim_normalized:
        return False, "Claim is empty."

    if not evidence_normalized:
        return False, "Evidence is empty."

    # ---------------------------------------------------------
    # 1. Exact claim contained in evidence
    # ---------------------------------------------------------

    if claim_normalized in evidence_normalized:
        return (
            True,
            "Claim text is directly present in the retrieved evidence.",
        )

    # ---------------------------------------------------------
    # 2. Token overlap
    # ---------------------------------------------------------

    claim_tokens = _tokenize(claim_text)
    evidence_tokens = _tokenize(evidence_text)

    if not claim_tokens:
        return False, "Claim contains no usable terms."

    overlap = claim_tokens & evidence_tokens

    overlap_ratio = len(overlap) / len(claim_tokens)

    # Strong deterministic support.
    if overlap_ratio >= 0.70:
        return (
            True,
            f"Claim has strong lexical support "
            f"({overlap_ratio:.0%} token overlap).",
        )

    # For short claims, require almost complete overlap.
    if len(claim_tokens) <= 5 and overlap_ratio >= 0.80:
        return (
            True,
            f"Short claim has strong lexical support "
            f"({overlap_ratio:.0%} token overlap).",
        )

    return (
        False,
        f"Insufficient lexical support "
        f"({overlap_ratio:.0%} token overlap).",
    )


def verify_claims(
    result: dict,
    evidence: list[dict],
) -> dict:
    """
    Verify every generated claim against its cited evidence.

    No additional LLM request is made here.
    """

    evidence_map = {
        normalize_citation(
            item.get("citation")
        ): item.get("text", "")
        for item in evidence
        if item.get("citation")
    }

    results = []

    for claim in result.get("claims", []):

        claim_text = claim.get(
            "text",
            "",
        )

        citation = normalize_citation(
            claim.get("citation")
        )

        evidence_text = evidence_map.get(
            citation
        )

        # -----------------------------------------------------
        # Missing citation
        # -----------------------------------------------------

        if not citation:
            results.append(
                {
                    "claim": claim_text,
                    "citation": citation,
                    "supported": False,
                    "reason": "Claim has no citation.",
                }
            )
            continue

        # -----------------------------------------------------
        # Citation not found
        # -----------------------------------------------------

        if not evidence_text:
            results.append(
                {
                    "claim": claim_text,
                    "citation": citation,
                    "supported": False,
                    "reason": (
                        "Citation was not found "
                        "in retrieved evidence."
                    ),
                }
            )
            continue

        # -----------------------------------------------------
        # Deterministic verification
        # -----------------------------------------------------

        supported, reason = _claim_supported(
            claim_text=claim_text,
            evidence_text=evidence_text,
        )

        results.append(
            {
                "claim": claim_text,
                "citation": citation,
                "supported": supported,
                "reason": reason,
            }
        )

    passed = (
        bool(results)
        and all(
            item["supported"]
            for item in results
        )
    )

    return {
        "passed": passed,
        "claims": results,
    }