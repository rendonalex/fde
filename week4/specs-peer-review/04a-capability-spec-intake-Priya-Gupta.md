# 04a — Capability Spec: Shift Request Intake
**MedFlex Healthcare Staffing | Gate 3 Submission**
**Author:** Priya Gupta

---

## Shared Glossary
*(applies to both 04a and 04b)*

| Term | Definition |
|---|---|
| `ShiftRequirement` | Structured record produced by the Intake Agent from a free-text inbound shift request. The canonical input to the Matching Agent. |
| `NurseProfile` | Record for a single nurse in the local data store, sourced from Kim's spreadsheet ingestion. Contains credentials, availability, location, placement history. |
| `CandidateScore` | Numeric score (0.0–1.0) assigned by the Matching Agent to a nurse for a specific `ShiftRequirement`. |
| `MatchConfidence` | Aggregate score (0.0–1.0) representing the Matching Agent's certainty that its top-ranked candidate is the right match. Gates autonomous vs. coordinator-review submission path. |
| `ParseConfidence` | Score (0.0–1.0) representing the Intake Agent's certainty that it correctly extracted all required fields from the inbound request. Gates auto-route vs. coordinator-correction path. |
| `CoordinatorOverrideRate` | % of parsed `ShiftRequirement` records where a coordinator corrects at least one field before the record passes to the Matching Agent. Primary week 1 KPI for parse quality. |
| `CoordinatorAgreementRate` | % of fills where the coordinator's final chosen candidate matches the Matching Agent's #1 ranked candidate. Primary week 2 KPI for match quality. |
| `credential_code` | Standardised credential identifier from the compliance team's database (e.g., `RN`, `ICU-CERT`, `PACU-EXP`). All credential comparisons use this code, not free-text descriptions. |
| `unit_type` | Taxonomy of hospital unit types: `ICU`, `PACU`, `ER`, `MedSurg`, `L&D`, `Peds`, `Float`. Exhaustive for MVP — requests with unrecognised unit types route to coordinator. |

---

## Capability: Shift Request Intake

### Purpose

Parse a free-text inbound shift request (email, phone transcript, or portal submission) into a structured `ShiftRequirement` record. Route high-confidence parses directly to the Matching Agent. Route low-confidence parses to the coordinator review queue with the draft record for correction.

---

## Input

| Field | Type | Source | Required |
|---|---|---|---|
| `raw_text` | string, max 10,000 chars | Email body / phone transcript / portal text field | Yes |
| `channel` | enum [`EMAIL`, `PHONE_TRANSCRIPT`, `PORTAL`] | ServiceNow metadata | Yes |
| `received_at` | ISO 8601 timestamp, UTC | ServiceNow queue event | Yes |
| `hospital_id` | string (internal MedFlex ID) or null | ServiceNow sender mapping — null if unrecognised sender | No |
| `servicenow_ticket_id` | string | ServiceNow | Yes |

---

