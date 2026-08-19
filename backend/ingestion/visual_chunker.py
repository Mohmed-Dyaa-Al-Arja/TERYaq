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
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Visual evidence not found: {INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            "visual_extracted_evidence.json must contain a list."
        )

    return data


def clean_items(items: Any) -> list[str]:
    if not isinstance(items, list):
        return []

    result = []

    for item in items:
        text = str(item).strip()

        if text and text not in result:
            result.append(text)

    return result


def build_visual_text(
    evidence: dict[str, Any]
) -> str:

    parts = []

    title = evidence.get(
        "semantic_title",
        ""
    )

    if title:
        parts.append(
            f"Visual title: {title}"
        )

    visual_type = evidence.get(
        "visual_type",
        "unknown"
    )

    parts.append(
        f"Visual type: {visual_type}"
    )

    caption = evidence.get(
        "source_caption",
        ""
    )

    if caption and caption != "not available":
        parts.append(
            f"Source caption: {caption}"
        )

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
            evidence.get(key, [])
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

    return "\n".join(parts)


def create_visual_chunk(
    item: dict[str, Any]
) -> dict[str, Any]:

    evidence = item.get(
        "visual_evidence",
        {}
    )

    document_id = item.get(
        "document_id",
        "unknown"
    )

    page = item.get(
        "page",
        "unknown"
    )

    visual_type = evidence.get(
        "visual_type",
        "unknown"
    )

    chunk_id = (
        f"{document_id}"
        f"_page_{page}"
        f"_visual"
    )

    text = build_visual_text(
        evidence
    )

    return {
        "chunk_id": chunk_id,

        "text": text,

        "metadata": {
            "document_id": document_id,

            "document": item.get(
                "document",
                "unknown"
            ),

            "page": page,

            "source_type": "visual",

            "visual_type": visual_type,

            "image_path": item.get(
                "image_path",
                ""
            ),

            "semantic_title": evidence.get(
                "semantic_title",
                ""
            ),

            "source_caption": evidence.get(
                "source_caption",
                ""
            ),

            "extraction_model": item.get(
                "extraction_model",
                ""
            ),
        }
    }


def build_visual_chunks() -> list[dict[str, Any]]:

    evidence_items = load_evidence()

    chunks = []

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
                f"Skipping visual item: {exc}"
            )

    return chunks


def save_chunks(
    chunks: list[dict[str, Any]]
):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            chunks,
            f,
            ensure_ascii=False,
            indent=2
        )


def main():

    print("=" * 70)
    print("TERYaq - VISUAL CHUNK BUILDER")
    print("=" * 70)

    chunks = build_visual_chunks()

    save_chunks(chunks)

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