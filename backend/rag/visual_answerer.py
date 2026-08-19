from __future__ import annotations

from typing import Any

from backend.rag.retriever import retrieve_grounded_evidence
from backend.rag.response_generator import generate_response
from backend.safety.output_guard import validate_grounded_output


def answer_visual_question(
    question: str,
    top_k: int = 5,
    min_score: float = 0.55,
) -> dict[str, Any]:
    """
    Answer a question using the visual evidence indexed in Chroma.

    Flow:
        Question
            ↓
        Visual/semantic retrieval
            ↓
        Reranking
            ↓
        Evidence Gate
            ↓
        Grounded LLM
            ↓
        Output validation
    """

    # ---------------------------------------------------------
    # 1. Retrieve grounded visual evidence
    # ---------------------------------------------------------

    evidence = retrieve_grounded_evidence(
        query=question,
        top_k=top_k,
        min_score=min_score,
    )

    # ---------------------------------------------------------
    # 2. Evidence Gate
    # ---------------------------------------------------------

    if not evidence:
        return {
            "answer": (
                "I’m unable to provide a grounded answer because "
                "the retrieved visual evidence is insufficient."
            ),
            "claims": [],
            "confidence": "low",
            "refusal": True,
            "evidence_sufficient": False,
            "sources": [],
        }

    # ---------------------------------------------------------
    # 3. Generate grounded response
    # ---------------------------------------------------------

    result = generate_response(
        question=question,
        evidence=evidence,
    )

    # ---------------------------------------------------------
    # 4. Validate generated answer
    # ---------------------------------------------------------

    validation = validate_grounded_output(
        result,
        evidence,
    )

    if not validation["passed"]:
        return {
            "answer": (
                "I’m unable to provide a grounded answer because "
                "the generated response could not be fully verified "
                "against the retrieved visual evidence."
            ),
            "claims": [],
            "confidence": "low",
            "refusal": True,
            "evidence_sufficient": True,
            "validation": validation,
            "sources": [],
        }

    # ---------------------------------------------------------
    # 5. Build visual sources
    # ---------------------------------------------------------

    sources = []

    for item in evidence:

        sources.append(
            {
                "document_id": item.get(
                    "document_id",
                    "N/A",
                ),
                "page": item.get(
                    "page",
                    "N/A",
                ),
                "section": item.get(
                    "section",
                    "N/A",
                ),
                "chunk_id": item.get(
                    "chunk_id",
                    "N/A",
                ),
                "content_type": item.get(
                    "content_type",
                    "visual",
                ),
                "citation": item.get(
                    "citation",
                    "N/A",
                ),
            }
        )

    # ---------------------------------------------------------
    # 6. Final response
    # ---------------------------------------------------------

    result["evidence_sufficient"] = True
    result["sources"] = sources
    result["validation"] = validation
    result["refusal"] = False

    return result


def test_visual_question(question: str) -> None:
    """
    Simple CLI test for the visual RAG answerer.
    """

    print("=" * 80)
    print("QUERY")
    print("=" * 80)
    print(question)

    result = answer_visual_question(
        question=question,
    )

    print()
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(result.get("answer", ""))

    print()
    print("=" * 80)
    print("EVIDENCE")
    print("=" * 80)
    print(
        "Sufficient:",
        result.get("evidence_sufficient"),
    )

    print()
    print("=" * 80)
    print("SOURCES")
    print("=" * 80)

    for source in result.get("sources", []):
        print(
            f"Page: {source.get('page')} | "
            f"Type: {source.get('content_type')} | "
            f"Title: {source.get('section')}"
        )


if __name__ == "__main__":

    test_visual_question(
        "What does Figure 23 show?"
    )