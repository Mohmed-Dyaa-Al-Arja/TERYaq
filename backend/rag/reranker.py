from __future__ import annotations

import re
from typing import Any


STOP_WORDS = {
    "what", "does", "do", "the", "a", "an", "is", "are",
    "of", "about", "show", "shows", "figure", "page",
    "tell", "me", "in", "on", "for", "and", "to"
}


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9%.\- ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in normalize(text).split()
        if token not in STOP_WORDS and len(token) > 1
    }


def extract_reference(query: str) -> str | None:
    """
    Extract explicit references such as:
    Figure 23
    Fig. 23
    Fig 23
    Map 1a
    Map 2b
    """

    query_normalized = normalize(query)

    figure_match = re.search(
        r"\bfig(?:ure)?\.?\s*(\d+)\s*([a-z]?)\b",
        query_normalized,
    )

    if figure_match:
        number = figure_match.group(1)
        suffix = figure_match.group(2)

        return f"fig. {number}{suffix}".strip()

    map_match = re.search(
        r"\bmap\s*(\d+)\s*([a-z]?)\b",
        query_normalized,
    )

    if map_match:
        number = map_match.group(1)
        suffix = map_match.group(2)

        return f"map {number}{suffix}".strip()

    return None


def score_result(
    query: str,
    document: str,
    metadata: dict[str, Any],
    distance: float,
) -> float:

    query_tokens = tokenize(query)

    title = str(
        metadata.get("semantic_title", "")
    )

    caption = str(
        metadata.get("source_caption", "")
    )

    visual_type = str(
        metadata.get("visual_type", "")
    )

    title_tokens = tokenize(title)
    caption_tokens = tokenize(caption)
    document_tokens = tokenize(document)

    score = 0.0

    # ---------------------------------------------------------
    # 1. Semantic similarity from Chroma
    # Lower cosine distance = better.
    # ---------------------------------------------------------

    semantic_score = max(
        0.0,
        1.0 - distance
    )

    score += semantic_score * 0.45

    # ---------------------------------------------------------
    # 2. Title overlap
    # ---------------------------------------------------------

    title_overlap = (
        len(query_tokens & title_tokens)
        / max(len(query_tokens), 1)
    )

    score += title_overlap * 0.25

    # ---------------------------------------------------------
    # 3. Caption overlap
    # ---------------------------------------------------------

    caption_overlap = (
        len(query_tokens & caption_tokens)
        / max(len(query_tokens), 1)
    )

    score += caption_overlap * 0.20

    # ---------------------------------------------------------
    # 4. General document overlap
    # ---------------------------------------------------------

    document_overlap = (
        len(query_tokens & document_tokens)
        / max(len(query_tokens), 1)
    )

    score += document_overlap * 0.10

    # ---------------------------------------------------------
    # 4.5 Important phrase / keyword matching
    # ---------------------------------------------------------

    query_normalized = normalize(query)

    title_normalized = normalize(title)
    caption_normalized = normalize(caption)
    document_normalized = normalize(document)

    # Strong phrases that indicate the query is asking
    # about the actual visual content.
    important_phrases = [
        "targets not being met",
        "targets not met",
        "causes",
        "underlying causes",
        "causes of underperformance",
        "three year survival",
        "breast cancer incidence",
        "incidence rates",
        "mortality rates",
    ]

    for phrase in important_phrases:

        if phrase in query_normalized:

            if phrase in title_normalized:
                score += 0.20

            elif phrase in caption_normalized:
                score += 0.18

            elif phrase in document_normalized:
                score += 0.12

    # ---------------------------------------------------------
    # 4.6 Numeric / percentage value matching
    # ---------------------------------------------------------
    #
    # If the query contains a numeric value or percentage
    # (e.g. "60%", "2 months", "3 years"), boost any document
    # that also contains that exact value.
    #
    # This catches questions like:
    #   "What is the ≥60% goal for early-stage diagnosis?"
    #   "What is the KPI of 2 months for Pillar 2?"
    #
    # In those cases the title/caption overlap is weak
    # because the title describes the visual theme, not the
    # specific metric — but the metric appears in the document
    # body text.
    # ---------------------------------------------------------

    numeric_tokens = set(
        re.findall(r"\d+(?:[%\.]\d+)?", query)
    )

    if numeric_tokens:
        numeric_matches = sum(
            1 for n in numeric_tokens
            if n in document_normalized
        )
        if numeric_matches:
            score += 0.15 * (
                numeric_matches / len(numeric_tokens)
            )

    # ---------------------------------------------------------
    # 5. Explicit Figure / Map reference matching
    # ---------------------------------------------------------

    reference = extract_reference(query)

    if reference:

        title_normalized = normalize(title)
        caption_normalized = normalize(caption)
        document_normalized = normalize(document)

        # Example:
        # query -> Figure 23
        # caption -> Fig. 23. Using a fishbone diagram...

        reference_number = (
            reference
            .replace("fig. ", "")
            .replace("map ", "")
        )

        # Exact reference in caption/title
        if (
            reference in caption_normalized
            or reference in title_normalized
        ):
            score += 1.00

        # Reference number appears in caption
        elif reference_number in caption_normalized:
            score += 0.75

        # Reference number appears somewhere in document
        elif reference_number in document_normalized:
            score += 0.40

    # ---------------------------------------------------------
    # 6. Visual type matching
    # ---------------------------------------------------------

    query_normalized = normalize(query)

    if visual_type and visual_type in query_normalized:
        score += 0.05

    return score


def rerank_results(
    query: str,
    results: dict[str, Any],
) -> list[dict[str, Any]]:

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    ids = results["ids"][0]

    ranked = []

    for document, metadata, distance, chunk_id in zip(
        documents,
        metadatas,
        distances,
        ids,
    ):

        score = score_result(
            query=query,
            document=document,
            metadata=metadata,
            distance=distance,
        )

        ranked.append(
            {
                "chunk_id": chunk_id,
                "document": document,
                "metadata": metadata,
                "distance": distance,
                "rerank_score": score,
            }
        )

    ranked.sort(
        key=lambda x: x["rerank_score"],
        reverse=True,
    )

    return ranked