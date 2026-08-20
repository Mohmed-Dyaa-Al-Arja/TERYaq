from __future__ import annotations

import re
from typing import Any

from backend.embedding.vector_store import get_client
from backend.embedding.model import embed_texts
from backend.embedding.config import COLLECTION_NAME

from backend.rag.reranker import rerank_results
from backend.rag.evidence_gate import validate_evidence


def normalize(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9%.\- ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_reference(query: str) -> str | None:
    """Extract explicit Figure/Map references."""
    q = normalize(query)

    figure_match = re.search(
        r"\bfig(?:ure)?\.?\s*(\d+)\s*([a-z]?)\b",
        q,
    )
    if figure_match:
        return f"fig. {figure_match.group(1)}{figure_match.group(2)}".strip()

    map_match = re.search(
        r"\bmap\s*(\d+)\s*([a-z]?)\b",
        q,
    )
    if map_match:
        return f"map {map_match.group(1)}{map_match.group(2)}".strip()

    return None


def _reference_contains_filter(reference: str) -> dict[str, Any] | None:
    """Build a case-variant Chroma document filter for an exact reference."""
    reference = normalize(reference)

    figure_match = re.fullmatch(r"fig\.\s*(\d+)([a-z]?)", reference)
    if figure_match:
        number, suffix = figure_match.groups()
        forms = [
            f"Figure {number}{suffix}",
            f"figure {number}{suffix}",
            f"Fig. {number}{suffix}",
            f"fig. {number}{suffix}",
            f"Fig {number}{suffix}",
            f"fig {number}{suffix}",
        ]
        return {"$or": [{"$contains": form} for form in forms]}

    map_match = re.fullmatch(r"map\s*(\d+)([a-z]?)", reference)
    if map_match:
        number, suffix = map_match.groups()
        forms = [
            f"Map {number}{suffix}",
            f"map {number}{suffix}",
        ]
        return {"$or": [{"$contains": form} for form in forms]}

    return None


def reference_matches(
    reference: str,
    document: str,
    metadata: dict[str, Any],
) -> bool:
    """Check whether a document represents the exact Figure/Map requested."""
    reference = normalize(reference)
    title = normalize(metadata.get("semantic_title", ""))
    caption = normalize(metadata.get("source_caption", ""))
    document_text = normalize(document)

    figure_match = re.fullmatch(r"fig\.\s*(\d+)([a-z]?)", reference)
    if figure_match:
        number, suffix = figure_match.groups()
        pattern = rf"\b(?:fig(?:ure)?\.?)\s*{re.escape(number)}{re.escape(suffix)}\b"
        return any(
            re.search(pattern, text, flags=re.IGNORECASE)
            for text in (caption, title, document_text)
        )

    map_match = re.fullmatch(r"map\s*(\d+)([a-z]?)", reference)
    if map_match:
        number, suffix = map_match.groups()
        pattern = rf"\bmap\s*{re.escape(number)}{re.escape(suffix)}\b"
        return any(
            re.search(pattern, text, flags=re.IGNORECASE)
            for text in (caption, title, document_text)
        )

    return False


def retrieve(
    query: str,
    top_k: int = 5,
) -> dict[str, Any]:
    client = get_client()
    collection = client.get_collection(name=COLLECTION_NAME)

    query_embedding = embed_texts([query])[0]

    semantic_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    reference = extract_reference(query)
    if not reference:
        return semantic_results

    reference_filter = _reference_contains_filter(reference)
    reference_matches_found: list[dict[str, Any]] = []

    if reference_filter:
        exact_items = collection.get(
            where_document=reference_filter,
            include=["documents", "metadatas"],
        )

        for document, metadata in zip(
            exact_items.get("documents", []),
            exact_items.get("metadatas", []),
        ):
            if reference_matches(reference, document, metadata):
                reference_matches_found.append(
                    {"document": document, "metadata": metadata}
                )

    if not reference_matches_found:
        return semantic_results

    final_documents: list[str] = []
    final_metadatas: list[dict] = []
    final_distances: list[float] = []
    final_ids: list[str] = []

    for item in reference_matches_found:
        metadata = item["metadata"]
        final_documents.append(item["document"])
        final_metadatas.append(metadata)
        final_distances.append(0.0)
        final_ids.append(f"reference_{metadata.get('page', 'unknown')}")

    semantic_documents = semantic_results["documents"][0]
    semantic_metadatas = semantic_results["metadatas"][0]
    semantic_distances = semantic_results["distances"][0]
    semantic_ids = semantic_results.get("ids", [[]])[0]

    for index, (document, metadata, distance) in enumerate(
        zip(semantic_documents, semantic_metadatas, semantic_distances)
    ):
        page = metadata.get("page")
        if any(existing.get("page") == page for existing in final_metadatas):
            continue

        final_documents.append(document)
        final_metadatas.append(metadata)
        final_distances.append(distance)
        final_ids.append(
            semantic_ids[index]
            if index < len(semantic_ids)
            else f"semantic_{page}"
        )

        if len(final_documents) >= top_k:
            break

    return {
        "documents": [final_documents[:top_k]],
        "metadatas": [final_metadatas[:top_k]],
        "distances": [final_distances[:top_k]],
        "ids": [final_ids[:top_k]],
    }


def retrieve_grounded_evidence(
    query: str,
    top_k: int = 5,
    min_score: float = 0.55,
) -> list[dict[str, Any]]:

    results = retrieve(query=query, top_k=top_k)
    ranked = rerank_results(query=query, results=results)

    # --------------------------------------------------------
    # DEBUG — shows rerank scores to diagnose false refusals
    # --------------------------------------------------------
    print("\n[RETRIEVER DEBUG]")
    for r in ranked[:5]:
        print(
            f"  SCORE: {r['rerank_score']:.3f} | "
            f"DIST: {r['distance']:.3f} | "
            f"PAGE: {r['metadata'].get('page')} | "
            f"TITLE: {str(r['metadata'].get('semantic_title', r['metadata'].get('section', '')))[:55]}"
        )

    # --------------------------------------------------------
    # Explicit Figure / Map: absolute priority
    # --------------------------------------------------------
    reference = extract_reference(query)
    if reference:
        exact_results = []
        other_results = []

        for result in ranked:
            if reference_matches(
                reference=reference,
                document=result["document"],
                metadata=result["metadata"],
            ):
                result["rerank_score"] = 999.0
                exact_results.append(result)
            else:
                other_results.append(result)

        ranked = exact_results + other_results

    # --------------------------------------------------------
    # Evidence Gate — adaptive threshold
    # --------------------------------------------------------
    # Try primary threshold first (0.55).
    # If nothing passes, retry at a relaxed threshold (0.35)
    # before giving up completely.
    #
    # This prevents false refusals on questions whose answer
    # IS present in the knowledge base but whose rerank score
    # falls just below the primary threshold due to weak
    # title/caption overlap (e.g. "breast cancer effects",
    # "how can I know I have breast cancer").
    # --------------------------------------------------------

    FALLBACK_SCORE = 0.35

    gate = validate_evidence(ranked, min_score=min_score)

    if not gate["sufficient"]:
        print(f"  [gate] primary threshold {min_score} failed — retrying at {FALLBACK_SCORE}")
        gate = validate_evidence(ranked, min_score=FALLBACK_SCORE)

    if not gate["sufficient"]:
        print("  [gate] fallback threshold also failed — returning empty")
        return []

    print(f"  [gate] passed — {len(gate['evidence'])} evidence chunk(s) accepted")

    # --------------------------------------------------------
    # Build grounded evidence list
    # --------------------------------------------------------
    evidence = []
    for result in gate["evidence"]:
        metadata = result["metadata"]
        evidence.append(
            {
                "text": result["document"],
                "document_id": metadata.get("document_id", "N/A"),
                "page": metadata.get("page", "N/A"),
                "section": metadata.get(
                    "section", metadata.get("semantic_title", "N/A")
                ),
                "chunk_id": result.get("chunk_id", "N/A"),
                "content_type": metadata.get("visual_type", "visual"),
                "citation": (
                    f"{metadata.get('document_id', 'N/A')}"
                    f" - page {metadata.get('page', 'N/A')}"
                ),
            }
        )

    return evidence