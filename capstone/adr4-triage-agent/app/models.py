"""
Data models for ADR-4 Clinical Content Triage Agent.
Per specs/06b-capability-spec-triage.md Section 9 (Entity Data Models).
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, UUID4
from uuid import uuid4


class ExtractionStatus(str, Enum):
    """Claim extraction status from ADR-1."""
    AUTO_COMPLETE = "AUTO_COMPLETE"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"
    PENDING_DUPLICATE = "PENDING_DUPLICATE"
    EXCEPTION_NOTE = "EXCEPTION_NOTE"


class RoutingDecision(str, Enum):
    """Routing path classification."""
    FAST_PATH = "FAST_PATH"
    CLINICAL_PATH = "CLINICAL_PATH"
    PENDING_TRIAGE = "PENDING_TRIAGE"


class RoutingMode(str, Enum):
    """Agent operating mode."""
    SHADOW = "SHADOW"
    LIVE = "LIVE"


class AgreementStatus(str, Enum):
    """Agent-processor agreement status."""
    AGREE = "AGREE"
    DISAGREE = "DISAGREE"


class ClinicalCategory(str, Enum):
    """Clinical content category."""
    DIAGNOSTIC_IMAGING = "DIAGNOSTIC_IMAGING"
    SPECIALIST_AUTHORIZATION = "SPECIALIST_AUTHORIZATION"
    MEDICAL_NECESSITY = "MEDICAL_NECESSITY"
    PROCEDURE_COMPLEXITY = "PROCEDURE_COMPLEXITY"
    PRIOR_AUTH_REQUIRED = "PRIOR_AUTH_REQUIRED"
    OTHER_CLINICAL = "OTHER_CLINICAL"


# ============================================================================
# INPUT: Normalized Claim Record (from ADR-1)
# ============================================================================

class NormalizedClaimRecord(BaseModel):
    """
    Normalized claim record input from ADR-1.
    Per specs/06a-capability-spec-intake.md Section 9.1.

    ADR-4 only reads the clinical fields necessary for classification.
    """
    claim_id: str = Field(..., description="UUID claim identifier")
    source_claim_ref: str = Field(..., description="Original claim reference")
    intake_channel: str = Field(..., description="Source channel (EDI_837P, CMS1500_PDF, etc.)")
    extraction_status: ExtractionStatus = Field(..., description="ADR-1 extraction status")
    member_id: str = Field(..., description="Member identifier")
    icd10_codes: List[str] = Field(default_factory=list, description="ICD-10 diagnosis codes")
    cpt_codes: List[str] = Field(default_factory=list, description="CPT procedure codes")
    prior_auth_required: bool = Field(default=False, description="Prior authorization flag")
    prior_auth_number: Optional[str] = Field(None, description="Authorization number if available")
    payer_id: Optional[str] = Field(None, description="Payer identifier")
    place_of_service: Optional[str] = Field(None, description="Place of service code")
    billed_amount: Optional[float] = Field(None, description="Total billed amount")

    class Config:
        json_schema_extra = {
            "example": {
                "claim_id": "a3f1e2d4-0c8b-4e6a-9f7d-1b2c3d4e5f60",
                "source_claim_ref": "PDF-2026-0441",
                "intake_channel": "CMS1500_PDF",
                "extraction_status": "AUTO_COMPLETE",
                "member_id": "M-4421908",
                "icd10_codes": ["Z00.00"],
                "cpt_codes": ["99213"],
                "prior_auth_required": False,
                "prior_auth_number": None,
                "payer_id": "BX-0042",
                "place_of_service": "11",
                "billed_amount": 185.00
            }
        }


# ============================================================================
# OUTPUT: Routing Decision (from Agent)
# ============================================================================

class RoutingDecisionOutput(BaseModel):
    """
    Agent classification output.
    Per specs/06b-capability-spec-triage.md Section 6.3 (System Prompt Template).
    """
    claim_id: str = Field(..., description="Claim UUID (copied from input)")
    source_claim_ref: str = Field(..., description="Original claim reference (copied from input)")
    routing_decision: RoutingDecision = Field(..., description="FAST_PATH or CLINICAL_PATH")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")
    confidence_fallback: bool = Field(..., description="True if confidence < threshold override applied")
    clinical_indicators_detected: List[str] = Field(..., description="Clinical indicators found in claim")
    criteria_provisions_matched: List[str] = Field(..., description="Codebook provision IDs matched")
    reasoning_trace: str = Field(..., description="Chain-of-thought reasoning (Steps 1-5)")
    routing_mode: RoutingMode = Field(..., description="SHADOW or LIVE")

    class Config:
        json_schema_extra = {
            "example": {
                "claim_id": "a3f1e2d4-0c8b-4e6a-9f7d-1b2c3d4e5f60",
                "source_claim_ref": "PDF-2026-0441",
                "routing_decision": "FAST_PATH",
                "confidence": 0.96,
                "confidence_fallback": False,
                "clinical_indicators_detected": ["ICD-10: Z00.00", "CPT: 99213"],
                "criteria_provisions_matched": [],
                "reasoning_trace": "Step 1 — ICD-10 scan: Z00.00 (routine adult health examination)...",
                "routing_mode": "SHADOW"
            }
        }


# ============================================================================
# SHADOW LOG: Routing Decision Record (database entity)
# ============================================================================

class RoutingDecisionRecord(BaseModel):
    """
    Shadow evaluation log entry.
    Per specs/06b-capability-spec-triage.md Section 9.1.
    """
    shadow_log_id: str = Field(default_factory=lambda: str(uuid4()), description="Primary key")
    claim_id: str = Field(..., description="Foreign key to NormalizedClaimRecord")
    agent_routing_decision: RoutingDecision = Field(..., description="Agent classification")
    agent_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    agent_confidence_fallback: bool = Field(..., description="Fallback rule applied")
    clinical_indicators_detected: List[str] = Field(..., description="Indicators found")
    criteria_provisions_matched: List[str] = Field(..., description="Provisions matched")
    reasoning_trace: str = Field(..., description="Chain-of-thought output")
    agent_version: str = Field(default="1.0.0", description="Agent semver")
    logged_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp")

    # Processor decision (updated after processor routes claim)
    processor_routing_decision: Optional[RoutingDecision] = Field(None, description="Processor classification")
    processor_user_id: Optional[str] = Field(None, description="Processor user ID")
    processor_decided_at: Optional[datetime] = Field(None, description="Processor decision timestamp")
    agreement: Optional[AgreementStatus] = Field(None, description="AGREE or DISAGREE")

    # Ground truth (Dr. Webb adjudication)
    ground_truth_routing: Optional[RoutingDecision] = Field(None, description="Definitive label from Dr. Webb")
    adjudication_id: Optional[str] = Field(None, description="Foreign key to AdjudicationQueueEntry")

    class Config:
        json_schema_extra = {
            "example": {
                "shadow_log_id": "d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f80",
                "claim_id": "a3f1e2d4-0c8b-4e6a-9f7d-1b2c3d4e5f60",
                "agent_routing_decision": "FAST_PATH",
                "agent_confidence": 0.96,
                "agent_confidence_fallback": False,
                "clinical_indicators_detected": ["ICD-10: Z00.00", "CPT: 99213"],
                "criteria_provisions_matched": [],
                "reasoning_trace": "Step 1 — ICD-10 scan: Z00.00...",
                "agent_version": "1.0.0",
                "logged_at": "2026-05-27T10:00:00Z",
                "processor_routing_decision": "FAST_PATH",
                "processor_user_id": "processor_001",
                "processor_decided_at": "2026-05-27T10:05:00Z",
                "agreement": "AGREE",
                "ground_truth_routing": None,
                "adjudication_id": None
            }
        }


class ProcessorDecisionUpdate(BaseModel):
    """Request to update shadow log entry with processor decision."""
    processor_routing_decision: RoutingDecision
    processor_user_id: str
    processor_decided_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# ============================================================================
# CODEBOOK: Criteria Codebook Entry
# ============================================================================

class CriteriaCodebookEntry(BaseModel):
    """
    Clinical criteria codebook provision.
    Per specs/06b-capability-spec-triage.md Section 9.2.
    """
    provision_id: str = Field(..., description="Primary key (CC-NNN)")
    provision_name: str = Field(..., description="Human-readable name")
    clinical_category: ClinicalCategory = Field(..., description="Clinical content category")
    trigger_icd10_patterns: List[str] = Field(default_factory=list, description="ICD-10 prefixes/codes")
    trigger_cpt_patterns: List[str] = Field(default_factory=list, description="CPT prefixes/codes")
    trigger_prior_auth_required: bool = Field(default=False, description="Prior auth alone triggers")
    trigger_free_text_keywords: List[str] = Field(default_factory=list, description="Free-text keywords")
    requires_prior_auth: bool = Field(default=False, description="This provision requires prior authorization")
    routing_outcome: RoutingDecision = Field(default=RoutingDecision.CLINICAL_PATH)
    description: str = Field(..., description="Clinical rationale")
    effective_date: str = Field(..., description="YYYY-MM-DD")
    retired_date: Optional[str] = Field(None, description="YYYY-MM-DD or null")
    approved_by: str = Field(..., description="Dr. Webb user ID")
    approved_at: str = Field(..., description="ISO 8601 UTC")

    class Config:
        json_schema_extra = {
            "example": {
                "provision_id": "CC-001",
                "provision_name": "Prior Authorization Required",
                "clinical_category": "PRIOR_AUTH_REQUIRED",
                "trigger_icd10_patterns": [],
                "trigger_cpt_patterns": [],
                "trigger_prior_auth_required": True,
                "trigger_free_text_keywords": ["prior auth", "authorization required"],
                "routing_outcome": "CLINICAL_PATH",
                "description": "Any claim where prior authorization is required...",
                "effective_date": "2026-04-22",
                "retired_date": None,
                "approved_by": "dr.webb",
                "approved_at": "2026-04-22T09:00:00Z"
            }
        }


class ClinicalCodebook(BaseModel):
    """Full codebook with metadata."""
    codebook_version: str
    approved_by: str
    approved_at: str
    effective_date: str
    note: Optional[str] = None
    provisions: List[CriteriaCodebookEntry]


# ============================================================================
# METRICS: [A6] Gate Query Response
# ============================================================================

class ShadowLogMetrics(BaseModel):
    """
    Metrics for [A6] gate validation.
    Per specs/06b-capability-spec-triage.md Section 8.2.
    """
    total_entries: int = Field(..., description="Total shadow log entries")
    labeled_entries: int = Field(..., description="Entries with processor decision")
    disagreement_entries: int = Field(..., description="Entries where agreement=DISAGREE")
    false_negative_count: int = Field(..., description="Agent=FAST_PATH, processor=CLINICAL_PATH")
    false_negative_rate: float = Field(..., description="false_negative_count / labeled_entries")
    gate_status: str = Field(..., description="PASS or FAIL")
    gate_threshold: float = Field(default=0.02, description="[A6] gate threshold")
    min_labeled_entries: int = Field(default=2000, description="Minimum entries required")
    wave_2_ready: bool = Field(..., description="All gate conditions met")

    class Config:
        json_schema_extra = {
            "example": {
                "total_entries": 2154,
                "labeled_entries": 2154,
                "disagreement_entries": 38,
                "false_negative_count": 21,
                "false_negative_rate": 0.0097,
                "gate_status": "PASS",
                "gate_threshold": 0.02,
                "min_labeled_entries": 2000,
                "wave_2_ready": True
            }
        }
