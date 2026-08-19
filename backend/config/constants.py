"""Project constants."""

MEDICAL_CONTENT_TYPES = {
    "text",
    "figure",
    "table",
    "chart",
    "map",
}

DEFAULT_REFUSAL_MESSAGE = (
    "I’m unable to provide a grounded answer because the available "
    "evidence is insufficient or the request requires patient-specific "
    "medical advice."
)
