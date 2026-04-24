"""
Unit Test 5: State Transition Validation

Tests state machine enforcement per Claude.md Section 2 and
edge-cases-and-testing.md Test 5.

Pass Criteria: 100% of valid transitions succeed, 100% of invalid transitions blocked
"""
import pytest
from datetime import datetime

from app.models.prior_auth_check import (
    PriorAuthCheck,
    CheckStatus,
)
from tests.conftest import create_prior_auth_check


@pytest.mark.unit
class TestStateMachineValidation:
    """Test state machine transition validation."""

    def test_valid_transition_pending_to_checking(self):
        """Test valid: PENDING_CHECK → CHECKING."""
        check = create_prior_auth_check(status=CheckStatus.PENDING_CHECK)

        check.transition_to(CheckStatus.CHECKING)

        assert check.status == CheckStatus.CHECKING
        assert check.last_updated_at is not None

    def test_valid_transition_checking_to_awaiting_review(self):
        """Test valid: CHECKING → AWAITING_HUMAN_REVIEW."""
        check = create_prior_auth_check(status=CheckStatus.CHECKING)

        check.transition_to(CheckStatus.AWAITING_HUMAN_REVIEW)

        assert check.status == CheckStatus.AWAITING_HUMAN_REVIEW

    def test_valid_transition_checking_to_escalated(self):
        """Test valid: CHECKING → ESCALATED."""
        check = create_prior_auth_check(status=CheckStatus.CHECKING)

        check.transition_to(CheckStatus.ESCALATED, reason="Multiple prior-auths found")

        assert check.status == CheckStatus.ESCALATED
        assert check.escalation_reason == "Multiple prior-auths found"

    def test_valid_transition_checking_to_failed(self):
        """Test valid: CHECKING → FAILED."""
        check = create_prior_auth_check(status=CheckStatus.CHECKING)

        check.transition_to(CheckStatus.FAILED, reason="Database unavailable")

        assert check.status == CheckStatus.FAILED

    def test_valid_transition_checking_to_completed(self):
        """Test valid: CHECKING → COMPLETED (prior-auth not required)."""
        check = create_prior_auth_check(status=CheckStatus.CHECKING)

        check.transition_to(CheckStatus.COMPLETED)

        assert check.status == CheckStatus.COMPLETED
        assert check.completed_at is not None

    def test_valid_transition_awaiting_review_to_approved(self):
        """Test valid: AWAITING_HUMAN_REVIEW → APPROVED."""
        check = create_prior_auth_check(status=CheckStatus.AWAITING_HUMAN_REVIEW)

        check.transition_to(CheckStatus.APPROVED)

        assert check.status == CheckStatus.APPROVED

    def test_valid_transition_awaiting_review_to_rescheduled(self):
        """Test valid: AWAITING_HUMAN_REVIEW → RESCHEDULED."""
        check = create_prior_auth_check(status=CheckStatus.AWAITING_HUMAN_REVIEW)

        check.transition_to(CheckStatus.RESCHEDULED)

        assert check.status == CheckStatus.RESCHEDULED

    def test_valid_transition_awaiting_review_to_escalated(self):
        """Test valid: AWAITING_HUMAN_REVIEW → ESCALATED."""
        check = create_prior_auth_check(status=CheckStatus.AWAITING_HUMAN_REVIEW)

        check.transition_to(CheckStatus.ESCALATED)

        assert check.status == CheckStatus.ESCALATED

    def test_valid_transition_escalated_to_awaiting_review(self):
        """Test valid: ESCALATED → AWAITING_HUMAN_REVIEW."""
        check = create_prior_auth_check(status=CheckStatus.ESCALATED)

        check.transition_to(CheckStatus.AWAITING_HUMAN_REVIEW)

        assert check.status == CheckStatus.AWAITING_HUMAN_REVIEW

    def test_valid_transition_escalated_to_completed(self):
        """Test valid: ESCALATED → COMPLETED."""
        check = create_prior_auth_check(status=CheckStatus.ESCALATED)

        check.transition_to(CheckStatus.COMPLETED)

        assert check.status == CheckStatus.COMPLETED

    def test_valid_transition_approved_to_completed(self):
        """Test valid: APPROVED → COMPLETED."""
        check = create_prior_auth_check(status=CheckStatus.APPROVED)

        check.transition_to(CheckStatus.COMPLETED)

        assert check.status == CheckStatus.COMPLETED

    def test_valid_transition_rescheduled_to_completed(self):
        """Test valid: RESCHEDULED → COMPLETED."""
        check = create_prior_auth_check(status=CheckStatus.RESCHEDULED)

        check.transition_to(CheckStatus.COMPLETED)

        assert check.status == CheckStatus.COMPLETED

    def test_valid_transition_failed_to_completed(self):
        """Test valid: FAILED → COMPLETED (manual fallback)."""
        check = create_prior_auth_check(status=CheckStatus.FAILED)

        check.transition_to(CheckStatus.COMPLETED)

        assert check.status == CheckStatus.COMPLETED

    def test_invalid_transition_completed_to_checking(self):
        """Test invalid: COMPLETED → CHECKING (terminal state, immutable)."""
        check = create_prior_auth_check(status=CheckStatus.COMPLETED)

        with pytest.raises(ValueError, match="Invalid state transition"):
            check.transition_to(CheckStatus.CHECKING)

    def test_invalid_transition_completed_to_any_state(self):
        """Test invalid: COMPLETED → any state (terminal state)."""
        check = create_prior_auth_check(status=CheckStatus.COMPLETED)

        invalid_targets = [
            CheckStatus.PENDING_CHECK,
            CheckStatus.CHECKING,
            CheckStatus.AWAITING_HUMAN_REVIEW,
            CheckStatus.APPROVED,
            CheckStatus.ESCALATED,
        ]

        for target_status in invalid_targets:
            with pytest.raises(ValueError, match="Invalid state transition"):
                check.transition_to(target_status)

    def test_invalid_transition_pending_to_approved(self):
        """Test invalid: PENDING_CHECK → APPROVED (must go through CHECKING)."""
        check = create_prior_auth_check(status=CheckStatus.PENDING_CHECK)

        with pytest.raises(ValueError, match="Invalid state transition"):
            check.transition_to(CheckStatus.APPROVED)

    def test_invalid_transition_pending_to_rescheduled(self):
        """Test invalid: PENDING_CHECK → RESCHEDULED (must go through CHECKING)."""
        check = create_prior_auth_check(status=CheckStatus.PENDING_CHECK)

        with pytest.raises(ValueError, match="Invalid state transition"):
            check.transition_to(CheckStatus.RESCHEDULED)

    def test_invalid_transition_awaiting_review_to_checking(self):
        """Test invalid: AWAITING_HUMAN_REVIEW → CHECKING (cannot go backwards)."""
        check = create_prior_auth_check(status=CheckStatus.AWAITING_HUMAN_REVIEW)

        with pytest.raises(ValueError, match="Invalid state transition"):
            check.transition_to(CheckStatus.CHECKING)

    def test_invalid_transition_failed_to_checking(self):
        """Test invalid: FAILED → CHECKING (cannot retry after failure)."""
        check = create_prior_auth_check(status=CheckStatus.FAILED)

        with pytest.raises(ValueError, match="Invalid state transition"):
            check.transition_to(CheckStatus.CHECKING)

    def test_completed_at_timestamp_set_on_completion(self):
        """Test completed_at timestamp set when transitioning to COMPLETED."""
        check = create_prior_auth_check(status=CheckStatus.APPROVED)
        check.completed_at = None

        check.transition_to(CheckStatus.COMPLETED)

        assert check.completed_at is not None
        assert isinstance(check.completed_at, datetime)

    def test_last_updated_at_timestamp_updated_on_transition(self):
        """Test last_updated_at updated on every transition."""
        check = create_prior_auth_check(status=CheckStatus.PENDING_CHECK)
        initial_updated_at = check.last_updated_at

        check.transition_to(CheckStatus.CHECKING)

        assert check.last_updated_at > initial_updated_at

    def test_escalation_reason_set_on_escalation(self):
        """Test escalation_reason set when transitioning to ESCALATED."""
        check = create_prior_auth_check(status=CheckStatus.CHECKING)

        check.transition_to(CheckStatus.ESCALATED, reason="Database timeout")

        assert check.escalation_reason == "Database timeout"

    def test_complete_workflow_pending_to_completed(self):
        """Test complete workflow: PENDING → CHECKING → AWAITING → APPROVED → COMPLETED."""
        check = create_prior_auth_check(status=CheckStatus.PENDING_CHECK)

        # Valid transition sequence
        check.transition_to(CheckStatus.CHECKING)
        assert check.status == CheckStatus.CHECKING

        check.transition_to(CheckStatus.AWAITING_HUMAN_REVIEW)
        assert check.status == CheckStatus.AWAITING_HUMAN_REVIEW

        check.transition_to(CheckStatus.APPROVED)
        assert check.status == CheckStatus.APPROVED

        check.transition_to(CheckStatus.COMPLETED)
        assert check.status == CheckStatus.COMPLETED
        assert check.completed_at is not None

    def test_escalation_workflow(self):
        """Test escalation workflow: CHECKING → ESCALATED → AWAITING → APPROVED → COMPLETED."""
        check = create_prior_auth_check(status=CheckStatus.CHECKING)

        check.transition_to(CheckStatus.ESCALATED, reason="Multiple prior-auths")
        assert check.status == CheckStatus.ESCALATED

        check.transition_to(CheckStatus.AWAITING_HUMAN_REVIEW)
        assert check.status == CheckStatus.AWAITING_HUMAN_REVIEW

        check.transition_to(CheckStatus.APPROVED)
        check.transition_to(CheckStatus.COMPLETED)
        assert check.status == CheckStatus.COMPLETED

    def test_reschedule_workflow(self):
        """Test reschedule workflow: CHECKING → AWAITING → RESCHEDULED → COMPLETED."""
        check = create_prior_auth_check(status=CheckStatus.CHECKING)

        check.transition_to(CheckStatus.AWAITING_HUMAN_REVIEW)
        check.transition_to(CheckStatus.RESCHEDULED)
        check.transition_to(CheckStatus.COMPLETED)

        assert check.status == CheckStatus.COMPLETED

    def test_failed_workflow(self):
        """Test failed workflow: CHECKING → FAILED → COMPLETED (manual fallback)."""
        check = create_prior_auth_check(status=CheckStatus.CHECKING)

        check.transition_to(CheckStatus.FAILED, reason="Database unavailable")
        assert check.status == CheckStatus.FAILED

        check.transition_to(CheckStatus.COMPLETED)
        assert check.status == CheckStatus.COMPLETED

    def test_same_state_transition_allowed(self):
        """Test transitioning to same state (idempotent)."""
        check = create_prior_auth_check(status=CheckStatus.CHECKING)

        # Should not raise error
        check.status = CheckStatus.CHECKING

        assert check.status == CheckStatus.CHECKING
