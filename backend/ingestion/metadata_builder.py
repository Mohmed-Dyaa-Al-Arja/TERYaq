"""Medical document metadata utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def build_document_metadata(
    *,
    document_id: str,
    source: str,
    title: str,
    publication_year: int | None,
    page_number: int,
    section: str,
    chunk_id: str,
    content_type: str = "text",
    source_file: str | None = None,
    image_path: str | None = None,
) -> dict[str, Any]:
    """Build a stable metadata record for retrieval and citations."""
    return {
        "document_id": document_id,
        "source": source,
        "title": title,
        "publication_year": publication_year,
        "page_number": page_number,
        "section": section,
        "chunk_id": chunk_id,
        "content_type": content_type,
        "source_file": source_file,
        "image_path": image_path,
    }
