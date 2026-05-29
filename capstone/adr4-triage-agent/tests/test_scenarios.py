"""
Validation scenarios from spec Section 10.
Per specs/06b-capability-spec-triage.md Section 10 (Validation Scenarios).
"""

import pytest
import os
import sys
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import NormalizedClaimRecord, RoutingDecision, ExtractionStatus
from app.agent import TriageAgent


class TestHappyPaths:
    """Test happy path scenarios from spec §10.1 and §10.2."""

    def test_happy_path_shadow_mode_clinical_claim(self):
        """
        §10.1: Shadow mode, clinical claim correctly identified.
        Input: Claim with Z51.11 (chemo) and CPT 96413 → matches CC-003.
        Expected: CLINICAL_PATH, high confidence, CC-003 matched.
        """
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="a3f1e2d4-0c8b-4e6a-9f7d-1b2c3d4e5f60",
            source_claim_ref="EDI-20260412-00417",
            intake_channel="EDI_837P",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-9938812",
            icd10_codes=["Z51.11"],  # Chemo encounter
            cpt_codes=["96413"],     # Chemo administration
            prior_auth_required=True,
            prior_auth_number="PA-20260410-4421",
            payer_id="UH-0017",
            place_of_service="22",
            billed_amount=4200.00
        )

        result = agent.classify(claim)

        assert result.routing_decision == RoutingDecision.CLINICAL_PATH
        assert result.confidence >= 0.70
        assert "CC-003" in result.criteria_provisions_matched  # Oncology
        assert result.confidence_fallback == False
        assert result.routing_mode.value == "SHADOW"

    def test_happy_path_live_mode_admin_claim(self):
        """
        §10.2: Live mode, administrative claim correctly routed FAST_PATH.
        Input: Routine office visit (Z00.00, 99213).
        Expected: FAST_PATH, high confidence, no provisions matched.
        """
        agent = TriageAgent(mode="LIVE", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="b7c2f3e5-1d9a-4f7b-8e0c-2c3d4e5f6a71",
            source_claim_ref="PDF-2026-0441",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-4421908",
            icd10_codes=["Z00.00"],  # Routine exam
            cpt_codes=["99213"],     # Office visit
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="BX-0042",
            place_of_service="11",
            billed_amount=185.00
        )

        result = agent.classify(claim)

        assert result.routing_decision == RoutingDecision.FAST_PATH
        assert result.confidence >= 0.70
        assert len(result.criteria_provisions_matched) == 0
        assert result.confidence_fallback == False
        assert result.routing_mode.value == "LIVE"


class TestEdgeCases:
    """Test edge cases from spec §10.3."""

    def test_ec2_confidence_below_threshold_fallback(self):
        """
        EC-2: Confidence below threshold — conservative fallback.
        Input: Clinically contradictory codes (bronchitis + chemo).
        Expected: CLINICAL_PATH, lower confidence due to mismatch, confidence_fallback=true.
        """
        # Set threshold to detect when Claude scores lower due to clinical mismatch
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.99)

        # J20.9 (bronchitis) + 96413 (chemotherapy) = clinically contradictory
        claim = NormalizedClaimRecord(
            claim_id="c9d4a5b6-2e0f-4a8c-7b1d-3d4e5f6a7b82",
            source_claim_ref="CLM-2026-9003",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="YYL88234510",
            icd10_codes=["J20.9"],  # Acute bronchitis (contradictory with chemo)
            cpt_codes=["96413"],    # Chemotherapy administration
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="ANT-001",
            place_of_service="22",
            billed_amount=4200.00
        )

        result = agent.classify(claim)

        # Should route CLINICAL_PATH (96413 matches CC-003)
        assert result.routing_decision == RoutingDecision.CLINICAL_PATH
        # Claude detects mismatch and scores lower
        assert result.confidence < 0.99
        # Fallback triggers
        assert result.confidence_fallback == True

    def test_ec4_prior_auth_required_marginal_indicators(self):
        """
        EC-4: Prior auth required, marginal other indicators.
        Input: Prior auth=true, routine codes otherwise.
        Expected: CLINICAL_PATH, CC-001 matched.
        """
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="d1e5b6c7-3f1a-4b9d-8c2e-4e5f6a7b8c93",
            source_claim_ref="PDF-2026-0631",
            intake_channel="PORTAL_JSON",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-6672341",
            icd10_codes=["M54.51"],  # Low back pain
            cpt_codes=["99214"],     # Office visit
            prior_auth_required=True,
            prior_auth_number=None,
            payer_id="BX-0042",
            place_of_service="11",
            billed_amount=275.00
        )

        result = agent.classify(claim)

        assert result.routing_decision == RoutingDecision.CLINICAL_PATH
        assert "CC-001" in result.criteria_provisions_matched
        assert result.confidence >= 0.70


