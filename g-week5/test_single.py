"""
Run a single test case from the ADR-2 test suite
Usage: python3 test_single.py FM-01
"""

import sys
import os
from agents.adr1_intake import ADR1IntakeAgent
from agents.adr2_triage import ADR2TriageAgent


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_single.py <test_name>")
        print("Available tests: HP-01, EC-01, FM-01, HITL-01")
        sys.exit(1)

    test_name = sys.argv[1]

    # Map test names to files
    test_files = {
        "HP-01": "mock-data/test-adr2/HP-01-expected-nonserious.txt",
        "EC-01": "mock-data/test-adr2/EC-01-serious-unexpected-expedited.txt",
        "FM-01": "mock-data/test-adr2/FM-01-ambiguous-seriousness.txt",
        "HITL-01": "mock-data/test-adr2/HITL-01-low-confidence-extraction.txt"
    }

    if test_name not in test_files:
        print(f"Unknown test: {test_name}")
        print(f"Available tests: {', '.join(test_files.keys())}")
        sys.exit(1)

    test_file = test_files[test_name]

    print(f"\n{'='*80}")
    print(f"Running single test: {test_name}")
    print(f"{'='*80}\n")

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        sys.exit(1)

    # Initialize agents
    adr1_agent = ADR1IntakeAgent(api_key=api_key)
    adr2_agent = ADR2TriageAgent(anthropic_api_key=api_key)

    # Read test file
    with open(test_file, 'r') as f:
        content = f.read()

    # Step 1: ADR-1 Intake
    print("--- ADR-1 INTAKE ---\n")
    result = adr1_agent.process_report(filename=test_file, content=content)

    if not result["case_package"]:
        print(f"❌ ADR-1 extraction failed: {result.get('error')}")
        sys.exit(1)

    case_package = result["case_package"]
    routing = result["routing_decision"]

    print(f"✅ Extraction complete")
    print(f"  Patient: {case_package.patient.age or 'unknown'}y, {case_package.patient.sex}")
    print(f"  Drug: {case_package.suspect_drug.name}")
    print(f"  Routing: {routing}\n")

    if "ADR-2" not in routing:
        print(f"⚠️  Case routed to {routing}, not ADR-2")
        print(f"   Test stopped at ADR-1")
        sys.exit(0)

    # Step 2: ADR-2 Triage
    print("--- ADR-2 TRIAGE ---\n")
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

    print(f"\n**MSO Deep Review:** {recommendation.mso_flags.deep_review_required}")
    print(f"  Reasons: {[r.value for r in recommendation.mso_flags.reason]}")

    print(f"\n**Signal Detection:** {recommendation.signal_detection_flag}")

    print(f"\n{'='*80}")
    print(f"✅ Test complete")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
