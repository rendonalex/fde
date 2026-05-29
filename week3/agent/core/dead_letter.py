from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Optional

import aiosqlite

from agent.models import DeadLetterRecord

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS dead_letter_queue (
    record_id     TEXT PRIMARY KEY,
    shift_request_id TEXT NOT NULL,
    operation     TEXT NOT NULL,
    payload       TEXT NOT NULL,
    retry_count   INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL,
    last_attempted_at TEXT
)
"""


class DeadLetterQueue:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    async def init(self) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(_CREATE_TABLE)
            await db.commit()

    async def push(
        self, shift_request_id: str, operation: str, payload: dict
    ) -> str:
        record_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "INSERT INTO dead_letter_queue VALUES (?,?,?,?,0,?,NULL)",
                (record_id, shift_request_id, operation, json.dumps(payload), now),
            )
            await db.commit()
        return record_id

    async def pop_batch(self, limit: int = 10) -> list[DeadLetterRecord]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM dead_letter_queue ORDER BY created_at ASC LIMIT ?",
                (limit,),
            )
            rows = await cursor.fetchall()
        return [
            DeadLetterRecord(
                record_id=row["record_id"],
                shift_request_id=row["shift_request_id"],
                operation=row["operation"],
                payload=json.loads(row["payload"]),
                retry_count=row["retry_count"],
                created_at=datetime.fromisoformat(row["created_at"]),
                last_attempted_at=(
                    datetime.fromisoformat(row["last_attempted_at"])
                    if row["last_attempted_at"]
                    else None
                ),
            )
            for row in rows
        ]

    async def mark_completed(self, record_id: str) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "DELETE FROM dead_letter_queue WHERE record_id = ?", (record_id,)
            )
            await db.commit()

    async def increment_retry(self, record_id: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "UPDATE dead_letter_queue SET retry_count = retry_count + 1, last_attempted_at = ? WHERE record_id = ?",
                (now, record_id),
            )
            await db.commit()

    async def depth(self) -> int:
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM dead_letter_queue")
            row = await cursor.fetchone()
            return row[0] if row else 0
