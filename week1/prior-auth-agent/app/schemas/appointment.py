"""Pydantic schemas for Appointment."""
from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel
from app.models.appointment import AppointmentStatus


class AppointmentResponse(BaseModel):
    """Response schema for appointment."""

    appointment_id: str
    patient_id: str
    scheduled_date: datetime
    scheduled_time: time
    appointment_type: Optional[str]
    procedure_codes: Optional[List[str]]
    procedure_descriptions: Optional[List[str]]
    insurance_policy_id: str
    appointment_status: AppointmentStatus
    prior_auth_check_id: Optional[str]
    prior_auth_verified: bool
    prior_auth_verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
