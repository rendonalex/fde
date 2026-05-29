# Validation Plan — AI Claims Processing Transformation
## Greenfield Health Systems · ADR-1 and ADR-4

**Prepared by:** FDE Engagement Lead  
**Date:** 2026-05-27  
**Status:** Draft — Phase 1 Pre-Launch

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [ADR-1: Claim Intake and Format Validation Agent](#2-adr-1-claim-intake-and-format-validation-agent)
   - 2.1 [Happy Path Tests](#21-happy-path-tests)
   - 2.2 [Edge Cases](#22-edge-cases)
   - 2.3 [Error Handling](#23-error-handling)
3. [ADR-4: Clinical Content Triage Agent](#3-adr-4-clinical-content-triage-agent)
   - 3.1 [Happy Path Tests](#31-happy-path-tests)
   - 3.2 [Edge Cases](#32-edge-cases)
   - 3.3 [Error Handling](#33-error-handling)
4. [Test Execution Matrix](#4-test-execution-matrix)
5. [Risk Register — Named Risks with Mitigations](#5-risk-register--named-risks-with-mitigations)
6. [Exit Criteria](#6-exit-criteria)
7. [Validation Summary](#7-validation-summary)

---

## 1. Executive Summary

This validation plan covers the two Wave 1 capability specifications: **ADR-1 (Claim Intake and Format Validation Agent)** and **ADR-4 (Clinical Content Triage Agent)** for Greenfield Health Systems. ADR-4 operates in shadow mode only during Wave 1; live routing requires clearing the [A6] false-negative gate before Wave 2. Both agents share the CMS API [A12] as a single point of failure.

The plan is risk-based and organized around five critical failure modes:

1. **False negatives on ADR-4** — a clinical claim misrouted to Fast Path reaches adjudication without physician review (patient safety failure; blocks Wave 2 launch)
2. **CMS API unavailability** — ADR-1 cannot write normalized records; ADR-4 cannot read claims for classification (both agents fail)
3. **Shadow mode isolation breach** — ADR-4 classification writes to live routing while MODE=SHADOW, corrupting the claims queue
4. **Non-EDI extraction accuracy below threshold** — HITL rate rises, negating intake savings and increasing manual workload beyond baseline
5. **Codebook version drift** — ADR-4 classifies against a stale codebook, producing systematic false negatives until discovered

**Exit gate:** ADR-1 must achieve ≥95% EDI parsing accuracy and ≤18% HITL rate before Wave 1 go-live. ADR-4 must achieve <2% false-negative rate over ≥2,000 labeled shadow-mode examples [A6] before Wave 2 live routing activates. All P0 tests must pass; ≥90% of P1 tests must pass.

Assumptions added to the register: [A29], [A30], [A31].

---

## 2. ADR-1: Claim Intake and Format Validation Agent

### 2.1 Happy Path Tests

| Test ID | Workflow | Steps | Expected Result | Priority |
|---------|----------|-------|-----------------|----------|
| HP-1A | EDI 837P claim — fully complete fields | (1) Submit valid EDI 837P from a professional provider. (2) Agent parses all required fields: member_id, provider_npi, date_of_service, icd10_codes, cpt_codes, billed_amount. (3) All fields extracted at ≥0.85 confidence. (4) Agent writes NormalizedClaimRecord to CMS. | `extraction_status = AUTO_COMPLETE`; all required fields populated; audit event `CLAIM_WRITTEN_TO_CMS` logged; record appears in triage queue within 30 seconds. | P0 |
| HP-1B | Portal JSON claim — all required fields present | (1) Submit a well-formed portal JSON payload containing all 12 required CMS fields. (2) Agent maps JSON keys to NormalizedClaimRecord schema. (3) All fields confidence ≥0.85. (4) CMS write succeeds. | `extraction_status = AUTO_COMPLETE`; no HUMAN_REQUIRED fields; record routed to triage queue; SLA timer started. | P0 |
| HP-1C | FHIR R4 claim bundle — single encounter | (1) Submit a FHIR R4 Claim resource. (2) Agent extracts required fields from FHIR resource elements. (3) Confidence ≥0.85 for all fields. (4) CMS write succeeds. | Normalized record maps FHIR fields correctly; `extraction_status = AUTO_COMPLETE`; no schema errors; audit trail complete. | P1 |
| HP-1D | Non-EDI PDF — clear scan, all fields visible | (1) Submit a clean PDF claim from a small provider group. (2) IDP pipeline extracts all required fields. (3) All fields ≥0.85 confidence. (4) Agent writes AUTO_COMPLETE record to CMS. | `extraction_status = AUTO_COMPLETE` (not HUMAN_REQUIRED); IDP confidence values logged per field; CMS record created; no HITL ticket generated. | P1 |
| HP-1E | Duplicate claim detection — exact re-submission | (1) Submit a claim that is byte-identical to a previously processed claim (same member_id, date_of_service, cpt_codes, billed_amount). (2) Agent computes duplicate signature. (3) Agent detects match against existing CMS record. | `extraction_status = PENDING_DUPLICATE`; duplicate flag written to CMS; source claim reference logged; no new CMS record created; audit event `DUPLICATE_DETECTED` logged. | P0 |

### 2.2 Edge Cases

| Test ID | Workflow | Steps | Expected Result | Priority |
|---------|----------|-------|-----------------|----------|
| EC-1A | Non-EDI PDF — low-quality scan (member_id unreadable) | (1) Submit a PDF claim with a degraded scan; member_id field is smudged/unreadable. (2) IDP pipeline extracts member_id at 0.60 confidence (below 0.85 threshold). (3) All other required fields extract at ≥0.85. | `extraction_status = HUMAN_REQUIRED` for member_id; HITL ticket created in review queue; record held; CMS write deferred until human reviewer confirms member_id [A29]. | P0 |
| EC-1B | Identity fallback rule — member_id ≥0.85, name below threshold | (1) Submit a PDF claim where member_id extracts at 0.87 confidence but subscriber_name extracts at 0.72. (2) Agent applies identity fallback rule: if member_id ≥0.85, name below threshold permits AUTO_COMPLETE with flag. | `extraction_status = AUTO_COMPLETE`; subscriber_name field flagged as `LOW_CONFIDENCE_SUPPRESSED`; no HITL ticket; audit note logged per identity fallback rule. | P1 |
| EC-1C | EXCEPTION_NOTE routing — claim references out-of-network provider with special contract flag | (1) Submit a claim with a provider NPI that matches the EXCEPTION_NOTE routing list in the system prompt. (2) Agent identifies special routing flag during field extraction. | `extraction_status = EXCEPTION_NOTE`; claim routed to exception handling queue (not standard triage); audit event logged; claim does not enter standard adjudication path. | P1 |
| EC-1D | Partial EDI 837I — institutional claim missing revenue code | (1) Submit an EDI 837I institutional claim where the revenue code segment (SV2) is absent. (2) Agent parses all other required fields at ≥0.85 confidence. (3) Revenue code is a required field for institutional claims. | `extraction_status = HUMAN_REQUIRED` for revenue_code; HITL ticket created; all other fields written; claim held in intake review queue pending human entry of revenue code. | P1 |
| EC-1E | Portal submission — rate limit response from portal API | (1) Submit 150 portal claims in rapid succession triggering the portal API rate limit (assume 100 requests/minute limit [A29]). (2) Agent receives HTTP 429 Too Many Requests on the 101st request. (3) Agent applies exponential backoff. | Agent retries with backoff (1s, 2s, 4s); portal requests resume after cooldown; no claims lost; all 150 records eventually written to CMS; `PORTAL_RATE_LIMIT_BACKOFF` event logged to ops monitoring. | P1 |

### 2.3 Error Handling

| Test ID | Workflow | Steps | Expected Result | Priority |
|---------|----------|-------|-----------------|----------|
| EH-1A | CMS API unavailable — HTTP 503 during claim write | (1) CMS API returns HTTP 503 for a NormalizedClaimRecord write. (2) Agent retries three times with exponential backoff (1s, 2s, 4s). (3) All retries fail. | Agent buffers the normalized record locally; ops alert triggered via monitoring channel; `CMS_WRITE_FAILED_BUFFERED` audit event logged; no data loss; record retried when CMS recovers. SLA timer paused for the affected claim. [A12 single point of failure] | P0 |
| EH-1B | IDP pipeline returns no extraction result — complete failure | (1) Submit a PDF claim. (2) IDP pipeline times out (>30 seconds) and returns no field extractions. (3) Agent receives an empty extraction payload. | `extraction_status = HUMAN_REQUIRED` for all fields; claim routed to HITL queue with note `IDP_EXTRACTION_FAILED`; no CMS write attempted; ops alert if IDP failure rate exceeds 5% over a 15-minute window [A30]. | P0 |
| EH-1C | EDI 837 malformed segment — parse error | (1) Submit an EDI 837P file with a malformed ISA header (missing element separator). (2) EDI parser encounters a structural error before field extraction begins. | Claim rejected at ingestion with `PARSE_ERROR` status; not written to CMS; audit event `EDI_PARSE_FAILED` logged with claim reference and error detail; submitting party notified via standard rejection response. | P1 |
| EH-1D | CMS write returns HTTP 409 — record already exists | (1) Agent attempts to write a NormalizedClaimRecord to CMS for a claim_id that already has a CMS record (e.g., race condition from concurrent processing). (2) CMS returns HTTP 409 Conflict. | Agent does not overwrite existing record; logs `DUPLICATE_CMS_RECORD` event; pauses processing for this claim_id; alerts ops; no data mutation. Idempotency guaranteed. | P1 |
| EH-1E | Required field missing from EDI — NPI absent | (1) Submit an EDI 837P where the billing provider NPI segment (NM1*85) is completely absent. (2) Agent identifies NPI as a required field with no value to extract. | Agent sets provider_npi confidence = 0.0; `extraction_status = HUMAN_REQUIRED`; HITL ticket created for NPI lookup; claim not written to CMS until NPI confirmed. Audit trail records absence of NPI in source submission. | P1 |

---

## 3. ADR-4: Clinical Content Triage Agent

### 3.1 Happy Path Tests

| Test ID | Workflow | Steps | Expected Result | Priority |
|---------|----------|-------|-----------------|----------|
| HP-4A | Routine administrative claim — FAST_PATH in shadow mode | (1) NormalizedClaimRecord enters triage queue with `extraction_status = AUTO_COMPLETE`; no ICD-10 codes, CPT codes are standard office visit (99213), `prior_auth_required = false`. (2) ADR-4 runs in MODE=SHADOW. (3) Agent checks each indicator against codebook — no provision matched. | `routing_decision = FAST_PATH`; `confidence ≥0.85`; `routing_mode = SHADOW`; reasoning_trace written with Steps 1–5; shadow log entry written to log store; CMS record NOT updated with routing_decision (shadow mode only); `ROUTING_DECISION_LOGGED` audit event. | P0 |
| HP-4B | Oncology claim — CLINICAL_PATH in shadow mode | (1) NormalizedClaimRecord with ICD-10 C50.912 (breast cancer), CPT 96413 (chemotherapy), `prior_auth_required = true`. (2) ADR-4 runs in MODE=SHADOW. (3) Agent matches ICD-10 C50.x pattern and CPT 964xx pattern against codebook. | `routing_decision = CLINICAL_PATH`; `confidence = 1.0`; `clinical_indicators_detected` lists ICD-10 C50.912 and CPT 96413; codebook provision IDs cited; `routing_mode = SHADOW`; reasoning_trace complete; shadow log entry written. | P0 |
| HP-4C | Prior auth only — CLINICAL_PATH in live mode | (1) NormalizedClaimRecord with no diagnostic codes but `prior_auth_required = true`. (2) ADR-4 runs in MODE=LIVE (post-[A6] gate). (3) Codebook provision: prior_auth_required = true alone triggers CLINICAL_PATH. | `routing_decision = CLINICAL_PATH`; `confidence = 1.0`; `routing_mode = LIVE`; PUT written to CMS updating routing_decision field; `ROUTING_DECISION_WRITTEN` audit event; claim enters physician review queue. | P0 |
| HP-4D | [A6] gate measurement — 2,000 labeled shadow examples | (1) Shadow mode runs for 60-day window. (2) Query shadow log store: `labeled_entries ≥ 2,000`. (3) Compute: `false_negative_rate = false_negative_count / labeled_entries`. | `false_negative_rate < 0.02` (less than 2%); [A6] gate passes; sign-off conditions met; Wave 2 live routing authorization can proceed. | P0 |
| HP-4E | Confidence fallback — borderline code triggers CLINICAL_PATH | (1) NormalizedClaimRecord with a single CPT code that produces only a broad-prefix match (one-character prefix); agent assigns confidence = 0.55. (2) Fallback rule: confidence < 0.70 → override to CLINICAL_PATH [A24]. | `routing_decision = CLINICAL_PATH`; `confidence = 0.55`; `confidence_fallback = true`; `routing_mode` preserved; reasoning_trace documents the fallback invocation; `ROUTING_FALLBACK_APPLIED` audit event logged. | P0 |

### 3.2 Edge Cases

| Test ID | Workflow | Steps | Expected Result | Priority |
|---------|----------|-------|-----------------|----------|
| EC-4A | Novel CPT code — not in criteria codebook | (1) NormalizedClaimRecord contains CPT 0789T (novel procedure not in current codebook). (2) Agent's Steps 1–4 find no matching provision; no indicator matches any trigger pattern. (3) Novel case guardrail applies. | `routing_decision = CLINICAL_PATH`; `confidence = 0.0`; `criteria_provisions_matched = ["NOVEL_CASE"]`; `NOVEL_CASE_FLAGGED` audit event; claim added to Dr. Webb adjudication queue; codebook gap captured for next revision cycle [A15]. | P0 |
| EC-4B | Claim arrives before codebook is deployed — empty codebook | (1) ADR-4 is instantiated with `{{CRITERIA_CODEBOOK}}` substituted with an empty string (misconfiguration). (2) Agent processes a claim with CPT 99214. (3) No codebook provisions to match. | Agent treats all claims as NOVEL_CASE (no provision to match); all claims route CLINICAL_PATH; `NOVEL_CASE_FLAGGED` for every claim; ops alert triggered if NOVEL_CASE rate >50% over 5-minute window [A31]; codebook deployment issue surfaced immediately rather than silently miscategorizing claims. | P0 |
| EC-4C | Claim with `extraction_status = HUMAN_REQUIRED` enters triage queue | (1) A NormalizedClaimRecord in HUMAN_REQUIRED state is incorrectly inserted into the triage queue (queue filter bypass). (2) ADR-4 receives the record. | Agent detects `extraction_status ≠ AUTO_COMPLETE`; applies safe fallback: routes to CLINICAL_PATH with `confidence = 0.0`, `criteria_provisions_matched = ["PRECONDITION_FAILED"]`, and reasoning trace explaining the precondition failure; ops alert triggered (queue filter may be broken); claim proceeds to physician review (patient safety maintained); shadow log entry written with PRECONDITION_FAILED status for monitoring. | P0 |
| EC-4D | ICD-10 code prefix matches multiple provisions — high-confidence classification | (1) NormalizedClaimRecord with ICD-10 I25.10 (coronary artery disease). (2) Code matches both a cardiovascular provision (prefix I25) and a prior authorization provision (based on CPT codes). Only ICD-10 present; no CPT codes in record. (3) Agent matches I25.x provision only. | `routing_decision = CLINICAL_PATH`; `confidence = 1.0` (exact prefix match); only the matching provision cited; no false escalation from unmatched provision; reasoning_trace shows single match, correctly cited. | P1 |
| EC-4E | Shadow mode log store unavailable — write fails | (1) ADR-4 classifies a claim in MODE=SHADOW. (2) POST to shadow log store returns HTTP 503. (3) Agent retries with backoff. (4) All retries fail. | Agent buffers shadow log entry locally; ops alert triggered (`SHADOW_LOG_WRITE_FAILED`); classification still logged locally; CMS not updated (shadow mode only); shadow entry retried when log store recovers. [A6] gate measurement not compromised if recovery is within 24 hours. [A25] | P0 |

### 3.3 Error Handling

| Test ID | Workflow | Steps | Expected Result | Priority |
|---------|----------|-------|-----------------|----------|
| EH-4A | Shadow mode isolation breach — agent attempts LIVE write while MODE=SHADOW | (1) ADR-4 system prompt is MODE=SHADOW. (2) LLM outputs JSON with `routing_mode: LIVE` (invalid; model hallucinated or prompt was mutated). (3) Agent validates output before any write. | Agent detects `routing_mode = LIVE` output from LLM when agent MODE=SHADOW; applies safe fallback: overrides to CLINICAL_PATH with `confidence = 0.0`, `criteria_provisions_matched = ["SHADOW_ISOLATION_VIOLATION"]`; critical ops alert triggered (shadow isolation breach detected); claim proceeds to physician review; shadow log entry written with violation status; prevents corrupting comparison dataset while maintaining claim processing continuity. [Single point of failure — shadow isolation] | P0 |
| EH-4B | False-negative detected post-audit — ADR-4 routed FAST_PATH, physician found clinical content | (1) ADR-4 in LIVE mode routes a claim as FAST_PATH (confidence 0.85). (2) Monthly 5% physician audit sample includes this claim. (3) Reviewing physician identifies clinical content that ADR-4 missed (ICD-10 code not in codebook). | Physician logs `FN_DETECTED_AUDIT` event in audit trail; claim re-routed to CLINICAL_PATH; FN event submitted to Dr. Webb adjudication queue; codebook gap recorded [A15]; cumulative FN rate recalculated; if monthly FN rate >2%, automatic suspension of autonomous routing triggered and ops alerted. | P0 |
| EH-4C | Model produces malformed JSON output — unparseable response | (1) ADR-4 LLM returns a response with invalid JSON or missing required fields (e.g., `routing_decision` key absent). (2) Agent attempts to parse response. | Agent catches parse error (JSONDecodeError, KeyError, missing fields); applies safe fallback: routes to CLINICAL_PATH with `confidence = 0.0`, `criteria_provisions_matched = ["OUTPUT_PARSE_FAILED"]`, reasoning trace with error details; ops alert triggered (model may be producing malformed output); claim proceeds to physician review; pattern monitoring alerts ops if rate exceeds 1% over 15 minutes. | P0 |
| EH-4D | Codebook version mismatch — ADR-4 prompt version does not match deployed codebook version | (1) A codebook update is deployed (e.g., codebook v2.0) but ADR-4 system prompt still references codebook v1.9 (deployment lag). (2) Classification runs against stale codebook. | Pre-deployment validation check must compare `ADR4_PROMPT_VERSION` against `CRITERIA_CODEBOOK_VERSION`; if mismatch detected at startup, agent refuses to process claims; logs `CODEBOOK_VERSION_MISMATCH` alert; processing halted until versions reconciled and Dr. Webb sign-off confirmed [A15]. [Regulatory drift risk] | P1 |
| EH-4E | CMS API unavailable — ADR-4 cannot write routing decision in LIVE mode | (1) ADR-4 in LIVE mode classifies a claim. (2) PUT to CMS to write routing_decision returns HTTP 503. (3) Retries exhausted. | Agent buffers routing decision locally with claim_id and timestamp; ops alert triggered; claim remains in PENDING_TRIAGE state in CMS (no routing corruption); buffered decision retried on recovery; `CMS_ROUTING_WRITE_FAILED` audit event logged. [A12 single point of failure] | P0 |

---

## 4. Test Execution Matrix

| Test ID | Agent | Category | Phase | Environment | Owner | Status |
|---------|-------|----------|-------|-------------|-------|--------|
| HP-1A | ADR-1 | Happy Path | Wave 1 pre-launch | Staging + CMS mock | Intake dev lead | Pending |
| HP-1B | ADR-1 | Happy Path | Wave 1 pre-launch | Staging + CMS mock | Intake dev lead | Pending |
| HP-1C | ADR-1 | Happy Path | Wave 1 pre-launch | Staging + CMS mock | Intake dev lead | Pending |
| HP-1D | ADR-1 | Happy Path | Wave 1 pre-launch | Staging + real IDP | Intake dev lead | Pending |
| HP-1E | ADR-1 | Happy Path | Wave 1 pre-launch | Staging + CMS mock | Intake dev lead | Pending |
| EC-1A | ADR-1 | Edge Case | Wave 1 pre-launch | Staging + low-qual test PDFs | QA lead | Pending |
| EC-1B | ADR-1 | Edge Case | Wave 1 pre-launch | Staging | QA lead | Pending |
| EC-1C | ADR-1 | Edge Case | Wave 1 pre-launch | Staging | QA lead | Pending |
| EC-1D | ADR-1 | Edge Case | Wave 1 pre-launch | Staging | QA lead | Pending |
| EC-1E | ADR-1 | Edge Case | Wave 1 pre-launch | Staging + portal rate limiter | QA lead | Pending |
| EH-1A | ADR-1 | Error Handling | Wave 1 pre-launch | Staging + CMS fault injector | QA lead | Pending |
| EH-1B | ADR-1 | Error Handling | Wave 1 pre-launch | Staging + IDP mock (fail) | QA lead | Pending |
| EH-1C | ADR-1 | Error Handling | Wave 1 pre-launch | Staging | QA lead | Pending |
| EH-1D | ADR-1 | Error Handling | Wave 1 pre-launch | Staging + CMS mock (409) | QA lead | Pending |
| EH-1E | ADR-1 | Error Handling | Wave 1 pre-launch | Staging | QA lead | Pending |
| HP-4A | ADR-4 | Happy Path | Wave 1 shadow | Shadow staging | Triage dev lead | Pending |
| HP-4B | ADR-4 | Happy Path | Wave 1 shadow | Shadow staging | Triage dev lead | Pending |
| HP-4C | ADR-4 | Happy Path | **Wave 2 pre-launch** | Production staging | Triage dev lead | Pending |
| HP-4D | ADR-4 | Happy Path | Wave 1 end (Day 60) | Production shadow log | FDE + Dr. Webb | Pending |
| HP-4E | ADR-4 | Happy Path | Wave 1 shadow | Shadow staging | Triage dev lead | Pending |
| EC-4A | ADR-4 | Edge Case | Wave 1 shadow | Shadow staging | QA lead | Pending |
| EC-4B | ADR-4 | Edge Case | Wave 1 pre-launch | Shadow staging | QA lead | Pending |
| EC-4C | ADR-4 | Edge Case | Wave 1 pre-launch | Shadow staging | QA lead | Pending |
| EC-4D | ADR-4 | Edge Case | Wave 1 shadow | Shadow staging | QA lead | Pending |
| EC-4E | ADR-4 | Edge Case | Wave 1 shadow | Shadow staging + log store fault | QA lead | Pending |
| EH-4A | ADR-4 | Error Handling | Wave 1 pre-launch | Shadow staging | Security/QA lead | Pending |
| EH-4B | ADR-4 | Error Handling | Wave 2 (ongoing) | Production | Dr. Webb / FDE | Pending |
| EH-4C | ADR-4 | Error Handling | Wave 1 shadow | Shadow staging | Triage dev lead | Pending |
| EH-4D | ADR-4 | Error Handling | Wave 1 + 2 pre-launch | Staging | DevOps lead | Pending |
| EH-4E | ADR-4 | Error Handling | Wave 2 pre-launch | Production staging + CMS fault | QA lead | Pending |

---

## 5. Risk Register — Named Risks with Mitigations

### R-1: CMS API — Single Point of Failure [A12]

**Risk:** Both ADR-1 and ADR-4 depend entirely on the CMS REST API for reads and writes. Any CMS outage or rate-limiting event halts claim ingestion (ADR-1) and prevents routing decisions from being persisted (ADR-4). This is the highest-impact single point of failure in the architecture.

**Probability:** Medium — legacy CMS platforms have intermittent availability; upgrade windows create planned outages.

**Impact:** Critical — claims accumulate unprocessed; SLA timers continue; payer penalties accrue [A8]; operator trust in the AI platform erodes.

**Mitigations:**
- ADR-1: Buffer normalized records locally on CMS write failure; retry with exponential backoff; ops alert after 3 consecutive failures (test: EH-1A)
- ADR-4 LIVE: Buffer routing decisions locally on CMS PUT failure; claim stays in PENDING_TRIAGE state; retry on recovery (test: EH-4E)
- Both agents: CMS health check endpoint polled every 30 seconds; circuit breaker trips after 5 consecutive failures; switchover to buffer mode before queue backs up
- Validation: Confirm CMS API SLA and planned maintenance windows in Week 1 IT discovery [A12]; establish a batch-file fallback integration if CMS API availability is <99.5%

---

### R-2: Portal API Rate Limits

**Risk:** Provider portal submissions arrive in bursts (end-of-day batch submissions from large provider groups). If the portal API enforces per-minute request limits, ADR-1 will receive HTTP 429 responses during peak ingestion, delaying normalization and SLA-start for affected claims.

**Probability:** Medium — all major portal APIs enforce rate limits; burst patterns are predictable.

**Impact:** Moderate — claims delayed 5–30 minutes at peak; SLA timers start late if claim arrival timestamp is not preserved.

**Mitigations:**
- ADR-1 applies exponential backoff on HTTP 429; preserves original claim submission timestamp as `received_at` regardless of processing delay (test: EC-1E)
- Portal submission rate monitored; if average rate regularly approaches limit, request increased quota from portal vendor or implement a submission queue with token-bucket rate control [A29]
- SLA timer anchors to `received_at` (original submission), not `normalized_at` (write to CMS), so rate-limit-induced delays do not penalize the claim's SLA position

---

### R-3: Model Accuracy Drift (ADR-4)

**Risk:** As Greenfield's claim mix evolves (new provider relationships, new CPT/ICD-10 code sets, seasonal patterns), ADR-4's classification accuracy may degrade over time against the fixed criteria codebook. A model or codebook that was accurate at launch may produce increasing false-negative rates months later without any visible failure signal.

**Probability:** Medium — CPT code additions occur annually (AMA releases); ICD-10 updates occur each October; new specialty providers may submit unfamiliar code patterns.

**Impact:** Critical — if false-negative rate drifts above 2%, clinical claims reach adjudication without physician review. Harm may not be visible until a physician audit or adverse outcome surfaces the error.

**Mitigations:**
- Monthly physician audit of 5% Fast Path sample (post-Wave 2 launch); auditor logs `FN_DETECTED_AUDIT` for any missed clinical content (test: EH-4B)
- Automated monthly FN rate dashboard compared against 2% threshold; automatic routing suspension if threshold breached
- Annual CPT/ICD-10 code set review against codebook coverage; Dr. Webb reviews novel case accumulation for codebook gaps [A15]
- On each new Claude model release, re-run the shadow-mode calibration suite on a 200-claim labeled sample before promoting the new model to production [A27 governance cadence]
- Novel case rate monitored monthly; if >5% of claims are NOVEL_CASE, codebook expansion is triggered before FN rate is affected

---

### R-4: Regulatory Drift — AI Adjudication Permissibility [A11, U5]

**Risk:** U.S. state insurance AI regulations are in active flux. Several states have introduced or are considering requirements for physician oversight of AI-generated claim denials. If a new regulation takes effect in Greenfield's operating jurisdictions, the Fast Path's autonomous denial capability may become non-compliant mid-deployment.

**Probability:** Medium — multiple states have active AI insurance bills as of 2026; federal HHS guidance on AI in healthcare is pending.

**Impact:** High — if AI-generated denials without physician sign-off become prohibited, the Fast Path scope must be narrowed to approvals only. This reduces throughput gain and requires architectural change, materially revising the ROI model.

**Mitigations:**
- Legal counsel quarterly review of applicable state insurance regulations through Month 12 [A11 validation path]
- ADR-4 routing decision and ADR-5 adjudication decision stored separately in CMS; physician sign-off can be inserted as a HITL step on denial decisions without re-architecting the routing logic
- Fast Path denial decisions are explicitly flagged in the audit trail as AI-generated; this audit trail is the compliance artifact required for any regulatory review
- If regulation requires physician sign-off on denials: add a denial-specific HITL step to ADR-5 (not ADR-4); does not affect the triage routing logic; ROI impact isolated to denial-specific throughput

---

### R-5: Shadow Mode Isolation Breach (ADR-4)

**Risk:** ADR-4 in Wave 1 must not affect live claim routing. If the application layer fails to validate the shadow mode constraint — or if the agent's output incorrectly sets `routing_mode: LIVE` — shadow classifications could be written to CMS as operative routing decisions, corrupting the processing queue.

**Probability:** Low — explicit isolation checks are designed in; but model hallucination on `routing_mode` output is a real edge case.

**Impact:** Critical — if FAST_PATH classifications from shadow mode are written to CMS, clinical claims bypass physician review. If CLINICAL_PATH shadow decisions are written, the physician queue is over-loaded with administrative claims. Either way, the integrity of the comparison dataset is destroyed.

**Mitigations:**
- Agent validates `routing_mode` matches deployment MODE before any output; if LLM returns LIVE when MODE=SHADOW, agent applies safe fallback (routes to CLINICAL_PATH) and logs `SHADOW_ISOLATION_VIOLATION` (test: EH-4A)
- MODE flag set at deployment, not at inference time — it is not in the user message and cannot be changed by the model's output
- Shadow-to-live switchover requires an explicit deployment step with a separate config change; cannot be triggered by a prompt modification
- Automated integration test: inject a mocked LLM response with `routing_mode: LIVE` in shadow mode; verify agent applies safe fallback, routes to CLINICAL_PATH, and alerts ops

---

## 6. Exit Criteria

### P0 — Must pass before any production claim processing begins

ADR-1:
- HP-1A and HP-1E pass (EDI parsing and duplicate detection correct)
- EH-1A passes (CMS API failure buffered without data loss)
- EH-4A equivalent for ADR-1: no CMS write on any error path that should hold a claim

ADR-4 (shadow mode launch):
- HP-4A and HP-4B pass (FAST_PATH and CLINICAL_PATH classified correctly in shadow mode)
- HP-4E passes (confidence fallback correctly routes to CLINICAL_PATH)
- EC-4A passes (novel case guardrail fires on unknown CPT code)
- EC-4B passes (empty codebook triggers universal CLINICAL_PATH, not silent miscategorization)
- EC-4C passes (HUMAN_REQUIRED claims route to CLINICAL_PATH with PRECONDITION_FAILED)
- EC-4E passes (shadow log failure does not corrupt classification)
- EH-4A passes (shadow isolation breach routes to CLINICAL_PATH with alert)
- EH-4C passes (malformed JSON routes to CLINICAL_PATH with OUTPUT_PARSE_FAILED)
- EH-4E passes (CMS write failure buffers without data corruption)

ADR-4 (Wave 2 live routing gate — [A6]):
- HP-4D passes: `labeled_entries ≥ 2,000` AND `false_negative_rate < 0.02` over 60-day shadow window
- All three stakeholders (CFO, CMO, VP Operations) sign the live routing authorization per the stakeholder alignment memo
- Legal counsel has confirmed AI adjudication permissibility in operating jurisdictions [A11]

### P1 — Must pass before Wave 1 scale-up (>10% of production volume)

- ≥90% of P1 tests pass
- ADR-1 EDI parsing accuracy ≥95% on a 200-claim calibration sample
- ADR-1 HITL rate ≤18% (must not exceed 20% or intake labor savings are eliminated)
- ADR-4 confidence fallback rate ≤15% (higher indicates codebook gaps [A15] must be addressed)
- Portal API rate limit backoff (EC-1E) confirmed with no claim loss in load test

### P2 — Should pass before steady-state operations (Month 6)

- EH-1B passes (IDP failure handled gracefully with HITL routing)
- EH-4D passes (codebook version mismatch prevents startup — deployment gate works)
- ADR-4 novel case rate <5% of daily volume (codebook coverage adequate)
- Monthly FN audit process (EH-4B) operationalized with Dr. Webb team
- Economic governance dashboard live and tracking cost per claim vs. budget

---

## 7. Validation Summary

### Results Table

| Test Group | Total Tests | P0 | P1 | P2 | Phase |
|------------|------------|----|----|----|----|
| ADR-1 Happy Path | 5 | 3 | 2 | 0 | Wave 1 pre-launch |
| ADR-1 Edge Cases | 5 | 1 | 4 | 0 | Wave 1 pre-launch |
| ADR-1 Error Handling | 5 | 2 | 3 | 0 | Wave 1 pre-launch |
| ADR-4 Happy Path | 5 | 5 | 0 | 0 | Wave 1 shadow / Wave 2 |
| ADR-4 Edge Cases | 5 | 4 | 1 | 0 | Wave 1 shadow |
| ADR-4 Error Handling | 5 | 4 | 1 | 0 | Wave 1 / Wave 2 |
| **Total** | **30** | **19** | **11** | **0** | — |

### Issues Table

| Issue ID | Description | Affected Tests | Severity | Owner | Resolution Path |
|----------|-------------|---------------|----------|-------|-----------------|
| ISS-01 | CMS API SLA and maintenance windows not yet confirmed | EH-1A, EH-4E | Critical | IT lead | Confirm in Week 1 IT discovery [A12] |
| ISS-02 | Portal API rate limit values not confirmed | EC-1E | High | IT lead | Confirm portal vendor rate limit specs before Wave 1 launch [A29] |
| ISS-03 | Dr. Webb adjudication team capacity not confirmed | HP-4D, EC-4A | High | CMO / Dr. Webb | Confirm max throughput (≤10 items/day assumed [A25]) before shadow mode begins |
| ISS-04 | Criteria codebook not yet drafted | EC-4B, EH-4D, all ADR-4 tests | Critical | Dr. Webb / FDE | Codebook must be co-developed and Dr. Webb-approved before any ADR-4 testing begins [A15] |
| ISS-05 | Legal review of AI adjudication permissibility pending | HP-4C (live mode) | High | Legal counsel | Required before Wave 2 launch [A11, U5] |
| ISS-06 | Shadow log store infrastructure not yet built | EC-4E, HP-4D | High | Triage dev lead | Build deliverable in Wave 1; must be available before shadow mode launches [A25] |

### Recommendation

**Do not launch any production processing until all P0 tests pass and ISS-04 (codebook) and ISS-01 (CMS API confirmation) are resolved.**

The validation sequence must follow strict ordering: criteria codebook first (required for all ADR-4 tests), then CMS API confirmation (required for all EH tests), then shadow mode launch (required for [A6] gate), then live mode activation only after the gate passes. Skipping any step or running ADR-4 tests before the codebook exists produces misleading results — the agent will classify all claims as NOVEL_CASE, which passes the test formally but validates nothing.

The [A6] gate (HP-4D) is the single most important test in this plan. It is the gating condition for the entire Fast Path economics: $845K/year in annual savings is locked behind this gate. The 60-day shadow window must begin as early as possible in Wave 1, which means ADR-1 intake must be operational first (ADR-4 requires `extraction_status = AUTO_COMPLETE` records to classify). Both agents' timelines are coupled.

---

*Assumptions added: [A29] — Portal API rate limit assumed 100 requests/minute until confirmed with portal vendor; [A30] — IDP pipeline failure rate alert threshold set at 5% over a 15-minute window (ops alert trigger); [A31] — NOVEL_CASE rate alert threshold set at 50% over a 5-minute window (empty codebook detection signal).*
