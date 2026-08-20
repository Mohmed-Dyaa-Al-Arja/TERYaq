"""Grounded response generation."""

from __future__ import annotations

from backend.llm.client import generate_grounded_response


def generate_response(
    question: str,
    evidence: list[dict],
    history: str = "",
) -> dict:
    """Generate a structured answer from accepted evidence.

    Parameters
    ----------
    question:
        The current user question.
    evidence:
        Accepted evidence chunks from the retriever.
    history:
        Plain-text conversation transcript formatted as
        "Role: content" lines, produced by
        visual_answerer._format_history().
        Passed through to the LLM client so the prompt can
        include prior turns for context-aware answering.
        Defaults to an empty string (stateless behaviour).
    """

    try:
        return generate_grounded_response(
            question=question,
            accepted_evidence=evidence,
            history=history,
        )
    except TypeError:
        # Fallback: LLM client does not yet accept `history`.
        # Operate statelessly rather than crashing.
        return generate_grounded_response(
            question=question,
            accepted_evidence=evidence,
        )