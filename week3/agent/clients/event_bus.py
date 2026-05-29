from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from typing import Optional

import httpx


class EventBusClient:
    def __init__(self, event_bus_url: Optional[str] = None) -> None:
        self._url = event_bus_url

    async def emit_shift_parsed(
        self, shift_request_id: str, parsed_requirement_id: str
    ) -> None:
        event = {
            "event_type": "shift_parsed",
            "shift_request_id": shift_request_id,
            "parsed_requirement_id": parsed_requirement_id,
            "emitted_at": datetime.now(timezone.utc).isoformat(),
        }

        if self._url:
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    await client.post(self._url, json=event)
            except Exception as exc:
                print(
                    json.dumps({"level": "WARN", "message": f"Event bus POST failed: {exc}", "event": event}),
                    file=sys.stderr,
                )
        else:
            print(
                json.dumps({"level": "INFO", "message": "shift_parsed event (no bus configured)", "event": event}),
                file=sys.stderr,
            )
