# CLAUDE.md

This file configures Claude Code's behavior when building the AI Claims Processing Transformation agents for Greenfield Health Systems.

---

## Project Purpose

Dual-path claims processing transformation: AI adjudicates routine administrative claims end-to-end (Fast Path, ~65% of volume) and pre-screens clinical claims so physicians review summaries, not full files (Clinical Path, ~35%). Wave 1 delivers ADR-1 (Claim Intake) and ADR-4 (Clinical Triage in shadow mode). Success requires cycle time ≤7 days on both paths, ADR-4 false-negative rate <2%, and 8 FTE admin reduction confirmed within 6 months.

**Key entities**: `NormalizedClaimRecord` (CMS system of record), `RoutingDecision` (FAST_PATH / CLINICAL_PATH), `ExtractionResult` (per-field confidence), `ShadowLog` (ADR-4 triage decision + ground truth for [A6] gate).

**For problem context, quantified baselines, and success metrics, see `specs/01-problem-framing.md`.**

---

## Repository Structure

```
capstone/
├── specs/
│   ├── CLAUDE.md                         # This file
│   ├── 01-problem-framing.md             # Problem statement, success metrics, critical unknowns
│   ├── 02-cognitive-load-map.md          # Process map and cognitive load analysis
│   ├── 03-delegation-matrix.md           # Delegation suitability per ADR (ADR-1 through ADR-9)
│   ├── 05-adrs.md                        # Architecture Decision Records (all 9 ADRs)
│   ├── 06a-capability-spec-intake.md     # ADR-1 full spec (entity models, contracts, system prompt)
│   ├── 06b-capability-spec-triage.md     # ADR-4 full spec (codebook, shadow mode, [A6] gate)
│   ├── 08-economics.md                   # Token economics, ROI, self-financing roadmap
│   ├── 09-validation-plan.md             # 30-test validation plan (P0/P1/P2 exit criteria)
│   ├── 10-stakeholder-memo.md            # Stakeholder alignment memo
│   └── assumptions.md                    # Assumptions register (A1–A31) with confidence levels
├── input-docs/
│   ├── scenario.md                       # Client scenario (Greenfield Health Systems)
│   ├── the-fde.md                        # FDE role definition
│   └── atx/                              # ATX methodology reference docs
```

**Authoritative specs**:
- Entity definitions, state machines, integration contracts: `specs/06a-capability-spec-intake.md` (ADR-1) and `specs/06b-capability-spec-triage.md` (ADR-4)
- All assumptions with confidence levels and validation owners: `specs/assumptions.md`
- Delegation decisions (archetypes, suitability scores): `specs/03-delegation-matrix.md` + `specs/05-adrs.md`

---

## Scope: What You SHOULD Build

**Wave 1 — currently in spec (build these):**

1. **ADR-1: Claim Intake and Format Validation Agent**
   - EDI 837P/I parser → `NormalizedClaimRecord` (fully agentic, no HITL)
   - IDP extraction pipeline for non-EDI channels (CMS-1500 PDF, fax PDF, email, FHIR R4, portal JSON)
   - Per-field confidence scoring; HITL routing when required field confidence < 0.85
   - Duplicate detection (`PENDING_DUPLICATE`), exception note annotation routing (`EXCEPTION_NOTE`)
   - CMS API write with idempotency key + local buffer on failure [A12]
   - For full activity catalog, autonomy matrix, and integration contracts: `specs/06a-capability-spec-intake.md`

2. **ADR-4: Clinical Content Triage Agent**
   - Codebook-based classification → `FAST_PATH` or `CLINICAL_PATH` using CoT reasoning
   - Shadow mode only in Wave 1: writes to shadow log, does NOT write routing decisions to CMS
   - [A6] gate logic: query shadow log store for `false_negative_rate`; block Wave 2 live routing until <2% over ≥2,000 labeled examples over 60 days
   - `NOVEL_CASE` guardrail: unmatched CPT/ICD-10 → `CLINICAL_PATH`, confidence=0.0, flag for Dr. Webb
   - Confidence fallback: confidence < 0.70 → override to `CLINICAL_PATH`
   - For full spec, system prompt template, and shadow log endpoints: `specs/06b-capability-spec-triage.md`

