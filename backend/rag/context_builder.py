"""Build the grounded evidence context."""

from __future__ import annotations


def build_context(evidence: list[dict]) -> str:
    """Render accepted evidence into a traceable context string."""
    if not evidence:
        return ""

    blocks = []

    for index, item in enumerate(
        evidence,
        start=1,
    ):
        blocks.append(
            f"""
[EVIDENCE {index}]
Citation: {item.get("citation", "N/A")}
Document: {item.get("document_id", "N/A")}
Page: {item.get("page", "N/A")}
Section: {item.get("section", "N/A")}
Chunk: {item.get("chunk_id", "N/A")}
Type: {item.get("content_type", "text")}

{item.get("text", "")}
""".strip()
        )

    return "\n\n".join(blocks)