class TestFailureModes:
    """Test failure mode scenarios from spec §10.4."""

    def test_fm3_precondition_failure_non_auto_complete(self):
        """
        Precondition failure: claim with extraction_status != AUTO_COMPLETE.
        Expected: ValueError raised, claim not classified.
        """
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="e2f6c7d8-4a2b-4c0e-9d3f-5f6a7b8c9d04",
            source_claim_ref="PDF-2026-0892",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.HUMAN_REQUIRED,  # Not AUTO_COMPLETE
            member_id="M-8814459",
            icd10_codes=["M79.3"],
            cpt_codes=["99213"],
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="UH-0017",
            place_of_service="11",
            billed_amount=850.00
        )

        with pytest.raises(ValueError) as exc_info:
            agent.classify(claim)

        assert "extraction_status" in str(exc_info.value)
        assert "AUTO_COMPLETE" in str(exc_info.value)


class TestSpecialCases:
    """Test special clinical scenarios."""

    def test_emergency_department_routes_clinical(self):
        """Test that ED visit routes to CLINICAL_PATH."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id=str(uuid4()),
            source_claim_ref="EDI-2026-ED-001",
            intake_channel="EDI_837P",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-ED-001",
            icd10_codes=["R07.9"],  # Chest pain
            cpt_codes=["99284"],    # ED visit, high complexity
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="PY-ED",
            place_of_service="23",  # Emergency department
            billed_amount=1500.00
        )

        result = agent.classify(claim)

        assert result.routing_decision == RoutingDecision.CLINICAL_PATH
        assert "CC-005" in result.criteria_provisions_matched  # ED services

    def test_surgical_procedure_routes_clinical(self):
        """Test that surgical procedure routes to CLINICAL_PATH."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id=str(uuid4()),
            source_claim_ref="EDI-2026-SURG-001",
            intake_channel="EDI_837P",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-SURG-001",
            icd10_codes=["M17.11"],  # Knee osteoarthritis
            cpt_codes=["27447"],     # Total knee arthroplasty
            prior_auth_required=True,
            prior_auth_number="PA-KNEE-001",
            payer_id="PY-SURG",
            place_of_service="22",  # Outpatient hospital
            billed_amount=35000.00
        )

        result = agent.classify(claim)

        assert result.routing_decision == RoutingDecision.CLINICAL_PATH
        # Should match CC-004 (surgical) and CC-010 (orthopedics)
        assert any(p in result.criteria_provisions_matched for p in ["CC-004", "CC-010"])

    def test_diagnostic_imaging_routes_clinical(self):
        """Test that diagnostic imaging routes to CLINICAL_PATH."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id=str(uuid4()),
            source_claim_ref="PDF-2026-MRI-001",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-MRI-001",
            icd10_codes=["M51.26"],  # Disc displacement, lumbar
            cpt_codes=["72148"],     # MRI lumbar spine
            prior_auth_required=True,
            prior_auth_number="PA-MRI-001",
            payer_id="PY-IMG",
            place_of_service="22",
            billed_amount=1200.00
        )

        result = agent.classify(claim)

        assert result.routing_decision == RoutingDecision.CLINICAL_PATH
        assert "CC-007" in result.criteria_provisions_matched  # Diagnostic imaging

    def test_mental_health_inpatient_routes_clinical(self):
        """Test that inpatient mental health routes to CLINICAL_PATH."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id=str(uuid4()),
            source_claim_ref="EDI-2026-MH-001",
            intake_channel="EDI_837I",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-MH-001",
            icd10_codes=["F32.2"],  # Major depressive disorder, severe
            cpt_codes=["90837"],    # Psychotherapy, 60 minutes
            prior_auth_required=True,
            prior_auth_number="PA-MH-001",
            payer_id="PY-MH",
            place_of_service="21",  # Inpatient hospital
            billed_amount=2400.00
        )

        result = agent.classify(claim)

        assert result.routing_decision == RoutingDecision.CLINICAL_PATH
        assert "CC-011" in result.criteria_provisions_matched  # Mental health inpatient


class TestConfidenceScoring:
    """Test confidence scoring logic."""

    def test_high_confidence_specific_match(self):
        """Test that specific code match yields high confidence."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id=str(uuid4()),
            source_claim_ref="TEST-CONF-001",
            intake_channel="EDI_837P",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-CONF-001",
            icd10_codes=["C50.911"],  # Specific oncology code
            cpt_codes=["96413"],      # Specific chemo code
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="PY-TEST",
            place_of_service="22",
            billed_amount=4000.00
        )

        result = agent.classify(claim)

        assert result.confidence >= 0.85  # High confidence
        assert result.routing_decision == RoutingDecision.CLINICAL_PATH

    def test_medium_confidence_broad_match(self):
        """Test that broad prefix match yields medium confidence."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id=str(uuid4()),
            source_claim_ref="TEST-CONF-002",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-CONF-002",
            icd10_codes=["C99.99"],  # Broad oncology prefix (C)
            cpt_codes=[],
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="PY-TEST",
            place_of_service="11",
            billed_amount=500.00
        )

        result = agent.classify(claim)

        # Should match oncology but with lower confidence due to broad match
        assert result.routing_decision == RoutingDecision.CLINICAL_PATH
        assert "CC-003" in result.criteria_provisions_matched


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
