from agent.models import LLMExtractionResult


def compute_confidence_score(result: LLMExtractionResult) -> float:
    return min(
        result.specialty_confidence,
        result.datetime_start_confidence,
        result.datetime_end_confidence,
        result.location_confidence,
        result.credential_confidence,
    )
