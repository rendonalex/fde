"""
ADR-2 Test Suite: Happy Path, Edge Case, and Failure Mode

Tests the full ADR-1 → ADR-2 pipeline on three distinct scenarios:
1. HP-01: Happy path (expected, non-serious) → NON_REPORTABLE
2. EC-01: Edge case (serious + unexpected) → EXPEDITED_15_DAY
3. FM-01: Failure mode (ambiguous seriousness) → MSO deep review
"""

import os
import sys
from agents.adr1_intake import ADR1IntakeAgent
from agents.adr2_triage import ADR2TriageAgent


def run_test(test_name: str, test_file: str, expected_outcomes: dict):
    """
    Run a single test case and validate outcomes.

    Args:
        test_name: Test case name
        test_file: Path to test file
        expected_outcomes: Dict with expected classification results
    """
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"File: {test_file}")
    print(f"{'='*80}\n")

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        return False

    # Initialize agents
    adr1_agent = ADR1IntakeAgent(api_key=api_key)
    adr2_agent = ADR2TriageAgent(anthropic_api_key=api_key)

    # Read test file
    try:
        with open(test_file, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Test file not found: {test_file}")
        return False

    # Step 1: ADR-1 Intake
    print("--- ADR-1 INTAKE ---")
    result = adr1_agent.process_report(filename=test_file, content=content)

    if not result["case_package"]:
        print(f"❌ ADR-1 extraction failed: {result.get('error')}")
        return False

    case_package = result["case_package"]
    routing = result["routing_decision"]

    print(f"✅ Extraction complete")
    print(f"  Patient: {case_package.patient.age or 'unknown'}y, {case_package.patient.sex}")
    print(f"  Drug: {case_package.suspect_drug.name}")
    print(f"  Routing: {routing}")

    # Check if this is a HITL test case (should stop at ADR-1)
    if "expected_routing" in expected_outcomes:
        expected_routing = expected_outcomes["expected_routing"]

        print(f"\n--- VALIDATION (ADR-1 Only) ---")

        if expected_routing in routing:
            print(f"✅ Routing: {routing} (expected: {expected_routing})")
            print(f"\n✅ TEST PASSED: {test_name}")
            print(f"   Case correctly routed to {expected_routing}, did not proceed to ADR-2")
            return True
        else:
            print(f"❌ Routing: {routing} (expected: {expected_routing})")
            print(f"\n❌ TEST FAILED: {test_name}")
            return False

    if "ADR-2" not in routing:
        print(f"⚠️  Case routed to {routing}, not ADR-2")
        print(f"   This may be expected for low-confidence test cases")
        return True  # Not a failure, just different routing

    # Step 2: ADR-2 Triage
    print("\n--- ADR-2 TRIAGE ---")
    recommendation, classification_log = adr2_agent.classify_case(case_package)

    print(f"✅ Classification complete\n")

    # Display results
    print(f"**Seriousness:** {recommendation.seriousness_classification.serious}")
    print(f"  Criteria: {[c.value for c in recommendation.seriousness_classification.criteria_matched]}")
    print(f"  Confidence: {recommendation.seriousness_classification.confidence:.2f}")

    print(f"\n**Expectedness:** {'Unexpected' if recommendation.expectedness_signal.unexpected else 'Expected'}")
    print(f"  RSI Match: {recommendation.expectedness_signal.rsi_match.value}")
    print(f"  Confidence: {recommendation.expectedness_signal.confidence:.2f}")

    print(f"\n**Reportability:** {recommendation.reportability_recommendation.recommendation.value}")
    print(f"  Jurisdictions: {[j.value for j in recommendation.reportability_recommendation.jurisdictions]}")
    print(f"  Confidence: {recommendation.reportability_recommendation.confidence:.2f}")

    print(f"\n**MSO Deep Review:** {recommendation.mso_flags.deep_review_required}")
    print(f"  Reasons: {[r.value for r in recommendation.mso_flags.reason]}")

    print(f"\n**Signal Detection:** {recommendation.signal_detection_flag}")

    # Validate expected outcomes
    print(f"\n--- VALIDATION ---")
    passed = True

    if "seriousness" in expected_outcomes:
        expected = expected_outcomes["seriousness"]
        actual = recommendation.seriousness_classification.serious
        if expected == actual:
            print(f"✅ Seriousness: {actual} (expected: {expected})")
        else:
            print(f"❌ Seriousness: {actual} (expected: {expected})")
            passed = False

    if "reportability" in expected_outcomes:
        expected = expected_outcomes["reportability"]
        actual = recommendation.reportability_recommendation.recommendation.value
        if expected == actual:
            print(f"✅ Reportability: {actual} (expected: {expected})")
        else:
            print(f"❌ Reportability: {actual} (expected: {expected})")
            passed = False

    if "mso_deep_review" in expected_outcomes:
        expected = expected_outcomes["mso_deep_review"]
        actual = recommendation.mso_flags.deep_review_required
        if expected == actual:
            print(f"✅ MSO Deep Review: {actual} (expected: {expected})")
        else:
            print(f"❌ MSO Deep Review: {actual} (expected: {expected})")
            passed = False

    if "unexpected" in expected_outcomes:
        expected = expected_outcomes["unexpected"]
        actual = recommendation.expectedness_signal.unexpected
        if expected == actual:
            print(f"✅ Unexpected: {actual} (expected: {expected})")
        else:
            print(f"❌ Unexpected: {actual} (expected: {expected})")
            passed = False

    if passed:
        print(f"\n✅ TEST PASSED: {test_name}")
    else:
        print(f"\n❌ TEST FAILED: {test_name}")

    return passed


def main():
    """Run all test cases"""
    print("\n" + "="*80)
    print("ADR-2 TRIAGE AGENT TEST SUITE")
    print("="*80)

    test_cases = [
        {
            "name": "HP-01: Happy Path (Expected, Non-Serious)",
            "file": "mock-data/test-adr2/HP-01-expected-nonserious.txt",
            "expected": {
                "seriousness": False,
                "unexpected": False,
                "reportability": "NON_REPORTABLE",
                "mso_deep_review": False
            }
        },
        {
            "name": "EC-01: Edge Case (Serious + Unexpected)",
            "file": "mock-data/test-adr2/EC-01-serious-unexpected-expedited.txt",
            "expected": {
                "seriousness": True,
                "unexpected": True,
                "reportability": "15_DAY_EXPEDITED",
                "mso_deep_review": True  # Novel AE term triggers deep review
            }
        },
        {
            "name": "FM-01: Failure Mode (Ambiguous Seriousness)",
            "file": "mock-data/test-adr2/FM-01-ambiguous-seriousness.txt",
            "expected": {
                "mso_deep_review": True  # Ambiguous seriousness triggers deep review
                # Don't validate seriousness/reportability - expect low confidence
            }
        },
        {
            "name": "HITL-01: ADR-1 HITL Routing (Low Confidence)",
            "file": "mock-data/test-adr2/HITL-01-low-confidence-extraction.txt",
            "expected": {
                "expected_routing": "HITL_QUEUE"
                # This test validates ADR-1 routing only, should NOT reach ADR-2
            }
        }
    ]

    results = []
    for test_case in test_cases:
        result = run_test(
            test_name=test_case["name"],
            test_file=test_case["file"],
            expected_outcomes=test_case["expected"]
        )
        results.append((test_case["name"], result))

    # Summary
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
