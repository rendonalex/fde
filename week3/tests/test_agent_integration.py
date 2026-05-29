"""
Agent integration tests mapping to specs/07-validation-plan.md.

Coverage:
  EC-01 (P0): Advisory lock — 409 on PARSING PATCH skips record; LLM not called
  EC-04 (P0): Duplicate ParsedShiftRequirement write (409) → idempotent; event emitted once
  ER-01 (P0): LLM HTTP 401 → agent halts; no PARSE_FAILED records created
  ER-02 (P0): ServiceNow write fails → DLQ entry created; shift_parsed NOT emitted
  ER-02b    : DLQ reconciliation succeeds → event emitted; DLQ cleared
  HP-01     : High-confidence BP2 parse → PARSED status + event emitted
  HP-02     : Ambiguous location → HITLQueueEntry written with AMBIGUOUS_LOCATION
  DLQ-depth : Dead-letter queue depth alert fires at threshold
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from agent.agent import ShiftIntakeParserAgent
from agent.clients.hitl_queue import HITLWriteOutcome
from agent.clients.llm import LLMAuthError, LLMUnavailableError
from agent.clients.servicenow import PatchOutcome, WriteOutcome
from agent.config import DomainConfig
from agent.models import (
    DeadLetterRecord,
    HITLFailureReason,
    LLMExtractionResult,
    ParseMethod,
    ParsedShiftRequirement,
    ShiftRequest,
    ShiftRequestStatus,
    SourceType,
)

DICTIONARIES_PATH = "config/dictionaries.yaml"

_FUTURE = (datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
_FUTURE_END = (datetime.now(timezone.utc) + timedelta(days=7, hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------ fixtures / helpers

def _make_record(
    sys_id: str = "sys-001",
    req_id: str = "req-001",
    raw_text: str = "ICU float RN, BLS req, St. David's North, 7a-7p Friday",
) -> ShiftRequest:
    return ShiftRequest(
        sys_id=sys_id,
        u_shift_request_id=req_id,
        u_source_type=SourceType.EMAIL,
        u_raw_text=raw_text,
        u_hospital_id="H001",
        u_status=ShiftRequestStatus.QUEUED,
        u_received_at=datetime.now(timezone.utc),
    )


def _high_confidence_result() -> LLMExtractionResult:
    return LLMExtractionResult(
        specialty_code="ICU_RN",
        specialty_confidence=1.0,
        datetime_start=_FUTURE,
        datetime_start_confidence=0.95,
        datetime_end=_FUTURE_END,
        datetime_end_confidence=0.95,
        location_id="ST_DAVIDS_NORTH",
        location_confidence=1.0,
        credentials=["BLS", "ACLS"],
        credential_confidence=1.0,
    )


def _ambiguous_location_result() -> LLMExtractionResult:
    """Maps to HP-02 / EC ambiguous location: location_id UNKNOWN triggers AMBIGUOUS_LOCATION."""
    return LLMExtractionResult(
        specialty_code="ED_RN",
        specialty_confidence=1.0,
        datetime_start=_FUTURE,
        datetime_start_confidence=0.60,
        datetime_end=_FUTURE_END,
        datetime_end_confidence=0.60,
        location_id="UNKNOWN",
        location_confidence=0.30,
        credentials=["BLS"],
        credential_confidence=1.0,
    )


def _make_agent(tmp_path) -> ShiftIntakeParserAgent:
    settings = MagicMock()
    settings.anthropic_api_key = "test-key"
    settings.llm_timeout_seconds = 5
    settings.confidence_threshold = 0.85
    settings.poll_interval_seconds = 30
    settings.poll_batch_size = 10
    settings.dead_letter_db_path = str(tmp_path / "dlq.db")
    settings.dead_letter_alert_threshold = 10
    settings.consecutive_failure_alert_threshold = 10
    settings.slack_webhook_url = None
    settings.hitl_queue_url = "http://localhost:8001"
    settings.system_service_token = "test-token"
    settings.event_bus_url = None

    domain = DomainConfig(DICTIONARIES_PATH)
    agent = ShiftIntakeParserAgent(settings, domain)
    agent._sn = AsyncMock()
    agent._hitl = AsyncMock()
    agent._events = AsyncMock()
    agent._llm = AsyncMock()
    return agent


# ------------------------------------------------------------------ EC-01

@pytest.mark.asyncio
async def test_ec01_advisory_lock_skips_record(tmp_path):
    """EC-01 (P0): 409 on PARSING PATCH → agent skips record; LLM not called."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    agent._sn.patch_status.return_value = PatchOutcome.ALREADY_SET

    await agent._process_record(_make_record())

    agent._llm.extract_shift.assert_not_called()
    agent._events.emit_shift_parsed.assert_not_called()
    agent._hitl.write_entry.assert_not_called()


