"""Section-aware text chunking based on the evaluated notebook."""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .metadata_builder import build_document_metadata


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


# ============================================================
# Document Configuration
# ============================================================

DOCUMENT_CONFIG = {

    # --------------------------------------------------------
    # WHO Global Breast Cancer Initiative
    # --------------------------------------------------------

    "9789240065987-eng": {
        "source": "WHO",
        "title": (
            "Global Breast Cancer Initiative "
            "Implementation Framework"
        ),
        "publication_year": 2023,
    },

    # --------------------------------------------------------
    # USPSTF Breast Cancer Screening
    # --------------------------------------------------------

    "breast-cancer-screening-final-rec": {
        "source": "USPSTF",
        "title": "Screening for Breast Cancer",
        "publication_year": 2024,
    },

    # --------------------------------------------------------
    # Backward compatibility
    # --------------------------------------------------------

    "WHO-BC-2023-001": {
        "source": "WHO",
        "title": (
            "Global Breast Cancer Initiative "
            "Implementation Framework"
        ),
        "publication_year": 2023,
    },

    "USPSTF-BC-2024-001": {
        "source": "USPSTF",
        "title": "Screening for Breast Cancer",
        "publication_year": 2024,
    },
}


# ============================================================
# Heading Detection
# ============================================================

def is_heading(line: str) -> bool:

    line = line.strip()

    if not line or len(line) > 80:
        return False

    if line.endswith(
        (".", ",", ";", ":", "?", "!")
    ):
        return False

    words = line.split()

    if len(words) > 8:
        return False

    # Numbered heading
    if re.match(
        r"^\d+(?:\.\d+)*\.?\s+[A-Z]",
        line,
    ):
        return True

    letters = [
        c
        for c in line
        if c.isalpha()
    ]

    if letters:

        uppercase_ratio = (
            sum(
                c.isupper()
                for c in letters
            )
            / len(letters)
        )

        if (
            uppercase_ratio >= 0.75
            and len(words) <= 8
        ):
            return True

    capitalized_words = sum(
        1
        for word in words
        if word
        and word[0].isupper()
    )

    return (
        len(words) <= 6
        and capitalized_words
        >= max(
            1,
            len(words) * 0.6,
        )
    )


# ============================================================
# Section Splitting
# ============================================================

def split_into_sections(
    page_text: str,
) -> list[dict[str, str]]:
    """Split one page into heading-aware sections."""

    lines = page_text.splitlines()

    sections = []

    current_section = "General"
    current_text: list[str] = []

    for line in lines:

        stripped = line.strip()

        if is_heading(stripped):

            if current_text:

                text = (
                    "\n".join(
                        current_text
                    ).strip()
                )

                if text:

                    sections.append(
                        {
                            "section": current_section,
                            "text": text,
                        }
                    )

            current_section = stripped
            current_text = []

        else:

            current_text.append(line)

    if current_text:

        text = (
            "\n".join(
                current_text
            ).strip()
        )

        if text:

            sections.append(
                {
                    "section": current_section,
                    "text": text,
                }
            )

    return sections


# ============================================================
# Document Configuration
# ============================================================

def _document_config(
    document_id: str,
) -> dict:

    if document_id not in DOCUMENT_CONFIG:

        raise KeyError(
            f"No document configuration for "
            f"{document_id}. "
            f"Available configurations: "
            f"{list(DOCUMENT_CONFIG.keys())}"
        )

    return DOCUMENT_CONFIG[
        document_id
    ]


# ============================================================
# Chunking
# ============================================================

def chunk_documents(
    pages: Iterable[Document],
) -> list[Document]:
    """
    Create final 1000/200 chunks with stable metadata.

    Each page must contain a document_id.
    """

    splitter = (
        RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )
    )

    chunks: list[Document] = []

    counters: Counter[str] = Counter()

    # --------------------------------------------------------
    # Process every page
    # --------------------------------------------------------

    for page in pages:

        document_id = page.metadata.get(
            "document_id"
        )

        if not document_id:

            raise ValueError(
                "Every page must contain "
                "document_id before chunking."
            )

        config = _document_config(
            str(document_id)
        )

        # ----------------------------------------------------
        # Page number
        # ----------------------------------------------------

        page_number = int(
            page.metadata.get(
                "page_number",
                page.metadata.get(
                    "page",
                    0,
                ) + 1,
            )
        )

        # ----------------------------------------------------
        # Sections
        # ----------------------------------------------------

        sections = split_into_sections(
            page.page_content
        )

        if not sections:

            sections = [
                {
                    "section": "General",
                    "text": page.page_content,
                }
            ]

        # ----------------------------------------------------
        # Create chunks
        # ----------------------------------------------------

        for section in sections:

            section_name = (
                section[
                    "section"
                ].strip()
            )

            section_text = (
                section[
                    "text"
                ].strip()
            )

            if not section_text:
                continue

            section_chunks = (
                splitter.create_documents(
                    [section_text]
                )
            )

            for chunk in section_chunks:

                counters[
                    str(document_id)
                ] += 1

                chunk_index = counters[
                    str(document_id)
                ]

                chunk_id = (
                    f"{document_id}"
                    f"-CH-"
                    f"{chunk_index:04d}"
                )

                chunk.metadata = (
                    build_document_metadata(
                        document_id=str(
                            document_id
                        ),
                        source=config[
                            "source"
                        ],
                        title=config[
                            "title"
                        ],
                        publication_year=config[
                            "publication_year"
                        ],
                        page_number=page_number,
                        section=section_name,
                        chunk_id=chunk_id,
                        content_type="text",
                        source_file=(
                            page.metadata.get(
                                "source_file"
                            )
                        ),
                    )
                )

                chunks.append(
                    chunk
                )

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    if not chunks:

        raise RuntimeError(
            "Chunking produced zero chunks."
        )

    print()
    print(
        "Chunking summary:"
    )

    for document_id, count in counters.items():

        print(
            f"  {document_id}: "
            f"{count} chunks"
        )

    print(
        f"  Total: {len(chunks)} chunks"
    )

    return chunks