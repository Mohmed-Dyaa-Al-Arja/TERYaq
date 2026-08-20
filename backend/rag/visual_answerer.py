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
# HISTORY FORMATTER
# ============================================================

def _format_history(
    history: list[dict],
) -> str:
    """
    Convert MongoDB message documents into a plain-text
    conversation transcript for the LLM prompt.

    Each entry has: role, content, created_at, sources.
    Only role + content are needed for the prompt.
    """

    if not history:
        return ""

    lines = []

    for turn in history:
        role = turn.get("role", "user").capitalize()
        content = turn.get("content", "").strip()

        if content:
            lines.append(f"{role}: {content}")

    return "\n".join(lines)


# ============================================================
# QUERY EXPANSION
# ============================================================

# Pronouns / vague references that signal the question depends
# on prior context to be understood by the retriever.
#
# NOTE: bare "this" / "that" / "they" / "them" / "their" were
# removed — they match far too often as ordinary conjunctions
# ("know THAT i have...", "given THAT...") and trigger needless,
# noisy expansion. Only keep patterns that are almost always a
# genuine backward reference.
_CONTEXT_DEPENDENT = re.compile(
    r"\b(it|its|the disease|this disease|that disease|"
    r"this condition|that condition|the condition|"
    r"this cancer|that cancer|the cancer)\b",
    re.IGNORECASE,
)

# Domain entities we can confidently resolve pronouns to.
# Matched across the WHOLE history (user + assistant), not just
# the last user turn — the entity name is far more likely to
# appear in the assistant's grounded answers than in a user's
# short follow-up question.
_ENTITY_PATTERNS = (
    re.compile(r"\bbreast cancer\b", re.IGNORECASE),
)


def _extract_topic_entity(history: list[dict]) -> str:
    """
    Scan the full conversation (both roles) for the most recently
    mentioned domain entity, e.g. "breast cancer".

    This is far more reliable than reusing the last raw user
    question: that question may never literally name the topic
    (e.g. "which age group should be screened with mammography?"
    never says "breast cancer" — only the assistant's answer does).
    """

    entity = ""

    for turn in history:
        content = turn.get("content", "")

        for pattern in _ENTITY_PATTERNS:
            match = pattern.search(content)
            if match:
                entity = match.group(0)

    return entity


def _extract_last_user_topic(history: list[dict]) -> str:
    """
    Fallback: extract the last user message content from history,
    trimmed at a word boundary. Used only when no known domain
    entity could be found anywhere in the conversation.
    """

    for turn in reversed(history):
        if turn.get("role") == "user":
            content = turn.get("content", "").strip()
            if content:
                # Trim at a word boundary instead of mid-word.
                if len(content) > 80:
                    content = content[:80].rsplit(" ", 1)[0]
                return content

    return ""


def _expand_query(question: str, history: list[dict]) -> str:
    """
    Expand the retrieval query with topic context from history
    when the question contains vague pronouns or references.

    Prefers a known domain entity (e.g. "breast cancer") found
    anywhere in the conversation; falls back to the last user
    question only if no entity can be resolved.

    Returns the original question unchanged if no expansion is
    needed (no history, or no context-dependent wording).
    """

    if not history:
        return question

    if not _CONTEXT_DEPENDENT.search(question):
        return question

    topic = _extract_topic_entity(history)

    if not topic:
        topic = _extract_last_user_topic(history)

    if not topic:
        return question

    # Prepend the prior topic so the retriever has enough signal.
    expanded = f"{topic} {question}"

    print(f"[query expansion] '{question}' -> '{expanded}'")

    return expanded


# ============================================================
# MAIN ANSWER FUNCTION
# ============================================================

def answer_visual_question(
    question: str,
    top_k: int = 5,
    min_score: float = 0.55,
    history: list[dict] | None = None,
) -> dict[str, Any]:

    history = history or []

    # ========================================================
    # 1. RETRIEVAL
    # ========================================================

    retrieval_query = _expand_query(
        question=question,
        history=history,
    )

    evidence = retrieve_grounded_evidence(
        query=retrieval_query,
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
                "I'm unable to provide a grounded answer "
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
    # 4. GENERATE ANSWER  (with conversation history)
    # ========================================================

    result = generate_response(
        question=question,
        evidence=evidence,
        history=_format_history(history),
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
                "I'm unable to provide a grounded answer "
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