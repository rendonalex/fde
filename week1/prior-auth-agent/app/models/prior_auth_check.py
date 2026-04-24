"""PriorAuthCheck entity with state machine [per Claude.md Section 2]."""
import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, DateTime, Boolean, Enum, Text, ARRAY
from sqlalchemy.orm import validates
from app.database import Base


class CheckStatus(str, enum.Enum):
    """State machine states for PriorAuthCheck [per Claude.md Section 2]."""

    PENDING_CHECK = "PENDING_CHECK"
    CHECKING = "CHECKING"
    AWAITING_HUMAN_REVIEW = "AWAITING_HUMAN_REVIEW"
    APPROVED = "APPROVED"
    RESCHEDULED = "RESCHEDULED"
    ESCALATED = "ESCALATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PriorAuthStatus(str, enum.Enum):
    """Prior-auth status outcomes."""

    VALID = "VALID"
    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"
    MISSING = "MISSING"
    AMBIGUOUS = "AMBIGUOUS"


class AIRecommendation(str, enum.Enum):
    """AI recommendation types."""

    PROCEED = "PROCEED"
    RESCHEDULE = "RESCHEDULE"
    ESCALATE = "ESCALATE"


class ConfidenceScore(str, enum.Enum):
    """Confidence score levels [per Claude.md Section 5, Step 5]."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class HumanDecision(str, enum.Enum):
    """Human decision types."""

    APPROVED = "APPROVED"
    RESCHEDULED = "RESCHEDULED"
    ESCALATED = "ESCALATED"
    OVERRIDDEN = "OVERRIDDEN"


class PriorAuthCheck(Base):
    """
    Prior-authorization verification workflow entity.

    Represents a single prior-authorization check for a scheduled appointment.
    Implements state machine transitions per Claude.md Section 2.
    """

    __tablename__ = "prior_auth_checks"

    # Primary identification
    check_id = Column(String(255), primary_key=True)
    patient_id = Column(String(255), nullable=False, index=True)
    appointment_id = Column(String(255), nullable=False, unique=True, index=True)
    scheduled_date = Column(DateTime, nullable=False)
    procedure_code = Column(String(10), nullable=False)
    procedure_description = Column(String(500))
    insurance_policy_id = Column(String(255), nullable=False, index=True)

    # Status tracking
    status = Column(Enum(CheckStatus), nullable=False, default=CheckStatus.PENDING_CHECK, index=True)
    prior_auth_required = Column(Boolean, nullable=True)
    prior_auth_status = Column(Enum(PriorAuthStatus), nullable=True)

    # AI analysis results
    ai_recommendation = Column(Enum(AIRecommendation), nullable=True)
    confidence_score = Column(Enum(ConfidenceScore), nullable=True)
    confidence_rationale = Column(Text, nullable=True)

    # Human decision
    human_decision = Column(Enum(HumanDecision), nullable=True)
    human_decision_by = Column(String(255), nullable=True)
    human_decision_at = Column(DateTime, nullable=True)
    human_decision_notes = Column(Text, nullable=True)

    # Audit trail
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    last_updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    escalation_reason = Column(Text, nullable=True)

    # Related entities (stored as comma-separated IDs for simplicity in this implementation)
    prior_auth_records_found = Column(Text, nullable=True)  # Comma-separated IDs
    matched_prior_auth_id = Column(String(255), nullable=True)

    # Valid state transitions [per Claude.md Section 2]
    VALID_TRANSITIONS = {
        CheckStatus.PENDING_CHECK: [CheckStatus.CHECKING],
        CheckStatus.CHECKING: [CheckStatus.AWAITING_HUMAN_REVIEW, CheckStatus.ESCALATED, CheckStatus.FAILED, CheckStatus.COMPLETED],
        CheckStatus.AWAITING_HUMAN_REVIEW: [CheckStatus.APPROVED, CheckStatus.RESCHEDULED, CheckStatus.ESCALATED],
        CheckStatus.ESCALATED: [CheckStatus.AWAITING_HUMAN_REVIEW, CheckStatus.COMPLETED],
        CheckStatus.APPROVED: [CheckStatus.COMPLETED],
        CheckStatus.RESCHEDULED: [CheckStatus.COMPLETED],
        CheckStatus.FAILED: [CheckStatus.COMPLETED],
        CheckStatus.COMPLETED: [],  # Terminal state
    }

    @validates("status")
    def validate_status_transition(self, key, new_status):
        """
        Validate state transitions per Claude.md Section 2.

        Raises ValueError if transition is invalid.
        """
        # FIX: Check if we have a current status (not initial creation)
        # Use getattr to safely get current status, works for both persisted and transient objects
        current_status = getattr(self, 'status', None)

        if current_status and new_status != current_status:
            valid_next_states = self.VALID_TRANSITIONS.get(current_status, [])
            if new_status not in valid_next_states:
                raise ValueError(
                    f"Invalid state transition from {current_status} to {new_status}. "
                    f"Valid transitions: {valid_next_states}"
                )
        return new_status

    def transition_to(self, new_status: CheckStatus, reason: Optional[str] = None) -> None:
        """
        Safely transition to a new status with validation.

        Args:
            new_status: Target status
            reason: Optional reason for the transition

        Raises:
            ValueError: If transition is invalid
        """
        self.status = new_status
        self.last_updated_at = datetime.utcnow()

        # Set completion timestamp for terminal states
        if new_status == CheckStatus.COMPLETED and not self.completed_at:
            self.completed_at = datetime.utcnow()

        # Track escalation reason for FAILED, ESCALATED, and AWAITING_HUMAN_REVIEW
        # FIX Phase 2: AWAITING_HUMAN_REVIEW can have escalation reasons (e.g., missing prior-auth)
        # FIX Phase 5: FAILED state also needs escalation reason (e.g., database unavailable)
        if new_status in [CheckStatus.FAILED, CheckStatus.ESCALATED, CheckStatus.AWAITING_HUMAN_REVIEW] and reason:
            self.escalation_reason = reason

    def get_prior_auth_records_list(self) -> List[str]:
        """Get list of prior-auth record IDs found."""
        if not self.prior_auth_records_found:
            return []
        return [pid.strip() for pid in self.prior_auth_records_found.split(",") if pid.strip()]

    def set_prior_auth_records_list(self, record_ids: List[str]) -> None:
        """Set list of prior-auth record IDs found."""
        self.prior_auth_records_found = ",".join(record_ids) if record_ids else None

    def __repr__(self):
        return (
            f"<PriorAuthCheck(check_id='{self.check_id}', "
            f"status={self.status}, "
            f"confidence={self.confidence_score})>"
        )
