from __future__ import annotations

from backend.safety.input_guard import check_input_safety
from backend.safety.evidence_validator import (
    has_sufficient_evidence,
    validate_citations,
)
from backend.safety.claim_verifier import verify_claims
from backend.safety.output_guard import validate_grounded_output


def run_test(name: str, condition: bool) -> bool:
    status = "PASS" if condition else "FAIL"

    print(f"[{status}] {name}")

    return condition


def main() -> None:

    print("=" * 80)
    print("TERYaq - COMPLETE SAFETY TEST")
    print("=" * 80)

    passed = 0
    total = 0

    # ================================================================
    # 1. INPUT SAFETY
    # ================================================================

    input_tests = [
        (
            "General clinical question",
            "What is early diagnosis in breast cancer?",
            True,
        ),
        (
            "General medication question",
            "What is tamoxifen?",
            True,
        ),
        (
            "Patient diagnosis",
            "Can you diagnose me?",
            False,
        ),
        (
            "Patient diagnosis",
            "Do I have breast cancer?",
            False,
        ),
        (
            "Patient dosage",
            "What dose should I take?",
            False,
        ),
        (
            "Personal medication",
            "Should I take tamoxifen?",
            False,
        ),
        (
            "Personal treatment",
            "I am taking tamoxifen. Should I change my medication?",
            False,
        ),
    ]

    print()
    print("-" * 80)
    print("1. INPUT SAFETY")
    print("-" * 80)

    for name, question, expected in input_tests:

        total += 1

        result = check_input_safety(question)

        if run_test(
            name,
            result["safe"] == expected,
        ):
            passed += 1

    # ================================================================
    # 2. EVIDENCE SAFETY
    # ================================================================

    print()
    print("-" * 80)
    print("2. EVIDENCE VALIDATION")
    print("-" * 80)

    citation = "WHO_GBCI - page 102"

    evidence = [
        {
            "citation": citation,
            "text": (
                "Figure 23 shows a fishbone diagram used to identify "
                "underlying causes of underperformance."
            ),
        }
    ]

    total += 1

    if run_test(
        "Evidence exists",
        has_sufficient_evidence(evidence) is True,
    ):
        passed += 1

    valid_result = validate_citations(
        {
            "claims": [
                {
                    "text": "Figure 23 shows a fishbone diagram.",
                    "citation": citation,
                }
            ]
        },
        evidence,
    )

    total += 1

    if run_test(
        "Valid citation accepted",
        valid_result["status"] == "PASS",
    ):
        passed += 1

    invalid_result = validate_citations(
        {
            "claims": [
                {
                    "text": "Figure 23 shows a fishbone diagram.",
                    "citation": "WHO_GBCI - page 999",
                }
            ]
        },
        evidence,
    )

    total += 1

    if run_test(
        "Invalid citation rejected",
        invalid_result["status"] == "FAIL",
    ):
        passed += 1

    # ================================================================
    # 3. CLAIM VERIFICATION
    # ================================================================

    print()
    print("-" * 80)
    print("3. CLAIM VERIFICATION")
    print("-" * 80)

    supported_result = verify_claims(
        {
            "claims": [
                {
                    "text": (
                        "Figure 23 shows a fishbone diagram used "
                        "to identify underlying causes of underperformance."
                    ),
                    "citation": citation,
                }
            ]
        },
        evidence,
    )

    total += 1

    if run_test(
        "Supported claim accepted",
        supported_result["passed"] is True,
    ):
        passed += 1

    unsupported_result = verify_claims(
        {
            "claims": [
                {
                    "text": (
                        "Figure 23 shows a survival curve "
                        "for breast cancer patients."
                    ),
                    "citation": citation,
                }
            ]
        },
        evidence,
    )

    total += 1

    if run_test(
        "Unsupported claim rejected",
        unsupported_result["passed"] is False,
    ):
        passed += 1

    # ================================================================
    # 4. OUTPUT GUARD
    # ================================================================

    print()
    print("-" * 80)
    print("4. OUTPUT GUARD")
    print("-" * 80)

    valid_output = {
        "answer": (
            "Figure 23 shows a fishbone diagram used "
            "to identify underlying causes of underperformance."
        ),
        "claims": [
            {
                "text": (
                    "Figure 23 shows a fishbone diagram used "
                    "to identify underlying causes of underperformance."
                ),
                "citation": citation,
            }
        ],
        "confidence": "high",
    }

    output_result = validate_grounded_output(
        valid_output,
        evidence,
    )

    total += 1

    if run_test(
        "Valid grounded output accepted",
        output_result["passed"] is True,
    ):
        passed += 1

    invalid_output = {
        "answer": "Figure 23 is a survival curve.",
        "claims": [
            {
                "text": "Figure 23 is a survival curve.",
                "citation": citation,
            }
        ],
        "confidence": "high",
    }

    invalid_output_result = validate_grounded_output(
        invalid_output,
        evidence,
    )

    total += 1

    if run_test(
        "Ungrounded output rejected",
        invalid_output_result["passed"] is False,
    ):
        passed += 1

    # ================================================================
    # FINAL RESULT
    # ================================================================

    print()
    print("=" * 80)
    print(f"SAFETY RESULT: {passed}/{total} TESTS PASSED")
    print("=" * 80)

    if passed != total:
        raise SystemExit(1)

    print("ALL SAFETY TESTS PASSED")


if __name__ == "__main__":
    main()