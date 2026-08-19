"""Teryaq end-to-end grounded RAG pipeline."""

from __future__ import annotations

from backend.rag.retriever import retrieve_grounded_evidence
from backend.rag.response_generator import generate_response
from backend.safety.input_guard import check_input_safety
from backend.safety.output_guard import validate_grounded_output


def _build_sources(evidence: list[dict]) -> list[dict]:
    """Convert accepted evidence into the public API source schema."""
    sources = []

    for item in evidence:
        sources.append(
            {
                "document_id": item.get("document_id", "N/A"),
                "page": item.get("page", "N/A"),
                "section": item.get("section", "N/A"),
                "chunk_id": item.get("chunk_id", "N/A"),
                "content_type": item.get("content_type", "visual"),
                "citation": item.get("citation", "N/A"),
            }
        )

    return sources


def _refusal(
    answer: str,
    safety: dict,
    *,
    validation: dict | None = None,
    evidence_sufficient: bool = False,
) -> dict:
    result = {
        "answer": answer,
        "claims": [],
        "confidence": "low",
        "refusal": True,
        "evidence_sufficient": evidence_sufficient,
        "sources": [],
        "safety": safety,
    }

    if validation is not None:
        result["validation"] = validation

    return result


def run_pipeline(question: str) -> dict:
    """Run safety -> retrieval -> generation -> output validation."""
    safety = check_input_safety(question)

    # Safety is intentionally the first executable stage. Unsafe requests
    # never reach retrieval, the LLM, or the output validator.
    if not safety["safe"]:
        return _refusal(safety["message"], safety)

    evidence = retrieve_grounded_evidence(question)

    if not evidence:
        return _refusal(
            "I’m unable to provide a grounded answer because the retrieved "
            "evidence is insufficient to answer the question.",
            safety,
        )

    result = generate_response(
        question=question,
        evidence=evidence,
    )

    validation = validate_grounded_output(
        result,
        evidence,
    )

    if not validation["passed"]:
        return _refusal(
            "I’m unable to provide a grounded answer because the generated "
            "response could not be fully verified against the retrieved evidence.",
            safety,
            validation=validation,
            evidence_sufficient=True,
        )

    result["safety"] = safety
    result["validation"] = validation
    result["evidence_sufficient"] = True
    result["sources"] = _build_sources(evidence)
    result["refusal"] = False
    return result