3. **Shadow log store** — data substrate for [A6] gate; must be built in Wave 1 alongside ADR-4

4. **Economics model** — token cost, ROI, self-financing roadmap: `specs/08-economics.md`

5. **Validation plan** — 30-test plan with P0/P1/P2 exit criteria: `specs/09-validation-plan.md`

---

## Out of Scope: What You Should NOT Build

- **ADR-2** (Member/Provider Eligibility Verification) — deferred; unified eligibility API not confirmed [A12]
- **ADR-3** (Coding and Compliance Validation) — Wave 2; rules engine not AI
- **ADR-5** (Fast Path Administrative Adjudication) — conditional on ADR-4 [A6] gate passing
- **ADR-6** (Clinical Pre-Screening Summary) — Wave 2; requires ADR-4 live routing
- **ADR-7** (Physician Clinical Review) — Human Only by CMO mandate; no AI decision-making
- **ADR-8** (Payment Determination) — Wave 3; agent triggers existing payment engine, does not replicate it
- **ADR-9** (Denial Communication and Appeal Management) — Wave 3; requires [A11] legal clearance
- **Never write routing decisions to CMS in shadow mode** — application layer must validate `routing_mode` before any CMS write
- **Never implement ADR-5 adjudication or ADR-8 payment** until [A6] gate passes and Wave 2 is approved
- **Never use self-hosted inference** unless data-sovereignty or volume-amortisation case is explicitly made (see `specs/08-economics.md` §Self-hosted)

---

## Critical Guard Rails

### Shadow Mode Isolation (ADR-4) — BLOCKING
```
MODE is set at deployment config, not at inference time.
If MODE=SHADOW: application layer MUST validate routing_mode == "SHADOW" before any CMS write.
If agent outputs routing_mode=LIVE while MODE=SHADOW: block write, emit SHADOW_ISOLATION_VIOLATION event, alert ops.
Switching to LIVE requires explicit deployment config change — not a prompt change.
```

### [A6] False-Negative Gate — BLOCKING before Wave 2
```
Do NOT enable live routing (ADR-5, ADR-6) until:
  shadow_log.false_negative_rate < 0.02
  AND shadow_log.labeled_entries >= 2000
  AND window >= 60 days
  AND three-stakeholder sign-off (Dr. Webb, CMO, legal)
```

### NOVEL_CASE Guardrail (ADR-4) — ALWAYS
```
If no codebook provision matches claim codes:
  routing_decision = "CLINICAL_PATH"
  confidence = 0.0
  criteria_provisions_matched = ["NOVEL_CASE"]
  Emit NOVEL_CASE_FLAGGED event for Dr. Webb adjudication queue
```

### Confidence Fallback (ADR-4) — ALWAYS
```
If confidence < 0.70 after classification:
  Override routing_decision = "CLINICAL_PATH"
  Set confidence_fallback = true
  Emit ROUTING_FALLBACK_APPLIED event
```

### Codebook Version Mismatch (ADR-4) — BLOCKING
```
At agent startup: compare system prompt codebook version vs. deployed codebook version.
If mismatch: halt agent, emit CODEBOOK_VERSION_MISMATCH alert, do not process any claims.
Dr. Webb must approve each codebook revision before system prompt update.
```

### CMS API Failure [A12] — BUFFERING REQUIRED
```
On CMS API 503/timeout:
  Buffer claim locally with idempotency key
  Retry with exponential backoff (3 retries max)
  Alert ops after 3 failed retries
  Never drop a claim — no data loss under any failure mode
```

---

## Escalation Triggers

**ADR-1 → Exception Queue (human re-key):**
- Any required field extraction confidence < 0.85 on non-EDI claim → `HUMAN_REQUIRED`
- IDP pipeline timeout or empty extraction → `HUMAN_REQUIRED`, ops alert if >5% rate over 15-min window [A30]
- Duplicate claim detected → `PENDING_DUPLICATE`, no new CMS record

