from __future__ import annotations

from enum import Enum
from typing import Optional

import httpx

from agent.models import HITLQueueEntry

_RETRY_DELAYS = [4, 8, 16]


class HITLWriteOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    DUPLICATE = "DUPLICATE"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    ERROR = "ERROR"


class HITLQueueClient:
    def __init__(self, base_url: str, service_token: str) -> None:
        self._url = f"{base_url.rstrip('/')}/internal/api/v1/hitl-queue"
        self._headers = {
            "Authorization": f"Bearer {service_token}",
            "Content-Type": "application/json",
        }

    async def write_entry(
        self, entry: HITLQueueEntry, received_at: str
    ) -> tuple[HITLWriteOutcome, Optional[str]]:
        body = {
            "shift_request_id": entry.u_shift_request_id,
            "raw_text": entry.u_raw_text,
            "partial_parse": entry.u_partial_parse,
            "failure_reason": entry.u_failure_reason.value,
            "confidence_score": entry.u_confidence_score,
            "received_at": received_at,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            for attempt, delay in enumerate([0] + _RETRY_DELAYS):
                if delay:
                    import asyncio
                    await asyncio.sleep(delay)
                try:
                    resp = await client.post(self._url, headers=self._headers, json=body)
                except httpx.TimeoutException:
                    if attempt < len(_RETRY_DELAYS):
                        continue
                    return HITLWriteOutcome.ERROR, None

                if resp.status_code == 201:
                    hitl_id = resp.json().get("hitl_entry_id")
                    return HITLWriteOutcome.SUCCESS, hitl_id
                if resp.status_code == 409:
                    return HITLWriteOutcome.DUPLICATE, None
                if resp.status_code == 422:
                    return HITLWriteOutcome.VALIDATION_ERROR, None
                if resp.status_code >= 500 and attempt < len(_RETRY_DELAYS):
                    continue
                return HITLWriteOutcome.ERROR, None
        return HITLWriteOutcome.ERROR, None
