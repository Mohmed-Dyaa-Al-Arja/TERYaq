"""Input safety gate for patient-specific medical requests."""

from __future__ import annotations

import re


# Keep word boundaries around English phrases so substrings such as
# "for metastatic" cannot accidentally match "for me".
_PATIENT_SPECIFIC_PATTERNS = [
    r"\bfor me\b",
    r"\bmy dose\b",
    r"\bdose for me\b",
    r"\bwhat should i take\b",
    r"\bwhat medicine should i take\b",
    r"\bwhich medication should i take\b",
    r"\bwhich drug should i take\b",
    r"\bshould i take\b",
    r"\bcan you diagnose me\b",
    r"\bdiagnose whether i\b",
    r"\bdo i have\b",
    r"\bam i suffering from\b",
    r"\bpersonally take\b",
    r"\bmy treatment\b",
    r"\bfor my treatment\b",
    r"\bchange my dose\b",
    r"\bincrease my dose\b",
    r"\bdecrease my dose\b",
]

# Arabic first-person/patient-specific requests. These deliberately focus on
# personal diagnosis, treatment and dosage rather than general education.
_ARABIC_PATIENT_SPECIFIC_PATTERNS = [
    r"جرعتي",
    r"جرعتي.*(?:ازود|أزود|ازيد|أزيد|اقلل|أقلل|أخفض|أرفع)",
    r"(?:ازود|أزود|ازيد|أزيد|اقلل|أقلل|أخفض|أرفع).*الجرع",
    r"(?:اخد|آخد|أخد|اخذ|آخذ|أخذ).*دواء",
    r"(?:ايه|إيه|ما هو|ماذا).*الدواء.*(?:اخد|آخذ|أخذ)",
    r"هل.*(?:اخد|آخذ|أخذ).*دواء",
    r"(?:علاجي|علاجي الشخصي|العلاج بتاعي)",
    r"(?:اشخصني|شخصني|هل انا مصاب|هل أنا مصاب)",
    r"(?:ازود|أزود|ازيد|أزيد).*الجرعة",
    r"(?:أقلل|اقلل|أخفض|اخفض).*الجرعة",
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


def _patient_specific_result(category: str, reason: str) -> dict:
    return {
        "safe": False,
        "category": category,
        "reason": reason,
        "message": (
            "I can only provide general clinical information supported by "
            "the medical documents. I can’t provide patient-specific "
            "diagnosis or treatment advice. Please consult a qualified "
            "healthcare professional."
        ),
    }


def check_input_safety(question: str) -> dict:
    """Classify whether the request is allowed to reach retrieval/generation."""
    normalized = " ".join(str(question).lower().split())

    for pattern in _PATIENT_SPECIFIC_PATTERNS:
        if re.search(pattern, normalized):
            return _patient_specific_result(
                "patient_specific_medical_request",
                "The request asks for patient-specific diagnosis, treatment, medication, or dosage guidance.",
            )

    for pattern in _ARABIC_PATIENT_SPECIFIC_PATTERNS:
        if re.search(pattern, normalized):
            return _patient_specific_result(
                "patient_specific_medical_request",
                "The request appears to ask for patient-specific diagnosis, treatment, medication, or dosage guidance in Arabic.",
            )

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
            return _patient_specific_result(
                "patient_specific_medication_request",
                "The request refers to the user's own medication or treatment.",
            )

    return {
        "safe": True,
        "category": "general_information_request",
        "reason": "Request passed the input safety gate.",
        "message": "",
    }
