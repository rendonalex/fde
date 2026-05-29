from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from hitl_service import db as hitl_db

DB_PATH = os.getenv("HITL_DB_PATH", "hitl_queue.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await hitl_db.init_db(DB_PATH)
    yield


app = FastAPI(title="MedFlex HITL Queue Service", lifespan=lifespan)


class HITLEntryRequest(BaseModel):
    shift_request_id: str
    raw_text: str
    partial_parse: Optional[dict] = None
    failure_reason: str
    confidence_score: Optional[float] = None
    received_at: Optional[str] = None


@app.post("/internal/api/v1/hitl-queue", status_code=201)
async def create_hitl_entry(body: HITLEntryRequest):
    existing = await hitl_db.get_existing(DB_PATH, body.shift_request_id)
    if existing:
        raise HTTPException(status_code=409, detail={"hitl_entry_id": existing["hitl_entry_id"], "message": "already exists"})

    result = await hitl_db.insert_entry(DB_PATH, body.model_dump())
    return result


@app.get("/internal/api/v1/hitl-queue")
async def list_hitl_entries(status: Optional[str] = None):
    entries = await hitl_db.list_entries(DB_PATH, status)
    return {"result": entries, "count": len(entries)}


@app.get("/internal/api/v1/hitl-queue/{hitl_entry_id}")
async def get_hitl_entry(hitl_entry_id: str):
    entries = await hitl_db.list_entries(DB_PATH)
    for e in entries:
        if e["hitl_entry_id"] == hitl_entry_id:
            return e
    raise HTTPException(status_code=404, detail="not found")


@app.get("/health")
async def health():
    return {"status": "ok"}
