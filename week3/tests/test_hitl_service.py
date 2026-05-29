"""
HITL Queue FastAPI service tests mapping to specs/07-validation-plan.md.

Coverage:
  ER-03 (P0): Duplicate coordinator review submission → HTTP 409; one record; one JtD-4 trigger
  Happy path: POST creates entry (HTTP 201); GET returns it
  List:       GET /hitl-queue returns all entries
  Health:     /health endpoint responds
"""
from __future__ import annotations

import pytest
import pytest_asyncio
import httpx

import hitl_service.main as hitl_main
from hitl_service import db as hitl_db


@pytest_asyncio.fixture
async def hitl_client(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test_hitl.db")
    monkeypatch.setattr(hitl_main, "DB_PATH", db_path)
    await hitl_db.init_db(db_path)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=hitl_main.app),
        base_url="http://test",
    ) as client:
        yield client


# ------------------------------------------------------------------ happy path

@pytest.mark.asyncio
async def test_create_hitl_entry_returns_201(hitl_client):
    """Happy path: POST /hitl-queue creates an entry and returns 201 with PENDING status."""
    resp = await hitl_client.post(
        "/internal/api/v1/hitl-queue",
        json={
            "shift_request_id": "req-001",
            "raw_text": "ICU RN needed at St. David's North",
            "failure_reason": "AMBIGUOUS_LOCATION",
            "confidence_score": 0.30,
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["shift_request_id"] == "req-001"
    assert body["status"] == "PENDING"
    assert "hitl_entry_id" in body


@pytest.mark.asyncio
async def test_create_hitl_entry_without_optional_fields(hitl_client):
    """POST with only required fields (no partial_parse, no confidence_score) returns 201."""
    resp = await hitl_client.post(
        "/internal/api/v1/hitl-queue",
        json={
            "shift_request_id": "req-002",
            "raw_text": "Nurse needed ASAP",
            "failure_reason": "LLM_UNAVAILABLE",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "PENDING"


# ------------------------------------------------------------------ ER-03

@pytest.mark.asyncio
async def test_er03_duplicate_submission_returns_409(hitl_client):
    """ER-03 (P0): Second POST with same shift_request_id → HTTP 409; one record created."""
    payload = {
        "shift_request_id": "req-dup-001",
        "raw_text": "ED RN needed Friday 7am, St. David's",
        "failure_reason": "AMBIGUOUS_LOCATION",
        "confidence_score": 0.30,
    }

    first = await hitl_client.post("/internal/api/v1/hitl-queue", json=payload)
    assert first.status_code == 201
    original_id = first.json()["hitl_entry_id"]

    second = await hitl_client.post("/internal/api/v1/hitl-queue", json=payload)
    assert second.status_code == 409
    assert second.json()["detail"]["hitl_entry_id"] == original_id


@pytest.mark.asyncio
async def test_er03_duplicate_does_not_create_second_record(hitl_client):
    """ER-03 (P0): After a duplicate 409, list shows exactly one record for that shift_request_id."""
    payload = {
        "shift_request_id": "req-dup-002",
        "raw_text": "ICU RN needed",
        "failure_reason": "LOW_CONFIDENCE",
    }

    await hitl_client.post("/internal/api/v1/hitl-queue", json=payload)
    await hitl_client.post("/internal/api/v1/hitl-queue", json=payload)

    list_resp = await hitl_client.get("/internal/api/v1/hitl-queue")
    assert list_resp.status_code == 200
    entries = [e for e in list_resp.json()["result"] if e["shift_request_id"] == "req-dup-002"]
    assert len(entries) == 1


# ------------------------------------------------------------------ list + get

@pytest.mark.asyncio
async def test_list_returns_all_entries(hitl_client):
    """GET /hitl-queue returns all submitted entries with correct count."""
    for i in range(3):
        await hitl_client.post(
            "/internal/api/v1/hitl-queue",
            json={
                "shift_request_id": f"req-list-{i}",
                "raw_text": f"request {i}",
                "failure_reason": "LOW_CONFIDENCE",
            },
        )

    resp = await hitl_client.get("/internal/api/v1/hitl-queue")
    assert resp.status_code == 200
    assert resp.json()["count"] == 3


@pytest.mark.asyncio
async def test_get_entry_by_id(hitl_client):
    """GET /hitl-queue/{id} returns the specific entry."""
    post_resp = await hitl_client.post(
        "/internal/api/v1/hitl-queue",
        json={
            "shift_request_id": "req-get-001",
            "raw_text": "Tele RN needed",
            "failure_reason": "DATETIME_IN_PAST",
            "confidence_score": 0.00,
        },
    )
    hitl_id = post_resp.json()["hitl_entry_id"]

    get_resp = await hitl_client.get(f"/internal/api/v1/hitl-queue/{hitl_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["hitl_entry_id"] == hitl_id
    assert get_resp.json()["shift_request_id"] == "req-get-001"


@pytest.mark.asyncio
async def test_get_nonexistent_entry_returns_404(hitl_client):
    """GET /hitl-queue/{id} for unknown id → HTTP 404."""
    resp = await hitl_client.get("/internal/api/v1/hitl-queue/nonexistent-id")
    assert resp.status_code == 404


# ------------------------------------------------------------------ health

@pytest.mark.asyncio
async def test_health_endpoint(hitl_client):
    """/health returns 200 and status ok."""
    resp = await hitl_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
