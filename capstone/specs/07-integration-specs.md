# System and Data Inventory, Integration Contracts, and Entity Data Models
## Greenfield Health Systems AI Claims Processing Transformation

**Compiled from:** specs/06a-capability-spec-intake.md (ADR-1) and specs/06b-capability-spec-triage.md (ADR-4)  
**Date:** 2026-05-27  
**Purpose:** Consolidated view of systems, integrations, and data entities per capability specification

---

## Table of Contents

1. [ADR-1: Claim Intake and Format Validation Agent](#adr-1-claim-intake-and-format-validation-agent)
   - [System and Data Inventory](#system-and-data-inventory)
   - [Integration Contracts](#integration-contracts)
   - [Entity Data Models](#entity-data-models)
2. [ADR-4: Clinical Content Triage Agent](#adr-4-clinical-content-triage-agent)
   - [System and Data Inventory](#system-and-data-inventory-1)
   - [Integration Contracts](#integration-contracts-1)
   - [Entity Data Models](#entity-data-models-1)

---

## ADR-1: Claim Intake and Format Validation Agent

### System and Data Inventory

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

### Integration Contracts

> **Reading note:** CMS API details are assumed pending Week 1 IT discovery [A12]. Contracts below define the *minimum interface the agent requires* — treat unconfirmed fields as integration requirements to be validated, not implementation choices. All [TODO] markers in this section must be resolved before Sprint 1 development begins.

#### 8.1 CMS Read/Write API [A12]

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

#### 8.2 EDI 837 Parser

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

---

### Entity Data Models

#### 9.1 NormalizedClaimRecord

This entity is the canonical data contract shared across all agents. ADR-1 creates it; all downstream agents read it via CMS. ADR-4 writes routing fields (§9.1.2). No other agent may write intake fields after ADR-1 creates the record.

**Primary key:** `claim_id` — UUID, immutable, generated by CMS on record creation.

##### 9.1.1 Intake Fields (written by ADR-1; immutable after creation)

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

##### 9.1.2 Routing Fields (written by ADR-4; null until triage completes)

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

##### 9.1.3 Record State Machine

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

#### 9.2 ExceptionQueueEntry

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

#### 9.3 AuditLogEntry

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

## ADR-4: Clinical Content Triage Agent

### System and Data Inventory

| System | Data Needed | Access Type | Availability | Gap / Risk |
|--------|-------------|:-----------:|--------------|------------|
| CMS (Claims Management System) | Normalized claim record (post-coding); routing decision write; audit metadata | Read / Write | Assumed API available [A12] | Shared dependency with ADR-1; integration built in Wave 1 by ADR-1 — ADR-4 reuses |
| Clinical criteria codebook [A15] | Formal specification of clinical content triggers: procedure types, diagnosis categories, prior auth flags, documentation markers requiring physician review | Read (procedural) | **Does not exist — must be built with Dr. Webb** | **Wave 1 blocker #1:** criteria must be documented before shadow mode prompt can be written; Week 1 deliverable |
| Shadow evaluation log store | Agent routing decisions (shadow mode): claim ID, classification, confidence, clinical indicator citations, timestamp | Write (shadow) / Read (evaluation) | Must be built | New infrastructure; stores parallel-run comparison data for [A6] false-negative rate calculation |
| Ground truth adjudication queue [A25] | Agent-vs-processor disagreements submitted to Dr. Webb's team for definitive labeling | Read / Write | Must be built | Lightweight queue (e.g., structured review portal); Dr. Webb team capacity is a gating constraint |
| Audit log store | All live routing decisions: claim ID, path assigned, confidence score, clinical indicators cited | Write | Shared with ADR-1 (same infrastructure) | No gap — reuses ADR-1 audit log infrastructure |
| Exception / escalation queue | Novel criteria edge cases flagged for Dr. Webb adjudication and codebook update | Read / Write | Assumed existing ops queue | Routing to correct clinical reviewer requires ops process definition |

**Shared with ADR-1 (Claim Intake Agent):** CMS read API, normalized claim record schema, audit log store. ADR-4 is a consumer of ADR-1 output — the normalized claim record is the triage agent's primary input. Schema consistency between these two agents is mandatory and must be designed jointly in Wave 1.

**Shared with ADR-6 (Clinical Pre-Screening Agent):** Clinical criteria codebook [A15]. Both agents operate on the definition of "clinical content" — ADR-4 uses it to detect the presence of clinical content; ADR-6 uses it to identify which content to extract. A single authoritative codebook maintained by Dr. Webb's team serves both agents.

---

### Integration Contracts

> **Shared contracts:** The CMS Read/Write API (§8.1 in `specs/06a-capability-spec-intake.md`) is the primary integration for both ADR-1 and ADR-4. ADR-4 reuses the full CMS contract defined in 06a §8.1 without modification. This section documents only the ADR-4-specific CMS write (routing fields) and the three new integrations ADR-4 must build: the shadow evaluation log store, ground-truth adjudication queue, and clinical policy vector store.

#### 8.1 CMS API — ADR-4 Routing Write

ADR-4 uses the same CMS base URL, authentication, retry logic, and error handling as ADR-1 (see `specs/06a-capability-spec-intake.md` §8.1). The only difference is the write payload: ADR-4 issues a `PUT /v1/claims/{claim_id}` to write routing fields onto an existing record.

**PUT /v1/claims/{claim_id} — ADR-4 Routing Write Request:**
```json
{
  "routing_decision":              "FAST_PATH | CLINICAL_PATH",
  "routing_confidence":            "float 0.0–1.0",
  "routing_confidence_fallback":   "boolean",
  "clinical_indicators_detected":  ["array of indicator strings"],
  "criteria_provisions_matched":   ["array of codebook provision IDs — or ['NOVEL_CASE'] if no match"],
  "routing_reasoning_trace":       "string — chain-of-thought output",
  "routing_agent_version":         "semver string",
  "routing_decided_at":            "ISO 8601 UTC",
  "routing_mode":                  "SHADOW | LIVE"
}
```

**Shadow mode constraint:** When `routing_mode = SHADOW`, the PUT payload must include `routing_mode: SHADOW`. The CMS system must accept this write as a metadata annotation — it must not change the claim's processing queue or `status` field. If the CMS system cannot distinguish shadow writes from operative writes, the shadow log store (§8.2) must be used exclusively and the CMS PUT must be omitted in Wave 1. This behavior is determined by the Week 1 IT discovery [A12].

**Idempotency:** ADR-4 must not write a routing decision to a claim already in `FAST_PATH` or `CLINICAL_PATH` status. Before issuing a PUT, the agent must verify `routing_decision = PENDING_TRIAGE` on the current record. If status is already set, log a `ROUTING_ALREADY_DECIDED` event and skip the write.

**Responses:** Same error handling as 04a §8.1 CMS contract. Additional case:
```
HTTP 409 Conflict (routing already written):
  { "error": "ROUTING_CONFLICT", "existing_routing_decision": "FAST_PATH | CLINICAL_PATH", "decided_at": "ISO 8601 UTC" }
  → Agent action: do NOT overwrite. Log ROUTING_ALREADY_DECIDED event. Skip write.
```

---

#### 8.2 Shadow Evaluation Log Store

> **Build deliverable:** Must be built in Wave 1. This store is the data substrate for the [A6] false-negative gate measurement.

**Endpoint (internal service):**
```
POST {SHADOW_LOG_URL}/v1/shadow-log   — write shadow evaluation entry
GET  {SHADOW_LOG_URL}/v1/shadow-log?claim_id={}&date_from={}&date_to={}
                                      — query entries for gate measurement
```

**POST /v1/shadow-log — Request:**
```json
{
  "shadow_log_id":               "UUID — agent-generated; primary key",
  "claim_id":                    "UUID — NormalizedClaimRecord foreign key",
  "agent_routing_decision":      "FAST_PATH | CLINICAL_PATH",
  "agent_confidence":            "float 0.0–1.0",
  "agent_confidence_fallback":   "boolean",
  "clinical_indicators_detected":"array of strings",
  "criteria_provisions_matched": "array of strings",
  "reasoning_trace":             "string — full CoT output",
  "agent_version":               "semver",
  "logged_at":                   "ISO 8601 UTC"
}
```

**Response (HTTP 201):** `{ "shadow_log_id": "UUID" }`

**POST /v1/shadow-log — Processor decision update** (written after processor completes routing, for comparison):
```
PUT {SHADOW_LOG_URL}/v1/shadow-log/{shadow_log_id}/processor-decision
```
```json
{
  "processor_routing_decision": "FAST_PATH | CLINICAL_PATH",
  "processor_user_id":          "string",
  "processor_decided_at":       "ISO 8601 UTC",
  "agreement":                  "AGREE | DISAGREE — computed: agent_routing_decision == processor_routing_decision"
}
```

**Query response (GET):**
```json
{
  "total_entries":          "integer",
  "labeled_entries":        "integer — entries where processor_routing_decision is set",
  "disagreement_entries":   "integer — entries where agreement = DISAGREE",
  "false_negative_count":   "integer — disagreements where agent=FAST_PATH and processor=CLINICAL_PATH",
  "false_negative_rate":    "float 0.0–1.0 — false_negative_count / labeled_entries"
}
```

**[A6] gate query:** To measure gate readiness, query with `date_from = shadow_start_date` and verify: `labeled_entries ≥ 2000` AND `false_negative_rate < 0.02`.

**Timeout:** 5 seconds. Write failure handling: retry with backoff (1 s, 2 s, 4 s); if all fail, buffer locally; alert ops; do not block claim classification.

**Retention:** Shadow log entries retained for 24 months (training data archive). After gate passes, shadow log is the primary evidence artifact for [A6] gate validation sign-off.

---

#### 8.3 Ground-Truth Adjudication Queue [A25]

> **Build deliverable:** Must be built in Wave 1. This is a lightweight review portal for Dr. Webb's team to adjudicate agent-vs-processor disagreements.

**Endpoint:**
```
POST {ADJUDICATION_QUEUE_URL}/v1/adjudication-items    — submit disagreement for labeling
PUT  {ADJUDICATION_QUEUE_URL}/v1/adjudication-items/{id} — record Dr. Webb's label
GET  {ADJUDICATION_QUEUE_URL}/v1/adjudication-items?status=PENDING — list open items
```

**POST /v1/adjudication-items — Request:**
```json
{
  "adjudication_id":             "UUID — agent-generated",
  "claim_id":                    "UUID",
  "shadow_log_id":               "UUID — reference to shadow log entry",
  "agent_routing_decision":      "FAST_PATH | CLINICAL_PATH",
  "processor_routing_decision":  "FAST_PATH | CLINICAL_PATH",
  "clinical_indicators_detected":"array of strings",
  "reasoning_trace":             "string",
  "submitted_at":                "ISO 8601 UTC"
}
```

**PUT /v1/adjudication-items/{id} — Dr. Webb label:**
```json
{
  "ground_truth_routing":  "FAST_PATH | CLINICAL_PATH",
  "adjudicator_id":        "string — Dr. Webb team member user ID",
  "adjudication_notes":    "string, optional, max 1000 chars — rationale or codebook clarification",
  "adjudicated_at":        "ISO 8601 UTC",
  "trigger_codebook_update": "boolean — true if adjudication reveals a gap in [A15] criteria"
}
```

**SLA:** Adjudication items must be reviewed within 5 business days of submission. Items pending > 5 days are flagged to Dr. Webb's supervisor. If the adjudication queue backlog exceeds 50 open items, the shadow evaluation rate is considered at risk and ops is alerted [A25].

**Capacity constraint [A25]:** Dr. Webb's team capacity for adjudication is not confirmed. Assume 10 items/day maximum throughput until confirmed. If the agent-vs-processor disagreement rate generates > 10 items/day, the shadow evaluation schedule must be reviewed.

---

#### 8.4 Clinical Policy Vector Store

**Purpose:** Semantic retrieval of clinical policy provisions when a claim's indicators partially match the criteria codebook — provides additional context for boundary-case classifications.

**Embedding model:** [TODO: confirm with IT discovery. Recommend OpenAI `text-embedding-3-small` or equivalent; must be the same model used to embed the policy corpus.] Store in env var `EMBEDDING_MODEL_ID`.

**Endpoint (internal vector DB, e.g., Pinecone, Weaviate, or pgvector):**
```
POST {VECTOR_STORE_URL}/v1/query   — similarity search
```

**POST /v1/query — Request:**
```json
{
  "query_text":    "string — the clinical indicator or procedure description to match against policy",
  "top_k":         3,
  "min_similarity": 0.72,
  "namespace":     "clinical-policy-v{N}"
}
```

**POST /v1/query — Response:**
```json
{
  "results": [
    {
      "chunk_id":    "string",
      "text":        "string — policy provision text",
      "similarity":  "float 0.0–1.0",
      "source_doc":  "string — policy document name and section",
      "version":     "string — policy effective date"
    }
  ]
}
```

**Trigger condition:** ADR-4 only queries the policy vector store when a claim contains clinical indicators that partially match criteria codebook entries — estimated 15–25% of claims [A4]. For clear Fast Path or clear Clinical Path classifications (all indicators either clearly absent or clearly matched), the policy RAG step is skipped. Policy RAG is not active in the current build (demo). Classification is codebook-only.

**Timeout:** 3 seconds per query. On timeout or failure: proceed with criteria codebook match only; log `POLICY_RAG_UNAVAILABLE` event. The classification decision must still be made — policy RAG is a supporting retrieval, not the primary decision mechanism.

**Cost:** Each RAG query adds approximately $0.02–$0.04 per claim to API cost. Total remains within [A4] estimate when triggered for ≤ 25% of claims.

**Namespace versioning:** Policy corpus is versioned by effective date (e.g., `clinical-policy-v3`). ADR-4 reads the `POLICY_VECTOR_STORE_NAMESPACE` env var at startup. Updates to the policy corpus require a new namespace and a corresponding env var update — no in-place mutation of embeddings.

---

### Entity Data Models

> **Shared entity:** The `NormalizedClaimRecord` entity — including ADR-4's routing fields (§9.1.2) — is defined in full in `specs/06a-capability-spec-intake.md` §9.1. ADR-4 reads and writes that entity. This section defines only the entities that ADR-4 builds and owns.

#### 9.1 RoutingDecisionRecord (shadow log entry)

This is the ShadowEvalLogEntry defined in §8.2 above, formalized as an entity.

| Field | Type | Required | Constraints |
|---|---|:---:|---|
| `shadow_log_id` | UUID | Yes | Agent-generated; primary key; immutable |
| `claim_id` | UUID | Yes | Foreign key to NormalizedClaimRecord; immutable |
| `agent_routing_decision` | enum | Yes | `FAST_PATH \| CLINICAL_PATH`; immutable |
| `agent_confidence` | float | Yes | 0.0–1.0; immutable |
| `agent_confidence_fallback` | boolean | Yes | `true` if routed by fallback rule [A24]; immutable |
| `clinical_indicators_detected` | array\<string\> | Yes | List of indicator strings found in claim; immutable |
| `criteria_provisions_matched` | array\<string\> | Yes | Codebook provision IDs; `["NOVEL_CASE"]` if no match; immutable |
| `reasoning_trace` | string | Yes | Full CoT output text; immutable; max 5000 chars |
| `agent_version` | string | Yes | Semver; immutable |
| `logged_at` | timestamp | Yes | ISO 8601 UTC; immutable |
| `processor_routing_decision` | enum | No | `FAST_PATH \| CLINICAL_PATH`; written after processor routes claim |
| `processor_user_id` | string | No | Written when processor decision is recorded |
| `processor_decided_at` | timestamp | No | ISO 8601 UTC; written when processor decision is recorded |
| `agreement` | enum | No | `AGREE \| DISAGREE`; computed: agent == processor; written when processor decision recorded |
| `ground_truth_routing` | enum | No | `FAST_PATH \| CLINICAL_PATH`; written by Dr. Webb adjudication [A25] |
| `adjudication_id` | UUID | No | Foreign key to AdjudicationQueueEntry; present if disagreement was adjudicated |

**State machine:**
```
LOGGED              — agent classification written; awaiting processor decision
    ↓  (processor routes claim)
PROCESSOR_LABELED   — processor decision recorded; agreement field computed
    ↓  (if agreement = DISAGREE)
ADJUDICATION_PENDING — submitted to Dr. Webb adjudication queue [A25]
    ↓  (Dr. Webb labels)
GROUND_TRUTH_SET    — definitive label available for gate calculation
    ↓  (if agreement = AGREE; no adjudication needed)
GROUND_TRUTH_SET    — agreement counts as ground truth confirmation
```

**[A6] gate calculation:** Uses only entries in `GROUND_TRUTH_SET` state. False negative = `agent_routing_decision = FAST_PATH` AND `ground_truth_routing = CLINICAL_PATH`.

---

#### 9.2 CriteriaCodebookEntry [A15]

> **Build deliverable:** Does not exist. Must be co-developed with Dr. Webb in Week 1. This entity definition specifies the data model the codebook must follow.

| Field | Type | Required | Constraints |
|---|---|:---:|---|
| `provision_id` | string | Yes | Primary key; format `CC-{NNN}` (e.g., `CC-001`); immutable once published |
| `provision_name` | string | Yes | Max 100 chars; human-readable name |
| `clinical_category` | enum | Yes | `DIAGNOSTIC_IMAGING \| SPECIALIST_AUTHORIZATION \| MEDICAL_NECESSITY \| PROCEDURE_COMPLEXITY \| PRIOR_AUTH_REQUIRED \| OTHER_CLINICAL` |
| `trigger_icd10_patterns` | array\<string\> | No | ICD-10 code prefixes or exact codes that trigger this provision (e.g., `["Z51.1", "C18"]`); empty array if not ICD-10-triggered |
| `trigger_cpt_patterns` | array\<string\> | No | CPT code prefixes or exact codes that trigger this provision; empty array if not CPT-triggered |
| `trigger_prior_auth_required` | boolean | No | `true` if prior_auth_required = true alone is sufficient to trigger this provision |
| `trigger_free_text_keywords` | array\<string\> | No | Keywords in unstructured claim notes that suggest this provision (used for partial-match RAG trigger) |
| `routing_outcome` | enum | Yes | `CLINICAL_PATH` — every provision in this codebook routes to Clinical Path. Fast Path is the default; provisions only override toward Clinical Path. |
| `description` | string | Yes | Max 500 chars; clinical rationale for why this provision requires physician review |
| `effective_date` | date | Yes | ISO 8601 `YYYY-MM-DD`; date provision took effect |
| `retired_date` | date | No | ISO 8601 `YYYY-MM-DD`; null if still active |
| `approved_by` | string | Yes | Dr. Webb's user ID; must be present before provision is deployed |
| `approved_at` | timestamp | Yes | ISO 8601 UTC; immutable once set |
| `codebook_version` | string | Yes | Semver of the codebook release this provision belongs to |

**Deployment rule:** A codebook entry must not be loaded into the ADR-4 system prompt until `approved_by` is populated by Dr. Webb and `effective_date` ≤ today. Entries with `retired_date` ≤ today must not appear in the active system prompt.

**Minimum viable codebook:** At least 1 provision per `clinical_category` must exist before shadow mode can begin. Dr. Webb's Week 1 deliverable is a codebook with at minimum 20 provisions covering the most common clinical content types in Greenfield's claim mix.

---

#### 9.3 AdjudicationQueueEntry [A25]

| Field | Type | Required | Constraints |
|---|---|:---:|---|
| `adjudication_id` | UUID | Yes | Agent-generated; primary key; immutable |
| `claim_id` | UUID | Yes | Foreign key to NormalizedClaimRecord; immutable |
| `shadow_log_id` | UUID | Yes | Foreign key to RoutingDecisionRecord; immutable |
| `agent_routing_decision` | enum | Yes | `FAST_PATH \| CLINICAL_PATH`; immutable |
| `processor_routing_decision` | enum | Yes | `FAST_PATH \| CLINICAL_PATH`; immutable |
| `clinical_indicators_detected` | array\<string\> | Yes | Copied from shadow log; immutable |
| `reasoning_trace` | string | Yes | Copied from shadow log; immutable |
| `submitted_at` | timestamp | Yes | ISO 8601 UTC; immutable |
| `status` | enum | Yes | `PENDING \| IN_REVIEW \| RESOLVED`; default `PENDING` |
| `ground_truth_routing` | enum | Conditional | Required when `status = RESOLVED`; `FAST_PATH \| CLINICAL_PATH` |
| `adjudicator_id` | string | Conditional | Required when `status = RESOLVED`; Dr. Webb team member user ID |
| `adjudication_notes` | string | No | Max 1000 chars; rationale or codebook gap identification |
| `trigger_codebook_update` | boolean | Conditional | Required when `status = RESOLVED`; `true` if this case reveals a codebook gap |
| `adjudicated_at` | timestamp | Conditional | ISO 8601 UTC; required when `status = RESOLVED` |
| `sla_deadline` | timestamp | Yes | `submitted_at + 5 business days`; auto-escalated at deadline |

---

*See `specs/assumptions.md` for full definitions of all [A#] assumption references.*  
*See `specs/06a-capability-spec-intake.md` and `specs/06b-capability-spec-triage.md` for complete capability specifications including context engineering, validation scenarios, and governance requirements.*
