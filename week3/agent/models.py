from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ShiftRequestStatus(str, Enum):
    QUEUED = "QUEUED"
    PARSING = "PARSING"
    PARSED = "PARSED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    PARSE_FAILED = "PARSE_FAILED"
    CANCELLED = "CANCELLED"


class SourceType(str, Enum):
    EMAIL = "EMAIL"
    PORTAL_FORM = "PORTAL_FORM"
    PHONE_TRANSCRIPTION = "PHONE_TRANSCRIPTION"


class ParseMethod(str, Enum):
    LLM_AUTO = "LLM_AUTO"
    HUMAN_CORRECTED = "HUMAN_CORRECTED"


class HITLFailureReason(str, Enum):
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    LLM_UNAVAILABLE = "LLM_UNAVAILABLE"
    INVALID_JSON = "INVALID_JSON"
    DATETIME_IN_PAST = "DATETIME_IN_PAST"
    UNKNOWN_SPECIALTY = "UNKNOWN_SPECIALTY"
    AMBIGUOUS_LOCATION = "AMBIGUOUS_LOCATION"


class HITLStatus(str, Enum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ShiftRequest(BaseModel):
    sys_id: str
    u_shift_request_id: str
    u_source_type: SourceType
    u_raw_text: str
    u_hospital_id: str
    u_status: ShiftRequestStatus = ShiftRequestStatus.QUEUED
    u_failure_reason: Optional[str] = None
    u_received_at: datetime
    u_parsed_at: Optional[datetime] = None
    u_reviewed_by: Optional[str] = None


class ParsedShiftRequirement(BaseModel):
    u_shift_request_id: str
    u_specialty_code: str
    u_datetime_start: str
    u_datetime_end: str
    u_location_id: str
    u_credentials: list[str] = Field(default_factory=list)
    u_confidence_score: float = Field(ge=0.0, le=1.0)
    u_parse_method: ParseMethod
    u_parsed_by: str


class HITLQueueEntry(BaseModel):
    u_shift_request_id: str
    u_raw_text: str
    u_partial_parse: Optional[dict] = None
    u_failure_reason: HITLFailureReason
    u_confidence_score: Optional[float] = None
    u_status: HITLStatus = HITLStatus.PENDING
    u_assigned_to: Optional[str] = None


class LLMExtractionResult(BaseModel):
    specialty_code: str
    specialty_confidence: float = Field(ge=0.0, le=1.0)
    datetime_start: Optional[str] = None
    datetime_start_confidence: float = Field(ge=0.0, le=1.0)
    datetime_end: Optional[str] = None
    datetime_end_confidence: float = Field(ge=0.0, le=1.0)
    location_id: str
    location_confidence: float = Field(ge=0.0, le=1.0)
    credentials: list[str] = Field(default_factory=list)
    credential_confidence: float = Field(ge=0.0, le=1.0)


class DeadLetterRecord(BaseModel):
    record_id: str
    shift_request_id: str
    operation: str
    payload: dict
    retry_count: int = 0
    created_at: datetime
    last_attempted_at: Optional[datetime] = None
