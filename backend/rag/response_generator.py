"""Grounded response generation."""

from __future__ import annotations

from backend.llm.client import generate_grounded_response


def generate_response(
    question: str,
    evidence: list[dict],
) -> dict:
    """Generate a structured answer from accepted evidence."""
    return generate_grounded_response(
        question=question,
        accepted_evidence=evidence,
    )
