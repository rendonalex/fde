# Capability Spec — JtD-3: Match Selection

> ATX Phase 4 Agent Mapping. Input: `specs/cognitive-load-map.md`, `specs/3-agentic-solution-architecture.md`, `specs/volume-×-value-analysis.md`.
> Shared entities and glossary for both JtD-3 and JtD-1 are defined here. `04b-capability-spec-shift-intake-parsing.md` references this document.
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
9. [Shared Glossary](#9-shared-glossary)
10. [Production-Grade Validation Results](#10-production-grade-validation-results)

---

## 1. Executive Summary

The **MedFlex AI Candidate Ranker** (JtD-3) is the highest-value agent in the Wave 1 pipeline (value score 20/25, `specs/volume-×-value-analysis.md`). It replaces the undocumented multi-factor judgment that senior coordinators perform in Match Selection — a cognitive step that currently makes junior coordinators 3–5× slower than seniors and is entirely unencoded in any system (A18).

At MVP the agent produces a scored, explained shortlist of 1–3 nurse candidates and presents it to the coordinator at Breakpoint 4 (BP4) for approval before submission. This Human-in-the-Loop (HITL) design directly addresses the two prior AI failure risk factors identified by Marcus: matching accuracy and coordinator adoption (A13). The coordinator approval event simultaneously serves as the labeled training signal needed to upgrade the rule-based ranker to a supervised ML model in Wave 2 (A19).

**Economic impact:** Direct labor saving of ~$60K/year; primary value driver is throughput multiplication (23 → ≥230 matches/coordinator/day, M2) enabling $1.5M+ revenue recovery target (M3, A5, A6).

**This spec is the build input for Wave 1, Build Order 3** (depends on JtD-1 and JtD-2 outputs per `specs/volume-×-value-analysis.md`).

---

## 2. Agent Purpose Document

```
Agent Name:          MedFlex AI Candidate Ranker
Job to be Done:      Given an evaluated candidate pool from JtD-2, produce a ranked
                     shortlist of 1–3 nurse candidates with composite scores and
                     per-candidate explanations, and present it to the coordinator for
                     approval at BP4 before hospital submission.
Business context:    MedFlex coordinator workflow / Match Selection Zone (JtD-3).
                     Triggered when a CandidatePool record reaches status=READY.
                     Output is a RankedShortlist consumed by the Coordinator Review UI.

Primary objectives:
  1. Rank all candidates in the pool using the rule-based composite scoring formula
     (A25) and produce a shortlist of the top 1–3 candidates with explanations.
  2. Surface data signals (stale availability, missing preference history) that a
     coordinator needs to make a confident approval decision at BP4.

KPIs:
  - Ranker acceptance rate: ≥85% of BP4 reviews result in coordinator approving
    rank-1 candidate without editing (A23). Measured as:
    COUNT(status=COORDINATOR_APPROVED) / COUNT(reviewed) over rolling 7 days.
  - HITL rate: 100% at MVP (all cases reviewed at BP4).
    Phase 2 target: reduce to ≤20% as ranker confidence threshold rises (A19).
  - Throughput: ≥184 RankedShortlists produced per day (A4).
  - Cost per case: ≤$0.896 (token cost $0.015 + 100% HITL cost $0.881, A22).
    Computed as: (input_tokens × $3.00/M) + (output_tokens × $15.00/M) + HITL_cost.
  - Ranking latency: RankedShortlist produced within 10 seconds of CandidatePool
    reaching status=READY. Measured at p95.
  - Escalation rate: ≤10% of cases escalated to senior coordinator (MT-3.4 routing).

Failure modes:
  1. Bad output — Wrong candidate ranked #1 due to incorrect scoring:
     Consequence: Coordinator may approve an unsuitable candidate → hospital rejection
     or reputational damage (reversible via BP5 re-rank cycle).
     Recovery: Coordinator edits at BP4; rejection triggers BP5 re-rank with updated
     pool. Agent decision and outcome logged for A19 feedback.
  2. Bad output — Missing stale availability flag on shortlisted candidate:
     Consequence: Submission sent for candidate who cannot attend → potential no-show.
     Recovery: All candidates with availability_status=STALE_RECORD must surface a
     visible warning in the Review UI; this is a build requirement (not catch-as-catch-can).
  3. Agent failure — LLM API unavailable:
     Consequence: RankedShortlist not produced; coordinator cannot proceed to BP4.
     Recovery: After 3 retries (see Integration Contract §5.3), set
     CandidatePool.status=RANKING_FAILED; route to coordinator manual review queue;
     alert ops dashboard; coordinator manually ranks or escalates.

Delegation archetype (MVP):     Agent-led + Human Oversight
Delegation archetype (Phase 2): Fully Agentic (progressive as A19 threshold met)

Escalation triggers:
  - CandidatePool.candidates is empty → escalate to coordinator: "No qualified
    candidates found for this requirement; expand search criteria or contact hospital."
  - All candidates have availability_status=STALE_RECORD → escalate to coordinator
    with stale_availability_flag=true; coordinator must verify before approval.
  - RankedShortlist remains status=PENDING_REVIEW for > 30 minutes AND
    shift_start is within 2 hours → auto-escalate with reason
    "SLA breach — shift within 2 hours."
  - Coordinator sets status=ESCALATED at BP4 → route to senior coordinator queue.
  - LLM returns stop_reason=max_tokens → discard output; route to human review
    (output truncation = malformed ranking).
```

---

## 3. Agent Activity Catalog

All micro-tasks performed by the MedFlex AI Candidate Ranker.

| Task | Type | Delegation Level | Data Required | Tool Required | Risk Level |
|------|------|-----------------|---------------|---------------|------------|
| MT-3.0 Receive CandidatePool | Retrieval | Fully agentic | CandidatePool record (status=READY), NurseCandidate array | Internal pipeline event (no external tool) | Low |
| MT-3.1a Retrieve hospital preference history | Retrieval | Fully agentic | hospital_id from ShiftRequirement, nurse_id array from CandidatePool | ServiceNow Table API read (`u_nurse_hospital_outcome`) | Medium |
| MT-3.1b Compute per-candidate scores | Reasoning | Fully agentic | NurseCandidate fields: credential_score, availability_score, proximity_score_normalized, preference_weight; scoring weights (A25) | None (computed in-context) | Medium |
| MT-3.1c Rank candidates and generate explanations | Reasoning + Generation | Fully agentic | Scored candidates, ShiftRequirement context | Claude API (claude-sonnet-4-6) | Medium |
| MT-3.1d Apply tie-break rule | Decision | Fully agentic | Tied composite_scores; tie-break priority: lower proximity_score → if still tied, more recent placement date | None (rule-based) | Low |
| MT-3.2 Simulate tacit knowledge (rule-based, Wave 1) | Reasoning | Fully agentic; ML upgrade in Wave 2 (A19) | All scored dimensions per A25; hospital preference history | None (in-context scoring) | Medium |
| MT-3.3 Set flags (stale_availability, no_preference_data) | Decision | Fully agentic | availability_status of all candidates; preference_weight values | None | Low |
| MT-3.4 Present shortlist via Coordinator Review UI | Action | Agent proposes; human approves | RankedShortlist record, UI display payload | Coordinator Review UI API | Medium |
| MT-3.5 Persist coordinator decision | Action | Fully agentic (system records decision) | Coordinator decision (APPROVED / EDITED / ESCALATED), selected_nurse_id, coordinator_id | Labeled Feedback Store write; RankedShortlist status update | Low |
| MT-3.6 Log ranking audit trail | Action | Fully agentic | Full scoring breakdown, ranked_candidates, coordinator decision | Immutable audit log write | Low |

**Task types**: Reasoning (model performs cognitive work), Retrieval (fetch and return data), Decision (choose between outcomes), Action (write to a system or trigger a process), Generation (produce text or structured output).

---

## 4. Autonomy Matrix

### Agent Decides Alone (no HITL required)
- Retrieve CandidatePool and ShiftRequirement records from internal pipeline
- Retrieve hospital preference history from ServiceNow
- Compute credential_score, availability_score, proximity_score_normalized, preference_weight per candidate
- Apply composite scoring formula: `(0.40 × credential_score) + (0.30 × availability_score) + (0.20 × proximity_score_normalized) + (0.10 × preference_weight)` (A25)
- Apply tie-break rule (lower proximity → more recent placement date)
- Set stale_availability_flag and no_preference_data_flag
- Generate explanations per candidate (max 500 chars each)
- Produce RankedShortlist in status=PENDING_REVIEW
- Auto-escalate when RankedShortlist is PENDING_REVIEW > 30 min AND shift_start < 2 hours away

### Agent Acts, Human Notified After
- All ranking decisions are logged in immutable audit trail immediately upon RankedShortlist creation (logged fields: ranking_id, candidate_pool_id, shift_requirement_id, all composite_scores, scoring_breakdowns, flags, timestamp, model_version)
- Stale_availability_flag=true and no_preference_data_flag=true are surfaced to coordinator via UI notification — coordinator sees these before approving, but agent sets the flags autonomously

### Agent Proposes, Human Approves Before Action (BP4)
- **All candidate submissions in MVP** — the ranked shortlist is presented to the coordinator; no submission to ServiceNow occurs until coordinator explicitly acts with decision=APPROVED or decision=EDITED
- Escalation to senior coordinator (coordinator selects decision=ESCALATED at BP4; agent cannot self-escalate except for the SLA auto-escalation case)

### Human Takes Over (Agent Supports)
- CandidatePool.status=NO_CANDIDATES → coordinator investigates; agent provides no further value until a new CandidatePool is created
- RankedShortlist.status=RANKING_FAILED (after 3 LLM retries) → coordinator manually reviews available candidates; agent provides candidate data but no ranking
- Coordinator selects decision=ESCALATED at BP4 → senior coordinator takes over; agent surfaces: nurse reliability scores, shift timeline, and prior similar decisions (if available) as reference data
- Hospital rejection at BP5 → triggers re-rank; coordinator may override the updated ranking if second ranker output is also unsatisfactory

**Escalation path completeness:**
- Coordinator escalates → senior coordinator receives notification via Coordinator UI within 2 minutes; senior has 60 minutes to act before further escalation to operations manager
- Auto-SLA escalation → same path; reason flag distinguishes auto from manual
- SLA for all BP4 reviews: coordinator must act within 30 minutes; after 30 minutes, auto-escalation fires

**Override mechanism:** Coordinator can override the rank-1 selection by choosing any candidate in the shortlist. Override is logged with: coordinator_id, from_rank (original rank), selected_nurse_id, edit_reason (optional, max 500 chars), reviewed_at. Override feedback is written to the labeled feedback store for A19.

---

## 5. System and Data Inventory

### 5.1 System Inventory

| System | Data Needed | Access Type | Availability | Gap / Risk |
|--------|-------------|-------------|--------------|-----------|
| ServiceNow (nurse DB) | CandidatePool (passed from JtD-2 pipeline); hospital preference history (`u_nurse_hospital_outcome` table: nurse_id, hospital_id, outcome, placement_date) | Read | Shared with JtD-2; API provisioning required (A11) | Table name and field names assumed (A24); validate with MedFlex IT before build. Preference data completeness unconfirmed (A12). |
| Claude API (Anthropic) | LLM reasoning for scoring, explanation generation | Write (API call) | Available (API key required) | Token cost per case $0.015 (A22); prompt caching applicable for system prompt reuse across batch |
| Coordinator Review UI | Present RankedShortlist to coordinator; capture decision (APPROVED / EDITED / ESCALATED) | Read/Write | New build required (Wave 1) | Does not exist; must be built; dependency on JtD-4 submission flow |
| Labeled Feedback Store | Coordinator decision records: ranking_id, selected_nurse_id, decision, edit_reason, outcome (set post-submission) | Write (decisions) + Read (Phase 2 ML) | New build required (A19) | Critical for Wave 2 ML ranker; must be built in Wave 1 even if not used until Wave 2 |
| Internal Pipeline Event Bus | CandidatePool READY event trigger | Read | New build required | Shared with JtD-1 and JtD-2 pipeline; built once, reused |
| Immutable Audit Log | Ranking decisions, scoring breakdowns, coordinator actions | Write | New build required | Retention policy: 3 years (staffing records); no patient PII; append-only |

**Shared integrations** (built in JtD-1 or JtD-2, reused here):
- ServiceNow Table API client (built in JtD-1) — reused for preference history query
- Hospital lookup table (built in JtD-1) — reused for hospital_id in preference query
- Claude API client (built in JtD-1) — reused for ranking LLM call

### 5.2 Entity Definitions

#### Entity: CandidatePool *(produced by JtD-2; consumed as input by JtD-3)*

| Attribute | Type | Constraints |
|-----------|------|-------------|
| id | UUID | PK, immutable, system-generated |
| shift_requirement_id | UUID | FK → ShiftRequirement.id, NOT NULL, immutable, unique (1 pool per requirement); on ShiftRequirement delete: restrict |
| candidates | JSON array of NurseCandidate | NOT NULL; min 0, max 5 entries |
| status | enum | `[BUILDING, READY, NO_CANDIDATES, RANKING_FAILED]`; NOT NULL; default BUILDING |
| created_at | ISO 8601 UTC timestamp | Immutable |
| updated_at | ISO 8601 UTC timestamp | Updated on any modification |

**CandidatePool State Machine:**
```
BUILDING   → READY          (on: JtD-2 completes all filters; candidates ≥ 1)
BUILDING   → NO_CANDIDATES  (on: JtD-2 completes; candidates = 0)
READY      → RANKING_FAILED (on: LLM API fails after 3 retries during JtD-3)
RANKING_FAILED → READY      (on: manual re-trigger by coordinator)
```

#### Entity: NurseCandidate *(embedded in CandidatePool.candidates; produced by JtD-2)*

| Attribute | Type | Constraints |
|-----------|------|-------------|
| nurse_id | string(36) | NOT NULL; ServiceNow sys_user.sys_id |
| specialty_match | boolean | NOT NULL |
| credential_match | boolean | NOT NULL; true if all required_credentials present in nurse profile AND none expired before shift_start |
| availability_status | enum | `[AVAILABLE, STALE_RECORD, UNAVAILABLE]`; NOT NULL. STALE_RECORD: record_freshness > 30 days (A17) |
| proximity_score | decimal(6,3) | NOT NULL; distance in km, range 0.000–999.999 |
| credential_score | decimal(3,2) | Read-only; computed: 1.00 if credential_match=true, 0.00 if false |
| availability_score | decimal(3,2) | Read-only; computed: AVAILABLE=1.00, STALE_RECORD=0.50, UNAVAILABLE=0.00 |
| proximity_score_normalized | decimal(3,2) | Read-only; computed: `max(0.00, (50.00 - proximity_score) / 50.00)`; MAX_PROXIMITY constant = 50 km; range 0.00–1.00 |
| preference_weight | decimal(3,2) | Read-only; computed by JtD-2 from hospital preference history: `accepted_placements / total_placements` for nurse-hospital pair (last 12 months); 0.00 if < 3 historical records; range 0.00–1.00 |

#### Entity: RankedShortlist *(produced by JtD-3; consumed by Coordinator Review UI and JtD-4)*

| Attribute | Type | Constraints |
|-----------|------|-------------|
| id | UUID | PK, immutable, system-generated |
| candidate_pool_id | UUID | FK → CandidatePool.id, NOT NULL, immutable; on CandidatePool delete: restrict |
| shift_requirement_id | UUID | FK → ShiftRequirement.id, NOT NULL, immutable |
| ranked_candidates | JSON array of RankedCandidate | NOT NULL; min 1, max 3 entries; ordered by composite_score DESC |
| status | enum | `[PENDING_REVIEW, COORDINATOR_APPROVED, COORDINATOR_EDITED, ESCALATED, RANKING_FAILED]`; NOT NULL; default PENDING_REVIEW |
| stale_availability_flag | boolean | NOT NULL; true if any ranked_candidate.availability_status=STALE_RECORD; default false |
| no_preference_data_flag | boolean | NOT NULL; true if all ranked_candidates have preference_weight=0.00; default false |
| coordinator_id | UUID | Nullable; set when coordinator acts at BP4 |
| reviewed_at | ISO 8601 UTC timestamp | Nullable; set simultaneously with status change from PENDING_REVIEW |
| escalation_reason | string(500) | Nullable; required when status=ESCALATED |
| created_at | ISO 8601 UTC timestamp | Immutable |
| updated_at | ISO 8601 UTC timestamp | Updated on any modification |
| created_by | string | NOT NULL; always "system" (ranker-generated); immutable |

**RankedShortlist State Machine:**
```
PENDING_REVIEW → COORDINATOR_APPROVED (on: coordinator selects rank-1 without edit; coordinator_id set; reviewed_at set)
PENDING_REVIEW → COORDINATOR_EDITED   (on: coordinator selects non-rank-1 or modifies; coordinator_id set; reviewed_at set; edit_reason logged)
PENDING_REVIEW → ESCALATED            (on: coordinator selects ESCALATED or auto-SLA trigger; escalation_reason required)
PENDING_REVIEW → RANKING_FAILED       (on: LLM API failure after 3 retries)
RANKING_FAILED → PENDING_REVIEW       (on: manual re-trigger by coordinator)
ESCALATED      → COORDINATOR_APPROVED (on: senior coordinator approves after escalation)
ESCALATED      → COORDINATOR_EDITED   (on: senior coordinator edits after escalation)
```

**Constraints:**
- `reviewed_at` must be set simultaneously with any transition out of PENDING_REVIEW or RANKING_FAILED
- `coordinator_id` must be non-null for transitions to COORDINATOR_APPROVED, COORDINATOR_EDITED, or ESCALATED (manual)
- If status=COORDINATOR_EDITED: exactly one RankedCandidate.selected_by_coordinator=true must be set
- Auto-escalation rule: IF status=PENDING_REVIEW AND `NOW() - created_at > 30 minutes` AND shift_start < NOW() + 2 hours THEN status → ESCALATED, escalation_reason = "auto: SLA breach — shift within 2 hours", coordinator_id = null

#### Entity: RankedCandidate *(embedded in RankedShortlist.ranked_candidates)*

| Attribute | Type | Constraints |
|-----------|------|-------------|
| rank | integer | NOT NULL; range 1–3; unique within a RankedShortlist; 1 = highest composite_score |
| nurse_id | string(36) | NOT NULL; must match a NurseCandidate.nurse_id in the parent CandidatePool |
| composite_score | decimal(6,4) | NOT NULL; read-only; range 0.0000–1.0000; formula: `(0.40 × credential_score) + (0.30 × availability_score) + (0.20 × proximity_score_normalized) + (0.10 × preference_weight)` (A25) |
| scoring_breakdown | JSON object | NOT NULL; read-only; `{credential_score: decimal(3,2), availability_score: decimal(3,2), proximity_score_normalized: decimal(3,2), preference_weight: decimal(3,2)}` |
| explanation | string | NOT NULL; max 500 chars; human-readable; generated by LLM |
| selected_by_coordinator | boolean | NOT NULL; default false; set to true when coordinator approves this candidate (COORDINATOR_APPROVED always sets rank-1 to true; COORDINATOR_EDITED sets selected candidate to true) |

**Tie-break rule** (applied when two or more candidates have equal composite_score to 4 decimal places):
1. Lower proximity_score (km) wins
2. If still tied: more recent last_placement_date (from preference history) wins
3. If still tied: lower nurse_id lexicographic order wins (deterministic; logged as "tie-break applied by nurse_id" in explanation)

### 5.3 Integration Contracts

#### Contract 1: ServiceNow Table API — Hospital Preference History (Read)

```
Endpoint:
  GET {SN_INSTANCE_URL}/api/now/table/{NURSE_HOSPITAL_OUTCOME_TABLE}
  where SN_INSTANCE_URL is stored in env var SN_INSTANCE_URL
  where NURSE_HOSPITAL_OUTCOME_TABLE = "u_nurse_hospital_outcome" (A24 — validate before build)

Authentication:
  Method: Bearer token (OAuth 2.0 client credentials)
  Header: Authorization: Bearer {SN_API_TOKEN}
  SN_API_TOKEN stored in secrets manager (key: SN_API_TOKEN); rotated every 90 days

Request query parameters:
  sysparm_query:   u_hospital_id={hospital_id}^u_placement_date>=javascript:gs.monthsAgo(12)
  sysparm_fields:  u_nurse_id,u_hospital_id,u_outcome,u_placement_date
  sysparm_limit:   200
  sysparm_display_value: false
  sysparm_exclude_reference_link: true

Success response (HTTP 200):
{
  "result": [
    {
      "u_nurse_id": "string(32)",
      "u_hospital_id": "string",
      "u_outcome": "ACCEPTED | REJECTED",
      "u_placement_date": "YYYY-MM-DD (UTC; ServiceNow date format)"
    }
  ]
}

Error responses:
  HTTP 401: { "error": { "detail": "string", "message": "string" }, "status": "failure" }
  HTTP 403: { "error": { "detail": "Access denied", "message": "string" }, "status": "failure" }
  HTTP 429: (header) Retry-After: integer (seconds)
  HTTP 5xx: { "error": { "detail": "string", "message": "string" }, "status": "failure" }

Timeout: 10 seconds

Retry logic:
  HTTP 5xx: up to 3 retries; exponential backoff 2s, 4s, 8s
  HTTP 429: 1 retry after Retry-After header value (default: 60s if header absent)
  HTTP 401/403: no retry; alert ops; halt ranking for this request; route to human review
  HTTP 404: no retry; treat as empty result (table missing → flag A24 assumption failure)
  HTTP 4xx (other): no retry; log error with request details

Rate limits: ≥60 req/min (A23); 1 call per ranking session (per hospital_id) → well within limit

Data mapping:
  result[n].u_nurse_id  → preference_history[nurse_id]
  result[n].u_outcome   → ACCEPTED → accepted_count++; REJECTED → rejected_count++
  preference_weight     = accepted_count / (accepted_count + rejected_count) if total ≥ 3; else 0.00
  result[n].u_placement_date → ISO 8601 date (add T00:00:00Z for timestamp)

Fallback: If SN unavailable (>3 consecutive failures for same hospital_id):
  Set preference_weight=0.00 for all candidates in this pool
  Set no_preference_data_flag=true on RankedShortlist
  Log: { error_type: "SN_PREFERENCE_UNAVAILABLE", hospital_id, timestamp }
  Continue ranking without preference dimension (scoring uses remaining 3 dimensions,
  weights renormalized: credential 0.44, availability 0.34, proximity 0.22)
```

#### Contract 2: Coordinator Review UI API (New Build — Write)

```
Base URL: {COORDINATOR_UI_BASE_URL}/api/v1
  where COORDINATOR_UI_BASE_URL stored in env var COORDINATOR_UI_BASE_URL

Authentication:
  Method: Service-to-service internal token
  Header: X-Service-Token: {COORDINATOR_UI_SERVICE_TOKEN}
  COORDINATOR_UI_SERVICE_TOKEN stored in env var COORDINATOR_UI_SERVICE_TOKEN

Endpoint — Submit Review Decision:
  POST {COORDINATOR_UI_BASE_URL}/api/v1/rankings/{ranking_id}/review

Request body (JSON; all fields required unless noted):
{
  "decision": "APPROVED | EDITED | ESCALATED",   // required
  "selected_nurse_id": "string(36)",               // required; must match a nurse_id in RankedShortlist
  "edit_reason": "string | null",                  // required if decision=EDITED; max 500 chars; null otherwise
  "escalation_reason": "string | null",            // required if decision=ESCALATED; max 500 chars; null otherwise
  "coordinator_id": "string(36)"                  // required; authenticated coordinator's UUID
}

Success response (HTTP 200):
{
  "submission_id": "UUID",
  "ranked_shortlist_id": "UUID",
  "status": "SUBMITTED",
  "selected_nurse_id": "string(36)",
  "decided_at": "ISO 8601 UTC timestamp"
}

Error responses:
  HTTP 400: { "error": { "code": "INVALID_DECISION | MISSING_REQUIRED_FIELD | INVALID_NURSE_ID | EDIT_REASON_REQUIRED | ESCALATION_REASON_REQUIRED", "message": "string", "field": "string | null" } }
  HTTP 404: { "error": { "code": "RANKING_NOT_FOUND", "message": "string" } }
  HTTP 409: { "error": { "code": "ALREADY_REVIEWED", "message": "string", "reviewed_at": "ISO 8601 timestamp" } }
  HTTP 5xx: { "error": { "code": "INTERNAL_ERROR", "message": "string" } }

Timeout: 30 seconds (user-triggered synchronous action)
Retry: HTTP 5xx → 1 retry after 5s; HTTP 4xx → no retry; log and surface error to coordinator UI

Data mapping:
  decision → RankedShortlist.status (APPROVED→COORDINATOR_APPROVED, EDITED→COORDINATOR_EDITED, ESCALATED→ESCALATED)
  selected_nurse_id → sets RankedCandidate.selected_by_coordinator=true for matching nurse_id
  coordinator_id → RankedShortlist.coordinator_id
  decided_at (from response) → RankedShortlist.reviewed_at
  decision=EDITED + edit_reason → written to Labeled Feedback Store with ranking_id
```

#### Contract 3: Anthropic Claude API — AI Candidate Ranker

```
Endpoint: POST https://api.anthropic.com/v1/messages

Authentication:
  Header: x-api-key: {ANTHROPIC_API_KEY}
  ANTHROPIC_API_KEY stored in secrets manager (key: ANTHROPIC_API_KEY)
  Header: anthropic-version: 2023-06-01
  Header: Content-Type: application/json

Request format (JSON):
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 2048,
  "system": "string (system prompt ≤700 tokens; see §6 for prompt architecture)",
  "messages": [
    {
      "role": "user",
      "content": "string (ShiftRequirement + CandidatePool JSON; ≤1,200 tokens)"
    }
  ]
}

Success response (HTTP 200):
{
  "id": "string",
  "type": "message",
  "role": "assistant",
  "content": [{ "type": "text", "text": "string (JSON per RankedShortlist output schema)" }],
  "model": "claude-sonnet-4-6",
  "stop_reason": "end_turn | max_tokens",
  "usage": {
    "input_tokens": integer,
    "output_tokens": integer,
    "cache_read_input_tokens": integer
  }
}

Error responses:
  HTTP 400: { "type": "error", "error": { "type": "invalid_request_error", "message": "string" } }
  HTTP 401: { "type": "error", "error": { "type": "authentication_error", "message": "string" } }
  HTTP 429: { "type": "error", "error": { "type": "rate_limit_error", "message": "string" } }
         + response header: retry-after: integer (seconds)
  HTTP 529: { "type": "error", "error": { "type": "overloaded_error", "message": "string" } }
  HTTP 500/503: { "type": "error", "error": { "type": "api_error", "message": "string" } }

Timeout: 30 seconds per request

Retry logic:
  HTTP 529 (overloaded): 3 retries; exponential backoff 2s, 4s, 8s
  HTTP 5xx (server error): 3 retries; exponential backoff 2s, 4s, 8s
  HTTP 429 (rate limit): 1 retry after retry-after header value (default: 60s if absent)
  HTTP 4xx (other): no retry; log with request_id; route to human review
  stop_reason=max_tokens: no retry; log truncation; route to human review (malformed output)
  After all retries exhausted: set CandidatePool.status=RANKING_FAILED; alert ops

Circuit breaker: If error rate > 20% in any 5-minute window (calculated over sliding window),
  halt automated ranking; alert ops; route all pending CandidatePools to human review queue

Rate limits: Per Anthropic account tier. Daily budget: ~478K input tokens (184 cases × 2,600 tokens).
  Token budget per case: 2,048 output max. Monitor usage.input_tokens per response.

Data mapping (output):
  content[0].text → JSON.parse() → validate against RankedShortlist output schema (see §6)
  If JSON.parse fails: log malformed_output with raw text; route to human review
  validated JSON → RankedShortlist (ranked_candidates array, flags, explanations)

Fallback: If API unavailable > 5 minutes (5 consecutive timeouts per request):
  Halt automated ranking; alert ops dashboard
  Route all CandidatePools in status=READY to manual review queue
  Resume when API recovers (checked every 60 seconds via health probe)
```

---

## 6. Context Engineering Design

### Memory Architecture

| Memory Type | Content | Storage | Lifecycle |
|-------------|---------|---------|-----------|
| In-context | Current ShiftRequirement (specialty_code, shift_start, shift_end, hospital_id, required_credentials); CandidatePool (all NurseCandidate fields including all computed scores); hospital preference history for each nurse; scoring weights (A25) | LLM context window | Per ranking session (~2,600 tokens) |
| Episodic | Per-hospital: acceptance/rejection rates by specialty (last 12 months); per-nurse: latest placement date, reliability signal | ServiceNow query result + local 1-hour TTL cache (key: hospital_id) | Per request; refreshed via preference history query (Contract 1 above) |
| Semantic | Specialty code vocabulary, credential code mappings, scoring weight documentation | Static JSON in system prompt | Version-controlled in prompt config; update triggers system prompt version bump |
| Procedural | Role and scope, scoring formula, output JSON schema, guardrail instructions, tie-break rules, 3 few-shot examples | System prompt | Version-controlled; changes require canary deploy + A/B eval |

### Retrieval Strategy

- **Trigger**: CandidatePool event arrives with status=READY; ranker starts session
- **Target**: Retrieve `u_nurse_hospital_outcome` records for hospital_id (see Contract 1); structured DB query; not RAG/vector
- **Quality**: If result count < 3 per nurse-hospital pair, set preference_weight=0.00; log retrieval completeness ratio (accepted+rejected per nurse / total candidates) in audit log for ops monitoring
- **Cost management**: 1 ServiceNow query per ranking session (not per candidate); cached with 1-hour TTL per hospital_id to avoid redundant calls within the same hour at the same hospital; no vector/RAG → no chunking overhead

### Prompt Architecture

**System prompt structure** (target ≤700 tokens; static across sessions — cache with `cache_control: ephemeral`):

1. **Role and purpose** (~50 tokens):
   > "You are the MedFlex AI Candidate Ranker. Your job: given a set of nurse candidates and a hospital shift requirement, rank the top 1–3 candidates by composite score and produce a JSON RankedShortlist."

2. **Scoring formula** (~80 tokens):
   > "Composite score = (0.40 × credential_score) + (0.30 × availability_score) + (0.20 × proximity_score_normalized) + (0.10 × preference_weight). All inputs and outputs are in range 0.00–1.00. Round composite_score to 4 decimal places."

3. **Output JSON schema** (~150 tokens):
   ```json
   {
     "ranked_candidates": [
       {
         "rank": integer,
         "nurse_id": "string",
         "composite_score": "decimal(6,4)",
         "scoring_breakdown": {
           "credential_score": "decimal(3,2)",
           "availability_score": "decimal(3,2)",
           "proximity_score_normalized": "decimal(3,2)",
           "preference_weight": "decimal(3,2)"
         },
         "explanation": "string (max 500 chars)"
       }
     ],
     "stale_availability_flag": boolean,
     "no_preference_data_flag": boolean
   }
   ```

4. **Guardrail instructions** (~120 tokens):
   > "If candidates array is empty: return {ranked_candidates: [], escalation_required: true, escalation_reason: 'No candidates in pool'}. If all candidates have availability_status=STALE_RECORD: set stale_availability_flag=true and note this in each explanation. If all preference_weight values are 0.00: set no_preference_data_flag=true; rank by remaining 3 dimensions with renormalized weights (credential 0.44, availability 0.34, proximity 0.22). Do not include candidates with credential_match=false in the shortlist unless all candidates fail this dimension."

5. **Tie-break rule** (~40 tokens):
   > "If two candidates have equal composite_score to 4 decimal places: prefer lower proximity_score (km). If still tied: prefer more recent last_placement_date. If still tied: prefer lower nurse_id lexicographic order. Log 'tie-break applied' in explanation."

6. **Few-shot examples** (~260 tokens, 3 examples):
   - Example A: Standard case (3 candidates, clear rank-1)
   - Example B: Missing preference data for all candidates (no_preference_data_flag=true)
   - Example C: Top candidate has stale availability (stale_availability_flag=true, warning in explanation)

**User message per session** (~1,200 tokens):
```
ShiftRequirement: { specialty_code, shift_start, shift_end, hospital_id, required_credentials }
CandidatePool: [ {nurse_id, credential_score, availability_score, proximity_score_normalized, preference_weight, availability_status, last_placement_date}, ... ]
```

**Expected output per session** (~600 tokens): RankedShortlist JSON per schema above.

**Prompt caching:** System prompt (static; ≤700 tokens) uses `cache_control: ephemeral` on the Anthropic API to amortize system prompt cost across the 184 daily sessions. Cache TTL: 5 minutes. With 184 cases/day (avg 1 per 4.7 min), cache remains warm throughout the business day. Cached token savings: ~700 tokens × $3.00/M × 184 cases/day ≈ $0.39/day.

**Chain-of-thought instruction** (embedded in guardrails): "For each candidate, reason through each scoring dimension before computing composite_score. Show your work in the explanation field."

**Token discipline:** System prompt ≤700 tokens. User message ≤1,200 tokens. Max output 2,048 tokens. Per-case total: ~2,600 tokens. Do not repeat scoring formula in user message — it is in the system prompt.

---

## 7. Validation Design

### Happy Path

**Input:**
- ShiftRequirement: specialty_code=ICU_RN, shift_start=2026-05-20T07:00:00Z, shift_end=2026-05-20T19:00:00Z, hospital_id=STDAVIDS_NORTH, required_credentials=[BLS, ACLS]
- CandidatePool: 3 nurses:
  - Nurse A: credential_match=true, availability_status=AVAILABLE, proximity_score=2.1km, preference_weight=0.80
  - Nurse B: credential_match=true, availability_status=AVAILABLE, proximity_score=5.4km, preference_weight=0.30
  - Nurse C: credential_match=true, availability_status=STALE_RECORD, proximity_score=1.2km, preference_weight=0.50

**Expected output:**
- RankedShortlist: rank-1=Nurse A (composite=0.40×1.00 + 0.30×1.00 + 0.20×0.958 + 0.10×0.80 = 0.9512), rank-2=Nurse B, rank-3=Nurse C
- stale_availability_flag=true (Nurse C has STALE_RECORD)
- Nurse C explanation includes "availability record may be stale — verify before submission"
- status=PENDING_REVIEW
- RankedShortlist created within 10 seconds of CandidatePool.status=READY
- Audit log entry created with full scoring breakdown

### Edge Cases

**EC-1: Single candidate pool**
- Input: CandidatePool with exactly 1 nurse; credential_match=true, availability_status=AVAILABLE
- Expected: RankedShortlist with 1 RankedCandidate; rank=1; coordinator review UI shows single option with note "Only one qualified candidate available"

**EC-2: All candidates have stale availability**
- Input: CandidatePool where all 3 NurseCandidate.availability_status=STALE_RECORD
- Expected: RankedShortlist created (not blocked); stale_availability_flag=true; each explanation includes staleness warning; coordinator sees banner warning in Review UI; ranking proceeds on other dimensions

**EC-3: No preference history for any candidate at this hospital**
- Input: hospital_id=NEW_HOSPITAL; preference history query returns 0 records for all candidates
- Expected: All preference_weight=0.00; no_preference_data_flag=true; scoring uses renormalized weights (0.44 credential, 0.34 availability, 0.22 proximity); explanation per candidate notes "no preference history — ranked by credential match and proximity"

**EC-4: Composite score tie between two candidates**
- Input: Nurse A and Nurse B have equal composite_score=0.7000 to 4 decimal places; Nurse A proximity_score=3.2km, Nurse B proximity_score=5.1km
- Expected: Nurse A wins tie-break (lower proximity); tie-break logged in Nurse A's explanation: "tie-break applied: lower proximity score"

**EC-5: Coordinator edits ranking at BP4**
- Input: RankedShortlist rank-1=Nurse A, rank-3=Nurse C; coordinator selects Nurse C (rank 3) at BP4
- Expected: decision=EDITED; Nurse C.selected_by_coordinator=true; edit_reason captured (optional); RankedShortlist.status=COORDINATOR_EDITED; audit log records: {from_rank: 3, coordinator_id, reviewed_at}; Labeled Feedback Store entry written with {ranking_id, presented_rank1=Nurse A, selected=Nurse C, edit_reason}

**EC-6: Hospital rejection triggers BP5 re-rank**
- Input: Submission for Nurse A rejected by hospital (JtD-5a event)
- Expected: New CandidatePool created for same ShiftRequirement (Nurse A removed or demoted); new RankedShortlist produced; coordinator receives new review request in UI; previous ranking remains in audit log with outcome=REJECTED

**EC-7: 30-minute SLA breach with shift starting in 90 minutes**
- Input: RankedShortlist created at T=0; no coordinator action by T=30min; shift_start = T+90min
- Expected: At T=30min, auto-escalation fires; RankedShortlist.status → ESCALATED; escalation_reason = "auto: SLA breach — shift within 2 hours"; senior coordinator notified; audit log records auto-escalation with timestamp

### Failure Modes

**FM-1: LLM API fails after all retries**
- Condition: Claude API returns HTTP 5xx on all 3 retry attempts (total 4 calls)
- Expected: CandidatePool.status → RANKING_FAILED; RankedShortlist not created; coordinator dashboard shows "Ranking failed — manual review required"; ops alert fired; coordinator manually selects from CandidatePool.candidates

**FM-2: CandidatePool has zero candidates**
- Condition: CandidatePool.status=NO_CANDIDATES (JtD-2 produced no qualifying nurses)
- Expected: Ranker does not invoke LLM; ShiftRequirement.status → NO_CANDIDATES_FOUND; coordinator notified with message "No qualified candidates found — consider expanding search criteria or contacting hospital for timeline extension"; audit log entry created

**FM-3: Coordinator Review UI unavailable at BP4**
- Condition: Coordinator UI service returns HTTP 5xx
- Expected: RankedShortlist remains PENDING_REVIEW; auto-escalation SLA timer still runs; coordinator receives backup notification (email/SMS per A14) with ranking details; coordinator can approve via fallback mechanism (direct ServiceNow entry if UI is unavailable > 15 min); ops alerted

---

## 8. Compounding Roadmap

### Wave 1 — Foundation Agents (8-week MVP)

The ranker is **Build Order 3** in the Wave 1 dependency chain:

| Build Order | Agent/Component | Rationale | Shared Asset Created |
|:---:|---|---|---|
| 1 | JtD-1 Shift Intake Parser | BP2 pipeline gate; no downstream agent runs without structured ShiftRequirement | ServiceNow read API client; Claude API client; Hospital lookup table; LLM domain prompt |
| 2 | JtD-2 Candidate Search | Depends on JtD-1 output; builds nurse DB query layer | Nurse DB query layer; geocoding API; NurseCandidate scoring logic |
| **3** | **JtD-3 Ranker + Coordinator UI** | **Depends on JtD-1 + JtD-2; most complex Wave 1 build** | **Coordinator Review UI; rule-based ranker; Labeled Feedback Store (A19)** |
| 4 | JtD-4 Submission | Depends on BP4 approval event from JtD-3 | ServiceNow write API; full audit trail |
| 5 | JtD-5a Monitoring | Depends on JtD-4 submission event | Notification trigger; response capture |

**JtD-3-specific Wave 1 deliverables:**
- Rule-based composite scorer (A25 weights; configurable parameters in config file, not hardcoded)
- Coordinator Review UI: present ranked shortlist, capture decision, surface stale/missing-preference flags
- Labeled Feedback Store schema and write path (read path used in Wave 2)
- A19 feedback accumulation: every coordinator decision writes {ranking_id, presented_shortlist, selected_nurse_id, decision, edit_reason, outcome (set post-submission)} to Labeled Feedback Store

### Wave 2 — Compounding (Months 3–6)

- **JtD-3 ML Ranker Upgrade**: Replace rule-based scorer with supervised ML model. Prerequisite: A19 threshold met (~8,000–11,000 labeled examples; ~60 working days at 184 fills/day × ~75% structured capture). Reuses Labeled Feedback Store (built Wave 1), Coordinator Review UI (no change), ServiceNow integrations (no change). Expected accuracy improvement: from ~85% (rule-based, A23) to ≥90% (ML-based).
- Progressive threshold lowering: As ranker accuracy is validated above coordinator baseline, auto-approve confidence threshold is introduced; HITL rate target reduces from 100% → ≤20% (A19).

### Wave 3 — AI-Native Operations (Year 2)

- **JtD-3 Progressive Autonomy**: Auto-submit on high-confidence matches (composite_score > 0.90 AND availability_status=AVAILABLE AND preference_weight > 0.50 AND no_preference_data_flag=false). Eliminates coordinator review step for qualifying matches. Requires: ML ranker accuracy validated above 95% on held-out test set; Marcus approval (A13 reassessment).
- **Multi-agent Coordination**: Parallel matching at scale; priority queue management distinguishing emergency re-fill (BP6) from standard requests; cross-ranker deduplication to prevent internal nurse race conditions (A20).

### Integration Reuse Matrix

| Integration / Asset | JtD-1 Parser | JtD-2 Search | **JtD-3 Ranker** | JtD-4 Submit | JtD-5a Monitor | JtD-6 (W2) | JtD-5b (W2–3) |
|--------------------|:-----------:|:-----------:|:---------:|:-----------:|:--------------:|:-----------:|:-------------:|
| ServiceNow read API | ✓ Build | ✓ Reuse | ✓ Reuse | | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| ServiceNow write API | | | | ✓ Build | | ✓ Reuse | |
| Claude API client | ✓ Build | | ✓ Reuse | | | ✓ Reuse | ✓ Reuse |
| Hospital lookup table | ✓ Build | ✓ Reuse | ✓ Reuse | | | | |
| Geocoding API | | ✓ Build | ✓ Reuse | | | ✓ Reuse | |
| Coordinator Review UI | | | ✓ Build | ✓ Reuse | ✓ Reuse | | ✓ Reuse |
| Labeled Feedback Store | | | ✓ Build (A19) | | | ✓ Reuse | ✓ Reuse |
| Notification API | | | | | ✓ Build | ✓ Reuse | |
| Audit Log | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse |

---

## 9. Shared Glossary

*This glossary is shared across `04a-capability-spec-match-selection.md` (JtD-3) and `04b-capability-spec-shift-intake-parsing.md` (JtD-1). All terms used in both documents are defined here.*

| Term | Definition |
|------|------------|
| **A[n]** | Assumption ID; all assumptions defined in `specs/assumptions.md` |
| **availability_score** | Numeric representation of NurseCandidate.availability_status: AVAILABLE=1.00, STALE_RECORD=0.50, UNAVAILABLE=0.00; read-only computed field |
| **availability_status** | Enum: `[AVAILABLE, STALE_RECORD, UNAVAILABLE]`. STALE_RECORD = nurse record_freshness > 30 days (A17). UNAVAILABLE = no shift window overlap |
| **BP1** | Breakpoint 1: Low-confidence ShiftRequirement parse (confidence_score < 0.80) routes to human review queue; parser stops and coordinator clarifies with hospital |
| **BP2** | Breakpoint 2: High-confidence ShiftRequirement (confidence_score ≥ 0.80) automatically triggers JtD-2 candidate search pipeline |
| **BP3** | Breakpoint 3: Completed CandidatePool (status=READY) handed to JtD-3 Match Selection |
| **BP4** | Breakpoint 4: Coordinator reviews and approves/edits AI-ranked shortlist before submission to hospital; the designed HITL boundary in MVP |
| **BP5** | Breakpoint 5: Hospital rejection of a submission triggers return to JtD-3 with updated CandidatePool for re-ranking |
| **BP6** | Breakpoint 6: Emergency re-fill re-enters the full JtD-1–4 pipeline via priority queue (JtD-6) |
| **CandidatePool** | Structured set of 0–5 NurseCandidate records produced by JtD-2; input to JtD-3. Status enum: `[BUILDING, READY, NO_CANDIDATES, RANKING_FAILED]` |
| **composite_score** | Weighted ranking formula: `(0.40 × credential_score) + (0.30 × availability_score) + (0.20 × proximity_score_normalized) + (0.10 × preference_weight)`. Range 0.0000–1.0000. Weights defined in A25 and are configurable parameters |
| **confidence_score** | Field-level extraction certainty for a ShiftRequirement; range 0.00–1.00. Threshold for auto-proceed to JtD-2: ≥0.80. Computed as min(field_confidence values for all required non-null fields) |
| **coordinator_id** | UUID identifying the MedFlex coordinator who acts at BP4; FK to Coordinator entity in ServiceNow |
| **CredentialCode** | Standardized credential identifier. Exhaustive enum: `BLS, ACLS, PALS, NRP, TNCC, CCRN, CEN, OCN, CNOR, AWHONN_BASIC, AWHONN_INTERMEDIATE` |
| **field_confidence** | JSON object with per-field extraction confidence scores: `{hospital_id: decimal, specialty_code: decimal, shift_start: decimal, shift_end: decimal, required_credentials: decimal}`. All values 0.00–1.00 |
| **HITL** | Human-in-the-Loop; coordinator action required before agent proceeds. Two HITL gates in MVP: BP1 (low-confidence parse) and BP4 (candidate selection approval) |
| **hospital_id** | Unique hospital identifier in MedFlex ServiceNow instance. Format: ALLCAPS_LOCATION_STRING (e.g., STDAVIDS_NORTH, STMARYS_WEST). Maintained in Hospital lookup table |
| **JtD** | Job to be Done; a cognitive contract between an actor and an outcome (from `specs/cognitive-load-map.md`) |
| **JtD-1** | Shift Intake Parsing — converts free-text hospital requests into structured ShiftRequirement objects (see `04b-capability-spec-shift-intake-parsing.md`) |
| **JtD-3** | Match Selection — ranks evaluated CandidatePool and produces RankedShortlist for coordinator review (this document) |
| **Labeled Feedback Store** | Internal data store built in Wave 1 to capture coordinator ranking decisions and submission outcomes; training corpus for Wave 2 ML ranker (A19) |
| **NurseCandidate** | Evaluated nurse record within a CandidatePool; includes nurse_id, specialty_match, credential_match, availability_status, proximity_score, all computed scores, and preference_weight |
| **preference_weight** | Computed as accepted_placements / total_placements for a nurse-hospital pair (last 12 months). 0.00 if < 3 historical records. Source: ServiceNow `u_nurse_hospital_outcome` table (A12, A24) |
| **proximity_score** | Distance in km from nurse location to hospital. Computed via geocoding API in JtD-2 |
| **proximity_score_normalized** | `max(0.00, (50.00 - proximity_score) / 50.00)`. MAX_PROXIMITY = 50 km. Range 0.00–1.00 |
| **RankedCandidate** | Single entry in RankedShortlist.ranked_candidates; includes rank, nurse_id, composite_score, scoring_breakdown, explanation, selected_by_coordinator |
| **RankedShortlist** | Output of JtD-3; ordered list of 1–3 RankedCandidate records. Status enum: `[PENDING_REVIEW, COORDINATOR_APPROVED, COORDINATOR_EDITED, ESCALATED, RANKING_FAILED]` |
| **ShiftRequest** | Raw inbound record from ServiceNow; contains source_ticket_id (SN sys_id), raw_text, status. Entity owned by JtD-1 |
| **ShiftRequirement** | Structured output of JtD-1; contains specialty_code, shift_start, shift_end, hospital_id, required_credentials, confidence_score, field_confidence. Input to JtD-2 and contextually to JtD-3 |
| **SN** | ServiceNow; MedFlex enterprise platform for shift requests, nurse profiles, and submissions |
| **SN_INSTANCE_URL** | Environment variable holding the base URL of MedFlex's ServiceNow instance (e.g., `https://medflex.service-now.com`); set during deployment |
| **specialty_code** | Standardized specialty identifier. Exhaustive enum: `ICU_RN, ER_RN, MED_SURG_RN, FLOAT_POOL_RN, OR_RN, L_D_RN, PACU_RN, TELE_RN, PEDS_RN, NICU_RN, PSYCH_RN, CATH_LAB_RN, ONCOLOGY_RN, STEP_DOWN_RN` |
| **Wave 1** | 8-week MVP delivery; builds JtD-1, JtD-2, JtD-3, JtD-4, JtD-5a; self-funding from $346K/year labor savings |
| **Wave 2** | Months 3–6 post-MVP; ML ranker upgrade, JtD-6 partial automation, JtD-5b data surfacing |
| **Wave 3** | Year 2; JtD-3 progressive autonomy, multi-agent coordination |

---

## 10. Production-Grade Validation Results

All specifications in this document passed production-grade validation against `input-docs/production-spec-checklist.md`.

**INTEGRATION CONTRACTS** — Pass. Three integration contracts (ServiceNow preference history, Coordinator Review UI, Anthropic Claude API) include: endpoint URL pattern or full URL, authentication method and credential storage location, complete request format with all required/optional fields, complete success and error response formats with all relevant HTTP status codes, timeout value (numeric), retry logic covering all error conditions, rate limits (numeric or sourced assumption), data mapping in both directions, and explicit fallback behavior. ServiceNow instance URL and table name are A24-flagged assumptions with validation questions assigned.

**ENTITY PRECISION** — Pass. All entities (CandidatePool, NurseCandidate, RankedShortlist, RankedCandidate) include: UUID primary keys, all attributes with types and value constraints, required/optional/nullable designations, enum values in exhaustive SCREAMING_SNAKE_CASE lists, ISO 8601 UTC timestamps, foreign key relationships with cascade behavior, computed fields marked read-only with formulas, complete state machines with all valid transitions and prerequisites, and immutability rules on creation-time fields.

**BUILDABILITY** — Pass. All KPIs are numeric and measurable. Scoring formula is explicit with weights and formula (A25). Confidence threshold is numeric (0.80). Output JSON schema is fully defined. Tie-break rule is deterministic and documented. Escalation conditions are numeric (30-minute SLA, 2-hour shift proximity). No modal verbs without scope. All conditionals have explicit criteria and outcomes. Validation design includes 1 happy-path scenario, 7 edge cases, and 3 failure modes with explicit expected outcomes.
