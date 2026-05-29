import pytest

from agent.core.scorer import compute_confidence_score
from agent.models import LLMExtractionResult


def _result(**kwargs) -> LLMExtractionResult:
    defaults = dict(
        specialty_code="ICU_RN",
        specialty_confidence=1.0,
        datetime_start="2026-06-01T12:00:00Z",
        datetime_start_confidence=1.0,
        datetime_end="2026-06-02T00:00:00Z",
        datetime_end_confidence=1.0,
        location_id="ST_DAVIDS_NORTH",
        location_confidence=1.0,
        credentials=["BLS", "ACLS"],
        credential_confidence=1.0,
    )
    defaults.update(kwargs)
    return LLMExtractionResult(**defaults)


def test_all_ones():
    assert compute_confidence_score(_result()) == 1.0


def test_min_is_specialty():
    r = _result(specialty_confidence=0.60)
    assert compute_confidence_score(r) == 0.60


def test_min_is_datetime_start():
    r = _result(datetime_start_confidence=0.30)
    assert compute_confidence_score(r) == 0.30


def test_min_is_datetime_end():
    r = _result(datetime_end_confidence=0.00)
    assert compute_confidence_score(r) == 0.00


def test_min_is_location():
    r = _result(location_confidence=0.30)
    assert compute_confidence_score(r) == 0.30


def test_min_is_credential():
    r = _result(credential_confidence=0.50)
    assert compute_confidence_score(r) == 0.50


def test_example1_high_confidence():
    r = _result(
        specialty_confidence=1.0,
        datetime_start_confidence=0.95,
        datetime_end_confidence=0.95,
        location_confidence=1.0,
        credential_confidence=1.0,
    )
    assert compute_confidence_score(r) == 0.95


def test_example2_low_confidence():
    r = _result(
        specialty_confidence=0.0,
        datetime_start_confidence=0.30,
        datetime_end_confidence=0.00,
        location_confidence=0.50,
        credential_confidence=0.50,
    )
    assert compute_confidence_score(r) == 0.0


def test_example3_ambiguous_location():
    r = _result(
        specialty_confidence=1.0,
        datetime_start_confidence=0.60,
        datetime_end_confidence=0.60,
        location_confidence=0.30,
        credential_confidence=1.0,
    )
    assert compute_confidence_score(r) == 0.30


def test_above_threshold_bp2():
    r = _result(
        specialty_confidence=1.0,
        datetime_start_confidence=0.95,
        datetime_end_confidence=0.95,
        location_confidence=1.0,
        credential_confidence=1.0,
    )
    assert compute_confidence_score(r) >= 0.85


def test_below_threshold_bp1():
    r = _result(location_confidence=0.30)
    assert compute_confidence_score(r) < 0.85
