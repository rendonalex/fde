# Capability Spec — Shift Intake Parsing (JtD-1)
## MedFlex Agentic Transformation

> ATX Phase 4 deliverable. Input sources: `specs/cognitive-load-map.md`, `specs/03-agentic-solution-architecture.md`, `specs/volume-×-value-analysis.md`, `specs/assumptions.md`, `input-docs/atx/atx-agent-mapping.md`.
> Assumption IDs reference `specs/assumptions.md`. New assumptions added in this spec: none (A26–A28 defined in 04a apply to the shared platform; this spec references A10, A11-read, A11-write, A22, A23, A24 as primary).

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Agent Purpose Document](#2-agent-purpose-document)
3. [Entity Data Models](#3-entity-data-models)
4. [Agent Activity Catalog](#4-agent-activity-catalog)
5. [Autonomy Matrix](#5-autonomy-matrix)
6. [System and Data Inventory](#6-system-and-data-inventory)
7. [Integration Contracts](#7-integration-contracts)
8. [Context Engineering Design](#8-context-engineering-design)
9. [Compounding Roadmap](#9-compounding-roadmap)
10. [Validation Design](#10-validation-design)

---

## 1. Executive Summary

The Shift Intake Parser is the first agent in the MedFlex matching pipeline and the primary bottleneck to the <1-hour fill-time target. Every downstream automation — candidate search (JtD-2), ranking (JtD-3), submission (JtD-4) — is blocked until this agent converts a free-text hospital request into a structured `ParsedShiftRequirement` object.

**What it does**: Polls the ServiceNow `u_shift_request` queue every 30 seconds. For each new record, calls Claude Sonnet to extract specialty code, shift datetime, location ID, and credential requirements from free text. High-confidence parses (≥ 0.85) proceed automatically to JtD-2 (BP2). Low-confidence parses route to the human review queue (BP1) for coordinator correction.

**Why it matters**: Parsing currently consumes ~35% of coordinator active work time per match (A16). At 184 fills/day (A4), that is approximately 1,274 minutes of daily parsing labor. The agent eliminates this for the ~85% of requests that parse cleanly (A10), reducing coordinator parse time to ~191 minutes/day — and cutting fill time by removing the queue accumulation delay between request arrival and structured data availability.

**MVP archetype**: Agent-led + Human Oversight (BP1 for exceptions; BP2 for standard path). Stable through Phase 2 — free-text input is a permanent feature of hospital behavior; the HITL path for ambiguous requests does not go away.

**Output schema lock**: The `ParsedShiftRequirement` JSON contract is frozen at end of week 1. JtD-2 (candidate search) and JtD-3 (ranker data model) build against this locked interface. Schema changes after week 1 break downstream integration contracts and are a named project risk.

**Key metrics**:
- Parser accuracy: ≥ 85% field-level extraction on 200-record validation corpus (A10)
- HITL rate: ≤ 15% of requests routed to BP1 human review
- Parse latency: ≤ 30 seconds from QUEUED to PARSED status
- Cost per parse: ≤ $0.011/case (A22: ~1,500 input / ~400 output tokens at Sonnet pricing)

---

## 2. Agent Purpose Document

### Agent Name
**MedFlex Shift Intake Parser**

### Job to be Done
Given a free-text hospital shift request in ServiceNow, extract structured shift requirements (specialty, datetime, location, credential list) and produce a validated `ParsedShiftRequirement` object. Route high-confidence extractions automatically to JtD-2. Route low-confidence extractions to the human review queue with the partial parse and failure reason attached.

### Delegation Archetype
**Agent-led + Human Oversight** (MVP and Phase 2 stable)

The agent processes 100% of inbound requests. Human action is required only for the exception path (BP1): low-confidence parses, fully unparseable requests, and LLM-unavailable fallbacks. Routine parsing produces no coordinator interaction.

### KPIs

| Metric | Target | Source |
|---|---|---|
| Field-level extraction accuracy (200-record corpus) | ≥ 85% | A10 |
| HITL rate (BP1 route) | ≤ 15% | A10 |
| Parse latency (QUEUED → PARSED) | ≤ 30 seconds | LLM timeout + 2 writes |
| Cost per parse | ≤ $0.011/case | A22 |
| LLM fallback rate (API unavailable > 60s) | ≤ 1% | Operational target |
| Queue clearance SLA (QUEUED → PARSING) | ≤ 30 seconds | Polling interval |

### Scope Boundary

**In scope (MVP)**:
- Poll ServiceNow `u_shift_request` for QUEUED records
- LLM extraction of specialty, datetime, location, credentials
- Confidence scoring and threshold routing (BP1/BP2)
- Write `ParsedShiftRequirement` to ServiceNow
- Write low-confidence cases to internal HITL queue
- Status updates on `u_shift_request` throughout pipeline

**Out of scope (MVP)**:
- Hospital clarification outreach (coordinator handles via existing channels)
- Priority scoring within the QUEUED set (FIFO in MVP; priority queue in Wave 2)
- Structured intake form overlay (T2 deferred to Phase 2 for high-volume partners)
- Multi-nurse request splitting (single-nurse requests only in MVP; see Edge Case 3)

### Upstream Dependencies
- ServiceNow `u_shift_request` records created by hospitals (email, portal, phone transcription)
- A11-read: ServiceNow read credentials provisioned by end of week 2
- ANTHROPIC_API_KEY: provisioned at engagement start

### Downstream Consumers
- **JtD-2 (Candidate Search)**: reads `ParsedShiftRequirement` as the trigger for specialty + credential database query
- **JtD-3 (Match Selection ranker)**: reads `specialty_code`, `credentials[]`, `location_id` for scoring; schema locked end of week 1

---

## 3. Entity Data Models

---

### 3.1 ShiftRequest

The raw inbound record created in ServiceNow when a hospital submits a shift request. This is the agent's input queue.

| Attribute | Type | Constraints |
|---|---|---|
| `sys_id` | string (ServiceNow UUID) | Primary key; immutable; generated by ServiceNow on creation |
| `u_shift_request_id` | UUID | Application-layer ID; used as idempotency key in downstream writes; immutable |
| `u_source_type` | enum [`EMAIL`, `PORTAL_FORM`, `PHONE_TRANSCRIPTION`] | Required; set at creation by intake channel |
| `u_raw_text` | string | Required; max 5,000 characters; the literal text of the hospital request; immutable once created |
| `u_hospital_id` | string | Required; FK to hospital record in ServiceNow; immutable |
| `u_status` | enum [`QUEUED`, `PARSING`, `PARSED`, `HUMAN_REVIEW`, `PARSE_FAILED`, `CANCELLED`] | Required; default `QUEUED`; updated by agent and coordinator |
| `u_failure_reason` | string | Optional; max 500 characters; set when routing to `HUMAN_REVIEW` or `PARSE_FAILED`; null otherwise |
| `u_received_at` | ISO 8601 datetime, UTC | Required; set by ServiceNow on record creation; immutable |
| `u_parsed_at` | ISO 8601 datetime, UTC | Optional; set by agent when status transitions to `PARSED`; null until then |
| `u_reviewed_by` | string (coordinator user_id) | Optional; set when a coordinator completes a HUMAN_REVIEW correction; null on auto-parse path |
| `sys_created_at` | ISO 8601 datetime, UTC | Set by ServiceNow; immutable |
| `sys_updated_at` | ISO 8601 datetime, UTC | Updated by ServiceNow on any modification |

**State Machine:**

```
QUEUED ──────────────────────────────► PARSING
                                           │
                        ┌──────────────────┼─────────────────────┐
                        ▼                  ▼                     ▼
                  PARSED (BP2)      HUMAN_REVIEW (BP1)     PARSE_FAILED
                  confidence ≥ 0.85  confidence < 0.85     LLM error / 
                                     or LLM unavailable    invalid JSON
                                           │
                              ┌────────────┴──────────────┐
                              ▼                           ▼
                         PARSED                      CANCELLED
                    (coordinator corrects)     (coordinator determines
                                               request invalid/duplicate)

PARSE_FAILED ──► QUEUED  (manual re-queue after investigation)
```

**Transition rules:**
- `QUEUED → PARSING`: agent picks up record during poll cycle; must acquire advisory lock (no two agents process same record)
- `PARSING → PARSED`: LLM returns valid JSON; confidence_score ≥ 0.85; agent writes `ParsedShiftRequirement`; sets `u_parsed_at`
- `PARSING → HUMAN_REVIEW`: confidence_score < 0.85, OR LLM unavailable > 60 seconds, OR LLM returns malformed JSON after 1 retry; sets `u_failure_reason`
- `PARSING → PARSE_FAILED`: LLM returns HTTP 400/401/422 (bad request — do not retry); sets `u_failure_reason` with LLM error detail
- `HUMAN_REVIEW → PARSED`: coordinator reviews and submits corrected parse via HITL queue interface; sets `u_reviewed_by`, `u_parsed_at`
- `HUMAN_REVIEW → CANCELLED`: coordinator determines request is invalid, duplicate, or already handled outside system
- `PARSE_FAILED → QUEUED`: ops manually re-queues after root cause investigation; clears `u_failure_reason`
- `PARSED` is terminal for the parser (JtD-2 picks up from here)
- `CANCELLED` is terminal

**Constraints:**
- `u_raw_text` is immutable after creation — never modified, even during human review (corrections go into `ParsedShiftRequirement`, not into the source record)
- `u_parsed_at` is set once; immutable thereafter
- Only one `ParsedShiftRequirement` per `u_shift_request_id` (enforced by unique constraint on the parsed record table)

---

### 3.2 ParsedShiftRequirement

The locked output schema of the parser. This is the contract that JtD-2 and JtD-3 build against. Schema frozen end of week 1.

| Attribute | Type | Constraints |
|---|---|---|
| `sys_id` | string (ServiceNow UUID) | Primary key; immutable |
| `u_parsed_requirement_id` | UUID | Application-layer ID; immutable; idempotency key for downstream writes |
| `u_shift_request_id` | UUID | Required; FK to `ShiftRequest.u_shift_request_id`; unique (one-to-one); immutable |
| `u_specialty_code` | string | Required; must be a valid value from SpecialtyCode dictionary (§8.2); max 20 chars |
| `u_datetime_start` | ISO 8601 datetime, UTC | Required; shift start time; must be a future datetime at time of parse |
| `u_datetime_end` | ISO 8601 datetime, UTC | Required; shift end time; must be > `u_datetime_start`; typical range 8–16 hours |
| `u_location_id` | string | Required; must match a valid value from HospitalLocation lookup (§8.3); max 50 chars |
| `u_credentials` | JSON array of strings | Required; min 0 items, max 10 items; each item must be a valid CredentialCode (§8.2); empty array `[]` is valid (no credentials specified) |
| `u_confidence_score` | decimal(3,2) | Required; range 0.00–1.00; overall parse confidence; see §8.4 for scoring rules |
| `u_parse_method` | enum [`LLM_AUTO`, `HUMAN_CORRECTED`] | Required; `LLM_AUTO` if confidence ≥ 0.85 auto-path; `HUMAN_CORRECTED` if coordinator edited |
| `u_parsed_by` | string | Required; `AGENT` for LLM_AUTO path; coordinator user_id string for HUMAN_CORRECTED path |
| `u_created_at` | ISO 8601 datetime, UTC | Required; set on creation; immutable |
| `u_updated_at` | ISO 8601 datetime, UTC | Updated on any modification (only possible if coordinator corrects in HUMAN_REVIEW path) |

**Constraints:**
- `u_shift_request_id` has a unique constraint — only one `ParsedShiftRequirement` per `ShiftRequest`; a second write attempt returns HTTP 409
- `u_specialty_code` must match an entry in the SpecialtyCode dictionary loaded in the system prompt (§8.2); if LLM returns a code not in the dictionary, confidence_score for that field is capped at 0.50 and the record routes to `HUMAN_REVIEW`
- `u_datetime_start` must be in the future at parse time; if the extracted datetime is in the past, set confidence_score for datetime to 0.00 and route to `HUMAN_REVIEW` with `u_failure_reason = DATETIME_IN_PAST`
- `u_credentials` may be an empty array if the hospital request specifies no credential requirements — this is valid, not an error
- `u_parse_method` is immutable once set
- `u_parsed_by` is immutable once set

**Schema lock note**: Fields, types, and constraints above are frozen at end of week 1. Adding a field is a non-breaking change (JtD-2 and JtD-3 ignore unknown fields). Removing or renaming a field is a breaking change requiring explicit version coordination with JtD-2 and JtD-3 teams.

---

### 3.3 HITLQueueEntry

The record written to the internal HITL queue when a `ShiftRequest` routes to BP1. This is what the coordinator sees in the human review interface.

| Attribute | Type | Constraints |
|---|---|---|
| `hitl_entry_id` | UUID | Primary key; immutable; generated on creation |
| `u_shift_request_id` | UUID | Required; FK to `ShiftRequest.u_shift_request_id`; unique per entry |
| `u_raw_text` | string | Required; copy of `ShiftRequest.u_raw_text`; immutable |
| `u_partial_parse` | JSON object | Optional; the partial extraction the LLM produced before confidence threshold failure; null if LLM was unavailable; fields match `ParsedShiftRequirement` schema |
| `u_failure_reason` | enum [`LOW_CONFIDENCE`, `LLM_UNAVAILABLE`, `INVALID_JSON`, `DATETIME_IN_PAST`, `UNKNOWN_SPECIALTY`, `AMBIGUOUS_LOCATION`] | Required; set by agent at routing time |
| `u_confidence_score` | decimal(3,2) | Optional; the confidence score if LLM ran; null if LLM unavailable |
| `u_status` | enum [`PENDING`, `IN_REVIEW`, `COMPLETED`, `CANCELLED`] | Required; default `PENDING` |
| `u_assigned_to` | string (coordinator user_id) | Optional; set when coordinator picks up the entry; null until claimed |
| `u_created_at` | ISO 8601 datetime, UTC | Required; immutable |
| `u_completed_at` | ISO 8601 datetime, UTC | Optional; set when coordinator submits correction or cancels |

**State Machine:**
```
PENDING → IN_REVIEW (coordinator claims the entry)
IN_REVIEW → COMPLETED (coordinator submits corrected parse → writes ParsedShiftRequirement)
IN_REVIEW → CANCELLED (coordinator cancels the shift request)
PENDING → CANCELLED (ops cancels without coordinator review)
```

---

## 4. Agent Activity Catalog

| MT | Micro-Task | Description | Delegation Level | Tools Required |
|---|---|---|---|---|
| MT-1.0 | Poll ServiceNow queue | GET `u_shift_request` where `u_status = QUEUED`; batch up to 10 records per cycle; 30-second interval | Fully Agentic | ServiceNow REST API (read) |
| MT-1.1 | Acquire processing lock | PATCH `u_status = PARSING` on selected record; acts as advisory lock to prevent duplicate processing by concurrent agent instances | Fully Agentic | ServiceNow REST API (write) |
| MT-1.2 | LLM extraction call | POST to Claude Sonnet API with system prompt (§8.1) + raw_text; receive structured JSON with per-field confidence scores | Fully Agentic | Claude Sonnet API (ANTHROPIC_API_KEY) |
| MT-1.3 | Validate LLM response schema | Parse LLM JSON output; validate all required fields present; validate specialty_code against SpecialtyCode dict; validate credential codes against CredentialCode dict; validate datetime format | Fully Agentic | Internal validation logic |
| MT-1.4a | Compute overall confidence score | `confidence_score = min(specialty_confidence, datetime_confidence, location_confidence, credential_confidence)`; see §8.4 for per-field scoring rules | Fully Agentic | Internal logic |
| MT-1.4b | Route high-confidence parse (BP2) | If `confidence_score ≥ 0.85`: write `ParsedShiftRequirement`; PATCH `u_status = PARSED`; set `u_parsed_at`; emit `shift_parsed` event to trigger JtD-2 | Fully Agentic | ServiceNow REST API (write) |
| MT-1.4c | Route low-confidence parse (BP1) | If `confidence_score < 0.85`, or LLM unavailable, or invalid JSON: write `HITLQueueEntry` with partial parse + failure reason; PATCH `u_status = HUMAN_REVIEW` | Agent Routes, Human Resolves | ServiceNow REST API (write); Internal HITL Queue API (write) |
| MT-1.5 | Handle PARSE_FAILED | If LLM returns HTTP 400/401/422 (non-retryable): PATCH `u_status = PARSE_FAILED`; set `u_failure_reason` with LLM error detail; alert ops | Fully Agentic | ServiceNow REST API (write); ops alert channel |
| MT-1.6 | Human review correction (BP1 resolution) | Coordinator reviews `HITLQueueEntry`; edits partial parse in HITL UI; submits correction → writes `ParsedShiftRequirement` with `u_parse_method = HUMAN_CORRECTED`; PATCH `ShiftRequest.u_status = PARSED` | Human Acts, Agent Logs | Internal HITL Queue API; ServiceNow REST API (write) |
| MT-1.7 | Emit parsed event to JtD-2 | On `PARSED` transition (both auto and human-corrected paths): write `shift_parsed` event with `u_shift_request_id` and `u_parsed_requirement_id` to trigger JtD-2 candidate search | Fully Agentic | Internal event bus or ServiceNow workflow trigger |

**Delegation level definitions:**
- **Fully Agentic**: agent executes without human notification or approval
- **Agent Routes, Human Resolves**: agent makes the routing decision; human performs the resolution action (correct the parse)
- **Human Acts, Agent Logs**: human takes the action; agent records it in ServiceNow

---

## 5. Autonomy Matrix

### Category 1 — Agent Decides Alone (No Human Notification)

| Decision | Threshold | Rationale |
|---|---|---|
| Pick up QUEUED record for processing | Any QUEUED record; FIFO order | Deterministic queue consumption; no judgment required |
| Call Claude Sonnet API | Every record | Standard execution; no human value in approval |
| Route to BP2 (auto-proceed) | confidence_score ≥ 0.85 | Threshold is explicit and numeric; A10 validates this produces ≤ 15% HITL rate |
| Apply exponential backoff on LLM HTTP 529 | Up to 3 retries (4s, 8s, 16s) | Standard retry; no human value in notification |
| Use cached specialty/credential dictionary | Valid dict version loaded at startup | Cache is trusted until explicitly refreshed; staleness risk is low |

### Category 2 — Agent Acts, Human Notified After

| Decision | Trigger | Notification Target | Latency |
|---|---|---|---|
| Route to PARSE_FAILED | LLM returns 400/401/422 | Ops alert channel | Immediate |
| Alert on consecutive LLM failures | ≥ 10 consecutive LLM unavailability events | Ops alert channel | After 10th failure (~5 minutes at 30s interval) |
| Route to HUMAN_REVIEW (LLM unavailable > 60s) | LLM API down > 60 seconds | HITL queue alert | Immediate |

### Category 3 — Agent Proposes, Human Resolves

| Decision | Agent Action | Human Action | SLA |
|---|---|---|---|
| Low-confidence parse (BP1) | Write HITLQueueEntry with partial parse + failure_reason; PATCH status to HUMAN_REVIEW | Coordinator reviews raw text, edits partial parse, submits correction | PENDING → IN_REVIEW: ≤ 30 minutes; IN_REVIEW → COMPLETED: ≤ 60 minutes; if not completed in 90 minutes, coordinator manager notified |
| Unparseable request (all fields null) | Write HITLQueueEntry with failure_reason = LOW_CONFIDENCE; partial_parse = null | Coordinator contacts hospital for clarification; submits manual parse or cancels | Same SLA as above |

### Category 4 — Human Takes Over

| Scenario | Handoff Mechanism | Agent State |
|---|---|---|
| Coordinator determines request is duplicate | HITL UI cancel action | HUMAN_REVIEW → CANCELLED; no ParsedShiftRequirement written |
| Coordinator determines request is invalid/malformed | HITL UI cancel action | HUMAN_REVIEW → CANCELLED |
| Ops manually re-queues PARSE_FAILED record | Manual PATCH in ServiceNow | PARSE_FAILED → QUEUED; agent picks up on next poll |

### HITL SLA Summary

| Queue state | SLA | Escalation |
|---|---|---|
| PENDING (not yet claimed) | ≤ 30 minutes | After 30 min: coordinator team lead notified |
| IN_REVIEW (claimed, not resolved) | ≤ 60 minutes from claim | After 60 min: manager notified; entry flagged in ops dashboard |
| PARSE_FAILED (no manual re-queue) | ≤ 4 hours | After 4 hours: ops incident |

---

## 6. System and Data Inventory

### Systems

| System | Role | Access Type | Credential | Provisioning Gate |
|---|---|---|---|---|
| ServiceNow `u_shift_request` | Input queue; status tracking | Read + Write (PATCH status fields) | `SERVICENOW_READ_TOKEN` (read), `SERVICENOW_WRITE_TOKEN` (status PATCH) | A11-read by end of week 2; A11-write by end of week 3 |
| ServiceNow `u_parsed_shift_requirement` | Output store for parsed requirements | Write (POST) | `SERVICENOW_WRITE_TOKEN` | A11-write by end of week 3 |
| Claude Sonnet API | LLM extraction engine | Write (POST /v1/messages) | `ANTHROPIC_API_KEY` | Provisioned at engagement start |
| Internal HITL Queue API | Low-confidence case routing | Write (POST /internal/api/v1/hitl-queue) | JWT Bearer (system service token) | Built in week 2–3 |
| Internal Event Bus | Trigger JtD-2 on PARSED | Write (emit shift_parsed event) | Internal service auth | Shared platform component (built with JtD-2 integration) |
| Ops Alert Channel | PARSE_FAILED and LLM failure alerts | Write | Configured at deployment | Week 1 infrastructure setup |

### Data Dependencies

| Data | Source | Structure | Freshness | If Unavailable |
|---|---|---|---|---|
| SpecialtyCode dictionary | Loaded at agent startup from config | Static enum (30+ codes); see §8.2 | Refreshed on agent restart; updated as part of system prompt changes | Agent cannot validate specialty_code; routes to HUMAN_REVIEW with UNKNOWN_SPECIALTY |
| CredentialCode dictionary | Loaded at agent startup from config | Static enum (15+ codes); see §8.2 | Refreshed on agent restart | Agent cannot validate credentials; marks credential_confidence = 0.50; may route to HUMAN_REVIEW |
| HospitalLocation lookup | Loaded at agent startup from config | Hospital name variants → location_id mapping | Refreshed on agent restart | Agent cannot map hospital name; routes to HUMAN_REVIEW with AMBIGUOUS_LOCATION |
| Raw shift request text | ServiceNow `u_raw_text` field | Free text; max 5,000 chars | Created on inbound request; immutable | No raw text = PARSE_FAILED immediately |

### A24 Dependency Note

All ServiceNow table names (`u_shift_request`, `u_parsed_shift_requirement`) and field names (`u_status`, `u_raw_text`, etc.) use the `u_` prefix convention per A24. Actual names must be validated against MedFlex's ServiceNow schema before development begins. A24 is Low confidence — this is the highest-risk data assumption for this spec.

---

## 7. Integration Contracts

---

### 7.1 ServiceNow — Queue Poll (Read)

**Purpose**: Retrieve QUEUED shift requests for processing.

**Endpoint**: `GET https://{SERVICENOW_INSTANCE}.service-now.com/api/now/table/u_shift_request`

**Authentication**: `Authorization: Bearer {SERVICENOW_READ_TOKEN}` (env var: `SERVICENOW_READ_TOKEN`)

**Request**:
```
Query parameters:
  sysparm_query=u_status%3DQUEUED  (u_status = QUEUED)
  sysparm_limit=10                  (batch up to 10 per poll cycle)
  sysparm_fields=sys_id,u_shift_request_id,u_raw_text,u_hospital_id,u_source_type,u_received_at
  sysparm_order_by=u_received_at    (FIFO order; oldest first)
```

**Success response (HTTP 200)**:
```json
{
  "result": [
    {
      "sys_id": "string",
      "u_shift_request_id": "uuid-string",
      "u_raw_text": "string",
      "u_hospital_id": "string",
      "u_source_type": "EMAIL|PORTAL_FORM|PHONE_TRANSCRIPTION",
      "u_received_at": "ISO 8601 datetime"
    }
  ]
}
```
Empty `result` array = no QUEUED records; agent sleeps until next poll interval. Not an error.

**Error responses**:
- HTTP 401: invalid token → halt; alert ops; do not retry automatically
- HTTP 403: insufficient permissions → halt; alert ops (A11-read not provisioned correctly)
- HTTP 429: rate limit → back off for 60 seconds; then retry
- HTTP 5xx: server error → retry up to 3 times with exponential backoff (4s, 8s, 16s); if all fail, skip cycle and wait for next poll interval

**Timeout**: 10 seconds

**Rate limit**: ≥ 60 requests/minute assumed (A23); poll at 30-second intervals = 2 requests/minute; well within limit

**Fallback**: If ServiceNow is unreachable for > 5 minutes: halt polling; emit ops alert; resume on next successful connection. QUEUED records remain in ServiceNow and are not lost — they accumulate and are processed when polling resumes.

---

### 7.2 ServiceNow — Status PATCH (Write)

**Purpose**: Update `u_status` on a `ShiftRequest` record to track processing state (PARSING, PARSED, HUMAN_REVIEW, PARSE_FAILED).

**Endpoint**: `PATCH https://{SERVICENOW_INSTANCE}.service-now.com/api/now/table/u_shift_request/{sys_id}`

**Authentication**: `Authorization: Bearer {SERVICENOW_WRITE_TOKEN}` (env var: `SERVICENOW_WRITE_TOKEN`; requires A11-write)

**Request body (JSON)**:
```json
{
  "u_status": "PARSING|PARSED|HUMAN_REVIEW|PARSE_FAILED",
  "u_failure_reason": "string (optional; max 500 chars; required when status = HUMAN_REVIEW or PARSE_FAILED)",
  "u_parsed_at": "ISO 8601 datetime, UTC (required when status = PARSED)"
}
```

**Success response (HTTP 200)**:
```json
{
  "result": {
    "sys_id": "string",
    "u_status": "string",
    "sys_updated_at": "ISO 8601 datetime"
  }
}
```

**Error responses**:
- HTTP 401/403: credential error → halt; alert ops
- HTTP 404: record not found → log and skip (race condition: record deleted between poll and PATCH); do not retry
- HTTP 409: status already set to target value → treat as success (idempotent); do not retry
- HTTP 5xx: server error → retry up to 3 times with exponential backoff (4s, 8s, 16s); if all fail, write to dead-letter queue; alert ops

**Timeout**: 10 seconds

**Idempotency**: If PATCH to `PARSING` fails and agent retries, a second PATCH of the same `sys_id` to `PARSING` returns HTTP 409 (already in that state) — treated as success. The agent does not double-process the same record.

**Critical**: PATCH to `PARSING` is the advisory lock mechanism. If this write fails, the agent must NOT proceed to call the LLM — it must skip the record and attempt on next poll cycle to avoid duplicate processing.

---

### 7.3 ServiceNow — ParsedShiftRequirement Write (Write)

**Purpose**: Persist the structured extraction result to ServiceNow.

**Endpoint**: `POST https://{SERVICENOW_INSTANCE}.service-now.com/api/now/table/u_parsed_shift_requirement`

**Authentication**: `Authorization: Bearer {SERVICENOW_WRITE_TOKEN}` (env var: `SERVICENOW_WRITE_TOKEN`; requires A11-write)

**Request body (JSON)**:
```json
{
  "u_shift_request_id": "uuid-string (required; unique constraint)",
  "u_specialty_code": "string (required; valid SpecialtyCode)",
  "u_datetime_start": "ISO 8601 datetime, UTC (required)",
  "u_datetime_end": "ISO 8601 datetime, UTC (required)",
  "u_location_id": "string (required; valid HospitalLocation ID)",
  "u_credentials": ["CREDENTIAL_CODE_1", "CREDENTIAL_CODE_2"] ,
  "u_confidence_score": 0.00,
  "u_parse_method": "LLM_AUTO|HUMAN_CORRECTED",
  "u_parsed_by": "AGENT|coordinator_user_id"
}
```

**Success response (HTTP 201)**:
```json
{
  "result": {
    "sys_id": "string",
    "u_parsed_requirement_id": "uuid-string",
    "u_shift_request_id": "uuid-string",
    "u_created_at": "ISO 8601 datetime"
  }
}
```

**Error responses**:
- HTTP 401/403: credential error → halt; alert ops
- HTTP 409: `u_shift_request_id` already exists → treat as success (idempotent write); do not create a duplicate; use the existing record's `u_parsed_requirement_id` for downstream event emission
- HTTP 422: invalid field value (e.g., `u_specialty_code` not in allowed values) → do not retry; PATCH `ShiftRequest.u_status = PARSE_FAILED`; log validation error detail
- HTTP 5xx: server error → retry up to 3 times with exponential backoff (4s, 8s, 16s); if all fail, write to dead-letter queue; **do not emit `shift_parsed` event until write is confirmed**; alert ops

**Timeout**: 15 seconds (larger payload than status PATCH)

**Ordering constraint**: This write must succeed before emitting the `shift_parsed` event to JtD-2. If the write fails after retries, JtD-2 must not be triggered for this record. The dead-letter queue reconciliation cron will re-attempt the write and trigger JtD-2 once confirmed.

---

### 7.4 Claude Sonnet API — LLM Extraction

**Purpose**: Extract structured shift requirements from free-text hospital request.

**Endpoint**: `POST https://api.anthropic.com/v1/messages`

**Authentication**: `x-api-key: {ANTHROPIC_API_KEY}` (env var: `ANTHROPIC_API_KEY`)

**Request body (JSON)**:
```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 600,
  "system": "<system_prompt_content>",
  "messages": [
    {
      "role": "user",
      "content": "Parse the following hospital shift request:\n\n{u_raw_text}"
    }
  ]
}
```

**Token budget** (A22):
- System prompt: ~700 tokens (specialty dict + credential dict + location lookup + instructions + 3 few-shot examples)
- User message: ~200 tokens (raw shift request text average)
- Output: ~400 tokens (JSON extraction with per-field confidence scores)
- **Total per call: ~1,500 input / ~400 output = $0.011/case at Sonnet pricing**

**Expected response (HTTP 200)**:
```json
{
  "id": "msg_...",
  "content": [
    {
      "type": "text",
      "text": "{ \"specialty_code\": \"ICU_RN\", \"specialty_confidence\": 0.95, \"datetime_start\": \"2026-05-15T07:00:00Z\", \"datetime_start_confidence\": 0.90, \"datetime_end\": \"2026-05-15T19:00:00Z\", \"datetime_end_confidence\": 0.90, \"location_id\": \"ST_DAVIDS_NORTH\", \"location_confidence\": 0.95, \"credentials\": [\"BLS\", \"ACLS\"], \"credential_confidence\": 1.00 }"
    }
  ],
  "usage": {
    "input_tokens": 1487,
    "output_tokens": 412
  }
}
```

**Error responses and handling**:
- HTTP 200 with malformed JSON in `content[0].text` → validate JSON schema; if invalid, retry once; if second attempt also malformed, route to HUMAN_REVIEW with `failure_reason = INVALID_JSON`
- HTTP 400 (bad request — invalid model, malformed request): do NOT retry; PATCH `ShiftRequest.u_status = PARSE_FAILED`; log error detail; alert ops
- HTTP 401 (invalid API key): halt all processing immediately; alert ops
- HTTP 422 (unprocessable entity): do NOT retry; PATCH status to PARSE_FAILED; log
- HTTP 429 (rate limit): retry after `retry-after` header value; if no header, wait 60 seconds
- HTTP 529 (overloaded): retry up to 3 times with exponential backoff (4s, 8s, 16s); if all fail after 60 seconds total elapsed, route to HUMAN_REVIEW with `failure_reason = LLM_UNAVAILABLE`
- HTTP 5xx (other server errors): same as 529 handling

**Timeout**: 30 seconds. If LLM does not respond within 30 seconds: count as one failure; retry once on 529 handling path; if LLM unavailable for 60 cumulative seconds → route to HUMAN_REVIEW.

**Rate limits** (Anthropic Tier 3): 5,000 requests/minute; 400,000 tokens/minute. At 184 fills/day over 8-hour window: ~0.38 requests/minute. Well within limits.

**Fallback**: After 10 consecutive LLM failures (any error type): alert ops; continue routing affected requests to HUMAN_REVIEW; do not halt polling.

**Data mapping**:
- `u_raw_text` → `messages[0].content` (user turn)
- System prompt → static content per §8.1 (loaded at agent startup)
- LLM response `specialty_code` → `ParsedShiftRequirement.u_specialty_code`
- LLM response `datetime_start` → `ParsedShiftRequirement.u_datetime_start`
- LLM response `datetime_end` → `ParsedShiftRequirement.u_datetime_end`
- LLM response `location_id` → `ParsedShiftRequirement.u_location_id`
- LLM response `credentials` → `ParsedShiftRequirement.u_credentials`
- Per-field confidence scores → used in §8.4 confidence computation → `ParsedShiftRequirement.u_confidence_score`

---

### 7.5 Internal HITL Queue API — Write

**Purpose**: Write low-confidence cases to the coordinator human review queue.

**Endpoint**: `POST /internal/api/v1/hitl-queue`

**Authentication**: `Authorization: Bearer {SYSTEM_SERVICE_TOKEN}` (env var: `SYSTEM_SERVICE_TOKEN`; system-to-system auth, not coordinator SSO)

**Request body (JSON)**:
```json
{
  "shift_request_id": "uuid-string (required)",
  "raw_text": "string (required; max 5000 chars)",
  "partial_parse": {
    "specialty_code": "string or null",
    "datetime_start": "ISO 8601 or null",
    "datetime_end": "ISO 8601 or null",
    "location_id": "string or null",
    "credentials": ["array or null"],
    "confidence_score": 0.00
  },
  "failure_reason": "LOW_CONFIDENCE|LLM_UNAVAILABLE|INVALID_JSON|DATETIME_IN_PAST|UNKNOWN_SPECIALTY|AMBIGUOUS_LOCATION (required)",
  "received_at": "ISO 8601 datetime, UTC (required; copied from ShiftRequest.u_received_at)"
}
```

**Success response (HTTP 201)**:
```json
{
  "hitl_entry_id": "uuid-string",
  "shift_request_id": "uuid-string",
  "status": "PENDING",
  "created_at": "ISO 8601 datetime"
}
```

**Error responses**:
- HTTP 409: `shift_request_id` already in HITL queue → treat as success (idempotent); do not create duplicate
- HTTP 422: missing required fields → log; PATCH ShiftRequest to PARSE_FAILED (cannot even write to HITL queue)
- HTTP 5xx: server error → retry up to 3 times (4s, 8s, 16s); if all fail, PATCH ShiftRequest to PARSE_FAILED; alert ops

**Timeout**: 10 seconds

**Ordering**: This write happens after the `PARSING → HUMAN_REVIEW` status PATCH on ShiftRequest is confirmed. If the HITL queue write fails after retries, ShiftRequest stays in HUMAN_REVIEW status but has no corresponding queue entry — this is a dead state that ops must detect via reconciliation cron (HUMAN_REVIEW records with no matching HITLQueueEntry after >5 minutes).

---

## 8. Context Engineering Design

---

### 8.1 System Prompt Structure

The system prompt is the primary mechanism for encoding domain knowledge into the LLM extraction call. It is loaded at agent startup and injected as the `system` field in every Claude API call.

**System prompt components (in order)**:

```
[ROLE]
You are a healthcare staffing intake parser for MedFlex, a travel nursing agency.
Your task is to extract structured shift requirements from free-text hospital requests.
Output ONLY valid JSON. Do not include any explanation, commentary, or markdown.

[OUTPUT SCHEMA]
{
  "specialty_code": "string (from SpecialtyCode list below, or UNKNOWN if cannot determine)",
  "specialty_confidence": float (0.00–1.00),
  "datetime_start": "ISO 8601 datetime UTC string, or null if cannot determine",
  "datetime_start_confidence": float (0.00–1.00),
  "datetime_end": "ISO 8601 datetime UTC string, or null if cannot determine",
  "datetime_end_confidence": float (0.00–1.00),
  "location_id": "string (from HospitalLocation list below, or UNKNOWN if cannot determine)",
  "location_confidence": float (0.00–1.00),
  "credentials": ["array of CredentialCode strings from list below; empty array if none specified"],
  "credential_confidence": float (0.00–1.00)
}

[SPECIALTY CODE DICTIONARY]
(see §8.2)

[CREDENTIAL CODE DICTIONARY]
(see §8.2)

[HOSPITAL LOCATION LOOKUP]
(see §8.3)

[CONFIDENCE SCORING RULES]
(see §8.4)

[FEW-SHOT EXAMPLES]
(see §8.5)

[IMPORTANT RULES]
- If a field cannot be determined with any confidence, set the value to null and the confidence to 0.00
- Do not infer or guess dates. If the request says "Friday" but today's date is not provided, set datetime_start to null and confidence to 0.30
- Credentials array may be empty. "No special credentials required" → credentials: []
- If specialty is ambiguous between two codes, use the more specific one and set confidence to 0.60
- All datetimes must be UTC. Assume US Central Time (UTC-5) if no timezone specified
```

**System prompt token budget**: ~700 tokens. Updated only when specialty/credential dictionaries change or few-shot examples are tuned. System prompt changes require re-validation against the 200-record corpus (A10 check).

---

### 8.2 Domain Dictionaries

These dictionaries are embedded in the system prompt and define the valid output vocabulary. All values are from MedFlex's ServiceNow credential and specialty schema (A24).

**SpecialtyCode dictionary** (representative; full list loaded from config):

| Code | Common Names / Abbreviations |
|---|---|
| `ICU_RN` | ICU, Intensive Care, MICU, SICU, Critical Care |
| `ED_RN` | ED, ER, Emergency, Emergency Department |
| `TELE_RN` | Tele, Telemetry, Step-down, PCU |
| `MED_SURG_RN` | Med-Surg, M/S, Medical-Surgical |
| `OR_RN` | OR, Operating Room, Perioperative, Scrub |
| `PACU_RN` | PACU, Post-Anesthesia, Recovery Room |
| `L_D_RN` | L&D, Labor and Delivery, OB |
| `NICU_RN` | NICU, Neonatal ICU, Newborn Intensive |
| `PEDS_RN` | Peds, Pediatric, Pediatrics |
| `FLOAT_RN` | Float, Float Pool, Flex |
| `LPN` | LPN, Licensed Practical Nurse |
| `CNA` | CNA, Certified Nursing Assistant, Aide |

**CredentialCode dictionary** (representative; full list loaded from config):

| Code | Common Names |
|---|---|
| `BLS` | BLS, Basic Life Support, CPR |
| `ACLS` | ACLS, Advanced Cardiac Life Support |
| `PALS` | PALS, Pediatric Advanced Life Support |
| `NRP` | NRP, Neonatal Resuscitation Program |
| `TNCC` | TNCC, Trauma Nursing Core Course |
| `CEN` | CEN, Certified Emergency Nurse |
| `CCRN` | CCRN, Critical Care Registered Nurse certification |
| `NIHSS` | NIHSS, NIH Stroke Scale |
| `ONS` | ONS, Oncology Nursing Society chemo cert |
| `STABLE` | STABLE, post-resuscitation neonatal stabilization |

**Dictionary maintenance**: Both dictionaries are loaded from a config file at agent startup (not hardcoded in the system prompt string). Updating a dictionary requires an agent restart to take effect. Dictionary changes are not schema changes — they do not break the `ParsedShiftRequirement` schema lock.

---

### 8.3 Hospital Location Lookup

Maps hospital name variants (as they appear in free-text requests) to the canonical `location_id` values in ServiceNow. Loaded from config at agent startup.

**Example entries:**

| Hospital Name Variants | location_id |
|---|---|
| "St. David's North", "St Davids North Austin", "SDN" | `ST_DAVIDS_NORTH` |
| "St. David's South", "St Davids South Austin", "SDS" | `ST_DAVIDS_SOUTH` |
| "St. David's Medical Center", "SDMC", "St David's Main" | `ST_DAVIDS_MAIN` |
| "Ascension Seton Medical Center", "Seton Main", "ASMC" | `SETON_MAIN` |
| "Ascension Seton Northwest", "Seton NW", "ASNW" | `SETON_NW` |

**Ambiguity handling**: If the hospital name in the request matches multiple entries (e.g., "St. David's" matches both North and South), set `location_id = UNKNOWN` and `location_confidence = 0.30`. This triggers BP1 routing with `failure_reason = AMBIGUOUS_LOCATION`.

**Unknown hospital**: If the hospital name does not match any entry in the lookup, set `location_id = UNKNOWN` and `location_confidence = 0.00`. Routes to BP1 with `failure_reason = AMBIGUOUS_LOCATION`. Coordinator confirms correct location_id during review.

---

### 8.4 Confidence Scoring Rules

Per-field confidence scores are computed by the LLM per the rules embedded in the system prompt. The agent then computes the overall `confidence_score` as the minimum across all four field scores.

**Per-field scoring rules (embedded in system prompt)**:

**specialty_confidence:**
- 1.00: exact match to a SpecialtyCode or a listed abbreviation
- 0.80: common but unlisted abbreviation that clearly maps to one code (e.g., "SICU" → ICU_RN)
- 0.60: ambiguous between two codes
- 0.30: specialty mentioned but unclear category
- 0.00: no specialty mentioned

**datetime_start_confidence / datetime_end_confidence:**
- 1.00: explicit date + time (e.g., "Friday May 15, 7am–7pm")
- 0.80: explicit time with relative day resolvable from context (e.g., "this Friday 7a–7p")
- 0.60: explicit time, day ambiguous (e.g., "Friday" — which Friday?)
- 0.30: time implied but not stated (e.g., "morning shift")
- 0.00: no date/time information

**location_confidence:**
- 1.00: exact hospital name match or exact abbreviation match in lookup table
- 0.80: partial name match resolving to exactly one hospital
- 0.50: partial name match with ambiguity between two or more hospitals
- 0.00: hospital name not found in lookup table

**credential_confidence:**
- 1.00: all credentials listed are in the CredentialCode dictionary
- 0.70: some credentials listed but one or more not in dictionary
- 0.50: credentials mentioned but no specific codes determinable (e.g., "current certifications required")
- 1.00: no credentials mentioned → credentials = [] is correct and confident (not an error)

**Overall confidence computation (agent-side, after LLM response)**:
```
confidence_score = min(specialty_confidence, datetime_start_confidence, datetime_end_confidence, location_confidence, credential_confidence)
```
Note: `credential_confidence = 1.00` when credentials = [] (no credentials required is a valid, confident answer).

**Routing threshold**:
- `confidence_score ≥ 0.85` → BP2 auto-proceed (PARSED)
- `confidence_score < 0.85` → BP1 human review (HUMAN_REVIEW)

---

### 8.5 Few-Shot Examples

Three examples embedded in system prompt to calibrate LLM output format and confidence scoring.

**Example 1 — High confidence (auto-proceed path)**:
```
Input: "ICU float RN, BLS/ACLS req, St. David's North, 7a–7p Friday May 15"

Output:
{
  "specialty_code": "ICU_RN",
  "specialty_confidence": 1.00,
  "datetime_start": "2026-05-15T12:00:00Z",
  "datetime_start_confidence": 0.95,
  "datetime_end": "2026-05-16T00:00:00Z",
  "datetime_end_confidence": 0.95,
  "location_id": "ST_DAVIDS_NORTH",
  "location_confidence": 1.00,
  "credentials": ["BLS", "ACLS"],
  "credential_confidence": 1.00
}
```
Note: 7am–7pm Central = 12:00–00:00 UTC (UTC-5). `confidence_score = min(1.00, 0.95, 0.95, 1.00, 1.00) = 0.95`. Auto-proceeds.

**Example 2 — Low confidence (human review path)**:
```
Input: "Need a nurse for St. David's Saturday morning. Bring certs."

Output:
{
  "specialty_code": "UNKNOWN",
  "specialty_confidence": 0.00,
  "datetime_start": null,
  "datetime_start_confidence": 0.30,
  "datetime_end": null,
  "datetime_end_confidence": 0.00,
  "location_id": "UNKNOWN",
  "location_confidence": 0.50,
  "credentials": [],
  "credential_confidence": 0.50
}
```
Note: `confidence_score = min(0.00, 0.30, 0.00, 0.50, 0.50) = 0.00`. Routes to HUMAN_REVIEW.

**Example 3 — Ambiguous location**:
```
Input: "ED RN needed Friday 7am–3pm, BLS required, St. David's"

Output:
{
  "specialty_code": "ED_RN",
  "specialty_confidence": 1.00,
  "datetime_start": "2026-05-15T12:00:00Z",
  "datetime_start_confidence": 0.60,
  "datetime_end": "2026-05-15T20:00:00Z",
  "datetime_end_confidence": 0.60,
  "location_id": "UNKNOWN",
  "location_confidence": 0.30,
  "credentials": ["BLS"],
  "credential_confidence": 1.00
}
```
Note: "St. David's" without North/South → location_confidence = 0.30. `confidence_score = min(1.00, 0.60, 0.60, 0.30, 1.00) = 0.30`. Routes to HUMAN_REVIEW with `failure_reason = AMBIGUOUS_LOCATION`. Partial parse (specialty + BLS credential) pre-fills the HITL form.

---

## 9. Compounding Roadmap

### Wave 1 — LLM Parser MVP (Weeks 1–6)

**What ships:**
- LLM parser on 100% of inbound ServiceNow free-text requests
- BP1/BP2 confidence routing (threshold: 0.85)
- HITL queue for low-confidence cases
- `ParsedShiftRequirement` schema locked end of week 1
- Parse method tracking (`LLM_AUTO` vs `HUMAN_CORRECTED`) — seeds the improvement corpus for Wave 2
- 200-record validation corpus run in week 2 (A10 check)

**What is NOT shipped:**
- Priority scoring within QUEUED set (FIFO only)
- Structured intake template for hospitals (T2 deferred)
- Parser accuracy dashboard (ops monitors via HITL rate metric)

**Wave 1 success criteria**: HITL rate ≤ 15% on production traffic after 2 weeks live; parse latency ≤ 30 seconds.

---

### Wave 2 — Parser Improvement (Post-Week 6)

**Inputs from Wave 1**: `HITLQueueEntry` records with coordinator corrections accumulate as a labeled dataset. Each `HUMAN_CORRECTED` record is a labeled example: (raw_text, correct_parse). After 4–6 weeks of live traffic (~750–1,100 HITL cases at 15% rate × 184/day × 20 working days), the corpus supports prompt engineering improvements.

**What ships:**
- System prompt v2: retune few-shot examples using real HITL correction cases; add new specialty/credential abbreviations discovered in production
- Confidence threshold recalibration based on observed HITL rate vs. accuracy trade-off (may lower threshold if auto-parse accuracy at 0.85 is higher than target, or raise if edit rate is high)
- Priority queue for QUEUED records based on hospital tier or SLA flag (requires new `u_priority` field on `u_shift_request` — non-breaking schema addition)
- Parser accuracy dashboard (HITL rate by hospital, by source_type, by failure_reason)

**Structured intake template (T2, conditional)**: If parser accuracy for specific high-volume hospital partners plateaus below 90%, propose structured intake form as an optional channel for those partners. Requires commercial negotiation. Hospital-submitted structured records bypass the LLM parser entirely (confidence_score = 1.00; `parse_method = STRUCTURED_INTAKE`).

---

### Wave 3 — Intake Intelligence (Post-Wave 2)

- Hospital-specific system prompt variants (if volume per hospital is sufficient to justify per-partner tuning)
- Proactive hospital feedback loop: if HITL corrections for a specific hospital are consistently similar (same ambiguous abbreviation, same format issue), auto-generate a "common issues" report for the hospital relationship manager
- Multi-nurse request handling: Wave 1 processes only single-nurse requests; Wave 3 adds splitting logic for requests containing multiple nurse needs (e.g., "2 ICU RNs and 1 ED RN for Saturday") → generates multiple `ParsedShiftRequirement` records from a single `ShiftRequest`

---

### Integration Reuse Matrix (Parser as Provider)

| JtD / Feature | What it reuses from JtD-1 | Reuse type |
|---|---|---|
| JtD-2 (Candidate Search) | `ParsedShiftRequirement` schema as query input | Data contract (locked week 1) |
| JtD-3 (Match Selection ranker) | `specialty_code`, `credentials[]`, `location_id` from `ParsedShiftRequirement` | Data contract (locked week 1) |
| JtD-4 (Submission) | `shift_request_id` from `ParsedShiftRequirement` for audit trail linking | Identifier reference |
| JtD-6 (Emergency Re-fill) | BP6 re-entry creates a new QUEUED `ShiftRequest`; JtD-1 processes it identically | Full pipeline re-use |
| Wave 2 Prompt Tuning | `HITLQueueEntry` corrections corpus | Training data |
| Ops Dashboard | `u_status` state machine + `u_failure_reason` + HITL rate metric | Observability |

---

## 10. Validation Design

---

### 10.1 Happy Path

**Scenario**: Standard ICU RN shift request, all fields present and unambiguous.

**Input**:
```
ShiftRequest:
  u_raw_text: "ICU float RN, BLS/ACLS req, St. David's North Austin, 7a–7p Friday May 15"
  u_source_type: EMAIL
  u_hospital_id: "H001"
  u_status: QUEUED
```

**Step-by-step execution**:
1. MT-1.0: Agent polls; finds record in QUEUED; selects for processing (FIFO)
2. MT-1.1: PATCH `u_status = PARSING` → HTTP 200 confirmed; advisory lock acquired
3. MT-1.2: POST to Claude Sonnet API with system prompt + raw_text → HTTP 200; LLM returns valid JSON
4. MT-1.3: Schema validation passes; `ICU_RN` in SpecialtyCode dict; `BLS`, `ACLS` in CredentialCode dict; `ST_DAVIDS_NORTH` in HospitalLocation lookup
5. MT-1.4a: `confidence_score = min(1.00, 0.95, 0.95, 1.00, 1.00) = 0.95`
6. MT-1.4b: confidence ≥ 0.85 → BP2 auto-proceed
7. Write `ParsedShiftRequirement` to ServiceNow → HTTP 201
8. PATCH `u_status = PARSED`; set `u_parsed_at`
9. MT-1.7: Emit `shift_parsed` event → JtD-2 triggered

**Expected output**:
```json
{
  "u_specialty_code": "ICU_RN",
  "u_datetime_start": "2026-05-15T12:00:00Z",
  "u_datetime_end": "2026-05-16T00:00:00Z",
  "u_location_id": "ST_DAVIDS_NORTH",
  "u_credentials": ["BLS", "ACLS"],
  "u_confidence_score": 0.95,
  "u_parse_method": "LLM_AUTO",
  "u_parsed_by": "AGENT"
}
```

**Total elapsed time**: < 10 seconds (10s ServiceNow poll + 30s max LLM + 2× 10s writes; typical ~8 seconds).

---

### 10.2 Edge Cases

**Edge Case 1 — Unknown specialty abbreviation**

Input: `"SICU RN needed Friday 7am–7pm, St. David's North, ACLS req"`
SICU (Surgical ICU) is not in the SpecialtyCode dictionary.

Expected: LLM sets `specialty_code = ICU_RN` (closest match), `specialty_confidence = 0.80`. `confidence_score = min(0.80, 0.90, 0.90, 1.00, 1.00) = 0.80`. BP1 route: `failure_reason = LOW_CONFIDENCE`. Partial parse pre-fills HITL form with `ICU_RN` as the suggested value. Coordinator confirms or changes to the correct code.

**Action**: After Wave 1, add `SICU` → `ICU_RN` mapping to SpecialtyCode dictionary if confirmed by coordinator corrections.

---

**Edge Case 2 — No shift end time**

Input: `"ED RN needed Saturday 7am, BLS/ACLS, Seton Main"`
No end time specified.

Expected: LLM sets `datetime_end = null`, `datetime_end_confidence = 0.00`. `confidence_score = min(1.00, 0.90, 0.00, 1.00, 1.00) = 0.00`. BP1 route: `failure_reason = LOW_CONFIDENCE`. Coordinator enters end time in HITL review.

**Constraint**: Agent must NOT infer a default end time (e.g., assume 12-hour shift). Missing end time is a data gap, not a fill-in.

---

**Edge Case 3 — Multi-nurse request**

Input: `"Need 2 ICU RNs and 1 ED RN for Saturday 7am–7pm, St. David's North, BLS req all"`
MVP scope: single-nurse requests only.

Expected (MVP): LLM attempts to parse the first nurse requirement; sets overall `confidence_score` lower due to ambiguity in multi-nurse context. If confidence < 0.85, routes to BP1. Coordinator manually creates separate shift requests for each nurse. **Agent does NOT split the request in MVP.** `failure_reason = LOW_CONFIDENCE`. Note for coordinator HITL form: this is a multi-nurse request; separate submissions required.

**Wave 3 target**: Multi-nurse splitting logic generates multiple `ParsedShiftRequirement` records from one `ShiftRequest`.

---

**Edge Case 4 — Duplicate submission (same shift request submitted twice)**

Input: Hospital submits same shift request via email AND portal form; two QUEUED records exist with different `sys_id` values but identical `u_raw_text` and `u_hospital_id`.

Expected: Both records are processed independently (agent has no deduplication at the `ShiftRequest` level — the hospital created two records). Both produce `ParsedShiftRequirement` records. Both trigger JtD-2. JtD-2 or JtD-3 coordinator review catches the duplicate when the same shift appears twice in the review queue. **JtD-1 does not deduplicate.**

**Rationale**: Deduplication at the parse layer would require comparing raw text across records — an LLM call with broader context. This is out of scope for MVP. The coordinator review UI (BP4) is the deduplication gate.

---

**Edge Case 5 — Datetime in the past**

Input: `"ICU RN needed Monday May 4, 7am–7pm, St. David's North, BLS req"` (parsed on May 13; May 4 is in the past)

Expected: Agent validates `u_datetime_start` against current UTC timestamp after receiving LLM response. If `u_datetime_start < now()`: set `datetime_start_confidence = 0.00`; route to BP1 with `failure_reason = DATETIME_IN_PAST`. Agent does NOT reject or cancel — the hospital may have meant a future Monday and typed the wrong date. Coordinator resolves.

---

**Edge Case 6 — LLM returns valid JSON but specialty_code = "UNKNOWN"**

Input: `"Nurse needed ASAP at St. David's North. Urgent."`

Expected: LLM returns `specialty_code = "UNKNOWN"`, `specialty_confidence = 0.00`. Agent receives valid JSON; schema validation passes (UNKNOWN is a valid output for specialty_code per the system prompt instructions). `confidence_score = 0.00`. Routes to BP1 with `failure_reason = LOW_CONFIDENCE`. Partial parse shows location = ST_DAVIDS_NORTH (high confidence) which pre-fills the HITL form.

---

### 10.3 Failure Modes

**Failure Mode 1 — Claude Sonnet API unavailable**

Trigger: LLM returns HTTP 529 (overloaded) 3 times consecutively within 60 seconds.

Expected behavior:
1. Agent retries up to 3 times (4s, 8s, 16s backoff)
2. After 60 cumulative seconds without success: PATCH `ShiftRequest.u_status = HUMAN_REVIEW`; set `failure_reason = LLM_UNAVAILABLE`
3. Write `HITLQueueEntry` with `partial_parse = null` (no extraction attempted)
4. After 10 consecutive LLM failures across all records: ops alert fires
5. Affected `ShiftRequest` records accumulate in HUMAN_REVIEW status; coordinators process manually
6. When LLM recovers: new QUEUED records process normally; HUMAN_REVIEW records from the outage window remain with coordinators (not automatically re-queued)

**Recovery**: Ops manually re-queues `HUMAN_REVIEW` records with `failure_reason = LLM_UNAVAILABLE` after LLM recovery if volume warrants automated re-parse over coordinator correction.

---

**Failure Mode 2 — ServiceNow write unavailable**

Trigger: PATCH `u_shift_request.u_status = PARSING` returns HTTP 5xx after 3 retries.

Expected behavior:
1. If the `PARSING` lock write fails: agent skips this record for this poll cycle; does NOT call LLM; record stays QUEUED; agent picks it up on next poll (30 seconds)
2. If the `ParsedShiftRequirement` POST fails (after LLM already called): write to dead-letter queue; do NOT emit `shift_parsed` event; reconciliation cron retries the POST every 5 minutes; emits `shift_parsed` once POST confirmed
3. Reconciliation cron alert: if dead-letter queue has > 10 items, ops notification

**Impact**: Parse latency degrades during ServiceNow write outage. No data loss — QUEUED records stay in ServiceNow; dead-letter queue preserves LLM extraction results.

---

**Failure Mode 3 — Polling service restart / gap**

Trigger: Parser agent restarts; polling pauses for 0–5 minutes.

Expected behavior: QUEUED records remain in ServiceNow unchanged (agent did not consume them). On restart: agent polls; finds all records that arrived during the outage; processes them in FIFO order. No records lost.

**Ordering note**: If 50 records accumulated during a 5-minute outage, the parser processes them sequentially (one at a time per LLM call). At ~8 seconds per parse, clearing 50 records takes ~7 minutes. Fill-time impact for those requests: +7 minutes from normal latency. Not a data loss; a latency spike.

**Circuit breaker**: If error rate on ServiceNow reads exceeds 20% over any 5-minute window, pause polling and alert ops. Do not continue to generate dead-letter entries at high volume.
