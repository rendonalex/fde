#!/usr/bin/env python3
"""
Example script demonstrating ADR-4 classification.
Run without OpenAI API for demonstration of logic.
"""

import sys
import os
import json

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import NormalizedClaimRecord, ExtractionStatus
from app.agent import TriageAgent


def print_result(result, claim_description):
    """Pretty print classification result."""
    print(f"\n{'='*80}")
    print(f"CLAIM: {claim_description}")
    print(f"{'='*80}")
    print(f"Claim ID:           {result.claim_id}")
    print(f"Source Ref:         {result.source_claim_ref}")
    print(f"Routing Decision:   {result.routing_decision.value}")
    print(f"Confidence:         {result.confidence:.2f}")
    print(f"Confidence Fallback: {result.confidence_fallback}")
    print(f"Routing Mode:       {result.routing_mode.value}")
    print(f"\nClinical Indicators:")
    for indicator in result.clinical_indicators_detected:
        print(f"  - {indicator}")
    print(f"\nProvisions Matched:")
    if result.criteria_provisions_matched:
        for provision in result.criteria_provisions_matched:
            print(f"  - {provision}")
    else:
        print("  (none)")
    print(f"\nReasoning Trace:")
    print(result.reasoning_trace)
    print(f"{'='*80}\n")


def main():
    """Run example classifications."""
    print("\n" + "="*80)
    print("ADR-4 CLINICAL CONTENT TRIAGE AGENT - CLASSIFICATION EXAMPLES")
    print("(LLM-based reasoning with codebook - matches Jupyter notebook)")
    print("="*80)

    # Initialize agent in SHADOW mode
    print("\nInitializing agent in SHADOW mode...")
    agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)
    print(f"✓ Agent initialized (LLM-based classification)")
    print(f"✓ Codebook version: {agent.codebook.codebook_version}")
    print(f"✓ Active provisions: {len(agent.codebook_loader.provisions)}")

    # Example 1: Routine office visit (FAST_PATH)
    print("\n\nExample 1: Routine Office Visit")
    claim1 = NormalizedClaimRecord(
        claim_id="example-001",
        source_claim_ref="PDF-2026-0441",
        intake_channel="CMS1500_PDF",
        extraction_status=ExtractionStatus.AUTO_COMPLETE,
        member_id="M-4421908",
        icd10_codes=["Z00.00"],  # Routine adult health examination
        cpt_codes=["99213"],      # Office visit, established patient
        prior_auth_required=False,
        prior_auth_number=None,
        payer_id="BX-0042",
        place_of_service="11",
        billed_amount=185.00
    )
    result1 = agent.classify(claim1)
    print_result(result1, "Routine Adult Health Examination")

    # Example 2: Oncology chemotherapy (CLINICAL_PATH)
    print("\n\nExample 2: Oncology Chemotherapy")
    claim2 = NormalizedClaimRecord(
        claim_id="example-002",
        source_claim_ref="EDI-20260412-00417",
        intake_channel="EDI_837P",
        extraction_status=ExtractionStatus.AUTO_COMPLETE,
        member_id="M-9938812",
        icd10_codes=["C50.911", "Z79.899"],  # Breast cancer, long-term drug therapy
        cpt_codes=["96413", "96415"],         # Chemo administration
        prior_auth_required=True,
        prior_auth_number="PA-20260410-4421",
        payer_id="UH-0017",
        place_of_service="22",
        billed_amount=4200.00
    )
    result2 = agent.classify(claim2)
    print_result(result2, "Oncology Chemotherapy Administration")

    # Example 3: Diagnostic imaging (CLINICAL_PATH)
    print("\n\nExample 3: Diagnostic Imaging")
    claim3 = NormalizedClaimRecord(
        claim_id="example-003",
        source_claim_ref="PDF-2026-0589",
        intake_channel="CMS1500_PDF",
        extraction_status=ExtractionStatus.AUTO_COMPLETE,
        member_id="M-2194567",
        icd10_codes=["R05.9"],   # Cough, unspecified
        cpt_codes=["71046"],     # Chest X-ray, 2 views
        prior_auth_required=False,
        prior_auth_number=None,
        payer_id="AE-0031",
        place_of_service="22",
        billed_amount=620.00
    )
    result3 = agent.classify(claim3)
    print_result(result3, "Diagnostic Imaging - Chest X-ray")

    # Example 4: Prior auth required only (CLINICAL_PATH)
    print("\n\nExample 4: Prior Authorization Required")
    claim4 = NormalizedClaimRecord(
        claim_id="example-004",
        source_claim_ref="PDF-2026-0631",
        intake_channel="PORTAL_JSON",
        extraction_status=ExtractionStatus.AUTO_COMPLETE,
        member_id="M-6672341",
        icd10_codes=["M54.51"],  # Low back pain
        cpt_codes=["99214"],     # Office visit, moderate complexity
        prior_auth_required=True,
        prior_auth_number=None,
        payer_id="BX-0042",
        place_of_service="11",
        billed_amount=275.00
    )
    result4 = agent.classify(claim4)
    print_result(result4, "Prior Authorization Required - Low Back Pain")

    print("\n" + "="*80)
    print("EXAMPLES COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
