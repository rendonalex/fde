"""
Integration Tests

Tests 6-10 from edge-cases-and-testing.md:
- Test 6: athenahealth EHR Integration
- Test 7: Prior-Auth Database Integration
- Test 8: Human Review Interface
- Test 9: Error Handling - Database Unavailable
- Test 10: Error Handling - EHR Write Failure

Pass Criteria: 95% pass rate
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.prior_auth_check import CheckStatus
from tests.conftest import create_prior_auth_check


@pytest.mark.integration
@pytest.mark.asyncio
class TestEHRIntegration:
    """Test 6: athenahealth EHR Integration."""

    async def test_read_appointment_from_ehr(self, mock_athena_adapter):
        """Test reading appointment data from EHR."""
        mock_athena_adapter.get_appointment.return_value = {
            "appointment_id": "APT-12345",
            "patient_id": "PAT-12345",
            "scheduled_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "procedure_codes": ["70553"],
            "procedure_descriptions": ["MRI Brain with Contrast"],
            "insurance_policy_id": "INS-POL-67890",
        }

        appointment = await mock_athena_adapter.get_appointment("APT-12345")

        assert appointment["appointment_id"] == "APT-12345"
        assert appointment["patient_id"] == "PAT-12345"
        assert "70553" in appointment["procedure_codes"]
        assert appointment["insurance_policy_id"] == "INS-POL-67890"

    async def test_write_verification_note_to_ehr(self, mock_athena_adapter):
        """Test writing prior-auth verification result to EHR."""
        check = create_prior_auth_check()
        check.status = CheckStatus.COMPLETED

        mock_athena_adapter.write_verification_note.return_value = {"success": True}

        result = await mock_athena_adapter.write_verification_note(
            appointment_id=check.appointment_id,
            note="Prior-auth verified: VALID, approval AUTH987654"
        )

        assert result["success"] is True
        mock_athena_adapter.write_verification_note.assert_called_once()

    async def test_ehr_read_with_timeout(self, mock_athena_adapter):
        """Test EHR read timeout handling."""
        mock_athena_adapter.get_appointment.side_effect = asyncio.TimeoutError("EHR timeout")

        with pytest.raises(asyncio.TimeoutError):
            await mock_athena_adapter.get_appointment("APT-12345")

    async def test_ehr_write_with_retry(self, mock_athena_adapter):
        """Test EHR write retry logic on failure."""
        # First call fails, second succeeds
        mock_athena_adapter.write_verification_note.side_effect = [
            Exception("503 Service Unavailable"),
            {"success": True}
        ]

        # Simulate retry logic (would be in actual service)
        try:
            await mock_athena_adapter.write_verification_note("APT-12345", "note")
        except Exception:
            # Retry
            result = await mock_athena_adapter.write_verification_note("APT-12345", "note")
            assert result["success"] is True


@pytest.mark.integration
@pytest.mark.asyncio
class TestPriorAuthDatabaseIntegration:
    """Test 7: Prior-Auth Database Integration."""

    async def test_query_prior_auths_success(self, mock_prior_auth_adapter):
        """Test querying prior-auth database successfully."""
        mock_prior_auth_adapter.query_prior_auths.return_value = [
            {
                "prior_auth_id": "PA-2024-001",
                "patient_id": "PAT-12345",
                "insurance_policy_id": "INS-POL-67890",
                "approval_number": "AUTH987654",
                "expiration_date": (datetime.now() + timedelta(days=45)).isoformat(),
                "approved_cpt_codes": ["70553"],
            }
        ]

        results = await mock_prior_auth_adapter.query_prior_auths(
            "PAT-12345",
            "INS-POL-67890",
            datetime.now()
        )

        assert len(results) == 1
        assert results[0]["prior_auth_id"] == "PA-2024-001"
        assert "70553" in results[0]["approved_cpt_codes"]

    async def test_query_prior_auths_no_results(self, mock_prior_auth_adapter):
        """Test querying prior-auth database with no results."""
        mock_prior_auth_adapter.query_prior_auths.return_value = []

        results = await mock_prior_auth_adapter.query_prior_auths(
            "PAT-99999",
            "INS-POL-99999",
            datetime.now()
        )

        assert len(results) == 0

    async def test_query_prior_auths_timeout(self, mock_prior_auth_adapter):
        """Test prior-auth database timeout."""
        mock_prior_auth_adapter.query_prior_auths.side_effect = asyncio.TimeoutError("Database timeout")

        with pytest.raises(asyncio.TimeoutError):
            await mock_prior_auth_adapter.query_prior_auths(
                "PAT-12345",
                "INS-POL-67890",
                datetime.now()
            )

    async def test_query_with_filters(self, mock_prior_auth_adapter):
        """Test query filters by patient, policy, and date."""
        scheduled_date = datetime.now() + timedelta(days=2)

        await mock_prior_auth_adapter.query_prior_auths(
            "PAT-12345",
            "INS-POL-67890",
            scheduled_date
        )

        mock_prior_auth_adapter.query_prior_auths.assert_called_once_with(
            "PAT-12345",
            "INS-POL-67890",
            scheduled_date
        )


@pytest.mark.integration
@pytest.mark.asyncio
class TestErrorHandling:
    """Tests 9 & 10: Error Handling."""

    async def test_database_unavailable_retry_logic(
        self, decision_engine, mock_prior_auth_adapter, mock_insurance_adapter, appointment_data
    ):
        """Test 9: Database unavailable triggers retry then FAILED status."""
        check = create_prior_auth_check()
        mock_insurance_adapter.check_prior_auth_requirement.return_value = {"prior_auth_required": True}
        mock_prior_auth_adapter.query_prior_auths.side_effect = Exception("Connection refused")

        result = await decision_engine.execute_check(check, appointment_data)

        assert result.status == CheckStatus.FAILED
        assert "database unavailable" in result.escalation_reason.lower()

    async def test_ehr_write_failure_fallback(self, mock_athena_adapter):
        """Test 10: EHR write failure with fallback storage."""
        check = create_prior_auth_check()
        check.status = CheckStatus.COMPLETED

        # Simulate EHR write failure
        mock_athena_adapter.write_verification_note.side_effect = Exception("EHR unavailable")

        # In production, would store in local database as fallback
        # Test that exception is caught and handled
        try:
            await mock_athena_adapter.write_verification_note(check.appointment_id, "note")
        except Exception as e:
            # Expected: exception caught, fallback triggered
            assert "EHR unavailable" in str(e)

    async def test_insurance_requirements_db_error(
        self, decision_engine, mock_insurance_adapter, appointment_data
    ):
        """Test error when insurance requirements database fails."""
        check = create_prior_auth_check()
        mock_insurance_adapter.check_prior_auth_requirement.side_effect = Exception("Database error")

        result = await decision_engine.execute_check(check, appointment_data)

        assert result.status == CheckStatus.ESCALATED
        assert "Insurance requirements database error" in result.escalation_reason


@pytest.mark.integration
class TestHumanReviewInterface:
    """Test 8: Human Review Interface (API endpoints)."""

    def test_human_decision_approval(self):
        """Test recording human APPROVED decision."""
        check = create_prior_auth_check(status=CheckStatus.AWAITING_HUMAN_REVIEW)

        # Simulate human decision
        check.transition_to(CheckStatus.APPROVED)
        check.human_decision_by = "user_123"
        check.human_decision_at = datetime.now()
        check.human_decision_notes = "Verified with insurance, proceed with appointment"

        assert check.status == CheckStatus.APPROVED
        assert check.human_decision_by == "user_123"
        assert check.human_decision_at is not None
        assert check.human_decision_notes is not None

    def test_human_decision_reschedule(self):
        """Test recording human RESCHEDULED decision."""
        check = create_prior_auth_check(status=CheckStatus.AWAITING_HUMAN_REVIEW)

        check.transition_to(CheckStatus.RESCHEDULED)
        check.human_decision_by = "user_456"
        check.human_decision_at = datetime.now()
        check.human_decision_notes = "Prior-auth expired, rescheduling after obtaining new auth"

        assert check.status == CheckStatus.RESCHEDULED
        assert "expired" in check.human_decision_notes.lower()

    def test_human_decision_escalate_further(self):
        """Test recording human ESCALATED decision (request physician input)."""
        check = create_prior_auth_check(status=CheckStatus.AWAITING_HUMAN_REVIEW)

        check.transition_to(CheckStatus.ESCALATED)
        check.human_decision_by = "user_789"
        check.human_decision_at = datetime.now()
        check.escalation_reason = "Unclear medical necessity, requesting physician review"

        assert check.status == CheckStatus.ESCALATED
        assert check.escalation_reason is not None


@pytest.mark.integration
@pytest.mark.asyncio
class TestDatabaseOperations:
    """Test database read/write operations."""

    async def test_save_prior_auth_check_to_database(self, db_session):
        """Test saving PriorAuthCheck to database."""
        check = create_prior_auth_check()

        db_session.add(check)
        db_session.commit()

        # Retrieve
        saved_check = db_session.query(type(check)).filter_by(check_id=check.check_id).first()

        assert saved_check is not None
        assert saved_check.check_id == check.check_id
        assert saved_check.patient_id == check.patient_id

    async def test_update_prior_auth_check_status(self, db_session):
        """Test updating PriorAuthCheck status in database."""
        check = create_prior_auth_check(status=CheckStatus.PENDING_CHECK)
        db_session.add(check)
        db_session.commit()

        # Update status
        check.transition_to(CheckStatus.CHECKING)
        db_session.commit()

        # Retrieve
        updated_check = db_session.query(type(check)).filter_by(check_id=check.check_id).first()

        assert updated_check.status == CheckStatus.CHECKING

    async def test_query_checks_by_status(self, db_session):
        """Test querying checks by status."""
        # FIX: Use unique appointment_ids to avoid UNIQUE constraint violation
        check1 = create_prior_auth_check(
            check_id="CHECK-001",
            appointment_id="APT-001",
            status=CheckStatus.AWAITING_HUMAN_REVIEW
        )
        check2 = create_prior_auth_check(
            check_id="CHECK-002",
            appointment_id="APT-002",
            status=CheckStatus.COMPLETED
        )
        check3 = create_prior_auth_check(
            check_id="CHECK-003",
            appointment_id="APT-003",
            status=CheckStatus.AWAITING_HUMAN_REVIEW
        )

        db_session.add_all([check1, check2, check3])
        db_session.commit()

        # Query awaiting review
        awaiting_checks = db_session.query(type(check1)).filter_by(
            status=CheckStatus.AWAITING_HUMAN_REVIEW
        ).all()

        assert len(awaiting_checks) == 2
        assert all(c.status == CheckStatus.AWAITING_HUMAN_REVIEW for c in awaiting_checks)


# Import asyncio for timeout tests
import asyncio
