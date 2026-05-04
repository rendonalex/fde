"""
Data models for PA Chase Timing Agent
"""
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Any


class PAStatus(Enum):
    """PA status values"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"


class InsurerName(Enum):
    """Known insurer names"""
    HUMANA = "Humana"
    UHC = "UnitedHealthcare Choice"
    BCBS_PPO = "BCBS PPO"
    MEDICARE = "Medicare"
    WELLPATH = "Wellpath"
    AETNA = "Aetna"
    UNKNOWN = "Unknown"


class ActionType(Enum):
    """Recommendation action types"""
    RECOMMEND_CHASE = "recommend_chase"
    ESCALATE_TO_DANA = "escalate_to_dana"
    URGENT_FLAG = "urgent_flag"
    WAIT = "wait"


class ConfidenceLevel(Enum):
    """Confidence levels for predictions"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class InsurerPattern:
    """Represents learned SLA pattern for an insurer"""
    insurer_name: str
    sla_days: int
    confidence: ConfidenceLevel
    sample_size: int  # Number of historical cases
    last_updated: date
    variance_days: float  # Standard deviation in approval timing
    notes: Optional[str] = None
    is_predictable: bool = True  # False for Aetna-like insurers


@dataclass
class DenialPattern:
    """Represents learned denial pattern for insurer + procedure"""
    insurer_name: str
    procedure_type: str
    denial_reason_pattern: str  # Regex or keyword match
    workaround_suggestion: str  # What docs to attach for resubmission
    occurrence_count: int  # How many times this pattern observed
    confidence: ConfidenceLevel
    last_seen: date


@dataclass
class PriorAuthorization:
    """Represents a PA case"""
    pa_id: str
    patient_id: str
    patient_name: str
    insurer: str
    procedure_type: str
    procedure_date: date
    submission_date: date
    status: PAStatus
    denial_reason: Optional[str] = None
    approval_date: Optional[date] = None
    notes: Optional[str] = None


@dataclass
class ChaseRecommendation:
    """Agent's chase recommendation output"""
    action: ActionType
    pa_id: str
    patient_name: str
    insurer: str
    procedure: str
    submission_date: date
    procedure_date: date
    recommended_chase_date: Optional[date]
    rationale: str
    confidence: ConfidenceLevel
    predicted_approval_date: Optional[date]
    escalation_reason: Optional[str] = None

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return {
            "action": self.action.value,
            "pa_id": self.pa_id,
            "patient_name": self.patient_name,
            "insurer": self.insurer,
            "procedure": self.procedure,
            "submission_date": self.submission_date.isoformat(),
            "procedure_date": self.procedure_date.isoformat(),
            "recommended_chase_date": self.recommended_chase_date.isoformat() if self.recommended_chase_date else None,
            "rationale": self.rationale,
            "confidence": self.confidence.value,
            "predicted_approval_date": self.predicted_approval_date.isoformat() if self.predicted_approval_date else None,
            "escalation_reason": self.escalation_reason
        }


@dataclass
class DanaCorrection:
    """Represents Dana's feedback on agent recommendation"""
    pa_id: str
    agent_recommended_date: date
    dana_corrected_date: date
    correction_days: int  # Positive = Dana pushed later, negative = earlier
    insurer: str
    correction_rationale: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class PatternUpdate:
    """Proposed update to insurer pattern based on corrections/anomalies"""
    insurer_name: str
    current_sla_days: int
    proposed_sla_days: int
    reason: str  # "correction_threshold" or "anomaly_detected"
    supporting_data: List[str]  # PA IDs or correction IDs
    confidence: ConfidenceLevel
    requires_dana_approval: bool = True
