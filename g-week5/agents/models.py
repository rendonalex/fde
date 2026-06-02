"""
Entity models for ADR-1 and ADR-2 agents.
Implements ICH E2D data structures with FDA May 2026 Guidance compliance.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from uuid import uuid4


# Enums
class ReportFormat(str, Enum):
    HCP_TEXT = "HCP_TEXT"
    PATIENT_WEBFORM = "PATIENT_WEBFORM"
    PHONE_VTT = "PHONE_VTT"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    TRIAL_REPORT = "TRIAL_REPORT"
    LITERATURE = "LITERATURE"


class ExtractionStatus(str, Enum):
    AUTO_COMPLETE = "AUTO_COMPLETE"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"
    PENDING_DUPLICATE = "PENDING_DUPLICATE"
    EXCEPTION_NOTE = "EXCEPTION_NOTE"
    REPORTER_FOLLOWUP = "REPORTER_FOLLOWUP"


class Sex(str, Enum):
    M = "M"
    F = "F"
    UNKNOWN = "Unknown"


class Outcome(str, Enum):
    RECOVERED = "recovered"
    RECOVERING = "recovering"
    NOT_RECOVERED = "not_recovered"
    FATAL = "fatal"
    UNKNOWN = "unknown"


class SourceDocumentFormat(str, Enum):
    EMAIL = "EMAIL"
    PDF = "PDF"
    VTT = "VTT"
    JSON = "JSON"
    TEXT = "TEXT"


class CreatedBy(str, Enum):
    ADR1 = "ADR-1"
    CASE_PROCESSOR = "CASE_PROCESSOR"


# Nested Entities
class Patient(BaseModel):
    """Patient demographics (nested in AECasePackage)"""
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    sex: Sex = Field(Sex.UNKNOWN, description="Patient sex")
    weight: Optional[float] = Field(None, gt=0.0, le=500.0, description="Weight in kg")
    race: Optional[str] = Field(None, max_length=50, description="Race (when voluntarily reported)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Per-field confidence score")

    @validator("age")
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 120):
            raise ValueError("Age must be between 0 and 120 years")
        return v


class SuspectDrug(BaseModel):
    """Suspect drug information (nested in AECasePackage)"""
    name: str = Field(..., max_length=200, description="Drug name (generic preferred, brand acceptable)")
    dose: str = Field(..., max_length=100, description="Dose + unit (e.g., '150 mg', '2 tablets')")
    route: Optional[str] = Field(None, max_length=50, description="Route of administration")
    indication: Optional[str] = Field(None, max_length=200, description="Indication for use")
    rxnorm_code: Optional[str] = Field(None, description="RxNorm RxCUI code")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Per-field confidence score")


class AEDescription(BaseModel):
    """Adverse event description (nested in AECasePackage)"""
    narrative: str = Field(..., max_length=5000, description="Free-text AE description")
    meddra_pt: Optional[str] = Field(None, max_length=200, description="MedDRA Preferred Term")
    meddra_code: Optional[str] = Field(None, description="MedDRA PT code (8-digit)")
    onset_date: Optional[str] = Field(None, description="AE onset date (ISO 8601 date)")
    outcome: Optional[Outcome] = Field(None, description="AE outcome")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Per-field confidence score")

    @validator("onset_date")
    def validate_onset_date(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("onset_date must be valid ISO 8601 date")
        return v


class Temporal(BaseModel):
    """Temporal relationships (nested in AECasePackage)"""
    drug_start_date: Optional[str] = Field(None, description="Drug start date (ISO 8601)")
    ae_onset_date: Optional[str] = Field(None, description="AE onset date (ISO 8601)")
    outcome_date: Optional[str] = Field(None, description="Outcome date (ISO 8601)")
    date_estimated: bool = Field(False, description="True if any date was estimated from ambiguous text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Per-field confidence score")


class ConcomitantMed(BaseModel):
    """Concomitant medication (nested in AECasePackage, array)"""
    name: str = Field(..., max_length=200, description="Medication name")
    dose: Optional[str] = Field(None, max_length=100, description="Dose + unit")
    route: Optional[str] = Field(None, max_length=50, description="Route of administration")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Per-field confidence score")


class MedicalHistory(BaseModel):
    """Medical history (nested in AECasePackage)"""
    narrative: Optional[str] = Field(None, max_length=2000, description="Free-text medical history")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Per-field confidence score")


class SpanCitation(BaseModel):
    """Span citation linking extracted value to source text location"""
    value: str = Field(..., description="Extracted value")
    source_span: str = Field(..., description="Character indices in source text (format: 'start-end')")

    @validator("source_span")
    def validate_span(cls, v):
        try:
            start, end = v.split("-")
            start_int, end_int = int(start), int(end)
            # Allow start == end for placeholder spans (will be flagged in audit)
            if start_int > end_int or start_int < 0:
                raise ValueError
        except (ValueError, AttributeError):
            raise ValueError("source_span must be format 'start-end' with start <= end and start >= 0")
        return v


class SourceDocument(BaseModel):
    """
    [CURVEBALL - FDA May 2026 Guidance]
    Source document metadata per FDA Requirement 1: "source documents consulted"
    for 10-year retention + FDA inspection traceability.
    """
    filename: str = Field(..., max_length=255, description="Original filename")
    format: SourceDocumentFormat = Field(..., description="Source document format")
    received_at: str = Field(..., description="Receipt timestamp (ISO 8601)")
    sha256_hash: str = Field(..., min_length=64, max_length=64, description="SHA-256 hash for integrity")

    @validator("sha256_hash")
    def validate_sha256(cls, v):
        if not all(c in "0123456789abcdefABCDEF" for c in v):
            raise ValueError("sha256_hash must be valid hex string")
        return v.lower()


# Root Entity
class AECasePackage(BaseModel):
    """
    Root entity: structured output from ADR-1 extraction, input to ADR-2 triage.
    System of record for extracted AE data.
    """
    case_id: str = Field(default_factory=lambda: str(uuid4()), description="UUID primary key, idempotency key")
    received_at: str = Field(..., description="Receipt timestamp (ISO 8601), immutable, anchors 15-day clock")
    format: ReportFormat = Field(..., description="Report format classification")
    extraction_status: ExtractionStatus = Field(..., description="Extraction workflow status")

    # Required nested entities
    patient: Patient = Field(..., description="Patient demographics")
    suspect_drug: SuspectDrug = Field(..., description="Suspect drug information")
    ae_description: AEDescription = Field(..., description="Adverse event description")
    temporal: Temporal = Field(..., description="Temporal relationships")

    # Optional nested entities
    concomitant_meds: List[ConcomitantMed] = Field(default_factory=list, description="Concomitant medications")
    medical_history: Optional[MedicalHistory] = Field(None, description="Medical history")

    # Audit trail
    span_citations: dict[str, SpanCitation] = Field(default_factory=dict, description="Span citations for extracted fields")

    # [CURVEBALL - FDA May 2026 Guidance] FDA Requirement 1 fields
    source_documents: List[SourceDocument] = Field(..., min_items=1, description="Source documents consulted (FDA Req 1)")
    model_version_adr1: str = Field(..., description="Model identity and version (FDA Req 1)")

    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z", description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z", description="Last update timestamp")
    created_by: CreatedBy = Field(CreatedBy.ADR1, description="Creator identifier")
    updated_by: CreatedBy = Field(CreatedBy.ADR1, description="Last updater identifier")

    @validator("source_documents")
    def validate_source_documents_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError("source_documents array must contain at least one document (FDA Req 1)")
        return v

    class Config:
        use_enum_values = True
        protected_namespaces = ()  # Allow model_version_adr1 field
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


# Validation helper
def validate_extraction_complete(package: AECasePackage) -> bool:
    """
    Validate that extraction meets AUTO_COMPLETE criteria:
    - All required fields have confidence >= 0.85
    - Concomitant meds have confidence >= 0.80 (lower threshold per spec)
    - 100% span citation completeness
    """
    required_fields_confidence = [
        package.patient.confidence,
        package.suspect_drug.confidence,
        package.ae_description.confidence,
        package.temporal.confidence
    ]

    # Check required fields
    if any(conf < 0.85 for conf in required_fields_confidence):
        return False

    # Check concomitant meds (0.80 threshold)
    if any(med.confidence < 0.80 for med in package.concomitant_meds):
        return False

    # Check span citations (must exist for required fields)
    required_citation_fields = [
        "patient.age", "patient.sex",
        "suspect_drug.name", "suspect_drug.dose",
        "ae_description.narrative",
        "temporal.ae_onset_date"
    ]

    for field in required_citation_fields:
        if field not in package.span_citations:
            # Allow missing citations for null/unknown values
            if field == "patient.age" and package.patient.age is None:
                continue
            if field == "temporal.ae_onset_date" and package.temporal.ae_onset_date is None:
                continue
            # Required field missing citation
            return False

    return True


# =============================================================================
# ADR-2 TRIAGE AGENT ENTITIES
# =============================================================================

# Enums for ADR-2
class SeriousnessCriterion(str, Enum):
    DEATH = "death"
    LIFE_THREATENING = "life_threatening"
    HOSPITALIZATION = "hospitalization"
    DISABILITY = "disability"
    CONGENITAL_ANOMALY = "congenital_anomaly"
    OTHER_MEDICALLY_IMPORTANT = "other_medically_important"


class RSIMatchType(str, Enum):
    EXACT = "exact"
    BROADER = "broader"
    NARROWER = "narrower"
    SYNONYM = "synonym"
    NONE = "none"


class ReportabilityType(str, Enum):
    EXPEDITED_15_DAY = "15_DAY_EXPEDITED"
    PERIODIC = "PERIODIC"
    NON_REPORTABLE = "NON_REPORTABLE"


class Jurisdiction(str, Enum):
    FDA = "FDA"
    EMA = "EMA"
    MHRA = "MHRA"
    PMDA = "PMDA"


class DeepReviewReason(str, Enum):
    AMBIGUOUS_SERIOUSNESS = "ambiguous_seriousness"
    NOVEL_AE_TERM = "novel_ae_term"
    TERM_SPECIFICITY_VARIANCE = "term_specificity_variance"
    MULTI_JURISDICTIONAL_COMPLEXITY = "multi_jurisdictional_complexity"
    CAUSALITY_UNRELATED = "causality_unrelated"


class MSOAction(str, Enum):
    ACCEPTED = "accepted"
    MODIFIED = "modified"
    OVERRIDDEN = "overridden"


# Nested ADR-2 Entities
class SeriousnessClassification(BaseModel):
    """Seriousness classification per ICH E2A criteria"""
    serious: bool = Field(..., description="True if serious per ICH E2A")
    criteria_matched: List[SeriousnessCriterion] = Field(
        default_factory=list,
        description="ICH E2A criteria matched (empty if non-serious)"
    )
    reasoning: str = Field(..., max_length=2000, description="CoT reasoning for classification")
    span_citations: dict[str, str] = Field(
        default_factory=dict,
        description="Links each criterion to source span"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")

    @validator("criteria_matched")
    def validate_criteria_consistency(cls, v, values):
        if values.get("serious") and len(v) == 0:
            raise ValueError("If serious=true, criteria_matched must have at least one value")
        if not values.get("serious") and len(v) > 0:
            raise ValueError("If serious=false, criteria_matched must be empty")
        return v


class ExpectednessSignal(BaseModel):
    """Expectedness assessment against product RSI"""
    unexpected: bool = Field(..., description="True if AE not in product RSI")
    rsi_match: RSIMatchType = Field(..., description="Type of RSI match")
    rsi_term_matched: Optional[str] = Field(None, max_length=200, description="Which RSI term matched")
    reasoning: str = Field(..., max_length=2000, description="CoT reasoning with MedDRA hierarchy")
    span_citations: dict[str, str] = Field(
        default_factory=dict,
        description="Links RSI term and AE term to source spans"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Expectedness confidence")

    @validator("confidence")
    def validate_novel_confidence(cls, v, values):
        if values.get("unexpected") and values.get("rsi_match") == RSIMatchType.NONE:
            if v != 0.0:
                raise ValueError("Novel AE term (rsi_match=none) must have confidence=0.0")
        return v

    @validator("rsi_term_matched")
    def validate_rsi_term(cls, v, values):
        rsi_match = values.get("rsi_match")
        if rsi_match == RSIMatchType.NONE and v is not None:
            raise ValueError("If rsi_match=none, rsi_term_matched must be null")
        if rsi_match != RSIMatchType.NONE and v is None:
            raise ValueError("If rsi_match!=none, rsi_term_matched must be non-null")
        return v


class ReportabilityRecommendation(BaseModel):
    """Reportability recommendation per FDA 21 CFR 314.80"""
    recommendation: ReportabilityType = Field(..., description="Reportability type")
    jurisdictions: List[Jurisdiction] = Field(
        default_factory=list,
        description="Regulators requiring expedited reporting"
    )
    rule_justification: str = Field(..., max_length=1000, description="Regulatory citations")
    causality_context: Optional[str] = Field(None, max_length=1000, description="Causality influence")
    reasoning: str = Field(..., max_length=2000, description="CoT reasoning for reportability")
    span_citations: dict[str, str] = Field(
        default_factory=dict,
        description="Links to regulatory rules"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Recommendation confidence")

    @validator("jurisdictions")
    def validate_jurisdictions(cls, v, values):
        rec = values.get("recommendation")
        if rec == ReportabilityType.EXPEDITED_15_DAY and len(v) == 0:
            raise ValueError("15_DAY_EXPEDITED must have at least one jurisdiction")
        if rec in [ReportabilityType.PERIODIC, ReportabilityType.NON_REPORTABLE] and len(v) > 0:
            raise ValueError("PERIODIC/NON_REPORTABLE must have empty jurisdictions")
        return v


class MSOFlags(BaseModel):
    """Flags for MSO deep review"""
    deep_review_required: bool = Field(..., description="True if MSO deep review needed")
    reason: List[DeepReviewReason] = Field(
        default_factory=list,
        description="Reasons for deep review"
    )

    @validator("reason")
    def validate_reason(cls, v, values):
        if values.get("deep_review_required") and len(v) == 0:
            raise ValueError("If deep_review_required=true, reason must have at least one value")
        return v


class AuditTrail(BaseModel):
    """Audit trail for FDA inspection"""
    timestamp: str = Field(..., description="Classification timestamp (ISO 8601)")
    agent_version: str = Field(..., description="ADR-2 version (e.g., 'ADR-2 v1.0')")
    regulatory_references: List[str] = Field(
        ...,
        min_items=2,
        description="Regulations cited (min: ICH E2A, FDA 21 CFR 314.80)"
    )

    @validator("timestamp")
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("timestamp must be valid ISO 8601")
        return v


class SignalPattern(BaseModel):
    """
    [CURVEBALL - FDA May 2026 Guidance]
    Signal detection pattern for 3-cases-in-90-days escalation
    """
    product: str = Field(..., description="Suspect drug product name")
    meddra_pt: str = Field(..., description="MedDRA Preferred Term")
    meddra_code: str = Field(..., description="8-digit MedDRA PT code")
    case_count: int = Field(..., ge=3, description="Total cases matching pattern (min 3)")
    window_start: str = Field(..., description="90-day window start (ISO 8601 date)")
    window_end: str = Field(..., description="90-day window end (ISO 8601 date)")


# Root ADR-2 Entity
class TriageRecommendation(BaseModel):
    """
    Root entity: structured output from ADR-2 triage, input to MSO review queue.
    Contains seriousness classification, expectedness signal, reportability recommendation.
    """
    case_id: str = Field(..., description="UUID linking to AECasePackage")

    # Core classifications
    seriousness_classification: SeriousnessClassification = Field(..., description="ICH E2A seriousness")
    expectedness_signal: ExpectednessSignal = Field(..., description="RSI expectedness assessment")
    reportability_recommendation: ReportabilityRecommendation = Field(..., description="FDA reportability")
    mso_flags: MSOFlags = Field(..., description="MSO review flags")
    audit_trail: AuditTrail = Field(..., description="FDA audit trail")

    # [CURVEBALL - FDA May 2026 Guidance] Signal detection fields
    signal_detection_flag: bool = Field(False, description="True if 3-cases-in-90-days pattern detected")
    signal_pattern: Optional[SignalPattern] = Field(None, description="Pattern details if flag=true")
    model_version_adr2: str = Field(..., description="Model version (FDA Req 1)")

    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    created_by: str = Field("ADR-2", description="Creator identifier")

    # MSO review fields
    mso_reviewed_at: Optional[str] = Field(None, description="MSO review timestamp")
    mso_reviewed_by: Optional[str] = Field(None, description="MSO user ID")
    mso_override: bool = Field(False, description="True if MSO overrode recommendation")
    mso_override_reason: Optional[str] = Field(None, max_length=1000, description="Override rationale")

    # [CURVEBALL - FDA May 2026 Guidance] FDA Requirement 2 fields
    mso_action: Optional[MSOAction] = Field(None, description="MSO action (accepted/modified/overridden)")
    mso_rationale: Optional[str] = Field(None, max_length=1000, description="MSO substantive review docs")

    @validator("signal_pattern")
    def validate_signal_pattern(cls, v, values):
        if values.get("signal_detection_flag") and v is None:
            raise ValueError("If signal_detection_flag=true, signal_pattern must be non-null")
        return v

    @validator("mso_rationale")
    def validate_mso_rationale(cls, v, values):
        action = values.get("mso_action")
        if action in [MSOAction.MODIFIED, MSOAction.OVERRIDDEN] and not v:
            raise ValueError("MSO modified/overridden action requires mso_rationale")
        return v

    class Config:
        use_enum_values = True
        protected_namespaces = ()
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }
