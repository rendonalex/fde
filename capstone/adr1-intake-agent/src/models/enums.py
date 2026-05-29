"""Enums for ADR-1 data models."""

from enum import Enum


class ClaimType(str, Enum):
    """Type of claim submission."""

    PROFESSIONAL = "PROFESSIONAL"
    INSTITUTIONAL = "INSTITUTIONAL"
    DENTAL = "DENTAL"


class ExtractionStatus(str, Enum):
    """Status of field extraction from claim submission."""

    AUTO_COMPLETE = "AUTO_COMPLETE"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"
    PENDING_DUPLICATE = "PENDING_DUPLICATE"


class IntakeChannel(str, Enum):
    """Channel through which claim was submitted."""

    EDI_837P = "EDI_837P"
    EDI_837I = "EDI_837I"
    PORTAL_JSON = "PORTAL_JSON"
    FHIR_R4 = "FHIR_R4"
    CMS1500_PDF = "CMS1500_PDF"
    CMS1500_OCR_TEXT = "CMS1500_OCR_TEXT"
    EMAIL = "EMAIL"
    FAX = "FAX"
    FAX_EMAIL = "FAX_EMAIL"
    EXCEPTION_NOTE = "EXCEPTION_NOTE"


class RoutingDecision(str, Enum):
    """Routing decision made by ADR-4 triage agent."""

    PENDING_TRIAGE = "PENDING_TRIAGE"
    FAST_PATH = "FAST_PATH"
    CLINICAL_PATH = "CLINICAL_PATH"


class RoutingMode(str, Enum):
    """Mode in which routing decision was made."""

    SHADOW = "SHADOW"
    LIVE = "LIVE"


class SLAQueue(str, Enum):
    """SLA priority queue assignment."""

    PRIORITY = "PRIORITY"
    STANDARD = "STANDARD"
    BATCH = "BATCH"


class ExceptionType(str, Enum):
    """Type of exception requiring human intervention."""

    LOW_CONFIDENCE_EXTRACTION = "LOW_CONFIDENCE_EXTRACTION"
    DUPLICATE_HOLD = "DUPLICATE_HOLD"
    FORMAT_UNRECOGNIZED = "FORMAT_UNRECOGNIZED"
    CMS_WRITE_FAILURE = "CMS_WRITE_FAILURE"


class RequiredAction(str, Enum):
    """Required human action to resolve exception."""

    HUMAN_REKEY = "HUMAN_REKEY"
    DUPLICATE_RESOLUTION = "DUPLICATE_RESOLUTION"
    FORMAT_IDENTIFICATION = "FORMAT_IDENTIFICATION"
    MANUAL_WRITE = "MANUAL_WRITE"


class Priority(str, Enum):
    """Priority level for exception queue items."""

    HIGH = "HIGH"
    STANDARD = "STANDARD"


class ResolutionStatus(str, Enum):
    """Status of exception queue item resolution."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"


class EventType(str, Enum):
    """Type of audit log event."""

    # ADR-1 events
    CLAIM_RECEIVED = "CLAIM_RECEIVED"
    EXTRACTION_COMPLETE = "EXTRACTION_COMPLETE"
    VALIDATION_COMPLETE = "VALIDATION_COMPLETE"
    CMS_WRITE_SUCCESS = "CMS_WRITE_SUCCESS"
    CMS_WRITE_FAILED = "CMS_WRITE_FAILED"
    EXCEPTION_QUEUED = "EXCEPTION_QUEUED"
    DUPLICATE_DETECTED = "DUPLICATE_DETECTED"

    # ADR-4 events (for future use)
    ROUTING_DECISION_LOGGED = "ROUTING_DECISION_LOGGED"
    ROUTING_DECISION_WRITTEN = "ROUTING_DECISION_WRITTEN"


class Outcome(str, Enum):
    """Outcome of processing event."""

    SUCCESS = "SUCCESS"
    PENDING_HUMAN = "PENDING_HUMAN"
    FAILED = "FAILED"
    DUPLICATE_HOLD = "DUPLICATE_HOLD"
