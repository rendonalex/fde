from __future__ import annotations

import asyncio
import json
import time
from typing import Optional

import httpx
from pydantic import ValidationError

from agent.models import LLMExtractionResult

_RETRY_DELAYS = [4, 8, 16]
_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


class LLMUnavailableError(Exception):
    pass


class LLMAuthError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        super().__init__(f"LLM auth error {status_code}: {detail}")


class LLMHaltError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        super().__init__(f"LLM halt error {status_code}: {detail}")


class InvalidJSONError(Exception):
    pass


class LLMClient:
    def __init__(self, api_key: str, system_prompt: str, timeout_seconds: int = 30) -> None:
        self._api_key = api_key
        self._system_prompt = system_prompt
        self._timeout = timeout_seconds

    async def extract_shift(self, raw_text: str) -> LLMExtractionResult:
        for json_attempt in range(2):
            raw_content = await self._call_api(raw_text)
            try:
                cleaned = _extract_json(raw_content)
                data = json.loads(cleaned)
                return LLMExtractionResult.model_validate(data)
            except (json.JSONDecodeError, ValidationError, KeyError):
                if json_attempt == 1:
                    raise InvalidJSONError(raw_content[:300])
        raise InvalidJSONError("unreachable")

    async def _call_api(self, raw_text: str) -> str:
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": "claude-sonnet-4-6",
            "max_tokens": 600,
            "system": self._system_prompt,
            "messages": [
                {"role": "user", "content": f"Parse the following hospital shift request:\n\n{raw_text}"}
            ],
        }

        start = time.monotonic()
        attempt = 0

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            while True:
                try:
                    resp = await client.post(_ANTHROPIC_URL, headers=headers, json=body)
                except httpx.TimeoutException:
                    elapsed = time.monotonic() - start
                    if elapsed >= 60:
                        raise LLMUnavailableError(f"LLM timeout after {elapsed:.0f}s")
                    attempt += 1
                    if attempt > 3:
                        raise LLMUnavailableError("LLM timeout on all retries")
                    await asyncio.sleep(_RETRY_DELAYS[attempt - 1])
                    continue

                if resp.status_code == 200:
                    data = resp.json()
                    return data["content"][0]["text"]

                if resp.status_code == 401:
                    raise LLMAuthError(401, resp.text)

                if resp.status_code in (400, 422):
                    raise LLMHaltError(resp.status_code, resp.text[:200])

                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("retry-after", "60"))
                    await asyncio.sleep(retry_after)
                    continue

                # 529 or 5xx
                elapsed = time.monotonic() - start
                if elapsed >= 60:
                    raise LLMUnavailableError(f"LLM unavailable for {elapsed:.0f}s")
                attempt += 1
                if attempt > 3:
                    raise LLMUnavailableError(f"LLM failed after {attempt} attempts")
                await asyncio.sleep(_RETRY_DELAYS[attempt - 1])


def _extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        inner = lines[1:] if len(lines) > 1 else lines
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        text = "\n".join(inner).strip()
    return text
