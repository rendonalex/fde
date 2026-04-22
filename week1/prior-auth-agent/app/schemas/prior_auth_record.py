"""Pydantic schemas for PriorAuthRecord."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.prior_auth_record import ApprovalStatus


class PriorAuthRecordResponse(BaseModel):
    """Response schema for prior-auth record."""

    prior_auth_id: str
    patient_id: str
    insurance_policy_id: str
    approval_number: str
    approval_date: datetime
    expiration_date: datetime
    approval_status: ApprovalStatus
    approved_cpt_codes: Optional[List[str]]
    approved_service_description: Optional[str]
    service_category: Optional[str]
    approved_units: Optional[int]
    units_used: int
    source_system: str
    last_verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
