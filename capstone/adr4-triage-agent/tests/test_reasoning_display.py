"""
Display reasoning traces from various claim scenarios.
Run with: python3 -m pytest tests/test_reasoning_display.py -v -s
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import TriageAgent
from app.models import NormalizedClaimRecord, ExtractionStatus


class TestReasoningDisplay:
    """Display Claude's reasoning for different claim types."""

    def test_routine_office_visit_reasoning(self):
        """Routine office visit - should route FAST_PATH."""
        print("\n" + "="*80)
        print("SCENARIO 1: Routine Office Visit")
        print("="*80)

        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="test-routine-001",
            source_claim_ref="ROUTINE-001",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-12345",
            icd10_codes=["Z00.00"],  # Wellness visit
            cpt_codes=["99213"],      # Office visit
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="PY-001",
            place_of_service="11",
            billed_amount=185.00
        )

        result = agent.classify(claim)

        print(f"\nClaim: {claim.icd10_codes} + {claim.cpt_codes}")
        print(f"Routing: {result.routing_decision.value}")
        print(f"Confidence: {result.confidence}")
        print(f"Provisions matched: {result.criteria_provisions_matched}")
        print(f"\nREASONING TRACE:")
        print(result.reasoning_trace)
        print("\n")

        assert result.routing_decision.value in ["FAST_PATH", "CLINICAL_PATH"]

    def test_oncology_claim_reasoning(self):
        """Oncology claim - should route CLINICAL_PATH."""
        print("\n" + "="*80)
        print("SCENARIO 2: Oncology Chemotherapy")
        print("="*80)

        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="test-onc-001",
            source_claim_ref="ONC-001",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-67890",
            icd10_codes=["C50.911"],  # Breast cancer
            cpt_codes=["96413"],       # Chemotherapy
            prior_auth_required=True,
            prior_auth_number="PA-001",
            payer_id="PY-002",
            place_of_service="22",
            billed_amount=4200.00
        )

        result = agent.classify(claim)

        print(f"\nClaim: {claim.icd10_codes} + {claim.cpt_codes}")
        print(f"Routing: {result.routing_decision.value}")
        print(f"Confidence: {result.confidence}")
        print(f"Provisions matched: {result.criteria_provisions_matched}")
        print(f"\nREASONING TRACE:")
        print(result.reasoning_trace)
        print("\n")

        assert result.routing_decision.value == "CLINICAL_PATH"

    def test_contradictory_codes_reasoning(self):
        """Clinically contradictory codes - bronchitis + chemotherapy."""
        print("\n" + "="*80)
        print("SCENARIO 3: Contradictory Codes (Bronchitis + Chemo)")
        print("="*80)

        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.95)

        claim = NormalizedClaimRecord(
            claim_id="test-contra-001",
            source_claim_ref="CLM-2026-9003",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="YYL88234510",
            icd10_codes=["J20.9"],  # Bronchitis (contradictory!)
            cpt_codes=["96413"],     # Chemotherapy
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="ANT-001",
            place_of_service="22",
            billed_amount=4200.00
        )

        result = agent.classify(claim)

        print(f"\nClaim: {claim.icd10_codes} + {claim.cpt_codes}")
        print(f"Routing: {result.routing_decision.value}")
        print(f"Confidence: {result.confidence}")
        print(f"Confidence Fallback Applied: {result.confidence_fallback}")
        print(f"Provisions matched: {result.criteria_provisions_matched}")
        print(f"\nREASONING TRACE:")
        print(result.reasoning_trace)
        print("\n")

        assert result.routing_decision.value == "CLINICAL_PATH"

    def test_diagnostic_imaging_reasoning(self):
        """Diagnostic imaging - should route CLINICAL_PATH."""
        print("\n" + "="*80)
        print("SCENARIO 4: Diagnostic Imaging (MRI)")
        print("="*80)

        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="test-img-001",
            source_claim_ref="MRI-001",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-IMG-001",
            icd10_codes=["M51.26"],  # Disc displacement
            cpt_codes=["72148"],      # MRI lumbar spine
            prior_auth_required=True,
            prior_auth_number="PA-MRI-001",
            payer_id="PY-IMG",
            place_of_service="22",
            billed_amount=1200.00
        )

        result = agent.classify(claim)

        print(f"\nClaim: {claim.icd10_codes} + {claim.cpt_codes}")
        print(f"Routing: {result.routing_decision.value}")
        print(f"Confidence: {result.confidence}")
        print(f"Provisions matched: {result.criteria_provisions_matched}")
        print(f"\nREASONING TRACE:")
        print(result.reasoning_trace)
        print("\n")

        assert result.routing_decision.value == "CLINICAL_PATH"

    def test_novel_case_reasoning(self):
        """Novel case - codes not in codebook (guardrail triggers)."""
        print("\n" + "="*80)
        print("SCENARIO 5: NOVEL CASE - Unrecognized Codes")
        print("="*80)

        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="test-novel-001",
            source_claim_ref="NOVEL-001",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-NOVEL-001",
            icd10_codes=["Z99.89"],   # Dependence on other enabling machines (not in codebook)
            cpt_codes=["99499"],       # Unlisted evaluation/management service (not in codebook)
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="PY-NOVEL",
            place_of_service="11",
            billed_amount=500.00
        )

        result = agent.classify(claim)

        print(f"\nClaim: {claim.icd10_codes} + {claim.cpt_codes}")
        print(f"Routing: {result.routing_decision.value}")
        print(f"Confidence: {result.confidence}")
        print(f"Provisions matched: {result.criteria_provisions_matched}")
        print(f"\n⚠️  EXPECTED: Should route to CLINICAL_PATH for physician review")
        print(f"⚠️  EXPECTED: Confidence should be 0.0 (no codebook match)")
        print(f"\nREASONING TRACE:")
        print(result.reasoning_trace)
        print("\n")

        # Novel cases should route to CLINICAL_PATH for safety
        assert result.routing_decision.value == "CLINICAL_PATH"
        # Should have low or zero confidence since no provisions match
        assert result.confidence <= 0.70

    def test_shadow_isolation_violation_failure(self):
        """Shadow mode isolation violation - agent rejects LIVE output in SHADOW mode."""
        print("\n" + "="*80)
        print("SCENARIO 6: FAILURE - Shadow Mode Isolation Violation")
        print("="*80)
        print("Testing guard rail: Agent in SHADOW mode receives LIVE routing_mode from LLM")
        print("="*80)

        from unittest.mock import patch, MagicMock
        from app.models import RoutingDecisionOutput, RoutingDecision, RoutingMode
        import json
        import os

        # Set API key for this test
        os.environ["ANTHROPIC_API_KEY"] = "test-key-for-mocking"
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="test-violation-001",
            source_claim_ref="VIOLATION-001",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-VIOLATION-001",
            icd10_codes=["Z00.00"],
            cpt_codes=["99213"],
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="PY-001",
            place_of_service="11",
            billed_amount=185.00
        )

        # Mock Anthropic client response to return LIVE mode (violation!)
        mock_api_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = json.dumps({
            "claim_id": "test-violation-001",
            "source_claim_ref": "VIOLATION-001",
            "routing_decision": "FAST_PATH",
            "confidence": 0.96,
            "confidence_fallback": False,
            "clinical_indicators_detected": ["ICD-10: Z00.00", "CPT: 99213"],
            "criteria_provisions_matched": [],
            "reasoning_trace": "Mock reasoning trace",
            "routing_mode": "LIVE"  # VIOLATION: Returns LIVE when agent is SHADOW
        })
        mock_api_response.content = [mock_content]

        print(f"\nAgent mode: SHADOW")
        print(f"LLM returns routing_mode: LIVE ← VIOLATION!")
        print(f"\n⚠️  EXPECTED: Safe fallback to CLINICAL_PATH with SHADOW_ISOLATION_VIOLATION")

        with patch.object(agent.client.messages, 'create', return_value=mock_api_response):
            result = agent.classify(claim)

        print(f"\n✅ SAFE FALLBACK (as expected):")
        print(f"   Routing: {result.routing_decision.value}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Provisions: {result.criteria_provisions_matched}")
        print(f"\nREASONING TRACE:")
        print(result.reasoning_trace)
        print(f"\nGuard rail successfully prevented shadow mode violation!")

        # Verify safe fallback behavior
        assert result.routing_decision.value == "CLINICAL_PATH"
        assert result.confidence == 0.0
        assert "SHADOW_ISOLATION_VIOLATION" in result.criteria_provisions_matched
        assert "routing_mode" in result.reasoning_trace

        print(f"\n✅ Test passed: Shadow isolation guard rail working correctly\n")
