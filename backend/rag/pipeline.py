"""Teryaq end-to-end grounded RAG pipeline."""

from __future__ import annotations

from backend.rag.retriever import retrieve_grounded_evidence
from backend.rag.response_generator import generate_response
from backend.safety.input_guard import check_input_safety
from backend.safety.output_guard import validate_grounded_output


def run_pipeline(question: str) -> dict:
    """Run safety -> retrieval -> generation -> output validation."""
    safety = check_input_safety(question)

    if not safety["safe"]:
        return {
            "answer": safety["message"],
            "claims": [],
            "confidence": "low",
            "refusal": True,
            "safety": safety,
        }

    evidence = retrieve_grounded_evidence(question)

    if not evidence:
        return {
            "answer": (
                "I’m unable to provide a grounded answer because "
                "the retrieved evidence is insufficient to answer "
                "the question."
            ),
            "claims": [],
            "confidence": "low",
            "refusal": True,
            "safety": safety,
        }

    result = generate_response(
        question=question,
        evidence=evidence,
    )

    validation = validate_grounded_output(
        result,
        evidence,
    )

    if not validation["passed"]:
        return {
            "answer": (
                "I’m unable to provide a grounded answer because "
                "the generated response could not be fully verified "
                "against the retrieved evidence."
            ),
            "claims": [],
            "confidence": "low",
            "refusal": True,
            "validation": validation,
        }

    result["safety"] = safety
    result["validation"] = validation
    return result