## Output: ShiftRequirement entity

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | primary key, immutable, generated on creation | |
| `servicenow_ticket_id` | string | foreign key, required, immutable | |
| `hospital_id` | string or null | nullable — null if sender not in MedFlex system | |
| `hospital_name_raw` | string | extracted from text, max 200 chars, required | used for display only |
| `shift_date` | ISO 8601 date (YYYY-MM-DD) | required when `status = PENDING_MATCH`; may be null when `status = PENDING_COORDINATOR_REVIEW` | |
| `shift_time_start` | ISO 8601 time (HH:MM, 24hr) | required when `status = PENDING_MATCH`; may be null when `status = PENDING_COORDINATOR_REVIEW` | |
| `shift_time_end` | ISO 8601 time (HH:MM, 24hr) | required when `status = PENDING_MATCH`; may be null when `status = PENDING_COORDINATOR_REVIEW` | |
| `unit_type` | enum [`ICU`, `PACU`, `ER`, `MedSurg`, `L&D`, `Peds`, `Float`] | required when `status = PENDING_MATCH`; may be null when `status = PENDING_COORDINATOR_REVIEW` | if unrecognised → triggers low-confidence path |
| `location_address` | string, max 300 chars | required when `status = PENDING_MATCH`; may be null or partial when `status = PENDING_COORDINATOR_REVIEW` | |
| `required_credentials` | array of `credential_code` strings | must have min 1 item when `status = PENDING_MATCH`; may be empty array when `status = PENDING_COORDINATOR_REVIEW` | |
| `unrecognised_credentials_raw` | array of strings | optional, may be empty | credential descriptions that could not be mapped to any `credential_code`; preserved for coordinator review |
| `preferred_attributes` | array of strings | optional, may be empty | free-text preferences extracted verbatim |
| `parse_confidence` | float (0.0–1.0) | required | see scoring rules below |
| `parse_confidence_flags` | array of strings | required (may be empty) | reasons why confidence was reduced; also used for system-level flags: `LLM_UNAVAILABLE`, `LLM_OUTPUT_MALFORMED`, `EMPTY_INPUT` |
| `status` | enum [`PENDING_MATCH`, `PENDING_COORDINATOR_REVIEW`, `COORDINATOR_CORRECTED`, `CANCELLED`] | required, default `PENDING_MATCH` for high-confidence | |
| `created_at` | ISO 8601 timestamp, UTC | set on creation, immutable | |
| `updated_at` | ISO 8601 timestamp, UTC | updated on any field change | |

---

## Processing logic

### Step 1: Extract fields via LLM

Send `raw_text` to LLM with structured extraction prompt. Extract all `ShiftRequirement` fields. Required fields that cannot be extracted are set to `null` with a corresponding confidence flag.

**[ASSUMPTION confidence=MEDIUM]** LLM extraction is run as a single-pass structured output call (JSON mode). If the LLM returns malformed JSON, retry once. If still malformed, route to coordinator with `parse_confidence = 0.0` and flag `"LLM_OUTPUT_MALFORMED"`.

### Step 2: Normalise credential codes

Map extracted credential descriptions to `credential_code` values using a lookup table maintained by the compliance team.

- Exact match → use `credential_code` directly
- Fuzzy match (e.g., "ICU experience" → `ICU-CERT`) → apply mapping, add flag `"CREDENTIAL_FUZZY_MAPPED"`
- No match → store raw description in `unrecognised_credentials_raw`, add flag `"CREDENTIAL_UNRECOGNISED"`, reduce parse confidence; do not add to `required_credentials`

**[ASSUMPTION confidence=HIGH]** Credential code lookup table is a static CSV file updated by the compliance team monthly. The agent reads it at startup and caches it in memory for the session.

### Step 3: Normalise unit_type

Map extracted unit description to `unit_type` enum value using a lookup table.

- Recognised → map to enum value
- Unrecognised → set `unit_type = null`, add flag `"UNIT_TYPE_UNRECOGNISED"`, set `parse_confidence` to ≤ 0.5

### Step 4: Compute parse_confidence

Start at 1.0. Apply deductions:

| Condition | Deduction |
|---|---|
| Any required field is null | −0.25 per field |
| `CREDENTIAL_FUZZY_MAPPED` flag | −0.10 per occurrence |
| `CREDENTIAL_UNRECOGNISED` flag | −0.20 per occurrence |
| `UNIT_TYPE_UNRECOGNISED` flag | −0.30 |
| `required_credentials` is empty array | −0.25 (flag: `"REQUIRED_CREDENTIALS_MISSING"`) |
| `location_address` is partial or incomplete | −0.10 (flag: `"LOCATION_INCOMPLETE"`) |
| `shift_date` is today | −0.10 (flag: `"URGENT_DATE"`) |
| `shift_date` is already in the past | −0.25 (flag: `"SHIFT_DATE_PAST"`) — always routes to coordinator regardless of total score |
| `preferred_attributes` contains credential-like language not explicitly marked as preferred | −0.05 (flag: `"POSSIBLE_MISSED_CREDENTIAL"`) |

Minimum score: 0.0. Score is not rounded.

### Step 5: Deduplication check

Before creating the `ShiftRequirement` record, check whether a record with the same `servicenow_ticket_id` already exists in the data store.

