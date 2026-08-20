"""Deterministic claim-level grounding verification."""

from __future__ import annotations

import re

from backend.safety.evidence_validator import (
    normalize_citation,
    _citation_document_id,
)


def _normalize_text(text: str) -> str:
    """Normalize text for deterministic comparison."""
    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9%.\- ]+",
        " ",
        text,
    )

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def _tokenize(text: str) -> set[str]:
    """Convert text into normalized tokens."""
    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "of",
        "to",
        "and",
        "or",
        "in",
        "on",
        "for",
        "with",
        "that",
        "this",
        "shows",
        "show",
        "figure",
        "diagram",
        "visual",
    }

    return {
        token
        for token in _normalize_text(text).split()
        if token not in stop_words
        and len(token) > 1
    }


def _ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    """Return all n-grams from a token list."""
    return {
        tuple(tokens[i: i + n])
        for i in range(len(tokens) - n + 1)
    }


def _claim_supported(
    claim_text: str,
    evidence_text: str,
) -> tuple[bool, str]:
    """
    Determine whether a claim is grounded in evidence.

    This verifier intentionally does NOT call the LLM.

    Checks (in order):
      1. Exact claim string present in evidence.
      2. Bigram overlap  ≥ 0.40  (catches paraphrased sentences
         that share key multi-word phrases like "40 to 49 years"
         or "biennial screening mammography").
      3. Key-term anchor  — at least one numeric/clinical token
         from the claim (age ranges, percentages, named entities)
         is present in the evidence.
      4. Unigram token overlap  ≥ 0.50.
    """

    claim_normalized = _normalize_text(claim_text)
    evidence_normalized = _normalize_text(evidence_text)

    if not claim_normalized:
        return False, "Claim is empty."

    if not evidence_normalized:
        return False, "Evidence is empty."

    # ---------------------------------------------------------
    # 1. Exact claim contained in evidence
    # ---------------------------------------------------------

    if claim_normalized in evidence_normalized:
        return (
            True,
            "Claim text is directly present in the retrieved evidence.",
        )

    # ---------------------------------------------------------
    # 2. Bigram overlap
    # ---------------------------------------------------------
    # Bigrams capture multi-word clinical phrases better than
    # single tokens. "biennial screening mammography" and
    # "aged 40 to 49 years" each survive heavy paraphrase as
    # bigrams even when the surrounding sentence is reworded.
    # ---------------------------------------------------------

    claim_token_list = [
        t for t in claim_normalized.split()
        if t not in {
            "the", "a", "an", "is", "are", "was", "were",
            "of", "to", "and", "or", "in", "on", "for",
            "with", "that", "this",
        }
        and len(t) > 1
    ]

    evidence_token_list = [
        t for t in evidence_normalized.split()
        if len(t) > 1
    ]

    if len(claim_token_list) >= 2:
        claim_bigrams = _ngrams(claim_token_list, 2)
        evidence_bigrams = _ngrams(evidence_token_list, 2)

        if claim_bigrams:
            bigram_overlap = (
                len(claim_bigrams & evidence_bigrams)
                / len(claim_bigrams)
            )

            if bigram_overlap >= 0.40:
                return (
                    True,
                    f"Claim has strong bigram support "
                    f"({bigram_overlap:.0%} bigram overlap).",
                )

    # ---------------------------------------------------------
    # 3. Key-term anchor check
    # ---------------------------------------------------------
    # If the claim contains a specific numeric value, age range,
    # or percentage that also appears in the evidence, the claim
    # is almost certainly grounded — even if the surrounding
    # wording is paraphrased.
    #
    # Examples: "40", "49", "50", "74", "60%", "2 months"
    # ---------------------------------------------------------

    key_terms = set(
        re.findall(
            r"\b\d+(?:[%\.]\d+)?\b",
            claim_normalized,
        )
    )

    if key_terms:
        matched_key_terms = key_terms & set(
            re.findall(r"\b\d+(?:[%\.]\d+)?\b", evidence_normalized)
        )

        if len(matched_key_terms) >= min(2, len(key_terms)):
            return (
                True,
                f"Claim is anchored by numeric key terms "
                f"present in the evidence: {matched_key_terms}.",
            )

    # ---------------------------------------------------------
    # 4. Unigram token overlap
    # ---------------------------------------------------------

    claim_tokens = _tokenize(claim_text)
    evidence_tokens = _tokenize(evidence_text)

    if not claim_tokens:
        return False, "Claim contains no usable terms."

    overlap = claim_tokens & evidence_tokens
    overlap_ratio = len(overlap) / len(claim_tokens)

    if overlap_ratio >= 0.50:
        return (
            True,
            f"Claim has sufficient lexical support "
            f"({overlap_ratio:.0%} token overlap).",
        )

    return (
        False,
        f"Insufficient lexical support "
        f"({overlap_ratio:.0%} token overlap, "
        f"overlap tokens: {overlap}).",
    )