# ------------------------------------------------------------------ EC-04

@pytest.mark.asyncio
async def test_ec04_duplicate_write_idempotent_event_emitted_once(tmp_path):
    """EC-04 (P0): 409 on ParsedShiftRequirement POST → treated as success; shift_parsed emitted once."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    agent._sn.patch_status.return_value = PatchOutcome.SUCCESS
    agent._llm.extract_shift.return_value = _high_confidence_result()
    agent._sn.write_parsed_requirement.return_value = (WriteOutcome.DUPLICATE, "existing-req-id")

    await agent._process_record(_make_record())

    agent._events.emit_shift_parsed.assert_called_once()
    _, emitted_req_id = agent._events.emit_shift_parsed.call_args[0]
    assert emitted_req_id == "existing-req-id"

    # Only one ParsedShiftRequirement write attempt
    agent._sn.write_parsed_requirement.assert_called_once()


# ------------------------------------------------------------------ ER-01

@pytest.mark.asyncio
async def test_er01_llm_auth_401_halts_agent(tmp_path):
    """ER-01 (P0): LLM HTTP 401 → agent._halt = True; status never set to PARSE_FAILED."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    agent._sn.patch_status.return_value = PatchOutcome.SUCCESS
    agent._llm.extract_shift.side_effect = LLMAuthError(401, "Unauthorized")

    await agent._process_record(_make_record())

    assert agent._halt is True
    all_status_patches = [c[0][1] for c in agent._sn.patch_status.call_args_list]
    assert ShiftRequestStatus.PARSE_FAILED not in all_status_patches
    agent._events.emit_shift_parsed.assert_not_called()


# ------------------------------------------------------------------ ER-02

@pytest.mark.asyncio
async def test_er02_sn_write_failure_pushes_dlq_no_event(tmp_path):
    """ER-02 (P0): ServiceNow write returns ERROR → DLQ entry created; shift_parsed NOT emitted."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    agent._sn.patch_status.return_value = PatchOutcome.SUCCESS
    agent._llm.extract_shift.return_value = _high_confidence_result()
    agent._sn.write_parsed_requirement.return_value = (WriteOutcome.ERROR, None)

    await agent._process_record(_make_record())

    assert await agent._dlq.depth() == 1
    agent._events.emit_shift_parsed.assert_not_called()


@pytest.mark.asyncio
async def test_er02_dlq_depth_alert_fires_at_threshold(tmp_path):
    """ER-02 (P0): DLQ depth ≥ alert threshold triggers ops alert."""
    settings = MagicMock()
    settings.dead_letter_db_path = str(tmp_path / "dlq.db")
    settings.dead_letter_alert_threshold = 3
    settings.confidence_threshold = 0.85
    settings.consecutive_failure_alert_threshold = 10
    settings.slack_webhook_url = None
    settings.hitl_queue_url = "http://localhost:8001"
    settings.system_service_token = "test-token"
    settings.event_bus_url = None

    domain = DomainConfig(DICTIONARIES_PATH)
    agent = ShiftIntakeParserAgent(settings, domain)
    agent._sn = AsyncMock()
    agent._hitl = AsyncMock()
    agent._events = AsyncMock()
    agent._llm = AsyncMock()
    await agent._dlq.init()

    agent._sn.patch_status.return_value = PatchOutcome.SUCCESS
    agent._llm.extract_shift.return_value = _high_confidence_result()
    agent._sn.write_parsed_requirement.return_value = (WriteOutcome.ERROR, None)

    # Push 3 records — at threshold
    for i in range(3):
        await agent._process_record(_make_record(sys_id=f"sys-{i}", req_id=f"req-{i}"))

    assert await agent._dlq.depth() == 3


# ------------------------------------------------------------------ ER-02b: reconciliation

@pytest.mark.asyncio
async def test_er02b_dlq_reconciliation_emits_event_and_clears_entry(tmp_path):
    """ER-02b: Reconciliation cron retries DLQ entry; on success emits event and clears queue."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    req = ParsedShiftRequirement(
        u_shift_request_id="req-001",
        u_specialty_code="ICU_RN",
        u_datetime_start=_FUTURE,
        u_datetime_end=_FUTURE_END,
        u_location_id="ST_DAVIDS_NORTH",
        u_credentials=["BLS"],
        u_confidence_score=0.95,
        u_parse_method=ParseMethod.LLM_AUTO,
        u_parsed_by="AGENT",
    )
    await agent._dlq.push("req-001", "write_parsed_requirement", req.model_dump())
    assert await agent._dlq.depth() == 1

    agent._sn.write_parsed_requirement.return_value = (WriteOutcome.SUCCESS, "new-parsed-id")
    agent._sn.patch_status.return_value = PatchOutcome.SUCCESS

    await agent._reconcile_dead_letter()

    assert await agent._dlq.depth() == 0
    agent._events.emit_shift_parsed.assert_called_once()
    shift_id, req_id = agent._events.emit_shift_parsed.call_args[0]
    assert shift_id == "req-001"
    assert req_id == "new-parsed-id"


