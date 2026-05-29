"""
Pipeline integration tests — three paths

Each test makes real API calls to prove the pipeline is buildable.
Requires ANTHROPIC_API_KEY in environment.

Run:
    pytest capstone/prototype/tests/ -v
"""
import json
import os
import re
import sys
import uuid
from pathlib import Path

import pytest

# ── Path setup ────────────────────────────────────────────────────────────────
HERE     = Path(__file__).resolve().parent.parent
DEMO_DIR = HERE.parent / "demo"
sys.path.insert(0, str(DEMO_DIR))

from preprocessors import preprocess
from prompts import INTAKE_SYSTEM_PROMPT, build_triage_prompt

import anthropic

# ── Shared fixtures ────────────────────────────────────────────────────────────
MOCK_DATA = HERE.parent / "mock-data"
CODEBOOK  = str(HERE.parent / "test-data" / "criteria-codebook-mock.json")
MODEL     = "claude-haiku-4-5-20251001"

HAPPY_PATH_FILE  = MOCK_DATA / "portal-json"  / "CLM-2026-1001201.json"
ESCALATION_FILE  = MOCK_DATA / "cms1500-ocr"  / "CLM-2026-1001630.txt"
EDGE_CASE_FILE   = MOCK_DATA / "portal-json"  / "CLM-2026-1001220.json"


@pytest.fixture(scope="session")
def client():
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN not set")
    return anthropic.Anthropic(api_key=api_key)


def _extract_json(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    assert m, f"No JSON object in model output:\n{text}"
    return json.loads(m.group())


def _run_adr1(path, client):
    preprocessed = preprocess(str(path))
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=INTAKE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(preprocessed, indent=2)}],
    )
    return _extract_json(response.content[0].text)


def _run_adr4(normalized, client):
    triage_input = {
        "claim_id":            str(uuid.uuid4()),
        "source_claim_ref":    normalized.get("source_claim_ref"),
        "intake_channel":      normalized.get("intake_channel"),
        "extraction_status":   normalized.get("extraction_status"),
        "claim_type":          normalized.get("claim_type"),
        "icd10_codes":         normalized.get("icd10_codes"),
        "cpt_codes":           normalized.get("cpt_codes"),
        "prior_auth_required": normalized.get("prior_auth_required"),
        "prior_auth_number":   normalized.get("prior_auth_number"),
    }
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=build_triage_prompt(CODEBOOK),
        messages=[{"role": "user", "content": json.dumps(triage_input, indent=2)}],
    )
    return _extract_json(response.content[0].text)


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_happy_path(client):
    """
    Clean portal JSON → ADR-1 AUTO_COMPLETE → ADR-4 FAST_PATH.
    Verifies the end-to-end agentic flow for a routine, low-complexity claim.
    """
    normalized = _run_adr1(HAPPY_PATH_FILE, client)

    assert normalized.get("extraction_status") == "AUTO_COMPLETE", (
        f"Expected AUTO_COMPLETE, got: {normalized.get('extraction_status')}\n"
        f"Low-confidence fields: {normalized.get('low_confidence_fields')}"
    )

    triage = _run_adr4(normalized, client)

    assert triage.get("routing_decision") == "FAST_PATH", (
        f"Expected FAST_PATH, got: {triage.get('routing_decision')}\n"
        f"Provisions matched: {triage.get('criteria_provisions_matched')}\n"
        f"Indicators: {triage.get('clinical_indicators_detected')}"
    )


def test_escalation_human_required(client):
    """
    CMS-1500 OCR with garbled ICD-10 codes → ADR-1 HUMAN_REQUIRED → escalation.
    Verifies the failure-mode path: agent correctly declines to auto-process
    and routes to human exception queue.
    """
    normalized = _run_adr1(ESCALATION_FILE, client)

    assert normalized.get("extraction_status") == "HUMAN_REQUIRED", (
        f"Expected HUMAN_REQUIRED, got: {normalized.get('extraction_status')}"
    )

    low_conf = normalized.get("low_confidence_fields", [])
    assert len(low_conf) > 0, (
        "Expected at least one low-confidence field for the garbled OCR claim"
    )

    # ADR-4 must NOT be called for HUMAN_REQUIRED — this is enforced by the gate
    # in demo.py; here we assert the ADR-1 output is correct to prove the gate fires.


def test_edge_case_clinical_path(client):
    """
    Portal JSON with M54.5 (pain) + CPT 72148 (MRI) → ADR-1 AUTO_COMPLETE
    → ADR-4 CLINICAL_PATH with CC-023 and/or CC-007 matched.
    Verifies the non-happy-path clinical routing the design anticipated.
    """
    normalized = _run_adr1(EDGE_CASE_FILE, client)

    assert normalized.get("extraction_status") == "AUTO_COMPLETE", (
        f"Expected AUTO_COMPLETE, got: {normalized.get('extraction_status')}\n"
        f"Low-confidence fields: {normalized.get('low_confidence_fields')}"
    )

    triage = _run_adr4(normalized, client)

    assert triage.get("routing_decision") == "CLINICAL_PATH", (
        f"Expected CLINICAL_PATH, got: {triage.get('routing_decision')}\n"
        f"Provisions matched: {triage.get('criteria_provisions_matched')}\n"
        f"Indicators: {triage.get('clinical_indicators_detected')}"
    )

    provisions = triage.get("criteria_provisions_matched", [])
    expected   = {"CC-023", "CC-007"}
    matched    = expected & set(provisions)
    assert matched, (
        f"Expected at least one of {expected} in provisions, got: {provisions}"
    )
