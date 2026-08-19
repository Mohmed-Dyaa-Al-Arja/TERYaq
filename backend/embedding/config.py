from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

VECTOR_STORE_DIR = (
    BASE_DIR / "processed" / "chroma"
)

COLLECTION_NAME = "teryaq_visual"

BATCH_SIZE = 32