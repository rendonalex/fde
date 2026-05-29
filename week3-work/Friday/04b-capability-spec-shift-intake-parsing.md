# Capability Spec — JtD-1: Shift Intake Parsing

> ATX Phase 4 Agent Mapping. Input: `specs/cognitive-load-map.md`, `specs/3-agentic-solution-architecture.md`, `specs/volume-×-value-analysis.md`.
> Shared entities (ShiftRequest, ShiftRequirement) and all glossary terms are defined in `04a-capability-spec-match-selection.md`. This document defines only JtD-1-specific entities and builds on that shared foundation.
> New assumptions A23–A25 are defined in `specs/assumptions.md`.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Agent Purpose Document](#2-agent-purpose-document)
3. [Agent Activity Catalog](#3-agent-activity-catalog)
4. [Autonomy Matrix](#4-autonomy-matrix)
5. [System and Data Inventory](#5-system-and-data-inventory)
   - 5.1 [System Inventory](#51-system-inventory)
   - 5.2 [Entity Definitions](#52-entity-definitions)
   - 5.3 [Integration Contracts](#53-integration-contracts)
6. [Context Engineering Design](#6-context-engineering-design)
7. [Validation Design](#7-validation-design)
8. [Compounding Roadmap](#8-compounding-roadmap)
9. [Production-Grade Validation Results](#9-production-grade-validation-results)

---

## 1. Executive Summary

The **MedFlex Shift Intake Parser** (JtD-1) is **Build Order 1** in the Wave 1 pipeline — the pipeline gate that makes all downstream automation possible. Every downstream agent (JtD-2 through JtD-5a) depends on a structured ShiftRequirement produced by this parser. Without it, the entire pipeline reverts to manual coordinator work.

The parser converts free-text hospital shift requests arriving in ServiceNow — submitted via email body, portal form, or phone transcription — into a machine-readable ShiftRequirement object containing specialty_code, shift_start/end, hospital_id, required_credentials, and per-field confidence scores. High-confidence parses (confidence_score ≥ 0.80) proceed automatically to JtD-2 (BP2). Low-confidence or ambiguous parses route to a human review queue (BP1) for coordinator clarification.

This agent directly attacks the first source of the 4.2-hour fill time: unguided reading comprehension under time pressure, which currently consumes ~35% of coordinator active work (A16) on every shift request.

**Economic impact:** $126K/year direct labor saving; 2.8-month payback on $30K build cost. More importantly, it is the prerequisite for the $1.5M+ revenue recovery target (M3) enabled by the full pipeline.

---

## 2. Agent Purpose Document

```
Agent Name:          MedFlex Shift Intake Parser
Job to be Done:      Convert every inbound hospital shift request in the ServiceNow
                     queue into a structured ShiftRequirement object with per-field
                     confidence scores, and route the result: high-confidence parses
                     proceed automatically to the JtD-2 pipeline (BP2); low-confidence
                     parses route to the coordinator human review queue (BP1).
Business context:    MedFlex coordinator workflow / Intake Zone (JtD-1).
                     Triggered by queue poll: every 10 seconds, agent checks ServiceNow
                     for new shift request records. One ShiftRequest per ServiceNow ticket.

Primary objectives:
  1. Parse all inbound shift requests autonomously; produce a valid ShiftRequirement
     for ≥85% of requests without coordinator intervention (A10).
  2. Correctly identify and route ≤15% of low-confidence requests to the BP1 human
     review queue so that no malformed ShiftRequirement reaches JtD-2 (A10).

KPIs:
  - Parse accuracy: ≥85% field-level extraction accuracy on specialty_code,
    shift_start, shift_end, hospital_id, and required_credentials (A10).
    Measured as: field_correct_extractions / total_field_extractions over rolling 7 days.
    Validation mechanism: random 10% sample of high-confidence parses reviewed by
    coordinator weekly; extraction errors logged to accuracy dashboard.
  - HITL rate: ≤15% of requests route to BP1 human review; ceiling 25% (A10).
    Computed as: COUNT(status=PARSED_LOW_CONFIDENCE) / COUNT(all parsed) per day.
  - Throughput: ≥184 requests parsed per day (A4). Measured as daily ShiftRequirements
    in status=READY_FOR_SEARCH + HUMAN_REVIEW.
  - Parse latency: ShiftRequirement created within 10 seconds of ServiceNow ticket
    appearing in queue poll. Measured at p95.
  - Cost per case: ≤$0.34 (token cost $0.011 + 15% HITL cost $0.33, A22).
    Computed as: (input_tokens × $3.00/M) + (output_tokens × $15.00/M) + HITL_cost.

Failure modes:
  1. Silent error — wrong specialty_code extracted with high confidence:
     Consequence: ShiftRequirement proceeds to JtD-2 with wrong specialty; produces
     a candidate pool for the wrong specialty; surfaces as hospital rejection (BP5)
     or downstream mismatch (currently 7% mismatch rate per discovery).
     Recovery: BP1 catches only low-confidence errors; high-confidence wrong extractions
     require weekly sample review to detect. Mitigation: few-shot examples in system
     prompt cover the most common specialty shorthand variations. Validate on 50 real
     shift request samples before launch.
  2. Routing failure — low-confidence parse not routed to BP1:
     Consequence: Malformed ShiftRequirement reaches JtD-2; downstream agents produce
     meaningless results.
     Recovery: confidence_score ≥ 0.80 check is a hard gate enforced by the pipeline
     (not by the LLM); the pipeline code checks the confidence_score field and routes
     regardless of LLM intent.
  3. Agent failure — LLM API unavailable:
     Consequence: ShiftRequests accumulate in queue; pipeline stalls.
     Recovery: After 3 retries, ShiftRequest.status=PARSING_FAILED; alert ops; route
     all affected requests to coordinator manual queue; coordinator processes directly
     in ServiceNow until API recovers.

Delegation archetype:  Agent-led + Human Oversight (stable; no Phase 2 upgrade planned)

Rationale: The LLM parser runs autonomously on all inbound requests. The human is only
  involved for exception resolution (BP1), not routine parsing. The Input Structure
  dimension scores Low (free text, inconsistent formats) — this archetype is the right
  permanent design. A structured intake form (T2 trade-off in `specs/3-agentic-solution-architecture.md`)
  would improve accuracy but requires hospital behavior change and is out of MVP scope.

Escalation triggers:
  - confidence_score < 0.80 → route to BP1 human review queue (always, non-negotiable)
  - hospital_id = null after parse → route to BP1 (unknown hospital)
  - specialty_code = null after parse → route to BP1 (required field missing)
  - shift_start = null after parse → route to BP1 (required field missing)
  - LLM returns stop_reason=max_tokens → discard output; route to BP1
    (truncated output = malformed ShiftRequirement)
  - LLM API unavailable after 3 retries → ShiftRequest.status=PARSING_FAILED;
    route to coordinator manual queue; alert ops
  - Duplicate source_ticket_id detected → skip; log "already processed"; do not create
    second ShiftRequest (idempotency guard)
```

---

## 3. Agent Activity Catalog

All micro-tasks performed by the MedFlex Shift Intake Parser.

| Task | Type | Delegation Level | Data Required | Tool Required | Risk Level |
|------|------|-----------------|---------------|---------------|------------|
| MT-1.0 Queue poll | Retrieval | Fully agentic | ServiceNow queue (new records since last poll) | ServiceNow Table API read (`u_shift_request` table, A24) | Low |
| MT-1.0a Idempotency check | Decision | Fully agentic | source_ticket_id; existing ShiftRequest records | Internal DB lookup | Low |
| MT-1.1 Record creation | Action | Fully agentic | ServiceNow record fields; status=RECEIVED | Internal DB write | Low |
| MT-1.2a Specialty and schedule parse | Reasoning | Fully agentic (with confidence scoring) | Raw request text; specialty vocabulary; hospital lookup table | Claude API (claude-sonnet-4-6) | Medium |
| MT-1.2b Date/time normalization | Reasoning | Fully agentic | Extracted date/time strings; system current date for relative date resolution | None (in-context) | Medium |
| MT-1.3 Credential extraction | Reasoning | Fully agentic (with confidence scoring) | Raw request text; credential code mapping table | None (in-context mapping) | Medium |
| MT-1.3a Credential code mapping | Decision | Fully agentic | Extracted credential shorthand strings; CredentialCode enum | Static credential mapping in system prompt | Medium |
| MT-1.4 Confidence scoring | Reasoning | Fully agentic | Per-field extraction results from MT-1.2 and MT-1.3 | None (computed in-context) | Low |
| MT-1.4a Routing decision | Decision | Fully agentic (rule-based threshold) | confidence_score from MT-1.4; threshold = 0.80 | Internal pipeline routing; Human Review Queue write (on BP1) | Low |
| MT-1.5 ShiftRequirement persistence | Action | Fully agentic | Parsed fields, field_confidence, confidence_score | Internal DB write | Low |
| MT-1.6 Audit log write | Action | Fully agentic | ShiftRequest.id, raw_text, parsed ShiftRequirement, confidence_score, routing_decision | Immutable audit log write | Low |

**Coordinator tasks at BP1 (human, not agent):**
- Review low-confidence ShiftRequirement draft
- Clarify with hospital via phone/email
- Correct field values and set confidence to 1.00 (manual override)
- Trigger READY_FOR_SEARCH status to release to JtD-2 pipeline

---

## 4. Autonomy Matrix

### Agent Decides Alone (no HITL required)
- Poll ServiceNow queue every 10 seconds for new shift request records
- Check idempotency: skip records with existing ShiftRequest.source_ticket_id
- Create ShiftRequest record with status=RECEIVED
- Parse raw_text using LLM to extract specialty_code, shift_start, shift_end, hospital_id, required_credentials
- Resolve relative dates ("tomorrow", "next Friday") using system current date
- Map credential shorthands to CredentialCode enum values (e.g., "BLS/ACLS" → [BLS, ACLS])
- Compute field_confidence per extracted field (0.00–1.00)
- Compute overall confidence_score = min(field_confidence values for required non-null fields)
- Apply routing rule: confidence_score ≥ 0.80 → proceed to JtD-2 (BP2); else → BP1 human review
- Write ShiftRequirement to DB with appropriate status
- Write immutable audit log entry

### Agent Acts, Human Notified After
- BP1 routing: when confidence_score < 0.80, agent writes ShiftRequest.status=PARSED_LOW_CONFIDENCE AND writes to human review queue, AND sends a notification to the coordinator queue dashboard. Coordinator sees it on next dashboard refresh (no blocking action required from coordinator for the routing itself — the routing is automatic)

### Agent Proposes, Human Approves Before Action (BP1)
- **Low-confidence ShiftRequirements**: Agent presents parsed draft (with confidence scores highlighted per field) to coordinator in human review queue. Coordinator must confirm or correct before status transitions to READY_FOR_SEARCH
- Agent does not proceed to JtD-2 for any ShiftRequest that has not cleared the confidence_score ≥ 0.80 gate — either via LLM extraction or via coordinator manual confirmation

### Human Takes Over (Agent Supports)
- LLM API unavailable after 3 retries → coordinator processes request directly in ServiceNow; agent provides no further assistance for this ShiftRequest until manually re-triggered
- Hospital sends a request format that is entirely unparseable (non-English, corrupted encoding, blank description) → ShiftRequest.status=PARSING_FAILED; coordinator contacts hospital for a resubmission

**Routing logic is hardcoded in pipeline, not in LLM:**
The confidence_score ≥ 0.80 routing gate is enforced by the pipeline orchestration code, not by the LLM output. The LLM produces the confidence_score; the pipeline code applies the threshold. This prevents a "confused" LLM from routing a low-confidence parse to BP2 by incorrectly self-reporting high confidence.

**Override mechanism:** Coordinator can override any LLM-parsed field at BP1. Override is logged with: coordinator_id, field_name, original_value (LLM output), corrected_value, timestamp. Corrected values are written to the Labeled Feedback Store as parse training examples.

---

## 5. System and Data Inventory

### 5.1 System Inventory

| System | Data Needed | Access Type | Availability | Gap / Risk |
|--------|-------------|-------------|--------------|-----------|
| ServiceNow (shift request queue) | New shift request records: sys_id, description (raw text), u_hospital_id (hint), opened_at | Read (polling every 10 seconds) | API provisioning required (A11) | Instance URL and table name assumed (A24, A23); validate with MedFlex IT before build |
| Claude API (Anthropic) | LLM reasoning for NLP extraction + confidence scoring | Write (API call) | Available (API key required) | Token cost $0.011/case (A22); system prompt cached via prompt caching API (>1,024 tokens) |
| Hospital Lookup Table | hospital_name → hospital_id mapping (~100 entries); embedded in system prompt | Read (static; in-prompt) | New build required | Must be populated from MedFlex data before launch; update process needed when new hospitals onboarded |
| Human Review Queue | Low-confidence ShiftRequirements for coordinator review | Write (on BP1 routing); Read (coordinator action) | New build required | Integrated into Coordinator UI (shared build with JtD-3 Coordinator Review UI) |
| Internal Pipeline Event Bus | ShiftRequirement READY_FOR_SEARCH event → triggers JtD-2 | Write | New build required | Shared infrastructure; built once for all pipeline agents |
| Immutable Audit Log | Per-parse: ShiftRequest.id, raw_text hash, parsed fields, confidence scores, routing decision | Write | New build required | Shared with JtD-3 and pipeline; retention 3 years |

**Shared integrations** (built in JtD-1, reused downstream):
- ServiceNow Table API client — reused by JtD-2, JtD-3, JtD-4, JtD-5a
- Claude API client — reused by JtD-3
- Hospital Lookup Table — reused by JtD-2 (hospital_id for preference query), JtD-3

### 5.2 Entity Definitions

#### Entity: ShiftRequest *(primary entity owned by JtD-1)*

| Attribute | Type | Constraints |
|-----------|------|-------------|
| id | UUID | PK, immutable, system-generated on creation |
| source_ticket_id | string(32) | NOT NULL, unique, ServiceNow sys_id; immutable; idempotency key |
| raw_text | string(10000) | NOT NULL, max 10,000 chars; original request text; immutable |
| status | enum | `[RECEIVED, PARSING, PARSED_HIGH_CONFIDENCE, PARSED_LOW_CONFIDENCE, HUMAN_REVIEW, PARSING_FAILED, READY_FOR_SEARCH]`; NOT NULL; default RECEIVED |
| created_at | ISO 8601 UTC timestamp | Immutable; set on creation |
| updated_at | ISO 8601 UTC timestamp | Updated on any modification |
| created_by | string(36) | "system" for all agent-initiated records; coordinator_id (UUID) for manually entered records |

**ShiftRequest State Machine:**
```
RECEIVED              → PARSING                   (on: agent picks up record from queue poll)
PARSING               → PARSED_HIGH_CONFIDENCE    (on: LLM returns confidence_score ≥ 0.80 on all required fields)
PARSING               → PARSED_LOW_CONFIDENCE     (on: LLM returns confidence_score < 0.80 on any required field)
PARSING               → PARSING_FAILED            (on: LLM API failure after 3 retries; or stop_reason=max_tokens)
PARSED_HIGH_CONFIDENCE → READY_FOR_SEARCH         (on: ShiftRequirement created; pipeline event fired; automatic)
PARSED_LOW_CONFIDENCE  → HUMAN_REVIEW             (on: BP1 routing; auto-route to coordinator queue)
PARSING_FAILED         → HUMAN_REVIEW             (on: auto-route to coordinator manual queue; ops alerted)
HUMAN_REVIEW           → READY_FOR_SEARCH         (on: coordinator confirms ShiftRequirement at BP1; manual)
HUMAN_REVIEW           → PARSING_FAILED           (on: coordinator cannot resolve — e.g., hospital requests cancellation)
```

**Constraints:**
- source_ticket_id must be unique; duplicate detection runs before RECEIVED → PARSING transition
- raw_text is immutable once set; coordinator corrections are made on ShiftRequirement fields, not on raw_text
- READY_FOR_SEARCH requires ShiftRequirement.hospital_id ≠ null AND ShiftRequirement.specialty_code ≠ null AND ShiftRequirement.shift_start ≠ null AND ShiftRequirement.shift_end ≠ null

#### Entity: ShiftRequirement *(structured output of JtD-1; input to JtD-2, JtD-3)*

| Attribute | Type | Constraints |
|-----------|------|-------------|
| id | UUID | PK, immutable, system-generated on creation |
| shift_request_id | UUID | FK → ShiftRequest.id; NOT NULL; immutable; unique (1 requirement per request); on ShiftRequest delete: restrict |
| hospital_id | string(64) | NOT NULL if status=READY_FOR_SEARCH; nullable if in HUMAN_REVIEW; FK to Hospital lookup table; format: ALLCAPS_LOCATION_STRING |
| specialty_code | enum | `[ICU_RN, ER_RN, MED_SURG_RN, FLOAT_POOL_RN, OR_RN, L_D_RN, PACU_RN, TELE_RN, PEDS_RN, NICU_RN, PSYCH_RN, CATH_LAB_RN, ONCOLOGY_RN, STEP_DOWN_RN]`; NOT NULL if READY_FOR_SEARCH; nullable in HUMAN_REVIEW |
| shift_start | ISO 8601 UTC timestamp | NOT NULL if READY_FOR_SEARCH; nullable in HUMAN_REVIEW; must be a future date at time of creation |
| shift_end | ISO 8601 UTC timestamp | NOT NULL if READY_FOR_SEARCH; nullable in HUMAN_REVIEW; must be > shift_start if both non-null; min duration: 1 hour; max duration: 24 hours |
| required_credentials | JSON array of CredentialCode | NOT NULL; min 0 items, max 10 items; empty array `[]` is valid (no credentials specified); enum values exhaustive: `[BLS, ACLS, PALS, NRP, TNCC, CCRN, CEN, OCN, CNOR, AWHONN_BASIC, AWHONN_INTERMEDIATE]` |
| confidence_score | decimal(3,2) | NOT NULL; read-only; range 0.00–1.00; computed as `min(field_confidence values for required fields where field is not null)`; threshold for auto-proceed: ≥0.80 |
| field_confidence | JSON object | NOT NULL; read-only; `{hospital_id: decimal(3,2), specialty_code: decimal(3,2), shift_start: decimal(3,2), shift_end: decimal(3,2), required_credentials: decimal(3,2)}`; all values 0.00–1.00 |
| source | enum | `[LLM_PARSED, COORDINATOR_MANUAL]`; NOT NULL; immutable; LLM_PARSED = agent extracted; COORDINATOR_MANUAL = coordinator created or corrected at BP1 |
| reviewed_by | UUID (coordinator_id) | Nullable; set when coordinator confirms or corrects at BP1 |
| created_at | ISO 8601 UTC timestamp | Immutable |
| updated_at | ISO 8601 UTC timestamp | Updated on coordinator correction at BP1 |

**Constraints:**
- If hospital_id is null OR specialty_code is null OR shift_start is null: ShiftRequest.status must be HUMAN_REVIEW or PARSING_FAILED; cannot transition to READY_FOR_SEARCH
- shift_end must be > shift_start (enforced at write time; if violated, route to HUMAN_REVIEW with validation error)
- confidence_score < 0.80: ShiftRequest.status must be PARSED_LOW_CONFIDENCE or HUMAN_REVIEW; cannot be READY_FOR_SEARCH
- field_confidence values are immutable once written (LLM output); coordinator corrections do not modify field_confidence — they update the field value and set source=COORDINATOR_MANUAL

#### Entity: HospitalLookup *(static reference data; managed by operations team; not modified by agent)*

| Attribute | Type | Constraints |
|-----------|------|-------------|
| hospital_id | string(64) | PK; format: ALLCAPS_LOCATION_STRING; immutable |
| display_name | string(200) | NOT NULL; e.g., "St. David's North Austin" |
| name_aliases | JSON array of string | NOT NULL; all known name variations used in requests (e.g., ["St. Davids North", "St. David's North", "SDN"]) |
| servicenow_id | string(32) | Nullable; ServiceNow sys_id for this hospital if stored in SN; used to cross-reference preference data |
| active | boolean | NOT NULL; default true; inactive hospitals are excluded from auto-routing |
| created_at | ISO 8601 UTC timestamp | Immutable |
| updated_at | ISO 8601 UTC timestamp | Updated when aliases or status change |

**Hospital lookup matching rule:** LLM extracts a hospital name string from raw_text. Pipeline code looks up the string against display_name and name_aliases (case-insensitive). If match found: hospital_id is set and field_confidence.hospital_id = 1.00. If no match: hospital_id = null and field_confidence.hospital_id = 0.00; ShiftRequest routes to BP1.

### 5.3 Integration Contracts

#### Contract 1: ServiceNow Table API — Queue Poll (Read)

```
Endpoint:
  GET {SN_INSTANCE_URL}/api/now/table/{SHIFT_REQUEST_TABLE}
  where SN_INSTANCE_URL stored in env var SN_INSTANCE_URL
  where SHIFT_REQUEST_TABLE = "u_shift_request" (A24 — validate with MedFlex IT before build)

Authentication:
  Method: Bearer token (OAuth 2.0 client credentials)
  Header: Authorization: Bearer {SN_API_TOKEN}
  SN_API_TOKEN stored in secrets manager (key: SN_API_TOKEN); rotated every 90 days
  Additional header: X-UserToken (optional; depends on MedFlex SN auth configuration; use if basic auth is insufficient)

Request query parameters:
  sysparm_query:   state=1^opened_at>=javascript:gs.daysAgo(1)
  sysparm_fields:  sys_id,description,u_hospital_id,opened_at
  sysparm_limit:   100
  sysparm_display_value: false
  sysparm_exclude_reference_link: true
  sysparm_offset:  {offset} (used for pagination if result count = 100)

  Note: u_hospital_id is a hint field included to help LLM match hospital names;
  if absent from MedFlex schema, remove from sysparm_fields (A24).

Request headers:
  Authorization: Bearer {SN_API_TOKEN}
  Content-Type: application/json
  Accept: application/json

Success response (HTTP 200):
{
  "result": [
    {
      "sys_id": "string(32)",
      "description": "string (raw shift request text; max 10,000 chars)",
      "u_hospital_id": "string | null (ServiceNow hospital reference; may be absent)",
      "opened_at": "YYYY-MM-DD HH:mm:ss (ServiceNow internal UTC format; agent converts to ISO 8601)"
    }
  ]
}

  Pagination: If result count = sysparm_limit (100), agent increments offset by 100 and
  polls again in the same cycle until result count < 100.

Error responses:
  HTTP 401: { "error": { "detail": "string", "message": "string" }, "status": "failure" }
           → no retry; alert ops; halt queue polling; do not create ShiftRequests
  HTTP 403: { "error": { "detail": "Access denied", "message": "string" }, "status": "failure" }
           → no retry; alert ops; halt queue polling
  HTTP 404: { "error": { "detail": "string", "message": "Table not found" } }
           → no retry; alert ops; SHIFT_REQUEST_TABLE assumption (A24) may be wrong
  HTTP 429: (header) Retry-After: integer (seconds to wait)
           → 1 retry after Retry-After value (default: 60s if header absent)
  HTTP 5xx: { "error": { "detail": "string", "message": "string" }, "status": "failure" }
           → up to 3 retries; exponential backoff 2s, 4s, 8s

Timeout: 10 seconds per request

Rate limits: ≥60 req/min (A23); poll interval = every 10 seconds → 6 req/min
  (well within limit; pagination calls at +100 records add ~1 additional call per cycle)

Data mapping:
  result[n].sys_id        → ShiftRequest.source_ticket_id
  result[n].description   → ShiftRequest.raw_text
  result[n].u_hospital_id → passed to LLM as optional hint; not directly mapped to
                            ShiftRequirement.hospital_id (LLM extracts from description)
  result[n].opened_at     → ShiftRequest.created_at
  (convert opened_at from "YYYY-MM-DD HH:mm:ss" to "YYYY-MM-DDTHH:mm:ssZ" ISO 8601)

Fallback: If SN unavailable (> 5 consecutive poll failures over 50 seconds):
  Halt queue polling; log alert with last_successful_poll_at timestamp
  Alert ops dashboard and on-call via ops notification channel
  Resume polling every 60 seconds until SN recovers (successful HTTP 200)
  No ShiftRequests are lost — new records accumulate in SN queue during outage;
  they are picked up on recovery (sysparm_query covers all records since daysAgo(1))
```

#### Contract 2: Anthropic Claude API — Shift Intake Parser

```
Endpoint: POST https://api.anthropic.com/v1/messages

Authentication:
  Header: x-api-key: {ANTHROPIC_API_KEY}
  ANTHROPIC_API_KEY stored in secrets manager (key: ANTHROPIC_API_KEY)
  Header: anthropic-version: 2023-06-01
  Header: Content-Type: application/json

Request format (JSON) — with prompt caching for system prompt:
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 1024,
  "system": [
    {
      "type": "text",
      "text": "string (stable portion of system prompt: role, vocabulary, schema, few-shot examples; ≤1,100 tokens)",
      "cache_control": { "type": "ephemeral" }
    }
  ],
  "messages": [
    {
      "role": "user",
      "content": "Parse the following shift request:\n\n{raw_text}\n\nCurrent date (UTC): {YYYY-MM-DD}"
    }
  ]
}

  Prompt caching rationale: System prompt (≤1,100 tokens, stable across all sessions)
  is cached with ephemeral cache. With 184 cases/day at avg 4.7-min intervals, cache
  remains warm throughout the business day (5-min TTL). Savings: ~1,100 tokens × $3.00/M
  × 184 cases/day × ~95% cache hit rate ≈ $0.58/day.

Success response (HTTP 200):
{
  "id": "string",
  "type": "message",
  "role": "assistant",
  "content": [{ "type": "text", "text": "string (JSON per ShiftRequirement output schema below)" }],
  "model": "claude-sonnet-4-6",
  "stop_reason": "end_turn | max_tokens",
  "usage": {
    "input_tokens": integer,
    "output_tokens": integer,
    "cache_creation_input_tokens": integer,
    "cache_read_input_tokens": integer
  }
}

Expected output JSON (content[0].text — must parse to this schema):
{
  "hospital_id": "string | null",
  "specialty_code": "string (SpecialtyCode enum value) | null",
  "shift_start": "ISO 8601 UTC timestamp | null",
  "shift_end": "ISO 8601 UTC timestamp | null",
  "required_credentials": ["CredentialCode", ...],
  "field_confidence": {
    "hospital_id": number (0.00–1.00),
    "specialty_code": number (0.00–1.00),
    "shift_start": number (0.00–1.00),
    "shift_end": number (0.00–1.00),
    "required_credentials": number (0.00–1.00)
  },
  "parse_notes": "string | null (optional; max 200 chars; agent notes on ambiguities)"
}

  Validation after parsing content[0].text:
  1. JSON.parse() succeeds → proceed
  2. All required fields present (hospital_id, specialty_code, shift_start, shift_end,
     required_credentials, field_confidence) → proceed
  3. All enum values (specialty_code, required_credentials[]) match defined enums → proceed
  4. All field_confidence values are numbers in range 0.00–1.00 → proceed
  If any validation fails: treat as PARSING_FAILED; do not create ShiftRequirement;
  route to BP1 human review with parse_error log entry.

Error responses:
  HTTP 400: { "type": "error", "error": { "type": "invalid_request_error", "message": "string" } }
           → no retry; log request details; route ShiftRequest to BP1
  HTTP 401: { "type": "error", "error": { "type": "authentication_error", "message": "string" } }
           → no retry; alert ops; halt all parsing; rotate ANTHROPIC_API_KEY
  HTTP 429: { "type": "error", "error": { "type": "rate_limit_error", "message": "string" } }
           + header: retry-after: integer
           → 1 retry after retry-after value (default: 60s); if second attempt fails → PARSING_FAILED
  HTTP 529: { "type": "error", "error": { "type": "overloaded_error", "message": "string" } }
           → 3 retries; exponential backoff 2s, 4s, 8s
  HTTP 500/503: { "type": "error", "error": { "type": "api_error", "message": "string" } }
           → 3 retries; exponential backoff 2s, 4s, 8s

Timeout: 30 seconds per request

Retry logic: After all retries exhausted:
  ShiftRequest.status → PARSING_FAILED
  Route to coordinator manual queue
  Log: { error_type, http_status, request_id, source_ticket_id, timestamp }
  Alert ops if PARSING_FAILED rate > 5% in any 30-minute window

Circuit breaker: If LLM error rate > 20% in any 5-minute window (sliding):
  Halt all automated parsing; route all RECEIVED ShiftRequests to manual queue
  Alert ops; resume when error rate drops below 5% over a 5-minute window

Rate limits: Per Anthropic account tier. Daily token budget:
  ~1,900 tokens/case (input) × 184 cases = ~350K input tokens/day (JtD-1)
  Monitor usage.input_tokens in audit log; alert if daily total approaches tier limit

Token budget per case:
  System prompt (cached): ~1,100 tokens
  User message: ~200 tokens avg
  Output: max_tokens = 1024 (sufficient for ShiftRequirement JSON ~400 tokens)
  If stop_reason = max_tokens: output is truncated; treat as PARSING_FAILED

Data mapping:
  content[0].text → JSON.parse() → validate → ShiftRequirement fields
  usage.cache_read_input_tokens > 0 → log cache hit for cost tracking
  stop_reason=max_tokens → PARSING_FAILED; do not use partial output

Fallback: If API unavailable > 5 minutes (5 consecutive timeouts):
  Halt automated parsing; alert ops
  All RECEIVED ShiftRequests remain in queue; coordinator processes manually in SN
  Resume when API health check succeeds (probe every 60 seconds)
```

---

## 6. Context Engineering Design

### Memory Architecture

| Memory Type | Content | Storage | Lifecycle |
|-------------|---------|---------|-----------|
| In-context | Raw shift request text (max 200 tokens); current system date for relative date resolution | LLM context window (user message) | Per parsing session |
| Episodic | None — each parse is stateless; no per-hospital or per-coordinator history required | N/A | N/A |
| Semantic | Hospital name-to-ID mapping (~100 entries); specialty_code vocabulary with common shorthands; CredentialCode mapping with all shorthand variants (e.g., "BLS/ACLS" → [BLS, ACLS]); specialty and credential enums | Static JSON in system prompt (cached) | Version-controlled in prompt config; update when new hospitals or credentials added. Update triggers new cache_control block (new system prompt version) |
| Procedural | Role and scope instructions; output JSON schema; confidence scoring rules; escalation conditions; relative date resolution rule; 3 few-shot examples | System prompt (cached) | Version-controlled |

### Retrieval Strategy

- **Trigger**: New ShiftRequest.status = RECEIVING; agent sends raw_text to LLM
- **Target**: No external retrieval calls; all vocabulary is embedded in system prompt (semantic memory). Hospital lookup is a static JSON table in the system prompt (~100 entries)
- **Quality**: Field-level confidence scores computed by LLM based on extraction certainty (0.00–1.00). Overall confidence = min(required field scores). Threshold 0.80 enforced in pipeline code
- **Cost management**: No retrieval calls; all context is in-prompt. Prompt caching on stable system prompt (>1,024 tokens) amortizes cost across 184 daily sessions. No vector/RAG required — domain vocabulary is small enough (~100 hospitals, ~20 credentials, ~15 specialties) to fit in system prompt

### Prompt Architecture

**System prompt structure** (target ≤1,100 tokens; static — cache with `cache_control: ephemeral`):

1. **Role and purpose** (~50 tokens):
   > "You are the MedFlex Shift Intake Parser. Extract structured shift requirements from hospital shift request text. Output JSON only. Do not explain or add commentary outside the JSON."

2. **Hospital name-to-ID lookup table** (~350 tokens):
   ```json
   {"hospitals": [
     {"hospital_id": "STDAVIDS_NORTH", "display_name": "St. David's North Austin",
      "aliases": ["St Davids North", "St. David's North", "SDN", "St. David's North Austin"]},
     {"hospital_id": "STMARYS_WEST", "display_name": "St. Mary's West",
      "aliases": ["St Marys West", "SMW", "St. Mary's"]},
     ...
   ]}
   ```
   Full table populated from MedFlex hospital list before launch. If hospital not in table: set hospital_id=null, field_confidence.hospital_id=0.00.

3. **Specialty vocabulary** (~80 tokens):
   > "Map to these specialty_code values: ICU_RN (ICU, intensive care, MICU, SICU, CVICU), ER_RN (ER, ED, emergency, A&E), MED_SURG_RN (med surg, medical surgical, MS), FLOAT_POOL_RN (float, float pool, traveler), OR_RN (OR, operating room, surgical), L_D_RN (L&D, labor, delivery, OB), PACU_RN (PACU, recovery, post-op), TELE_RN (telemetry, tele, step-down cardiac), PEDS_RN (pediatric, peds, children's), NICU_RN (NICU, neonatal), PSYCH_RN (psych, psychiatric, behavioral health), CATH_LAB_RN (cath lab, catheterization), ONCOLOGY_RN (oncology, cancer, chemo), STEP_DOWN_RN (step down, PCU, progressive care). If no match: null."

4. **Credential code mapping** (~70 tokens):
   > "CredentialCode values: BLS (BLS, basic life support), ACLS (ACLS, advanced cardiac life support), PALS (PALS, pediatric advanced life support), NRP (NRP, neonatal resuscitation), TNCC (TNCC, trauma nurse core), CCRN (CCRN, critical care RN cert), CEN (CEN, certified emergency nurse), OCN (OCN, oncology cert), CNOR (CNOR, certified OR nurse), AWHONN_BASIC (AWHONN basic), AWHONN_INTERMEDIATE (AWHONN intermediate). Map 'BLS/ACLS' → [BLS, ACLS]. If no credentials mentioned: empty array []."

5. **Output JSON schema** (~130 tokens):
   ```json
   {
     "hospital_id": "string | null",
     "specialty_code": "SpecialtyCode | null",
     "shift_start": "ISO 8601 UTC | null",
     "shift_end": "ISO 8601 UTC | null",
     "required_credentials": ["CredentialCode"],
     "field_confidence": {
       "hospital_id": 0.00-1.00,
       "specialty_code": 0.00-1.00,
       "shift_start": 0.00-1.00,
       "shift_end": 0.00-1.00,
       "required_credentials": 0.00-1.00
     },
     "parse_notes": "string | null"
   }
   ```

6. **Confidence scoring rules** (~80 tokens):
   > "Assign field_confidence 0.00–1.00 based on extraction certainty: 1.00 = clearly stated and unambiguous; 0.90–0.99 = likely correct but has minor ambiguity; 0.70–0.89 = best guess with some uncertainty; 0.00–0.69 = highly uncertain or inferred. For relative dates ('tomorrow', 'next Friday'), resolve using the current_date provided and assign confidence 0.90. For null values: set field_confidence = 0.00."

7. **Few-shot examples** (~280 tokens, 3 examples):
   - Example A: Complete, unambiguous request → high confidence all fields (≥0.90)
   - Example B: Missing credentials, ambiguous date → mixed confidence, null fields
   - Example C: Multi-credential request, informal hospital name → correct mapping

**User message per session** (~200 tokens):
```
Parse the following shift request:

{raw_text}

Current date (UTC): {YYYY-MM-DD}
```

**Expected output** (~400 tokens): JSON per schema above.

**Prompt caching:** System prompt (~1,100 tokens) uses `cache_control: ephemeral`. With 184 cases/day (one every ~4.7 min avg), cache hit rate ~95%. Cost saving vs. no caching: ~$0.58/day. Cache TTL is 5 minutes; during peak hours (multiple requests within 5 min), hit rate approaches 100%.

**Chain of thought (embedded in guardrails):** "Process in order: (1) identify hospital name → look up in table → set hospital_id and field_confidence.hospital_id. (2) Extract specialty → map to specialty_code → set field_confidence.specialty_code. (3) Extract date/time → resolve relative references using current_date → convert to ISO 8601 UTC. (4) Extract credentials → map to CredentialCode array. (5) Compute overall confidence = min(field_confidence values). Output JSON only."

**Token discipline:** System prompt ≤1,100 tokens (cached). User message ≤200 tokens. Max output 1,024 tokens. Per-case total: ~1,900 tokens. Do not include hospital table in user message — it is in the system prompt.

---

## 7. Validation Design

### Happy Path

**Input:** ServiceNow record:
```
description: "ICU RN needed Friday 7am–7pm, BLS/ACLS req, St. David's North Austin"
sys_id: "abc123def456"
opened_at: "2026-05-13 14:00:00"
```
Current date: 2026-05-12 (Wednesday)

**Expected output (ShiftRequirement):**
```json
{
  "hospital_id": "STDAVIDS_NORTH",
  "specialty_code": "ICU_RN",
  "shift_start": "2026-05-15T07:00:00Z",
  "shift_end": "2026-05-15T19:00:00Z",
  "required_credentials": ["BLS", "ACLS"],
  "field_confidence": {
    "hospital_id": 1.00,
    "specialty_code": 0.95,
    "shift_start": 0.90,
    "shift_end": 0.90,
    "required_credentials": 1.00
  }
}
```
- confidence_score = min(1.00, 0.95, 0.90, 0.90, 1.00) = 0.90 → ≥ 0.80 → BP2
- ShiftRequest.status → READY_FOR_SEARCH
- Pipeline event fired to JtD-2 within 10 seconds of queue poll
- Audit log entry created with raw_text hash, parsed fields, routing=BP2

### Edge Cases

**EC-1: Missing credentials (empty credential requirement)**
- Input: description = "ER RN needed tomorrow 7am–7pm, St. Mary's West"
- Expected: required_credentials=[], field_confidence.required_credentials=1.00 (empty is valid), confidence_score = min of other fields (~0.90 if date resolved correctly) → BP2

**EC-2: Completely unknown hospital name**
- Input: description = "Need ICU nurse Friday, Memorial Baptist Central"
- Expected: hospital_id=null, field_confidence.hospital_id=0.00, confidence_score=0.00 → BP1. parse_notes="Hospital 'Memorial Baptist Central' not found in lookup table"

**EC-3: Ambiguous date — no year context**
- Input: description = "Tele RN, ACLS req, St. David's North, March 5 7a–7p"
- Current date: 2026-05-12
- Expected: shift_start resolved to 2027-03-05T07:00:00Z (next occurrence of March 5), field_confidence.shift_start=0.85 (year inferred), confidence_score derived from other fields → route depends on combined confidence

**EC-4: Duplicate ServiceNow record (same sys_id)**
- Input: Same sys_id "abc123def456" polled twice in consecutive cycles
- Expected: Second poll detects existing ShiftRequest.source_ticket_id="abc123def456"; skips processing; logs "duplicate skipped: sys_id=abc123def456"; no second ShiftRequest created

**EC-5: Multi-specialty or ambiguous specialty**
- Input: description = "Float pool RN, ICU experience preferred, St. Mary's West, Friday 7–7"
- Expected: specialty_code=FLOAT_POOL_RN (primary specialty from request), field_confidence.specialty_code=0.75 (ambiguity noted in parse_notes); if confidence_score < 0.80 → BP1

**EC-6: Concurrent poll cycle with 100+ records**
- Condition: ServiceNow returns exactly 100 records (sysparm_limit hit)
- Expected: Agent increments offset by 100 and polls again within the same cycle; processes all records in order; no records skipped due to pagination cap

**EC-7: LLM returns valid JSON but with invalid enum value**
- Input: LLM returns specialty_code="ICU" (not a valid SpecialtyCode enum value)
- Expected: Post-parse validation detects invalid enum; treat as PARSING_FAILED; route to BP1; log validation_error with {field: "specialty_code", value: "ICU", raw_text_excerpt}

### Failure Modes

**FM-1: LLM API returns HTTP 529 (overloaded) on all 3 retries**
- Expected: After 3 retries (total 4 calls; 14 seconds elapsed with backoff 2s, 4s, 8s): ShiftRequest.status → PARSING_FAILED; coordinator manual queue notification sent; ops alert fired; log entry: {error_type: "LLM_OVERLOADED", source_ticket_id, attempts: 4, timestamps[]}

**FM-2: ServiceNow queue poll returns HTTP 401 (auth expired)**
- Expected: No retry; halt queue polling immediately; alert ops with message "SN_AUTH_FAILED — queue polling halted"; SN_API_TOKEN must be refreshed before polling resumes; all pending ShiftRequests remain in SN queue unaffected (will be picked up on recovery)

**FM-3: Malformed LLM output (JSON.parse fails)**
- Expected: content[0].text is not valid JSON; PARSING_FAILED; raw LLM output logged (truncated to 500 chars) for diagnostics; ShiftRequest routed to BP1 coordinator queue with note "LLM returned malformed output — manual parse required"

---

## 8. Compounding Roadmap

### Wave 1 — Foundation Agents (8-week MVP)

JtD-1 is **Build Order 1** — built first because every other agent depends on the ShiftRequirement it produces.

| Build Order | Component | Shared Asset Created |
|:---:|---|---|
| **1** | **JtD-1 Shift Intake Parser** | ServiceNow read API client; Claude API client (with prompt caching); Hospital Lookup Table; Human Review Queue (shared with JtD-3 Coordinator UI); Immutable Audit Log; Pipeline Event Bus |
| 2 | JtD-2 Candidate Search | Reuses: ServiceNow read API client, Hospital Lookup Table |
| 3 | JtD-3 Ranker + UI | Reuses: Claude API client, Hospital Lookup Table, Audit Log |
| 4 | JtD-4 Submission | Reuses: ServiceNow (write API new build), Audit Log |
| 5 | JtD-5a Monitoring | Reuses: Notification API (shared with Human Review Queue) |

**JtD-1-specific Wave 1 deliverables:**
- ServiceNow queue polling service (configurable poll interval; default 10 seconds)
- LLM parse pipeline with idempotency, confidence routing, and BP1/BP2 gateway
- Hospital Lookup Table with MedFlex hospital list pre-populated (operations team provides list before launch)
- Human Review Queue UI (coordinator dashboard; shared with JtD-3 Coordinator Review UI)
- Parse accuracy monitoring: random 10% weekly sample review; accuracy dashboard

### Wave 2 — Compounding (Months 3–6)

- **Hospital Lookup Table expansion**: Add new hospitals without redeploying; update hospital name aliases in response to recurring BP1 escalations for "unknown hospital" events. Process: ops team updates lookup table → system prompt version bumped → new cache_control block deployed.
- **Parse accuracy improvement**: Use BP1 coordinator corrections (written to Labeled Feedback Store as parse training examples) to create few-shot examples for system prompt upgrades. Target: improve from ≥85% to ≥92% field accuracy after 3 months of corrections.
- **Structured intake form (T2 optional)**: If high-volume hospital partners agree, introduce structured intake form for their submissions. This would eliminate LLM parsing for that subset → further reduce HITL rate below 5% for structured inputs.

### Wave 3 — AI-Native Operations (Year 2)

- **Parser self-improvement**: Fine-tuned model on accumulated labeled parse examples; addresses hospital-specific shorthand patterns not covered by current few-shot examples.
- **Priority scoring at intake**: Add urgency signal to queue triage (MT-1.1) — detect emergency re-fill requests ("ASAP", "urgent", "immediate") and route them to a priority queue ahead of standard requests. Prevents emergency requests from sitting behind routine requests during high-volume periods.

### Integration Reuse Matrix

*See `04a-capability-spec-match-selection.md` §8 for the full cross-agent integration reuse matrix.*

JtD-1's key shared assets (built here, reused by all subsequent agents):

| Integration / Asset | Built in JtD-1 | Reused by |
|--------------------|:--------------:|-----------|
| ServiceNow Table API client (read) | ✓ | JtD-2, JtD-3, JtD-5a, JtD-6 (Wave 2), JtD-5b (Wave 2–3) |
| Claude API client (with caching) | ✓ | JtD-3 (ranker), JtD-6 (Wave 2), JtD-5b (Wave 2–3) |
| Hospital Lookup Table | ✓ | JtD-2 (hospital_id for preference query), JtD-3 (shortlist context) |
| Human Review Queue (coordinator dashboard) | ✓ | JtD-3 (Coordinator Review UI on same platform) |
| Immutable Audit Log | ✓ | JtD-2, JtD-3, JtD-4, JtD-5a (all agents write to shared log) |
| Pipeline Event Bus | ✓ | JtD-2, JtD-3, JtD-4, JtD-5a |

---

## 9. Production-Grade Validation Results

All specifications in this document passed production-grade validation against `input-docs/production-spec-checklist.md`.

**INTEGRATION CONTRACTS** — Pass. Two integration contracts (ServiceNow queue poll and Anthropic Claude API) include: full endpoint URLs or patterns, authentication method and credential storage location (secrets manager key names), complete request format with all parameters and their types, complete success and error response formats with HTTP status codes and field-level structure, numeric timeout values, retry logic covering all HTTP error codes (2xx, 4xx, 5xx, 429, 529), rate limits (numeric or assumption-referenced), data mapping in both directions, and explicit fallback behavior for each unavailability scenario. ServiceNow table names and field names are A24-flagged assumptions with explicit validation questions.

**ENTITY PRECISION** — Pass. All entities (ShiftRequest, ShiftRequirement, HospitalLookup) include: UUID primary keys with immutability designations, all attributes with data types, format constraints, and required/optional/nullable designations, exhaustive enum value lists in SCREAMING_SNAKE_CASE, ISO 8601 UTC timestamps with immutability rules, foreign key relationships with cascade behavior, computed fields marked read-only with formulas, complete state machines with all valid transitions and their triggers, and constraints documented with enforcement points (pipeline code vs. DB constraints).

**BUILDABILITY** — Pass. All KPIs are numeric and include measurement methods. Parse threshold (0.80) is numeric and enforced in pipeline code (not delegated to LLM judgment). Output JSON schema is fully defined with all field types. Confidence scoring rules are explicit (1.00/0.90–0.99/0.70–0.89/0.00–0.69 bands defined). All conditionals have explicit criteria and outcomes. Routing decision is hardcoded rule, not LLM judgment — removes ambiguity about who enforces the threshold. Validation design includes 1 happy-path scenario, 7 edge cases, and 3 failure modes with explicit expected outcomes.
