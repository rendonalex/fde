"""
Quick test script for ADR-2 Triage Agent.
Runs a single AE case through classification pipeline.
"""

import os
import json
from agents.adr1_intake import ADR1IntakeAgent
from agents.adr2_triage import ADR2TriageAgent
from agents.models import AECasePackage


def test_adr2_pipeline():
    """
    Test ADR-1 → ADR-2 pipeline on a single case.
    """
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return

    # Initialize agents
    print("Initializing ADR-1 and ADR-2 agents...")
    adr1_agent = ADR1IntakeAgent(api_key=api_key)
    adr2_agent = ADR2TriageAgent(anthropic_api_key=api_key)

    # Test file - high confidence structured report
    test_file = "mock-data/test-adr2/high_confidence_report.txt"

    print(f"\n{'='*80}")
    print(f"Testing ADR-1 → ADR-2 Pipeline")
    print(f"{'='*80}\n")

    # Step 1: ADR-1 Intake
    print(f"📄 Processing: {test_file}")
    print(f"\n--- ADR-1: INTAKE AGENT ---\n")

    with open(test_file, 'r') as f:
        report_content = f.read()

    result = adr1_agent.process_report(
        filename=test_file,
        content=report_content
    )

    case_package = result["case_package"]
    extraction_log = result["extraction_log"]
    routing_decision = result["routing_decision"]

    if not case_package:
        print(f"❌ Extraction failed: {result.get('error')}")
        print(f"\n**Extraction Log:**")
        for entry in extraction_log:
            print(f"  {entry}")
        return

    print(f"✅ Extraction Status: Success")
    print(f"✅ Routing Decision: {routing_decision}")
    print(f"\n**Case Summary:**")
    print(f"  Case ID: {case_package.case_id}")
    print(f"  Patient: {case_package.patient.age or 'unknown'} years, {case_package.patient.sex}")
    print(f"  Suspect Drug: {case_package.suspect_drug.name}")
    print(f"  AE: {case_package.ae_description.narrative[:100]}...")
    print(f"  Confidence: Patient={case_package.patient.confidence:.2f}, Drug={case_package.suspect_drug.confidence:.2f}")

    # Check if case should proceed to ADR-2
    if "ADR-2" not in routing_decision:
        print(f"\n⚠️  Case routed to {routing_decision}, not ADR-2. Stopping here.")
        return

    # Step 2: ADR-2 Triage
    print(f"\n--- ADR-2: TRIAGE AGENT ---\n")

    recommendation, classification_log = adr2_agent.classify_case(case_package)

    print(f"✅ Classification Complete\n")

    # Display results
    print(f"**Seriousness Classification:**")
    print(f"  Serious: {recommendation.seriousness_classification.serious}")
    print(f"  Criteria Matched: {[c.value for c in recommendation.seriousness_classification.criteria_matched]}")
    print(f"  Confidence: {recommendation.seriousness_classification.confidence:.2f}")
    print(f"  Reasoning: {recommendation.seriousness_classification.reasoning[:150]}...")

    print(f"\n**Expectedness Assessment:**")
    print(f"  Unexpected: {recommendation.expectedness_signal.unexpected}")
    print(f"  RSI Match Type: {recommendation.expectedness_signal.rsi_match.value}")
    print(f"  Confidence: {recommendation.expectedness_signal.confidence:.2f}")
    print(f"  RSI Term: {recommendation.expectedness_signal.rsi_term_matched or 'N/A'}")
    print(f"  Reasoning: {recommendation.expectedness_signal.reasoning[:150]}...")

    print(f"\n**Reportability Recommendation:**")
    print(f"  Type: {recommendation.reportability_recommendation.recommendation.value}")
    print(f"  Jurisdictions: {[j.value for j in recommendation.reportability_recommendation.jurisdictions]}")
    print(f"  Rule Justification: {recommendation.reportability_recommendation.rule_justification}")
    print(f"  Reasoning: {recommendation.reportability_recommendation.reasoning[:150]}...")

    print(f"\n**Signal Detection (FDA Requirement 3):**")
    print(f"  Signal Detected: {recommendation.signal_detection_flag}")
    if recommendation.signal_pattern:
        print(f"  Product: {recommendation.signal_pattern.product}")
        print(f"  MedDRA PT: {recommendation.signal_pattern.meddra_pt} ({recommendation.signal_pattern.meddra_code})")
        print(f"  Case Count: {recommendation.signal_pattern.case_count}")
        print(f"  Window: {recommendation.signal_pattern.window_start} to {recommendation.signal_pattern.window_end}")

    print(f"\n**MSO Review Flags (FDA Requirement 2):**")
    print(f"  Deep Review Required: {recommendation.mso_flags.deep_review_required}")
    print(f"  Reasons: {[r.value for r in recommendation.mso_flags.reason]}")

    print(f"\n**FDA Compliance:**")
    print(f"  Model Version: {recommendation.model_version_adr2}")
    print(f"  MSO Action: {recommendation.mso_action.value if recommendation.mso_action else 'Pending'}")
    print(f"  Audit Trail: {len(recommendation.audit_trail.regulatory_references)} regulatory references")
    print(f"  Created At: {recommendation.created_at}")

    print(f"\n{'='*80}")
    print(f"✅ ADR-1 → ADR-2 Pipeline Test Complete")
    print(f"{'='*80}\n")

    # Save results
    output = {
        "case_id": case_package.case_id,
        "adr1_extraction": {"log": extraction_log, "routing": routing_decision},
        "adr2_classification": classification_log,
        "final_recommendation": recommendation.dict()
    }

    with open("test_adr2_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"📁 Results saved to: test_adr2_results.json")


if __name__ == "__main__":
    test_adr2_pipeline()
