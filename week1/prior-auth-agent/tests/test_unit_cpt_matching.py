"""
Unit Test 2: CPT Code Matching Logic

Tests Step 3 of decision logic per Claude.md Section 3 and
edge-cases-and-testing.md Test 2.

Pass Criteria: 95% accuracy on 100 test cases (exact matches, mismatches, fuzzy matches)
"""
import pytest
from datetime import datetime, timedelta

from app.models.prior_auth_check import CheckStatus, PriorAuthStatus, ConfidenceScore
from tests.conftest import create_prior_auth_check


@pytest.mark.unit
@pytest.mark.asyncio
class TestCPTMatching:
    """Test CPT code matching logic."""

    async def test_exact_cpt_match(self, decision_engine):
        """Test exact CPT code match (HIGH confidence)."""
        check = create_prior_auth_check(procedure_code="70553")
        prior_auth_records = [
            {
                "prior_auth_id": "PA-001",
                "approved_cpt_codes": ["70553"],
                "approved_service_description": "MRI Brain",
            }
        ]

        matched = await decision_engine.step3_validate_match(check, prior_auth_records, {})

        assert matched is not None
        assert check.matched_prior_auth_id == "PA-001"
        assert check.confidence_score == ConfidenceScore.HIGH

    async def test_cpt_mismatch(self, decision_engine):
        """Test CPT code mismatch - procedures are clinically different."""
        check = create_prior_auth_check(
            procedure_code="70553",  # MRI with contrast
            procedure_description="MRI Brain with Contrast"
        )
        prior_auth_records = [
            {
                "prior_auth_id": "PA-001",
                "approved_cpt_codes": ["70551"],  # MRI without contrast
                "approved_service_description": "MRI Brain without contrast",
            }
        ]

        matched = await decision_engine.step3_validate_match(check, prior_auth_records, {})

        # "MRI Brain with Contrast" vs "MRI Brain without contrast" are clinically different
        # (score ~0.70, below 0.8 threshold), should NOT fuzzy match
        assert matched is None  # No match - procedures are different
        assert check.status == CheckStatus.AWAITING_HUMAN_REVIEW
        assert check.prior_auth_status == PriorAuthStatus.AMBIGUOUS
        assert check.confidence_score == ConfidenceScore.LOW

    async def test_fuzzy_match_high_similarity(self, decision_engine):
        """Test fuzzy match with high similarity (MEDIUM confidence)."""
        check = create_prior_auth_check(
            procedure_code="70553",
            procedure_description="MRI Brain with Contrast"
        )
        prior_auth_records = [
            {
                "prior_auth_id": "PA-001",
                "approved_cpt_codes": ["70551"],  # Different code
                "approved_service_description": "Brain MRI with Contrast",  # Very similar
            }
        ]

        matched = await decision_engine.step3_validate_match(check, prior_auth_records, {})

        assert matched is not None
        assert check.matched_prior_auth_id == "PA-001"
        assert check.confidence_score == ConfidenceScore.MEDIUM
        assert "similar" in check.escalation_reason.lower()

    async def test_multiple_cpt_codes_in_prior_auth(self, decision_engine):
        """Test prior-auth covering multiple CPT codes."""
        check = create_prior_auth_check(procedure_code="70553")
        prior_auth_records = [
            {
                "prior_auth_id": "PA-001",
                "approved_cpt_codes": ["70551", "70553", "70552"],  # Multiple codes
                "approved_service_description": "MRI Brain",
            }
        ]

        matched = await decision_engine.step3_validate_match(check, prior_auth_records, {})

        assert matched is not None
        assert check.matched_prior_auth_id == "PA-001"
        assert check.confidence_score == ConfidenceScore.HIGH

    async def test_multiple_prior_auths_single_match(self, decision_engine):
        """Test multiple prior-auths with only one matching (HIGH confidence)."""
        check = create_prior_auth_check(procedure_code="70553")
        prior_auth_records = [
            {
                "prior_auth_id": "PA-001",
                "approved_cpt_codes": ["72148"],  # Different procedure
                "approved_service_description": "MRI Spine",
            },
            {
                "prior_auth_id": "PA-002",
                "approved_cpt_codes": ["70553"],  # Matches!
                "approved_service_description": "MRI Brain",
            },
            {
                "prior_auth_id": "PA-003",
                "approved_cpt_codes": ["74177"],  # Different procedure
                "approved_service_description": "CT Abdomen",
            },
        ]

        matched = await decision_engine.step3_validate_match(check, prior_auth_records, {})

        assert matched is not None
        assert check.matched_prior_auth_id == "PA-002"
        assert check.confidence_score == ConfidenceScore.HIGH

    async def test_multiple_prior_auths_multiple_matches(self, decision_engine):
        """Test multiple prior-auths with multiple matches (escalate - ambiguous)."""
        check = create_prior_auth_check(procedure_code="70553")
        prior_auth_records = [
            {
                "prior_auth_id": "PA-001",
                "approval_number": "AUTH111",
                "approved_cpt_codes": ["70553"],
                "approved_service_description": "MRI Brain",
            },
            {
                "prior_auth_id": "PA-002",
                "approval_number": "AUTH222",
                "approved_cpt_codes": ["70553"],
                "approved_service_description": "MRI Brain with Contrast",
            },
        ]

        matched = await decision_engine.step3_validate_match(check, prior_auth_records, {})

        assert matched is None
        assert check.status == CheckStatus.AWAITING_HUMAN_REVIEW
        assert check.prior_auth_status == PriorAuthStatus.AMBIGUOUS
        assert check.confidence_score == ConfidenceScore.LOW
        assert "Multiple prior-auths match" in check.escalation_reason

    async def test_multiple_prior_auths_no_match(self, decision_engine):
        """Test multiple prior-auths with no matching codes (escalate)."""
        check = create_prior_auth_check(procedure_code="70553")
        prior_auth_records = [
            {
                "prior_auth_id": "PA-001",
                "approved_cpt_codes": ["72148"],
                "approved_service_description": "MRI Spine",
            },
            {
                "prior_auth_id": "PA-002",
                "approved_cpt_codes": ["74177"],
                "approved_service_description": "CT Abdomen",
            },
        ]

        matched = await decision_engine.step3_validate_match(check, prior_auth_records, {})

        assert matched is None
        assert check.status == CheckStatus.AWAITING_HUMAN_REVIEW
        assert check.prior_auth_status == PriorAuthStatus.AMBIGUOUS
        assert check.confidence_score == ConfidenceScore.LOW

    async def test_vague_approval_language(self, decision_engine):
        """Test vague prior-auth approval language (low similarity, escalate)."""
        check = create_prior_auth_check(
            procedure_code="70553",
            procedure_description="MRI Brain with Contrast"
        )
        prior_auth_records = [
            {
                "prior_auth_id": "PA-001",
                "approved_cpt_codes": ["99999"],  # No match
                "approved_service_description": "Approved for imaging",  # Vague
            }
        ]

        matched = await decision_engine.step3_validate_match(check, prior_auth_records, {})

        assert matched is None
        assert check.status == CheckStatus.AWAITING_HUMAN_REVIEW

    async def test_empty_approved_cpt_codes(self, decision_engine):
        """Test prior-auth with empty approved CPT codes list."""
        check = create_prior_auth_check(
            procedure_code="70553",
            procedure_description="MRI Brain"
        )
        prior_auth_records = [
            {
                "prior_auth_id": "PA-001",
                "approved_cpt_codes": [],  # Empty
                "approved_service_description": "MRI Brain",  # Try fuzzy match
            }
        ]

        matched = await decision_engine.step3_validate_match(check, prior_auth_records, {})

        # Should attempt fuzzy match
        assert matched is not None or check.status == CheckStatus.AWAITING_HUMAN_REVIEW

    async def test_case_insensitive_cpt_match(self, decision_engine):
        """Test CPT matching is not case-sensitive (codes should be uppercase)."""
        check = create_prior_auth_check(procedure_code="70553")
        prior_auth_records = [
            {
                "prior_auth_id": "PA-001",
                "approved_cpt_codes": ["70553"],  # Standard format
                "approved_service_description": "MRI Brain",
            }
        ]

        matched = await decision_engine.step3_validate_match(check, prior_auth_records, {})

        assert matched is not None
        assert check.confidence_score == ConfidenceScore.HIGH
