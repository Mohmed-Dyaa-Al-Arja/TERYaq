"""Claim-level grounding verification."""

from __future__ import annotations

from backend.llm.client import get_grounded_llm
from backend.safety.evidence_validator import normalize_citation


def verify_claims(
    result: dict,
    evidence: list[dict],
) -> dict:
    """Verify that each cited claim is supported by its cited evidence.

    This keeps the same evidence-only principle used in the notebook.
    """
    evidence_map = {
        normalize_citation(item.get("citation")): item.get("text", "")
        for item in evidence
        if item.get("citation")
    }

    results = []

    for claim in result.get("claims", []):
        citation = normalize_citation(
            claim.get("citation")
        )
        evidence_text = evidence_map.get(citation)

        if not evidence_text:
            results.append(
                {
                    "claim": claim.get("text", ""),
                    "citation": citation,
                    "supported": False,
                    "reason": "Citation was not found in retrieved evidence.",
                }
            )
            continue

        prompt = f"""
You are a strict evidence-grounding evaluator.

Use ONLY the evidence below.

Claim:
{claim.get("text", "")}

Citation:
{citation}

Evidence:
{evidence_text}

Return ONLY JSON:
{{
  "supported": true,
  "reason": "..."
}}

Set supported=true ONLY when the evidence directly supports
or clearly entails the claim.
""".strip()

        response = get_grounded_llm().invoke(prompt)
        raw = getattr(response, "content", str(response))

        # The LLM is only used as a claim-support evaluator;
        # the final pipeline still fails closed if verification fails.
        import json
        try:
            evaluation = json.loads(raw)
        except json.JSONDecodeError:
            evaluation = {
                "supported": False,
                "reason": "Claim verifier returned invalid JSON.",
            }

        results.append(
            {
                "claim": claim.get("text", ""),
                "citation": citation,
                "supported": bool(
                    evaluation.get("supported", False)
                ),
                "reason": evaluation.get("reason", ""),
            }
        )

    passed = bool(results) and all(
        item["supported"] for item in results
    )

    return {
        "passed": passed,
        "claims": results,
    }
