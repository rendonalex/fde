from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from agent.config import DomainConfig
from agent.core.validator import validate_llm_response
from agent.models import HITLFailureReason, LLMExtractionResult

DICTIONARIES_PATH = "config/dictionaries.yaml"


@pytest.fixture
def domain():
    return DomainConfig(DICTIONARIES_PATH)


def _future_iso() -> str:
    dt = datetime.now(timezone.utc) + timedelta(days=7)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _past_iso() -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=1)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _result(**kwargs) -> LLMExtractionResult:
    defaults = dict(
        specialty_code="ICU_RN",
        specialty_confidence=1.0,
        datetime_start=_future_iso(),
        datetime_start_confidence=1.0,
        datetime_end=_future_iso(),
        datetime_end_confidence=1.0,
        location_id="ST_DAVIDS_NORTH",
        location_confidence=1.0,
        credentials=["BLS"],
        credential_confidence=1.0,
    )
    defaults.update(kwargs)
    return LLMExtractionResult(**defaults)


def test_valid_result_passes(domain):
    vr = validate_llm_response(_result(), domain)
    assert vr.is_valid


def test_datetime_in_past_triggers_reason(domain):
    vr = validate_llm_response(_result(datetime_start=_past_iso(), datetime_start_confidence=0.9), domain)
    assert vr.failure_reason == HITLFailureReason.DATETIME_IN_PAST
    assert vr.result.datetime_start_confidence == 0.0


def test_unknown_location_triggers_ambiguous(domain):
    vr = validate_llm_response(_result(location_id="UNKNOWN", location_confidence=0.3), domain)
    assert vr.failure_reason == HITLFailureReason.AMBIGUOUS_LOCATION


def test_location_not_in_dict_triggers_ambiguous(domain):
    vr = validate_llm_response(_result(location_id="SOME_UNKNOWN_HOSPITAL", location_confidence=0.5), domain)
    assert vr.failure_reason == HITLFailureReason.AMBIGUOUS_LOCATION


def test_unknown_specialty_caps_confidence(domain):
    vr = validate_llm_response(_result(specialty_code="SICU_XYZ", specialty_confidence=0.9), domain)
    assert vr.result.specialty_confidence <= 0.50


def test_invalid_credential_caps_confidence(domain):
    vr = validate_llm_response(_result(credentials=["BLS", "FAKE_CERT"], credential_confidence=1.0), domain)
    assert vr.result.credential_confidence <= 0.70


def test_empty_credentials_valid(domain):
    vr = validate_llm_response(_result(credentials=[], credential_confidence=1.0), domain)
    assert vr.is_valid


def test_unknown_specialty_code_ok(domain):
    vr = validate_llm_response(_result(specialty_code="UNKNOWN", specialty_confidence=0.0), domain)
    # specialty UNKNOWN caps to 0.50 max; but it's already 0.0 — location is valid so no failure_reason from validation
    # the low confidence will be caught by scorer + router, not by validator
    assert vr.failure_reason is None or vr.failure_reason == HITLFailureReason.AMBIGUOUS_LOCATION


def test_valid_all_known_codes(domain):
    vr = validate_llm_response(
        _result(
            specialty_code="ED_RN",
            credentials=["BLS", "ACLS", "TNCC"],
            location_id="SETON_MAIN",
        ),
        domain,
    )
    assert vr.is_valid
