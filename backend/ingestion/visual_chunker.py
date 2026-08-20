"""Build searchable chunks from extracted visual evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "processed"
    / "metadata"
    / "visual_extracted_evidence.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "processed"
    / "chunks"
    / "visual_chunks.json"
)


def load_evidence() -> list[dict[str, Any]]:
    """Load visual evidence JSON."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Visual evidence not found: {INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "visual_extracted_evidence.json "
            "must contain a list."
        )

    return data


def clean_items(
    items: Any,
) -> list[str]:
    """Normalize list-like evidence fields."""

    if not isinstance(items, list):
        return []

    result: list[str] = []

    for item in items:

        text = str(
            item
        ).strip()

        if text and text not in result:
            result.append(text)

    return result


def build_visual_text(
    evidence: dict[str, Any],
) -> str:
    """
    Convert structured visual evidence into
    searchable natural-language text.
    """

    parts: list[str] = []

    # ---------------------------------------------------------
    # Title
    # ---------------------------------------------------------

    title = str(
        evidence.get(
            "semantic_title",
            "",
        )
    ).strip()

    if title:
        parts.append(
            f"Visual title: {title}"
        )

    # ---------------------------------------------------------
    # Visual type
    # ---------------------------------------------------------

    visual_type = str(
        evidence.get(
            "visual_type",
            "unknown",
        )
    ).strip()

    parts.append(
        f"Visual type: {visual_type}"
    )

    # ---------------------------------------------------------
    # Caption
    # ---------------------------------------------------------

    caption = str(
        evidence.get(
            "source_caption",
            "",
        )
    ).strip()

    if (
        caption
        and caption.lower() != "not available"
    ):
        parts.append(
            f"Source caption: {caption}"
        )

    # ---------------------------------------------------------
    # Structured evidence
    # ---------------------------------------------------------

    fields = [
        ("Visible text", "visible_text"),
        ("Labels", "labels"),
        ("Legend", "legend"),
        ("Axes", "axes"),
        ("Categories", "categories"),
        ("Explicit values", "explicit_values"),
        ("Relationships", "relationships"),
        ("Visible observations", "visible_observations"),
        ("Uncertainties", "uncertainties"),
    ]

    for label, key in fields:

        values = clean_items(
            evidence.get(
                key,
                [],
            )
        )

        if not values:
            continue

        parts.append(
            f"{label}:"
        )

        for value in values:
            parts.append(
                f"- {value}"
            )

    return "\n".join(
        parts
    )


def create_visual_chunk(
    item: dict[str, Any],
) -> dict[str, Any]:
    """Create one normalized visual chunk."""

    evidence = item.get(
        "visual_evidence",
        {},
    )

    if not isinstance(
        evidence,
        dict,
    ):
        evidence = {}

    document_id = str(
        item.get(
            "document_id",
            "unknown",
        )
    )

    page = item.get(
        "page",
        "unknown",
    )

    visual_type = str(
        evidence.get(
            "visual_type",
            "unknown",
        )
    )

    semantic_title = str(
        evidence.get(
            "semantic_title",
            "",
        )
    )

    source_caption = str(
        evidence.get(
            "source_caption",
            "",
        )
    )

    # ---------------------------------------------------------
    # Stable ID
    # ---------------------------------------------------------

    chunk_id = (
        f"{document_id}"
        f"_page_{page}"
        f"_visual"
    )

    # ---------------------------------------------------------
    # Searchable text
    # ---------------------------------------------------------

    text = build_visual_text(
        evidence
    )

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    metadata = {
        "document_id": document_id,

        "document": str(
            item.get(
                "document",
                document_id,
            )
        ),

        "page": str(page),

        # Important:
        # Both source_type and content_type are kept
        # for backward compatibility.
        "source_type": "visual",
        "content_type": "visual",

        "visual_type": visual_type,

        "image_path": str(
            item.get(
                "image_path",
                "",
            )
        ),

        "semantic_title": semantic_title,

        "source_caption": source_caption,

        "extraction_model": str(
            item.get(
                "extraction_model",
                "",
            )
        ),
    }

    return {
        "chunk_id": chunk_id,
        "text": text,
        "metadata": metadata,
    }


def build_visual_chunks() -> list[dict[str, Any]]:
    """Build all visual chunks."""

    evidence_items = load_evidence()

    chunks: list[
        dict[str, Any]
    ] = []

    for item in evidence_items:

        try:

            chunk = create_visual_chunk(
                item
            )

            if chunk["text"].strip():
                chunks.append(
                    chunk
                )

        except Exception as exc:

            print(
                "Skipping visual item: "
                f"{exc}"
            )

    return chunks


def save_chunks(
    chunks: list[dict[str, Any]],
) -> None:
    """Save normalized visual chunks."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2,
        )


def main() -> None:

    print("=" * 70)
    print(
        "TERYaq - VISUAL CHUNK BUILDER"
    )
    print("=" * 70)

    chunks = build_visual_chunks()

    save_chunks(
        chunks
    )

    print()
    print(
        f"Visual evidence items: "
        f"{len(chunks)}"
    )

    print(
        f"Output: "
        f"{OUTPUT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()