"""Models for extraction pipeline input/output."""

from typing import Any, Optional

from pydantic import BaseModel

from .enums import IntakeChannel


class ExtractedField(BaseModel):
    """A single field extracted from a claim submission."""

    value: Any
    confidence: float


class ExtractionResult(BaseModel):
    """
    Output from EDI parser or IDP extraction pipeline.
    This is the input to the ADR-1 LLM agent.
    """

    source_format: str
    source_claim_ref: str
    intake_channel: IntakeChannel
    extracted_fields: dict[str, ExtractedField]
    rfc5322_headers: Optional[dict[str, str]] = None  # For EMAIL channel

    model_config = {"use_enum_values": True}