- If a record already exists with that `servicenow_ticket_id`: discard the incoming event. Log: `"DUPLICATE_TICKET_SUPPRESSED: {servicenow_ticket_id}"`. Do not create a second record.
- If no existing record: proceed to create and route.

This prevents duplicate `ShiftRequirement` records when a webhook fires twice for the same ServiceNow ticket (e.g., on retry or network instability). The `servicenow_ticket_id` uniqueness constraint must be enforced at the data store level as well (unique index on `servicenow_ticket_id`).

### Step 6: Route

| parse_confidence | Action |
|---|---|
| ≥ 0.85 | Set `status = PENDING_MATCH`. Pass `ShiftRequirement` to Matching Agent. |
| < 0.85 | Set `status = PENDING_COORDINATOR_REVIEW`. Route to coordinator review queue with draft record. |

If `parse_confidence_flags` contains `"SHIFT_DATE_PAST"`, route to `PENDING_COORDINATOR_REVIEW` regardless of score.

**[ASSUMPTION confidence=MEDIUM]** The 0.85 threshold is an operational starting point, to be calibrated against coordinator override rate in week 1. If coordinator override rate on auto-routed records exceeds 20%, lower threshold to 0.90.

---

## Delegation boundaries

| Action | Who acts | ATX level |
|---|---|---|
| Extract fields from raw text | Agent | FA |
| Map credentials to standard codes | Agent | FA |
| Route high-confidence record to Matching Agent | Agent | FA — logged |
| Route low-confidence record to coordinator queue | Agent | FA — logged |
| Correct fields in low-confidence record | Coordinator | HO |
| Confirm corrected record passes to Matching Agent | Agent (on coordinator save) | FA |
| Cancel a `ShiftRequirement` | Coordinator only | HO |

Every route decision is logged with: `servicenow_ticket_id`, `parse_confidence`, `parse_confidence_flags`, `routing_decision` (`AUTO_MATCH` or `COORDINATOR_REVIEW`), `timestamp`.

---

## Integration contracts

### ServiceNow (inbound queue)

- **Trigger:** Webhook from ServiceNow on new ticket creation in the MedFlex inbound queue
- **[ASSUMPTION confidence=MEDIUM]** ServiceNow webhook is available and can be configured to POST to the agent's endpoint. If not, fallback: agent polls ServiceNow queue every 60 seconds via REST API.
- **Fallback endpoint (polling):** `GET /api/now/table/incident?sysparm_query=state=1&sysparm_limit=50`
- **Auth:** OAuth 2.0, credentials stored in environment variable `SERVICENOW_API_KEY`
- **Timeout:** 10 seconds
- **Retry:** HTTP 5xx → retry 3× with exponential backoff (2s, 4s, 8s). HTTP 4xx → log and alert coordinator; do not retry.

### LLM extraction

- **Call:** POST to LLM API with structured output schema
- **Model:** [ASSUMPTION confidence=HIGH] Claude claude-sonnet-4-6 or equivalent, JSON mode
- **Timeout:** 30 seconds
- **Retry:** HTTP 5xx or timeout → retry 3× with exponential backoff (2s, 4s, 8s). If HTTP 5xx/timeout retries are exhausted, route to coordinator with `parse_confidence = 0.0` and flag `"LLM_UNAVAILABLE"`. Malformed JSON output → retry once. If second attempt still malformed → route to coordinator with `parse_confidence = 0.0` and flag `"LLM_OUTPUT_MALFORMED"`.
- **Rate limit:** [ASSUMPTION confidence=LOW — to confirm] Assumed 60 requests/min. Queue inbound requests if burst exceeds this.

### Coordinator review queue (outbound)

- **Action:** Write `ShiftRequirement` record to coordinator queue data store with `status = PENDING_COORDINATOR_REVIEW`
- **Coordinator UI reads from this store** — UI spec is out of scope for this capability spec; the data contract is the `ShiftRequirement` entity above

---

## Worked examples

### Example 1 — High confidence, clean input

