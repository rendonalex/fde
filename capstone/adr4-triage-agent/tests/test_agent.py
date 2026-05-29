"""
Unit tests for ADR-4 Triage Agent.
Tests classification logic, confidence scoring, and guard rails.
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import NormalizedClaimRecord, RoutingDecision, RoutingMode, ExtractionStatus
from app.agent import TriageAgent
from app.codebook import CodebookLoader


class TestCodebookMatching:
    """Test codebook loading and matching logic."""

    def test_codebook_loads_successfully(self):
        """Test that codebook loads from config file."""
        codebook_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config",
            "criteria-codebook.json"
        )
        loader = CodebookLoader(codebook_path)
        codebook = loader.load()

        assert codebook is not None
        assert codebook.codebook_version == "1.0.0"
        assert codebook.approved_by == "dr.webb"
        assert len(loader.provisions) > 0

    def test_prior_auth_trigger_matches(self):
        """Test that prior_auth_required=True matches CC-001."""
        codebook_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config",
            "criteria-codebook.json"
        )
        loader = CodebookLoader(codebook_path)
        loader.load()

        matched, indicators = loader.match_claim(
            icd10_codes=[],
            cpt_codes=[],
            prior_auth_required=True
        )

        assert "CC-001" in matched
        assert "Prior Auth: Required" in indicators

    def test_icd10_prefix_matching(self):
        """Test ICD-10 prefix matching (oncology codes)."""
        codebook_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config",
            "criteria-codebook.json"
        )
        loader = CodebookLoader(codebook_path)
        loader.load()

        # C50.911 should match CC-003 (oncology)
        matched, indicators = loader.match_claim(
            icd10_codes=["C50.911"],
            cpt_codes=[],
            prior_auth_required=False
        )

        assert "CC-003" in matched
        assert "ICD-10: C50.911" in indicators

    def test_cpt_prefix_matching(self):
        """Test CPT prefix matching (chemotherapy)."""
        codebook_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config",
            "criteria-codebook.json"
        )
        loader = CodebookLoader(codebook_path)
        loader.load()

        # 96413 should match CC-003 (chemotherapy)
        matched, indicators = loader.match_claim(
            icd10_codes=[],
            cpt_codes=["96413"],
            prior_auth_required=False
        )

        assert "CC-003" in matched
        assert "CPT: 96413" in indicators

    def test_no_match_returns_empty(self):
        """Test that routine claim returns no matches."""
        codebook_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config",
            "criteria-codebook.json"
        )
        loader = CodebookLoader(codebook_path)
        loader.load()

        # Z00.00 (routine exam) and 99213 (office visit) should not match
        matched, indicators = loader.match_claim(
            icd10_codes=["Z00.00"],
            cpt_codes=["99213"],
            prior_auth_required=False
        )

        assert len(matched) == 0
        assert "ICD-10: Z00.00" in indicators
        assert "CPT: 99213" in indicators


class TestAgentClassification:
    """Test agent classification logic."""

    def test_agent_initializes(self):
        """Test that agent initializes correctly."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        assert agent.mode == RoutingMode.SHADOW
        assert agent.confidence_threshold == 0.70
        assert agent.codebook is not None
        assert agent.system_prompt is not None

    def test_routine_claim_routes_fast_path(self):
        """Test that routine office visit routes to FAST_PATH."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="test-001",
            source_claim_ref="PDF-2026-0001",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-12345",
            icd10_codes=["Z00.00"],
            cpt_codes=["99213"],
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="PY-001",
            place_of_service="11",
            billed_amount=185.00
        )

        result = agent.classify(claim)

        assert result.routing_decision == RoutingDecision.FAST_PATH
        assert result.confidence >= 0.70
        assert result.confidence_fallback == False
        assert len(result.criteria_provisions_matched) == 0
        assert result.routing_mode == RoutingMode.SHADOW

    def test_oncology_claim_routes_clinical_path(self):
        """Test that oncology claim routes to CLINICAL_PATH."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="test-002",
            source_claim_ref="EDI-2026-0002",
            intake_channel="EDI_837P",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-67890",
            icd10_codes=["C50.911", "Z79.899"],
            cpt_codes=["96413", "96415"],
            prior_auth_required=True,
            prior_auth_number="PA-20260410-4421",
            payer_id="PY-002",
            place_of_service="22",
            billed_amount=4200.00
        )

        result = agent.classify(claim)

        assert result.routing_decision == RoutingDecision.CLINICAL_PATH
        assert result.confidence >= 0.70
        assert "CC-003" in result.criteria_provisions_matched  # Oncology
        assert "CC-001" in result.criteria_provisions_matched  # Prior auth
        assert result.routing_mode == RoutingMode.SHADOW

    def test_prior_auth_only_routes_clinical(self):
        """Test that prior auth alone routes to CLINICAL_PATH."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="test-003",
            source_claim_ref="PDF-2026-0003",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-111222",
            icd10_codes=["M54.51"],  # Low back pain (not clinical trigger)
            cpt_codes=["99214"],     # Office visit (not clinical trigger)
            prior_auth_required=True,
            prior_auth_number=None,
            payer_id="PY-003",
            place_of_service="11",
            billed_amount=275.00
        )

        result = agent.classify(claim)

        assert result.routing_decision == RoutingDecision.CLINICAL_PATH
        assert "CC-001" in result.criteria_provisions_matched
        assert result.routing_mode == RoutingMode.SHADOW

    def test_confidence_fallback_overrides_to_clinical(self):
        """Test that clinically contradictory codes trigger lower confidence and fallback."""
        # Use high threshold to detect when Claude scores lower due to clinical mismatch
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.95)

        # J20.9 (bronchitis) + 96413 (chemotherapy) = clinically contradictory
        # Claude should detect mismatch and return lower confidence
        claim = NormalizedClaimRecord(
            claim_id="CLM-2026-9003",
            source_claim_ref="CLM-2026-9003",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="YYL88234510",
            icd10_codes=["J20.9"],  # Acute bronchitis
            cpt_codes=["96413"],    # Chemotherapy administration (contradictory!)
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="ANT-001",
            place_of_service="22",
            billed_amount=4200.00
        )

        result = agent.classify(claim)

        # Should route CLINICAL_PATH (96413 matches CC-003 Oncology)
        assert result.routing_decision == RoutingDecision.CLINICAL_PATH
        # Claude should detect clinical mismatch and score lower confidence
        assert result.confidence < 0.95
        # Fallback should trigger due to low confidence
        assert result.confidence_fallback == True

    def test_precondition_validation_fails(self):
        """Test that non-AUTO_COMPLETE claims are rejected."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="test-005",
            source_claim_ref="PDF-2026-0005",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.HUMAN_REQUIRED,  # Not AUTO_COMPLETE
            member_id="M-555666",
            icd10_codes=["Z00.00"],
            cpt_codes=["99213"],
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="PY-005",
            place_of_service="11",
            billed_amount=185.00
        )

        with pytest.raises(ValueError) as exc_info:
            agent.classify(claim)

        assert "extraction_status" in str(exc_info.value)
        assert "AUTO_COMPLETE" in str(exc_info.value)


