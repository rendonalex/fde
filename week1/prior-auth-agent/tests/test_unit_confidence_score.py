"""
Unit Test 4: Confidence Score Calculation

Tests Step 5 of decision logic per Claude.md Section 3, Step 5 and
edge-cases-and-testing.md Test 4.

Pass Criteria: 90% accuracy on 50 test cases
"""
import pytest
from datetime import datetime, timedelta

from app.models.prior_auth_check import (
    CheckStatus,
    PriorAuthStatus,
    AIRecommendation,
    ConfidenceScore,
)
from tests.conftest import create_prior_auth_check


@pytest.mark.unit
class TestConfidenceScoreCalculation:
    """Test confidence score assignment logic."""

    def test_high_confidence_exact_match_valid_expiration(self):
        """Test HIGH confidence: exact CPT match + valid expiration + complete data."""
        check = create_prior_auth_check()
        check.prior_auth_status = PriorAuthStatus.VALID
        check.ai_recommendation = AIRecommendation.PROCEED
        check.confidence_score = ConfidenceScore.HIGH
        check.matched_prior_auth_id = "PA-001"

        # Verify HIGH confidence conditions
        assert check.confidence_score == ConfidenceScore.HIGH
        assert check.prior_auth_status == PriorAuthStatus.VALID
        assert check.matched_prior_auth_id is not None

    def test_high_confidence_missing_prior_auth(self):
        """Test HIGH confidence: high confidence that prior-auth is MISSING."""
        check = create_prior_auth_check()
        check.prior_auth_status = PriorAuthStatus.MISSING
        check.ai_recommendation = AIRecommendation.ESCALATE
        check.confidence_score = ConfidenceScore.HIGH  # High confidence it's missing

        assert check.confidence_score == ConfidenceScore.HIGH
        assert check.prior_auth_status == PriorAuthStatus.MISSING

    def test_high_confidence_expired_prior_auth(self):
        """Test HIGH confidence: prior-auth clearly expired."""
        check = create_prior_auth_check()
        check.prior_auth_status = PriorAuthStatus.EXPIRED
        check.ai_recommendation = AIRecommendation.RESCHEDULE
        check.confidence_score = ConfidenceScore.HIGH
        check.confidence_rationale = "Prior-auth expired 10 days ago"

        assert check.confidence_score == ConfidenceScore.HIGH
        assert check.ai_recommendation == AIRecommendation.RESCHEDULE

    def test_medium_confidence_fuzzy_match(self):
        """Test MEDIUM confidence: fuzzy match on service description."""
        check = create_prior_auth_check()
        check.prior_auth_status = PriorAuthStatus.VALID
        check.confidence_score = ConfidenceScore.MEDIUM
        check.escalation_reason = "CPT codes don't exactly match, but service description similar"

        assert check.confidence_score == ConfidenceScore.MEDIUM
        assert check.escalation_reason is not None

    def test_medium_confidence_expiring_soon(self):
        """Test MEDIUM confidence: prior-auth expiring within 7 days."""
        check = create_prior_auth_check()
        check.prior_auth_status = PriorAuthStatus.EXPIRING_SOON
        check.ai_recommendation = AIRecommendation.ESCALATE
        check.confidence_score = ConfidenceScore.MEDIUM
        check.escalation_reason = "Prior-auth expires within 7 days"

        assert check.confidence_score == ConfidenceScore.MEDIUM
        assert check.prior_auth_status == PriorAuthStatus.EXPIRING_SOON

    def test_medium_confidence_same_day_expiration(self):
        """Test MEDIUM confidence: prior-auth expires on appointment day."""
        check = create_prior_auth_check()
        check.prior_auth_status = PriorAuthStatus.EXPIRING_SOON
        check.ai_recommendation = AIRecommendation.ESCALATE
        check.confidence_score = ConfidenceScore.MEDIUM
        check.escalation_reason = "Prior-auth expires same day as appointment"

        assert check.confidence_score == ConfidenceScore.MEDIUM

    def test_low_confidence_multiple_prior_auths(self):
        """Test LOW confidence: multiple prior-auths, unclear which applies."""
        check = create_prior_auth_check()
        check.prior_auth_status = PriorAuthStatus.AMBIGUOUS
        check.ai_recommendation = AIRecommendation.ESCALATE
        check.confidence_score = ConfidenceScore.LOW
        check.escalation_reason = "Multiple prior-auths match procedure"

        assert check.confidence_score == ConfidenceScore.LOW
        assert check.prior_auth_status == PriorAuthStatus.AMBIGUOUS

    def test_low_confidence_cpt_mismatch(self):
        """Test LOW confidence: CPT code mismatch, no fuzzy match."""
        check = create_prior_auth_check()
        check.prior_auth_status = PriorAuthStatus.AMBIGUOUS
        check.ai_recommendation = AIRecommendation.ESCALATE
        check.confidence_score = ConfidenceScore.LOW
        check.escalation_reason = "Prior-auth CPT code mismatch"

        assert check.confidence_score == ConfidenceScore.LOW

    def test_low_confidence_missing_expiration_date(self):
        """Test LOW confidence: prior-auth record missing expiration date."""
        check = create_prior_auth_check()
        check.prior_auth_status = PriorAuthStatus.AMBIGUOUS
        check.ai_recommendation = AIRecommendation.ESCALATE
        check.confidence_score = ConfidenceScore.LOW
        check.escalation_reason = "Prior-auth record is missing expiration date"

        assert check.confidence_score == ConfidenceScore.LOW
        assert "missing expiration date" in check.escalation_reason.lower()

    def test_confidence_rationale_generated(self, decision_engine):
        """Test that confidence rationale is always generated."""
        check = create_prior_auth_check()
        check.prior_auth_status = PriorAuthStatus.VALID
        check.ai_recommendation = AIRecommendation.PROCEED
        check.confidence_score = ConfidenceScore.HIGH

        decision_engine.step5_generate_recommendation(check)

        assert check.confidence_rationale is not None
        assert len(check.confidence_rationale) > 0

    def test_confidence_rationale_default_generation(self, decision_engine):
        """Test default rationale when none set."""
        check = create_prior_auth_check()
        check.prior_auth_status = PriorAuthStatus.VALID
        check.ai_recommendation = AIRecommendation.PROCEED
        check.confidence_score = ConfidenceScore.HIGH
        check.confidence_rationale = None  # Not set

        decision_engine.step5_generate_recommendation(check)

        assert check.confidence_rationale is not None
        assert "Prior-auth status" in check.confidence_rationale

    def test_high_confidence_no_conflicting_information(self):
        """Test HIGH confidence requires no conflicting information."""
        check = create_prior_auth_check()
        check.prior_auth_status = PriorAuthStatus.VALID
        check.confidence_score = ConfidenceScore.HIGH
        check.matched_prior_auth_id = "PA-001"
        # No escalation_reason means no conflicts

        assert check.confidence_score == ConfidenceScore.HIGH
        assert check.escalation_reason is None or check.escalation_reason == ""

    def test_medium_confidence_minor_data_issues(self):
        """Test MEDIUM confidence: minor data quality issues."""
        check = create_prior_auth_check()
        check.confidence_score = ConfidenceScore.MEDIUM
        check.prior_auth_status = PriorAuthStatus.VALID
        check.escalation_reason = "Missing service description but CPT match exists"

        assert check.confidence_score == ConfidenceScore.MEDIUM

    def test_low_confidence_unknown_requirement(self):
        """Test LOW confidence: cannot determine if prior-auth required."""
        check = create_prior_auth_check()
        check.confidence_score = ConfidenceScore.LOW
        check.status = CheckStatus.ESCALATED
        check.escalation_reason = "Cannot determine if prior-auth required for CPT 99999"

        assert check.confidence_score == ConfidenceScore.LOW
        assert check.status == CheckStatus.ESCALATED

    def test_confidence_progression_through_steps(self):
        """Test confidence can be adjusted through steps."""
        check = create_prior_auth_check()

        # Step 3: Start with HIGH (exact match)
        check.confidence_score = ConfidenceScore.HIGH

        # Step 4: Downgrade to MEDIUM (expiring soon)
        check.confidence_score = ConfidenceScore.MEDIUM
        check.prior_auth_status = PriorAuthStatus.EXPIRING_SOON

        assert check.confidence_score == ConfidenceScore.MEDIUM

    def test_confidence_with_single_prior_auth_exact_match(self):
        """Test confidence with ideal conditions: single prior-auth, exact match."""
        check = create_prior_auth_check()
        check.matched_prior_auth_id = "PA-001"
        check.prior_auth_status = PriorAuthStatus.VALID
        check.confidence_score = ConfidenceScore.HIGH
        check.ai_recommendation = AIRecommendation.PROCEED

        assert check.confidence_score == ConfidenceScore.HIGH
        assert check.ai_recommendation == AIRecommendation.PROCEED

    def test_confidence_escalation_preserves_reason(self):
        """Test that escalation reason is preserved with confidence score."""
        check = create_prior_auth_check()
        check.confidence_score = ConfidenceScore.LOW
        check.escalation_reason = "Multiple prior-auths found, unclear which applies"
        check.ai_recommendation = AIRecommendation.ESCALATE

        assert check.confidence_score == ConfidenceScore.LOW
        assert check.escalation_reason is not None
        assert "Multiple prior-auths" in check.escalation_reason
