from __future__ import annotations

import json
from pathlib import Path

import chromadb

from .config import (
    COLLECTION_NAME,
    VECTOR_STORE_DIR,
)
from .model import embed_texts


BASE_DIR = Path(__file__).resolve().parents[2]

CHUNKS_FILE = (
    BASE_DIR
    / "processed"
    / "chunks"
    / "visual_chunks.json"
)


def load_chunks():
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"Chunks not found: {CHUNKS_FILE}"
        )

    with open(
        CHUNKS_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def get_client():

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    return chromadb.PersistentClient(
        path=str(VECTOR_STORE_DIR)
    )


def build_visual_collection():

    chunks = load_chunks()

    if not chunks:
        raise ValueError(
            "No visual chunks found."
        )

    client = get_client()

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine"
        }
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

    print("=" * 70)
    print("TERYaq - VISUAL EMBEDDING")
    print("=" * 70)

    print(
        f"Chunks: {len(chunks)}"
    )

    print(
        f"Model: "
        f"{__import__('backend.embedding.config', fromlist=['EMBEDDING_MODEL_NAME']).EMBEDDING_MODEL_NAME}"
    )

    print(
        "Generating embeddings..."
    )

    embeddings = embed_texts(
        texts
    )

    print(
        f"Embedding dimension: "
        f"{len(embeddings[0])}"
    )

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print()
    print(
        f"Indexed: "
        f"{collection.count()}"
    )

    print(
        f"Collection: "
        f"{COLLECTION_NAME}"
    )

    print(
        f"Vector store: "
        f"{VECTOR_STORE_DIR}"
    )

    print("=" * 70)

    return collection


if __name__ == "__main__":
    build_visual_collection()