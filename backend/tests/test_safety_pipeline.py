from backend.safety.claim_verifier import _claim_supported
from backend.safety.input_guard import check_input_safety


def test_for_me_boundary_does_not_reject_metastatic():
    result = check_input_safety(
        "What are treatment options for metastatic breast cancer?"
    )
    assert result["safe"] is True


def test_english_patient_specific_dose_is_blocked():
    result = check_input_safety("What dose should I take?")
    assert result["safe"] is False
    assert result["category"] == "patient_specific_medical_request"


def test_arabic_patient_specific_dose_is_blocked():
    result = check_input_safety("هل أزود جرعتي؟")
    assert result["safe"] is False
    assert result["category"] == "patient_specific_medical_request"


def test_general_arabic_question_is_allowed():
    result = check_input_safety("ما هي أعراض سرطان الثدي؟")
    assert result["safe"] is True


def test_claim_verifier_handles_clinical_paraphrase():
    supported, _ = _claim_supported(
        "Treatment is an important part of disease management.",
        "Therapy is an important part of disease management for patients.",
    )
    assert supported is True


def test_claim_verifier_rejects_unsupported_claim():
    supported, _ = _claim_supported(
        "The treatment completely prevents recurrence.",
        "Treatment can reduce symptoms and improve quality of life.",
    )
    assert supported is False
