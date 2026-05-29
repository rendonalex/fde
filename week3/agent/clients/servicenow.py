from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import httpx

from agent.models import ParsedShiftRequirement, ShiftRequest, ShiftRequestStatus, SourceType

_RETRY_DELAYS = [4, 8, 16]


class PatchOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    ALREADY_SET = "ALREADY_SET"
    NOT_FOUND = "NOT_FOUND"
    AUTH_ERROR = "AUTH_ERROR"
    ERROR = "ERROR"


class WriteOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    DUPLICATE = "DUPLICATE"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    ERROR = "ERROR"


class ServiceNowClient:
    def __init__(self, instance: str, read_token: str, write_token: str) -> None:
        base = f"https://{instance}/api/now/table"
        self._shift_url = f"{base}/u_shift_request"
        self._parsed_url = f"{base}/u_parsed_shift_requirement"
        self._read_headers = {"Authorization": f"Bearer {read_token}", "Accept": "application/json"}
        self._write_headers = {
            "Authorization": f"Bearer {write_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def poll_queued_records(self, limit: int = 10) -> list[ShiftRequest]:
        params = {
            "sysparm_query": "u_status=QUEUED",
            "sysparm_limit": str(limit),
            "sysparm_fields": "sys_id,u_shift_request_id,u_raw_text,u_hospital_id,u_source_type,u_received_at",
            "sysparm_order_by": "u_received_at",
        }
        async with httpx.AsyncClient(timeout=10) as client:
            for attempt, delay in enumerate([0] + _RETRY_DELAYS):
                if delay:
                    import asyncio
                    await asyncio.sleep(delay)
                try:
                    resp = await client.get(self._shift_url, headers=self._read_headers, params=params)
                except httpx.TimeoutException:
                    if attempt < len(_RETRY_DELAYS):
                        continue
                    return []

                if resp.status_code == 200:
                    return [_parse_shift_record(r) for r in resp.json().get("result", [])]
                if resp.status_code in (401, 403):
                    raise RuntimeError(f"ServiceNow auth error {resp.status_code} on poll")
                if resp.status_code == 429:
                    import asyncio
                    await asyncio.sleep(60)
                    continue
                if resp.status_code >= 500 and attempt < len(_RETRY_DELAYS):
                    continue
                return []
        return []

    async def patch_status(
        self,
        sys_id: str,
        status: ShiftRequestStatus,
        failure_reason: Optional[str] = None,
        parsed_at: Optional[datetime] = None,
    ) -> PatchOutcome:
        body: dict = {"u_status": status.value}
        if failure_reason:
            body["u_failure_reason"] = failure_reason
        if parsed_at:
            body["u_parsed_at"] = parsed_at.astimezone(timezone.utc).isoformat()

        url = f"{self._shift_url}/{sys_id}"
        async with httpx.AsyncClient(timeout=10) as client:
            for attempt, delay in enumerate([0] + _RETRY_DELAYS):
                if delay:
                    import asyncio
                    await asyncio.sleep(delay)
                try:
                    resp = await client.patch(url, headers=self._write_headers, json=body)
                except httpx.TimeoutException:
                    if attempt < len(_RETRY_DELAYS):
                        continue
                    return PatchOutcome.ERROR

                if resp.status_code == 200:
                    return PatchOutcome.SUCCESS
                if resp.status_code == 409:
                    return PatchOutcome.ALREADY_SET
                if resp.status_code == 404:
                    return PatchOutcome.NOT_FOUND
                if resp.status_code in (401, 403):
                    return PatchOutcome.AUTH_ERROR
                if resp.status_code >= 500 and attempt < len(_RETRY_DELAYS):
                    continue
                return PatchOutcome.ERROR
        return PatchOutcome.ERROR

    async def write_parsed_requirement(
        self, req: ParsedShiftRequirement
    ) -> tuple[WriteOutcome, Optional[str]]:
        body = req.model_dump()
        body["u_credentials"] = req.u_credentials

        async with httpx.AsyncClient(timeout=15) as client:
            for attempt, delay in enumerate([0] + _RETRY_DELAYS):
                if delay:
                    import asyncio
                    await asyncio.sleep(delay)
                try:
                    resp = await client.post(self._parsed_url, headers=self._write_headers, json=body)
                except httpx.TimeoutException:
                    if attempt < len(_RETRY_DELAYS):
                        continue
                    return WriteOutcome.ERROR, None

                if resp.status_code == 201:
                    parsed_id = resp.json().get("result", {}).get("u_parsed_requirement_id")
                    return WriteOutcome.SUCCESS, parsed_id
                if resp.status_code == 409:
                    existing_id = resp.json().get("result", {}).get("u_parsed_requirement_id")
                    return WriteOutcome.DUPLICATE, existing_id
                if resp.status_code == 422:
                    return WriteOutcome.VALIDATION_ERROR, None
                if resp.status_code in (401, 403):
                    return WriteOutcome.AUTH_ERROR, None
                if resp.status_code >= 500 and attempt < len(_RETRY_DELAYS):
                    continue
                return WriteOutcome.ERROR, None
        return WriteOutcome.ERROR, None

    async def get_stale_parsing_records(self, older_than_minutes: int = 5) -> list[str]:
        cutoff = datetime.now(timezone.utc)
        from datetime import timedelta
        cutoff -= timedelta(minutes=older_than_minutes)
        query = f"u_status=PARSING^sys_updated_at<{cutoff.strftime('%Y-%m-%d %H:%M:%S')}"
        params = {
            "sysparm_query": query,
            "sysparm_fields": "sys_id",
            "sysparm_limit": "50",
        }
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.get(self._shift_url, headers=self._read_headers, params=params)
                if resp.status_code == 200:
                    return [r["sys_id"] for r in resp.json().get("result", [])]
            except Exception:
                pass
        return []


def _parse_shift_record(raw: dict) -> ShiftRequest:
    received_at = raw.get("u_received_at", "")
    try:
        dt = datetime.fromisoformat(received_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        dt = datetime.now(timezone.utc)

    return ShiftRequest(
        sys_id=raw["sys_id"],
        u_shift_request_id=raw.get("u_shift_request_id", raw["sys_id"]),
        u_source_type=SourceType(raw.get("u_source_type", "EMAIL")),
        u_raw_text=raw.get("u_raw_text", ""),
        u_hospital_id=raw.get("u_hospital_id", ""),
        u_status=ShiftRequestStatus.QUEUED,
        u_received_at=dt,
    )
