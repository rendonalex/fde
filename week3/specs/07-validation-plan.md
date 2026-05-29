# 07 — Validation Plan: MedFlex Agentic Transformation

> Covers JtD-1 (Shift Intake Parser) and JtD-3 (Match Selection Ranker).
> Input specs: `specs/04b-capability-spec-shift-intake-parsing.md`, `specs/04a-capability-spec-match-selection.md`.
> Success criteria: `specs/01-problem-framing-and-success-metrics.md`.
> New assumption added: A29 (`specs/assumptions.md`).

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Scope](#2-scope)
3. [Happy Path Tests](#3-happy-path-tests)
4. [Edge Cases](#4-edge-cases)
5. [Error Handling](#5-error-handling)
6. [Production Risk Register](#6-production-risk-register)
7. [Test Execution Matrix](#7-test-execution-matrix)
8. [Exit Criteria](#8-exit-criteria)
9. [Validation Summary](#9-validation-summary)

---

## 1. Executive Summary

This validation plan covers the two highest-value agents in the MedFlex pipeline: the Shift Intake Parser (JtD-1) and the Match Selection Ranker (JtD-3). Together they represent the critical path from free-text hospital request to coordinator-approved shortlist — the sequence that must work reliably before fill time can drop below 1 hour (M1).

The plan is risk-weighted: tests concentrate on the four failure modes with the highest business impact — parser accuracy below the 85% threshold (blocks A10 validation), the advisory lock race condition (duplicate processing corrupts pipeline), the ServiceNow write failure at BP4 (stalls submission), and LLM API unavailability (fills queue with HUMAN_REVIEW backlog). Everything else is P1 or lower.

**Test counts**: 5 happy path, 5 edge cases, 5 error handling = 15 tests total.
**Deploy gate**: All 7 P0 tests must pass. No P0 security issues open. Performance SLAs met.

---

## 2. Scope

| In scope | Out of scope |
|---|---|
| JtD-1 parser: LLM extraction, confidence routing, ServiceNow writes, HITL queue write | JtD-2 candidate search (separate spec) |
| JtD-3 ranker: disqualification pass, scoring formula, shortlist generation, BP4 review API, feedback write | JtD-4 submission (downstream; receives trigger only) |
| End-to-end pipeline: JtD-1 → JtD-3 → BP4 coordinator decision | Feature 5 Confirmation Notifier (deferred) |
| Integration contracts: ServiceNow read/write, Claude Sonnet API, Google Maps API, Internal HITL Queue API, Internal Coordinator Review API | Hospital-facing portal, nurse mobile app |
| SLA compliance: parse latency ≤ 30s, shortlist latency ≤ 5s, M1 fill time ≤ 60min | Load testing beyond 2× daily volume (Phase 2) |

**Environment requirement (A29)**: All tests run against a ServiceNow non-production instance pre-loaded with representative anonymized data. Tests against the production instance are prohibited before exit criteria are fully met.

---

## 3. Happy Path Tests

### HP-01 — Standard shift request auto-parses and produces an approved shortlist

**Workflow**: Full end-to-end pipeline from QUEUED record to JtD-4 trigger

**Priority**: P0

| Step | Action | Expected Result |
|---|---|---|
| 1 | Shift record `u_status = QUEUED` created in ServiceNow with text: `"ICU float RN, BLS/ACLS req, St. David's North, 7a–7p Friday May 15"` | Record visible in poll query |
| 2 | Agent polls; acquires advisory lock (PATCH `u_status = PARSING`) | HTTP 200; no second agent can pick up same record |
| 3 | Agent calls Claude Sonnet API with system prompt + raw_text | HTTP 200; valid JSON returned |
| 4 | Agent validates JSON; computes `confidence_score = min(1.00, 0.95, 0.95, 1.00, 1.00) = 0.95` | `confidence_score ≥ 0.85` → BP2 path |
| 5 | Agent writes `ParsedShiftRequirement` to `u_parsed_shift_requirement` | HTTP 201; `u_parse_method = LLM_AUTO` |
| 6 | Agent PATCHes `u_status = PARSED`; sets `u_parsed_at` | HTTP 200 |
| 7 | Agent emits `shift_parsed` event; JtD-2 triggered (stubbed for this test) | Event confirmed |
| 8 | JtD-3 receives `CandidatePool` (3 candidates: Nurse A has PALS, Nurse B does not, Nurse C has expired ACLS) | Pool received within 5s of JtD-3 start |
| 9 | JtD-3 disqualification pass: Nurse C → `EXPIRED_REQUIRED_CREDENTIAL` | Nurse C excluded |
| 10 | JtD-3 scores Nurse A (0.96), Nurse B (0.55); generates `RankedShortlist` | `all_disqualified = false`; `low_confidence = false` |
| 11 | Shortlist presented to coordinator; coordinator submits `action = APPROVED`, `selected_nurse_id = Nurse A` | HTTP 200 from `POST /internal/api/v1/coordinator-review` |
| 12 | Agent writes `CoordinatorReview` to ServiceNow; writes `RankerFeedback` (`coordinator_edited = false`) | Both HTTP 201 |
| 13 | Agent triggers JtD-4 with `selected_nurse_id = Nurse A` | JtD-4 trigger event confirmed |

**Pass criteria**:
- Total elapsed time from QUEUED to JtD-4 trigger ≤ 60 minutes (M1)
- Parse latency (steps 2–6) ≤ 30 seconds
- Shortlist generated within 5 seconds of JtD-3 receiving CandidatePool
- `coordinator_edited = false` in RankerFeedback
- No duplicate records in any ServiceNow table

---

### HP-02 — BP1 HITL path resolves and pipeline continues

**Workflow**: Ambiguous request → coordinator corrects → ParsedShiftRequirement written → JtD-2 triggered

**Priority**: P0

| Step | Action | Expected Result |
|---|---|---|
| 1 | Shift record created with text: `"ED RN needed Friday 7am–3pm, BLS required, St. David's"` | QUEUED |
| 2 | Agent parses; LLM returns `location_id = UNKNOWN`, `location_confidence = 0.30` | `confidence_score = 0.30` |
| 3 | Agent routes to BP1: writes `HITLQueueEntry` with `failure_reason = AMBIGUOUS_LOCATION`; PATCHes `u_status = HUMAN_REVIEW` | HITLQueueEntry `status = PENDING`; partial parse pre-fills `specialty_code = ED_RN`, `credentials = [BLS]` |
| 4 | Coordinator claims entry (→ `IN_REVIEW`); corrects `location_id = ST_DAVIDS_NORTH`; submits | HITLQueueEntry `status = COMPLETED` |
| 5 | `ParsedShiftRequirement` written with `u_parse_method = HUMAN_CORRECTED` | HTTP 201 |
| 6 | `ShiftRequest.u_status = PARSED`; `shift_parsed` event emitted | JtD-2 triggered |

**Pass criteria**:
- HITLQueueEntry PENDING → IN_REVIEW transition ≤ 30 minutes (SLA check)
- `u_raw_text` on ShiftRequest is immutable — unchanged after coordinator correction
- `ParsedShiftRequirement` reflects coordinator's corrected `location_id`, not LLM's UNKNOWN
- Exactly one `shift_parsed` event emitted (no double-fire)

---

### HP-03 — Coordinator edits shortlist (EDITED action); RankerFeedback logs correctly

**Workflow**: Coordinator selects rank #2 over rank #1; pipeline continues; edit logged for A19 corpus

**Priority**: P0

| Step | Action | Expected Result |
|---|---|---|
| 1 | JtD-3 presents shortlist [Nurse A (0.96), Nurse B (0.55)] to coordinator | `status = PENDING_REVIEW`; `presented_at` set |
| 2 | Coordinator submits `action = EDITED`, `selected_nurse_id = Nurse B`, `edit_reason = "Nurse A unavailable per direct contact"` | HTTP 200; `next_step = SUBMISSION_QUEUED` |
| 3 | Internal API validates `Nurse B ∈ shortlist.candidates` | Validation passes |
| 4 | CoordinatorReview written with `action = EDITED` | HTTP 201 |
| 5 | RankerFeedback written with `coordinator_edited = true` | `selected_nurse_id = Nurse B`; `coordinator_edited = true` |
| 6 | JtD-4 triggered with `selected_nurse_id = Nurse B` | Trigger confirmed |

**Pass criteria**:
- `coordinator_edited = true` in RankerFeedback (A19 labeled example captured)
- `review_duration_seconds` computed server-side from `presented_at` — not accepted from client
- JtD-4 fires with Nurse B, not Nurse A

---

### HP-04 — Hospital rejects submission at BP5; JtD-3 re-ranks and presents revised shortlist

**Workflow**: BP5 rejection event triggers re-rank; coordinator sees revised shortlist

**Priority**: P1

| Step | Action | Expected Result |
|---|---|---|
| 1 | Nurse A approved at BP4; JtD-4 submitted; hospital sends BP5 rejection with `rejected_nurse_id = Nurse A` | JtD-5a event received |
| 2 | MT-3.8 triggered: re-rank excluding Nurse A from original pool | Nurse A excluded from new scoring pass |
| 3 | New `RankedShortlist` generated with remaining eligible candidates | `REJECTION_CONTEXT` flag present |
| 4 | New shortlist presented to coordinator: "Hospital rejected Nurse A — presenting revised shortlist" | Coordinator sees context |
| 5 | Coordinator approves from revised shortlist | New `CoordinatorReview` written; new JtD-4 trigger |
| 6 | Original `RankerFeedback.submission_outcome` updated to REJECTED | Outcome logged |

**Pass criteria**:
- Original RankerFeedback record is immutable (not overwritten); new RankerFeedback record created with same `shift_request_id`
- `submission_outcome = REJECTED` on the original record
- No stale Nurse A in revised shortlist candidates array

---

### HP-05 — 200-record corpus validation passes A10 threshold

**Workflow**: Pre-launch accuracy validation against labeled corpus (week 2 check)

**Priority**: P0

| Step | Action | Expected Result |
|---|---|---|
| 1 | Load 200 historical shift requests (anonymized; labeled ground truth from coordinator review) into staging ServiceNow | Records in QUEUED state |
| 2 | Run parser in batch against all 200 records | No crashes; all records transition out of QUEUED |
| 3 | For each auto-parsed record: compare `ParsedShiftRequirement` fields against labeled ground truth | Field-level accuracy computed per record |
| 4 | Compute per-field accuracy: specialty, datetime_start, datetime_end, location_id, credentials | Aggregated accuracy score |
| 5 | Compute overall extraction accuracy and HITL rate | Summary metrics |

**Pass criteria**:
- Field-level extraction accuracy ≥ 85% (A10) — blocks launch if not met
- HITL rate ≤ 15% — blocks launch if not met
- Zero records stuck in PARSING state after run completes (no lock leaks)
- No `PARSE_FAILED` records from malformed LLM JSON (zero tolerance for unhandled JSON errors)

---

## 4. Edge Cases

### EC-01 — Concurrent agent instances attempt to process the same QUEUED record

**Scenario**: Two parser agent instances start simultaneously; both attempt to PATCH same `sys_id` to PARSING.

**Input**: Single QUEUED record; two agents poll within the same 30-second window.

**Expected behavior**:
- First PATCH succeeds: HTTP 200 → that agent proceeds to LLM call
- Second PATCH receives HTTP 409 (already PARSING) → treated as advisory lock failure → agent skips record; does NOT call LLM
- Exactly one `ParsedShiftRequirement` written; exactly one `shift_parsed` event emitted

**Pass criteria**:
- Zero duplicate `ParsedShiftRequirement` records for same `u_shift_request_id`
- Zero duplicate `shift_parsed` events
- Skipping agent logs: `"advisory_lock_failed: skipping record {sys_id}"`

**Priority**: P0

---

### EC-02 — All candidates in pool are disqualified (zero eligible after disqualification pass)

**Scenario**: CandidatePool contains 5 nurses; all are missing a required credential (`RN_LICENSE`).

**Input**: `ParsedShiftRequirement.credentials = [{code: RN_LICENSE, required: true}]`; all 5 candidates lack `RN_LICENSE` in their profile.

**Expected behavior**:
- All 5 → `disqualified = true`, `disqualification_reason = MISSING_REQUIRED_CREDENTIAL`
- `RankedShortlist.all_disqualified = true`; `candidates = []`
- Status transitions directly `GENERATED → ESCALATED` (not PENDING_REVIEW)
- Coordinator notified with disqualification reason per candidate
- JtD-4 NOT triggered
- Ops log: `"ALL_CANDIDATES_DISQUALIFIED for shift_request_id={id}"`

**Pass criteria**:
- No `CoordinatorReview` record written
- No `shift_parsed` event re-emitted
- `RankedShortlist.status = ESCALATED` immediately after generation (not after timeout)

**Priority**: P1

---

### EC-03 — Low-confidence shortlist requires explicit coordinator acknowledgment

**Scenario**: All candidates have `composite_score = 0.33` (stale availability + distant location + prior rejections). `max(composite_score) < 0.40` → `low_confidence = true`.

**Input**: `low_confidence = true` shortlist presented; coordinator attempts to approve without `low_confidence_acknowledged = true`.

**Expected behavior**:
- First submission (missing `low_confidence_acknowledged`): HTTP 422 with `{"error": "low_confidence_acknowledgment_required"}`
- Second submission with `low_confidence_acknowledged = true`: HTTP 200; accepted normally
- RankerFeedback written; `coordinator_edited` reflects actual selection

**Pass criteria**:
- HTTP 422 on first attempt (not HTTP 200)
- No CoordinatorReview written on the failed attempt
- Idempotency: second submission with same `shortlist_id` + `low_confidence_acknowledged = true` succeeds; third duplicate attempt returns HTTP 409

**Priority**: P1

---

### EC-04 — Duplicate `ParsedShiftRequirement` write (idempotency under retry)

**Scenario**: Agent writes `ParsedShiftRequirement` successfully (HTTP 201), then retries due to a network timeout on the response leg. Second write attempt uses same `u_shift_request_id`.

**Expected behavior**:
- Second POST returns HTTP 409 (unique constraint on `u_shift_request_id`)
- Agent treats 409 as success; uses existing `u_parsed_requirement_id` from first write for downstream event
- Exactly one `shift_parsed` event emitted (not two)
- No second record created in `u_parsed_shift_requirement`

**Pass criteria**:
- One record in `u_parsed_shift_requirement` for the `u_shift_request_id`
- One `shift_parsed` event in event log
- No error surfaced to ops for an expected 409

**Priority**: P0

---

### EC-05 — Parser polling restarts after 5-minute gap; 50 accumulated QUEUED records process correctly

**Scenario**: Parser agent is restarted; 5-minute outage; ~10 records accumulated in QUEUED state (at 184/day over 8h ≈ 0.38/min × 5min ≈ 2 records; stress-test with 50).

**Expected behavior**:
- On restart: agent polls; finds 50 QUEUED records; processes in FIFO order
- All 50 process without error within ~7 minutes (50 × ~8s/parse)
- No records stuck in PARSING from prior run (no stale lock from crashed instance)
- Latency spike logged; ops alert fires if any record's `u_received_at` is > 30 minutes stale

**Pass criteria**:
- All 50 records reach terminal state (PARSED, HUMAN_REVIEW, or PARSE_FAILED) within 10 minutes of restart
- Zero records remain in PARSING state after 10 minutes (stale lock detection)
- `u_received_at` + processing delay is logged per record for SLA tracking

**Priority**: P1

---

## 5. Error Handling

### ER-01 — Claude Sonnet API returns HTTP 401 (invalid API key)

**Trigger**: `ANTHROPIC_API_KEY` is invalid or revoked.

**Expected behavior**:
- Agent receives HTTP 401 on first call
- Agent halts all processing immediately — does NOT retry (401 is not transient)
- Ops alert fires: `"ANTHROPIC_API_KEY invalid — parser halted"`
- All in-progress records (status = PARSING) remain in PARSING; ops must manually re-queue after key is fixed
- No records transition to PARSE_FAILED (this is an infrastructure error, not a parse error)

**User message (ops alert)**: `"Parser halted: ANTHROPIC_API_KEY authentication failure. Replace key and restart agent."`

**Pass criteria**:
- Zero LLM calls made after the 401
- Ops alert delivered within 60 seconds of the 401
- Agent process is stopped (not silently continuing in degraded state)
- No records incorrectly transitioned to PARSE_FAILED

**Priority**: P0

---

### ER-02 — ParsedShiftRequirement ServiceNow write fails after 3 retries (dead-letter queue)

**Trigger**: ServiceNow write API returns HTTP 503 three consecutive times for the `u_parsed_shift_requirement` POST.

**Expected behavior**:
- Agent retries with backoff: 4s, 8s, 16s (total ~28s)
- After 3 failures: extraction result written to dead-letter queue (local JSON file)
- `shift_parsed` event is NOT emitted (JtD-2 not triggered until write confirmed)
- Ops alert fires: `"ParsedShiftRequirement write failed for shift_request_id={id}; queued for retry"`
- Reconciliation cron retries every 5 minutes; emits `shift_parsed` once write confirmed
- `ShiftRequest.u_status` stays PARSING (not PARSED) until write is confirmed

**User message (ops alert)**: `"ServiceNow write failure — {N} records pending reconciliation."`

**Pass criteria**:
- Zero premature `shift_parsed` events before ServiceNow write confirmed
- Dead-letter queue entry persists across agent restart
- After ServiceNow recovers: reconciliation cron writes record; emits event; clears dead-letter entry
- If dead-letter queue depth > 10: escalation alert fires

**Priority**: P0

---

### ER-03 — Coordinator submits BP4 review for already-reviewed shortlist (duplicate submission)

**Trigger**: Coordinator double-clicks submit; or browser refreshes mid-submit; second POST to `/internal/api/v1/coordinator-review` with same `shortlist_id`.

**Expected behavior**:
- First submission: HTTP 200; `review_id` returned; JtD-4 triggered
- Second submission (same `shortlist_id`): HTTP 409 with `{"error": "already_reviewed", "review_id": "<original_review_id>"}`
- No second `CoordinatorReview` record written
- No second JtD-4 trigger
- No second `RankerFeedback` record written

**User message**: `"This shortlist has already been reviewed. Submission ID: {review_id}"`

**Pass criteria**:
- HTTP 409 on duplicate (not HTTP 200 or 500)
- Exactly one `CoordinatorReview` record in ServiceNow for the `shortlist_id`
- Exactly one JtD-4 trigger event in the event log

**Priority**: P0

---

### ER-04 — Google Maps geocoding API unavailable; shortlist generation continues unblocked

**Trigger**: Google Maps Geocoding API returns HTTP 503 for all requests during shortlist generation.

**Expected behavior**:
- Agent retries each ZIP code lookup: 2s, 4s, 8s (3 attempts)
- After 3 failures per candidate: `proximity_score = 0.50` (neutral fallback) for all candidates
- Shortlist generated without proximity differentiation
- Coordinator UI shows: `"Distance data unavailable for this shortlist"`
- Warning logged per candidate: `"geocoding_unavailable; proximity_score defaulted to 0.50 for nurse_id={id}"`
- Ops alert fires only if geocoding fails for > 10 consecutive shortlists (not on first failure)

**User message (coordinator UI)**: `"Distance data unavailable for this shortlist"`

**Pass criteria**:
- Shortlist generated and presented to coordinator within 5 seconds despite geocoding failure
- `composite_score` computed correctly with `proximity_score = 0.50` for all candidates (not null, not 0.00)
- No shortlist generation blocked by geocoding failure

**Priority**: P1

---

### ER-05 — ServiceNow `u_coordinator_review` write fails at BP4; JtD-4 proceeds

**Trigger**: Coordinator approves at BP4; Internal Review API accepts; agent attempts POST to `u_coordinator_review` → HTTP 503 after 3 retries.

**Expected behavior**:
- CoordinatorReview event queued to dead-letter store
- JtD-4 is NOT blocked — submission proceeds with approved `nurse_id` (submission is higher priority than audit write)
- Ops alert fires: `"CoordinatorReview write failed for shift_request_id={id}; queued for retry"`
- Reconciliation cron re-attempts write every 15 minutes
- Dead-letter record marked `delayed_write = true` for audit traceability when eventually written
- If dead-letter queue depth > 10: escalation to ops lead

**Pass criteria**:
- JtD-4 trigger fires even when CoordinatorReview write fails
- Dead-letter entry is created and survives agent restart
- Reconciliation writes the record within 30 minutes of ServiceNow recovery
- `delayed_write = true` flag is present on the eventually-written record

**Priority**: P0

---

## 6. Production Risk Register

These risks are not test cases — they are named operational hazards with mitigation strategies that must be confirmed before production deployment.

| Risk ID | Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|---|
| R1 | **LLM output drift** — Claude Sonnet model versions change silently on Anthropic's API; extraction quality degrades below 85% threshold (A10) | HITL rate spikes; coordinator overload | Medium (model updates are periodic) | Pin `model: claude-sonnet-4-6` in all API calls; rerun 200-record corpus validation after any Anthropic model deprecation notice; monitor HITL rate weekly as a leading indicator |
| R2 | **HITL rate spike** — Parser HITL rate exceeds 15% in production (e.g., new hospital with unusual request format) | Coordinator queue backlog; fill time SLA breach | Medium | Alert threshold: ops notified when 7-day rolling HITL rate > 15%; runbook: add hospital-specific few-shot examples to system prompt (Wave 2 mitigation) |
| R3 | **ServiceNow rate limit (A23 Low confidence)** — Actual rate limit is lower than assumed 60 req/min; burst parsing after outage recovery triggers 429s | Parsing stalls; dead-letter queue fills | Low-Medium (A23 is Low confidence) | Confirm actual rate limits with MedFlex ServiceNow admin before launch; implement 429 handling with `Retry-After` backoff (already in spec); test at 2× daily volume |
| R4 | **Single point of failure: Claude Sonnet API** — Anthropic outage routes 100% of parses to HITL; coordinators cannot absorb volume manually | Fill time SLA breach during outage | Low (Anthropic SLA >99.9%); catastrophic if it occurs | No fallback LLM in MVP (T3 decision); mitigation is HITL queue with priority routing; ops runbook for manual triage during extended outage (>30 min); feature flag to pause intake queue during outage rather than accumulate a backlog coordinators cannot clear |
| R5 | **Parser schema lock drift** — `ParsedShiftRequirement` field added or renamed post-week-1 without coordinating JtD-2 and JtD-3 update | Downstream NullPointerException / silent data loss | Low (explicit contract; one team) | Schema change process: any field removal or rename requires version bump + explicit sign-off from JtD-2 and JtD-3 maintainers; adding optional fields is non-breaking (consumers ignore unknown fields) |
| R6 | **Google Maps API key expiry** — `GOOGLE_MAPS_API_KEY` expires or hits quota; proximity scores default to 0.50 for all candidates permanently | Ranker proximity component effectively disabled; ranking quality degrades | Low (Google API key rotation is predictable) | Set 30-day expiry reminder on API key rotation; ops alert on `REQUEST_DENIED` status from geocoding (§7.4 ER-04 path); monitor `geocoding_unavailable` warning log rate |
| R7 | **Stale PARSING lock on agent crash** — Agent crashes mid-parse; `ShiftRequest.u_status` stuck in PARSING; record never processed again | Silent data loss (shift never filled) | Low-Medium (depends on infrastructure stability) | Reconciliation cron: detect records in PARSING for > 5 minutes; reset to QUEUED; alert ops; agent must be stateless enough to re-process any record from QUEUED safely |

---

## 7. Test Execution Matrix

| Test ID | Category | Description | Type | Priority | Status | Owner | Notes |
|---|---|---|---|---|---|---|---|
| HP-01 | Happy Path | Standard ICU RN request end-to-end (JtD-1 → JtD-3 → BP4 approve → JtD-4 trigger) | Manual + Integration | P0 | Not Started | | Requires staging ServiceNow + stubbed JtD-2 and JtD-4 |
| HP-02 | Happy Path | BP1 HITL path: ambiguous location → coordinator corrects → pipeline continues | Manual | P0 | Not Started | | Coordinator must be available for HITL resolution step |
| HP-03 | Happy Path | Coordinator edits shortlist (EDITED action); `coordinator_edited = true` in RankerFeedback | Manual | P0 | Not Started | | Validates A19 data capture |
| HP-04 | Happy Path | BP5 hospital rejection → re-rank → revised shortlist presented | Manual | P1 | Not Started | | Requires JtD-5a event simulation |
| HP-05 | Happy Path | 200-record corpus accuracy ≥ 85%; HITL rate ≤ 15% (A10 check) | Automated | P0 | Not Started | | Must run in week 2; gate for launch |
| EC-01 | Edge Case | Concurrent agents: advisory lock prevents duplicate processing | Automated | P0 | Not Started | | Requires running 2 agent instances simultaneously |
| EC-02 | Edge Case | All candidates disqualified → status = ESCALATED (not PENDING_REVIEW) | Automated | P1 | Not Started | | |
| EC-03 | Edge Case | Low-confidence shortlist: HTTP 422 without `low_confidence_acknowledged = true` | Automated | P1 | Not Started | | |
| EC-04 | Edge Case | Duplicate `ParsedShiftRequirement` write → HTTP 409 → idempotent success; one event emitted | Automated | P0 | Not Started | | |
| EC-05 | Edge Case | 50-record backlog after restart clears without stale PARSING locks | Automated | P1 | Not Started | | Stress-test; run after HP-05 corpus |
| ER-01 | Error Handling | HTTP 401 from Anthropic → agent halts + ops alert; no PARSE_FAILED records created | Manual | P0 | Not Started | | Replace `ANTHROPIC_API_KEY` with invalid value in staging |
| ER-02 | Error Handling | ServiceNow write fails → dead-letter queue; `shift_parsed` not emitted until write confirmed | Automated | P0 | Not Started | | Block ServiceNow write endpoint via test harness |
| ER-03 | Error Handling | Duplicate BP4 submission → HTTP 409; one CoordinatorReview; one JtD-4 trigger | Automated | P0 | Not Started | | |
| ER-04 | Error Handling | Google Maps unavailable → `proximity_score = 0.50`; shortlist generated within SLA | Automated | P1 | Not Started | | Block Maps API via test harness |
| ER-05 | Error Handling | ServiceNow `u_coordinator_review` write fails → dead-letter; JtD-4 not blocked | Automated | P0 | Not Started | | |

**P0 count**: 9 tests. **P1 count**: 6 tests.

---

## 8. Exit Criteria

### Must Have (deploy gate)

- [ ] All 9 P0 tests pass
- [ ] HP-05 corpus accuracy ≥ 85% field-level extraction (A10 hard gate)
- [ ] HP-05 HITL rate ≤ 15% on 200-record corpus
- [ ] Parse latency ≤ 30 seconds (measured on HP-01 and HP-05)
- [ ] Shortlist generation ≤ 5 seconds (measured on HP-01)
- [ ] 90%+ of P1 tests pass; documented workarounds for any failures
- [ ] No open P0 security issues (specifically: coordinator JWT validated server-side; `review_duration_seconds` computed server-side, not accepted from client; no PII in agent logs)
- [ ] Advisory lock race condition test (EC-01) passes — non-negotiable data integrity gate
- [ ] Dead-letter queue and reconciliation cron tested end-to-end (ER-02, ER-05)
- [ ] Production risk register reviewed; R1–R7 mitigations confirmed or deferred with explicit sign-off

### Should Have (can deploy with workaround)

- [ ] EC-02 (zero eligible candidates) passes — workaround: ops monitors ESCALATED queue
- [ ] EC-03 (low-confidence acknowledgment) passes — workaround: coordinator training covers this case
- [ ] EC-05 (50-record backlog) passes — workaround: ops runbook for manual triage during outage
- [ ] ER-04 (geocoding failure) passes — workaround: ops informed proximity scores will be neutral during Maps outage

### Issue Severity Definitions

| Severity | Definition | Action |
|---|---|---|
| P0 (Critical) | Blocks core pipeline, data loss risk, security issue, or accuracy below threshold | Must fix before deploy |
| P1 (High) | Major functionality impaired; workaround exists | Should fix; can deploy with documented workaround |
| P2 (Medium) | Minor issue; edge case; coordinator UX degraded | Can deploy; address in Wave 2 |
| P3 (Low) | Enhancement; performance optimization | Future release |

---

## 9. Validation Summary

*To be completed at execution time.*

### Results

| Category | Total | Passed | Failed | Pass Rate |
|---|---|---|---|---|
| Happy Path | 5 | | | |
| Edge Cases | 5 | | | |
| Error Handling | 5 | | | |
| **Total** | **15** | | | |

### Issues

| ID | Severity | Description | Status | Resolution |
|---|---|---|---|---|
| | | | | |

### Recommendation

- [ ] **Deploy to production** — all P0 criteria met; A10 accuracy validated; SLAs confirmed
- [ ] **Deploy with conditions** — [list any P1 failures and workarounds]
- [ ] **Do not deploy** — [list P0 blockers]

---

*Document owner: Alexandra Rendon, FDE*
*Last updated: 2026-05-13*
*Referenced specs: `specs/04a-capability-spec-match-selection.md`, `specs/04b-capability-spec-shift-intake-parsing.md`, `specs/01-problem-framing-and-success-metrics.md`*