**Input:**
```
Hi MedFlex team, we need an RN for ICU coverage tomorrow (May 14) 7am-7pm at St. Mary's Hospital, 
123 Oak Street, Springfield. Must have current RN license and ICU certification. Preferred: 
recent PACU experience. Please confirm ASAP.
— Sandra, St. Mary's staffing
```

**Extracted output:**
```json
{
  "shift_date": "2026-05-14",
  "shift_time_start": "07:00",
  "shift_time_end": "19:00",
  "unit_type": "ICU",
  "location_address": "123 Oak Street, Springfield",
  "required_credentials": ["RN", "ICU-CERT"],
  "preferred_attributes": ["recent PACU experience"],
  "parse_confidence": 0.95,
  "parse_confidence_flags": [],
  "status": "PENDING_MATCH"
}
```

### Example 2 — Low confidence, missing credential detail

**Input:**
```
Need someone for tonight, ER shift, 8pm to 4am, General Hospital downtown. 
Usual requirements. Quick response needed.
```

**Extracted output:**
```json
{
  "shift_date": "2026-05-13",
  "shift_time_start": "20:00",
  "shift_time_end": "04:00",
  "unit_type": "ER",
  "location_address": "General Hospital downtown",
  "required_credentials": [],
  "preferred_attributes": [],
  "parse_confidence": 0.55,
  "parse_confidence_flags": ["REQUIRED_CREDENTIALS_MISSING", "URGENT_DATE", "LOCATION_INCOMPLETE"],
  "status": "PENDING_COORDINATOR_REVIEW"
}
```

*"Usual requirements" is not parseable to credential codes — `required_credentials` is empty, flagged as `REQUIRED_CREDENTIALS_MISSING`. "General Hospital downtown" is a partial address, not null, so flagged as `LOCATION_INCOMPLETE` rather than `REQUIRED_FIELD_NULL`. Both route to coordinator. Neither field is null — partial data is preserved to help the coordinator correct rather than re-enter.*

---

## Edge cases

| Scenario | Expected behaviour |
|---|---|
| Shift date in the past | Extract date, add flag `"SHIFT_DATE_PAST"`, deduct 0.25 from confidence, route to coordinator |
| Duplicate request (same `servicenow_ticket_id`) | Reject with log entry: `"DUPLICATE_TICKET_SUPPRESSED: {servicenow_ticket_id}"`. Do not create second `ShiftRequirement`. |
| `raw_text` is empty or whitespace only | Create `ShiftRequirement` with all fields null, `parse_confidence = 0.0`, flag `"EMPTY_INPUT"`, route to coordinator |
| Phone transcript includes multiple shift requests in one message | Extract first shift only. Add flag `"MULTIPLE_SHIFTS_DETECTED"`. Coordinator must create additional records manually. |
| `unit_type` extracted as "float" or "float pool" | Map to `Float` enum value. No confidence deduction. |
| Credential described as "ACLS" (not in standard taxonomy) | Store `"ACLS"` in `unrecognised_credentials_raw`. Add flag `"CREDENTIAL_UNRECOGNISED"`. Deduct 0.20. Route to coordinator if total confidence < 0.85. |

---

## Assumptions register

| ID | Assumption | Why it matters | If wrong | Status |
|---|---|---|---|---|
| A1 | ServiceNow webhook is configurable | Determines real-time vs. polling trigger | Fall back to 60-second polling; adds latency | [Flagged — confirm with Aaron] |
| A2 | Credential code lookup table is a static CSV, updated monthly | Agent caches it at startup | If updated mid-session, agent uses stale codes until restart | [Assumed — confirm with compliance team] |
| A3 | 0.85 parse_confidence threshold is the right gate | Too high → too much coordinator load. Too low → bad records reach matching | Calibrate against week 1 coordinator override rate | [Assumed — tunable] |
| A4 | LLM JSON mode output is reliable for structured extraction | Drives entire parse quality | Retry logic catches malformed output; coordinator catches semantic errors | [Known — LLM JSON mode is stable] |
| A5 | `unit_type` taxonomy (7 values) covers all MedFlex hospital requests | If a request uses an unrecognised unit, it routes to coordinator | Coordinator handles edge cases; taxonomy can be extended in future sprint | [Assumed — validate with Kim week 1] |
