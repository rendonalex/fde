"""Entity data models for ADR-1."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from .enums import (
    ClaimType,
    EventType,
    ExceptionType,
    ExtractionStatus,
    IntakeChannel,
    Outcome,
    Priority,
    RequiredAction,
    ResolutionStatus,
    RoutingDecision,
    RoutingMode,
    SLAQueue,
)


class NormalizedClaimRecord(BaseModel):
    """
    Canonical claim record shared across all agents.
    ADR-1 creates it; downstream agents read/update via CMS.
    Corresponds to spec Section 9.1.
    """

    # Primary key (CMS-generated on creation)
    claim_id: Optional[UUID] = None

    # ===== Intake Fields (written by ADR-1; immutable after creation) =====

    source_claim_ref: str = Field(..., max_length=50)
    member_id: str = Field(..., max_length=20)
    member_dob: Optional[str] = None  # YYYY-MM-DD, optional - resolved by ADR-2
    member_name_last: str = Field(..., max_length=60)
    member_name_first: str = Field(..., max_length=60)
    rendering_provider_npi: Optional[str] = Field(None, pattern=r"^\d{10}$")
    billing_provider_npi: Optional[str] = Field(None, pattern=r"^\d{10}$")
    billing_provider_tax_id: Optional[str] = Field(None, pattern=r"^\d{9}$")
    date_of_service_start: str  # YYYY-MM-DD
    date_of_service_end: str  # YYYY-MM-DD
    place_of_service_code: Optional[str] = Field(None, pattern=r"^\d{2}$")
    claim_type: ClaimType
    icd10_codes: list[str] = Field(..., min_length=1, max_length=12)
    cpt_codes: list[str] = Field(..., min_length=1, max_length=50)
    revenue_codes: list[str] = Field(default_factory=list)
    drg_code: Optional[str] = Field(None, pattern=r"^\d{3}$")
    billed_amount: Optional[float] = Field(None, gt=0)
    currency: str = Field(default="USD")
    payer_id: Optional[str] = Field(None, max_length=20)
    payer_name: str = Field(..., max_length=100)
    plan_id: Optional[str] = Field(None, max_length=30)
    prior_auth_required: bool
    prior_auth_number: Optional[str] = Field(None, max_length=30)
    intake_channel: IntakeChannel
    extraction_status: ExtractionStatus
    field_confidence: Optional[dict[str, float]] = None
    low_confidence_fields: list[str] = Field(default_factory=list)
    sla_queue: SLAQueue
    sla_deadline: datetime
    queue_assigned_at: Optional[datetime] = None
    intake_agent_version: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str

    # ===== Routing Fields (written by ADR-4; null until triage completes) =====

    routing_decision: RoutingDecision = RoutingDecision.PENDING_TRIAGE
    routing_confidence: Optional[float] = None
    routing_confidence_fallback: Optional[bool] = None
    clinical_indicators_detected: Optional[list[str]] = None
    criteria_provisions_matched: Optional[list[str]] = None
    routing_reasoning_trace: Optional[str] = None
    routing_agent_version: Optional[str] = None
    routing_decided_at: Optional[datetime] = None
    routing_mode: Optional[RoutingMode] = None

    # Validator removed - ADR-4 validates clinical correctness of prior auth

    @field_validator("date_of_service_end")
    @classmethod
    def validate_dos_end(cls, v, info):
        """Ensure date_of_service_end >= date_of_service_start."""
        start = info.data.get("date_of_service_start")
        if start and v < start:
            raise ValueError("date_of_service_end must be >= date_of_service_start")
        return v

    model_config = {"use_enum_values": True}


class LowConfidenceField(BaseModel):
    """Details of a field with low extraction confidence."""

    field: str
    extracted_value: Optional[str]
    confidence: float


class ExceptionQueueEntry(BaseModel):
    """
    Entry in the human exception queue for unresolved extractions.
    Corresponds to spec Section 9.2.
    """

    exception_id: UUID = Field(default_factory=uuid4)
    claim_id: UUID
    exception_type: ExceptionType
    low_confidence_fields: Optional[list[LowConfidenceField]] = None
    required_action: RequiredAction
    priority: Priority
    resolution_status: ResolutionStatus = ResolutionStatus.OPEN
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    source_agent: str = "ADR-1"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sla_resolution_by: datetime

    @field_validator("low_confidence_fields")
    @classmethod
    def validate_low_confidence_fields(cls, v, info):
        """Ensure low_confidence_fields present when exception_type=LOW_CONFIDENCE_EXTRACTION."""
        if info.data.get("exception_type") == ExceptionType.LOW_CONFIDENCE_EXTRACTION and not v:
            raise ValueError(
                "low_confidence_fields required for LOW_CONFIDENCE_EXTRACTION exception"
            )
        return v

    model_config = {"use_enum_values": True}


class AuditLogEntry(BaseModel):
    """
    Append-only audit log entry for claim processing events.
    Corresponds to spec Section 9.3.
    """

    audit_id: UUID = Field(default_factory=uuid4)
    claim_id: UUID
    agent_id: str
    agent_version: str
    event_type: EventType
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)
    extraction_status: Optional[ExtractionStatus] = None
    field_confidence: Optional[dict[str, float]] = None
    operator_id: Optional[str] = None
    outcome: Outcome

    model_config = {"use_enum_values": True}
