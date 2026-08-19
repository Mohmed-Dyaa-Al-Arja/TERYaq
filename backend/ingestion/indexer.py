"""Knowledge-base indexing entry point."""

from __future__ import annotations

from langchain_core.documents import Document

from backend.embedding.vector_store import build_vector_store
from .chunker import chunk_documents
from .pdf_loader import load_all_pdfs


def build_medical_index() -> tuple[list[Document], object]:
    """Load PDFs, chunk them and index the text evidence."""
    pages = load_all_pdfs()
    chunks = chunk_documents(pages)
    vector_store = build_vector_store(chunks)
    return chunks, vector_store
