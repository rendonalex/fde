"""
Unit Test 3: Expiration Date Calculation

Tests Step 4 of decision logic per Claude.md Section 3 and
edge-cases-and-testing.md Test 3.

Pass Criteria: 100% accuracy on 20 test cases (various expiration scenarios)
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
@pytest.mark.asyncio
class TestExpirationDateCalculation:
    """Test expiration date validation logic."""

    async def test_valid_prior_auth_30_days_future(self, decision_engine):
        """Test prior-auth valid for 30 days after appointment (VALID, PROCEED, HIGH)."""
        check = create_prior_auth_check()
        check.scheduled_date = datetime.now() + timedelta(days=2)

        prior_auth = {
            "prior_auth_id": "PA-001",
            "expiration_date": (datetime.now() + timedelta(days=32)).isoformat(),
        }

        await decision_engine.step4_check_expiration(check, prior_auth, {})

        assert check.prior_auth_status == PriorAuthStatus.VALID
        assert check.ai_recommendation == AIRecommendation.PROCEED
        assert check.confidence_score == ConfidenceScore.HIGH
        assert "valid until" in check.confidence_rationale.lower()

    async def test_expired_prior_auth_10_days_past(self, decision_engine):
        """Test prior-auth expired 10 days ago (EXPIRED, RESCHEDULE, HIGH)."""
        check = create_prior_auth_check()
        check.scheduled_date = datetime.now() + timedelta(days=2)

        prior_auth = {
            "prior_auth_id": "PA-001",
            "expiration_date": (datetime.now() - timedelta(days=10)).isoformat(),
        }

        await decision_engine.step4_check_expiration(check, prior_auth, {})

        assert check.prior_auth_status == PriorAuthStatus.EXPIRED
        assert check.ai_recommendation == AIRecommendation.RESCHEDULE
        assert check.confidence_score == ConfidenceScore.HIGH
        assert "expired" in check.confidence_rationale.lower()

    async def test_expires_same_day_as_appointment(self, decision_engine):
        """Test prior-auth expires on appointment day (EXPIRING_SOON, ESCALATE, MEDIUM)."""
        scheduled_date = datetime.now() + timedelta(days=2)
        check = create_prior_auth_check()
        check.scheduled_date = scheduled_date

        prior_auth = {
            "prior_auth_id": "PA-001",
            "expiration_date": scheduled_date.isoformat(),  # Same day
        }

        await decision_engine.step4_check_expiration(check, prior_auth, {})

        assert check.prior_auth_status == PriorAuthStatus.EXPIRING_SOON
        assert check.ai_recommendation == AIRecommendation.ESCALATE
        assert check.confidence_score == ConfidenceScore.MEDIUM
        assert "expires on appointment date" in check.confidence_rationale.lower()
        assert "same day" in check.escalation_reason.lower()

    async def test_expires_within_7_days(self, decision_engine):
        """Test prior-auth expires in 5 days (EXPIRING_SOON, ESCALATE, MEDIUM)."""
        check = create_prior_auth_check()
        check.scheduled_date = datetime.now() + timedelta(days=2)

        # Expires 7 days after scheduled date (within warning threshold)
        prior_auth = {
            "prior_auth_id": "PA-001",
            "expiration_date": (datetime.now() + timedelta(days=7)).isoformat(),
        }

        await decision_engine.step4_check_expiration(check, prior_auth, {})

        assert check.prior_auth_status == PriorAuthStatus.EXPIRING_SOON
        assert check.ai_recommendation == AIRecommendation.ESCALATE
        assert check.confidence_score == ConfidenceScore.MEDIUM

    async def test_expires_exactly_7_days_after(self, decision_engine):
        """Test prior-auth expires exactly 7 days after appointment (boundary case)."""
        check = create_prior_auth_check()
        check.scheduled_date = datetime.now()

        prior_auth = {
            "prior_auth_id": "PA-001",
            "expiration_date": (datetime.now() + timedelta(days=7)).isoformat(),
        }

        await decision_engine.step4_check_expiration(check, prior_auth, {})

        # At exactly 7 days, should be EXPIRING_SOON (<=7 means <=)
        assert check.prior_auth_status == PriorAuthStatus.EXPIRING_SOON
        assert check.ai_recommendation == AIRecommendation.ESCALATE

    async def test_expires_8_days_after(self, decision_engine):
        """Test prior-auth expires 8 days after appointment (VALID, just outside warning)."""
        check = create_prior_auth_check()
        check.scheduled_date = datetime.now()

        prior_auth = {
            "prior_auth_id": "PA-001",
            "expiration_date": (datetime.now() + timedelta(days=8)).isoformat(),
        }

        await decision_engine.step4_check_expiration(check, prior_auth, {})

        assert check.prior_auth_status == PriorAuthStatus.VALID
        assert check.ai_recommendation == AIRecommendation.PROCEED

    async def test_expired_1_day_ago(self, decision_engine):
        """Test prior-auth expired yesterday (EXPIRED, RESCHEDULE, HIGH)."""
        check = create_prior_auth_check()
        check.scheduled_date = datetime.now() + timedelta(days=2)

        prior_auth = {
            "prior_auth_id": "PA-001",
            "expiration_date": (datetime.now() - timedelta(days=1)).isoformat(),
        }

        await decision_engine.step4_check_expiration(check, prior_auth, {})

        assert check.prior_auth_status == PriorAuthStatus.EXPIRED
        assert check.ai_recommendation == AIRecommendation.RESCHEDULE
        assert check.confidence_score == ConfidenceScore.HIGH

    async def test_expires_1_day_after_appointment(self, decision_engine):
        """Test prior-auth expires 1 day after appointment (EXPIRING_SOON)."""
        check = create_prior_auth_check()
        check.scheduled_date = datetime.now()

        prior_auth = {
            "prior_auth_id": "PA-001",
            "expiration_date": (datetime.now() + timedelta(days=1)).isoformat(),
        }

        await decision_engine.step4_check_expiration(check, prior_auth, {})

        assert check.prior_auth_status == PriorAuthStatus.EXPIRING_SOON
        assert check.ai_recommendation == AIRecommendation.ESCALATE

    async def test_expires_6_months_future(self, decision_engine):
        """Test prior-auth valid for 6 months (VALID, PROCEED, HIGH)."""
        check = create_prior_auth_check()
        check.scheduled_date = datetime.now()

        prior_auth = {
            "prior_auth_id": "PA-001",
            "expiration_date": (datetime.now() + timedelta(days=180)).isoformat(),
        }

        await decision_engine.step4_check_expiration(check, prior_auth, {})

        assert check.prior_auth_status == PriorAuthStatus.VALID
        assert check.ai_recommendation == AIRecommendation.PROCEED
        assert check.confidence_score == ConfidenceScore.HIGH

    async def test_no_prior_auth_provided(self, decision_engine):
        """Test when no prior-auth record provided (should not crash)."""
        check = create_prior_auth_check()

        await decision_engine.step4_check_expiration(check, None, {})

        # Should gracefully handle None (no status change)
        assert check.prior_auth_status is None or check.prior_auth_status == PriorAuthStatus.MISSING

    async def test_confidence_score_preserved_from_step3(self, decision_engine):
        """Test that MEDIUM confidence from Step 3 (fuzzy match) is preserved."""
        check = create_prior_auth_check()
        check.scheduled_date = datetime.now()
        check.confidence_score = ConfidenceScore.MEDIUM  # Set by Step 3

        prior_auth = {
            "prior_auth_id": "PA-001",
            "expiration_date": (datetime.now() + timedelta(days=30)).isoformat(),
        }

        await decision_engine.step4_check_expiration(check, prior_auth, {})

        # Should keep MEDIUM confidence (not upgrade to HIGH)
        assert check.confidence_score == ConfidenceScore.MEDIUM
        assert check.prior_auth_status == PriorAuthStatus.VALID
        assert check.ai_recommendation == AIRecommendation.PROCEED

    async def test_days_until_expiration_calculation(self, decision_engine):
        """Test days until expiration is calculated correctly."""
        check = create_prior_auth_check()
        scheduled_date = datetime(2024, 6, 1, 10, 0, 0)
        expiration_date = datetime(2024, 6, 15, 23, 59, 59)  # 14 days later
        check.scheduled_date = scheduled_date

        prior_auth = {
            "prior_auth_id": "PA-001",
            "expiration_date": expiration_date.isoformat(),
        }

        await decision_engine.step4_check_expiration(check, prior_auth, {})

        # 14 days difference, should be VALID
        assert check.prior_auth_status == PriorAuthStatus.VALID
        assert "14 days after appointment" in check.confidence_rationale

    async def test_timezone_handling(self, decision_engine):
        """Test timezone handling in date comparison."""
        check = create_prior_auth_check()
        check.scheduled_date = datetime.now()

        # ISO format with Z timezone
        prior_auth = {
            "prior_auth_id": "PA-001",
            "expiration_date": (datetime.now() + timedelta(days=30)).isoformat() + "Z",
        }

        await decision_engine.step4_check_expiration(check, prior_auth, {})

        # Should handle timezone conversion correctly
        assert check.prior_auth_status == PriorAuthStatus.VALID
