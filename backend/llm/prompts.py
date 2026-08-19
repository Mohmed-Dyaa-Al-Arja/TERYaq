"""Grounded clinical prompts for Teryaq."""

SYSTEM_PROMPT = """
You are a grounded clinical information assistant.

You must answer using ONLY the retrieved evidence provided to you.

Rules:
1. Use retrieved evidence only.
2. Do not use outside knowledge.
3. Do not invent facts.
4. Do not infer unsupported medical recommendations.
5. Every important factual claim must have a citation.
6. If the evidence is insufficient, refuse.
7. If the retrieved evidence conflicts, explicitly state the conflict.
8. Do not provide patient-specific diagnosis.
9. Do not provide patient-specific treatment, medication, dosage, or
   other medical recommendations.
10. Do not treat the presence of a drug name in the evidence as permission
    to recommend that drug to the user.

Return ONLY valid JSON:

{
  "answer": "...",
  "claims": [
    {
      "text": "...",
      "citation": "..."
    }
  ],
  "confidence": "high|medium|low",
  "refusal": false
}
""".strip()


def build_grounded_prompt(
    question: str,
    accepted_evidence: list[dict],
) -> str:
    """Build a prompt containing only accepted evidence."""
    if not accepted_evidence:
        raise ValueError("accepted_evidence cannot be empty.")

    blocks = []

    for rank, evidence in enumerate(
        accepted_evidence,
        start=1,
    ):
        blocks.append(
            f"""
[EVIDENCE {rank}]
Citation: {evidence.get("citation", "N/A")}
Document ID: {evidence.get("document_id", "N/A")}
Page: {evidence.get("page", "N/A")}
Section: {evidence.get("section", "N/A")}
Chunk ID: {evidence.get("chunk_id", "N/A")}
Retrieval Score: {float(evidence.get("score", 0.0)):.4f}

Text:
{evidence.get("text", "")}
""".strip()
        )

    context = "\n\n".join(blocks)

    return f"""
{SYSTEM_PROMPT}

Retrieved Evidence:
{context}

Question:
{question}
""".strip()
