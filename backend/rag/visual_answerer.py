from __future__ import annotations

import re
from typing import Any

from backend.rag.retriever import retrieve_grounded_evidence
from backend.rag.response_generator import generate_response
from backend.safety.output_guard import validate_grounded_output


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize(text: str) -> str:
    """Normalize text for reliable reference matching."""

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


# ============================================================
# EXPLICIT FIGURE / MAP REFERENCE
# ============================================================

def extract_reference(question: str) -> str | None:
    """
    Extract explicit Figure or Map references.

    Examples:

        Figure 23
        Fig. 23
        Figure 15A
        Fig 15B
        Map 1A
        Map 1B
    """

    normalized = normalize(question)

    # Figure / Fig
    figure_match = re.search(
        r"\b(?:figure|fig)\.?\s*(\d+)\s*([a-z]?)\b",
        normalized,
    )

    if figure_match:
        number = figure_match.group(1)
        suffix = figure_match.group(2)

        return f"figure {number}{suffix}"

    # Map
    map_match = re.search(
        r"\bmap\s*(\d+)\s*([a-z]?)\b",
        normalized,
    )

    if map_match:
        number = map_match.group(1)
        suffix = map_match.group(2)

        return f"map {number}{suffix}"

    return None


# ============================================================
# CAPTION MATCHING
# ============================================================

def caption_matches_reference(
    caption: str,
    reference: str,
) -> bool:
    """
    Check whether a source caption contains the exact
    Figure/Map requested by the user.
    """

    caption = normalize(caption)
    reference = normalize(reference)

    # --------------------------------------------------------
    # Figure
    # --------------------------------------------------------

    figure_match = re.match(
        r"figure\s+(\d+)([a-z]?)",
        reference,
    )

    if figure_match:

        number = figure_match.group(1)
        suffix = figure_match.group(2)

        pattern = (
            rf"\b(?:figure|fig)\.?\s*"
            rf"{number}{suffix}\b"
        )

        return bool(
            re.search(
                pattern,
                caption,
                flags=re.IGNORECASE,
            )
        )

    # --------------------------------------------------------
    # Map
    # --------------------------------------------------------

    map_match = re.match(
        r"map\s+(\d+)([a-z]?)",
        reference,
    )

    if map_match:

        number = map_match.group(1)
        suffix = map_match.group(2)

        pattern = (
            rf"\bmap\s*"
            rf"{number}{suffix}\b"
        )

        return bool(
            re.search(
                pattern,
                caption,
                flags=re.IGNORECASE,
            )
        )

    return False


# ============================================================
# RESULT MATCHING
# ============================================================

def result_matches_reference(
    item: dict[str, Any],
    reference: str,
) -> bool:
    """
    Match an explicit Figure/Map reference against the
    actual retrieved visual text.

    The retriever returns flattened evidence:
        text
        document_id
        page
        section
        chunk_id
        content_type
        citation

    Therefore, the Figure/Map reference is extracted
    directly from `item["text"]`.
    """

    text = normalize(
        item.get(
            "text",
            "",
        )
    )

    reference = normalize(
        reference
    )

    # --------------------------------------------------------
    # Figure reference
    # --------------------------------------------------------

    figure_match = re.match(
        r"figure\s+(\d+)([a-z]?)",
        reference,
    )

    if figure_match:

        number = figure_match.group(1)
        suffix = figure_match.group(2)

        pattern = (
            rf"\b(?:figure|fig)\.?\s*"
            rf"{number}{suffix}\b"
        )

        return bool(
            re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
        )

    # --------------------------------------------------------
    # Map reference
    # --------------------------------------------------------

    map_match = re.match(
        r"map\s+(\d+)([a-z]?)",
        reference,
    )

    if map_match:

        number = map_match.group(1)
        suffix = map_match.group(2)

        pattern = (
            rf"\bmap\s*"
            rf"{number}{suffix}\b"
        )

        return bool(
            re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
        )

    return False

# ============================================================
# EXPLICIT REFERENCE FILTER
# ============================================================

