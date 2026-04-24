"""
End-to-End Tests: Complete Workflows

Tests 11-15 from edge-cases-and-testing.md:
- Test 11: Happy Path - Valid Prior-Auth
- Test 12: Expired Prior-Auth
- Test 13: Missing Prior-Auth
- Test 14: Ambiguous Case - Multiple Prior-Auths
- Test 15: System Error - Database Unavailable

Pass Criteria: 90% pass rate
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from app.models.prior_auth_check import (
    CheckStatus,
    PriorAuthStatus,
    AIRecommendation,
    ConfidenceScore,
)
from tests.conftest import create_prior_auth_check


@pytest.mark.e2e
@pytest.mark.asyncio
class TestE2EHappyPath:
    """Test 11: Happy Path - Valid Prior-Auth (complete workflow)."""

    async def test_complete_workflow_valid_prior_auth(
        self, decision_engine, mock_prior_auth_adapter, mock_insurance_adapter, appointment_data
    ):
        """
        Test complete workflow with valid prior-auth.

        Expected flow: PENDING → CHECKING → AWAITING_HUMAN_REVIEW → APPROVED → COMPLETED
        Expected: AI recommends PROCEED with HIGH confidence
        """
        # Setup
        check = create_prior_auth_check()
        mock_insurance_adapter.check_prior_auth_requirement.return_value = {"prior_auth_required": True}
        mock_prior_auth_adapter.query_prior_auths.return_value = [
            {
                "prior_auth_id": "PA-2024-001",
                "patient_id": "PAT-12345",
                "insurance_policy_id": "INS-POL-67890",
                "approval_number": "AUTH987654",
                "approval_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "expiration_date": (datetime.now() + timedelta(days=45)).isoformat(),
                "approval_status": "ACTIVE",
                "approved_cpt_codes": ["70553"],  # Exact match
                "approved_service_description": "MRI Brain with Contrast",
                "service_category": "imaging",
            }
        ]

        # Execute
        result = await decision_engine.execute_check(check, appointment_data)

        # Verify
        assert result.status == CheckStatus.AWAITING_HUMAN_REVIEW
        assert result.prior_auth_required is True
        assert result.prior_auth_status == PriorAuthStatus.VALID
        assert result.ai_recommendation == AIRecommendation.PROCEED
        assert result.confidence_score == ConfidenceScore.HIGH
        assert result.matched_prior_auth_id == "PA-2024-001"
        assert result.confidence_rationale is not None
        assert result.created_at is not None
        assert result.last_updated_at is not None


@pytest.mark.e2e
@pytest.mark.asyncio
class TestE2EExpiredPriorAuth:
    """Test 12: Expired Prior-Auth."""

    async def test_expired_prior_auth_workflow(
        self, decision_engine, mock_prior_auth_adapter, mock_insurance_adapter, appointment_data
    ):
        """
        Test workflow with expired prior-auth.

        Expected: AI recommends RESCHEDULE with HIGH confidence
        """
        check = create_prior_auth_check()
        mock_insurance_adapter.check_prior_auth_requirement.return_value = {"prior_auth_required": True}
        mock_prior_auth_adapter.query_prior_auths.return_value = [
            {
                "prior_auth_id": "PA-2024-002",
                "patient_id": "PAT-12345",
                "insurance_policy_id": "INS-POL-67890",
                "approval_number": "AUTH111222",
                "expiration_date": (datetime.now() - timedelta(days=10)).isoformat(),  # Expired!
                "approval_status": "ACTIVE",
                "approved_cpt_codes": ["70553"],
                "approved_service_description": "MRI Brain",
            }
        ]

        result = await decision_engine.execute_check(check, appointment_data)

        assert result.prior_auth_status == PriorAuthStatus.EXPIRED
        assert result.ai_recommendation == AIRecommendation.RESCHEDULE
        assert result.confidence_score == ConfidenceScore.HIGH
        assert "expired" in result.confidence_rationale.lower()
        assert result.status == CheckStatus.AWAITING_HUMAN_REVIEW


@pytest.mark.e2e
@pytest.mark.asyncio
class TestE2EMissingPriorAuth:
    """Test 13: Missing Prior-Auth."""

    async def test_missing_prior_auth_workflow(
        self, decision_engine, mock_prior_auth_adapter, mock_insurance_adapter, appointment_data
    ):
        """
        Test workflow when no prior-auth found.

        Expected: AI escalates with HIGH confidence (confident it's missing)
        """
        check = create_prior_auth_check()
        mock_insurance_adapter.check_prior_auth_requirement.return_value = {"prior_auth_required": True}
        mock_prior_auth_adapter.query_prior_auths.return_value = []  # No prior-auth found

        result = await decision_engine.execute_check(check, appointment_data)

        assert result.prior_auth_status == PriorAuthStatus.MISSING
        assert result.ai_recommendation == AIRecommendation.ESCALATE
        assert result.confidence_score == ConfidenceScore.HIGH  # High confidence it's missing
        assert "No active prior-auth found" in result.escalation_reason
        assert result.status == CheckStatus.AWAITING_HUMAN_REVIEW


@pytest.mark.e2e
@pytest.mark.asyncio
class TestE2EAmbiguousCase:
    """Test 14: Ambiguous Case - Multiple Prior-Auths."""

    async def test_multiple_prior_auths_workflow(
        self, decision_engine, mock_prior_auth_adapter, mock_insurance_adapter, appointment_data
    ):
        """
        Test workflow with multiple matching prior-auths.

        Expected: AI escalates with LOW confidence (ambiguous which applies)
        """
        check = create_prior_auth_check()
        mock_insurance_adapter.check_prior_auth_requirement.return_value = {"prior_auth_required": True}
        mock_prior_auth_adapter.query_prior_auths.return_value = [
            {
                "prior_auth_id": "PA-001",
                "approval_number": "AUTH111",
                "approved_cpt_codes": ["70553"],
                "expiration_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "approved_service_description": "MRI Brain",
            },
            {
                "prior_auth_id": "PA-002",
                "approval_number": "AUTH222",
                "approved_cpt_codes": ["70553"],
                "expiration_date": (datetime.now() + timedelta(days=45)).isoformat(),
                "approved_service_description": "MRI Brain with Contrast",
            },
        ]

        result = await decision_engine.execute_check(check, appointment_data)

        assert result.prior_auth_status == PriorAuthStatus.AMBIGUOUS
        assert result.ai_recommendation == AIRecommendation.ESCALATE
        assert result.confidence_score == ConfidenceScore.LOW
        assert "Multiple prior-auths match" in result.escalation_reason
        assert result.status == CheckStatus.AWAITING_HUMAN_REVIEW


@pytest.mark.e2e
@pytest.mark.asyncio
class TestE2ESystemError:
    """Test 15: System Error - Database Unavailable."""

    async def test_database_unavailable_workflow(
        self, decision_engine, mock_prior_auth_adapter, mock_insurance_adapter, appointment_data
    ):
        """
        Test workflow when prior-auth database is unavailable.

        Expected: System transitions to FAILED, manual fallback triggered
        """
        check = create_prior_auth_check()
        mock_insurance_adapter.check_prior_auth_requirement.return_value = {"prior_auth_required": True}
        mock_prior_auth_adapter.query_prior_auths.side_effect = Exception("Database timeout")

        result = await decision_engine.execute_check(check, appointment_data)

        assert result.status == CheckStatus.FAILED
        assert "Prior-auth database unavailable" in result.escalation_reason
        # Manual fallback task should be created (tested in integration tests)


@pytest.mark.e2e
@pytest.mark.asyncio
class TestE2ENoRequirementWorkflow:
    """Test workflow when procedure doesn't require prior-auth."""

    async def test_no_prior_auth_required(
        self, decision_engine, mock_insurance_adapter, appointment_data
    ):
        """
        Test workflow when procedure doesn't require prior-auth.

        Expected: Quick exit after Step 1, status COMPLETED
        """
        check = create_prior_auth_check(procedure_code="99213")  # Office visit
        mock_insurance_adapter.check_prior_auth_requirement.return_value = {"prior_auth_required": False}

        result = await decision_engine.execute_check(check, appointment_data)

        assert result.prior_auth_required is False
        assert result.status == CheckStatus.COMPLETED
        assert "does not require prior-authorization" in result.confidence_rationale


@pytest.mark.e2e
@pytest.mark.asyncio
class TestE2EExpiringSoonWorkflow:
    """Test workflow with prior-auth expiring soon."""

    async def test_expiring_soon_escalation(
        self, decision_engine, mock_prior_auth_adapter, mock_insurance_adapter, appointment_data
    ):
        """
        Test workflow with prior-auth expiring within 7 days.

        Expected: AI escalates with MEDIUM confidence
        """
        check = create_prior_auth_check()
        scheduled_date = datetime.now() + timedelta(days=2)
        check.scheduled_date = scheduled_date

        mock_insurance_adapter.check_prior_auth_requirement.return_value = {"prior_auth_required": True}
        mock_prior_auth_adapter.query_prior_auths.return_value = [
            {
                "prior_auth_id": "PA-003",
                "approved_cpt_codes": ["70553"],
                "expiration_date": (scheduled_date + timedelta(days=5)).isoformat(),  # 5 days after
                "approved_service_description": "MRI Brain",
            }
        ]

        result = await decision_engine.execute_check(check, appointment_data)

        assert result.prior_auth_status == PriorAuthStatus.EXPIRING_SOON
        assert result.ai_recommendation == AIRecommendation.ESCALATE
        assert result.confidence_score == ConfidenceScore.MEDIUM


@pytest.mark.e2e
@pytest.mark.asyncio
class TestE2EPerformance:
    """Test end-to-end performance requirements."""

    async def test_workflow_completes_within_10_seconds(
        self, decision_engine, mock_prior_auth_adapter, mock_insurance_adapter, appointment_data
    ):
        """
        Test that complete workflow completes within 10 seconds (NFR-PA-001).

        This is a smoke test for performance - detailed benchmarking separate.
        """
        import time

        check = create_prior_auth_check()
        mock_insurance_adapter.check_prior_auth_requirement.return_value = {"prior_auth_required": True}
        mock_prior_auth_adapter.query_prior_auths.return_value = [
            {
                "prior_auth_id": "PA-001",
                "approved_cpt_codes": ["70553"],
                "expiration_date": (datetime.now() + timedelta(days=45)).isoformat(),
                "approved_service_description": "MRI Brain",
            }
        ]

        start_time = time.time()
        result = await decision_engine.execute_check(check, appointment_data)
        elapsed_time = time.time() - start_time

        assert result.status in [CheckStatus.AWAITING_HUMAN_REVIEW, CheckStatus.COMPLETED]
        assert elapsed_time < 10.0  # Should complete in <10 seconds
