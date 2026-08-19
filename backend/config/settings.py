"""Application settings for Teryaq."""

from __future__ import annotations

from backend.embedding.config import (
    EMBEDDING_MODEL_NAME,
    VECTOR_COLLECTION_NAME,
    VECTOR_STORE_DIR,
    TOP_K,
    RETRIEVAL_THRESHOLD,
)
from backend.llm.config import (
    PROVIDER,
    MODEL_NAME,
    TEMPERATURE,
    MAX_TOKENS,
)


class Settings:
    provider = PROVIDER
    llm_model = MODEL_NAME
    temperature = TEMPERATURE
    max_tokens = MAX_TOKENS

    embedding_model = EMBEDDING_MODEL_NAME
    vector_collection = VECTOR_COLLECTION_NAME
    vector_store_dir = VECTOR_STORE_DIR

    top_k = TOP_K
    retrieval_threshold = RETRIEVAL_THRESHOLD


settings = Settings()
