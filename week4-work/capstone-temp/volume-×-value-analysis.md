# Volume × Value Analysis
## Candidate Prioritization — Greenfield Health Systems AI Claims Processing

**Project:** Greenfield Health Systems — AI Claims Processing Transformation  
**Prepared by:** FDE Engagement Lead  
**Date:** 2026-05-21  
**Inputs:** `specs/cognitive-load-map.md`, `specs/03-agentic-solution-architecture.md`  
**Status:** Active — preliminary scoring subject to Phase 1 validation data

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Step 1: Suitability Gating](#2-step-1-suitability-gating)
3. [Step 2: Volume × Value Scoring](#3-step-2-volume--value-scoring)
4. [Step 3: Total Cost of Ownership Assessment](#4-step-3-total-cost-of-ownership-assessment)
5. [Step 4: Feasibility Scoring Matrix](#5-step-4-feasibility-scoring-matrix)
6. [Step 5: Strategic Sequencing](#6-step-5-strategic-sequencing)
7. [Prioritized Candidate Shortlist](#7-prioritized-candidate-shortlist)
8. [Implementation Sequencing Logic](#8-implementation-sequencing-logic)
9. [Assumptions Referenced](#9-assumptions-referenced)

---

## 1. Executive Summary

Eight of nine ADRs pass the suitability gate in some form; ADR-7 (Physician Clinical Review) is eliminated as Human Only by CMO mandate and consistent with the delegation suitability analysis. The remaining eight divide into two priority tiers:

**Tier 1 — Primary agentic targets** (value score ≥ 15): ADR-4 Clinical Triage (25), ADR-6 Clinical Pre-Screening (16), ADR-5 Fast Path Adjudication (15). These sit in the top-right quadrant — high volume, high non-determinism — where agent reasoning creates irreplaceable value. ADR-4 and ADR-5 together constitute the entire Fast Path financial case; ADR-6 is the enabling capability for the Clinical Path.

**Tier 2 — Rules/automation candidates** (value score 8–14): ADR-1 Intake (10), ADR-2 Eligibility (10), ADR-3 Coding (10), ADR-9 Denial/Appeals (12). These sit top-left — high volume, low non-determinism — where rules engines, API integrations, or lightweight automation deliver better economics than LLM agents. ADR-3 and ADR-8 (score: 5) are anti-pattern catches: rules lookup and arithmetic, not LLM problems.

Three implementation waves are recommended:

- **Wave 1** (Phase 1, Months 1–3): ADR-8, ADR-3, ADR-1 — platform foundation + immediate savings + fund Wave 2
- **Wave 2** (Phase 2, Months 4–6): ADR-2, ADR-5, ADR-6 — main value delivery; SLA restoration and Fast/Clinical Path launch
- **Wave 3** (Phase 3, Month 7+): ADR-4, ADR-9 (denial letters) — AI-native operations, conditional on Phase 1 [A6] gate and [A11] legal clearance

Combined Year 1 savings from the admin automation stack are estimated at **$604K** against a **$400K** build budget — Year 1 ROI of **51%**, payback in **8 months**. Penalty avoidance [A8] is additive and not included in the base case; including it would materially strengthen the ROI. The financial case closes if [A6], [A11], and [A12] resolve favorably.

---

## 2. Step 1: Suitability Gating

**Gate criteria** (from ATX scoring guidance): at least Medium suitability on Input Structure, Decision Determinism, and Tool Coverage; no hard blocks on Risk/Compliance.

| ADR | Description | Input Struct | Decision Determ | Tool Coverage | Compliance Block | **Gate Result** |
|-----|-------------|:-----------:|:---------------:|:-------------:|:----------------:|:--------------|
| ADR-1 | Claim Intake & Format Validation | M | H | M | None | **Pass** — conditional on PDF extraction pipeline |
| ADR-2 | Eligibility Verification | M | H | L | None | **Conditional** — blocked on [A12] unified eligibility API |
| ADR-3 | Coding & Compliance Validation | H | H | H | None | **Pass** — anti-pattern: use rules engine for deterministic sub-tasks |
| ADR-4 | Clinical Content Triage | L | L | L | Patient safety [A6] | **Conditional** — gated on Phase 1 false-negative threshold |
| ADR-5 | Fast Path Adjudication | H | H | M | [A11] legal uncertainty | **Conditional** — approvals pass; denials gated on [A11] |
| ADR-6 | Clinical Pre-Screening | L | M | M | None | **Conditional** — requires [A15] criteria and [A20] portal |
| ADR-7 | Physician Clinical Review | M | L | M | CMO mandate | **Fail — Human Only** |
| ADR-8 | Payment & EOB Generation | H | H | H | None | **Pass** — anti-pattern: trigger existing payment engine |
| ADR-9 | Denial Communication & Appeals | M | L | M | [A19] deadlines | **Conditional** — MT-9.1/9.2/9.3 pass; MT-9.4/9.5 fail |

ADR-7 is excluded from all downstream scoring. ADR-9 proceeds as a split-archetype candidate for MT-9.1–9.3 only (denial letter generation, appeal rights notice, appeal intake/logging).

---

## 3. Step 2: Volume × Value Scoring

### Scoring Basis

**Volume — Execution Frequency** (1–5):  
Based on 1,667 claims/day [U1], 65/35 path split [A2], and estimated denial rate [A22]:

| Score | Threshold |
|:-----:|-----------|
| 5 | 500+ instances/day — every claim passes through |
| 4 | 100–500/day — subset of claims (Clinical Path or denied claims) |
| 3 | 10–100/day |
| 2 | Several/day |
| 1 | Weekly or less |

**Non-Determinism Effort** (1–5):  
How much does the task require reasoning beyond rules?

| Score | Threshold |
|:-----:|-----------|
| 5 | High synthesis: multiple data sources, policy interpretation, contextual clinical judgment |
| 4 | Significant reasoning: patterns with contextual adaptation and exception handling |
| 3 | Mixed: rule-based core with reasoning for edge cases |
| 2 | Mostly deterministic: small reasoning component around structured rules |
| 1 | Fully deterministic: pure rules/arithmetic, no reasoning required |

**Agentic Value Score = Volume × Non-Determinism** (1–25 scale)

### Scoring Table

| ADR | Description | Volume Score | ND Score | **Value Score** | Interpretation |
|-----|-------------|:---:|:---:|:---:|----------------|
| ADR-1 | Claim Intake & Format Validation | 5 | 2 | **10** | Consider agentic; validate TCO — EDI path is mostly rule-based |
| ADR-2 | Eligibility Verification | 5 | 2 | **10** | Consider agentic; conditional on [A12] — lookup logic is deterministic |
| ADR-3 | Coding & Compliance Validation | 5 | 2 | **10** | Consider agentic; rules engine preferred for ICD-10/NCCI; LLM only for plausibility |
| ADR-4 | Clinical Content Triage | 5 | 5 | **25** | Strong agentic candidate — gated on Phase 1 [A6] |
| ADR-5 | Fast Path Adjudication | 5 | 3 | **15** | Strong agentic candidate — coverage rule application with edge case reasoning |
| ADR-6 | Clinical Pre-Screening | 4 | 4 | **16** | Strong agentic candidate — synthesis of unstructured clinical docs into physician package |
| ADR-7 | Physician Clinical Review | — | — | — | **Excluded** (Human Only) |
| ADR-8 | Payment & EOB Generation | 5 | 1 | **5** | Anti-pattern — deterministic arithmetic; use existing payment engine |
| ADR-9 | Denial & Appeal Management | 4 | 3 | **12** | Consider agentic (MT-9.1–9.3 only); denial letters are patterned with policy citation reasoning |

**Volume score notes:**
- ADR-1 through ADR-5, ADR-8: all 1,667 claims/day → Score 5
- ADR-6: 35% of claims = ~583 clinical claims/day [A2] → Score 4
- ADR-9: estimated ~20% denial rate across all paths = ~333 denials/day [A22] → Score 4

### Volume × Value Quadrant

|                | **Low ND Effort**<br/>(Deterministic/Rules) | **High ND Effort**<br/>(Reasoning/Agentic) |
|----------------|---------------------------------------------|-------------------------------------------------|
| **High Volume**| **ADR-1** Intake (10)<br/>**ADR-2** Eligibility (10)<br/>**ADR-3** Coding (10)<br/>**ADR-8** Payment (5)<br/><br/>*Rules/RPA* | **ADR-4** Clinical Triage (25)<br/>**ADR-5** Fast Path Adj. (15)<br/>**ADR-6** Clinical Pre-Screening (16)<br/>**ADR-9** Denial/Appeals (12)<br/><br/>*Primary Agentic Targets* |
| **Low Volume** | *(No candidates)* | *(No candidates)* |


**Quadrant analysis:**

- **Top-right (Primary Agentic Targets):** ADR-4, ADR-5, ADR-6, ADR-9 — high volume AND high reasoning requirement. LLM agents provide irreplaceable value here over rule-based automation; this is where the investment is justified.
- **Top-left (Rules/RPA):** ADR-1, ADR-2, ADR-3, ADR-8 — high volume but low reasoning. These should be API integrations, rules engines, or structured lookups — not LLM agents. Build them as platform infrastructure, not as reasoning systems.
- All ADRs are high-volume (score ≥ 4) because claims processing is a continuous, high-frequency operation. The X-axis (non-determinism) is the primary decision variable for agentic investment.

---

## 4. Step 3: Total Cost of Ownership Assessment

### Baseline Model

**Key inputs:**
- Admin pool: 20 processors × $65,000/year fully loaded = **$1,300,000/year** [A1]
- Hourly rate: $31.25/hour ($65K ÷ 2,080 hours)
- Annual claim volume: 600,000 (50,000/month)
- Time allocation by ADR [A21]: proportion of the 35-minute processing average attributed to each workstream

| ADR | % of Admin Work [A21] | **Annual Baseline Cost** |
|-----|:---:|---:|
| ADR-1 (Intake) | 9% | $117,000 |
| ADR-2 (Eligibility) | 23% | $299,000 |
| ADR-3 (Coding) | 17% | $221,000 |
| ADR-4 (Triage) | 9% | $117,000 |
| ADR-5 (Fast Path adj — 65% of claims) | 19% | $247,000 |
| ADR-8 (Payment) | 9% | $117,000 |
| ADR-9 (Denial letters — partial) | 7% | $91,000 |
| Overhead / edge cases | 7% | $91,000 |
| **Total** | **100%** | **$1,300,000** |

### Agent Cost Model

**AI API costs [A4]:** $0.05/Fast Path claim · $0.10/Clinical Path claim  
Annual API cost: (390,000 × $0.05) + (210,000 × $0.10) = $19,500 + $21,000 = **$40,500/year**

**HITL costs** (exception handling retained in human queue after delegation):

| ADR | HITL Scenario | Rate | Annual HITL Cost |
|-----|--------------|:----:|---:|
| ADR-1 | Non-EDI claims needing human review (~10% of 30% non-EDI) | 18,000/yr × 5 min × $31.25/hr | $46,875 |
| ADR-2 | Eligibility exceptions (retroactive changes, COB) | 90,000/yr × 5 min × $31.25/hr | $234,375 |
| ADR-3 | Plausibility edge cases (~10% of coding tasks) | 60,000/yr × 3 min × $31.25/hr | $93,750 |
| ADR-4 | Random Fast Path audit (5% sample) [A6] | 30,000/yr × 2 min × $31.25/hr | $31,250 |
| ADR-5 | Fast Path denials pending [A11] (~20% of Fast Path denials) | 78,000/yr × 4 min × $31.25/hr | $162,500 |
| ADR-9 | Phase 2 human sign-off on AI denial letters (MT-9.1) | 83,250/yr × 2 min × $31.25/hr | $86,979 |
| **Total HITL** | | | **$655,729** |

**Total annual agent cost: $40,500 + $655,729 = $696,229/year**

### Build Cost and ROI

| Component | Estimated Build Cost |
|-----------|--------------------:|
| Phase 1 shadow infrastructure + CMS integration foundation | $90,000 [A9] |
| ADR-8: Payment engine integration (trigger existing system) | $15,000 |
| ADR-3: Rules engine wrap + LLM plausibility layer | $25,000 |
| ADR-1: EDI intake pipeline + PDF extraction module | $35,000 |
| ADR-2: Eligibility API integration (multi-system) | $40,000 |
| ADR-5: Fast Path adjudication engine + approval/denial workflow | $65,000 |
| ADR-6: Clinical pre-screening + physician summary portal [A20] | $75,000 |
| ADR-9: Denial letter generation + policy citation integration [A18] | $45,000 |
| Testing, governance, and monitoring infrastructure | $10,000 |
| **Total** | **$400,000** |

**ROI Calculation:**

```
Annual baseline cost (admin pool):    $1,300,000
Annual agent cost (API + HITL):         $696,229
                                      ----------
Annual saving:                          $603,771

Build cost:                             $400,000
Payback period:                         7.9 months

Year 1 ROI:  ($603,771 - $400,000) / $400,000 =   51%
3-year ROI:  ($603,771 × 3 - $400,000) / $400,000 = 353%
```

**Additional value not in base case:**

| Value Driver | Estimated Annual Value | Assumption |
|-------------|----------------------:|------------|
| SLA penalty avoidance (2 days over threshold eliminated) | $1.5M–$2.0M/year | [A8] $15/claim/day × 1,667 claims × 2 days |
| Avoided physician hiring (ADR-6 capacity multiplier 2.7×) | ~$1.5M/year | [A5] [A23] 6 FTEs × $250K |
| Denial overturn rate reduction (41% → ~20% baseline) | Unquantified Phase 3 target | [A16] |

**Economic gate result:** Year 1 ROI > 0% ✓ · Payback ≤ 18 months ✓ · Proceed to production planning

---

## 5. Step 4: Feasibility Scoring Matrix

**Scale:** 1 (low feasibility / high obstacle) → 5 (high feasibility / low obstacle). Higher is better for all factors; Compliance Risk score of 5 means low regulatory risk.

| ADR | Data Avail | Sys. Integration | Compliance Risk | Context Stability | Org Readiness | TCO Viability | **Total /30** |
|-----|:----------:|:----------------:|:---------------:|:-----------------:|:-------------:|:-------------:|:---:|
| ADR-3 (Coding) | 5 | 5 | 4 | 5 | 4 | 5 | **28** |
| ADR-8 (Payment) | 5 | 4 | 4 | 5 | 5 | 5 | **28** |
| ADR-1 (Intake) | 4 | 3 | 4 | 5 | 4 | 4 | **24** |
| ADR-5 (Fast Path) | 4 | 3 | 3 | 4 | 4 | 5 | **23** |
| ADR-2 (Eligibility) | 3 | 2 | 4 | 4 | 4 | 4 | **21** |
| ADR-6 (Pre-Screen) | 3 | 3 | 3 | 3 | 4 | 4 | **20** |
| ADR-9 (Denial) | 3 | 3 | 2 | 3 | 3 | 4 | **18** |
| ADR-4 (Triage) | 2 | 2 | 1 | 3 | 2 | 3 | **13** |

**Scoring notes:**

- **ADR-3 and ADR-8** (28): All inputs structured, commercial tools available, risk is reversible — the two easiest wins in the portfolio. Wave 1 anchors.
- **ADR-5** (23): Strong TCO and org readiness; held back by [A18] coverage rules engine uncertainty and [A11] legal unknowns.
- **ADR-2** (21): Deterministic decision logic but limited by multi-system integration complexity [A12]. Second-worst integration feasibility score.
- **ADR-6** (20): Org readiness is a relative strength (Dr. Webb is supportive); held back by portal capability [A20] and unstructured clinical input.
- **ADR-9** (18): Compliance risk (2) reflects regulatory appeal deadlines [A19] and legally defensible documentation requirement. Context stability (3) reflects evolving regulatory environment.
- **ADR-4** (13): Lowest feasibility despite highest value score (25). Undefined criteria [A15], no decision support tooling, and patient safety gate [A6] make this the highest-risk candidate. Wave 3 placement is warranted despite the financial importance.

---

## 6. Step 5: Strategic Sequencing

### Sequencing Criteria Assessment

| Criterion | Weight | ADR-8 | ADR-3 | ADR-1 | ADR-2 | ADR-5 | ADR-6 | ADR-9 | ADR-4 |
|-----------|:------:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| Self-financing ROI | High | ★★★ | ★★★ | ★★ | ★★ | ★★★ | ★★ | ★★ | ★ |
| Integration reusability | High | ★★ | ★★★ | ★★★ | ★★★ | ★★ | ★★ | ★ | ★ |
| Low compliance risk | Medium | ★★★ | ★★★ | ★★★ | ★★★ | ★★ | ★★ | ★★ | ★ |
| Data readiness | Medium | ★★★ | ★★★ | ★★★ | ★★ | ★★★ | ★★ | ★★ | ★ |
| Organisational readiness | Medium | ★★★ | ★★★ | ★★★ | ★★★ | ★★★ | ★★★ | ★★ | ★★ |
| Strategic visibility | Low | ★ | ★★ | ★★ | ★★ | ★★★ | ★★★ | ★★ | ★★★ |

**Wave 1 — Self-Funding Foundation (Phase 1, Months 1–3)**

Builds platform integrations that every subsequent ADR inherits. Generates immediate savings before Wave 2 is funded.

| ADR | Wave 1 Rationale | Platform Asset Created |
|-----|-----------------|----------------------|
| ADR-8 (Payment) | Fastest payback (~2 months); zero compliance risk; triggers existing payment engine | Payment engine API integration |
| ADR-3 (Coding) | Replaces highest-skill manual task; rules engine available; builds code validation pipeline reused by ADR-5 | NCCI edits engine + ICD-10/HCPCS reference API |
| ADR-1 (Intake — EDI path) | Foundational CMS API integration required by ADR-2, ADR-5, ADR-8; EDI format is lowest risk intake path | CMS API + queue management module |

Wave 1 estimated savings: ~$408K/year · Wave 1 build cost: ~$130K · Payback: ~3.8 months

**Wave 2 — Main Value Delivery (Phase 2, Months 4–6)**

Inherits CMS API, code validation, and payment engine from Wave 1. Delivers the Fast Path and begins the Clinical Path.

| ADR | Wave 2 Rationale | Prerequisite |
|-----|-----------------|-------------|
| ADR-2 (Eligibility) | Inherits CMS API from ADR-1; resolves the largest single time sink per claim (23% of admin work [A21]) | [A12] unified API confirmed in Week 1 IT discovery |
| ADR-5 (Fast Path Adj) | Inherits ADR-2 (eligibility) + ADR-3 (coding); delivers 65% Fast Path end-to-end agent adjudication | ADR-2 and ADR-3 complete; [A18] rules engine confirmed |
| ADR-6 (Pre-Screening) | Enables Clinical Path physician throughput target [A5]; requires criteria defined with Dr. Webb | [A15] clinical criteria defined; [A20] portal assessed |

Wave 2 unlocks the Fast Path → SLA improvement → penalty avoidance activates. CFO's 13 FTE reduction target is achievable by Month 6 with ADR-5 live.

**Wave 3 — AI-Native Operations (Phase 3, Month 7+)**

Conditional on Phase 1 validation and legal review. Highest value, highest risk.

| ADR | Wave 3 Rationale | Gate Condition |
|-----|-----------------|---------------|
| ADR-4 (Clinical Triage) | Highest value score (25); closes the last manual routing bottleneck; keystone of full financial case | [A6] Phase 1 false-negative rate < 2% over 60-day shadow |
| ADR-9 (Denial Letters) | Addresses 41% overturn rate; policy citation accuracy requires coverage rules engine and sample validation | [A11] legal review complete; [A18] rules engine live; 90-day sample review confirms policy citation accuracy |

---

## 7. Prioritized Candidate Shortlist

Ranked by composite score: Value Score (40%) + Feasibility Score normalized to 25 (30%) + Wave urgency (30%).

| Rank | ADR | Value Score | Feasibility /30 | Wave | Delegation Archetype | Recommendation |
|------|-----|:-----------:|:---------------:|:----:|---------------------|----------------|
| 1 | ADR-8 (Payment & EOB) | 5 | 28 | **Wave 1** | Fully Agentic | **Proceed** — lowest risk, fastest payback; anti-pattern: trigger payment engine |
| 2 | ADR-3 (Coding Validation) | 10 | 28 | **Wave 1** | Fully Agentic | **Proceed** — rules engine + LLM for plausibility only |
| 3 | ADR-1 (Intake & Validation) | 10 | 24 | **Wave 1** | Agent-led + Human Oversight | **Proceed** — builds foundational CMS integration for all ADRs |
| 4 | ADR-5 (Fast Path Adj) | 15 | 23 | **Wave 2** | Agent-led + Human Oversight | **Proceed after Wave 1** — conditional on [A12], [A18], [A11] |
| 5 | ADR-2 (Eligibility) | 10 | 21 | **Wave 2** | Agent-led + Human Oversight | **Proceed after Wave 1** — conditional on [A12] API availability |
| 6 | ADR-6 (Clinical Pre-Screen) | 16 | 20 | **Wave 2** | Agent-led + Human Oversight | **Proceed after Wave 1** — conditional on [A15] and [A20] |
| 7 | ADR-9 (Denial letters only) | 12 | 18 | **Wave 3** | Agent-led + Human Oversight | **Defer** — requires [A11], [A18], and 90-day sample review |
| 8 | ADR-4 (Clinical Triage) | 25 | 13 | **Wave 3** | Agent-led + Human Oversight | **Defer** — gated on Phase 1 [A6]; current state = Human Only |
| — | ADR-7 (Physician Review) | — | — | — | Human Only | **Excluded** — not a delegation candidate |

**Shortlist summary by wave:**
- **Wave 1 (proceed now):** ADR-8, ADR-3, ADR-1 — $130K build · $408K/year savings · 3.8-month payback
- **Wave 2 (proceed next quarter):** ADR-5, ADR-2, ADR-6 — $180K build · $546K/year incremental savings
- **Wave 3 (defer, pending gates):** ADR-4, ADR-9 — $90K build · Unlocks full financial case + denial quality improvement

---

## 8. Implementation Sequencing Logic

**How each wave funds the next:**

```
Wave 1 (Months 1–3) — Build cost ~$130K
  ADR-8  saves ~$117K/year (payment processing admin time)
  ADR-3  saves ~$221K/year (coding validation admin time)
  ADR-1  saves ~$70K/year  (EDI intake admin time)
  ─────────────────────────────────────────────────────
  Wave 1 total savings:  ~$408K/year
  Payback on Wave 1:     ~3.8 months

  → Wave 1 savings fund Wave 2 (~$180K build) within 5 months
  → CMS integration and code validation pipeline built once;
    reused by ADR-2, ADR-5, ADR-9

Wave 2 (Months 4–6) — Build cost ~$180K (funded by Wave 1)
  ADR-5  saves ~$247K/year (Fast Path adjudication admin time)
         + eliminates SLA penalty exposure up to $1.5M–$2M/year [A8]
  ADR-2  saves ~$299K/year (eligibility verification admin time)
  ADR-6  enables 2.7× physician throughput — avoids ~$1.5M in
         physician hiring [A5, A23]
  ─────────────────────────────────────────────────────
  Wave 2 incremental savings: ~$546K/year (admin) + SLA avoidance
  Combined Wave 1+2 savings:  ~$954K/year
  CFO's 13 FTE reduction ($845K) confirmed by Month 6

Wave 3 (Month 7+) — Build cost ~$90K (funded by Wave 1+2)
  ADR-4  closes the manual routing bottleneck; enables full
         Fast/Clinical split at scale [A6]
  ADR-9  targets 41% → <20% denial overturn rate [A16]
         with accurate policy citation in denial letters
  ─────────────────────────────────────────────────────
  Board presentation: validated headcount, SLA, and accuracy data
```

**Critical path dependencies:**

| Dependency | ADRs Blocked | Must Resolve By |
|-----------|-------------|----------------|
| CMS API availability [A12] | ADR-1 full scope; ADR-2, ADR-5, ADR-8 | Week 1 IT discovery sprint |
| Clinical criteria definition [A15] | ADR-4 Phase 1 shadow; ADR-6 design | Week 1 — before any agent development |
| AI denials legal review [A11] | ADR-5 denial automation; ADR-9 | Day 30 of engagement |
| Coverage rules engine format [A18] | ADR-5 full scope; ADR-9 policy citation | Phase 1 IT discovery sprint |
| Phase 1 false-negative gate [A6] | ADR-4 live deployment | End of Month 3 shadow period |
| Physician portal capability [A20] | ADR-6 scope and UI design | Phase 1 IT discovery sprint |

**Fallback positions if dependencies block:**

| Blocked Dependency | Fallback Position | Impact |
|-------------------|------------------|--------|
| [A12] no CMS API | ADR-1 limited to EDI; ADR-2 → Human-led + Automation Support; Wave 2 delayed ~2 months | Cycle time improvement delayed; penalty exposure continues |
| [A6] gate not cleared | ADR-4 remains Human Only; Phase 3 does not launch | CFO's full 13 FTE reduction target does not close — escalate to governance |
| [A11] adverse | Fast Path approvals proceed autonomously; denials route to physician queue | Denial throughput reduced; CFO headcount model partially at risk |
| [A18] not machine-readable | ADR-5 scope limited; coverage rule encoding added as prerequisite work item | Wave 2 delayed 4–6 weeks for encoding sprint |

---

## 9. Assumptions Referenced

| ID | Description | Confidence | Relevant To |
|----|-------------|:----------:|-------------|
| A1 | Admin processor fully loaded cost ($65K/year) | Medium (65%) | TCO baseline |
| A2 | 65% Fast Path / 35% Clinical Path split | Low (50%) | Volume scoring, all ADRs |
| A3 | 85% processor productive utilization | Medium (65%) | TCO capacity model |
| A4 | AI token cost ($0.05 Fast Path / $0.10 Clinical) | Low–Medium (55%) | Agent cost model |
| A5 | Physician throughput: 5–8/hr → 20/hr with pre-screening | Low (45%) | ADR-6 value case |
| A6 | <2% clinical flagging false-negative achievable | Medium (60%) | ADR-4 Phase 1 gate |
| A8 | Payer penalty rate ~$15/claim/day | Low (40%) | SLA avoidance value |
| A9 | Phase 1 infrastructure cost $80–100K | Low (40%) | Build cost model |
| A11 | AI Fast Path denials legally permissible | Low (45%) | ADR-5 denial scope, ADR-9 |
| A12 | CMS has usable API for integration | Low (40%) | Wave 1 foundation dependency |
| A15 | Clinical criteria informal/undocumented | Medium (60%) | ADR-4 sequencing gate |
| A16 | Denial letters use manual template fill-in | Medium (55%) | ADR-9 overturn rate case |
| A18 | Coverage rules engine in machine-readable form | Low (45%) | ADR-5, ADR-9 |
| A19 | Regulatory appeal deadlines tracked | Low (40%) | ADR-9 compliance risk |
| A20 | Physician portal supports structured summaries | Low (45%) | ADR-6 |
| **A21** | Time allocation across ADRs (% of 35 min/claim) | Low (40%) | TCO baseline allocation |
| **A22** | Denial rate across all claims (~20%) | Low (40%) | ADR-9 volume scoring |
| **A23** | Physician fully loaded annual cost (~$250K) | Low (40%) | ADR-6 physician capacity value |

New assumptions A21–A23 are defined in full in `specs/assumptions.md`.
