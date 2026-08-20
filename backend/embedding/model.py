from __future__ import annotations

from fastembed import TextEmbedding

from .config import EMBEDDING_MODEL_NAME


_embedding_model: TextEmbedding | None = None


def get_embedding_model() -> TextEmbedding:
    """Return the cached embedding model."""

    global _embedding_model

    if _embedding_model is None:

        print(
            f"Loading embedding model: "
            f"{EMBEDDING_MODEL_NAME}"
        )

        _embedding_model = TextEmbedding(
            model_name=EMBEDDING_MODEL_NAME
        )

    return _embedding_model


def embed_texts(
    texts: list[str],
) -> list[list[float]]:
    """Generate embeddings for a list of texts."""

    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.embed(
        texts
    )

    return [
        embedding.tolist()
        for embedding in embeddings
    ]