@pytest.mark.asyncio
async def test_er02b_dlq_reconciliation_increments_retry_on_failure(tmp_path):
    """ER-02b: Reconciliation cron increments retry_count when write still fails."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    req = ParsedShiftRequirement(
        u_shift_request_id="req-002",
        u_specialty_code="ICU_RN",
        u_datetime_start=_FUTURE,
        u_datetime_end=_FUTURE_END,
        u_location_id="ST_DAVIDS_NORTH",
        u_credentials=[],
        u_confidence_score=0.90,
        u_parse_method=ParseMethod.LLM_AUTO,
        u_parsed_by="AGENT",
    )
    await agent._dlq.push("req-002", "write_parsed_requirement", req.model_dump())

    agent._sn.write_parsed_requirement.return_value = (WriteOutcome.ERROR, None)

    await agent._reconcile_dead_letter()

    # Entry still in DLQ; retry_count incremented
    records = await agent._dlq.pop_batch(10)
    assert len(records) == 1
    assert records[0].retry_count == 1
    agent._events.emit_shift_parsed.assert_not_called()


# ------------------------------------------------------------------ HP-01

@pytest.mark.asyncio
async def test_hp01_bp2_auto_proceed_parsed_status_and_event(tmp_path):
    """HP-01 (P0): High-confidence parse → status PARSED; shift_parsed event emitted once."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    agent._sn.patch_status.return_value = PatchOutcome.SUCCESS
    agent._llm.extract_shift.return_value = _high_confidence_result()
    agent._sn.write_parsed_requirement.return_value = (WriteOutcome.SUCCESS, "parsed-req-001")

    await agent._process_record(_make_record())

    all_statuses = [c[0][1] for c in agent._sn.patch_status.call_args_list]
    assert ShiftRequestStatus.PARSING in all_statuses
    assert ShiftRequestStatus.PARSED in all_statuses

    agent._events.emit_shift_parsed.assert_called_once_with("req-001", "parsed-req-001")
    agent._hitl.write_entry.assert_not_called()


@pytest.mark.asyncio
async def test_hp01_no_duplicate_events_on_bp2_path(tmp_path):
    """HP-01 (P0): Exactly one shift_parsed event emitted on the BP2 path."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    agent._sn.patch_status.return_value = PatchOutcome.SUCCESS
    agent._llm.extract_shift.return_value = _high_confidence_result()
    agent._sn.write_parsed_requirement.return_value = (WriteOutcome.SUCCESS, "parsed-req-001")

    await agent._process_record(_make_record())

    assert agent._events.emit_shift_parsed.call_count == 1


# ------------------------------------------------------------------ HP-02

@pytest.mark.asyncio
async def test_hp02_ambiguous_location_routes_to_human_review(tmp_path):
    """HP-02 (P0): Ambiguous location → HITLQueueEntry written with AMBIGUOUS_LOCATION failure reason."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    agent._sn.patch_status.return_value = PatchOutcome.SUCCESS
    agent._llm.extract_shift.return_value = _ambiguous_location_result()
    agent._hitl.write_entry.return_value = (HITLWriteOutcome.SUCCESS, "hitl-001")

    await agent._process_record(_make_record())

    all_statuses = [c[0][1] for c in agent._sn.patch_status.call_args_list]
    assert ShiftRequestStatus.HUMAN_REVIEW in all_statuses
    assert ShiftRequestStatus.PARSED not in all_statuses

    agent._hitl.write_entry.assert_called_once()
    hitl_entry = agent._hitl.write_entry.call_args[0][0]
    assert hitl_entry.u_failure_reason == HITLFailureReason.AMBIGUOUS_LOCATION
    assert hitl_entry.u_raw_text == _make_record().u_raw_text

    agent._events.emit_shift_parsed.assert_not_called()