**ADR-1 → Ops Alert:**
- CMS API 3 consecutive failures → ops alert + buffer locally
- IDP failure rate > 5% over 15 minutes [A30]
- Portal API persistent 429 after backoff exhausted [A29]

**ADR-4 → Clinical Path (patient safety fallback — always err clinical):**
- Novel CPT/ICD-10 code not in codebook → `NOVEL_CASE_FLAGGED` to Dr. Webb
- Confidence < 0.70 after classification → `ROUTING_FALLBACK_APPLIED`
- Malformed JSON output → conservative fallback to `CLINICAL_PATH`
- Precondition failure: claim enters triage queue with `extraction_status != AUTO_COMPLETE` → return to intake queue

**ADR-4 → Ops Alert:**
- NOVEL_CASE rate > 50% over any 5-minute window (indicates missing/empty codebook) [A31]
- Shadow log write failure → buffer locally, emit `SHADOW_LOG_WRITE_FAILED`
- Shadow isolation violation → emit `SHADOW_ISOLATION_VIOLATION`, block write, alert ops

**For full autonomy matrix and escalation logic, see:**
- ADR-1: `specs/06a-capability-spec-intake.md` Section 4 (Autonomy Matrix)
- ADR-4: `specs/06b-capability-spec-triage.md` Section 4 (Autonomy Matrix)

---

## Integration Constraints

**CMS API [A12] — PRIMARY DEPENDENCY (unconfirmed)**
- Write: `POST /api/v1/claims` (ADR-1 normalized record), `PUT /api/v1/claims/{claim_id}/routing` (ADR-4 LIVE only)
- Read: `GET /api/v1/claims/{claim_id}` (duplicate check)
- Authentication: confirm in Week 1 IT discovery
- Failure handling: local buffer + idempotency key + retry + ops alert (see §Critical Guard Rails)
- **CRITICAL**: API SLA unconfirmed [A12]. Week 1 Go/No-Go validation required. If SLA <99.5%, negotiate batch-file fallback with IT.

