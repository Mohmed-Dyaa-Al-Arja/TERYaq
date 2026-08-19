"""Deterministic claim-level grounding verification."""

from __future__ import annotations

import re

from backend.safety.evidence_validator import normalize_citation


# Small, explicit equivalence groups for common clinical paraphrases. This is
# intentionally deterministic and conservative; it is not an LLM substitute.
_CONCEPT_GROUPS = [
    {"mortality", "death", "deaths"},
    {"incidence", "occurrence", "cases"},
    {"survival", "survive", "surviving"},
    {"treatment", "therapy", "management"},
    {"diagnosis", "diagnose"},
    {"metastatic", "advanced", "spread"},
    {"risk", "chance", "likelihood"},
    {"increase", "higher", "increased", "rise", "rising"},
    {"decrease", "lower", "decreased", "reduction", "reduced"},
]

_CONCEPT_INDEX = {
    token: frozenset(group)
    for group in _CONCEPT_GROUPS
    for token in group
}


_STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "to", "and",
    "or", "in", "on", "for", "with", "that", "this", "shows", "show",
    "figure", "diagram", "visual", "what", "does", "do", "about", "how",
}


def _normalize_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9%.\- ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in _normalize_text(text).split()
        if token not in _STOP_WORDS and len(token) > 1
    }


def _concept_supported(claim_token: str, evidence_tokens: set[str]) -> bool:
    if claim_token in evidence_tokens:
        return True

    group = _CONCEPT_INDEX.get(claim_token)
    if group is None:
        return False

    return bool(group & evidence_tokens)


def _coverage(claim_tokens: set[str], evidence_tokens: set[str]) -> float:
    if not claim_tokens:
        return 0.0

    supported = sum(
        _concept_supported(token, evidence_tokens)
        for token in claim_tokens
    )
    return supported / len(claim_tokens)


def _claim_supported(
    claim_text: str,
    evidence_text: str,
) -> tuple[bool, str]:
    """Determine whether a claim has conservative deterministic support."""
    claim_normalized = _normalize_text(claim_text)
    evidence_normalized = _normalize_text(evidence_text)

    if not claim_normalized:
        return False, "Claim is empty."
    if not evidence_normalized:
        return False, "Evidence is empty."

    if claim_normalized in evidence_normalized:
        return True, "Claim text is directly present in the retrieved evidence."

    claim_tokens = _tokenize(claim_text)
    evidence_tokens = _tokenize(evidence_text)

    if not claim_tokens:
        return False, "Claim contains no usable terms."

    # First compare against the whole chunk, as before, but allow explicitly
    # mapped clinical paraphrases.
    global_coverage = _coverage(claim_tokens, evidence_tokens)
    if global_coverage >= 0.70:
        return True, f"Claim has strong concept support ({global_coverage:.0%} coverage)."

    # A generated claim is often a concise paraphrase of one sentence in a
    # larger chunk. Comparing against the entire chunk can therefore dilute
    # valid support. Evaluate the strongest evidence sentence as well.
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", evidence_text)
        if sentence.strip()
    ]

    best_sentence_coverage = max(
        (_coverage(claim_tokens, _tokenize(sentence)) for sentence in sentences),
        default=0.0,
    )

    if best_sentence_coverage >= 0.65:
        return (
            True,
            "Claim has strong concept support in an evidence sentence "
            f"({best_sentence_coverage:.0%} coverage).",
        )

    return (
        False,
        "Insufficient deterministic concept support "
        f"(whole chunk {global_coverage:.0%}, "
        f"best sentence {best_sentence_coverage:.0%}).",
    )


def verify_claims(
    result: dict,
    evidence: list[dict],
) -> dict:
    """Verify every generated claim against its cited evidence."""
    evidence_map = {
        normalize_citation(item.get("citation")): item.get("text", "")
        for item in evidence
        if item.get("citation")
    }

    results = []

    for claim in result.get("claims", []):
        claim_text = claim.get("text", "")
        citation = normalize_citation(claim.get("citation"))

        if not citation:
            results.append({
                "claim": claim_text,
                "citation": citation,
                "supported": False,
                "reason": "Claim has no citation.",
            })
            continue

        evidence_text = evidence_map.get(citation)
        if not evidence_text:
            results.append({
                "claim": claim_text,
                "citation": citation,
                "supported": False,
                "reason": "Citation was not found in retrieved evidence.",
            })
            continue

        supported, reason = _claim_supported(
            claim_text=claim_text,
            evidence_text=evidence_text,
        )

        results.append({
            "claim": claim_text,
            "citation": citation,
            "supported": supported,
            "reason": reason,
        })

    passed = bool(results) and all(item["supported"] for item in results)

    return {
        "passed": passed,
        "claims": results,
    }
