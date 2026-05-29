from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import respx
import httpx

from agent.clients.llm import InvalidJSONError, LLMClient, LLMHaltError, LLMUnavailableError
from agent.config import DomainConfig
from agent.core.prompt import build_system_prompt
from agent.core.scorer import compute_confidence_score
from agent.core.validator import validate_llm_response
from agent.models import HITLFailureReason, LLMExtractionResult

DICTIONARIES_PATH = "config/dictionaries.yaml"

FUTURE_DT = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
FUTURE_DT_END = (datetime.now(timezone.utc) + timedelta(days=7, hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")

HIGH_CONFIDENCE_RESPONSE = json.dumps({
    "specialty_code": "ICU_RN",
    "specialty_confidence": 1.0,
    "datetime_start": FUTURE_DT,
    "datetime_start_confidence": 0.95,
    "datetime_end": FUTURE_DT_END,
    "datetime_end_confidence": 0.95,
    "location_id": "ST_DAVIDS_NORTH",
    "location_confidence": 1.0,
    "credentials": ["BLS", "ACLS"],
    "credential_confidence": 1.0,
})

LOW_CONFIDENCE_RESPONSE = json.dumps({
    "specialty_code": "UNKNOWN",
    "specialty_confidence": 0.0,
    "datetime_start": None,
    "datetime_start_confidence": 0.30,
    "datetime_end": None,
    "datetime_end_confidence": 0.0,
    "location_id": "UNKNOWN",
    "location_confidence": 0.50,
    "credentials": [],
    "credential_confidence": 0.50,
})


@pytest.fixture
def domain():
    return DomainConfig(DICTIONARIES_PATH)


# ------------------------------------------------------------------ LLM client unit tests

@pytest.mark.asyncio
@respx.mock
async def test_llm_happy_path():
    respx.post("https://api.anthropic.com/v1/messages").mock(
        return_value=httpx.Response(200, json={
            "content": [{"type": "text", "text": HIGH_CONFIDENCE_RESPONSE}],
            "usage": {"input_tokens": 1400, "output_tokens": 380},
        })
    )
    client = LLMClient("test-key", "system prompt", timeout_seconds=5)
    result = await client.extract_shift("ICU float RN, BLS/ACLS req, St. David's North, 7a-7p Friday")
    assert result.specialty_code == "ICU_RN"
    assert result.specialty_confidence == 1.0
    assert result.location_id == "ST_DAVIDS_NORTH"


@pytest.mark.asyncio
@respx.mock
async def test_llm_401_raises_auth_error():
    respx.post("https://api.anthropic.com/v1/messages").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    client = LLMClient("bad-key", "system prompt", timeout_seconds=5)
    from agent.clients.llm import LLMAuthError
    with pytest.raises(LLMAuthError):
        await client.extract_shift("some request")


@pytest.mark.asyncio
@respx.mock
async def test_llm_400_raises_halt_error():
    respx.post("https://api.anthropic.com/v1/messages").mock(
        return_value=httpx.Response(400, text="Bad Request")
    )
    client = LLMClient("test-key", "system prompt", timeout_seconds=5)
    with pytest.raises(LLMHaltError):
        await client.extract_shift("some request")


@pytest.mark.asyncio
@respx.mock
async def test_llm_malformed_json_twice_raises_invalid():
    respx.post("https://api.anthropic.com/v1/messages").mock(
        return_value=httpx.Response(200, json={
            "content": [{"type": "text", "text": "not valid json {{{{"}],
        })
    )
    client = LLMClient("test-key", "system prompt", timeout_seconds=5)
    with pytest.raises(InvalidJSONError):
        await client.extract_shift("some request")


# ------------------------------------------------------------------ scorer + validator integration

def test_hp01_happy_path(domain):
    result = LLMExtractionResult(
        specialty_code="ICU_RN",
        specialty_confidence=1.0,
        datetime_start=FUTURE_DT,
        datetime_start_confidence=0.95,
        datetime_end=FUTURE_DT_END,
        datetime_end_confidence=0.95,
        location_id="ST_DAVIDS_NORTH",
        location_confidence=1.0,
        credentials=["BLS", "ACLS"],
        credential_confidence=1.0,
    )
    vr = validate_llm_response(result, domain)
    assert vr.is_valid
    score = compute_confidence_score(vr.result)
    assert score >= 0.85


def test_bp1_low_confidence_route(domain):
    result = LLMExtractionResult(
        specialty_code="UNKNOWN",
        specialty_confidence=0.0,
        datetime_start=None,
        datetime_start_confidence=0.30,
        datetime_end=None,
        datetime_end_confidence=0.0,
        location_id="UNKNOWN",
        location_confidence=0.50,
        credentials=[],
        credential_confidence=0.50,
    )
    vr = validate_llm_response(result, domain)
    score = compute_confidence_score(vr.result)
    assert score < 0.85


def test_ec01_ambiguous_location(domain):
    result = LLMExtractionResult(
        specialty_code="ED_RN",
        specialty_confidence=1.0,
        datetime_start=FUTURE_DT,
        datetime_start_confidence=0.60,
        datetime_end=FUTURE_DT_END,
        datetime_end_confidence=0.60,
        location_id="UNKNOWN",
        location_confidence=0.30,
        credentials=["BLS"],
        credential_confidence=1.0,
    )
    vr = validate_llm_response(result, domain)
    assert vr.failure_reason == HITLFailureReason.AMBIGUOUS_LOCATION


def test_ec05_datetime_in_past(domain):
    past = (datetime.now(timezone.utc) - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = LLMExtractionResult(
        specialty_code="ICU_RN",
        specialty_confidence=1.0,
        datetime_start=past,
        datetime_start_confidence=0.90,
        datetime_end=FUTURE_DT_END,
        datetime_end_confidence=0.90,
        location_id="ST_DAVIDS_NORTH",
        location_confidence=1.0,
        credentials=["BLS"],
        credential_confidence=1.0,
    )
    vr = validate_llm_response(result, domain)
    assert vr.failure_reason == HITLFailureReason.DATETIME_IN_PAST
    assert vr.result.datetime_start_confidence == 0.0


def test_system_prompt_builds(domain):
    prompt = build_system_prompt(domain)
    assert "ICU_RN" in prompt
    assert "BLS" in prompt
    assert "ST_DAVIDS_NORTH" in prompt
    assert "OUTPUT SCHEMA" in prompt
    assert "FEW-SHOT EXAMPLES" in prompt