**IDP Pipeline [A14] — Wave 1 Build (~$35K)**
- Not currently in place; must be built for non-EDI path (CMS-1500 PDF, fax PDF, email, FHIR R4)
- Per-field confidence scores required; confidence threshold: 0.85 (0.80 for pre-OCR'd text)
- Timeout handling: on IDP failure → route to `HUMAN_REQUIRED`, do not drop claim

**Portal API [A29]**
- Rate limit: ~100 requests/minute (assumed; confirm in Week 1) [A29]
- On HTTP 429: exponential backoff; preserve `received_at` timestamp for SLA anchoring
- SLA timer anchors to original `received_at`, not to processing completion

**Shadow Log Store [A25] — Wave 1 Build**
- Endpoints: `POST /api/v1/shadow-log` (write classification), `GET /api/v1/shadow-log/metrics` ([A6] gate query)
- Write failure must NOT block classification — buffer locally, emit `SHADOW_LOG_WRITE_FAILED`
- Must be operational before ADR-4 shadow mode begins

**For full endpoint specs, authentication, and fallback logic, see:**
- `specs/06a-capability-spec-intake.md` Section 5 (System and Data Inventory) and Section 8 (Integration Contracts)
- `specs/06b-capability-spec-triage.md` Section 5 (System and Data Inventory)

---

## Naming Conventions

- **extraction_status values**: `AUTO_COMPLETE`, `HUMAN_REQUIRED`, `PENDING_DUPLICATE`, `EXCEPTION_NOTE`
- **routing_decision values**: `FAST_PATH`, `CLINICAL_PATH`
- **routing_mode values**: `SHADOW`, `LIVE`
- **Event names**: SCREAMING_SNAKE_CASE (`AUDIT_EVENT_WRITTEN`, `NOVEL_CASE_FLAGGED`, `ROUTING_FALLBACK_APPLIED`, `SHADOW_ISOLATION_VIOLATION`, `CODEBOOK_VERSION_MISMATCH`)
- **Field names**: snake_case (`claim_id`, `member_id`, `received_at`, `confidence_score`, `criteria_provisions_matched`)
- **Claim formats**: EDI 837P (professional), EDI 837I (institutional), FHIR R4, portal JSON, CMS-1500 PDF
- **Confidence thresholds**: 0.85 standard (0.80 for pre-OCR'd text), 0.70 ADR-4 fallback trigger
- **Timestamps**: ISO 8601 with timezone; `received_at` is immutable after ingestion — preserve regardless of processing delays

---

## When to Ask vs When to Decide

**Decide alone** (do not ask):
- Route non-EDI claim to `HUMAN_REQUIRED` when any required field confidence < 0.85
- Apply `NOVEL_CASE` guardrail when no codebook provision matches
- Override to `CLINICAL_PATH` when confidence < 0.70
- Block CMS write when `routing_mode=SHADOW`
- Buffer locally on CMS API failure and retry
- Emit all audit events and ops alerts per spec

**Ask the user before proceeding**:
- CMS API SLA or authentication method unknown after Week 1 IT discovery sprint
- Codebook content (Dr. Webb must provide and approve — do not infer clinical criteria)
- Requests to bypass confidence thresholds or shadow mode isolation
- [A6] gate parameters — do not adjust false-negative threshold without stakeholder sign-off
- Any modification to `routing_decision` logic that affects patient safety

**Never ask — always apply guard rail**:
- "Should I write to CMS in shadow mode?" → NO. Always block.
- "Should I route to FAST_PATH when confidence is 0.65?" → NO. Always fallback to CLINICAL_PATH.
- "Should I continue processing if codebook version mismatches?" → NO. Always halt.

---

## Assumptions & Risks

**Critical assumptions** (see `specs/assumptions.md` for full register A1–A31):

| ID | Assumption | Confidence | Risk if wrong |
|----|-----------|-----------|---------------|
| [A2] | 35% clinical / 65% admin split | Medium (60%) | ADR-4 false-negative rate rises; financial case erodes |
| [A6] | ADR-4 false-negative rate achievable < 2% | Medium (65%) | Wave 2 blocked indefinitely; dual-path case collapses |
| [A7] | 70% EDI / 30% non-EDI channel split | Medium (65%) | HITL rate and IDP build scope both shift |
| [A11] | AI-generated denials legally permissible | Low (50%) | ADR-5 and ADR-9 blocked; requires legal clearance before Wave 2 |
| [A12] | CMS API available and documented | Low (45%) | ADR-1 and ADR-4 both blocked; entire architecture depends on this |
| [A14] | IDP pipeline buildable within Wave 1 scope | Medium (60%) | Non-EDI path stays manual; $117K/year saving delayed |
| [A15] | Clinical criteria codebook can be documented | Medium (55%) | ADR-4 classification meaningless; [A6] gate unmeasurable |
| [A29] | Portal API rate limit ~100 req/min | Low (40%) | Burst ingestion causes claim loss if not handled |

**Week 1 Go/No-Go validations required** (block Phase 1 if unresolved):
- [A12] CMS API: confirm availability, authentication, and SLA
- [A15] Codebook: confirm Dr. Webb can draft criteria before Wave 1 shadow mode begins
- [A11] Legal: confirm AI-generated denial permissibility before Wave 2 scoping

**For full assumption entries, validation owners, and contingency plans, see `specs/assumptions.md`.**

---

## Document Control

- **Version**: 1.0
- **Created**: 2026-05-27
- **Owner**: FDE Engagement Lead
- **Active specs**: ADR-1 (`specs/06a-capability-spec-intake.md`), ADR-4 (`specs/06b-capability-spec-triage.md`)
- **Next milestone**: Week 1 IT discovery — validate [A12], [A15], [A11] before Wave 1 build begins
