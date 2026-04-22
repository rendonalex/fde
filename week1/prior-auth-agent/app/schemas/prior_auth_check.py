"""Pydantic schemas for PriorAuthCheck API."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.prior_auth_check import (
    CheckStatus,
    PriorAuthStatus,
    AIRecommendation,
    ConfidenceScore,
    HumanDecision,
)


class PriorAuthCheckCreate(BaseModel):
    """Request schema for creating a new prior-auth check."""

    appointment_id: str = Field(..., description="Unique appointment ID from EHR")

    class Config:
        json_schema_extra = {"example": {"appointment_id": "APT-2024-001"}}


class PriorAuthCheckResponse(BaseModel):
    """Response schema for prior-auth check."""

    check_id: str
    patient_id: str
    appointment_id: str
    scheduled_date: datetime
    procedure_code: str
    procedure_description: Optional[str]
    insurance_policy_id: str

    # Status
    status: CheckStatus
    prior_auth_required: Optional[bool]
    prior_auth_status: Optional[PriorAuthStatus]

    # AI analysis
    ai_recommendation: Optional[AIRecommendation]
    confidence_score: Optional[ConfidenceScore]
    confidence_rationale: Optional[str]

    # Human decision
    human_decision: Optional[HumanDecision]
    human_decision_by: Optional[str]
    human_decision_at: Optional[datetime]
    human_decision_notes: Optional[str]

    # Audit
    created_at: datetime
    completed_at: Optional[datetime]
    last_updated_at: datetime
    escalation_reason: Optional[str]

    # Related entities
    prior_auth_records_found: Optional[List[str]] = Field(default_factory=list)
    matched_prior_auth_id: Optional[str]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_lists(cls, db_obj):
        """Convert ORM object to response with proper list handling."""
        data = {
            "check_id": db_obj.check_id,
            "patient_id": db_obj.patient_id,
            "appointment_id": db_obj.appointment_id,
            "scheduled_date": db_obj.scheduled_date,
            "procedure_code": db_obj.procedure_code,
            "procedure_description": db_obj.procedure_description,
            "insurance_policy_id": db_obj.insurance_policy_id,
            "status": db_obj.status,
            "prior_auth_required": db_obj.prior_auth_required,
            "prior_auth_status": db_obj.prior_auth_status,
            "ai_recommendation": db_obj.ai_recommendation,
            "confidence_score": db_obj.confidence_score,
            "confidence_rationale": db_obj.confidence_rationale,
            "human_decision": db_obj.human_decision,
            "human_decision_by": db_obj.human_decision_by,
            "human_decision_at": db_obj.human_decision_at,
            "human_decision_notes": db_obj.human_decision_notes,
            "created_at": db_obj.created_at,
            "completed_at": db_obj.completed_at,
            "last_updated_at": db_obj.last_updated_at,
            "escalation_reason": db_obj.escalation_reason,
            "prior_auth_records_found": db_obj.get_prior_auth_records_list(),
            "matched_prior_auth_id": db_obj.matched_prior_auth_id,
        }
        return cls(**data)


class PriorAuthCheckUpdate(BaseModel):
    """Request schema for updating a prior-auth check (partial update)."""

    status: Optional[CheckStatus] = None
    prior_auth_status: Optional[PriorAuthStatus] = None
    ai_recommendation: Optional[AIRecommendation] = None
    confidence_score: Optional[ConfidenceScore] = None
    escalation_reason: Optional[str] = None


class HumanDecisionRequest(BaseModel):
    """Request schema for recording human decision."""

    decision: HumanDecision = Field(..., description="Human decision on AI recommendation")
    decision_by: str = Field(..., description="User ID of staff member making decision")
    notes: Optional[str] = Field(None, description="Optional rationale for decision")

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "APPROVED",
                "decision_by": "staff-001",
                "notes": "Prior-auth verified, patient can proceed",
            }
        }
