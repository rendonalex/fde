from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from typing import Optional

import httpx


async def alert_ops(
    message: str,
    level: str = "ERROR",
    slack_webhook_url: Optional[str] = None,
    context: Optional[dict] = None,
) -> None:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "service": "shift-intake-parser",
        "message": message,
        **(context or {}),
    }
    print(json.dumps(payload), file=sys.stderr, flush=True)

    if slack_webhook_url:
        text = f"[{level}] shift-intake-parser: {message}"
        if context:
            text += f"\n```{json.dumps(context, indent=2)}```"
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                await client.post(slack_webhook_url, json={"text": text})
        except Exception:
            pass
