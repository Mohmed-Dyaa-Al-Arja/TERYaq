"""Input safety gate for patient-specific medical requests."""

from __future__ import annotations

import re


_PATIENT_SPECIFIC_PATTERNS = [
    r"for me",
    r"my dose",
    r"dose for me",
    r"what should i take",
    r"what medicine should i take",
    r"which medication should i take",
    r"which drug should i take",
    r"should i take",
    r"can you diagnose me",
    r"diagnose whether i",
    r"do i have",
    r"am i suffering from",
    r"personally take",
    r"my treatment",
    r"for my treatment",
    r"change my dose",
    r"increase my dose",
    r"decrease my dose",
]

_MEDICATION_TERMS = [
    "dose",
    "dosage",
    "medication",
    "medicine",
    "drug",
    "chemotherapy",
    "tamoxifen",
]


def check_input_safety(question: str) -> dict:
    """Classify whether the request is allowed to reach generation."""
    normalized = " ".join(question.lower().split())

    for pattern in _PATIENT_SPECIFIC_PATTERNS:
        if re.search(pattern, normalized):
            return {
                "safe": False,
                "category": "patient_specific_medical_request",
                "reason": (
                    "The request asks for patient-specific diagnosis, "
                    "treatment, medication, or dosage guidance."
                ),
                "message": (
                    "I can only provide general clinical information "
                    "supported by the medical documents. I can’t provide "
                    "patient-specific diagnosis or treatment advice. "
                    "Please consult a qualified healthcare professional."
                ),
            }

    # Explicit first-person medical treatment intent.
    if any(term in normalized for term in _MEDICATION_TERMS):
        if any(
            token in normalized
            for token in [
                "i take",
                "i am taking",
                "i use",
                "my medication",
                "my medicine",
                "my drug",
            ]
        ):
            return {
                "safe": False,
                "category": "patient_specific_medication_request",
                "reason": (
                    "The request refers to the user's own medication "
                    "or treatment."
                ),
                "message": (
                    "I can provide general information from the documents, "
                    "but I can’t advise you personally about medication or "
                    "treatment. Please consult a qualified healthcare "
                    "professional."
                ),
            }

    return {
        "safe": True,
        "category": "general_information_request",
        "reason": "Request passed the input safety gate.",
        "message": "",
    }
