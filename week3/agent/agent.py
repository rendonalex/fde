from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional

from agent.alerts import alert_ops
from agent.clients.event_bus import EventBusClient
from agent.clients.hitl_queue import HITLQueueClient, HITLWriteOutcome
from agent.clients.llm import (
    InvalidJSONError,
    LLMAuthError,
    LLMClient,
    LLMHaltError,
    LLMUnavailableError,
)
from agent.clients.servicenow import PatchOutcome, ServiceNowClient, WriteOutcome
from agent.config import DomainConfig, Settings
from agent.core.dead_letter import DeadLetterQueue
from agent.core.prompt import build_system_prompt
from agent.core.scorer import compute_confidence_score
from agent.core.validator import ValidationResult, build_partial_parse, validate_llm_response
from agent.models import (
    HITLFailureReason,
    HITLQueueEntry,
    LLMExtractionResult,
    ParsedShiftRequirement,
    ParseMethod,
    ShiftRequest,
    ShiftRequestStatus,
)


class ShiftIntakeParserAgent:
    def __init__(self, settings: Settings, domain: DomainConfig) -> None:
        self._settings = settings
        self._domain = domain
        self._sn = ServiceNowClient(
            settings.servicenow_instance,
            settings.servicenow_read_token,
            settings.servicenow_write_token,
        )
        self._llm: Optional[LLMClient] = None
        self._hitl = HITLQueueClient(settings.hitl_queue_url, settings.system_service_token)
        self._events = EventBusClient(settings.event_bus_url)
        self._dlq = DeadLetterQueue(settings.dead_letter_db_path)
        self._consecutive_failures = 0
        self._failure_lock = asyncio.Lock()
        self._halt = False

    async def start(self) -> None:
        await self._dlq.init()
        system_prompt = build_system_prompt(self._domain)
        self._llm = LLMClient(
            self._settings.anthropic_api_key,
            system_prompt,
            self._settings.llm_timeout_seconds,
        )
        await asyncio.gather(
            self._poll_loop(),
            self._reconciliation_loop(),
        )

    # ------------------------------------------------------------------ poll

    async def _poll_loop(self) -> None:
        while not self._halt:
            try:
                records = await self._sn.poll_queued_records(self._settings.poll_batch_size)
                if records:
                    await asyncio.gather(*[self._process_record(r) for r in records])
            except RuntimeError as exc:
                await alert_ops(
                    str(exc),
                    slack_webhook_url=self._settings.slack_webhook_url,
                )
                self._halt = True
                return
            except Exception as exc:
                await alert_ops(
                    f"Poll loop error: {exc}",
                    slack_webhook_url=self._settings.slack_webhook_url,
                )
            await asyncio.sleep(self._settings.poll_interval_seconds)

    # ---------------------------------------------------------- record processing

    async def _process_record(self, record: ShiftRequest) -> None:
        # MT-1.1: advisory lock
        outcome = await self._sn.patch_status(record.sys_id, ShiftRequestStatus.PARSING)
        if outcome == PatchOutcome.AUTH_ERROR:
            await alert_ops(
                "ServiceNow write auth error",
                slack_webhook_url=self._settings.slack_webhook_url,
            )
            self._halt = True
            return
        if outcome != PatchOutcome.SUCCESS:
            return

        # MT-1.2: LLM extraction
        try:
            result = await self._llm.extract_shift(record.u_raw_text)
            await self._reset_failure_counter()
        except LLMAuthError as exc:
            await alert_ops(
                f"LLM auth failure — halting: {exc}",
                slack_webhook_url=self._settings.slack_webhook_url,
            )
            self._halt = True
            return
        except LLMHaltError as exc:
            await self._route_parse_failed(record, f"LLM error {exc.status_code}: {exc}")
            return
        except LLMUnavailableError:
            await self._increment_failure_counter()
            await self._route_human_review(record, HITLFailureReason.LLM_UNAVAILABLE, None)
            return
        except InvalidJSONError:
            await self._increment_failure_counter()
            await self._route_human_review(record, HITLFailureReason.INVALID_JSON, None)
            return

        # MT-1.3: validate
        validation = validate_llm_response(result, self._domain)

        # MT-1.4a: confidence
        confidence = compute_confidence_score(validation.result)

        # Determine failure reason for BP1 routing
        if validation.failure_reason == HITLFailureReason.DATETIME_IN_PAST:
            await self._route_human_review(record, HITLFailureReason.DATETIME_IN_PAST, validation.result, confidence)
            return

        if validation.failure_reason == HITLFailureReason.AMBIGUOUS_LOCATION:
            await self._route_human_review(record, HITLFailureReason.AMBIGUOUS_LOCATION, validation.result, confidence)
            return

        if confidence < self._settings.confidence_threshold:
            await self._route_human_review(record, HITLFailureReason.LOW_CONFIDENCE, validation.result, confidence)
            return

        # MT-1.4b: BP2 auto-proceed
        await self._route_auto_proceed(record, validation.result, confidence)

    # ---------------------------------------------------------- routing helpers

    async def _route_auto_proceed(
        self, record: ShiftRequest, result: LLMExtractionResult, confidence: float
    ) -> None:
        req = ParsedShiftRequirement(
            u_shift_request_id=record.u_shift_request_id,
            u_specialty_code=result.specialty_code,
            u_datetime_start=result.datetime_start or "",
            u_datetime_end=result.datetime_end or "",
            u_location_id=result.location_id,
            u_credentials=result.credentials,
            u_confidence_score=round(confidence, 2),
            u_parse_method=ParseMethod.LLM_AUTO,
            u_parsed_by="AGENT",
        )

        write_outcome, parsed_id = await self._sn.write_parsed_requirement(req)

        if write_outcome == WriteOutcome.VALIDATION_ERROR:
            await self._route_parse_failed(record, "ParsedShiftRequirement validation error (HTTP 422)")
            return

        if write_outcome == WriteOutcome.AUTH_ERROR:
            await alert_ops(
                "ServiceNow write auth error on ParsedShiftRequirement",
                slack_webhook_url=self._settings.slack_webhook_url,
            )
            self._halt = True
            return

        if write_outcome in (WriteOutcome.ERROR,):
            # MT-7.3 ordering constraint: do NOT emit event; push to DLQ
            await self._dlq.push(
                record.u_shift_request_id,
                "write_parsed_requirement",
                req.model_dump(),
            )
            await self._check_dlq_depth()
            return

        # DUPLICATE (409) treated as success — use existing parsed_id
        if write_outcome == WriteOutcome.DUPLICATE and parsed_id is None:
            parsed_id = f"existing-{record.u_shift_request_id}"

        now = datetime.now(timezone.utc)
        await self._sn.patch_status(
            record.sys_id,
            ShiftRequestStatus.PARSED,
            parsed_at=now,
        )

        # MT-1.7: emit event only after write confirmed
        await self._events.emit_shift_parsed(record.u_shift_request_id, parsed_id or "")

    async def _route_human_review(
        self,
        record: ShiftRequest,
        reason: HITLFailureReason,
        result: Optional[LLMExtractionResult],
        confidence: Optional[float] = None,
    ) -> None:
        # §7.5: PATCH status first, then write HITL entry
        patch = await self._sn.patch_status(
            record.sys_id,
            ShiftRequestStatus.HUMAN_REVIEW,
            failure_reason=reason.value,
        )
        if patch == PatchOutcome.AUTH_ERROR:
            self._halt = True
            return

        partial = build_partial_parse(result) if result else None
        if partial and confidence is not None:
            partial["confidence_score"] = round(confidence, 2)

        entry = HITLQueueEntry(
            u_shift_request_id=record.u_shift_request_id,
            u_raw_text=record.u_raw_text,
            u_partial_parse=partial,
            u_failure_reason=reason,
            u_confidence_score=round(confidence, 2) if confidence is not None else None,
        )

        hitl_outcome, _ = await self._hitl.write_entry(
            entry, record.u_received_at.isoformat()
        )
        if hitl_outcome == HITLWriteOutcome.ERROR:
            await alert_ops(
                f"HITL queue write failed for {record.u_shift_request_id} — record is in HUMAN_REVIEW with no queue entry",
                slack_webhook_url=self._settings.slack_webhook_url,
            )

    async def _route_parse_failed(self, record: ShiftRequest, detail: str) -> None:
        await self._sn.patch_status(
            record.sys_id,
            ShiftRequestStatus.PARSE_FAILED,
            failure_reason=detail[:500],
        )
        await alert_ops(
            f"PARSE_FAILED: {record.u_shift_request_id} — {detail[:200]}",
            slack_webhook_url=self._settings.slack_webhook_url,
        )

    # ---------------------------------------------------------- reconciliation

    async def _reconciliation_loop(self) -> None:
        while not self._halt:
            await asyncio.sleep(300)
            await self._reconcile_dead_letter()
            await self._reconcile_stale_locks()

    async def _reconcile_dead_letter(self) -> None:
        records = await self._dlq.pop_batch(10)
        for dlr in records:
            if dlr.operation == "write_parsed_requirement":
                req = ParsedShiftRequirement.model_validate(dlr.payload)
                write_outcome, parsed_id = await self._sn.write_parsed_requirement(req)
                if write_outcome in (WriteOutcome.SUCCESS, WriteOutcome.DUPLICATE):
                    await self._dlq.mark_completed(dlr.record_id)
                    now = datetime.now(timezone.utc)
                    await self._sn.patch_status(
                        dlr.payload.get("sys_id", dlr.shift_request_id),
                        ShiftRequestStatus.PARSED,
                        parsed_at=now,
                    )
                    await self._events.emit_shift_parsed(
                        dlr.shift_request_id, parsed_id or ""
                    )
                else:
                    await self._dlq.increment_retry(dlr.record_id)
        await self._check_dlq_depth()

    async def _reconcile_stale_locks(self) -> None:
        stale = await self._sn.get_stale_parsing_records(older_than_minutes=5)
        for sys_id in stale:
            await self._sn.patch_status(sys_id, ShiftRequestStatus.QUEUED)

    # ---------------------------------------------------------- failure counter

    async def _increment_failure_counter(self) -> None:
        async with self._failure_lock:
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._settings.consecutive_failure_alert_threshold:
                await alert_ops(
                    f"LLM consecutive failure threshold reached ({self._consecutive_failures})",
                    slack_webhook_url=self._settings.slack_webhook_url,
                )

    async def _reset_failure_counter(self) -> None:
        async with self._failure_lock:
            self._consecutive_failures = 0

    async def _check_dlq_depth(self) -> None:
        depth = await self._dlq.depth()
        if depth >= self._settings.dead_letter_alert_threshold:
            await alert_ops(
                f"Dead-letter queue depth {depth} >= threshold {self._settings.dead_letter_alert_threshold}",
                slack_webhook_url=self._settings.slack_webhook_url,
            )
