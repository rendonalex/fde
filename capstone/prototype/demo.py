#!/usr/bin/env python3
"""
ADR-1 → ADR-4 Pipeline Prototype Demo

Three paths run in sequence:
  1. Happy path    — AUTO_COMPLETE → FAST_PATH
  2. Escalation    — HUMAN_REQUIRED → human exception queue
  3. Edge case     — AUTO_COMPLETE → CLINICAL_PATH (two codebook hits)

Usage:
    python demo.py

Requires ANTHROPIC_API_KEY in environment.
"""
import json
import os
import re
import sys
import time
import uuid
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
HERE     = Path(__file__).resolve().parent
DEMO_DIR = HERE.parent / "demo"
sys.path.insert(0, str(DEMO_DIR))

from preprocessors import preprocess
from prompts import INTAKE_SYSTEM_PROMPT, build_triage_prompt

import anthropic

# ── Configuration ─────────────────────────────────────────────────────────────
MOCK_DATA    = HERE.parent / "mock-data"
CODEBOOK     = str(HERE.parent / "test-data" / "criteria-codebook-mock.json")
MODEL        = "claude-haiku-4-5-20251001"

PATHS = [
    {
        "label":       "PATH 1 — HAPPY PATH",
        "description": "Clean portal JSON, all required fields present",
        "file":        MOCK_DATA / "portal-json"   / "CLM-2026-1001201.json",
    },
    {
        "label":       "PATH 2 — FAILURE-MODE ESCALATION",
        "description": "CMS-1500 OCR with garbled diagnosis codes → human exception queue",
        "file":        MOCK_DATA / "cms1500-ocr"   / "CLM-2026-1001630.txt",
    },
    {
        "label":       "PATH 3 — EDGE CASE: CLINICAL ROUTING",
        "description": "Interventional pain + imaging CPT — two codebook provisions matched",
        "file":        MOCK_DATA / "portal-json"   / "CLM-2026-1001220.json",
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────
WIDTH = 60

def banner(label, description):
    print()
    print("═" * WIDTH)
    print(label)
    print(description)
    print("═" * WIDTH)

def extract_json(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"No JSON object found in model output:\n{text}")
    return json.loads(m.group())

def fmt_list(items):
    return ", ".join(items) if items else "(none)"

# ── Core pipeline ─────────────────────────────────────────────────────────────
def run_path(path_cfg, client):
    path        = str(path_cfg["file"])
    filename    = Path(path).name

    banner(path_cfg["label"], path_cfg["description"])

    # ── Step 1: IDP Extraction ─────────────────────────────────────────────
    print()
    print("  Step 1 — IDP Extraction  (ADR-1, no LLM)")
    t0 = time.time()
    preprocessed = preprocess(path)
    idp_ms = int((time.time() - t0) * 1000)
    print(f"    File:    {filename}  [{preprocessed['source_format']}]")
    print(f"    Ref:     {preprocessed['source_claim_ref']}")
    print(f"    Time:    {idp_ms} ms")

    # ── Step 2: ADR-1 LLM Validation ──────────────────────────────────────
    print()
    print("  Step 2 — LLM Validation & Normalization  (ADR-1)")
    t0 = time.time()
    adr1_response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=INTAKE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(preprocessed, indent=2)}],
    )
    adr1_ms = int((time.time() - t0) * 1000)
    normalized = extract_json(adr1_response.content[0].text)

    status    = normalized.get("extraction_status")
    low_conf  = normalized.get("low_confidence_fields", [])
    routing   = normalized.get("routing_action")

    print(f"    Tokens:  {adr1_response.usage.input_tokens} in / {adr1_response.usage.output_tokens} out")
    print(f"    Time:    {adr1_ms} ms")

    # EXCEPTION_NOTE path
    if routing:
        print(f"    Action:  EXCEPTION_NOTE → {routing}")
        ref = normalized.get("claim_id") or normalized.get("source_claim_ref")
        if routing == "ANNOTATE_CLAIM" and ref:
            print(f"    Ref:     {ref}")
        print()
        print("    ADR-4 not called.")
        return normalized, None

    print(f"    Status:  {status}")
    if low_conf:
        print(f"    Low-confidence fields: {fmt_list(low_conf)}")

    # HUMAN_REQUIRED escalation
    if status == "HUMAN_REQUIRED":
        print()
        print("    → ESCALATED: routed to human exception queue (re-key required)")
        print("    ADR-4 not called.")
        return normalized, None

    # ── Step 3: ADR-4 Clinical Triage ─────────────────────────────────────
    print()
    print("  Step 3 — Clinical Content Triage  (ADR-4)")
    claim_uuid   = str(uuid.uuid4())
    triage_input = {
        "claim_id":            claim_uuid,
        "source_claim_ref":    normalized.get("source_claim_ref"),
        "intake_channel":      normalized.get("intake_channel"),
        "extraction_status":   normalized.get("extraction_status"),
        "claim_type":          normalized.get("claim_type"),
        "icd10_codes":         normalized.get("icd10_codes"),
        "cpt_codes":           normalized.get("cpt_codes"),
        "prior_auth_required": normalized.get("prior_auth_required"),
        "prior_auth_number":   normalized.get("prior_auth_number"),
    }

    t0 = time.time()
    adr4_response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=build_triage_prompt(CODEBOOK),
        messages=[{"role": "user", "content": json.dumps(triage_input, indent=2)}],
    )
    adr4_ms = int((time.time() - t0) * 1000)
    triage = extract_json(adr4_response.content[0].text)

    decision    = triage.get("routing_decision")
    confidence  = triage.get("confidence", 0)
    fallback    = triage.get("confidence_fallback", False)
    provisions  = triage.get("criteria_provisions_matched", [])
    indicators  = triage.get("clinical_indicators_detected", [])

    print(f"    Tokens:  {adr4_response.usage.input_tokens} in / {adr4_response.usage.output_tokens} out")
    print(f"    Time:    {adr4_ms} ms")
    print(f"    Decision:    {decision}")
    print(f"    Confidence:  {confidence:.2f}", end="")
    if fallback:
        print("  ** fallback applied (< 0.70 threshold)", end="")
    print()
    print(f"    Provisions:  {fmt_list(provisions)}")
    print(f"    Indicators:  {fmt_list(indicators)}")

    if decision == "CLINICAL_PATH":
        print()
        print("    → ROUTED TO: clinical review queue")
    else:
        print()
        print("    → ROUTED TO: fast-track adjudication")

    return normalized, triage

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"Model: {MODEL}")
    has_key = "ANTHROPIC_API_KEY" in os.environ or "ANTHROPIC_AUTH_TOKEN" in os.environ
    print(f"API key set: {has_key}")

    if not has_key:
        print("ERROR: ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN not set.")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    client  = anthropic.Anthropic(api_key=api_key)
    t_start  = time.time()

    for path_cfg in PATHS:
        run_path(path_cfg, client)

    elapsed = time.time() - t_start
    print()
    print("═" * WIDTH)
    print(f"Demo complete — {elapsed:.1f}s total")
    print("═" * WIDTH)

if __name__ == "__main__":
    main()
