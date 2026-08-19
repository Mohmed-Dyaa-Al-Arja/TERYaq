from __future__ import annotations

from typing import Any


DEFAULT_MIN_SCORE = 0.55
DEFAULT_MIN_EVIDENCE = 1


def validate_evidence(
    ranked_results: list[dict[str, Any]],
    min_score: float = DEFAULT_MIN_SCORE,
    min_evidence: int = DEFAULT_MIN_EVIDENCE,
) -> dict[str, Any]:

    if not ranked_results:
        return {
            "sufficient": False,
            "reason": "No retrieved evidence.",
            "evidence": [],
        }

    valid_results = [
        result
        for result in ranked_results
        if result["rerank_score"] >= min_score
    ]

    if len(valid_results) < min_evidence:
        return {
            "sufficient": False,
            "reason": (
                "Retrieved evidence is below "
                "the required confidence threshold."
            ),
            "evidence": [],
        }

    return {
        "sufficient": True,
        "reason": "Sufficient retrieved evidence.",
        "evidence": valid_results,
    }