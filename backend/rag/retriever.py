from __future__ import annotations

import re
from typing import Any

from backend.embedding.vector_store import get_client
from backend.embedding.model import embed_texts
from backend.embedding.config import COLLECTION_NAME

from backend.rag.reranker import rerank_results
from backend.rag.evidence_gate import validate_evidence


# ============================================================
# Helpers
# ============================================================

def normalize(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9%.\- ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_reference(query: str) -> str | None:
    """
    Extract explicit references such as:

    Figure 23
    Fig. 23
    Fig 23
    Figure 23A
    Fig. 23A
    Map 1a
    Map 2b
    """

    q = normalize(query)

    # --------------------------------------------------------
    # Figure reference
    # --------------------------------------------------------

    figure_match = re.search(
        r"\bfig(?:ure)?\.?\s*(\d+)\s*([a-z]?)\b",
        q,
    )

    if figure_match:
        number = figure_match.group(1)
        suffix = figure_match.group(2)

        return f"fig. {number}{suffix}".strip()

    # --------------------------------------------------------
    # Map reference
    # --------------------------------------------------------

    map_match = re.search(
        r"\bmap\s*(\d+)\s*([a-z]?)\b",
        q,
    )

    if map_match:
        number = map_match.group(1)
        suffix = map_match.group(2)

        return f"map {number}{suffix}".strip()

    return None


def reference_matches(
    reference: str,
    document: str,
    metadata: dict[str, Any],
) -> bool:
    """
    Check whether a document is the exact Figure / Map
    explicitly requested by the user.
    """

    reference = normalize(reference)

    title = normalize(
        metadata.get("semantic_title", "")
    )

    caption = normalize(
        metadata.get("source_caption", "")
    )

    document_text = normalize(document)

    # ========================================================
    # FIGURE REFERENCE
    # ========================================================

    figure_match = re.match(
        r"^fig\.\s*(\d+)([a-z]?)$",
        reference,
    )

    if figure_match:

        number = figure_match.group(1)
        suffix = figure_match.group(2)

        # ----------------------------------------------------
        # Match:
        #
        # Fig. 23
        # Figure 23
        # Fig 23
        # Fig. 23A
        # Figure 23A
        # ----------------------------------------------------

        pattern = (
            rf"\b(?:fig(?:ure)?\.?)\s*"
            rf"{re.escape(number)}"
            rf"{re.escape(suffix)}\b"
        )

        # Caption is strongest.
        if re.search(pattern, caption):
            return True

        # Title.
        if re.search(pattern, title):
            return True

        # Document text fallback.
        if re.search(pattern, document_text):
            return True

        return False

    # ========================================================
    # MAP REFERENCE
    # ========================================================

    map_match = re.match(
        r"^map\s*(\d+)([a-z]?)$",
        reference,
    )

    if map_match:

        number = map_match.group(1)
        suffix = map_match.group(2)

        pattern = (
            rf"\bmap\s*"
            rf"{re.escape(number)}"
            rf"{re.escape(suffix)}\b"
        )

        if re.search(pattern, caption):
            return True

        if re.search(pattern, title):
            return True

        if re.search(pattern, document_text):
            return True

        return False

    return False


# ============================================================
# Main Retrieval
# ============================================================

def retrieve(
    query: str,
    top_k: int = 5,
) -> dict[str, Any]:

    client = get_client()

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    query_embedding = embed_texts(
        [query]
    )[0]

    # ========================================================
    # 1. Normal semantic retrieval
    # ========================================================

    semantic_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    # ========================================================
    # 2. Check for explicit Figure / Map reference
    # ========================================================

    reference = extract_reference(query)

    if not reference:
        return semantic_results

    # ========================================================
    # 3. Deterministic reference search
    #
    # IMPORTANT:
    # Do NOT rely on vector similarity to find Figure 23.
    # Search indexed metadata/document content directly.
    # ========================================================

    all_items = collection.get(
        include=[
            "documents",
            "metadatas",
        ],
    )

    all_documents = all_items.get(
        "documents",
        [],
    )

    all_metadatas = all_items.get(
        "metadatas",
        [],
    )

    reference_matches_found = []

    for document, metadata in zip(
        all_documents,
        all_metadatas,
    ):

        if reference_matches(
            reference=reference,
            document=document,
            metadata=metadata,
        ):

            reference_matches_found.append(
                {
                    "document": document,
                    "metadata": metadata,
                }
            )

    # ========================================================
    # 4. If exact Figure / Map was found,
    #    put it BEFORE semantic results.
    # ========================================================

    if reference_matches_found:

        final_documents = []
        final_metadatas = []
        final_distances = []
        final_ids = []

        # ----------------------------------------------------
        # Exact reference matches FIRST
        # ----------------------------------------------------

        for item in reference_matches_found:

            metadata = item["metadata"]

            final_documents.append(
                item["document"]
            )

            final_metadatas.append(
                metadata
            )

            # Exact reference = perfect distance.
            final_distances.append(
                0.0
            )

            final_ids.append(
                f"reference_{metadata.get('page', 'unknown')}"
            )

        # ----------------------------------------------------
        # Add semantic results
        # ----------------------------------------------------

        semantic_documents = semantic_results[
            "documents"
        ][0]

        semantic_metadatas = semantic_results[
            "metadatas"
        ][0]

        semantic_distances = semantic_results[
            "distances"
        ][0]

        semantic_ids = semantic_results.get(
            "ids",
            [[]],
        )[0]

        for index, (
            document,
            metadata,
            distance,
        ) in enumerate(
            zip(
                semantic_documents,
                semantic_metadatas,
                semantic_distances,
            )
        ):

            page = metadata.get("page")

            # Don't duplicate exact reference result.
            already_added = any(
                existing.get("page") == page
                for existing in final_metadatas
            )

            if already_added:
                continue

            final_documents.append(
                document
            )

            final_metadatas.append(
                metadata
            )

            final_distances.append(
                distance
            )

            if index < len(semantic_ids):

                final_ids.append(
                    semantic_ids[index]
                )

            else:

                final_ids.append(
                    f"semantic_{page}"
                )

            if len(final_documents) >= top_k:
                break

        return {
            "documents": [
                final_documents[:top_k]
            ],
            "metadatas": [
                final_metadatas[:top_k]
            ],
            "distances": [
                final_distances[:top_k]
            ],
            "ids": [
                final_ids[:top_k]
            ],
        }

    # ========================================================
    # 5. No exact reference found
    #    Fall back to semantic retrieval.
    # ========================================================

    return semantic_results


# ============================================================
# Grounded Retrieval
# ============================================================

def retrieve_grounded_evidence(
    query: str,
    top_k: int = 5,
    min_score: float = 0.55,
) -> list[dict[str, Any]]:

    results = retrieve(
        query=query,
        top_k=top_k,
    )

    # --------------------------------------------------------
    # Normal reranking
    # --------------------------------------------------------

    ranked = rerank_results(
        query=query,
        results=results,
    )

    # ========================================================
    # Explicit Figure / Map Priority
    # ========================================================
    #
    # If the user explicitly asks:
    #
    #   Figure 23
    #   Fig. 23
    #   Map 1a
    #
    # the exact referenced visual MUST remain first.
    #
    # We therefore give it an absolute priority score.
    # ========================================================

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

                # ------------------------------------------------
                # Absolute priority.
                #
                # This prevents semantic reranking from moving
                # another visually similar result above it.
                # ------------------------------------------------

                result["rerank_score"] = 999.0

                exact_results.append(
                    result
                )

            else:

                other_results.append(
                    result
                )

        # Exact Figure / Map first.
        ranked = (
            exact_results
            + other_results
        )

    # ========================================================
    # Evidence Gate
    # ========================================================

    gate = validate_evidence(
        ranked,
        min_score=min_score,
    )

    if not gate["sufficient"]:
        return []

    # ========================================================
    # Build grounded evidence
    # ========================================================

    evidence = []

    for result in gate["evidence"]:

        metadata = result["metadata"]

        evidence.append(
            {
                "text": result["document"],

                "document_id": metadata.get(
                    "document_id",
                    "N/A",
                ),

                "page": metadata.get(
                    "page",
                    "N/A",
                ),

                "section": metadata.get(
                    "section",
                    metadata.get(
                        "semantic_title",
                        "N/A",
                    ),
                ),

                "chunk_id": result.get(
                    "chunk_id",
                    "N/A",
                ),

                "content_type": metadata.get(
                    "visual_type",
                    "visual",
                ),

                "citation": (
                    f"{metadata.get('document_id', 'N/A')}"
                    f" - page {metadata.get('page', 'N/A')}"
                ),
            }
        )

    return evidence