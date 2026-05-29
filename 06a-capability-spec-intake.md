# Capability Specification: Claim Intake and Format Validation Agent
## ADR-1 — Greenfield Health Systems AI Claims Processing Transformation

**Prepared by:** FDE Engagement Lead  
**Date:** 2026-05-21  
**Wave:** Wave 1 (Phase 1, Months 1–3)  
**Delegation Archetype:** Agent-led + Human Oversight  
**Status:** Active — specification finalized pending [A12] CMS API confirmation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Agent Purpose Document](#2-agent-purpose-document)
3. [Agent Activity Catalog](#3-agent-activity-catalog)
4. [Autonomy Matrix](#4-autonomy-matrix)
5. [System and Data Inventory](#5-system-and-data-inventory)
6. [Context Engineering Design](#6-context-engineering-design)
7. [Compounding Roadmap](#7-compounding-roadmap)
8. [Integration Contracts](#8-integration-contracts)
9. [Entity Data Models](#9-entity-data-models)
10. [Validation Scenarios](#10-validation-scenarios)
11. [Governance](#11-governance)

---

## 1. Executive Summary

ADR-1 is the foundational intake layer for the entire dual-path claims architecture. It transforms raw claim submissions — EDI 837, PDF, and portal formats — into validated, normalized, SLA-prioritized records in the Claims Management System (CMS), ready for downstream agent processing.

The intake agent runs on two sub-paths. The **EDI path** (70% of volume [A7]) is fully agentic: EDI 837 transactions are structured by HIPAA mandate, machine-parsable, and flow through without human involvement. The **non-EDI path** (30% of volume [A7]) uses an Intelligent Document Processing (IDP) pipeline — currently not in place [A14] — to extract required fields from PDF and portal submissions. Extractions above a per-field confidence threshold proceed automatically; those below route to a human exception queue for re-key. The target HITL rate is ≤10% of non-EDI volume (~50 claims/day).

ADR-1 is sequenced Wave 1 for two reasons: (1) the intake pipeline is the structural prerequisite for ADR-4 triage — the clinical classification model requires normalized, structured claim records as input; and (2) it generates the only Wave 1 autonomous savings (~$117K/year [A21]) while ADR-4 runs in shadow mode without adjudicating any claims.

The primary platform assets created by ADR-1 — the CMS API integration, normalized claim record schema, IDP extraction pipeline, and SLA-aware queue module — are reused by every Wave 2 and Wave 3 agent. The marginal build cost of downstream agents is materially reduced by this foundation.

**Key metrics:**
- Throughput: 1,667 claims/day processed to queue-assigned status within 1 hour of receipt [U1]
- Accuracy: ≥98% field extraction on EDI path; ≥90% on non-EDI path
- HITL rate: ≤10% of non-EDI volume (~50 claims/day escalated to human queue)
- Cost per claim: ~$0.05 API cost [A4]; $46,875/year HITL residual
- Payback contribution: ~$117K/year from intake automation (9% of admin baseline [A21])

---

## 2. Agent Purpose Document

```
Agent Name:       Claim Intake and Format Validation Agent
Job to be Done:   Transform every incoming claim submission into a validated, normalized,
                  SLA-prioritized record in the CMS — the structured input prerequisite
                  for all downstream agents.
Business context: Zone 1 (Intake) — the entry point of the claims processing workflow;
                  handles all 1,667 claims/day [U1] across EDI, PDF, and portal channels.

Primary objectives:
  1. Parse and normalize all EDI 837 submissions end-to-end without human involvement.
  2. Extract structured fields from non-EDI submissions via IDP; escalate unresolvable
     extractions to a human exception queue with per-field confidence detail.
  3. Validate required field completeness and assign every claim to an SLA-prioritized
     queue before releasing it for downstream processing.

KPIs:
  - Accuracy:    ≥98% field extraction accuracy on EDI path;
                 ≥90% on non-EDI path (per-field confidence ≥ 0.85 threshold)
  - Coverage:    ≥90% of all claims processed to CMS without human intervention
                 (EDI path: 100%; non-EDI path: ~80% [A14])
  - Throughput:  1,667 claims/day queued within 1 hour of receipt
  - Cost/claim:  ~$0.05 API cost [A4]
  - HITL rate:   ≤10% of non-EDI volume (~50 claims/day human re-key)

Failure modes:
  - Extraction failure (required field unresolvable): pend claim with specific
    missing-field flag; do NOT deny; route to exception queue for re-key.
  - CMS write failure [A12]: hold claim locally with idempotency key; retry on
    API recovery; alert ops team after 3 failed retries.
  - Duplicate claim detected (same claim ID + member + DOS + provider): pend
    with duplicate flag; notify submitting processor for resolution.
  - Novel format (not EDI, not standard PDF): route to exception queue with
    format-unrecognized flag; do not attempt extraction.

Delegation archetype:
  Agent-led + Human Oversight — split by sub-path:
    - EDI sub-path: Fully Agentic (no human involvement for well-formed EDI 837)
    - Non-EDI sub-path: Agent-led + Human Oversight (HITL only on extraction failures)

Escalation triggers:
  - Any required field extraction confidence < 0.85 → human re-key queue
  - CMS API unavailable after 3 retries [A12] → ops alert
  - Duplicate claim detected → processor notification queue
  - Claim volume spike >2× daily average → ops alert for capacity check
```

---

## 3. Agent Activity Catalog

| Task | Type | Delegation Level | Data Required | Tool Required | Risk Level |
|------|------|:----------------:|---------------|---------------|:----------:|
| Detect incoming claim format (EDI 837 / PDF / portal) | Reasoning | Fully agentic | Incoming file/message headers | Format detection library | Low |
| Parse EDI 837 transaction set (segments: CLM, NM1, SV1, DTP, etc.) | Retrieval | Fully agentic | EDI 837 file | EDI 837 parser | Low |
| Extract required claim fields from PDF/portal via IDP [A14] | Retrieval | Agent-led + HITL on low-confidence | PDF or portal submission | IDP extraction pipeline | Medium |
| Score per-field extraction confidence | Reasoning | Fully agentic | IDP extraction result | Confidence scoring model | Medium |
| Validate required field completeness against CMS field schema | Decision | Fully agentic | Extracted fields + CMS schema | Field validation rules engine | Medium |
| Check for duplicate submission (claim ID, member ID, DOS, provider NPI) | Decision | Fully agentic | Normalized claim fields | CMS read API | Low |
| Flag completeness exception with per-field detail | Generation | Fully agentic | Validation result | CMS write API (exception flag) | Low |
| Write normalized claim record to CMS | Action | Fully agentic | Validated + normalized claim data | CMS write API | Medium |
| Assign claim to SLA-prioritized processing queue [A17] | Action | Fully agentic | Claim receipt timestamp, payer SLA config | Queue management module | Low |
| Route low-confidence extractions to human exception queue | Action | Fully agentic (escalation decision) | Per-field confidence scores | Exception queue API | Medium |
| Log intake decision and extraction metadata for audit trail | Action | Fully agentic | All above fields + confidence scores | Audit log store | Medium |

**Task type legend:** Reasoning (model does cognitive work) · Retrieval (fetch/return data) · Decision (choose between outcomes) · Action (write to system or trigger process) · Generation (produce structured output)

**Key design notes:**
- MT-1.2 (non-EDI extraction) is the only task with meaningful HITL. The IDP pipeline handles ~80% of PDFs automatically [A14]; the remaining ~20% require human re-key and are the source of the $46,875/year HITL cost (Section 4 of the Volume × Value Analysis).
- MT-1.4 (queue assignment) implements the SLA-aware prioritization described in [A17] — claims nearest the 7-day penalty threshold surface first. This is a new capability not present in the current process.
- MT-1.3 (completeness validation) uses the CMS required-field schema as a deterministic rule set — no LLM reasoning required here; the agent wraps the rules engine.

---

## 4. Autonomy Matrix

```
AGENT DECIDES ALONE (no HITL required):
  - EDI 837 parsing and field extraction
  - Completeness validation against required field list
  - Duplicate claim detection
  - SLA-priority queue assignment
  - CMS record creation for validated claims
  - Exception flag generation with per-field detail
  - Routing of below-threshold extractions to human queue
    (escalation decision is autonomous; human executes re-key)
  - Audit log entry for every processed claim

AGENT ACTS, HUMAN NOTIFIED AFTER:
  - Non-EDI extraction where all fields resolve above confidence threshold
    (extraction result logged; processor receives notification of new claim in queue)
  - Duplicate hold (processor notified after pend is placed)

AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION:
  - Non-EDI extraction where ≥1 required field confidence < 0.85:
    agent presents extracted fields with confidence scores;
    human reviews, corrects, and approves before CMS write
  - (No approvals required on EDI path)

HUMAN TAKES OVER (agent supports):
  - CMS API failure that exceeds retry budget [A12] — ops team manages
    batch recovery; agent queues claims locally and provides status log
  - Claims in unrecognized formats — agent flags format + provides
    available metadata; human determines handling
  - Batch import of legacy backlog claims — human-managed with agent
    assisting field extraction
```

---

## 5. System and Data Inventory

| System | Data Needed | Access Type | Availability | Gap / Risk |
|--------|-------------|:-----------:|--------------|------------|
| CMS (Claims Management System) | Claim record create; queue assignment; duplicate lookup by claim ID, member ID, DOS, provider NPI | Read / Write | Assumed API available [A12] | **Primary Wave 1 blocker** — integration scope and API maturity must be confirmed in Week 1 IT discovery sprint |
| EDI 837 parser | EDI transaction segments: CLM, NM1, SV1, DTP, REF, HI/HCP diagnosis and procedure codes | Read | Commercially available (e.g., StediStudio, Centauri Health) | No gap — standard healthcare tooling; license cost only |
| IDP extraction pipeline | Claim fields from PDF/portal submissions: provider NPI, member ID, DOS, ICD-10, CPT, billed amount | Read | **Must be built** — not currently in place [A14] | Wave 1 build deliverable (~$35K in build cost budget); scope depends on PDF structure variety |
| Queue management module | SLA age, payer priority config, queue position assignment | Read / Write | Part of CMS or standalone | SLA-aware config may not exist [A17]; may require new CMS configuration or standalone module |
| Audit log store | Intake decision, extraction confidence scores, timestamps, routing outcome, operator ID for re-key | Write | Standard infrastructure (e.g., structured log to data warehouse) | No gap — standard logging infrastructure |
| Exception queue | Human re-key routing; per-field extraction detail passed to processor UI | Read / Write | Assumed existing ops queue workflow | Ops process integration required; UI for displaying per-field confidence scores to processor needs design |

**Shared with ADR-4 (Clinical Content Triage Agent):** CMS read API and normalized claim record schema. ADR-4 ingests ADR-1 output directly — the canonical claim record format designed in Wave 1 must accommodate triage classification metadata fields (clinical indicator flags, routing decision) without schema changes in Wave 2.

---

## 6. Context Engineering Design

### Memory Architecture

| Memory Type | Content | Storage | Lifecycle |
|-------------|---------|:-------:|-----------|
| **In-context** (short-term) | Current claim fields, IDP extraction result, validation status, confidence scores | Prompt window | Per claim — stateless; no cross-claim context |
| **Procedural** (static) | Required field list, CMS field schema, validation rules, duplicate detection logic, confidence threshold (0.85), escalation decision rules | System prompt | Version-controlled; updated on schema change |
| **Episodic** (medium-term) | Per-claim extraction history (confidence scores, prior rejection flags, re-submission count) | CMS claim record metadata | Per claim; used for re-submission handling and audit |

ADR-1 does not require semantic memory (RAG) — all decisions are deterministic rule application. The system prompt carries the complete rulebook.

### Retrieval Strategy

- **Field schema lookup:** Deterministic. Required field list and CMS schema loaded into system prompt at deployment time — not retrieved per claim. Updated on CMS schema change via prompt versioning.
- **Duplicate check:** Structured CMS query by claim ID + member ID + DOS + provider NPI — exact match via CMS read API. Not semantic retrieval.
- **Payer SLA config:** Loaded into queue management module at startup; refreshed daily. Not per-claim retrieval.
- **Retrieval cost management:** No RAG required; zero retrieval overhead per claim. Agent cost is dominated by IDP extraction calls (non-EDI path only).

### Prompt / Context Engineering Principles

1. **Role and scope first:** System prompt opens with agent identity and the exact list of permitted actions: parse, validate, deduplicate, log, queue-assign, escalate. Prohibited actions stated explicitly: "Do not make clinical decisions. Do not deny claims. Do not modify billing codes."
2. **Structured output required:** Agent outputs a JSON record conforming to the CMS write API contract. Field: `extraction_status` ∈ {`AUTO_COMPLETE`, `HUMAN_REQUIRED`, `PENDING_DUPLICATE`}; field `field_confidence` is a map of required fields to confidence scores.
3. **Guardrail for escalation:** "If any required field in the attached schema resolves at confidence < 0.85, set `extraction_status: HUMAN_REQUIRED` and populate `field_confidence` with per-field scores. Do not write to CMS until human confirmation is received."
4. **No few-shot examples needed on EDI path** — parsing is deterministic. Non-EDI path benefits from 3–5 extraction examples covering PDF layout variants common in Greenfield's provider mix.
5. **Token discipline:** System prompt is minimal (~300 tokens for rules + schema). Claim data (EDI transaction or extracted fields) passed as structured input. Avoid prose descriptions in the system prompt; prefer field-level rules.
6. **No chain-of-thought required** — intake is rule-bound; step-by-step reasoning instructions add cost without accuracy benefit. Reserve CoT for ADR-4 triage where clinical reasoning is required.

### System Prompt Template

> **Versioning:** The prompt is a versioned deployment artifact stored in the secrets/config manager under key `ADR1_SYSTEM_PROMPT_V{N}`. Any change to the Required Field List or output schema constitutes a new prompt version and requires a redeployment. Template variables in `{{double braces}}` are substituted at deployment time, not at inference time.

> **Input format:** The user message passed to this agent on each inference call is a JSON object containing either: (a) the output of the EDI 837 parser — a flat field map with no confidence scores; or (b) the output of the IDP extraction pipeline — a field map with per-field `confidence` values. The agent never receives raw EDI transactions or raw PDFs directly.

```
SYSTEM PROMPT — ADR-1 Claim Intake and Format Validation Agent
Prompt version: {{ADR1_PROMPT_VERSION}}
CMS field schema version: {{CMS_SCHEMA_VERSION}}

## Role
You are the intake validation layer for Greenfield Health Systems' claims processing pipeline.
You receive extracted claim fields and determine whether the claim is complete enough to write
to the Claims Management System (CMS) or must be held for human review.

## What you do
1. Review the extracted claim fields in the user message.
2. Check every required field against the Required Field List below.
3. For non-EDI claims: check per-field confidence values against the threshold.
4. Determine extraction_status using the rules below.
5. Output a complete, structured JSON record.

## What you do not do
- Do not parse raw EDI transactions (the EDI parser handles this before calling you).
- Do not call APIs — the application layer handles all CMS writes, queue assignment, and logging.
- Do not make clinical decisions of any kind.
- Do not deny claims. Unresolvable fields → HUMAN_REQUIRED, never a denial.
- Do not modify ICD-10 codes, CPT codes, or billed amounts.
- Do not infer or fabricate a missing field value.

## Required Field List
Every claim record must contain all of the following (non-null, non-empty):
  member_id             — string, max 20 chars
  member_dob            — YYYY-MM-DD
  member_name_last      — string, max 60 chars
  member_name_first     — string, max 60 chars
  rendering_provider_npi — string, exactly 10 digits
  billing_provider_npi  — string, exactly 10 digits
  billing_provider_tax_id — string, exactly 9 digits (EIN)
  date_of_service_start — YYYY-MM-DD
  date_of_service_end   — YYYY-MM-DD; must be >= date_of_service_start
  place_of_service_code — string, exactly 2 digits
  claim_type            — PROFESSIONAL | INSTITUTIONAL | DENTAL
  icd10_codes           — array of strings, min 1 element
  cpt_codes             — array of strings, min 1 element
  billed_amount         — decimal > 0
  payer_id              — string, max 20 chars
  payer_name            — string, max 100 chars
  plan_id               — string, max 30 chars
  prior_auth_required   — boolean
CONDITIONAL:
  prior_auth_number     — required when prior_auth_required = true; must be null when false

## Extraction status rules
Set exactly one of: AUTO_COMPLETE | HUMAN_REQUIRED
(PENDING_DUPLICATE is set by the application layer after the CMS duplicate check; never set it yourself.)

AUTO_COMPLETE:
  All required fields are present AND one of:
    (a) intake_channel = EDI_837 (EDI extraction is deterministic; no confidence check needed), OR
    (b) intake_channel = PDF | PORTAL AND every required field has confidence >= 0.85

HUMAN_REQUIRED:
  Any required field is absent or null, OR
  intake_channel = PDF | PORTAL AND any required field has confidence < 0.85
  → When HUMAN_REQUIRED: populate field_confidence for ALL extracted fields (not only the
    low-confidence ones) so the human reviewer sees the full picture.

## Output format
Respond with a single JSON object only. No prose before or after the JSON.

{
  "source_claim_ref":        "string, max 50 chars",
  "member_id":               "string, max 20 chars",
  "member_dob":              "YYYY-MM-DD",
  "member_name_last":        "string, max 60 chars",
  "member_name_first":       "string, max 60 chars",
  "rendering_provider_npi":  "string, exactly 10 digits",
  "billing_provider_npi":    "string, exactly 10 digits",
  "billing_provider_tax_id": "string, exactly 9 digits",
  "date_of_service_start":   "YYYY-MM-DD",
  "date_of_service_end":     "YYYY-MM-DD",
  "place_of_service_code":   "string, exactly 2 digits",
  "claim_type":              "PROFESSIONAL | INSTITUTIONAL | DENTAL",
  "icd10_codes":             ["string"],
  "cpt_codes":               ["string"],
  "revenue_codes":           ["string — INSTITUTIONAL claims only; empty array [] otherwise"],
  "drg_code":                "string — INSTITUTIONAL claims only; null otherwise",
  "billed_amount":           0.00,
  "currency":                "USD",
  "payer_id":                "string, max 20 chars",
  "payer_name":              "string, max 100 chars",
  "plan_id":                 "string, max 30 chars",
  "prior_auth_required":     true,
  "prior_auth_number":       "string | null",
  "intake_channel":          "EDI_837 | PDF | PORTAL",
  "extraction_status":       "AUTO_COMPLETE | HUMAN_REQUIRED",
  "field_confidence":        { "<field_name>": 0.00 }
}

field_confidence rules:
  EDI_837: omit field_confidence entirely.
  PDF | PORTAL with HUMAN_REQUIRED: include all extracted fields with their confidence values.
  PDF | PORTAL with AUTO_COMPLETE: include field_confidence for audit completeness.

## Few-shot examples (non-EDI PDF claims)

--- EXAMPLE 1: Clean PDF extraction — all fields above threshold → AUTO_COMPLETE ---
User message:
{
  "source_format": "PDF",
  "source_claim_ref": "PDF-2026-0441",
  "extracted_fields": {
    "member_id":               { "value": "M-4421908",      "confidence": 0.97 },
    "member_dob":              { "value": "1978-03-14",     "confidence": 0.95 },
    "member_name":             { "value": "Alice Thompson",  "confidence": 0.96 },
    "rendering_provider_npi":  { "value": "1234567890",     "confidence": 0.99 },
    "billing_provider_npi":    { "value": "9876543210",     "confidence": 0.99 },
    "billing_provider_tax_id": { "value": "47-2918304",     "confidence": 0.93 },
    "payer_id":                { "value": "BX-0042",        "confidence": 0.98 },
    "dos":                     { "value": "2026-04-11",     "confidence": 0.97 },
    "place_of_service":        { "value": "11",             "confidence": 0.99 },
    "icd10_codes":             { "value": ["Z00.00"],       "confidence": 0.92 },
    "cpt_codes":               { "value": ["99213"],        "confidence": 0.94 },
    "billed_amount":           { "value": 185.00,           "confidence": 0.91 },
    "prior_auth_number":       { "value": null,             "confidence": 1.00 },
    "prior_auth_required":     { "value": false,            "confidence": 0.97 }
  }
}
Assistant:
{
  "source_claim_ref":        "PDF-2026-0441",
  "member_id":               "M-4421908",
  "member_dob":              "1978-03-14",
  "member_name":             "Alice Thompson",
  "rendering_provider_npi":  "1234567890",
  "billing_provider_npi":    "9876543210",
  "billing_provider_tax_id": "47-2918304",
  "payer_id":                "BX-0042",
  "dos":                     "2026-04-11",
  "place_of_service":        "11",
  "icd10_codes":             ["Z00.00"],
  "cpt_codes":               ["99213"],
  "billed_amount":           185.00,
  "prior_auth_number":       null,
  "prior_auth_required":     false,
  "extraction_status":       "AUTO_COMPLETE",
  "low_confidence_fields":   [],
  "field_confidence": {
    "member_id": 0.97, "member_dob": 0.95, "member_name": 0.96,
    "rendering_provider_npi": 0.99, "billing_provider_npi": 0.99,
    "billing_provider_tax_id": 0.93, "payer_id": 0.98, "dos": 0.97,
    "place_of_service": 0.99, "icd10_codes": 0.92, "cpt_codes": 0.94,
    "billed_amount": 0.91, "prior_auth_number": 1.00, "prior_auth_required": 0.97
  }
}

--- EXAMPLE 2: PDF with one field below confidence threshold → HUMAN_REQUIRED ---
User message:
{
  "source_format": "PDF",
  "source_claim_ref": "PDF-2026-0512",
  "extracted_fields": {
    "member_id":               { "value": "M-783304",       "confidence": 0.61 },
    "member_dob":              { "value": "1965-11-02",     "confidence": 0.94 },
    "member_name":             { "value": "Robert Chen",    "confidence": 0.95 },
    "rendering_provider_npi":  { "value": "2109876543",     "confidence": 0.98 },
    "billing_provider_npi":    { "value": "3012345678",     "confidence": 0.97 },
    "billing_provider_tax_id": { "value": "52-4471882",     "confidence": 0.91 },
    "payer_id":                { "value": "UH-0017",        "confidence": 0.96 },
    "dos":                     { "value": "2026-04-15",     "confidence": 0.98 },
    "place_of_service":        { "value": "11",             "confidence": 0.99 },
    "icd10_codes":             { "value": ["J06.9","R05.9"],"confidence": 0.89 },
    "cpt_codes":               { "value": ["99213","87880"],"confidence": 0.92 },
    "billed_amount":           { "value": 240.00,           "confidence": 0.90 },
    "prior_auth_number":       { "value": null,             "confidence": 1.00 },
    "prior_auth_required":     { "value": false,            "confidence": 0.95 }
  }
}
Assistant:
{
  "source_claim_ref":        "PDF-2026-0512",
  "member_id":               "M-783304",
  "member_dob":              "1965-11-02",
  "member_name":             "Robert Chen",
  "rendering_provider_npi":  "2109876543",
  "billing_provider_npi":    "3012345678",
  "billing_provider_tax_id": "52-4471882",
  "payer_id":                "UH-0017",
  "dos":                     "2026-04-15",
  "place_of_service":        "11",
  "icd10_codes":             ["J06.9", "R05.9"],
  "cpt_codes":               ["99213", "87880"],
  "billed_amount":           240.00,
  "prior_auth_number":       null,
  "prior_auth_required":     false,
  "extraction_status":       "HUMAN_REQUIRED",
  "low_confidence_fields":   ["member_id"],
  "field_confidence": {
    "member_id": 0.61, "member_dob": 0.94, "member_name": 0.95,
    "rendering_provider_npi": 0.98, "billing_provider_npi": 0.97,
    "billing_provider_tax_id": 0.91, "payer_id": 0.96, "dos": 0.98,
    "place_of_service": 0.99, "icd10_codes": 0.89, "cpt_codes": 0.92,
    "billed_amount": 0.90, "prior_auth_number": 1.00, "prior_auth_required": 0.95
  }
}

--- EXAMPLE 3: PDF with required field absent (not extracted) → HUMAN_REQUIRED ---
User message:
{
  "source_format": "PDF",
  "source_claim_ref": "PDF-2026-0589",
  "extracted_fields": {
    "member_id":               { "value": "M-2194567",      "confidence": 0.96 },
    "member_dob":              { "value": "1952-07-28",     "confidence": 0.93 },
    "member_name":             { "value": "Linda Okafor",   "confidence": 0.97 },
    "rendering_provider_npi":  { "value": "4418273650",     "confidence": 0.99 },
    "billing_provider_npi":    { "value": "5503984712",     "confidence": 0.98 },
    "billing_provider_tax_id": { "value": null,             "confidence": 0.00 },
    "payer_id":                { "value": "AE-0031",        "confidence": 0.95 },
    "dos":                     { "value": "2026-04-18",     "confidence": 0.97 },
    "place_of_service":        { "value": "22",             "confidence": 0.99 },
    "icd10_codes":             { "value": ["E11.9"],        "confidence": 0.94 },
    "cpt_codes":               { "value": ["99214"],        "confidence": 0.96 },
    "billed_amount":           { "value": 310.00,           "confidence": 0.92 },
    "prior_auth_number":       { "value": null,             "confidence": 1.00 },
    "prior_auth_required":     { "value": false,            "confidence": 0.91 }
  }
}
Assistant:
{
  "source_claim_ref":        "PDF-2026-0589",
  "member_id":               "M-2194567",
  "member_dob":              "1952-07-28",
  "member_name":             "Linda Okafor",
  "rendering_provider_npi":  "4418273650",
  "billing_provider_npi":    "5503984712",
  "billing_provider_tax_id": null,
  "payer_id":                "AE-0031",
  "dos":                     "2026-04-18",
  "place_of_service":        "22",
  "icd10_codes":             ["E11.9"],
  "cpt_codes":               ["99214"],
  "billed_amount":           310.00,
  "prior_auth_number":       null,
  "prior_auth_required":     false,
  "extraction_status":       "HUMAN_REQUIRED",
  "low_confidence_fields":   ["billing_provider_tax_id"],
  "field_confidence": {
    "member_id": 0.96, "member_dob": 0.93, "member_name": 0.97,
    "rendering_provider_npi": 0.99, "billing_provider_npi": 0.98,
    "billing_provider_tax_id": 0.00, "payer_id": 0.95, "dos": 0.97,
    "place_of_service": 0.99, "icd10_codes": 0.94, "cpt_codes": 0.96,
    "billed_amount": 0.92, "prior_auth_number": 1.00, "prior_auth_required": 0.91
  }
}
```

---

## 7. Compounding Roadmap

ADR-1 is Wave 1's platform-building agent. Every integration and asset it creates is reused by Wave 2 and Wave 3 agents — reducing marginal build cost and ensuring schema consistency across the pipeline.

### Wave Sequencing

**Wave 1 — ADR-1 builds the foundation (Months 1–3):**
- CMS API integration (read/write) — the single shared integration point for all downstream agents
- Normalized claim record schema — the canonical data contract; must be designed with downstream ADR field requirements in mind
- EDI 837 parser — reused if a future EDI output path is needed (e.g., ADR-8 payment trigger)
- IDP extraction pipeline — reused by ADR-6 for clinical documentation extraction
- SLA-aware queue management module — reused by ADR-4 (triage routing queue) and ADR-5 (Fast Path adjudication queue)
- Audit log infrastructure — reused by ADR-4 (shadow mode logging) and all Wave 2 agents

**Wave 2 — All Wave 2 agents reuse ADR-1 assets (Months 4–6):**
- ADR-4 (triage): ingests normalized claim record from ADR-1; uses CMS API to write routing decision
- ADR-2 (eligibility): reads member and provider fields from ADR-1 normalized record via CMS API
- ADR-3 (coding validation): reads ICD-10/CPT fields from ADR-1 normalized record via CMS API
- ADR-5 (Fast Path adjudication): reads validated claim record; writes adjudication decision to CMS
- ADR-6 (clinical pre-screening): reuses IDP extraction pipeline for unstructured clinical documentation

**Wave 3 — Continued reuse (Month 7+):**
- ADR-9 (denial letters): reads claim record and denial rationale from CMS; writes denial communication
- ADR-8 (payment): reads approved adjudication outcome; triggers payment engine via CMS event

### Integration Reuse Matrix

| Integration / Asset | ADR-1 (Intake) | ADR-4 (Triage) | ADR-2 (Elig.) | ADR-3 (Coding) | ADR-5 (Fast Path) | ADR-6 (Pre-Screen) | ADR-9 (Denial) | ADR-8 (Payment) |
|--------------------|:--------------:|:--------------:|:-------------:|:--------------:|:-----------------:|:-----------------:|:--------------:|:---------------:|
| CMS read/write API [A12] | **✓ Build** | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| Normalized claim record schema | **✓ Build** | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| EDI 837 parser | **✓ Build** | — | — | — | — | — | — | — |
| IDP extraction pipeline | **✓ Build** | — | — | — | — | ✓ Reuse | — | — |
| SLA-aware queue module [A17] | **✓ Build** | ✓ Reuse | — | — | ✓ Reuse | ✓ Reuse | — | — |
| Audit log store | **✓ Build** | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| Clinical classification model | — | ✓ Build (ADR-4) | — | — | — | ✓ Reuse | — | — |
| Clinical criteria codebook [A15] | — | ✓ Build (ADR-4) | — | — | — | ✓ Reuse | — | — |
| Shadow evaluation pipeline | — | ✓ Build (ADR-4) | — | — | — | — | — | — |

**Maximising the matrix:** The CMS API, normalized claim record, and audit log are shared across all eight agents. The IDP extraction pipeline built for non-EDI intake in ADR-1 avoids a duplicate build in ADR-6 — both deal with unstructured document inputs. Every integration that ADR-1 resolves in Wave 1 is a Wave 2 acceleration.

### Critical Path Note

ADR-1 is a prerequisite for ADR-4. The clinical triage shadow pipeline ingests normalized claim records — it cannot run until ADR-1's CMS integration and claim record schema are in place. Wave 1 build order: ADR-1 intake pipeline → ADR-4 shadow mode wiring. The two can develop concurrently in sprint, but ADR-4 shadow evaluation cannot begin until ADR-1 is delivering records to CMS.

---

---

## 8. Integration Contracts

> **Reading note:** CMS API details are assumed pending Week 1 IT discovery [A12]. Contracts below define the *minimum interface the agent requires* — treat unconfirmed fields as integration requirements to be validated, not implementation choices. All [TODO] markers in this section must be resolved before Sprint 1 development begins.

### 8.1 CMS Read/Write API [A12]

**Contract status:** Assumed [A12]. Confirm endpoint URL, authentication method, and rate limits in Week 1 IT discovery sprint. Development is blocked until confirmed.

**Endpoints:**
```
Base URL:  env var CMS_BASE_URL (stored in secrets manager key: CMS_BASE_URL)
POST   {CMS_BASE_URL}/v1/claims                                              — create claim record
GET    {CMS_BASE_URL}/v1/claims/{claim_id}                                   — read claim record
PUT    {CMS_BASE_URL}/v1/claims/{claim_id}                                   — update claim record (HITL re-key resolution)
GET    {CMS_BASE_URL}/v1/claims?member_id={}&date_of_service_start={}&rendering_provider_npi={}&payer_id={}
                                                                             — duplicate check query
```

**Authentication:** Bearer token in `Authorization: Bearer <token>` header. Token stored in secrets manager under key `CMS_API_KEY`. [TODO: confirm whether CMS supports mTLS — prefer mTLS if available.]

**POST /v1/claims — Request body (JSON):**
All fields are required unless marked optional.
```json
{
  "source_claim_ref":         "string, max 50 chars — original EDI ISA control number or portal transaction ID",
  "member_id":                "string, max 20 chars — payer-issued member ID",
  "member_dob":               "YYYY-MM-DD",
  "member_name_last":         "string, max 60 chars",
  "member_name_first":        "string, max 60 chars",
  "rendering_provider_npi":   "string, exactly 10 digits",
  "billing_provider_npi":     "string, exactly 10 digits",
  "billing_provider_tax_id":  "string, exactly 9 digits (EIN)",
  "date_of_service_start":    "YYYY-MM-DD",
  "date_of_service_end":      "YYYY-MM-DD — must be >= date_of_service_start",
  "place_of_service_code":    "string, exactly 2 digits — CMS POS code",
  "claim_type":               "PROFESSIONAL | INSTITUTIONAL | DENTAL",
  "icd10_codes":              ["array of string, ICD-10-CM format (e.g. Z79.899), min 1, max 12"],
  "cpt_codes":                ["array of string, CPT + optional 2-char modifier (e.g. 99213-25), min 1, max 50"],
  "revenue_codes":            ["array of string(4) — optional, INSTITUTIONAL claims only"],
  "drg_code":                 "string(3) — optional, INSTITUTIONAL claims only",
  "billed_amount":            "decimal(10,2), > 0, USD",
  "payer_id":                 "string, max 20 chars",
  "payer_name":               "string, max 100 chars",
  "plan_id":                  "string, max 30 chars",
  "prior_auth_required":      "boolean",
  "prior_auth_number":        "string, max 30 chars — required if prior_auth_required = true, omit otherwise",
  "intake_channel":           "EDI_837 | PDF | PORTAL",
  "extraction_status":        "AUTO_COMPLETE | HUMAN_REQUIRED | PENDING_DUPLICATE",
  "field_confidence":         {"<field_name>": "float 0.0–1.0 — required for non-EDI; omit for EDI_837"},
  "sla_queue":                "PRIORITY | STANDARD | BATCH",
  "sla_deadline":             "ISO 8601 UTC timestamp"
}
```

**Responses:**
```
HTTP 201 Created:
  { "claim_id": "UUID", "created_at": "ISO 8601 UTC", "status": "QUEUED" }

HTTP 409 Conflict (duplicate detected):
  { "error": "DUPLICATE_CLAIM", "existing_claim_id": "UUID", "message": "string" }
  → Agent action: set extraction_status = PENDING_DUPLICATE; route to exception queue; do NOT retry.

HTTP 422 Unprocessable Entity (field validation failure):
  { "error": "VALIDATION_FAILED", "fields": [{ "field": "string", "reason": "string" }] }
  → Agent action: do NOT retry; log field errors; route to exception queue with exception_type: CMS_WRITE_FAILURE.

HTTP 429 Too Many Requests:
  Headers: Retry-After: <seconds>
  { "error": "RATE_LIMITED", "retry_after_seconds": integer }
  → Agent action: wait exactly Retry-After seconds, then retry once.

HTTP 5xx Server Error:
  { "error": "SERVER_ERROR", "message": "string", "request_id": "string" }
  → Agent action: see retry logic below.
```

**Timeout:** 10 seconds per request.

**Retry logic:**
- HTTP 5xx: retry up to 3 times, exponential backoff: 2 s → 4 s → 8 s. After 3 failures: persist claim locally with `idempotency_key = SHA-256(source_claim_ref + "|" + member_id + "|" + date_of_service_start)`; post `CMS_UNAVAILABLE` alert to ops channel; retry on 5-minute intervals until CMS recovers. On recovery: replay locally-queued claims in FIFO order using idempotency key to prevent duplicate writes.
- HTTP 429: wait `Retry-After` seconds, retry once. If second attempt also returns 429, treat as 5xx path.
- HTTP 4xx (except 409, 429): do not retry. Log `claim_id` and error detail. Route to exception queue.
- Timeout: retry once after 5 s. If second attempt also times out, treat as 5xx failure path.

**Rate limits:** [TODO: confirm with IT discovery. Assume ≤ 100 req/s until confirmed.] Implement token-bucket rate limiter targeting 80 req/s to leave headroom.

**Data mapping:** NormalizedClaimRecord (§9.1) is the canonical CMS record. All fields map 1:1 to the POST body above. No transformation layer required at write time. Routing fields (`routing_decision`, `routing_confidence`, etc.) are written by ADR-4, not ADR-1 — ADR-1 must not write those fields.

---

### 8.2 EDI 837 Parser

**Tool:** Commercially licensed ANSI X12 837 parser (e.g., Stedi, Centauri Health Solutions, or equivalent). Must support EDI 837P (Professional) and 837I (Institutional) transaction sets.

**Input:** Raw EDI 837 transaction set as UTF-8 string.

**Required segment-to-field mapping:**

| EDI Segment | Loop | Field Extracted | NormalizedClaimRecord Field |
|---|---|---|---|
| CLM01 | 2300 | Claim reference number | `source_claim_ref` |
| NM1*IL — NM109 | 2010BA | Member ID | `member_id` |
| NM1*IL — NM104/05 | 2010BA | Member last/first name | `member_name_last`, `member_name_first` |
| DMG*D8 | 2010BA | Member date of birth | `member_dob` |
| NM1*82 — NM109 | 2310B | Rendering provider NPI | `rendering_provider_npi` |
| NM1*85 — NM109 | 2010AA | Billing provider NPI | `billing_provider_npi` |
| REF*EI | 2010AA | Billing provider tax ID | `billing_provider_tax_id` |
| DTP*472 | 2300 | Date of service start/end | `date_of_service_start`, `date_of_service_end` |
| HI*ABK / HI*ABF | 2300 | Primary / additional ICD-10 codes | `icd10_codes` |
| SV1*HC | 2400 | CPT code + modifier | `cpt_codes` |
| CLM05-1 | 2300 | Place of service code | `place_of_service_code` |
| CLM09 | 2300 | Prior auth indicator (Y/N) | `prior_auth_required` |
| REF*G1 | 2300 | Prior auth number | `prior_auth_number` |
| SBR*P — SBR03 | 2000B | Payer ID | `payer_id` |
| NM1*PR — NM103 | 2010BB | Payer name | `payer_name` |

**Field confidence:** All EDI-extracted fields receive `field_confidence: 1.0`. The `field_confidence` map is omitted from the CMS write for EDI_837 claims; CMS defaults to 1.0 if absent.

**Error handling:**
- Malformed ISA envelope or unrecognized transaction set type: route entire claim to exception queue with `exception_type: FORMAT_UNRECOGNIZED`; do not attempt partial extraction.
- Missing required segment (e.g., no NM1*IL loop): set `extraction_status: HUMAN_REQUIRED`; set `field_confidence[<field>]: 0.0` for all fields that depended on that segment.
- Duplicate ISA13 control number found in audit log within past 30 calendar days: set `extraction_status: PENDING_DUPLICATE` before CMS write attempt.

**Output:** Structured field map conforming to NormalizedClaimRecord required fields (§9.1). No LLM involved; extraction is deterministic.

---

### 8.3 IDP Extraction Pipeline [A14]

> **Build deliverable:** This component does not exist and must be built in Wave 1 (~$35K). The contract below is the *internal service API specification* the build team must implement.

**Endpoint (internal service, not external):**
```
POST {IDP_BASE_URL}/v1/extract    — submit document for extraction
GET  {IDP_BASE_URL}/v1/extract/{document_id}  — poll extraction status (async variant)
```
`IDP_BASE_URL` stored in env var (secrets manager key: `IDP_BASE_URL`).

**POST /v1/extract — Request body (JSON):**
```json
{
  "document_id":       "UUID — generated by caller; used for idempotency and correlation",
  "claim_id":          "UUID — CMS claim record this document belongs to",
  "document_type":     "PDF | PORTAL_STRUCTURED | PORTAL_UNSTRUCTURED",
  "document_content":  "base64-encoded document bytes",
  "required_fields":   ["member_id", "rendering_provider_npi", "billing_provider_npi",
                        "date_of_service_start", "date_of_service_end", "icd10_codes",
                        "cpt_codes", "billed_amount", "payer_id", "prior_auth_required"]
}
```

**POST /v1/extract — Response (HTTP 200, synchronous):**
```json
{
  "document_id":           "UUID",
  "claim_id":              "UUID",
  "fields": {
    "<field_name>": {
      "value":              "string | number | YYYY-MM-DD",
      "confidence":         "float 0.0–1.0",
      "extraction_method":  "OCR | RULE_BASED | ML_EXTRACTION"
    }
  },
  "low_confidence_fields": ["array of field names where confidence < 0.85"],
  "extraction_status":     "COMPLETE | PARTIAL | FAILED"
}
```

**Error responses:**
```
HTTP 422  { "error": "DOCUMENT_UNREADABLE", "document_id": "UUID", "message": "string" }
HTTP 415  { "error": "FORMAT_UNSUPPORTED",  "document_type": "string" }
HTTP 504  { "error": "EXTRACTION_TIMEOUT",  "document_id": "UUID" }
```

**Timeout:** 30 seconds (synchronous path). For documents > 5 MB, caller must use async poll variant; polling interval: 5 s; max wait: 120 s.

**Retry:** `EXTRACTION_TIMEOUT`: retry once after 10 s using the same `document_id` (idempotent). `DOCUMENT_UNREADABLE` or `FORMAT_UNSUPPORTED`: do not retry; route to exception queue immediately.

**Throughput SLA (build requirement):** IDP pipeline must sustain ≥ 500 documents/hour to process all non-EDI daily volume within the 1-hour processing window target.

**Confidence threshold contract:** Any field in `low_confidence_fields` (confidence < 0.85) causes ADR-1 to set `extraction_status: HUMAN_REQUIRED` on the NormalizedClaimRecord. The IDP pipeline is not responsible for the HITL routing decision — it reports confidence; ADR-1 applies the threshold rule.

---

### 8.4 SLA Queue Management Module [A17]

**Contract status:** May be part of CMS or a standalone module. Confirm in Week 1 IT discovery. If CMS already provides queue assignment, replace this contract with the CMS queue endpoint.

**Endpoints:**
```
POST {QUEUE_BASE_URL}/v1/queue/assign     — assign claim to SLA tier
GET  {QUEUE_BASE_URL}/v1/queue/{claim_id} — read current queue assignment
```

**POST /v1/queue/assign — Request:**
```json
{
  "claim_id":       "UUID",
  "created_at":     "ISO 8601 UTC — claim receipt timestamp",
  "payer_id":       "string",
  "intake_channel": "EDI_837 | PDF | PORTAL"
}
```

**POST /v1/queue/assign — Response (HTTP 200):**
```json
{
  "queue_id":     "UUID",
  "sla_queue":    "PRIORITY | STANDARD | BATCH",
  "sla_deadline": "ISO 8601 UTC",
  "position":     "integer — position in queue at time of assignment"
}
```

**Queue tier assignment rules** (deterministic, no LLM):
| Tier | Condition |
|---|---|
| `PRIORITY` | `sla_deadline` is within 24 h of `created_at` |
| `STANDARD` | `sla_deadline` is 24 h – 72 h after `created_at` |
| `BATCH`    | `sla_deadline` is > 72 h after `created_at` |

**Fallback:** If `payer_id` has no registered SLA config: assign `STANDARD` tier, set `sla_deadline = created_at + 72 h`, emit `SLA_CONFIG_MISSING` event to ops log. Do not block claim processing.

**Timeout:** 5 seconds. On timeout or HTTP 5xx: assign `STANDARD` tier locally; log `QUEUE_ASSIGNMENT_DEGRADED` event; do not block claim. Reconcile on CMS recovery.

---

### 8.5 Exception Queue

**Endpoint:**
```
POST {EXCEPTION_QUEUE_URL}/v1/exceptions   — submit exception item
GET  {EXCEPTION_QUEUE_URL}/v1/exceptions/{exception_id} — read status
```

**POST /v1/exceptions — Request:**
```json
{
  "exception_id":          "UUID — agent-generated",
  "claim_id":              "UUID",
  "exception_type":        "LOW_CONFIDENCE_EXTRACTION | DUPLICATE_HOLD | FORMAT_UNRECOGNIZED | CMS_WRITE_FAILURE",
  "low_confidence_fields": [
    { "field": "string", "extracted_value": "string | null", "confidence": "float 0.0–1.0" }
  ],
  "required_action":       "HUMAN_REKEY | DUPLICATE_RESOLUTION | FORMAT_IDENTIFICATION | MANUAL_WRITE",
  "priority":              "HIGH | STANDARD",
  "source_agent":          "ADR-1",
  "created_at":            "ISO 8601 UTC"
}
```

**Priority assignment rules:**
- `HIGH`: `exception_type = CMS_WRITE_FAILURE`; or claim is missing `member_id` or `date_of_service_start`.
- `STANDARD`: all other exception types.

**Response (HTTP 201):**
```json
{ "queue_id": "UUID", "position": integer, "sla_resolution_by": "ISO 8601 UTC" }
```

**SLA:** Exception items must be resolved within 4 business hours to sustain daily throughput. Items unresolved at 4 h mark are auto-escalated to the operations supervisor queue.

**Timeout:** 5 seconds. On failure: persist exception record locally in durable store; retry on 1-minute intervals; alert ops after 3 consecutive failures.

---

### 8.6 Audit Log Store

**Endpoint:** `POST {AUDIT_LOG_URL}/v1/audit-entries` — async write, fire-and-forget.

**Write schema (JSON):**
```json
{
  "audit_id":          "UUID — agent-generated; primary key",
  "claim_id":          "UUID",
  "agent_id":          "ADR-1",
  "agent_version":     "semver string (e.g. 1.0.3)",
  "event_type":        "CLAIM_RECEIVED | EXTRACTION_COMPLETE | VALIDATION_COMPLETE | CMS_WRITE_SUCCESS | CMS_WRITE_FAILED | EXCEPTION_QUEUED | DUPLICATE_DETECTED",
  "event_timestamp":   "ISO 8601 UTC — immutable once written",
  "extraction_status": "AUTO_COMPLETE | HUMAN_REQUIRED | PENDING_DUPLICATE | null",
  "field_confidence":  { "<field_name>": "float 0.0–1.0" },
  "operator_id":       "string — user ID of human processor if HITL action; null if fully agentic",
  "outcome":           "SUCCESS | PENDING_HUMAN | FAILED | DUPLICATE_HOLD"
}
```

**Behavior:** Audit write must not block claim processing. Write failure handling: retry with backoff (1 s, 2 s, 4 s, 8 s); if all retries fail, write to local fallback file and emit `AUDIT_WRITE_FAILED` alert. Claim processing continues regardless.

**Retention:** 7 years from event date (HIPAA minimum for healthcare claims). Records are append-only; no modification or deletion within retention period.

---

## 9. Entity Data Models

### 9.1 NormalizedClaimRecord

This entity is the canonical data contract shared across all agents. ADR-1 creates it; all downstream agents read it via CMS. ADR-4 writes routing fields (§9.1.2). No other agent may write intake fields after ADR-1 creates the record.

**Primary key:** `claim_id` — UUID, immutable, generated by CMS on record creation.

#### 9.1.1 Intake Fields (written by ADR-1; immutable after creation)

| Field | Type | Required | Constraints |
|---|---|:---:|---|
| `claim_id` | UUID | Yes | Immutable; CMS-generated on POST |
| `source_claim_ref` | string | Yes | Max 50 chars; immutable; EDI ISA control number or portal transaction ID |
| `member_id` | string | Yes | Max 20 chars; payer-issued |
| `member_dob` | date | Yes | ISO 8601 `YYYY-MM-DD` |
| `member_name_last` | string | Yes | Max 60 chars |
| `member_name_first` | string | Yes | Max 60 chars |
| `rendering_provider_npi` | string | Yes | Exactly 10 digits; Luhn check required |
| `billing_provider_npi` | string | Yes | Exactly 10 digits; Luhn check required |
| `billing_provider_tax_id` | string | Yes | Exactly 9 digits; EIN format |
| `date_of_service_start` | date | Yes | ISO 8601 `YYYY-MM-DD`; immutable |
| `date_of_service_end` | date | Yes | ISO 8601 `YYYY-MM-DD`; must be ≥ `date_of_service_start`; immutable |
| `place_of_service_code` | string | Yes | Exactly 2 digits; valid CMS POS code list |
| `claim_type` | enum | Yes | `PROFESSIONAL \| INSTITUTIONAL \| DENTAL`; immutable |
| `icd10_codes` | array\<string\> | Yes | Min 1, max 12 items; each matches ICD-10-CM format `[A-Z][0-9]{2}(\.[0-9A-Z]{1,4})?` |
| `cpt_codes` | array\<string\> | Yes | Min 1, max 50 items; each is 5-digit CPT code with optional `-XX` 2-char modifier |
| `revenue_codes` | array\<string\> | No | Max 4-char each; present only if `claim_type = INSTITUTIONAL` |
| `drg_code` | string | No | Exactly 3 digits; present only if `claim_type = INSTITUTIONAL` |
| `billed_amount` | decimal(10,2) | Yes | > 0; USD; immutable |
| `currency` | string | Yes | Fixed value: `"USD"`; immutable |
| `payer_id` | string | Yes | Max 20 chars |
| `payer_name` | string | Yes | Max 100 chars |
| `plan_id` | string | Yes | Max 30 chars |
| `prior_auth_required` | boolean | Yes | |
| `prior_auth_number` | string | Conditional | Max 30 chars; required when `prior_auth_required = true`; must be null when `prior_auth_required = false` |
| `intake_channel` | enum | Yes | `EDI_837 \| PDF \| PORTAL`; immutable |
| `extraction_status` | enum | Yes | `AUTO_COMPLETE \| HUMAN_REQUIRED \| PENDING_DUPLICATE` |
| `field_confidence` | map\<string, float\> | Conditional | Required when `intake_channel ≠ EDI_837`; omit for EDI; values 0.0–1.0 |
| `sla_queue` | enum | Yes | `PRIORITY \| STANDARD \| BATCH` |
| `sla_deadline` | timestamp | Yes | ISO 8601 UTC; computed by queue module |
| `queue_assigned_at` | timestamp | Yes | ISO 8601 UTC; set when queue assignment completes |
| `intake_agent_version` | string | Yes | Semver; set by ADR-1 at write time |
| `created_at` | timestamp | Yes | ISO 8601 UTC; set by CMS on POST; immutable |
| `updated_at` | timestamp | Yes | ISO 8601 UTC; updated by CMS on any PUT |
| `created_by` | string | Yes | `"AGENT:ADR-1"` for agentic intake; `"OPERATOR:{user_id}"` for HITL-assisted |

#### 9.1.2 Routing Fields (written by ADR-4; null until triage completes)

| Field | Type | Default | Constraints |
|---|---|---|---|
| `routing_decision` | enum | `PENDING_TRIAGE` | `FAST_PATH \| CLINICAL_PATH \| PENDING_TRIAGE` |
| `routing_confidence` | float | null | 0.0–1.0; null until ADR-4 writes |
| `routing_confidence_fallback` | boolean | null | `true` when routed by fallback rule [A24]; null until ADR-4 writes |
| `clinical_indicators_detected` | array\<string\> | null | List of indicator strings; null until ADR-4 writes |
| `criteria_provisions_matched` | array\<string\> | null | List of codebook provision IDs; null until ADR-4 writes |
| `routing_reasoning_trace` | string | null | Chain-of-thought text; null until ADR-4 writes |
| `routing_agent_version` | string | null | Semver; null until ADR-4 writes |
| `routing_decided_at` | timestamp | null | ISO 8601 UTC; null until ADR-4 writes |
| `routing_mode` | enum | null | `SHADOW \| LIVE`; null until ADR-4 writes |

#### 9.1.3 Record State Machine

```
RECEIVED  — claim ingested by ADR-1; intake in progress
    ↓  (extraction complete, validation passes, CMS write succeeds)
QUEUED    — claim in SLA-prioritized queue; awaiting ADR-4 triage
    ↓  (ADR-4 shadow mode: routing_mode = SHADOW; record stays QUEUED)
    ↓  (ADR-4 live mode: routing_decision written)
FAST_PATH       — routed to ADR-5 Fast Path Adjudication
CLINICAL_PATH   — routed to ADR-6 Clinical Pre-Screening

RECEIVED → ON_HOLD  (extraction_status = HUMAN_REQUIRED or PENDING_DUPLICATE)
ON_HOLD  → QUEUED   (human resolves re-key or duplicate; HITL operator updates record)
ON_HOLD  is not terminal — claim must not remain ON_HOLD beyond 4 business hours (SLA)

FAST_PATH | CLINICAL_PATH → ADJUDICATED  (downstream agents complete processing)
ADJUDICATED is terminal for this workflow
```

**Immutability rules:**
- Fields marked immutable in §9.1.1 must not be modified after record creation.
- `routing_decision` field transitions: `PENDING_TRIAGE → FAST_PATH` or `PENDING_TRIAGE → CLINICAL_PATH` only. Cannot revert to `PENDING_TRIAGE` after a routing decision is written.
- `created_at` and `claim_id` are immutable forever.

---

### 9.2 ExceptionQueueEntry

| Field | Type | Required | Constraints |
|---|---|:---:|---|
| `exception_id` | UUID | Yes | Agent-generated; primary key; immutable |
| `claim_id` | UUID | Yes | Foreign key to NormalizedClaimRecord; immutable |
| `exception_type` | enum | Yes | `LOW_CONFIDENCE_EXTRACTION \| DUPLICATE_HOLD \| FORMAT_UNRECOGNIZED \| CMS_WRITE_FAILURE` |
| `low_confidence_fields` | array\<object\> | Conditional | Required when `exception_type = LOW_CONFIDENCE_EXTRACTION`; each object: `{field: string, extracted_value: string\|null, confidence: float}` |
| `required_action` | enum | Yes | `HUMAN_REKEY \| DUPLICATE_RESOLUTION \| FORMAT_IDENTIFICATION \| MANUAL_WRITE` |
| `priority` | enum | Yes | `HIGH \| STANDARD` |
| `resolution_status` | enum | Yes | `OPEN \| IN_PROGRESS \| RESOLVED \| ESCALATED`; default `OPEN` |
| `resolved_by` | string | Conditional | Operator user ID; required when `resolution_status = RESOLVED` |
| `resolved_at` | timestamp | Conditional | ISO 8601 UTC; required when `resolution_status = RESOLVED` |
| `source_agent` | string | Yes | Fixed: `"ADR-1"` |
| `created_at` | timestamp | Yes | ISO 8601 UTC; immutable |
| `sla_resolution_by` | timestamp | Yes | ISO 8601 UTC; `created_at + 4 business hours`; computed on creation |

**State machine:**
```
OPEN → IN_PROGRESS  (operator picks up item)
IN_PROGRESS → RESOLVED  (operator completes action; claim transitions back to QUEUED)
OPEN | IN_PROGRESS → ESCALATED  (SLA deadline passes without resolution)
ESCALATED → RESOLVED  (supervisor resolves)
```

---

### 9.3 AuditLogEntry

| Field | Type | Required | Constraints |
|---|---|:---:|---|
| `audit_id` | UUID | Yes | Agent-generated; primary key; immutable |
| `claim_id` | UUID | Yes | Foreign key to NormalizedClaimRecord; immutable |
| `agent_id` | string | Yes | `"ADR-1"` for intake events; `"ADR-4"` for routing events |
| `agent_version` | string | Yes | Semver |
| `event_type` | enum | Yes | `CLAIM_RECEIVED \| EXTRACTION_COMPLETE \| VALIDATION_COMPLETE \| CMS_WRITE_SUCCESS \| CMS_WRITE_FAILED \| EXCEPTION_QUEUED \| DUPLICATE_DETECTED` (ADR-1 events); `ROUTING_DECISION_LOGGED \| ROUTING_DECISION_WRITTEN` (ADR-4 events) |
| `event_timestamp` | timestamp | Yes | ISO 8601 UTC; immutable once written |
| `extraction_status` | enum | No | `AUTO_COMPLETE \| HUMAN_REQUIRED \| PENDING_DUPLICATE`; present on ADR-1 events only |
| `field_confidence` | map\<string, float\> | No | Present on ADR-1 EXTRACTION_COMPLETE events for non-EDI claims |
| `operator_id` | string | No | User ID of human processor if HITL action occurred; null for fully agentic events |
| `outcome` | enum | Yes | `SUCCESS \| PENDING_HUMAN \| FAILED \| DUPLICATE_HOLD` |

**Retention:** 7 years. Append-only. No record may be modified or deleted.

---

## 10. Validation Scenarios

### 10.1 Happy Path — EDI 837 Claim, End-to-End

**Input:** Well-formed EDI 837P transaction received via EDI channel. All required segments present. No prior submissions with matching member_id + date_of_service + provider_npi in CMS.

**Expected outcome:**
1. Format detected as `EDI_837`.
2. Parser extracts all required fields; `field_confidence` omitted (EDI = deterministic).
3. Completeness validation passes (all required fields present).
4. Duplicate check returns no match.
5. CMS POST returns HTTP 201; `claim_id` assigned.
6. Queue module assigns `sla_queue` tier based on payer SLA config; `sla_deadline` computed.
7. Audit log entry written: `event_type: CMS_WRITE_SUCCESS`, `extraction_status: AUTO_COMPLETE`, `outcome: SUCCESS`.
8. No exception queue entry created.
9. NormalizedClaimRecord state: `QUEUED`. `extraction_status: AUTO_COMPLETE`.
10. End-to-end processing time: < 5 seconds from receipt to QUEUED state.

---

### 10.2 Edge Cases

**EC-1: PDF with one field below confidence threshold**
- Input: PDF claim; IDP extraction returns `member_id` with confidence 0.82; all other fields ≥ 0.85.
- Expected: `extraction_status: HUMAN_REQUIRED`; `field_confidence: {member_id: 0.82, ...}`. Exception queue entry created with `exception_type: LOW_CONFIDENCE_EXTRACTION`, `low_confidence_fields: [{field: "member_id", extracted_value: "<extracted>", confidence: 0.82}]`, `required_action: HUMAN_REKEY`, `priority: HIGH` (member_id is identity-critical). CMS write does NOT occur until human resolves. NormalizedClaimRecord state: `ON_HOLD`.

**EC-2: Exact duplicate submission**
- Input: EDI 837 claim with `source_claim_ref`, `member_id`, `date_of_service_start`, and `rendering_provider_npi` all matching an existing CMS record created within the past 30 days.
- Expected: CMS POST returns HTTP 409. Agent sets `extraction_status: PENDING_DUPLICATE`. Exception queue entry with `exception_type: DUPLICATE_HOLD`, `required_action: DUPLICATE_RESOLUTION`. No second CMS write attempted. Audit entry: `event_type: DUPLICATE_DETECTED`.

**EC-3: CMS write fails on first attempt, succeeds on retry**
- Input: Well-formed claim; CMS POST returns HTTP 503 on first attempt.
- Expected: Agent retries after 2 s. Second attempt returns HTTP 201. Audit entry logged for both attempts: first with `outcome: FAILED`, second with `outcome: SUCCESS`. No exception queue entry created (retry succeeded).

**EC-4: Completely unrecognized format**
- Input: Incoming submission is a JPEG image (not EDI, not PDF, not portal JSON).
- Expected: Format detection returns `FORMAT_UNRECOGNIZED`. Agent does not invoke EDI parser or IDP pipeline. Exception queue entry with `exception_type: FORMAT_UNRECOGNIZED`, `required_action: FORMAT_IDENTIFICATION`, `priority: STANDARD`. No CMS write attempted. Audit entry: `event_type: EXCEPTION_QUEUED`.

**EC-5: All fields at exactly the confidence threshold boundary**
- Input: PDF claim; all required fields return `confidence: 0.85` from IDP.
- Expected: No fields appear in `low_confidence_fields` (threshold is strictly < 0.85; 0.85 passes). `extraction_status: AUTO_COMPLETE`. CMS write proceeds without HITL.

**EC-6: Prior auth required but number absent**
- Input: PDF claim; `prior_auth_required: true`; `prior_auth_number` field not found by IDP (confidence 0.0).
- Expected: `low_confidence_fields` includes `prior_auth_number`. `extraction_status: HUMAN_REQUIRED`. Exception queue entry. CMS write deferred.

**EC-7: Claim volume spike exceeds 2× daily average within a 30-minute window**
- Input: 834 claims received in 30 minutes (vs. 1,667/day ÷ 48 = ~35/30 min baseline).
- Expected: Agent continues processing. Ops alert emitted: `VOLUME_SPIKE` event with current rate and timestamp. No claims dropped or rejected. Queue tier assignment adapts based on individual claim SLA deadlines (spike does not override tier logic).

---

### 10.3 Failure Mode Scenarios

**FM-1: CMS unavailable for 20 minutes**
- Trigger: CMS POST returns HTTP 503; all 3 retries (2 s, 4 s, 8 s) exhaust.
- Expected: (1) Claims persisted locally with idempotency keys. (2) `CMS_UNAVAILABLE` alert posted to ops channel within 30 s of first exhausted retry cycle. (3) Agent continues accepting and extracting new claims; all pend locally. (4) Agent retries CMS on 5-minute intervals. (5) When CMS recovers, local queue replays in FIFO order. (6) Duplicate writes prevented by idempotency key check. (7) All claims eventually reach `QUEUED` state; SLA clock accounts for delay.

**FM-2: IDP extraction pipeline unavailable**
- Trigger: IDP POST returns HTTP 504 on first attempt and retry.
- Expected: (1) Affected PDF/portal claims routed to exception queue with `exception_type: CMS_WRITE_FAILURE` (extraction prerequisite failed), `required_action: MANUAL_WRITE`. (2) EDI 837 claims are unaffected — they bypass IDP entirely. (3) Ops alert generated with `IDP_UNAVAILABLE` flag. (4) When IDP recovers, exception queue items can be resubmitted; agent re-runs extraction.

**FM-3: Malformed EDI 837 — invalid ISA envelope**
- Trigger: EDI transaction received with corrupted ISA header (wrong element count).
- Expected: (1) Parser throws structural parse error before any segment extraction. (2) Exception queue entry created: `exception_type: FORMAT_UNRECOGNIZED`, `required_action: FORMAT_IDENTIFICATION`. (3) No partial extraction attempted — a partially-extracted EDI record with some fields at confidence 1.0 and others at 0.0 would be misleading. (4) Submitter notification triggered via exception queue resolution workflow.

---

## 11. Governance

### 11.1 HIPAA Compliance

ADR-1 processes Protected Health Information (PHI) including member names, dates of birth, provider NPIs, diagnosis codes, and treatment information. The following constraints are mandatory:

| Requirement | Implementation |
|---|---|
| PHI access logging | Every CMS read and write by ADR-1 must generate an audit log entry with `operator_id` (human) or `agent_id: ADR-1` (agentic). No PHI access without a corresponding audit record. |
| PHI storage scope | PHI must not be persisted outside of: (1) the CMS system, (2) the audit log store, (3) the exception queue. Ephemeral claim data held in the agent's prompt context during processing is not persisted; it exists only for the duration of a single claim's processing call. |
| PHI in transit | All API calls (CMS, IDP, queue, audit log) must use TLS 1.2 or higher. |
| Test data | Non-production environments must use synthetic or de-identified claim data. Real PHI must not be used in development, staging, or test environments. |
| Breach notification | If the audit log or exception queue is exposed without authorization, the incident response team must be notified within 1 hour. |

### 11.2 Audit Trail Requirements

Every claim processed by ADR-1 must produce at minimum the following audit log entries:

| Event | When | Required Fields |
|---|---|---|
| `CLAIM_RECEIVED` | On receipt of raw submission | `claim_id`, `intake_channel`, `event_timestamp`, `agent_version` |
| `EXTRACTION_COMPLETE` | After parse/IDP extraction completes | `claim_id`, `extraction_status`, `field_confidence` (non-EDI), `outcome` |
| `CMS_WRITE_SUCCESS` or `CMS_WRITE_FAILED` | After CMS POST attempt | `claim_id`, `outcome`, `event_timestamp` |
| `EXCEPTION_QUEUED` | When claim is routed to exception queue | `claim_id`, `exception_type`, `required_action` |

**Retention:** 7 years from `event_timestamp`. Records are append-only and must be stored in a tamper-evident system.

### 11.3 HITL Approval Gate

When `extraction_status = HUMAN_REQUIRED`, the following SLA applies:

| Action | Owner | SLA |
|---|---|---|
| Human processor picks up exception item | Operations team | Within 4 business hours of `created_at` |
| Human processor completes re-key or resolution | Operations team | Within 4 business hours of picking up |
| Auto-escalation to supervisor if unresolved | System | At `sla_resolution_by` timestamp |

Human processor corrections must be logged with `operator_id` and `resolved_at`. The corrected claim re-enters the processing pipeline and receives a new audit entry with `outcome: SUCCESS` and `operator_id` populated.

### 11.4 Override Mechanism

A human operator can override ADR-1's escalation decision in the following cases:
- Override a `PENDING_DUPLICATE` hold: operator marks the duplicate check as resolved (e.g., resubmission after prior denial). Override logged with `operator_id`, `resolved_at`, and `override_reason` (free text, max 500 chars).
- Override a `FORMAT_UNRECOGNIZED` flag: operator manually identifies format and triggers re-extraction. Override logged identically.

No operator may override `extraction_status: AUTO_COMPLETE` to insert themselves into a fully-agentic decision — the agent's decision stands unless the claim is subsequently appealed through the downstream claims process.

---

*See `specs/assumptions.md` for full definitions of [A4], [A7], [A12], [A14], [A17], [A21], [U1].*  
*See `specs/volume-×-value-analysis.md` Section 4 for HITL cost derivation and build cost allocation.*  
*Shared entities (CMS API, normalized record schema, reuse matrix) are consistent with `specs/04b-capability-spec-triage.md`.*