def filter_explicit_reference_results(
    question: str,
    evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    If the question contains an explicit Figure/Map reference,
    return ONLY the exact matching visual evidence.
    """

    reference = extract_reference(
        question
    )

    if reference is None:
        return evidence

    print(
        f"Explicit reference detected: {reference}"
    )

    exact_matches = []

    for item in evidence:

        if result_matches_reference(
            item=item,
            reference=reference,
        ):
            exact_matches.append(item)

    print(
        f"Exact reference matches: "
        f"{len(exact_matches)}"
    )

    if not exact_matches:
        return []

    return exact_matches


# ============================================================
# MAIN ANSWER FUNCTION
# ============================================================

def answer_visual_question(
    question: str,
    top_k: int = 5,
    min_score: float = 0.55,
) -> dict[str, Any]:

    # ========================================================
    # 1. RETRIEVAL
    # ========================================================

    evidence = retrieve_grounded_evidence(
        query=question,
        top_k=top_k,
        min_score=min_score,
    )

    print("\n" + "=" * 80)
    print("DEBUG RETRIEVED EVIDENCE")
    print("=" * 80)

    for i, item in enumerate(evidence, 1):

        print(f"\n--- RESULT {i} ---")

        print("KEYS:")
        print(item.keys())

        print("\nMETADATA:")
        print(item.get("metadata"))

        print("\nDOCUMENT:")
        print(item.get("document", "")[:1000])

        print("\nTEXT:")
        print(item.get("text", "")[:1000])

    evidence = filter_explicit_reference_results(
        question=question,
        evidence=evidence,
    )

    # ========================================================
    # 3. EVIDENCE GATE
    # ========================================================

    if not evidence:

        return {
            "answer": (
                "I’m unable to provide a grounded answer "
                "because the requested visual evidence "
                "was not found."
            ),
            "claims": [],
            "confidence": "low",
            "refusal": True,
            "evidence_sufficient": False,
            "sources": [],
        }

    # ========================================================
    # 4. GENERATE ANSWER
    # ========================================================

    result = generate_response(
        question=question,
        evidence=evidence,
    )

    # ========================================================
    # 5. VALIDATE ANSWER
    # ========================================================

    validation = validate_grounded_output(
        result,
        evidence,
    )

    if not validation["passed"]:

        return {
            "answer": (
                "I’m unable to provide a grounded answer "
                "because the generated response could not "
                "be fully verified against the retrieved "
                "visual evidence."
            ),
            "claims": [],
            "confidence": "low",
            "refusal": True,
            "evidence_sufficient": True,
            "validation": validation,
            "sources": [],
        }

    # ========================================================
    # 6. BUILD SOURCES
    # ========================================================

    sources = []

    for item in evidence:

        metadata = item.get(
            "metadata",
            {},
        )

        sources.append(
            {
                "document_id": item.get(
                    "document_id",
                    metadata.get(
                        "document_id",
                        "N/A",
                    ),
                ),
                "page": item.get(
                    "page",
                    metadata.get(
                        "page",
                        "N/A",
                    ),
                ),
                "section": item.get(
                    "section",
                    metadata.get(
                        "semantic_title",
                        "",
                    ),
                ),
                "chunk_id": item.get(
                    "chunk_id",
                    "N/A",
                ),
                "content_type": item.get(
                    "content_type",
                    metadata.get(
                        "visual_type",
                        "visual",
                    ),
                ),
                "citation": item.get(
                    "citation",
                    "N/A",
                ),
            }
        )

    # ========================================================
    # 7. FINAL RESPONSE
    # ========================================================

    result["evidence_sufficient"] = True
    result["sources"] = sources
    result["validation"] = validation
    result["refusal"] = False

    return result


# ============================================================
# CLI TEST
# ============================================================

def test_visual_question(
    question: str,
) -> None:

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

    print(
        result.get(
            "answer",
            "",
        )
    )

    print()
    print("=" * 80)
    print("EVIDENCE")
    print("=" * 80)

    print(
        "Sufficient:",
        result.get(
            "evidence_sufficient"
        ),
    )

    print()
    print("=" * 80)
    print("SOURCES")
    print("=" * 80)

    for source in result.get(
        "sources",
        [],
    ):

        print(
            f"Page: {source.get('page')} | "
            f"Type: {source.get('content_type')} | "
            f"Title: {source.get('section')}"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    test_visual_question(
        "What does Figure 23 show?"
    )