def verify_claims(
    result: dict,
    evidence: list[dict],
) -> dict:
    """
    Verify every generated claim against its cited evidence.

    No additional LLM request is made here.
    """

    # Build two lookup maps:
    #   1. full normalized citation  -> text  (exact match)
    #   2. document-id prefix        -> text  (fallback for LLM truncation)
    #
    # The LLM often writes "breast-cancer-screening-final-rec" while
    # the evidence stores "breast-cancer-screening-final-rec - page unknown".
    # We accept either form so that valid, well-grounded claims are not
    # incorrectly rejected because of a citation suffix mismatch.

    evidence_map: dict[str, str] = {}
    evidence_map_by_doc_id: dict[str, str] = {}

    for item in evidence:
        raw = item.get("citation")
        if not raw:
            continue
        full = normalize_citation(raw)
        text = item.get("text", "")
        evidence_map[full] = text
        # doc-id key: keep the longest text if duplicates exist
        doc_id = _citation_document_id(full)
        if doc_id not in evidence_map_by_doc_id:
            evidence_map_by_doc_id[doc_id] = text
        else:
            # Prefer the longer evidence text (more content to verify against)
            if len(text) > len(evidence_map_by_doc_id[doc_id]):
                evidence_map_by_doc_id[doc_id] = text

    results = []

    for claim in result.get("claims", []):

        claim_text = claim.get(
            "text",
            "",
        )

        citation = normalize_citation(
            claim.get("citation")
        )

        # Try full citation first, then fall back to doc-id prefix.
        evidence_text = evidence_map.get(citation)
        if not evidence_text:
            doc_id = _citation_document_id(citation)
            evidence_text = evidence_map_by_doc_id.get(doc_id)

        # -----------------------------------------------------
        # Missing citation
        # -----------------------------------------------------

        if not citation:
            results.append(
                {
                    "claim": claim_text,
                    "citation": citation,
                    "supported": False,
                    "reason": "Claim has no citation.",
                }
            )
            continue

        # -----------------------------------------------------
        # Citation not found
        # -----------------------------------------------------

        if not evidence_text:
            results.append(
                {
                    "claim": claim_text,
                    "citation": citation,
                    "supported": False,
                    "reason": (
                        "Citation was not found "
                        "in retrieved evidence."
                    ),
                }
            )
            continue

        # -----------------------------------------------------
        # Deterministic verification
        # -----------------------------------------------------

        supported, reason = _claim_supported(
            claim_text=claim_text,
            evidence_text=evidence_text,
        )

        results.append(
            {
                "claim": claim_text,
                "citation": citation,
                "supported": supported,
                "reason": reason,
            }
        )

    # If the LLM produced no claims at all, it chose to refuse
    # rather than hallucinate — this is valid behaviour.
    # Only fail when claims exist but are unsupported.
    if not results:
        passed = True
    else:
        passed = all(item["supported"] for item in results)

    return {
        "passed": passed,
        "claims": results,
    }