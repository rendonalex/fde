#!/usr/bin/env python3
"""
Quick test script to verify ADR-1 agent functionality.
Processes one sample HCP report and displays results.
"""

import os
from agents.adr1_intake import ADR1IntakeAgent

def test_single_file():
    """Test ADR-1 with single HCP report"""

    # Sample file path
    sample_file = "mock-data/hcp-reports/AE-2026-05-09-001_Tezarimab_HCP_report.txt"

    if not os.path.exists(sample_file):
        print(f"❌ Sample file not found: {sample_file}")
        return False

    print("=" * 80)
    print("ADR-1 QUICK TEST")
    print("=" * 80)
    print()

    # Read file
    with open(sample_file, 'r') as f:
        content = f.read()

    print(f"✓ Loaded test file: {sample_file}")
    print(f"  File size: {len(content)} bytes")
    print()

    # Initialize agent (requires ANTHROPIC_API_KEY env var)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not set - using mock mode only")
        print("   Set export ANTHROPIC_API_KEY='your-key' to test full extraction")
        print()

    print("✓ Initializing ADR-1 agent...")
    agent = ADR1IntakeAgent()
    print()

    # Process report
    print("✓ Processing report with ADR-1...")
    print("-" * 80)

    try:
        result = agent.process_report(os.path.basename(sample_file), content)

        # Display log
        print("\nProcessing Log:")
        for log_entry in result["extraction_log"]:
            print(f"  {log_entry}")

        print()
        print("-" * 80)

        # Display summary
        if result["case_package"]:
            pkg = result["case_package"]

            print(f"\n✅ EXTRACTION SUCCESSFUL")
            print(f"\nCase ID: {pkg.case_id}")
            print(f"Status: {pkg.extraction_status}")
            print(f"Routing: {result['routing_decision']}")
            print(f"\nPatient: {pkg.patient.sex}, {pkg.patient.age} years (confidence: {pkg.patient.confidence:.2f})")
            print(f"Drug: {pkg.suspect_drug.name} {pkg.suspect_drug.dose}")
            if pkg.suspect_drug.rxnorm_code:
                print(f"  RxNorm: {pkg.suspect_drug.rxnorm_code}")
            print(f"AE: {pkg.ae_description.narrative[:80]}...")
            if pkg.ae_description.meddra_pt:
                print(f"  MedDRA: {pkg.ae_description.meddra_pt} ({pkg.ae_description.meddra_code})")

            print(f"\n[FDA Compliance]")
            print(f"Model version: {pkg.model_version_adr1}")
            print(f"Source documents: {len(pkg.source_documents)}")
            print(f"Span citations: {len(pkg.span_citations)} fields")

            print("\n" + "=" * 80)
            print("✅ TEST PASSED")
            print("=" * 80)
            return True
        else:
            print(f"\n❌ EXTRACTION FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print("\n" + "=" * 80)
            print("❌ TEST FAILED")
            print("=" * 80)
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        return False

if __name__ == "__main__":
    success = test_single_file()
    exit(0 if success else 1)
