from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import chromadb
from langchain_core.documents import Document
from langchain_chroma import Chroma

from .config import (
    COLLECTION_NAME,
    VECTOR_STORE_DIR,
)
from .model import embed_texts


BASE_DIR = Path(__file__).resolve().parents[2]

VISUAL_CHUNKS_FILE = (
    BASE_DIR
    / "processed"
    / "chunks"
    / "visual_chunks.json"
)


# ============================================================
# Chroma Client
# ============================================================

def get_client():

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    return chromadb.PersistentClient(
        path=str(
            VECTOR_STORE_DIR
        )
    )


# ============================================================
# Visual chunks
# ============================================================

def load_visual_chunks() -> list[dict[str, Any]]:
    """Load normalized visual chunks."""

    if not VISUAL_CHUNKS_FILE.exists():
        return []

    with open(
        VISUAL_CHUNKS_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    if not isinstance(
        data,
        list,
    ):
        return []

    return data


# ============================================================
# Text normalization
# ============================================================

def prepare_text_chunks(
    chunks: list[Document],
) -> list[dict[str, Any]]:
    """
    Convert LangChain text Documents into the same
    normalized structure used by visual chunks.
    """

    prepared: list[
        dict[str, Any]
    ] = []

    for index, document in enumerate(
        chunks
    ):

        text = str(
            document.page_content
        ).strip()

        if not text:
            continue

        raw_metadata = (
            document.metadata
            or {}
        )

        metadata = {
            "document_id": str(
                raw_metadata.get(
                    "document_id",
                    raw_metadata.get(
                        "source_file",
                        raw_metadata.get(
                            "source",
                            "unknown",
                        ),
                    ),
                )
            ),

            "document": str(
                raw_metadata.get(
                    "source_file",
                    raw_metadata.get(
                        "source",
                        "unknown",
                    ),
                )
            ),

            "page": str(
                raw_metadata.get(
                    "page_number",       # metadata_builder stores page as page_number
                    raw_metadata.get(
                        "page",          # fallback for legacy chunks
                        "unknown",
                    ),
                )
            ),

            "content_type": str(
                raw_metadata.get(
                    "content_type",
                    "text",
                )
            ),

            "source_type": "text",

            "semantic_title": str(
                raw_metadata.get(
                    "semantic_title",
                    "",
                )
            ),

            "source_caption": str(
                raw_metadata.get(
                    "source_caption",
                    "",
                )
            ),

            "visual_type": str(
                raw_metadata.get(
                    "visual_type",
                    "",
                )
            ),

            "section": str(
                raw_metadata.get(
                    "section",
                    "",
                )
            ),
        }

        # Stable text ID.
        chunk_id = str(
            raw_metadata.get(
                "chunk_id",
                f"text_chunk_{index}",
            )
        )

        # Prevent collision with visual IDs.
        chunk_id = (
            f"text::{chunk_id}"
        )

        prepared.append(
            {
                "chunk_id": chunk_id,
                "text": text,
                "metadata": metadata,
            }
        )

    return prepared


# ============================================================
# Unified chunks
# ============================================================

def build_unified_chunks(
    text_chunks: list[Document],
) -> list[dict[str, Any]]:
    """
    Combine PDF text chunks and visual evidence
    into one normalized collection.
    """

    text_items = prepare_text_chunks(
        text_chunks
    )

    visual_items = load_visual_chunks()

    normalized_visual_items: list[
        dict[str, Any]
    ] = []

    for item in visual_items:

        text = str(
            item.get(
                "text",
                "",
            )
        ).strip()

        if not text:
            continue

        metadata = (
            item.get(
                "metadata",
                {}
            )
            or {}
        )

        # Ensure required fields exist.
        metadata = {
            **metadata,

            "content_type": "visual",

            "source_type": "visual",
        }

        normalized_visual_items.append(
            {
                "chunk_id": str(
                    item.get(
                        "chunk_id"
                    )
                ),
                "text": text,
                "metadata": metadata,
            }
        )

    return (
        text_items
        + normalized_visual_items
    )


# ============================================================
# Build Chroma collection
# ============================================================

def build_vector_store(
    text_chunks: list[Document],
    reset: bool = True,
):
    """
    Build the unified Chroma vector store.

    Indexed sources:
        - PDF text
        - Visual evidence

    Both are stored in the same collection.
    """

    client = get_client()

    # --------------------------------------------------------
    # Reset old collection when rebuilding.
    # --------------------------------------------------------

    if reset:

        try:

            client.delete_collection(
                name=COLLECTION_NAME
            )

            print(
                f"Deleted old collection: "
                f"{COLLECTION_NAME}"
            )

        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine"
        },
    )

    # --------------------------------------------------------
    # Build unified dataset
    # --------------------------------------------------------

    unified_chunks = build_unified_chunks(
        text_chunks
    )

    if not unified_chunks:
        raise ValueError(
            "No text or visual chunks available."
        )

    print("=" * 80)
    print(
        "TERYaq - UNIFIED VECTOR STORE"
    )
    print("=" * 80)

    text_count = sum(
        1
        for item in unified_chunks
        if item["metadata"].get(
            "content_type"
        ) == "text"
    )

    visual_count = sum(
        1
        for item in unified_chunks
        if item["metadata"].get(
            "content_type"
        ) == "visual"
    )

    print(
        f"Text chunks: {text_count}"
    )

    print(
        f"Visual chunks: {visual_count}"
    )

    print(
        f"Total chunks: "
        f"{len(unified_chunks)}"
    )

    # --------------------------------------------------------
    # Prepare embedding input
    # --------------------------------------------------------

    ids = [
        item["chunk_id"]
        for item in unified_chunks
    ]

    texts = [
        item["text"]
        for item in unified_chunks
    ]

    metadatas = [
        item["metadata"]
        for item in unified_chunks
    ]

    # --------------------------------------------------------
    # Embeddings
    # --------------------------------------------------------

    print()
    print(
        "Generating embeddings..."
    )

    embeddings = embed_texts(
        texts
    )

    if not embeddings:
        raise RuntimeError(
            "Embedding generation returned no vectors."
        )

    print(
        f"Embedding dimension: "
        f"{len(embeddings[0])}"
    )

    # --------------------------------------------------------
    # Upsert
    # --------------------------------------------------------

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print()
    print(
        f"Collection: "
        f"{COLLECTION_NAME}"
    )

    print(
        f"Collection count: "
        f"{collection.count()}"
    )

    print(
        f"Vector store: "
        f"{VECTOR_STORE_DIR}"
    )

    print("=" * 80)

    # --------------------------------------------------------
    # Return LangChain Chroma object
    # --------------------------------------------------------

    return Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
    )


# ============================================================
# Backward-compatible visual builder
# ============================================================

def build_visual_collection():

    from backend.ingestion.visual_chunker import (
        build_visual_chunks,
    )

    chunks = build_visual_chunks()

    if not chunks:
        raise ValueError(
            "No visual chunks found."
        )

    client = get_client()

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine"
        },
    )

    ids = [
        chunk["chunk_id"]
        for chunk in chunks
    ]

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    metadatas = [
        chunk["metadata"]
        for chunk in chunks
    ]

    embeddings = embed_texts(
        texts
    )

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return collection