@pytest.mark.asyncio
async def test_hp02_partial_parse_pre_fills_hitl_entry(tmp_path):
    """HP-02: Partial parse (specialty + credential) attached to HITL entry for coordinator."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    agent._sn.patch_status.return_value = PatchOutcome.SUCCESS
    agent._llm.extract_shift.return_value = _ambiguous_location_result()
    agent._hitl.write_entry.return_value = (HITLWriteOutcome.SUCCESS, "hitl-002")

    await agent._process_record(_make_record())

    hitl_entry = agent._hitl.write_entry.call_args[0][0]
    assert hitl_entry.u_partial_parse is not None
    assert hitl_entry.u_partial_parse["specialty_code"] == "ED_RN"


# ------------------------------------------------------------------ LLM unavailable

@pytest.mark.asyncio
async def test_llm_unavailable_routes_to_human_review_with_null_partial_parse(tmp_path):
    """Failure Mode 1: LLM unavailable → HUMAN_REVIEW with LLM_UNAVAILABLE; partial_parse = null."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    agent._sn.patch_status.return_value = PatchOutcome.SUCCESS
    agent._llm.extract_shift.side_effect = LLMUnavailableError("LLM overloaded")
    agent._hitl.write_entry.return_value = (HITLWriteOutcome.SUCCESS, "hitl-003")

    await agent._process_record(_make_record())

    all_statuses = [c[0][1] for c in agent._sn.patch_status.call_args_list]
    assert ShiftRequestStatus.HUMAN_REVIEW in all_statuses

    hitl_entry = agent._hitl.write_entry.call_args[0][0]
    assert hitl_entry.u_failure_reason == HITLFailureReason.LLM_UNAVAILABLE
    assert hitl_entry.u_partial_parse is None


# ------------------------------------------------------------------ consecutive failure counter

@pytest.mark.asyncio
async def test_consecutive_failure_counter_increments_on_unavailable(tmp_path):
    """§7.4 Fallback: consecutive failure counter increments on LLM unavailability."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    agent._sn.patch_status.return_value = PatchOutcome.SUCCESS
    agent._llm.extract_shift.side_effect = LLMUnavailableError("overloaded")
    agent._hitl.write_entry.return_value = (HITLWriteOutcome.SUCCESS, "hitl-x")

    await agent._process_record(_make_record(sys_id="s1", req_id="r1"))
    assert agent._consecutive_failures == 1

    await agent._process_record(_make_record(sys_id="s2", req_id="r2"))
    assert agent._consecutive_failures == 2


@pytest.mark.asyncio
async def test_consecutive_failure_counter_resets_on_success(tmp_path):
    """§7.4: Consecutive failure counter resets to 0 on successful LLM extraction."""
    agent = _make_agent(tmp_path)
    await agent._dlq.init()

    agent._sn.patch_status.return_value = PatchOutcome.SUCCESS
    agent._llm.extract_shift.side_effect = LLMUnavailableError("overloaded")
    agent._hitl.write_entry.return_value = (HITLWriteOutcome.SUCCESS, "hitl-x")

    await agent._process_record(_make_record(sys_id="s1", req_id="r1"))
    assert agent._consecutive_failures == 1

    # Next call succeeds
    agent._llm.extract_shift.side_effect = None
    agent._llm.extract_shift.return_value = _high_confidence_result()
    agent._sn.write_parsed_requirement.return_value = (WriteOutcome.SUCCESS, "parsed-id")

    await agent._process_record(_make_record(sys_id="s2", req_id="r2"))
    assert agent._consecutive_failures == 0
