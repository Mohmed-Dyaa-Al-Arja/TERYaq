"""Knowledge-base indexing entry point."""

from __future__ import annotations

import re

from langchain_core.documents import Document

from backend.embedding.vector_store import build_vector_store

from .chunker import chunk_documents
from .pdf_loader import load_all_pdfs


def _make_document_id(
    page: Document,
    index: int,
) -> str:
    """
    Build a stable document ID from page metadata.

    Priority:
        1. Existing document_id
        2. source_file
        3. source
        4. fallback ID
    """

    metadata = page.metadata or {}

    existing_id = metadata.get(
        "document_id"
    )

    if existing_id:
        return str(
            existing_id
        )

    source = (
        metadata.get(
            "source_file"
        )
        or metadata.get(
            "source"
        )
        or ""
    )

    if source:

        source_name = str(
            source
        )

        # Keep only filename if a full path exists.
        source_name = (
            source_name
            .replace("\\", "/")
            .split("/")[-1]
        )

        # Remove extension.
        source_name = re.sub(
            r"\.[^.]+$",
            "",
            source_name,
        )

        # Normalize ID.
        source_name = re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            source_name,
        ).strip("_")

        if source_name:
            return source_name

    return f"document_{index}"


def _ensure_page_metadata(
    pages: list[Document],
) -> list[Document]:
    """
    Ensure every PDF page contains the metadata required
    by the chunking pipeline.
    """

    for index, page in enumerate(
        pages
    ):

        if page.metadata is None:
            page.metadata = {}

        metadata = page.metadata

        # -----------------------------------------------------
        # document_id
        # -----------------------------------------------------

        document_id = _make_document_id(
            page,
            index,
        )

        metadata[
            "document_id"
        ] = document_id

        # -----------------------------------------------------
        # source_file
        # -----------------------------------------------------

        if not metadata.get(
            "source_file"
        ):

            source = metadata.get(
                "source"
            )

            if source:
                metadata[
                    "source_file"
                ] = str(
                    source
                ).replace(
                    "\\",
                    "/",
                ).split("/")[-1]

        # -----------------------------------------------------
        # page number
        # -----------------------------------------------------

        if "page" not in metadata:
            metadata[
                "page"
            ] = index

        # -----------------------------------------------------
        # Content type
        # -----------------------------------------------------

        if not metadata.get(
            "content_type"
        ):
            metadata[
                "content_type"
            ] = "text"

        # -----------------------------------------------------
        # Source type
        # -----------------------------------------------------

        if not metadata.get(
            "source_type"
        ):
            metadata[
                "source_type"
            ] = "text"

    return pages


def build_medical_index(
    reset: bool = True,
) -> tuple[list[Document], object]:
    """
    Build the unified TERYaq knowledge index.

    Sources:
        1. PDF text chunks
        2. Visual evidence extracted from images/figures

    Both sources are indexed into the same Chroma collection.
    """

    print("=" * 80)
    print(
        "TERYaq - UNIFIED MEDICAL KNOWLEDGE INDEX"
    )
    print("=" * 80)

    # =========================================================
    # 1. Load PDF pages
    # =========================================================

    print()
    print(
        "[1/4] Loading PDF documents..."
    )

    pages = load_all_pdfs()

    print(
        f"Loaded pages: {len(pages)}"
    )

    if not pages:
        raise ValueError(
            "No PDF pages were loaded."
        )

    # =========================================================
    # 2. Ensure required metadata
    # =========================================================

    print()
    print(
        "[2/4] Preparing page metadata..."
    )

    pages = _ensure_page_metadata(
        pages
    )

    document_ids = sorted(
        {
            str(
                page.metadata.get(
                    "document_id"
                )
            )
            for page in pages
        }
    )

    print(
        f"Documents detected: "
        f"{len(document_ids)}"
    )

    for document_id in document_ids:
        print(
            f"  - {document_id}"
        )

    # =========================================================
    # 3. Create text chunks
    # =========================================================

    print()
    print(
        "[3/4] Creating text chunks..."
    )

    text_chunks = chunk_documents(
        pages
    )

    print(
        f"Text chunks: "
        f"{len(text_chunks)}"
    )

    # =========================================================
    # 4. Build unified vector store
    # =========================================================

    print()
    print(
        "[4/4] Building unified vector store..."
    )

    vector_store = build_vector_store(
        text_chunks=text_chunks,
        reset=reset,
    )

    # =========================================================
    # Summary
    # =========================================================

    print()
    print(
        "=" * 80
    )
    print(
        "INDEXING COMPLETED"
    )
    print(
        "=" * 80
    )

    try:
        count = (
            vector_store
            ._collection
            .count()
        )

        print(
            f"Collection count: {count}"
        )

    except Exception:
        pass

    print(
        "=" * 80
    )

    return (
        text_chunks,
        vector_store,
    )


if __name__ == "__main__":

    build_medical_index(
        reset=True
    )