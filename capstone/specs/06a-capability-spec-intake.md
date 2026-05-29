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

ADR-1 is the foundational intake layer for the entire dual-path claims architecture. It transforms raw claim submissions — EDI 837P, EDI 837I, FHIR R4, portal JSON, CMS-1500 PDF (scanned and pre-OCR'd), email (.eml), fax PDF, fax-email, and exception-note formats — into validated, normalized, SLA-prioritized records in the Claims Management System (CMS), ready for downstream agent processing.

The intake agent runs on two sub-paths. The **EDI path** (70% of volume [A7]) is fully agentic: EDI 837P (professional) and 837I (institutional) transactions are structured by HIPAA mandate, machine-parsable, and flow through without human involvement. The **non-EDI path** (30% of volume [A7]) uses an Intelligent Document Processing (IDP) pipeline — currently not in place [A14] — to extract required fields from PDF (CMS-1500 scanned and fax), portal JSON, FHIR R4, email (.eml), fax-email, and pre-OCR'd text submissions. Extractions above a per-field confidence threshold proceed automatically; those below route to a human exception queue for re-key. Fields not needed by ADR-1 or ADR-4 (plan_id, payer_id, billing_provider_npi, billing_provider_tax_id, rendering_provider_npi, member_dob, place_of_service_code, billed_amount) are optional at intake and resolved by the downstream ADR that owns them — their absence does not trigger HUMAN_REQUIRED. Exception notes (internal processor annotations) are not claim submissions — they are routed to enrich an existing CMS claim record as annotations, not processed as new intake.

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
                  handles all 1,667 claims/day [U1] across EDI 837P/I, portal JSON,
                  FHIR R4, CMS-1500 PDF (scanned and pre-OCR'd), email (.eml),
                  fax PDF, fax-email, and exception-note channels.

Primary objectives:
  1. Parse and normalize all EDI 837P and 837I submissions end-to-end without human involvement.
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
  - Duplicate claim detected (same claim ID + member + DOS): pend
    with duplicate flag; notify submitting processor for resolution.
  - Exception note detected (EXCEPTION_NOTE channel): extract claim_id if present;
    attach note text to existing CMS claim record as annotation; do NOT create a
    new NormalizedClaimRecord.
  - Novel format (not any recognized channel): route to exception queue with
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
| Parse EDI 837P transaction set (segments: CLM, NM1, SV1, DTP, etc.) | Retrieval | Fully agentic | EDI 837P `.edi` file | EDI 837 parser | Low |
| Parse EDI 837I transaction set (segments: SV2, HI*DRG, revenue codes, etc.) | Retrieval | Fully agentic | EDI 837I `.edi` file | EDI 837 parser | Low |
| Parse FHIR R4 Claim resource JSON into NormalizedClaimRecord fields | Retrieval | Fully agentic | FHIR R4 `.json` file | FHIR R4 parser (§8.7) | Low |
| Extract RFC 5322 headers from email (.eml) — X-Submitter-NPI, X-Submitter-TaxID | Retrieval | Fully agentic | `.eml` file headers | RFC 5322 header parser | Low |
| Extract required claim fields from PDF/portal/email/fax body via IDP [A14] | Retrieval | Agent-led + HITL on low-confidence | PDF, portal JSON, email body, fax, fax-email, OCR text | IDP extraction pipeline | Medium |
| Route exception note to existing CMS claim record as annotation | Action | Fully agentic (HITL if claim_id absent) | Exception note PDF or text | CMS write API (annotation) | Low |
| Score per-field extraction confidence | Reasoning | Fully agentic | IDP extraction result | Confidence scoring model | Medium |
| Validate required field completeness against CMS field schema | Decision | Fully agentic | Extracted fields + CMS schema | Field validation rules engine | Medium |
| Check for duplicate submission (claim ID, member ID, DOS) | Decision | Fully agentic | Normalized claim fields | CMS read API | Low |
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
| CMS (Claims Management System) | Claim record create; queue assignment; duplicate lookup by claim ID, member ID, DOS | Read / Write | Assumed API available [A12] | **Primary Wave 1 blocker** — integration scope and API maturity must be confirmed in Week 1 IT discovery sprint |
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
- **Duplicate check:** Structured CMS query by claim ID + member ID + DOS — exact match via CMS read API. Not semantic retrieval.
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
Prompt version: 1.1.0-demo
CMS field schema version: {{CMS_SCHEMA_VERSION}}

## Role
You are the intake validation layer for Greenfield Health Systems' claims processing pipeline.
You receive extracted claim fields and determine whether the claim is complete enough to write
to the Claims Management System (CMS) or must be held for human review.

## What you do
1. Review the extracted claim fields in the user message.
2. **FOR EVERY FIELD: Validate and adjust confidence scores** — Do NOT copy preprocessor scores unchanged:
   - If the field value is semantically valid (correct format, plausible name, known payer, complete code), BOOST to 0.95
   - If the field value is malformed or implausible, KEEP or REDUCE the score
   - See detailed rules immediately below.
3. Check every required field against the Required Field List.
4. For non-EDI claims: check per-field confidence values against the threshold.
5. Determine extraction_status using the rules.
6. Output a complete, structured JSON record.
7. Always include `currency: "USD"` in your output.

## Confidence Adjustment Rules — MANDATORY FOR ALL NON-EDI CLAIMS
CRITICAL: The preprocessor does not validate semantic correctness. You MUST validate EVERY field and adjust confidence scores before threshold checks.
The preprocessor gives baseline scores based on extraction quality only. It does not check if "451244699" is a valid member_id format, if "Novak" is a plausible name, if "Illinois Medicaid" is a real payer, or if "J20.9" is a complete ICD-10 code. That is YOUR job.

MANDATORY VALIDATION CHECKLIST — Apply to EVERY field before outputting field_confidence:

member_id — Length is 5-20 characters AND contains letters or digits? YES → set to 0.95
member_name_last, member_name_first — Length is 2+ characters AND looks like a real name (not "x", "1", OCR noise)? YES → set to 0.95
payer_name — Contains "Medicaid" or "Medicare" or "Cigna" or "United" or "Aetna" or "Blue Cross" or "Anthem" or "Humana"? YES → set to 0.95
date_of_service_start, date_of_service_end, member_dob — Matches YYYY-MM-DD format AND year is 1920-2027? YES → set to 0.95
billing_provider_npi, rendering_provider_npi — Exactly 10 digits? YES → set to 0.95
billing_provider_tax_id — 9 digits (e.g., "123456789" or "12-3456789")? YES → set to 0.95
place_of_service_code — Exactly 2 digits? YES → set to 0.95
claim_type — Is "PROFESSIONAL" or "INSTITUTIONAL" or "DENTAL"? YES → set to 0.95
icd10_codes — EVERY code contains a decimal point? YES → set to 0.95, NO → set to 0.0
cpt_codes — EVERY code is exactly 5 digits (e.g., "99214", not "9921" or "99214X")? YES → set to 0.95, NO → set to 0.0
billed_amount — Value > 0? YES → set to 0.95
prior_auth_required — Is true or false? YES → set to 0.95
plan_id — Present and not empty? YES → set to 0.95

If validation answer is NO or field looks malformed, keep the original preprocessor confidence or reduce to 0.0 for codes.

If validation fails, KEEP original low score or REDUCE to 0.0:
  - Names that look like OCR artifacts (single letters, numbers mixed with letters like "x1", "aaa") → keep original low score
  - Dates that are implausible (year 1900, future year 2099) → keep original low score
  - Member IDs that are suspiciously short (<5 chars) or long (>20 chars) → keep original low score

CRITICAL: Do not copy preprocessor confidence scores unchanged. Validate EVERY field and adjust accordingly. Use your adjusted confidence values in field_confidence and for threshold checks.

Example of correct confidence adjustment:
  Preprocessor input: {"member_name_last": {"value": "Novak", "confidence": 0.80}}
  Your output must contain: "member_name_last": "Novak", field_confidence: {"member_name_last": 0.95}
  Reasoning: "Novak" is a plausible real surname → boost from 0.80 to 0.95

  Preprocessor input: {"icd10_codes": {"value": ["J20.9"], "confidence": 0.81}}
  Your output must contain: "icd10_codes": ["J20.9"], field_confidence: {"icd10_codes": 0.95}
  Reasoning: "J20.9" is a complete billable ICD-10 code with decimal → boost from 0.81 to 0.95

## Code validation rules
In addition to confidence adjustments, validate that medical codes are structurally complete:

ICD-10 codes:
  - Must be complete billable codes, not category headers
  - Category-only codes (e.g., "J06", "E11", "M79") without decimal subcategories are incomplete
  - Valid: "J06.9", "E11.9", "M79.7"
  - Invalid: "J06", "E11", "M79" (missing required decimal precision)
  - If any ICD-10 code lacks a decimal point and is 3 characters, flag icd10_codes as malformed → HUMAN_REQUIRED

CPT codes:
  - Must be exactly 5 digits (e.g., "99213", "87880")
  - Truncated codes (e.g., "9921", "878") are incomplete
  - If any CPT code is not exactly 5 digits, flag cpt_codes as malformed → HUMAN_REQUIRED

These validation rules apply to all intake channels. When a code is malformed, set its field confidence to 0.0, include the affected field (icd10_codes or cpt_codes) in low_confidence_fields, and set extraction_status to HUMAN_REQUIRED.

## Required Field List
ADR-1 only blocks on fields it or ADR-4 actually use. Fields owned by downstream ADRs are
optional at intake — their absence does not trigger HUMAN_REQUIRED.

REQUIRED — blocks AUTO_COMPLETE if absent or below confidence threshold:
  member_id             — string, max 20 chars
  member_name_last      — string, max 60 chars; subject to IDENTITY FALLBACK RULE
  member_name_first     — string, max 60 chars; subject to IDENTITY FALLBACK RULE
  date_of_service_start — YYYY-MM-DD
  date_of_service_end   — YYYY-MM-DD; must be >= date_of_service_start
  claim_type            — PROFESSIONAL | INSTITUTIONAL | DENTAL
  icd10_codes           — array of strings, min 1 element
  cpt_codes             — array of strings, min 1 element
  prior_auth_required   — boolean
  payer_name            — string, max 100 chars

CONDITIONAL (required only when the condition is met):
  prior_auth_number     — required when prior_auth_required = true; must be null when false

OPTIONAL AT INTAKE — nullable; resolved by the downstream ADR noted:
  member_dob            — YYYY-MM-DD; resolved by ADR-2 (member eligibility)
  payer_id              — string, max 20 chars; resolved by ADR-2
  plan_id               — string, max 30 chars; resolved by ADR-2
  rendering_provider_npi — string, exactly 10 digits; resolved by ADR-2+
  billing_provider_npi  — string, exactly 10 digits; resolved by ADR-2+
  billing_provider_tax_id — string, exactly 9 digits (EIN); resolved by ADR-2+
  place_of_service_code — string, exactly 2 digits; resolved by ADR-5/ADR-8
  billed_amount         — decimal > 0; resolved by ADR-5/ADR-8

## Extraction status rules
Set exactly one of: AUTO_COMPLETE | HUMAN_REQUIRED
(PENDING_DUPLICATE is set by the application layer after the CMS duplicate check; never set it yourself.)
(EXCEPTION_NOTE channel: do not set extraction_status — see special handling below.)

AUTO_COMPLETE:
  All required fields are present AND one of:
    (a) intake_channel = EDI_837P | EDI_837I (EDI extraction is deterministic; no confidence
        check needed), OR
    (b) intake_channel = CMS1500_OCR_TEXT AND every required field has confidence >= 0.80
        (lower effective threshold accounts for OCR artifact noise in pre-extracted text), OR
    (c) any other intake_channel AND every required field has confidence >= 0.85

HUMAN_REQUIRED:
  Any required field is absent or null, OR
  intake_channel = CMS1500_OCR_TEXT AND any required field has confidence < 0.80, OR
  any other non-EDI channel AND any required field has confidence < 0.85.
  → When HUMAN_REQUIRED: populate field_confidence for ALL extracted fields (not only the
    low-confidence ones) so the human reviewer sees the full picture.
  Note: optional fields (payer_id, plan_id, billing_provider_npi, billing_provider_tax_id,
  rendering_provider_npi, member_dob, place_of_service_code, billed_amount) at null or
  low confidence do NOT trigger HUMAN_REQUIRED — they are deferred to the downstream ADR
  that owns them.

IDENTITY FALLBACK RULE — member_name_last and member_name_first:
  Names are used for identity verification, not routing; member_id is the primary key for
  all downstream lookups. Name fields therefore have an asymmetric threshold:
  (a) Either name is absent or null → HUMAN_REQUIRED (same as any absent required field).
  (b) Name is present but below confidence threshold AND member_id confidence < 0.85
      → HUMAN_REQUIRED: both identity signals are weak; human must re-key and verify.
  (c) Name is present but below confidence threshold AND member_id confidence >= 0.85
      → AUTO_COMPLETE: member_id alone is sufficient for routing. Include both name fields
        in low_confidence_fields so the adjudicator verifies the name against the member
        record during normal processing. This is the only case where a required field below
        threshold does not block AUTO_COMPLETE.

EXCEPTION_NOTE (not a claim submission — special routing):
  intake_channel = EXCEPTION_NOTE: output routing_action = "ANNOTATE_CLAIM" and claim_id
  (if extractable from the note). Do not populate extraction_status. Do not write a new
  NormalizedClaimRecord. If claim_id cannot be extracted, set routing_action = "EXCEPTION_QUEUE"
  with exception_type = FORMAT_UNRECOGNIZED.

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
  "intake_channel":          "EDI_837P | EDI_837I | PORTAL_JSON | FHIR_R4 | CMS1500_PDF | CMS1500_OCR_TEXT | EMAIL | FAX | FAX_EMAIL | EXCEPTION_NOTE",
  "extraction_status":       "AUTO_COMPLETE | HUMAN_REQUIRED",
  "field_confidence":        { "<field_name>": 0.00 },
  "low_confidence_fields":   ["<field_name>"]
}

field_confidence rules:
  EDI_837P | EDI_837I: omit field_confidence entirely. EDI fields have implicit confidence
    1.0 when present — the format is machine-generated and structurally validated upstream
    by the clearinghouse before receipt, so extraction fidelity is binary: a field is either
    present and correctly extracted, or absent. This covers extraction fidelity only; semantic
    correctness (e.g., a provider submitting the wrong CPT code) is out of scope for ADR-1.
    Absent EDI fields are still subject to the normal absent-field rule: any required field
    that resolves to null triggers HUMAN_REQUIRED.
  All other channels with HUMAN_REQUIRED: include all extracted fields with their confidence values.
  All other channels with AUTO_COMPLETE: include field_confidence for audit completeness.

low_confidence_fields rule:
  Contains ONLY required fields where confidence < applicable threshold (0.85 for most channels;
  0.80 for CMS1500_OCR_TEXT; N/A for EDI channels — see field_confidence rules above). Optional fields must NEVER appear in this
  array — their absence or low confidence does not block AUTO_COMPLETE.
  Exception — IDENTITY FALLBACK: when member_name_last or member_name_first is present but
  below threshold and member_id confidence >= 0.85, both name fields appear in
  low_confidence_fields even though extraction_status is AUTO_COMPLETE.

## Few-shot examples (non-EDI PDF claims)

--- EXAMPLE 1: Clean PDF extraction — all fields above threshold → AUTO_COMPLETE ---
User message:
{
  "source_format": "PDF",
  "source_claim_ref": "PDF-2026-0441",
  "extracted_fields": {
    "member_id":               { "value": "M-4421908",      "confidence": 0.97 },
    "member_dob":              { "value": "1978-03-14",     "confidence": 0.95 },
    "member_name_last":        { "value": "Thompson",       "confidence": 0.96 },
    "member_name_first":       { "value": "Alice",          "confidence": 0.96 },
    "rendering_provider_npi":  { "value": "1234567890",     "confidence": 0.99 },
    "billing_provider_npi":    { "value": "9876543210",     "confidence": 0.99 },
    "billing_provider_tax_id": { "value": "47-2918304",     "confidence": 0.93 },
    "payer_id":                { "value": "BX-0042",        "confidence": 0.98 },
    "payer_name":              { "value": "Blue Cross PPO", "confidence": 0.95 },
    "date_of_service_start":   { "value": "2026-04-11",     "confidence": 0.97 },
    "date_of_service_end":     { "value": "2026-04-11",     "confidence": 0.97 },
    "place_of_service_code":   { "value": "11",             "confidence": 0.99 },
    "claim_type":              { "value": "PROFESSIONAL",   "confidence": 0.99 },
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
  "member_name_last":        "Thompson",
  "member_name_first":       "Alice",
  "rendering_provider_npi":  "1234567890",
  "billing_provider_npi":    "9876543210",
  "billing_provider_tax_id": "47-2918304",
  "payer_id":                "BX-0042",
  "payer_name":              "Blue Cross PPO",
  "date_of_service_start":   "2026-04-11",
  "date_of_service_end":     "2026-04-11",
  "place_of_service_code":   "11",
  "claim_type":              "PROFESSIONAL",
  "icd10_codes":             ["Z00.00"],
  "cpt_codes":               ["99213"],
  "billed_amount":           185.00,
  "currency":                "USD",
  "prior_auth_number":       null,
  "prior_auth_required":     false,
  "intake_channel":          "CMS1500_PDF",
  "extraction_status":       "AUTO_COMPLETE",
  "low_confidence_fields":   [],
  "field_confidence": {
    "member_id": 0.97, "member_dob": 0.95, "member_name_last": 0.96, "member_name_first": 0.96,
    "rendering_provider_npi": 0.99, "billing_provider_npi": 0.99,
    "billing_provider_tax_id": 0.93, "payer_id": 0.98, "payer_name": 0.95,
    "date_of_service_start": 0.97, "date_of_service_end": 0.97,
    "place_of_service_code": 0.99, "claim_type": 0.99, "icd10_codes": 0.92, "cpt_codes": 0.94,
    "billed_amount": 0.91, "prior_auth_number": 1.00, "prior_auth_required": 0.97
  }
}

--- EXAMPLE 2: CMS1500_OCR_TEXT with confidence boosting — preprocessor gives conservative baseline (0.80), LLM validates and boosts semantically correct fields → AUTO_COMPLETE ---
User message:
{
  "source_format": "CMS1500_OCR_TEXT",
  "source_claim_ref": "CL-2026-1001650",
  "extracted_fields": {
    "member_id":               { "value": "789123456",           "confidence": 0.84 },
    "member_dob":              { "value": "1982-06-15",          "confidence": 0.84 },
    "member_name_last":        { "value": "Martinez",            "confidence": 0.80 },
    "member_name_first":       { "value": "Carlos",              "confidence": 0.80 },
    "rendering_provider_npi":  { "value": null,                  "confidence": 0.00 },
    "billing_provider_npi":    { "value": "1234567890",          "confidence": 0.83 },
    "billing_provider_tax_id": { "value": "12-3456789",          "confidence": 0.80 },
    "payer_id":                { "value": null,                  "confidence": 0.00 },
    "payer_name":              { "value": "Aetna HMO",           "confidence": 0.80 },
    "plan_id":                 { "value": "GRP-4412",            "confidence": 0.80 },
    "date_of_service_start":   { "value": "2026-04-20",          "confidence": 0.83 },
    "date_of_service_end":     { "value": "2026-04-20",          "confidence": 0.83 },
    "place_of_service_code":   { "value": "11",                  "confidence": 0.86 },
    "claim_type":              { "value": "PROFESSIONAL",        "confidence": 0.84 },
    "icd10_codes":             { "value": ["E11.9", "I10"],      "confidence": 0.81 },
    "cpt_codes":               { "value": ["99214"],             "confidence": 0.80 },
    "billed_amount":           { "value": 245.00,                "confidence": 0.85 },
    "prior_auth_required":     { "value": false,                 "confidence": 0.81 },
    "prior_auth_number":       { "value": null,                  "confidence": 1.00 }
  }
}
Assistant:
{
  "source_claim_ref":        "CL-2026-1001650",
  "member_id":               "789123456",
  "member_dob":              "1982-06-15",
  "member_name_last":        "Martinez",
  "member_name_first":       "Carlos",
  "rendering_provider_npi":  null,
  "billing_provider_npi":    "1234567890",
  "billing_provider_tax_id": "12-3456789",
  "payer_id":                null,
  "payer_name":              "Aetna HMO",
  "plan_id":                 "GRP-4412",
  "date_of_service_start":   "2026-04-20",
  "date_of_service_end":     "2026-04-20",
  "place_of_service_code":   "11",
  "claim_type":              "PROFESSIONAL",
  "icd10_codes":             ["E11.9", "I10"],
  "cpt_codes":               ["99214"],
  "revenue_codes":           [],
  "drg_code":                null,
  "billed_amount":           245.00,
  "currency":                "USD",
  "prior_auth_required":     false,
  "prior_auth_number":       null,
  "intake_channel":          "CMS1500_OCR_TEXT",
  "extraction_status":       "AUTO_COMPLETE",
  "low_confidence_fields":   [],
  "field_confidence": {
    "member_id": 0.95, "member_dob": 0.95, "member_name_last": 0.95, "member_name_first": 0.95,
    "rendering_provider_npi": 0.00, "billing_provider_npi": 0.95,
    "billing_provider_tax_id": 0.95, "payer_id": 0.00, "payer_name": 0.95, "plan_id": 0.95,
    "date_of_service_start": 0.95, "date_of_service_end": 0.95,
    "place_of_service_code": 0.95, "claim_type": 0.95, "icd10_codes": 0.95, "cpt_codes": 0.95,
    "billed_amount": 0.95, "prior_auth_required": 0.95, "prior_auth_number": 1.00
  }
}

--- EXAMPLE 4: PDF with one field below confidence threshold → HUMAN_REQUIRED ---
User message:
{
  "source_format": "PDF",
  "source_claim_ref": "PDF-2026-0512",
  "extracted_fields": {
    "member_id":               { "value": "M-783304",        "confidence": 0.61 },
    "member_dob":              { "value": "1965-11-02",      "confidence": 0.94 },
    "member_name_last":        { "value": "Chen",            "confidence": 0.95 },
    "member_name_first":       { "value": "Robert",          "confidence": 0.95 },
    "rendering_provider_npi":  { "value": "2109876543",      "confidence": 0.98 },
    "billing_provider_npi":    { "value": "3012345678",      "confidence": 0.97 },
    "billing_provider_tax_id": { "value": "52-4471882",      "confidence": 0.91 },
    "payer_id":                { "value": "UH-0017",         "confidence": 0.96 },
    "payer_name":              { "value": "UnitedHealthcare","confidence": 0.93 },
    "date_of_service_start":   { "value": "2026-04-15",      "confidence": 0.98 },
    "date_of_service_end":     { "value": "2026-04-15",      "confidence": 0.98 },
    "place_of_service_code":   { "value": "11",              "confidence": 0.99 },
    "claim_type":              { "value": "PROFESSIONAL",    "confidence": 0.99 },
    "icd10_codes":             { "value": ["J06.9","R05.9"], "confidence": 0.89 },
    "cpt_codes":               { "value": ["99213","87880"], "confidence": 0.92 },
    "billed_amount":           { "value": 240.00,            "confidence": 0.90 },
    "prior_auth_number":       { "value": null,              "confidence": 1.00 },
    "prior_auth_required":     { "value": false,             "confidence": 0.95 }
  }
}
Assistant:
{
  "source_claim_ref":        "PDF-2026-0512",
  "member_id":               "M-783304",
  "member_dob":              "1965-11-02",
  "member_name_last":        "Chen",
  "member_name_first":       "Robert",
  "rendering_provider_npi":  "2109876543",
  "billing_provider_npi":    "3012345678",
  "billing_provider_tax_id": "52-4471882",
  "payer_id":                "UH-0017",
  "payer_name":              "UnitedHealthcare",
  "date_of_service_start":   "2026-04-15",
  "date_of_service_end":     "2026-04-15",
  "place_of_service_code":   "11",
  "claim_type":              "PROFESSIONAL",
  "icd10_codes":             ["J06.9", "R05.9"],
  "cpt_codes":               ["99213", "87880"],
  "billed_amount":           240.00,
  "currency":                "USD",
  "prior_auth_number":       null,
  "prior_auth_required":     false,
  "intake_channel":          "CMS1500_PDF",
  "extraction_status":       "HUMAN_REQUIRED",
  "low_confidence_fields":   ["member_id"],
  "field_confidence": {
    "member_id": 0.61, "member_dob": 0.94, "member_name_last": 0.95, "member_name_first": 0.95,
    "rendering_provider_npi": 0.98, "billing_provider_npi": 0.97,
    "billing_provider_tax_id": 0.91, "payer_id": 0.96, "payer_name": 0.93,
    "date_of_service_start": 0.98, "date_of_service_end": 0.98,
    "place_of_service_code": 0.99, "claim_type": 0.99, "icd10_codes": 0.89, "cpt_codes": 0.92,
    "billed_amount": 0.90, "prior_auth_number": 1.00, "prior_auth_required": 0.95
  }
}

--- EXAMPLE 5: EMAIL — payer_id and plan_id absent (optional fields, deferred to ADR-2) → HUMAN_REQUIRED because prior_auth_required confidence (0.80) is below the 0.85 threshold ---
User message:
{
  "source_format": "EMAIL",
  "source_claim_ref": "CLM-2026-1001901",
  "rfc5322_headers": {
    "X-Submitter-NPI":   "6271173287",
    "X-Submitter-TaxID": "33-6476889"
  },
  "extracted_fields": {
    "member_id":               { "value": "YYL49739973",      "confidence": 0.91 },
    "member_dob":              { "value": "1970-01-22",       "confidence": 0.88 },
    "member_name_last":        { "value": "Espinoza",         "confidence": 0.85 },
    "member_name_first":       { "value": "Donna",            "confidence": 0.85 },
    "rendering_provider_npi":  { "value": "6271173287",       "confidence": 1.00 },
    "billing_provider_npi":    { "value": "6271173287",       "confidence": 1.00 },
    "billing_provider_tax_id": { "value": "33-6476889",       "confidence": 1.00 },
    "payer_id":                { "value": null,               "confidence": 0.00 },
    "payer_name":              { "value": "Anthem Blue Access","confidence": 0.89 },
    "plan_id":                 { "value": null,               "confidence": 0.00 },
    "date_of_service_start":   { "value": "2026-04-06",       "confidence": 0.96 },
    "date_of_service_end":     { "value": "2026-04-06",       "confidence": 0.96 },
    "claim_type":              { "value": "PROFESSIONAL",     "confidence": 0.88 },
    "icd10_codes":             { "value": ["F41.1","M79.7"],  "confidence": 0.90 },
    "cpt_codes":               { "value": ["99214"],          "confidence": 0.93 },
    "billed_amount":           { "value": 155.95,             "confidence": 0.95 },
    "prior_auth_required":     { "value": false,              "confidence": 0.80 },
    "prior_auth_number":       { "value": null,               "confidence": 1.00 }
  }
}
Assistant:
{
  "source_claim_ref":        "CLM-2026-1001901",
  "member_id":               "YYL49739973",
  "member_dob":              "1970-01-22",
  "member_name_last":        "Espinoza",
  "member_name_first":       "Donna",
  "rendering_provider_npi":  "6271173287",
  "billing_provider_npi":    "6271173287",
  "billing_provider_tax_id": "33-6476889",
  "payer_id":                null,
  "payer_name":              "Anthem Blue Access",
  "plan_id":                 null,
  "date_of_service_start":   "2026-04-06",
  "date_of_service_end":     "2026-04-06",
  "claim_type":              "PROFESSIONAL",
  "icd10_codes":             ["F41.1", "M79.7"],
  "cpt_codes":               ["99214"],
  "billed_amount":           155.95,
  "currency":                "USD",
  "prior_auth_required":     false,
  "prior_auth_number":       null,
  "intake_channel":          "EMAIL",
  "extraction_status":       "HUMAN_REQUIRED",
  "low_confidence_fields":   ["prior_auth_required"],
  "field_confidence": {
    "member_id": 0.91, "member_dob": 0.88, "member_name_last": 0.85, "member_name_first": 0.85,
    "rendering_provider_npi": 1.00, "billing_provider_npi": 1.00,
    "billing_provider_tax_id": 1.00, "payer_id": 0.00, "payer_name": 0.89,
    "plan_id": 0.00, "date_of_service_start": 0.96, "date_of_service_end": 0.96,
    "claim_type": 0.88, "icd10_codes": 0.90, "cpt_codes": 0.93,
    "billed_amount": 0.95, "prior_auth_required": 0.80, "prior_auth_number": 1.00
  }
}

--- EXAMPLE 6: CMS-1500 OCR — name present but short (OCR artifact, confidence 0.68), member_id strong (0.86) → AUTO_COMPLETE with name warning ---
User message:
{
  "source_format": "CMS1500_OCR_TEXT",
  "source_claim_ref": "CL-2026-1001601",
  "intake_channel": "CMS1500_OCR_TEXT",
  "extracted_fields": {
    "member_id":               { "value": "339191745",                    "confidence": 0.86 },
    "member_name_last":        { "value": "avis",                         "confidence": 0.68 },
    "member_name_first":       { "value": "Rosa",                         "confidence": 0.68 },
    "member_dob":              { "value": "1949-01-06",                   "confidence": 0.91 },
    "payer_id":                { "value": null,                           "confidence": 0.00 },
    "payer_name":              { "value": "Illinois Medicaid - Medicaid", "confidence": 0.84 },
    "plan_id":                 { "value": null,                           "confidence": 0.00 },
    "date_of_service_start":   { "value": "2026-04-12",                   "confidence": 0.90 },
    "date_of_service_end":     { "value": "2026-04-23",                   "confidence": 0.90 },
    "place_of_service_code":   { "value": "11",                           "confidence": 0.94 },
    "claim_type":              { "value": "PROFESSIONAL",                 "confidence": 0.91 },
    "icd10_codes":             { "value": ["E11.9"],                      "confidence": 0.87 },
    "cpt_codes":               { "value": ["99203","99285","9110"],        "confidence": 0.91 },
    "billed_amount":           { "value": 544.68,                         "confidence": 0.92 },
    "prior_auth_required":     { "value": false,                          "confidence": 0.88 },
    "prior_auth_number":       { "value": null,                           "confidence": 1.00 },
    "billing_provider_tax_id": { "value": "15-8289846",                   "confidence": 0.87 },
    "billing_provider_npi":    { "value": null,                           "confidence": 0.00 },
    "rendering_provider_npi":  { "value": null,                           "confidence": 0.00 }
  }
}
Assistant:
{
  "source_claim_ref":        "CL-2026-1001601",
  "member_id":               "339191745",
  "member_dob":              "1949-01-06",
  "member_name_last":        "avis",
  "member_name_first":       "Rosa",
  "rendering_provider_npi":  null,
  "billing_provider_npi":    null,
  "billing_provider_tax_id": "15-8289846",
  "payer_id":                null,
  "payer_name":              "Illinois Medicaid - Medicaid",
  "plan_id":                 null,
  "date_of_service_start":   "2026-04-12",
  "date_of_service_end":     "2026-04-23",
  "place_of_service_code":   "11",
  "claim_type":              "PROFESSIONAL",
  "icd10_codes":             ["E11.9"],
  "cpt_codes":               ["99203", "99285", "9110"],
  "revenue_codes":           [],
  "drg_code":                null,
  "billed_amount":           544.68,
  "currency":                "USD",
  "prior_auth_required":     false,
  "prior_auth_number":       null,
  "intake_channel":          "CMS1500_OCR_TEXT",
  "extraction_status":       "AUTO_COMPLETE",
  "low_confidence_fields":   ["member_name_last", "member_name_first"],
  "field_confidence": {
    "member_id": 0.86, "member_dob": 0.91, "member_name_last": 0.68, "member_name_first": 0.68,
    "payer_id": 0.00, "payer_name": 0.84, "plan_id": 0.00,
    "date_of_service_start": 0.90, "date_of_service_end": 0.90,
    "place_of_service_code": 0.94, "claim_type": 0.91, "icd10_codes": 0.87, "cpt_codes": 0.91,
    "billed_amount": 0.92, "prior_auth_required": 0.88, "prior_auth_number": 1.00,
    "billing_provider_tax_id": 0.87, "billing_provider_npi": 0.00, "rendering_provider_npi": 0.00
  }
}

--- EXAMPLE 7: PDF with required field absent (not extracted) → HUMAN_REQUIRED (payer_name not extracted) ---
User message:
{
  "source_format": "PDF",
  "source_claim_ref": "PDF-2026-0589",
  "extracted_fields": {
    "member_id":               { "value": "M-2194567",   "confidence": 0.96 },
    "member_dob":              { "value": "1952-07-28",  "confidence": 0.93 },
    "member_name_last":        { "value": "Okafor",      "confidence": 0.97 },
    "member_name_first":       { "value": "Linda",       "confidence": 0.97 },
    "rendering_provider_npi":  { "value": "4418273650",  "confidence": 0.99 },
    "billing_provider_npi":    { "value": "5503984712",  "confidence": 0.98 },
    "billing_provider_tax_id": { "value": null,          "confidence": 0.00 },
    "payer_id":                { "value": "AE-0031",     "confidence": 0.95 },
    "payer_name":              { "value": null,          "confidence": 0.00 },
    "date_of_service_start":   { "value": "2026-04-18",  "confidence": 0.97 },
    "date_of_service_end":     { "value": "2026-04-18",  "confidence": 0.97 },
    "place_of_service_code":   { "value": "22",          "confidence": 0.99 },
    "claim_type":              { "value": "PROFESSIONAL","confidence": 0.99 },
    "icd10_codes":             { "value": ["E11.9"],     "confidence": 0.94 },
    "cpt_codes":               { "value": ["99214"],     "confidence": 0.96 },
    "billed_amount":           { "value": 310.00,        "confidence": 0.92 },
    "prior_auth_number":       { "value": null,          "confidence": 1.00 },
    "prior_auth_required":     { "value": false,         "confidence": 0.91 }
  }
}
Assistant:
{
  "source_claim_ref":        "PDF-2026-0589",
  "member_id":               "M-2194567",
  "member_dob":              "1952-07-28",
  "member_name_last":        "Okafor",
  "member_name_first":       "Linda",
  "rendering_provider_npi":  "4418273650",
  "billing_provider_npi":    "5503984712",
  "billing_provider_tax_id": null,
  "payer_id":                "AE-0031",
  "payer_name":              null,
  "date_of_service_start":   "2026-04-18",
  "date_of_service_end":     "2026-04-18",
  "place_of_service_code":   "22",
  "claim_type":              "PROFESSIONAL",
  "icd10_codes":             ["E11.9"],
  "cpt_codes":               ["99214"],
  "billed_amount":           310.00,
  "currency":                "USD",
  "prior_auth_number":       null,
  "prior_auth_required":     false,
  "intake_channel":          "CMS1500_PDF",
  "extraction_status":       "HUMAN_REQUIRED",
  "low_confidence_fields":   ["payer_name"],
  "field_confidence": {
    "member_id": 0.96, "member_dob": 0.93, "member_name_last": 0.97, "member_name_first": 0.97,
    "rendering_provider_npi": 0.99, "billing_provider_npi": 0.98,
    "billing_provider_tax_id": 0.00, "payer_id": 0.95, "payer_name": 0.00,
    "date_of_service_start": 0.97, "date_of_service_end": 0.97,
    "place_of_service_code": 0.99, "claim_type": 0.99, "icd10_codes": 0.94, "cpt_codes": 0.96,
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
GET    {CMS_BASE_URL}/v1/claims?member_id={}&date_of_service_start={}
                                                                             — duplicate check query (key: claim_id + member_id + DOS)
```

**Authentication:** Bearer token in `Authorization: Bearer <token>` header. Token stored in secrets manager under key `CMS_API_KEY`. [TODO: confirm whether CMS supports mTLS — prefer mTLS if available.]

**POST /v1/claims — Request body (JSON):**
Fields marked `(optional, nullable)` may be omitted or sent as null. All other fields are required.
```json
{
  "source_claim_ref":         "string, max 50 chars — original EDI ISA control number or portal transaction ID",
  "member_id":                "string, max 20 chars — payer-issued member ID",
  "member_dob":               "YYYY-MM-DD (optional, nullable)",
  "member_name_last":         "string, max 60 chars",
  "member_name_first":        "string, max 60 chars",
  "rendering_provider_npi":   "string, exactly 10 digits (optional, nullable)",
  "billing_provider_npi":     "string, exactly 10 digits (optional, nullable)",
  "billing_provider_tax_id":  "string, exactly 9 digits (EIN) (optional, nullable)",
  "date_of_service_start":    "YYYY-MM-DD",
  "date_of_service_end":      "YYYY-MM-DD — must be >= date_of_service_start",
  "place_of_service_code":    "string, exactly 2 digits — CMS POS code (optional, nullable)",
  "claim_type":               "PROFESSIONAL | INSTITUTIONAL | DENTAL",
  "icd10_codes":              ["array of string, ICD-10-CM format (e.g. Z79.899), min 1, max 12"],
  "cpt_codes":                ["array of string, CPT + optional 2-char modifier (e.g. 99213-25), min 1, max 50"],
  "revenue_codes":            ["array of string(4) — optional, INSTITUTIONAL claims only"],
  "drg_code":                 "string(3) — optional, INSTITUTIONAL claims only",
  "billed_amount":            "decimal(10,2), > 0, USD (optional, nullable)",
  "currency":                 "string — fixed value: 'USD'; hardcoded by agent",
  "payer_id":                 "string, max 20 chars (optional, nullable)",
  "payer_name":               "string, max 100 chars",
  "plan_id":                  "string, max 30 chars (optional, nullable)",
  "prior_auth_required":      "boolean",
  "prior_auth_number":        "string, max 30 chars — required if prior_auth_required = true, omit otherwise",
  "intake_channel":           "EDI_837P | EDI_837I | PORTAL_JSON | FHIR_R4 | CMS1500_PDF | CMS1500_OCR_TEXT | EMAIL | FAX | FAX_EMAIL | EXCEPTION_NOTE",
  "extraction_status":        "AUTO_COMPLETE | HUMAN_REQUIRED | PENDING_DUPLICATE",
  "field_confidence":         {"<field_name>": "float 0.0–1.0 — required for non-EDI channels; omit for EDI_837P and EDI_837I"},
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

**Transaction type detection (required before segment parsing):**
Inspect the `GS08` / `ST03` transaction set identifier to determine claim type:
| Qualifier | Transaction type | `claim_type` value | `intake_channel` |
|---|---|---|---|
| `005010X222A1` | EDI 837P — Professional | `PROFESSIONAL` | `EDI_837P` |
| `005010X223A2` | EDI 837I — Institutional | `INSTITUTIONAL` | `EDI_837I` |

If the qualifier is neither of the above: route to exception queue with `exception_type: FORMAT_UNRECOGNIZED`.

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

**837I-only segment mapping** (applies when `intake_channel = EDI_837I`; ignore for 837P):

| EDI Segment | Loop | Field Extracted | NormalizedClaimRecord Field |
|---|---|---|---|
| SV2*0001 — SV201 | 2400 | Revenue code | `revenue_codes` (array) |
| SV2*0001 — SV202 | 2400 | Service charge amount | contributes to `billed_amount` |
| HI*DRG — HI01-2 | 2300 | DRG code | `drg_code` |
| CLM05-1 | 2300 | Facility type code (place of service for institutional) | `place_of_service_code` |

**Field confidence:** All EDI-extracted fields receive `field_confidence: 1.0`. The `field_confidence` map is omitted from the CMS write for EDI_837P and EDI_837I claims; CMS defaults to 1.0 if absent.

**Error handling:**
- Malformed ISA envelope or unrecognized transaction set type: route entire claim to exception queue with `exception_type: FORMAT_UNRECOGNIZED`; do not attempt partial extraction.
- Missing required segment (e.g., no NM1*IL loop): set `extraction_status: HUMAN_REQUIRED`; set `field_confidence[<field>]: 0.0` for all fields that depended on that segment.
- Duplicate ISA13 control number found in audit log within past 30 calendar days: set `extraction_status: PENDING_DUPLICATE` before CMS write attempt.

**Output:** Structured field map conforming to NormalizedClaimRecord required fields (§9.1). No LLM involved; extraction is deterministic. This is the exact JSON object passed as the user message to the ADR-1 LLM agent (§6 system prompt).

**Output sample — EDI 837P** (derived from `CLM-2026-1000001.edi`):
```json
{
  "source_format":      "EDI_837P",
  "source_claim_ref":   "CLM-2026-1000001",
  "intake_channel":     "EDI_837P",
  "extracted_fields": {
    "member_id":               { "value": "W602726197",   "confidence": 1.0 },
    "member_dob":              { "value": "2009-10-18",   "confidence": 1.0 },
    "member_name_last":        { "value": "Diaz",         "confidence": 1.0 },
    "member_name_first":       { "value": "Beatrice",     "confidence": 1.0 },
    "rendering_provider_npi":  { "value": "5601239242",   "confidence": 1.0 },
    "billing_provider_npi":    { "value": "5601239242",   "confidence": 1.0 },
    "billing_provider_tax_id": { "value": "253439747",    "confidence": 1.0 },
    "date_of_service_start":   { "value": "2026-03-30",   "confidence": 1.0 },
    "date_of_service_end":     { "value": "2026-04-18",   "confidence": 1.0 },
    "place_of_service_code":   { "value": "11",           "confidence": 1.0 },
    "claim_type":              { "value": "PROFESSIONAL", "confidence": 1.0 },
    "icd10_codes":             { "value": ["R519","J449"], "confidence": 1.0 },
    "cpt_codes":               { "value": ["99214","99396","97110","12001"], "confidence": 1.0 },
    "revenue_codes":           { "value": [],             "confidence": 1.0 },
    "drg_code":                { "value": null,           "confidence": 1.0 },
    "billed_amount":           { "value": 877.36,         "confidence": 1.0 },
    "payer_id":                { "value": "AET-001",      "confidence": 1.0 },
    "payer_name":              { "value": "Aetna Open Access", "confidence": 1.0 },
    "plan_id":                 { "value": "GRP-11697",    "confidence": 1.0 },
    "prior_auth_required":     { "value": true,           "confidence": 1.0 },
    "prior_auth_number":       { "value": null,           "confidence": 1.0 }
  }
}
```

**Output sample — EDI 837I** (derived from `CLM-2026-1001001.edi`):
```json
{
  "source_format":      "EDI_837I",
  "source_claim_ref":   "CLM-2026-1001001",
  "intake_channel":     "EDI_837I",
  "extracted_fields": {
    "member_id":               { "value": "435860987-06",  "confidence": 1.0 },
    "member_dob":              { "value": "1943-06-09",    "confidence": 1.0 },
    "member_name_last":        { "value": "Fischer",       "confidence": 1.0 },
    "member_name_first":       { "value": "Monica",        "confidence": 1.0 },
    "rendering_provider_npi":  { "value": "5799110529",    "confidence": 1.0 },
    "billing_provider_npi":    { "value": "5799110529",    "confidence": 1.0 },
    "billing_provider_tax_id": { "value": "235462507",     "confidence": 1.0 },
    "date_of_service_start":   { "value": "2026-03-28",    "confidence": 1.0 },
    "date_of_service_end":     { "value": "2026-04-20",    "confidence": 1.0 },
    "place_of_service_code":   { "value": "21",            "confidence": 1.0 },
    "claim_type":              { "value": "INSTITUTIONAL", "confidence": 1.0 },
    "icd10_codes":             { "value": ["H6690","R5383"], "confidence": 1.0 },
    "cpt_codes":               { "value": ["90471","44970","99285"], "confidence": 1.0 },
    "revenue_codes":           { "value": ["0360","0450"], "confidence": 1.0 },
    "drg_code":                { "value": "470",           "confidence": 1.0 },
    "billed_amount":           { "value": 2462.37,         "confidence": 1.0 },
    "payer_id":                { "value": "UHC-002",       "confidence": 1.0 },
    "payer_name":              { "value": "UnitedHealthcare Navigate", "confidence": 1.0 },
    "plan_id":                 { "value": "GRP-11311",     "confidence": 1.0 },
    "prior_auth_required":     { "value": true,            "confidence": 1.0 },
    "prior_auth_number":       { "value": null,            "confidence": 1.0 }
  }
}
```

> Note: `plan_id` is sourced from `SBR03` (group number) for EDI claims — this is the closest EDI equivalent to a plan identifier. `prior_auth_required` is mapped from `CLM09` (`Y` → `true`, `N` → `false`). `revenue_codes` and `drg_code` are populated for 837I and always empty/null for 837P.

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
  "document_type":     "CMS1500_PDF | FAX_PDF | PORTAL_STRUCTURED | PORTAL_UNSTRUCTURED | EMAIL | FAX_EMAIL | CMS1500_OCR_TEXT",
  "document_content":  "base64-encoded document bytes (omit for CMS1500_OCR_TEXT — use document_text instead)",
  "document_text":     "UTF-8 string — used only when document_type = CMS1500_OCR_TEXT; omit otherwise",
  "required_fields":   ["member_id", "member_name_last", "member_name_first",
                        "date_of_service_start", "date_of_service_end", "claim_type",
                        "icd10_codes", "cpt_codes", "payer_name", "prior_auth_required"]
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

**Document-type-specific handling notes:**

| document_type | Pre-processing required | Expected confidence profile | Notes |
|---|---|---|---|
| `CMS1500_PDF` | None — IDP runs OCR internally | Typically high (≥0.90) for clean forms; drops on handwritten or degraded scans | Standard scanned CMS-1500 form |
| `FAX_PDF` | None | Moderate — fax watermark and transmission artifacts can degrade OCR on overlapping fields | Fax cover sheet structured table usually parses well; watermark (`FAX` diagonal stamp) may reduce confidence on charge/procedure fields |
| `PORTAL_STRUCTURED` | None | High (≥0.95) — machine-generated JSON, no OCR needed | Portal submissions with well-defined schema |
| `PORTAL_UNSTRUCTURED` | None | Medium — field name variants across portals | Portal submissions with non-standard layout |
| `EMAIL` | **Required:** caller must parse RFC 5322 headers before invoking IDP. Extract `X-Submitter-NPI` and `X-Submitter-TaxID` headers at `confidence: 1.0` and pass as pre-seeded `extracted_fields` in the request; IDP handles body NLP only | Low-to-medium on body fields; `payer_id` and `plan_id` are absent from body text — expect `confidence: 0.00` for both (deferred to ADR-2) | `payer_id` and `plan_id` null values do NOT trigger HUMAN_REQUIRED (optional fields); HUMAN_REQUIRED set only if required fields fall below confidence threshold |
| `FAX_EMAIL` | None — no RFC 5322 headers present; body text only | Low-to-medium — no header-based high-confidence anchors; all fields via body NLP; `payer_id` and `plan_id` absent but deferred to ADR-2 | Confidence-based routing same as other non-EDI channels; `payer_id`/`plan_id` null values do NOT trigger HUMAN_REQUIRED |
| `CMS1500_OCR_TEXT` | None — text already extracted; IDP performs field parsing only (no OCR step) | **Use lower confidence baseline (≥0.80 effective threshold)** — OCR artifacts are common (e.g., dropped characters, transposed digits in NPI/tax ID, OCR misreads in procedure code fields) | Pre-extracted text from `cms1500-ocr/` folder; IDP must tolerate partial OCR noise |

**FHIR R4 is not handled by the IDP pipeline** — it is structured JSON requiring a dedicated parser. See §8.7.
**EXCEPTION_NOTE inputs are not claim submissions** — do not submit to IDP. See §2 failure modes for routing instructions.

**IDP pipeline output samples:**

The samples below show the agent-input format passed to ADR-1 after the IDP pipeline processes each document type. Field confidence values reflect the expected extraction quality for each channel; actual values vary by document condition.

**`CMS1500_PDF` — output sample** (derived from `CLM-2026-1001601`):
> OCR artifacts present: `member_name_last` first character lowercase (`"avis"` → normalized to `"Avis"`); third CPT entry is `"9110"` (4-char OCR artifact of `"9 110"`, invalid CPT); `rendering_provider_npi` and `billing_provider_npi` blank in field 33; `payer_id` and `plan_id` absent from CMS-1500 format.
```json
{
  "source_format":    "CMS1500_PDF",
  "source_claim_ref": "CLM-2026-1001601",
  "intake_channel":   "CMS1500_PDF",
  "extracted_fields": {
    "member_id":               { "value": "339191745",                    "confidence": 0.97 },
    "member_name_last":        { "value": "Avis",                         "confidence": 0.83 },
    "member_name_first":       { "value": "Rosa",                         "confidence": 0.91 },
    "member_dob":              { "value": "1949-01-06",                   "confidence": 0.96 },
    "rendering_provider_npi":  { "value": null,                           "confidence": 0.00 },
    "billing_provider_npi":    { "value": null,                           "confidence": 0.00 },
    "billing_provider_tax_id": { "value": "158289846",                    "confidence": 0.94 },
    "date_of_service_start":   { "value": "2026-04-12",                   "confidence": 0.91 },
    "date_of_service_end":     { "value": "2026-04-23",                   "confidence": 0.91 },
    "place_of_service_code":   { "value": "11",                           "confidence": 0.95 },
    "claim_type":              { "value": "PROFESSIONAL",                 "confidence": 0.99 },
    "icd10_codes":             { "value": ["E11.9"],                      "confidence": 0.91 },
    "cpt_codes":               { "value": ["99203", "99285", "9110"],     "confidence": 0.62 },
    "billed_amount":           { "value": 544.68,                         "confidence": 0.97 },
    "payer_id":                { "value": null,                           "confidence": 0.00 },
    "payer_name":              { "value": "Illinois Medicaid - Medicaid", "confidence": 0.92 },
    "plan_id":                 { "value": null,                           "confidence": 0.00 },
    "prior_auth_required":     { "value": false,                          "confidence": 0.90 },
    "prior_auth_number":       { "value": null,                           "confidence": 1.00 },
    "revenue_codes":           { "value": [],                             "confidence": 1.00 },
    "drg_code":                { "value": null,                           "confidence": 1.00 }
  }
}
```
> `extraction_status` → `HUMAN_REQUIRED` (`rendering_provider_npi`, `billing_provider_npi`, `cpt_codes` at 0.62, `payer_id`, `plan_id` below threshold or null).

**`CMS1500_OCR_TEXT` — output sample** (derived from `CLM-2026-1001601`, pre-extracted OCR text from `cms1500-ocr/`):
> Same claim as above; source is already-extracted text. IDP performs field parsing only (no OCR step). OCR artifacts from the original scan remain in the input text. Effective confidence threshold is 0.80 for this channel.
```json
{
  "source_format":    "CMS1500_OCR_TEXT",
  "source_claim_ref": "CLM-2026-1001601",
  "intake_channel":   "CMS1500_OCR_TEXT",
  "extracted_fields": {
    "member_id":               { "value": "339191745",                    "confidence": 0.94 },
    "member_name_last":        { "value": "Avis",                         "confidence": 0.79 },
    "member_name_first":       { "value": "Rosa",                         "confidence": 0.88 },
    "member_dob":              { "value": "1949-01-06",                   "confidence": 0.93 },
    "rendering_provider_npi":  { "value": null,                           "confidence": 0.00 },
    "billing_provider_npi":    { "value": null,                           "confidence": 0.00 },
    "billing_provider_tax_id": { "value": "158289846",                    "confidence": 0.91 },
    "date_of_service_start":   { "value": "2026-04-12",                   "confidence": 0.89 },
    "date_of_service_end":     { "value": "2026-04-23",                   "confidence": 0.89 },
    "place_of_service_code":   { "value": "11",                           "confidence": 0.93 },
    "claim_type":              { "value": "PROFESSIONAL",                 "confidence": 0.99 },
    "icd10_codes":             { "value": ["E11.9"],                      "confidence": 0.88 },
    "cpt_codes":               { "value": ["99203", "99285", "9110"],     "confidence": 0.68 },
    "billed_amount":           { "value": 544.68,                         "confidence": 0.95 },
    "payer_id":                { "value": null,                           "confidence": 0.00 },
    "payer_name":              { "value": "Illinois Medicaid - Medicaid", "confidence": 0.90 },
    "plan_id":                 { "value": null,                           "confidence": 0.00 },
    "prior_auth_required":     { "value": false,                          "confidence": 0.90 },
    "prior_auth_number":       { "value": null,                           "confidence": 1.00 },
    "revenue_codes":           { "value": [],                             "confidence": 1.00 },
    "drg_code":                { "value": null,                           "confidence": 1.00 }
  }
}
```
> `extraction_status` → `HUMAN_REQUIRED` (`member_name_last` at 0.79 is below the 0.80 effective threshold; `rendering_provider_npi`, `billing_provider_npi`, `cpt_codes`, `payer_id`, `plan_id` null or below threshold).

**`EMAIL` — output sample** (derived from `CLM-2026-1001901.eml`):
> `rendering_provider_npi`, `billing_provider_npi`, `billing_provider_tax_id` seeded from RFC 5322 headers `X-Submitter-NPI` and `X-Submitter-TaxID` at `confidence: 1.00` before IDP body NLP runs. `payer_id` and `plan_id` are structurally absent (payer name only; `"PPO"` in body is plan type, not a plan ID). `place_of_service_code` absent from email body.
```json
{
  "source_format":    "EMAIL",
  "source_claim_ref": "CLM-2026-1001901",
  "intake_channel":   "EMAIL",
  "extracted_fields": {
    "member_id":               { "value": "YYL49739973",            "confidence": 0.95 },
    "member_name_last":        { "value": "Espinoza",               "confidence": 0.93 },
    "member_name_first":       { "value": "Donna",                  "confidence": 0.91 },
    "member_dob":              { "value": "1970-01-22",             "confidence": 0.95 },
    "rendering_provider_npi":  { "value": "6271173287",             "confidence": 1.00 },
    "billing_provider_npi":    { "value": "6271173287",             "confidence": 1.00 },
    "billing_provider_tax_id": { "value": "336476889",              "confidence": 1.00 },
    "date_of_service_start":   { "value": "2026-04-06",             "confidence": 0.96 },
    "date_of_service_end":     { "value": "2026-04-06",             "confidence": 0.96 },
    "place_of_service_code":   { "value": null,                     "confidence": 0.00 },
    "claim_type":              { "value": "PROFESSIONAL",           "confidence": 0.88 },
    "icd10_codes":             { "value": ["F41.1", "M79.7"],       "confidence": 0.96 },
    "cpt_codes":               { "value": ["99214"],                "confidence": 0.95 },
    "billed_amount":           { "value": 155.95,                   "confidence": 0.97 },
    "payer_id":                { "value": null,                     "confidence": 0.00 },
    "payer_name":              { "value": "Anthem Blue Access",     "confidence": 0.89 },
    "plan_id":                 { "value": null,                     "confidence": 0.00 },
    "prior_auth_required":     { "value": false,                    "confidence": 0.80 },
    "prior_auth_number":       { "value": null,                     "confidence": 1.00 },
    "revenue_codes":           { "value": [],                       "confidence": 1.00 },
    "drg_code":                { "value": null,                     "confidence": 1.00 }
  }
}
```
> `extraction_status` → `HUMAN_REQUIRED` because `prior_auth_required` confidence (0.80) is below the 0.85 threshold. `payer_id`, `plan_id`, and `place_of_service_code` are optional fields (deferred to ADR-2 and ADR-5/ADR-8 respectively) — their absence does not contribute to HUMAN_REQUIRED.

**`FAX` — output sample** (representative; derived from `CLM-2026-1001938` fax cover sheet):
> Fax watermark and transmission artifacts degrade OCR on fields that overlap the diagonal stamp. `rendering_provider_npi`, `billing_provider_npi`, `billing_provider_tax_id` below threshold due to digit degradation. `payer_id` and `plan_id` absent from fax cover sheet format. `prior_auth_required` below threshold (no prior-auth section present).
```json
{
  "source_format":    "FAX",
  "source_claim_ref": "CLM-2026-1001938",
  "intake_channel":   "FAX",
  "extracted_fields": {
    "member_id":               { "value": "U83015882",              "confidence": 0.87 },
    "member_name_last":        { "value": "Quintana",               "confidence": 0.90 },
    "member_name_first":       { "value": "Adrian",                 "confidence": 0.91 },
    "member_dob":              { "value": "1967-10-31",             "confidence": 0.88 },
    "rendering_provider_npi":  { "value": "5336755600",             "confidence": 0.81 },
    "billing_provider_npi":    { "value": "5336755600",             "confidence": 0.81 },
    "billing_provider_tax_id": { "value": "783382094",              "confidence": 0.79 },
    "date_of_service_start":   { "value": "2026-04-09",             "confidence": 0.90 },
    "date_of_service_end":     { "value": "2026-04-09",             "confidence": 0.90 },
    "place_of_service_code":   { "value": null,                     "confidence": 0.00 },
    "claim_type":              { "value": "PROFESSIONAL",           "confidence": 0.88 },
    "icd10_codes":             { "value": ["F41.1"],                "confidence": 0.87 },
    "cpt_codes":               { "value": ["90471"],                "confidence": 0.83 },
    "billed_amount":           { "value": 15.00,                    "confidence": 0.92 },
    "payer_id":                { "value": null,                     "confidence": 0.00 },
    "payer_name":              { "value": "Cigna Open Access Plus", "confidence": 0.84 },
    "plan_id":                 { "value": null,                     "confidence": 0.00 },
    "prior_auth_required":     { "value": false,                    "confidence": 0.72 },
    "prior_auth_number":       { "value": null,                     "confidence": 0.85 },
    "revenue_codes":           { "value": [],                       "confidence": 1.00 },
    "drg_code":                { "value": null,                     "confidence": 1.00 }
  }
}
```
> `extraction_status` → `HUMAN_REQUIRED` (`rendering_provider_npi`, `billing_provider_npi`, `billing_provider_tax_id`, `cpt_codes`, `payer_id`, `plan_id`, `prior_auth_required` below threshold or null).

**`FAX_EMAIL` — output sample** (derived from `CLM-2026-1001901.txt`, fax-as-email plain text):
> Plain-text email body with no RFC 5322 claim-data headers (`X-Submitter-NPI`/`TaxID` absent). All fields extracted via body NLP only — no header-based high-confidence anchors. `payer_id` and `plan_id` structurally absent (name + plan type only). `place_of_service_code` absent from body text.
```json
{
  "source_format":    "FAX_EMAIL",
  "source_claim_ref": "CLM-2026-1001901",
  "intake_channel":   "FAX_EMAIL",
  "extracted_fields": {
    "member_id":               { "value": "XOJ145496096",                          "confidence": 0.87 },
    "member_name_last":        { "value": "Anderson",                              "confidence": 0.90 },
    "member_name_first":       { "value": "Lina",                                  "confidence": 0.91 },
    "member_dob":              { "value": "2008-07-29",                            "confidence": 0.93 },
    "rendering_provider_npi":  { "value": "0920133110",                            "confidence": 0.84 },
    "billing_provider_npi":    { "value": "0920133110",                            "confidence": 0.84 },
    "billing_provider_tax_id": { "value": "165876470",                             "confidence": 0.82 },
    "date_of_service_start":   { "value": "2026-04-20",                            "confidence": 0.88 },
    "date_of_service_end":     { "value": "2026-04-26",                            "confidence": 0.88 },
    "place_of_service_code":   { "value": null,                                    "confidence": 0.00 },
    "claim_type":              { "value": "PROFESSIONAL",                          "confidence": 0.85 },
    "icd10_codes":             { "value": ["M25.562", "M17.11", "Z00.00"],         "confidence": 0.89 },
    "cpt_codes":               { "value": ["47562", "99281", "73030"],             "confidence": 0.87 },
    "billed_amount":           { "value": 2853.21,                                 "confidence": 0.91 },
    "payer_id":                { "value": null,                                    "confidence": 0.00 },
    "payer_name":              { "value": "Blue Cross Blue Shield of Illinois",    "confidence": 0.83 },
    "plan_id":                 { "value": null,                                    "confidence": 0.00 },
    "prior_auth_required":     { "value": false,                                   "confidence": 0.75 },
    "prior_auth_number":       { "value": null,                                    "confidence": 0.80 },
    "revenue_codes":           { "value": [],                                      "confidence": 1.00 },
    "drg_code":                { "value": null,                                    "confidence": 1.00 }
  }
}
```
> `extraction_status` → `HUMAN_REQUIRED` because `prior_auth_required` confidence (0.75) is below the 0.85 threshold. `payer_id`, `plan_id`, and `place_of_service_code` are optional (deferred to ADR-2 and ADR-5/ADR-8); `billing_provider_npi`, `billing_provider_tax_id`, and `rendering_provider_npi` are optional (deferred to ADR-2+). Their null/low values do not contribute to HUMAN_REQUIRED.

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
  "intake_channel": "EDI_837P | EDI_837I | PORTAL_JSON | FHIR_R4 | CMS1500_PDF | CMS1500_OCR_TEXT | EMAIL | FAX | FAX_EMAIL | EXCEPTION_NOTE"
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

### 8.7 FHIR R4 Parser

> **Note:** FHIR R4 is structured JSON — it does not go through the IDP pipeline. The parser is a dedicated transformation component that maps FHIR R4 `Claim` resource fields to `NormalizedClaimRecord` fields. Unlike EDI parsing, FHIR R4 often requires external resource lookups because patient and provider identities are expressed as reference URIs rather than direct values.

**Input:** FHIR R4 `Claim` resource as a parsed JSON object. File extension `.json`; identified by presence of `"resourceType": "Claim"` at the root.

**Field mapping — FHIR R4 path → NormalizedClaimRecord:**

| NormalizedClaimRecord field | FHIR R4 source path | Confidence | Gap / action required |
|---|---|:---:|---|
| `claim_type` | `type.coding[].code` — map: `professional` → `PROFESSIONAL`, `institutional` → `INSTITUTIONAL` | 1.0 | None |
| `member_id` | `patient.reference` (e.g., `"Patient/297764010-09"`) | **0.00** | Reference URI — not a payer member ID. Must be resolved via member lookup; set `confidence: 0.00`; always triggers `HUMAN_REQUIRED` |
| `member_name_last` / `_first` | Not present in `Claim` resource | **0.00** | Must come from linked `Patient` resource (not included in claim file); set `confidence: 0.00` |
| `member_dob` | Not present in `Claim` resource | **0.00** | Must come from linked `Patient` resource; set `confidence: 0.00` |
| `rendering_provider_npi` | `provider.reference` (e.g., `"Practitioner/8909446606"`) — extract numeric suffix | 0.70 | May be a Practitioner ID, not always a 10-digit NPI; validate Luhn; set `confidence: 0.70` pending lookup confirmation |
| `billing_provider_npi` | Not directly present — `provider.reference` is the only NPI field | **0.00** | FHIR R4 `Claim` does not distinguish billing vs rendering; set same value as `rendering_provider_npi` with `confidence: 0.00` and flag for human review |
| `billing_provider_tax_id` | Not present in `Claim` resource | **0.00** | Absent structurally; set `confidence: 0.00` |
| `date_of_service_start` | `billablePeriod.start` or `item[0].servicedDate` (minimum) | 0.95 | Use `billablePeriod.start` as claim-level start; per-line `servicedDate` available in `item[]` |
| `date_of_service_end` | `billablePeriod.end` | 0.95 | Use `billablePeriod.end`; may be null for single-date claims — set equal to `start` if absent |
| `place_of_service_code` | `item[].locationCodeableConcept.coding[].code` | 0.95 | Per service line; use code from first line item; validate against CMS POS code list |
| `icd10_codes` | `diagnosis[].diagnosisCodeableConcept.coding[].code` where `system = "http://hl7.org/fhir/sid/icd-10-cm"` | 0.95 | Extract all diagnosis codes in sequence order |
| `cpt_codes` | `item[].productOrService.coding[].code` where `system = "http://www.ama-assn.org/go/cpt"` | 0.95 | One code per `item[]` entry; append modifier from `item[].modifier[].code` if present |
| `billed_amount` | `total.value` | 0.99 | Use claim-level total; `total.currency` must equal `USD` |
| `payer_id` | `insurer.reference` (e.g., `"Organization/UHC-002"`) | 0.70 | Organization ID may be mappable to payer_id via lookup table; if no mapping found, set `confidence: 0.00` |
| `payer_name` | `insurer.display` | 0.90 | Direct string value |
| `plan_id` | Not present in `Claim` resource | **0.00** | Absent structurally; set `confidence: 0.00` |
| `revenue_codes` | `item[].revenue.coding[].code` | 0.95 | INSTITUTIONAL claims only; empty array for PROFESSIONAL |
| `drg_code` | Not present in FHIR R4 `Claim` resource | **0.00** | May be in linked resources (e.g., `Encounter`); set `confidence: 0.00` if absent |
| `prior_auth_required` | Not present as boolean | **0.00** | FHIR R4 does not carry a prior auth boolean in the `Claim` resource; set `confidence: 0.00`; defer to human review |
| `prior_auth_number` | Not present | **0.00** | Set `confidence: 0.00` |

**FHIR R4 typically produces `HUMAN_REQUIRED`:** The required fields `member_id` (supplied as a reference URI, not a payer member ID), `member_name_last/first`, and `prior_auth_required` are typically absent or below confidence threshold, which in practice triggers `HUMAN_REQUIRED` for most FHIR R4 claims. Fields `member_dob`, `billing_provider_tax_id`, and `plan_id` are optional at intake (deferred to ADR-2) and their absence does not contribute to HUMAN_REQUIRED. The parser should extract all resolvable fields and populate `field_confidence` so the human reviewer sees exactly which fields are missing vs extractable.

**`intake_channel`:** Set to `FHIR_R4` for all claims processed through this parser.

**Output:** Partial `NormalizedClaimRecord` field map with per-field confidence values, in the same structure as IDP pipeline output (§8.3). Pass to ADR-1 validation layer.

**Output sample — FHIR R4** (derived from `CLM-2026-1001801.json`):
```json
{
  "source_format":    "FHIR_R4",
  "source_claim_ref": "CLM-2026-1001801",
  "intake_channel":   "FHIR_R4",
  "extracted_fields": {
    "claim_type":              { "value": "PROFESSIONAL",              "confidence": 1.00 },
    "member_id":               { "value": null,                        "confidence": 0.00 },
    "member_name_last":        { "value": null,                        "confidence": 0.00 },
    "member_name_first":       { "value": null,                        "confidence": 0.00 },
    "member_dob":              { "value": null,                        "confidence": 0.00 },
    "rendering_provider_npi":  { "value": "8909446606",                "confidence": 0.70 },
    "billing_provider_npi":    { "value": "8909446606",                "confidence": 0.00 },
    "billing_provider_tax_id": { "value": null,                        "confidence": 0.00 },
    "date_of_service_start":   { "value": "2026-03-31",                "confidence": 0.95 },
    "date_of_service_end":     { "value": "2026-04-15",                "confidence": 0.95 },
    "place_of_service_code":   { "value": "31",                        "confidence": 0.95 },
    "icd10_codes":             { "value": ["N39.0", "E66.9"],          "confidence": 0.95 },
    "cpt_codes":               { "value": ["99204", "20610", "90686"], "confidence": 0.95 },
    "revenue_codes":           { "value": [],                          "confidence": 1.00 },
    "drg_code":                { "value": null,                        "confidence": 0.00 },
    "billed_amount":           { "value": 386.64,                      "confidence": 0.99 },
    "payer_id":                { "value": "UHC-002",                   "confidence": 0.70 },
    "payer_name":              { "value": "UnitedHealthcare Navigate",  "confidence": 0.90 },
    "plan_id":                 { "value": null,                        "confidence": 0.00 },
    "prior_auth_required":     { "value": null,                        "confidence": 0.00 },
    "prior_auth_number":       { "value": null,                        "confidence": 0.00 }
  }
}
```

> The fields at `confidence: 0.00` — `member_id`, `member_name_last/first`, `member_dob`, `billing_provider_tax_id`, `plan_id`, `prior_auth_required` — are structurally absent from the FHIR R4 `Claim` resource. Of these, `member_id`, `member_name_last/first`, and `prior_auth_required` are required fields — their absence triggers `extraction_status: HUMAN_REQUIRED`. `member_dob`, `billing_provider_tax_id`, and `plan_id` are optional (deferred to ADR-2) and their absence does not contribute to HUMAN_REQUIRED. The `billing_provider_npi` at `confidence: 0.00` reflects that the value was copied from `rendering_provider_npi` — this field is optional (deferred to ADR-2+) and does not trigger HUMAN_REQUIRED on its own.

---

### 8.8 Portal JSON Field Mapping

> **Note:** The IDP pipeline handles portal JSON as `PORTAL_STRUCTURED` or `PORTAL_UNSTRUCTURED`, but the portal JSON field names do not map directly to `NormalizedClaimRecord` fields. This section documents the required transformation layer.

**Input:** Provider portal JSON submission (`.json` files from `portal-json/`). Identified by presence of `"submission_id"` at the root (distinguishes from FHIR R4 `"resourceType": "Claim"`).

**Field mapping — portal JSON path → NormalizedClaimRecord:**

| NormalizedClaimRecord field | Portal JSON source path | Transformation required | Gap |
|---|---|---|---|
| `source_claim_ref` | `submission_id` | None | None |
| `member_id` | `insurance.member_id` | None | None |
| `member_dob` | `patient.date_of_birth` | None | None |
| `member_name_last` | `patient.last_name` | Key rename | None |
| `member_name_first` | `patient.first_name` | Key rename | None |
| `rendering_provider_npi` | Not present as separate field; only `submitter.npi` available | Treat `submitter.npi` as billing NPI; set rendering = billing if no distinct rendering NPI present | Rendering vs billing NPI indistinguishable — flag for human confirmation; set `confidence: 0.70` |
| `billing_provider_npi` | `submitter.npi` | None | None |
| `billing_provider_tax_id` | `submitter.tax_id` | Strip hyphen: `"25-3439747"` → `"253439747"` | Hyphenated EIN format; must normalize to 9 digits |
| `date_of_service_start` | Minimum `service_lines[].date_of_service` across all lines | Take min date across all service line `date_of_service` values | No claim-level DOS; derived from line items |
| `date_of_service_end` | Maximum `service_lines[].date_of_service` across all lines | Take max date across all service line `date_of_service` values | No claim-level DOS end; derived from line items |
| `place_of_service_code` | `service_lines[0].place_of_service` | Take from first line; validate all lines are consistent | Per-line field — check consistency across lines |
| `claim_type` | Not present | Infer `PROFESSIONAL` by default for portal submissions unless revenue codes are present | Not explicit in portal JSON |
| `icd10_codes` | `diagnoses[].code` | Collect all codes into array | None |
| `cpt_codes` | `service_lines[].cpt_code` + `service_lines[].modifiers[]` | Concatenate: `"99213"` + `["-25"]` → `"99213-25"`; empty modifiers → code only | Modifier array may be empty `[]` |
| `billed_amount` | `total_charge_amount` | None | None |
| `payer_id` | `insurance.payer_id` | None | None |
| `payer_name` | `insurance.payer_name` | None | None |
| `plan_id` | `insurance.plan` | **Not a plan ID** — e.g., `"PPO"` is a plan type, not a plan identifier | Optional field (deferred to ADR-2); set `confidence: 0.00`; discard the plan type value — do not store in any annotation field; null value does NOT trigger HUMAN_REQUIRED |
| `prior_auth_required` | Infer from `prior_auth_number != null` | `true` if `prior_auth_number` is non-null and non-empty; `false` otherwise | No explicit boolean; inferred |
| `prior_auth_number` | `prior_auth_number` | None | May be `null` |

**`intake_channel`:** Set to `PORTAL_JSON` for all claims processed through this mapping.

**Key note:** `plan_id` is structurally absent from portal JSON (only plan type is available). `plan_id` is an optional field at intake (deferred to ADR-2) — its absence does NOT trigger `HUMAN_REQUIRED`. Discard the plan type value (`insurance.plan`) — do not store in any annotation field. `HUMAN_REQUIRED` is triggered only if required fields (e.g., `icd10_codes`, `cpt_codes`, `prior_auth_required`) fall below confidence threshold.

**`PORTAL_JSON` — output sample** (derived from `CLM-2026-1001201.json`):
> After applying the field mapping above: `billing_provider_tax_id` hyphen stripped (`"25-3439747"` → `"253439747"`); `rendering_provider_npi` treated as billing NPI with `confidence: 0.70` (rendering vs billing indistinguishable); `date_of_service_start/end` derived from single service line; `plan_id` null (`"PPO"` is plan type, not a plan ID); `prior_auth_required` inferred from null `prior_auth_number`.
```json
{
  "source_format":    "PORTAL_JSON",
  "source_claim_ref": "CLM-2026-1001201",
  "intake_channel":   "PORTAL_JSON",
  "extracted_fields": {
    "member_id":               { "value": "YYL39541245",          "confidence": 0.99 },
    "member_name_last":        { "value": "Kim",                  "confidence": 0.99 },
    "member_name_first":       { "value": "Roberto",              "confidence": 0.99 },
    "member_dob":              { "value": "1941-12-20",           "confidence": 0.99 },
    "rendering_provider_npi":  { "value": "4227019308",           "confidence": 0.70 },
    "billing_provider_npi":    { "value": "4227019308",           "confidence": 0.99 },
    "billing_provider_tax_id": { "value": "253439747",            "confidence": 0.99 },
    "date_of_service_start":   { "value": "2026-04-26",           "confidence": 0.99 },
    "date_of_service_end":     { "value": "2026-04-26",           "confidence": 0.99 },
    "place_of_service_code":   { "value": "11",                   "confidence": 0.99 },
    "claim_type":              { "value": "PROFESSIONAL",         "confidence": 0.90 },
    "icd10_codes":             { "value": ["J20.9", "R51.9"],     "confidence": 0.99 },
    "cpt_codes":               { "value": ["97110"],              "confidence": 0.99 },
    "billed_amount":           { "value": 48.57,                  "confidence": 0.99 },
    "payer_id":                { "value": "ANT-001",              "confidence": 0.99 },
    "payer_name":              { "value": "Anthem Blue Access",   "confidence": 0.99 },
    "plan_id":                 { "value": null,                   "confidence": 0.00 },
    "prior_auth_required":     { "value": false,                  "confidence": 0.95 },
    "prior_auth_number":       { "value": null,                   "confidence": 1.00 },
    "revenue_codes":           { "value": [],                     "confidence": 1.00 },
    "drg_code":                { "value": null,                   "confidence": 1.00 }
  }
}
```
> `extraction_status` → `AUTO_COMPLETE` — all required fields are present at confidence ≥ 0.85. `plan_id` is null but optional (deferred to ADR-2). `rendering_provider_npi` at 0.70 is optional (deferred to ADR-2+). `billing_provider_npi` and `billing_provider_tax_id` are optional (deferred to ADR-2+). None of these affect the required-field check.

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
| `member_dob` | date | No | ISO 8601 `YYYY-MM-DD`; optional — resolved by ADR-2 |
| `member_name_last` | string | Yes | Max 60 chars |
| `member_name_first` | string | Yes | Max 60 chars |
| `rendering_provider_npi` | string | No | Exactly 10 digits; Luhn check required; optional — resolved by ADR-2+ |
| `billing_provider_npi` | string | No | Exactly 10 digits; Luhn check required; optional — resolved by ADR-2+ |
| `billing_provider_tax_id` | string | No | Exactly 9 digits; EIN format; optional — resolved by ADR-2+ |
| `date_of_service_start` | date | Yes | ISO 8601 `YYYY-MM-DD`; immutable |
| `date_of_service_end` | date | Yes | ISO 8601 `YYYY-MM-DD`; must be ≥ `date_of_service_start`; immutable |
| `place_of_service_code` | string | No | Exactly 2 digits; valid CMS POS code list; optional — resolved by ADR-5/ADR-8 |
| `claim_type` | enum | Yes | `PROFESSIONAL \| INSTITUTIONAL \| DENTAL`; immutable |
| `icd10_codes` | array\<string\> | Yes | Min 1, max 12 items; each matches ICD-10-CM format `[A-Z][0-9]{2}(\.[0-9A-Z]{1,4})?` |
| `cpt_codes` | array\<string\> | Yes | Min 1, max 50 items; each is 5-digit CPT code with optional `-XX` 2-char modifier |
| `revenue_codes` | array\<string\> | No | Max 4-char each; present only if `claim_type = INSTITUTIONAL` |
| `drg_code` | string | No | Exactly 3 digits; present only if `claim_type = INSTITUTIONAL` |
| `billed_amount` | decimal(10,2) | No | > 0; USD; optional — resolved by ADR-5/ADR-8 |
| `currency` | string | Yes | Fixed value: `"USD"`; immutable |
| `payer_id` | string | No | Max 20 chars; optional — resolved by ADR-2 |
| `payer_name` | string | Yes | Max 100 chars |
| `plan_id` | string | No | Max 30 chars; optional — resolved by ADR-2 |
| `prior_auth_required` | boolean | Yes | |
| `prior_auth_number` | string | Conditional | Max 30 chars; required when `prior_auth_required = true`; must be null when `prior_auth_required = false` |
| `intake_channel` | enum | Yes | `EDI_837P \| EDI_837I \| PORTAL_JSON \| FHIR_R4 \| CMS1500_PDF \| CMS1500_OCR_TEXT \| EMAIL \| FAX \| FAX_EMAIL \| EXCEPTION_NOTE`; immutable |
| `extraction_status` | enum | Yes | `AUTO_COMPLETE \| HUMAN_REQUIRED \| PENDING_DUPLICATE` |
| `field_confidence` | map\<string, float\> | Conditional | Required when `intake_channel ∉ {EDI_837P, EDI_837I}`; omit for EDI; values 0.0–1.0 |
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

**Input:** Well-formed EDI 837P transaction received via EDI channel. All required segments present. No prior submissions with matching claim_id + member_id + date_of_service_start in CMS.

**Expected outcome:**
1. Format detected as `EDI_837P` (transaction qualifier `005010X222A1`).
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
- Input: EDI 837 claim with `source_claim_ref`, `member_id`, and `date_of_service_start` all matching an existing CMS record created within the past 30 days.
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

**EC-8: EDI 837I institutional claim with revenue codes and DRG**
- Input: Well-formed EDI 837I transaction (transaction qualifier `005010X223A2`). Contains `SV2` revenue code segments and `HI*DRG` DRG code. All required segments present.
- Expected: Parser detects `005010X223A2` qualifier; sets `intake_channel: EDI_837I`, `claim_type: INSTITUTIONAL`. Extracts `revenue_codes` from `SV2` segments; extracts `drg_code` from `HI*DRG`. Output record includes non-empty `revenue_codes` array and `drg_code` string. `extraction_status: AUTO_COMPLETE`. CMS write proceeds without HITL.

**EC-9: FHIR R4 claim — member_id is a reference URI, not a payer member ID**
- Input: FHIR R4 `Claim` resource JSON with `patient.reference: "Patient/297764010-09"`. No `member_name` or `prior_auth_required` fields extractable from the `Claim` resource.
- Expected: FHIR R4 parser sets `member_id: null, confidence: 0.00`; `member_name_last: null, confidence: 0.00`; `member_name_first: null, confidence: 0.00`; `prior_auth_required: null, confidence: 0.00`. `intake_channel: FHIR_R4`. `extraction_status: HUMAN_REQUIRED` — required fields `member_id`, `member_name_last/first`, and `prior_auth_required` are absent. `member_dob`, `billing_provider_tax_id`, and `plan_id` are optional (deferred to ADR-2) and do not appear in `low_confidence_fields` as blocking reasons. Exception queue entry created. CMS write deferred.

**EC-10: Email submission — payer_id and plan_id absent from body**
- Input: RFC 5322 `.eml` file. Headers contain `X-Submitter-NPI: 6271173287` and `X-Submitter-TaxID: 33-6476889`. Body contains payer name (`Anthem Blue Access`) but no payer ID and no plan_id.
- Expected: Caller pre-processes RFC 5322 headers; NPI fields seeded at `confidence: 1.00`; `billing_provider_tax_id` at `confidence: 1.00`. IDP extracts body fields; `payer_id: null, confidence: 0.00`; `plan_id: null, confidence: 0.00`. `intake_channel: EMAIL`. `payer_id` and `plan_id` are optional (deferred to ADR-2) — their null values do NOT trigger HUMAN_REQUIRED. `extraction_status` determined solely by required-field confidence: if all required fields (`member_id`, `member_name`, `DOS`, `claim_type`, `icd10_codes`, `cpt_codes`, `prior_auth_required`, `payer_name`) are ≥ 0.85, result is `AUTO_COMPLETE`.

**EC-11: Fax PDF — watermark degrades confidence on overlapping fields**
- Input: Fax cover sheet PDF with diagonal `FAX` watermark overlapping the charge amount and procedure code table cells.
- Expected: IDP (`document_type: FAX_PDF`) extracts structured table fields; fields not obscured by watermark return `confidence ≥ 0.90`; charge amount and/or one procedure code return `confidence < 0.85` due to watermark occlusion. `extraction_status: HUMAN_REQUIRED`. Exception queue entry with those fields in `low_confidence_fields`. `intake_channel: FAX`.

**EC-12: Exception note with a recoverable claim_id reference**
- Input: PDF exception note containing text `"Pulled claim CLM-2026-1001962. Confirmed received — in queue for adjudication."`. Not a new claim submission.
- Expected: Agent detects `intake_channel: EXCEPTION_NOTE`. Does not invoke EDI parser or IDP pipeline. Extracts `claim_id: CLM-2026-1001962` from note text. Outputs `routing_action: ANNOTATE_CLAIM` with `claim_id` and note text. CMS `PUT /v1/claims/CLM-2026-1001962` appends note annotation. No new NormalizedClaimRecord created. No exception queue entry created.

**EC-13: Pre-OCR'd CMS-1500 text with significant OCR artifacts**
- Input: Pre-OCR'd `.txt` file from `cms1500-ocr/` folder. Text contains artifacts: `"pATIENT RE ATIONSHIP"`, `"9 110"` (should be CPT `99110`), blank NPI field.
- Expected: IDP (`document_type: CMS1500_OCR_TEXT`) processes text; applies lower confidence baseline (effective threshold 0.80). CPT code `"9 110"` fails format validation; `confidence: 0.00`. Blank NPI field returns `confidence: 0.00`. `extraction_status: HUMAN_REQUIRED`. `intake_channel: CMS1500_OCR_TEXT`. `low_confidence_fields` includes at minimum the malformed CPT code and missing NPI.

---

### 10.3 Failure Mode Scenarios

**FM-1: CMS unavailable for 20 minutes**
- Trigger: CMS POST returns HTTP 503; all 3 retries (2 s, 4 s, 8 s) exhaust.
- Expected: (1) Claims persisted locally with idempotency keys. (2) `CMS_UNAVAILABLE` alert posted to ops channel within 30 s of first exhausted retry cycle. (3) Agent continues accepting and extracting new claims; all pend locally. (4) Agent retries CMS on 5-minute intervals. (5) When CMS recovers, local queue replays in FIFO order. (6) Duplicate writes prevented by idempotency key check. (7) All claims eventually reach `QUEUED` state; SLA clock accounts for delay.

**FM-2: IDP extraction pipeline unavailable**
- Trigger: IDP POST returns HTTP 504 on first attempt and retry.
- Expected: (1) Affected PDF/portal/email/fax/fax-email/OCR-text claims routed to exception queue with `exception_type: CMS_WRITE_FAILURE` (extraction prerequisite failed), `required_action: MANUAL_WRITE`. (2) EDI 837P and 837I claims are unaffected — they bypass IDP entirely. (3) FHIR R4 claims are unaffected — they use the FHIR R4 parser (§8.7), not IDP. (4) Ops alert generated with `IDP_UNAVAILABLE` flag. (5) When IDP recovers, exception queue items can be resubmitted; agent re-runs extraction.

**FM-3: Malformed EDI 837 — invalid ISA envelope**
- Trigger: EDI transaction received with corrupted ISA header (wrong element count).
- Expected: (1) Parser throws structural parse error before any segment extraction. (2) Exception queue entry created: `exception_type: FORMAT_UNRECOGNIZED`, `required_action: FORMAT_IDENTIFICATION`. (3) No partial extraction attempted — a partially-extracted EDI record with some fields at confidence 1.0 and others at 0.0 would be misleading. (4) Submitter notification triggered via exception queue resolution workflow.

**FM-4: FHIR R4 parser receives a claim with unresolvable member reference**
- Trigger: FHIR R4 `Claim` resource arrives with `patient.reference: "Patient/UNKNOWN"` — no numeric ID extractable; linked `Patient` resource not included.
- Expected: (1) FHIR R4 parser sets `member_id: null, confidence: 0.00`. (2) `extraction_status: HUMAN_REQUIRED` (FHIR_R4 always). (3) Exception queue entry created with `low_confidence_fields` including `member_id`. (4) Human resolver must perform manual member lookup using available fields (payer name, patient display name from `patient.display`, date of service) and supply the correct `member_id` before CMS write proceeds.

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
*Shared entities (CMS API, normalized record schema, reuse matrix) are consistent with `specs/06b-capability-spec-triage.md`.*
