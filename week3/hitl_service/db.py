from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import aiosqlite

_CREATE = """
CREATE TABLE IF NOT EXISTS hitl_queue (
    hitl_entry_id       TEXT PRIMARY KEY,
    shift_request_id    TEXT UNIQUE NOT NULL,
    raw_text            TEXT NOT NULL,
    partial_parse       TEXT,
    failure_reason      TEXT NOT NULL,
    confidence_score    REAL,
    status              TEXT NOT NULL DEFAULT 'PENDING',
    assigned_to         TEXT,
    received_at         TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    completed_at        TEXT
)
"""


async def init_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(_CREATE)
        await db.commit()


async def insert_entry(db_path: str, body: dict) -> dict:
    hitl_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """INSERT INTO hitl_queue
               (hitl_entry_id, shift_request_id, raw_text, partial_parse, failure_reason,
                confidence_score, status, received_at, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                hitl_id,
                body["shift_request_id"],
                body["raw_text"],
                json.dumps(body.get("partial_parse")),
                body["failure_reason"],
                body.get("confidence_score"),
                "PENDING",
                body.get("received_at") or now,
                now,
            ),
        )
        await db.commit()
    return {"hitl_entry_id": hitl_id, "shift_request_id": body["shift_request_id"], "status": "PENDING", "created_at": now}


async def get_existing(db_path: str, shift_request_id: str) -> dict | None:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM hitl_queue WHERE shift_request_id = ?", (shift_request_id,)
        )
        row = await cursor.fetchone()
    if row is None:
        return None
    return dict(row)


async def list_entries(db_path: str, status: str | None = None) -> list[dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        if status:
            cursor = await db.execute("SELECT * FROM hitl_queue WHERE status = ?", (status,))
        else:
            cursor = await db.execute("SELECT * FROM hitl_queue ORDER BY created_at DESC")
        rows = await cursor.fetchall()
    return [dict(r) for r in rows]
