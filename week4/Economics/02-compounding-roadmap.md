# MedFlex Agentic Transformation — Compounding Roadmap

**Revision**: 2026-05-19  
**Scope**: JtD-1 through JtD-6; Waves 1–3; self-financing through Wave 2  
**Key principle**: Platform assets built for Wave 1 agents reduce Wave 2–3 build costs by ~$35K and eliminate the need for external Wave 2 funding.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Wave 1 — Foundation Agents (Weeks 1–8)](#2-wave-1--foundation-agents-weeks-18)
3. [Integration Reuse Matrix](#3-integration-reuse-matrix)
4. [Wave 2 — Compounding Agents (Months 3–12)](#4-wave-2--compounding-agents-months-312)
5. [Wave 3 — Multi-Agent Workflows (Year 2+)](#5-wave-3--multi-agent-workflows-year-2)
6. [Cumulative Value Summary](#6-cumulative-value-summary)
7. [Self-Financing Logic](#7-self-financing-logic)

---

## 1. Executive Summary

| | Wave 1 | Wave 2 | Wave 3 |
|---|---|---|---|
| **Timing** | Weeks 1–8 | Months 3–12 | Year 2+ |
| **Gross investment** | $120,000 | ~$85,000 | TBD |
| **Asset reuse reduction** | — | ~$35,000 | ~$15,000 est. |
| **Net investment** | $120,000 | ~$50,000 | — |
| **Annual labor saving added** | ~$346,000/year | +~$35,000/year | +~$37,000/year |
| **Payback** | ~3.8 months | Self-funded by month 8 | Funded by Wave 2 surplus |
| **Cumulative 3-year net value** | ~$918K (labor only) | +$105K incremental | ~$1.1M+ |
| **Key compounding mechanism** | JtD-1 assets ($16K) reduce all downstream Wave 1 builds | Wave 1 labor surplus + A19 corpus fund Wave 2 | ML ranker accuracy enables progressive auto-submit |

**Three findings that drive the compounding logic:**

1. **JtD-1 is the economic keystone.** Its 3.0-month payback and $10K/month surplus starting in month 4 offset JtD-3's slower 12-month labor-only payback. The $16K in reusable infrastructure it creates (ServiceNow auth, HITL Queue API, event bus, DLQ) is the single largest build-cost multiplier in Wave 1.

2. **The A19 feedback store is a data asset, not just a table.** Built in Wave 1 by JtD-3 from day one, the `u_ranker_feedback` store accumulates ~8,000–16,000 labeled match outcomes within 3 months of go-live. This corpus directly funds the Wave 2 ML ranker — eliminating a separate data-collection phase that would otherwise cost ~$20,000 to rebuild.

3. **Wave 2 is fully self-financed without M3 revenue.** Wave 1 labor savings of ~$173K by month 6 cover the $85K Wave 2 gross build cost by month 8, with ~$88K surplus remaining. M3 revenue recovery ($375K–$1.5M in Year 1 base/ceiling scenarios) is additive upside, not a requirement.

---

## 2. Wave 1 — Foundation Agents (Weeks 1–8)

### Wave 1 Portfolio Overview

| JtD | Agent Name | Weeks | Build Cost | Annual Labor Saving | Payback | Delegation Model |
|---|---|---|---|---|---|---|
| JtD-1 | Shift Intake Parser | 1–2 | $30,000 | $119,900 | 3.0 months | Agent-led + HITL (15%) |
| JtD-2 | Candidate Search & Evaluation | 2–4 | $45,000 | $119,350 | 4.5 months | Fully Agentic |
| JtD-3 | Match Selection | 3–6 | $60,000 | $60,288 + M3 | ~12 months (labor) / <2 months (with M3) | Agent-led + HITL (100% BP4) |
| JtD-4 | Submission | 7 | $15,000 | $40,020 | 4.5 months | Fully Agentic |
| JtD-5a | Monitoring & Notification | 8 | $15,000 | Indirect | Strategic | Fully Agentic |
| **Wave 1 Total** | | **Weeks 1–8** | **$120,000** | **~$346,000/year** | **~3.8 months** | |

Wave 1 total payback shortens from 4.2 months (without asset reuse) to 3.8 months because JtD-1's $16K in reusable assets reduces subsequent build costs before those agents are even started.

---

### JtD-1 — Shift Intake Parser (Weeks 1–2)

**Purpose**: Polls `u_shift_request` every 30 seconds; calls Claude Sonnet to extract specialty, datetime, location, and credentials from free-text hospital requests; routes high-confidence (≥0.85) to BP2 auto-proceed and low-confidence (<0.85) to BP1 human review.

**Wave 1 rationale**: First in the pipeline; unblocks all downstream agents; fastest payback in the portfolio ($30K build, 3.0-month payback); pure overhead replacement with no judgment risk.

**Key integrations built**:
- ServiceNow REST read client (auth + retry + rate limiting + circuit breaker, serving all agents that read `u_shift_request`)
- Anthropic API client + error-handling pattern (reused by JtD-3 Phase 2 LLM inference)
- Internal HITL Queue API write contract + schema (reused by JtD-3 BP4 coordinator review)
- Internal event bus trigger pattern (reused by JtD-2, JtD-3)
- Dead-letter queue + reconciliation cron infrastructure (reused by JtD-2, JtD-3, JtD-4)

**Shared assets created** (value to downstream Wave 1 agents):

| Asset | Downstream Beneficiary | Build Cost Reduction |
|---|---|---|
| ServiceNow REST read client | JtD-2, JtD-3 | ~$5,000 |
| Anthropic API pattern | JtD-3 Phase 2 | ~$2,000 |
| HITL Queue API | JtD-3 | ~$4,000 |
| Event bus pattern | JtD-2, JtD-3 | ~$2,000 |
| Dead-letter queue + reconciliation cron | JtD-2, JtD-3, JtD-4 | ~$3,000 |
| **JtD-1 total asset value** | | **~$16,000** |

**Economics**: $141,900/year baseline → $22,066/year agent operating cost → $119,834/year net saving. Token + tool costs = $0.015/case (3% of total); HITL = $0.463/case (97%). HITL rate reduction is the only meaningful cost lever.

---

### JtD-2 — Candidate Search & Evaluation (Weeks 2–4)

**Purpose**: Queries nurse profiles from `sys_user` against the `ParsedShiftRequirement` (locked end of Week 1); evaluates credential match, availability, and proximity; returns ranked candidate shortlist to JtD-3.

**Wave 1 rationale**: Fully agentic; no judgment required; builds the geocoding cache and nurse query layer that JtD-3 and JtD-6 reuse.

**Reuses from JtD-1**:
- ServiceNow REST read client (queries `sys_user` nurse profiles and `u_` tables)
- Event bus trigger pattern (receives `ParsedShiftRequirement` event; emits shortlist event)
- Dead-letter queue infrastructure (handles stale availability records — A17: 15–20% of queries)

**New integrations built**:
- Nurse profile DB query layer (filter by specialty, credentials, availability window)
- Google Maps Geocoding API integration with ZIP-level 24-hour cache (~920 raw proximity calculations/day → ~50 unique API calls/day after cache; saves ~$0.23/day at scale)
- Availability freshness check pattern (reactive re-queue on `AVAILABILITY_STALE` rather than pre-check — trade-off T3)
- Candidate evaluation scoring (pre-ranker; produces `u_shortlist_json` snapshot required by A28)

**Shared assets created** (value to downstream agents):

| Asset | Downstream Beneficiary | Build Cost Reduction |
|---|---|---|
| Nurse DB query layer | JtD-3 (ranker inputs), JtD-6 (emergency re-fill) | ~$5,000 |
| Geocoding cache layer | JtD-3 (proximity scoring), JtD-6 MT-6.4 | ~$5,000 |
| `u_shortlist_json` snapshot contract | JtD-3 (A28 feedback loop), JtD-4 (submission payload) | ~$3,000 |

**Economics**: ~$121,600/year baseline → ~$2,250/year agent cost (fully agentic, minimal HITL) → ~$119,350/year saving. $45K build; 4.5-month payback.

---

### JtD-3 — Match Selection / Ranker (Weeks 3–6)

**Purpose**: Applies rule-based ranker (A25 weights: credential 0.40 / availability 0.30 / proximity 0.20 / hospital preference 0.10) to shortlist from JtD-2; presents ranked candidates to coordinator for BP4 review; logs outcome to `u_ranker_feedback` for A19 corpus accumulation.

**Wave 1 rationale**: MVP is 100% HITL (coordinator approves every match); economics close via M3 revenue recovery ($375K–$1.5M Year 1) and throughput multiplier (~10× per coordinator vs. unassisted). A19 feedback accumulation from day one is a prerequisite for Wave 2 ML upgrade.

**Reuses from JtD-1**:
- ServiceNow REST read client (reads `u_shift_request`, nurse records)
- HITL Queue API (BP4 coordinator review uses the same HITL infrastructure)
- Event bus pattern (receives shortlist event from JtD-2; emits `MATCH_SELECTED` event to JtD-4)
- Dead-letter queue (handles BP5 rejections, re-rank events)

**Reuses from JtD-2**:
- Nurse DB query layer (ranker reads pre-fetched candidate attributes)
- Geocoding cache (proximity scoring uses cached ZIP-level distances)
- `u_shortlist_json` snapshot (A28: required field in `u_ranker_feedback` for ML training)

**New integrations built**:
- Rule-based ranker scoring engine (configurable weights, A25; not hardcoded)
- Coordinator review UI + RankerFeedback API (A27: records which candidate was selected, why, and any edits)
- `u_ranker_feedback` table schema + write client (A28: stores labeled match outcomes for A19 ML corpus)
- `u_pipeline_audit_log` schema + client (full end-to-end audit trail shared by all agents)
- ServiceNow write client (used jointly with JtD-4; provisions `u_shift_request` status updates)

**Shared assets created** (value to Wave 2 agents):

| Asset | Wave 2 Beneficiary | Build Cost Reduction |
|---|---|---|
| ServiceNow write client (shared with JtD-4) | JtD-6 MT-6.2, JtD-5b | ~$8,000 |
| Coordinator review UI + API | JtD-3 Phase 2 (ML ranker interface) | ~$10,000 |
| `u_pipeline_audit_log` client | All Wave 2 JtDs | ~$5,000 |
| A19 labeled feedback store (data value) | JtD-3 Phase 2 ML ranker training | ~$20,000 (data value) |

**Economics**: $101,360/year baseline → $41,072/year agent cost (100% HITL at 2 min/review) → $60,288/year labor saving. $60K build; 12-month payback (labor only) / <2-month payback (with M3 base case). KPI ceiling: ≤$0.90/case — MVP result $0.892 passes.

---

### JtD-4 — Submission (Week 7)

**Purpose**: Receives `MATCH_SELECTED` event from JtD-3; writes confirmed assignment back to ServiceNow (`u_shift_request` status = `FILLED`); emits to JtD-5a for confirmation notification. Fully agentic; no coordinator touchpoint.

**Wave 1 rationale**: Closes the revenue loop — a coordinator-approved match that is not submitted generates no revenue. At 184 fills/day, unsubmitted matches are the final failure mode before payment. Zero judgment required (coordinator has already approved); highest-certainty delegation.

**Reuses from JtD-1**:
- ServiceNow REST read client (reads match confirmation payload)
- Event bus pattern (receives `MATCH_SELECTED`; emits `SHIFT_FILLED`)
- Dead-letter queue (handles ServiceNow write failures; retry with exponential back-off)

**Reuses from JtD-3**:
- ServiceNow write client (provisions `FILLED` status write on `u_shift_request`)
- `u_pipeline_audit_log` client (records submission event for audit trail)

**New integrations built**:
- Submission idempotency guard (prevents double-submission on DLQ retry; uses `shift_request_id` as idempotency key)

**Economics**: ~$40,480/year baseline → ~$460/year agent cost (fully agentic, tool-only) → ~$40,020/year saving. $15K build; 4.5-month payback.

---

### JtD-5a — Monitoring & Notification (Week 8)

**Purpose**: Receives `SHIFT_FILLED` event; sends T-48h and T-24h confirmation notifications to nurse and hospital via SMS/email; records delivery status. Closes M4 (notification reliability tracking).

**Wave 1 rationale**: Lowest build cost in portfolio ($15K); indirect saving via no-show reduction (current no-show rate 12%, A9); required to close the shift lifecycle loop for audit compliance.

**Reuses from JtD-3/JtD-4**:
- `u_pipeline_audit_log` client (logs notification events)
- Event bus pattern (receives `SHIFT_FILLED` trigger)
- `u_ranker_feedback` outcome updates (A28: records shift outcome — show/no-show — for A19 corpus quality)

**New integrations built**:
- Notification sending adapter (SMS gateway + email; one-way only — bidirectional response capture is unresolved, U4, deferred)
- Notification status tracking table

**Note on U4 (unresolved)**: Bidirectional confirmation response capture (nurse replies "confirmed" via SMS) is not implemented in Wave 1. Wave 2 JtD-5b resolves the nurse-decline path; U4 may require a separate channel integration beyond SMS gateway.

---

## 3. Integration Reuse Matrix

The matrix below shows every platform asset built across the three waves, its category, which agents built and reuse it, and the build cost reduction it generates in each downstream wave.

**Categories:**
- **Integration** — external system connectors (ServiceNow, Anthropic API, Google Maps, SMS/email)
- **Infrastructure** — reliability and messaging patterns (event bus, DLQ, idempotency guard, HITL Queue)
- **Retrieval pipeline** — data fetching, caching, and structured data contracts (nurse query, geocoding, shortlist snapshot)
- **Scoring / AI** — model and scoring engines (rule-based ranker; Wave 2 ML ranker)
- **Governance** — audit, review UI, and feedback loops (coordinator UI, ranker feedback store, audit log)

| Category | Asset | Built By | Wave 1 Reused By | Wave 2 Reused By | Wave 2 Build Reduction | Wave 3 Reused By | Wave 3 Build Reduction |
|---|---|---|---|---|---|---|---|
| Integration | **ServiceNow REST read client** (auth, retry, rate limit, circuit breaker) | JtD-1 Week 1 | JtD-2, JtD-3 | JtD-6 MT-6.1, JtD-5b | ~$5,000 | Full pipeline orchestration; no-show recurrence check | ~$3,000 |
| Integration | **Anthropic API client** (error handling, timeout, retry) | JtD-1 Week 1 | — | JtD-3 Phase 2 (LLM inference) | ~$2,000 | JtD-3 Phase 3 (LLM-augmented auto-submit confidence) | ~$1,000 |
| Integration | **ServiceNow REST write client** (idempotency key, write retry) | JtD-3/JtD-4 Weeks 5–7 | JtD-4 (submission) | JtD-6 MT-6.2, JtD-5b | ~$8,000 | Auto-submit path (direct write without coordinator) | ~$0 (already fully built) |
| Integration | **Notification sending adapter** (SMS/email) | JtD-5a Week 8 | — | JtD-5b (decline notification), JtD-6 (no-show alert) | ~$5,000 | Extended for bidirectional response (U4 resolution) | ~$5,000 |
| Infrastructure | **HITL Queue API** (write contract + schema) | JtD-1 Week 2 | JtD-3 BP4 | JtD-6 (human escalation) | ~$4,000 | Retained for ~30% HITL band in auto-submit model | ~$0 (unchanged) |
| Infrastructure | **Event bus trigger pattern** | JtD-1 Week 2 | JtD-2, JtD-3, JtD-4 | JtD-5b, JtD-6 | ~$2,000 | End-to-end pipeline orchestration backbone | ~$3,000 |
| Infrastructure | **Dead-letter queue + reconciliation cron** | JtD-1 Week 2 | JtD-2, JtD-3, JtD-4 | JtD-5b, JtD-6 | ~$3,000 | Full pipeline reliability (no new config needed) | ~$0 (already amortized) |
| Infrastructure | **Submission idempotency guard** | JtD-4 Week 7 | — | JtD-6 (re-fill submission) | ~$3,000 | Auto-submit path uses same guard | ~$0 (already built) |
| Retrieval pipeline | **Nurse DB query layer** (specialty, credential, availability filters) | JtD-2 Weeks 2–4 | JtD-3 | JtD-6 MT-6.4 (emergency re-fill) | ~$5,000 | No-show risk scoring — filters high-risk nurses from shortlist | ~$3,000 |
| Retrieval pipeline | **Google Maps Geocoding cache** (ZIP-level, 24h TTL) | JtD-2 Weeks 2–4 | JtD-3 (proximity scoring) | JtD-6 MT-6.4 | ~$5,000 | JtD-6 emergency re-fill proximity re-rank (already active) | ~$0 (already active) |
| Retrieval pipeline | **`u_shortlist_json` snapshot contract** | JtD-2 Weeks 2–4 | JtD-3 (A28 payload), JtD-4 | JtD-3 Phase 2 ML training | ~$3,000 | Full-lifecycle cross-agent correlation and tracing | ~$2,000 |
| Scoring / AI | **Rule-based ranker scoring engine** (A25 configurable weights) | JtD-3 Weeks 3–5 | — | JtD-3 Phase 2 (starting point for ML replacement) | ~$10,000 | Calibration baseline and fallback for auto-submit threshold | ~$5,000 |
| Scoring / AI | **ML ranker model** (trained on A19 corpus) | JtD-3 Phase 2 (Wave 2) | — | — | — | Auto-submit confidence scoring; threshold tuning | ~$10,000 |
| Governance | **Coordinator review UI + RankerFeedback API** (A27) | JtD-3 Weeks 4–6 | — | JtD-3 Phase 2 (modified for ML ranker) | ~$10,000 | Auto-submit override UI and audit display | ~$8,000 |
| Governance | **`u_ranker_feedback` table + write client** (A28) | JtD-3 from Week 3 | — | JtD-3 Phase 2 ML training data | ~$20,000 (data value) | Continuous ML model retraining input (ongoing) | ~$0 (ongoing data) |
| Governance | **`u_pipeline_audit_log` schema + client** | JtD-3 Weeks 3–4 | JtD-4, JtD-5a | All Wave 2 JtDs | ~$5,000 | Cross-agent full-lifecycle tracing and compliance audit | ~$3,000 |

**Wave 1 direct build reduction** (Wave 2): ~$35,000  
**Wave 1 data asset value** (A19 corpus, not a direct build cost): ~$20,000  
**Wave 2 net investment after reuse**: ~$85,000 gross − ~$35,000 = **~$50,000 net**

**Wave 2 direct build reduction** (Wave 3): ~$32,000 est.  
**Wave 3 net investment**: lower than Wave 2; primarily configuration, threshold tuning, and U4 extension work

### 3.1 Simplified View

| Category | Asset | JtD-1 (W1) | JtD-2 (W1) | JtD-3 (W1) | JtD-4 (W1) | JtD-5a (W1) | JtD-3 Ph.2 (W2) | JtD-5b (W2) | JtD-6 (W2) | Wave 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| Integration | ServiceNow REST read client | ✓ Build | ✓ Reuse | ✓ Reuse | — | — | — | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| Integration | Anthropic API client | ✓ Build | — | — | — | — | ✓ Reuse | — | — | ✓ Reuse |
| Integration | ServiceNow REST write client | — | — | ✓ Build | ✓ Reuse | — | — | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| Integration | Notification sending adapter | — | — | — | — | ✓ Build | — | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| Infrastructure | HITL Queue API | ✓ Build | — | ✓ Reuse | — | — | — | — | ✓ Reuse | ✓ Reuse |
| Infrastructure | Event bus trigger pattern | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | — | ✓ Reuse | ✓ Reuse | ✓ Reuse |
| Infrastructure | Dead-letter queue + reconciliation cron | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | — | — | ✓ Reuse | ✓ Reuse | — |
| Infrastructure | Submission idempotency guard | — | — | — | ✓ Build | — | — | — | ✓ Reuse | ✓ Reuse |
| Retrieval pipeline | Nurse DB query layer | — | ✓ Build | ✓ Reuse | — | — | — | — | ✓ Reuse | ✓ Reuse |
| Retrieval pipeline | Google Maps Geocoding cache | — | ✓ Build | ✓ Reuse | — | — | — | — | ✓ Reuse | — |
| Retrieval pipeline | u_shortlist_json snapshot | — | ✓ Build | ✓ Reuse | ✓ Reuse | — | ✓ Reuse | — | — | ✓ Reuse |
| Scoring / AI | Rule-based ranker engine | — | — | ✓ Build | — | — | ✓ Reuse | — | — | ✓ Reuse |
| Scoring / AI | ML ranker model | — | — | — | — | — | ✓ Build | — | — | ✓ Reuse |
| Governance | Coordinator review UI + RankerFeedback API | — | — | ✓ Build | — | — | ✓ Reuse | — | — | ✓ Reuse |
| Governance | u_ranker_feedback (A28) | — | — | ✓ Build | — | ✓ Reuse | ✓ Reuse | — | — | ✓ Reuse |
| Governance | u_pipeline_audit_log | — | — | ✓ Build | ✓ Reuse | ✓ Reuse | — | ✓ Reuse | ✓ Reuse | ✓ Reuse |

---

## 4. Wave 2 — Compounding Agents (Months 3–12)

Wave 2 is fully self-financed from Wave 1 labor surplus by month 8 — no M3 revenue required. The $35K asset reuse reduction means Wave 2 gross build cost is ~$85K, net ~$50K. Wave 1 generates ~$173K in labor savings by month 6; after covering the $120K Wave 1 investment, ~$53K surplus is available. Months 7–8 savings close the remaining ~$32K funding gap.

### Wave 2 Portfolio Overview

| Component | Type | Trigger | Gross Build Cost | Asset Reuse | Net Cost | Incremental Annual Saving |
|---|---|---|---|---|---|---|
| JtD-3 Phase 2: ML Ranker | Agent upgrade | A19 ≥ 8,000 labeled examples | ~$30,000 | ~$30,000 (UI + data) | ~$0 | +$27,692/year |
| JtD-1 Phase 2: Prompt re-tuning | Capability improvement | ≥500 HUMAN_CORRECTED + HITL ≥12% for 2 weeks | ~$7,500 | — | ~$7,500 | +$7,100/year |
| JtD-5b: Decline & Conflict Resolution | New agent | Nurse-decline API available | ~$25,000 | ~$5,000 | ~$20,000 | TBD (indirect) |
| JtD-6: No-Show Management | New agent | Wave 1 surplus confirmed | ~$22,500 | ~$21,000 | ~$1,500 | TBD |
| **Wave 2 Total** | | | **~$85,000** | **~$56,000** | **~$29,000** | **+~$35,000/year** |

---

### JtD-3 Phase 2 — ML Ranker (Months 3–6, post A19 corpus threshold)

**Purpose**: Replace rule-based ranker (A25 hardcoded weights) with ML-trained model using `u_ranker_feedback` outcomes. Enables auto-submit for high-confidence matches (composite_score ≥ 0.90 AND editor edit rate < 10%) — reducing HITL from 100% to ≤30% (A30).

**Trigger conditions** (all four must be met before activation):
1. A19 corpus ≥ 8,000 labeled examples (at 184/day × 50% structured capture → ~3 months)
2. ML model accuracy ≥ coordinator baseline on holdout set
3. Coordinator edit rate ≤ 20% for 30 consecutive working days
4. Phase 2 dry-run cost ≤ $0.30/case

**Reuses from Wave 1**:
- `u_ranker_feedback` + `u_shortlist_json` (A28): training data — ~3 months of labeled outcomes eliminates a separate data-collection phase worth ~$20,000
- Coordinator review UI + RankerFeedback API (A27): modified for ML confidence display; existing UI frame reused
- Anthropic API client (JtD-1): used for LLM-augmented ranking inference in Phase 2 hot path (~$0.015/case LLM cost)
- Rule-based ranker scoring engine: starting point and fallback for ML model (cold-start guarantee)

**New work required**:
- ML model training pipeline (offline; feature engineering from `u_shortlist_json` snapshot fields)
- Auto-submit threshold logic and override UI
- Phase 2 dry-run harness

**Economics**:
- HITL drops from 100% to ≤30% (A30): saves $28,382/year additional HITL labor
- LLM inference adds $690/year
- Net uplift: **$27,692/year** incremental on top of Wave 1 JtD-3 saving
- Net cost to build: ~$0 (entirely funded by reused Wave 1 assets: $10K UI + $20K data = $30K offset against ~$30K build)

---

### JtD-1 Phase 2 — System Prompt Re-Tuning (Months 1–2, post trigger)

**Purpose**: Re-tune JtD-1 system prompt using accumulated `HUMAN_CORRECTED` examples to reduce HITL rate from ≤15% (A10) to ≤10% (A32). Targets highest-frequency BP1 failure modes: ambiguous location references, unknown specialty abbreviations, relative datetime expressions.

**Trigger conditions**:
1. ≥ 500 `HUMAN_CORRECTED` entries in HITL queue
2. HITL rate ≥ 12% (stable) for 2 consecutive weeks
3. Expected timing: 4–6 weeks post-launch at 15% × 184/day × 20 production days = 750–1,100 examples

**Work required**: ~1–2 FDE engineer-weeks to identify top-5 failure modes, update few-shot examples in system prompt, re-validate against 200-record corpus. No ML required.

**Economics**:
- HITL cost per case: $0.463 → $0.308 (15% → 10% HITL rate, A32)
- Annual additional saving: **$7,100/year**
- Build cost: ~$7,500 at A21 rates (~1.5 FDE engineer-weeks)
- Payback: ~13 months

**Confidence caveat (A32)**: Medium. If production HITL failures are concentrated in genuinely ambiguous requests (multi-nurse submissions, missing hospital location data) rather than prompt-addressable patterns, the Wave 2 T2 structured intake template may be required to reach 10% rather than prompt tuning alone.

---

### JtD-5b — Decline & Multi-Agency Conflict Resolution (Month 4–6)

**Purpose**: Handles nurse-decline events (MT-5.3) and multi-agency submission conflicts (MT-5.4). Currently Human-led + Agent Support. Wave 2 target: automate conflict detection; escalate decline path to structured re-nomination.

**Deferred from Wave 1 because**: Nurse-decline API not available (U4: bidirectional response capture unresolved). Wave 2 depends on JtD-5a notification adapter (built Wave 1) being extended with inbound response parsing.

**Reuses from Wave 1**:
- Notification sending adapter (JtD-5a): extended for decline response parsing
- ServiceNow write client (JtD-3/JtD-4): records conflict resolution outcome
- Event bus pattern (JtD-1): receives `NURSE_DECLINED` trigger
- HITL Queue API (JtD-1): routes unresolvable conflicts to human escalation

---

### JtD-6 — No-Show Management (Month 6–9)

**Purpose**: Detects confirmed no-shows (12% of fills, A9); triggers emergency re-fill via JtD-2 shortlist re-run; notifies hospital. Currently Human-led + Automation Support; Wave 2 target: automated re-fill for ≥70% of no-show events.

**Deferred from Wave 1 because**: Phone-based intake for last-minute hospital changes is not automatable in Wave 1. Emergency re-fill window is 0–4 hours; requires geocoding-based proximity re-ranking against the original shortlist.

**Reuses from Wave 1** (highest asset reuse ratio in Wave 2):
- ServiceNow read + write clients (JtD-1/JtD-4): read original `u_shift_request`; write re-fill outcome
- Nurse DB query layer + geocoding cache (JtD-2): re-run proximity-sorted shortlist within emergency window
- Event bus + DLQ (JtD-1): receive `NO_SHOW_DETECTED` trigger; handle re-fill retry
- Notification adapter (JtD-5a): alert hospital on replacement nurse dispatch
- `u_pipeline_audit_log` client (JtD-3): record no-show event for outcome tracking
- Submission idempotency guard (JtD-4): prevent duplicate re-fill submissions

**Net cost**: ~$22,500 gross − ~$21,000 reuse = **~$1,500 net** (primarily integration configuration and no-show detection logic)

---

## 5. Wave 3 — Multi-Agent Workflows (Year 2+)

### Progressive Auto-Submit — JtD-3 Phase 3

**Purpose**: Remove coordinator touchpoint for the highest-confidence match band (~70% of volume), reducing HITL from ≤30% (Wave 2) to near-zero for auto-submit-eligible cases. Retains human oversight for the remaining ~30% (borderline, escalations, multi-agency conflict cases).

**Trigger**: ML ranker accuracy ≥ coordinator baseline on holdout set AND composite_score ≥ 0.90 AND coordinator edit rate < 10% (measured over 30 consecutive working days post-Wave 2 launch).

**Orchestration pattern**: Event-driven pipeline with confidence-gated branching:
```
JtD-1 (ParsedShiftRequirement) 
  → JtD-2 (ranked shortlist)
  → JtD-3 Phase 3:
      composite_score ≥ 0.90 → BP2 auto-submit path → JtD-4 (direct submission)
      composite_score < 0.90 → BP4 coordinator review → JtD-4 (post-approval submission)
  → JtD-4 (Submission)
  → JtD-5a (Notification)
```

**Economics**:
| | Per Case | Annual (46K cases) |
|---|---|---|
| Auto-submit band (70%, no HITL) | ~$0.026 | ~$1,196/year |
| HITL band (30%, 2-min review) | ~$0.290 | ~$4,002/year |
| Blended cost | ~$0.105 | ~$4,830/year |
| Baseline (pre-agentic) | $2.20 | $101,360/year |
| **Annual saving vs. baseline** | | **~$96,530/year** |
| **ROI on $60K JtD-3 investment** | | **~1,609%** |

**Volume scaling** (at $200M revenue target, 25% market share: ~667 fills/day):
- Annual cases: ~167,000
- Blended agent cost at scale: 167,000 × $0.105 = ~$17,535/year
- Baseline at scale (112 coordinators): ~$367,400/year
- Annual saving at scale: ~$349,865/year
- Headcount scaling cost eliminated: 104 additional coordinators × $55K = **$5.72M/year** that does not need to be hired

### Full Pipeline Orchestration — End-to-End

**Workflow**: Full shift lifecycle from intake to post-shift outcome tracking, with no human touchpoint for routine cases.

**Agents involved**: JtD-1 → JtD-2 → JtD-3 → JtD-4 → JtD-5a → (JtD-5b if decline) → (JtD-6 if no-show)

**Orchestration pattern**: Event-driven with dead-letter queue fallback at each handoff; audit trail via `u_pipeline_audit_log`; HITL escalation at three gates (BP1: intake exception; BP4/BP2: match selection; BP5: post-approval conflict).

**Wave 3 new capabilities required**:
- Bidirectional nurse response capture (U4 resolution: SMS reply parsing or app confirmation)
- Cross-agent correlation (link `shift_request_id` across all pipeline events for full-lifecycle tracing)
- No-show recurrence scoring (flag nurses with >2 no-shows in rolling 30 days before JtD-3 shortlist inclusion)

---

## 6. Cumulative Value Summary

| Period | Investment | Annual Labor Saving | M3 Revenue Upside | Cumulative 3-Year Net |
|---|---|---|---|---|
| Wave 1 (Months 0–8) | $120,000 | ~$346,000/year | $375K–$1.5M (base/ceiling) | ~$918K (labor only) |
| Wave 2 (Months 3–12) | ~$50,000 net | +~$35,000/year incremental | Throughput upside | +~$105K incremental |
| Wave 3 (Year 2+) | Funded by Wave 2 surplus | +~$37,000/year incremental | Full auto-submit potential | ~$1.1M+ total |

**Sensitivity check**: All three waves generate positive ROI even in the conservative scenario (A5=0%, no M3 revenue recovery, +50% token costs). The business case rests on labor savings alone for Wave 1. M3 revenue recovery is significant upside but not a requirement for Wave 2 funding.

---

## 7. Self-Financing Logic

The compounding logic runs in three steps:

### Step 1 — JtD-1 Reduces All Wave 1 Build Costs ($16K reduction, Week 1)

JtD-1 is built first (Weeks 1–2). The ServiceNow read client, HITL Queue API, event bus, and DLQ it creates are immediately available to JtD-2 (Weeks 2–4) and JtD-3 (Weeks 3–6). Each subsequent Wave 1 agent does not rebuild these foundations. Net effect: Wave 1 effective build cost drops from a hypothetical ~$136K (without reuse) to $120K — shortening portfolio payback from 4.2 to 3.8 months.

### Step 2 — Wave 1 Labor Surplus Funds Wave 2 ($173K surplus by month 6)

```
Wave 1 monthly labor saving:    ~$28,833/month (~$346K/year ÷ 12)
Wave 1 build cost:              $120,000
Months to payback:              ~3.8 months

Accumulated labor saving by month 6:  ~$173,000
  − Wave 1 build cost:                $120,000
  = Wave 1 surplus by month 6:         ~$53,000

Wave 2 gross build cost:        ~$85,000
Wave 2 asset reuse reduction:  ~$35,000
Wave 2 net cost:                ~$50,000

Wave 2 funding from month 6 surplus:  $53,000 (covers $50K net cost with $3K remaining)
Full Wave 2 self-financed by:         Month 8 (months 7–8 savings close any shortfall)
M3 revenue requirement for Wave 2:   NONE
```

### Step 3 — A19 Feedback Store Eliminates Wave 2 Data Collection Phase ($20K data value)

JtD-3 begins writing to `u_ranker_feedback` (A28) from day one of Wave 1 go-live. By month 3, the corpus reaches 8,000–11,000 labeled match outcomes (184/day × 50% structured capture × ~90 working days = ~8,280 examples). This corpus is the direct training input for the Wave 2 ML ranker. Without this asset, Wave 2 would require a separate 3-month data-collection phase costing ~$20,000 in FDE time — a phase that is eliminated entirely because JtD-3 builds the feedback infrastructure from the start.

Combined effect: Wave 2 effective cost drops from ~$85K gross to ~$30K net (after $35K direct build reduction + $20K data value).

### Step 4 — Wave 2 Surplus + Asset Reuse Self-Finances Wave 3 (~$8K net cost)

```
Combined Wave 1+2 monthly saving:  ~$31,750/month (~$381K/year ÷ 12)
Net position at month 12 (Wave 2 fully operational):  +$176,000

Wave 3 gross build cost:            ~$40,000 est.
  (auto-submit threshold logic, U4 bidirectional response,
   no-show recurrence scoring, cross-agent correlation)
Wave 3 asset reuse reduction:       ~$32,000
  (ML ranker model, coordinator UI, governance assets — see §3)
Wave 3 net cost:                    ~$8,000

Wave 3 funding:                     Covered entirely by months 13–14 surplus
M3 revenue requirement for Wave 3:  NONE
```

The compounding effect is most visible here: Wave 3's ~$40K gross build cost is almost entirely offset by reusing Wave 2 assets (ML ranker, coordinator UI, governance layer), leaving a ~$8K net cost that the accumulated surplus covers within 9 days of combined Wave 1+2 operation. The primary Wave 3 investment is therefore **time** (threshold calibration, U4 integration, auto-submit dry-run) rather than money.

Wave 3 adds ~$8,510/year incremental saving for JtD-3 (auto-submit band drops per-case cost from $0.290 to $0.105 for 70% of volume), with further upside from JtD-5b and JtD-6 stabilising the no-show and decline paths.

### Monthly Cash Flow Summary

| Month | Event | Cumulative Investment | Cumulative Saving | Net Position |
|---|---|---|---|---|
| 0 | Wave 1 engagement starts | $0 | $0 | $0 |
| 2 | JtD-1 + JtD-2 live | $75,000 | $28,833 | −$46,167 |
| 4 | JtD-3 + JtD-4 live | $120,000 | $86,500 | −$33,500 |
| 6 | Wave 1 fully operational | $120,000 | $173,000 | **+$53,000** |
| 8 | Wave 2 net cost covered | $170,000 | $229,667 | **+$59,667** |
| 12 | Wave 2 fully operational | $170,000 | $346,000 | **+$176,000** |
| 14 | Wave 3 net cost covered (~$8K from surplus) | $178,000 | $409,500 | **+$231,500** |
| 18 | Wave 3 fully operational (auto-submit live) | $178,000 | $536,250 | **+$358,250** |
| 24 | Year 2 end | ~$178,000 | ~$727,250 | **+~$549,250** |
| 36 | Year 3 end | ~$178,000 | ~$1,108,250 | **+~$930,250** |

Figures above are labor savings only. M3 revenue recovery ($375K–$1.5M in Year 1 base/ceiling scenarios) is not included and shifts the net position decisively positive by month 6 in the base case.