class TestGuardRails:
    """Test guard rails and safety mechanisms."""

    def test_shadow_mode_enforced(self):
        """Test that SHADOW mode is enforced in output."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="test-006",
            source_claim_ref="PDF-2026-0006",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-777888",
            icd10_codes=["Z00.00"],
            cpt_codes=["99213"],
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="PY-006",
            place_of_service="11",
            billed_amount=185.00
        )

        result = agent.classify(claim)

        assert result.routing_mode == RoutingMode.SHADOW
        assert "SHADOW" in agent.system_prompt

    def test_live_mode_enforced(self):
        """Test that LIVE mode is enforced in output."""
        agent = TriageAgent(mode="LIVE", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="test-007",
            source_claim_ref="PDF-2026-0007",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-999000",
            icd10_codes=["Z00.00"],
            cpt_codes=["99213"],
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="PY-007",
            place_of_service="11",
            billed_amount=185.00
        )

        result = agent.classify(claim)

        assert result.routing_mode == RoutingMode.LIVE
        assert "LIVE" in agent.system_prompt

    def test_reasoning_trace_present(self):
        """Test that reasoning trace is always generated."""
        agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)

        claim = NormalizedClaimRecord(
            claim_id="test-008",
            source_claim_ref="PDF-2026-0008",
            intake_channel="CMS1500_PDF",
            extraction_status=ExtractionStatus.AUTO_COMPLETE,
            member_id="M-111000",
            icd10_codes=["Z00.00"],
            cpt_codes=["99213"],
            prior_auth_required=False,
            prior_auth_number=None,
            payer_id="PY-008",
            place_of_service="11",
            billed_amount=185.00
        )

        result = agent.classify(claim)

        assert len(result.reasoning_trace) > 0
        assert "Step 1" in result.reasoning_trace
        assert "Step 2" in result.reasoning_trace
        # Claude may say "Final decision" instead of "Step 6"
        assert ("Step 6" in result.reasoning_trace or "Final decision" in result.reasoning_trace)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
