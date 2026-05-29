from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from agent.config import DomainConfig
from agent.models import HITLFailureReason, LLMExtractionResult


class ValidationResult:
    def __init__(
        self,
        result: LLMExtractionResult,
        failure_reason: Optional[HITLFailureReason] = None,
    ) -> None:
        self.result = result
        self.failure_reason = failure_reason

    @property
    def is_valid(self) -> bool:
        return self.failure_reason is None


def validate_llm_response(
    raw_result: LLMExtractionResult, config: DomainConfig
) -> ValidationResult:
    result = raw_result.model_copy(deep=True)

    # Cap specialty confidence if code not in dictionary (§3.2)
    if result.specialty_code not in config.valid_specialty_codes and result.specialty_code != "UNKNOWN":
        result.specialty_confidence = min(result.specialty_confidence, 0.50)

    # Cap credential confidence if any code not in dictionary (§8.4)
    invalid = [c for c in result.credentials if c not in config.valid_credential_codes]
    if invalid:
        result.credential_confidence = min(result.credential_confidence, 0.70)

    # Datetime in the past check (§3.2, Edge Case 5)
    if result.datetime_start is not None:
        try:
            dt_str = result.datetime_start.replace("Z", "+00:00")
            dt = datetime.fromisoformat(dt_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt <= datetime.now(timezone.utc):
                result.datetime_start_confidence = 0.00
                return ValidationResult(result, HITLFailureReason.DATETIME_IN_PAST)
        except ValueError:
            result.datetime_start_confidence = 0.00

    # Ambiguous or unknown location (§8.3)
    if result.location_id == "UNKNOWN" or result.location_id not in config.valid_location_ids:
        return ValidationResult(result, HITLFailureReason.AMBIGUOUS_LOCATION)

    return ValidationResult(result, None)


def build_partial_parse(result: LLMExtractionResult) -> dict:
    return {
        "specialty_code": result.specialty_code if result.specialty_code != "UNKNOWN" else None,
        "datetime_start": result.datetime_start,
        "datetime_end": result.datetime_end,
        "location_id": result.location_id if result.location_id != "UNKNOWN" else None,
        "credentials": result.credentials,
        "confidence_score": None,
    }
