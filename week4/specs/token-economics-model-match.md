# Token Economics Model — MedFlex Match Selection (JtD-3)

> Economics deliverable for ATX Phase 5.
> Primary input: `specs/04a-capability-spec-match-selection.md`.
> Guidance: `input-docs/atx/atx-economics.md`.
> Supporting inputs: `specs/volume-×-value-analysis.md`, `specs/cognitive-load-map.md`.
> Assumption IDs reference `specs/assumptions.md`; new assumptions A30–A31 added in this session.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Baseline Cost Model](#2-baseline-cost-model)
3. [Token Economics Model](#3-token-economics-model)
   - 3.1 [Token Consumption per Micro-Task](#31-token-consumption-per-micro-task)
   - 3.2 [Tool Call Costs](#32-tool-call-costs)
   - 3.3 [Infrastructure Cost](#33-infrastructure-cost)
   - 3.4 [HITL Cost](#34-hitl-cost)
   - 3.5 [Total Agent Cost per Case](#35-total-agent-cost-per-case)
4. [ROI and Business Case](#4-roi-and-business-case)
   - 4.1 [Standard Business Case Model](#41-standard-business-case-model)
   - 4.2 [Financial Sensitivity Table](#42-financial-sensitivity-table)
5. [Self-Financing Roadmap](#5-self-financing-roadmap)
6. [Calibration — Making Economics Survive Reality](#6-calibration--making-economics-survive-reality)
7. [Economic Governance — Ongoing](#7-economic-governance--ongoing)
8. [Delegation Qualification Analysis](#8-delegation-qualification-analysis)

---

## 1. Executive Summary

JtD-3 (Match Selection) carries the highest agentic value score in the MedFlex pipeline (20/25, `specs/volume-×-value-analysis.md`) but the weakest standalone labor-saving justification: direct labor savings of ~$60K/year barely cover a $60K build cost. The economics depend on the revenue recovery hypothesis (M3, A5, A6) and the strategic throughput multiplier to close.

**Three findings shape the economics:**

**Finding 1 — HITL dominates cost, not tokens.** With 100% coordinator review at BP4 (A13), HITL labor ($0.881/case) constitutes 98% of total agent cost per case. Token cost in MVP is effectively $0.00: scoring and explanation are entirely rule-based with no LLM calls in the hot path (A22). The $0.015/case figure in A22 is a Phase 2 budget reserve for ML ranker inference.

**Finding 2 — Phase 2 HITL reduction is the primary cost optimization lever.** When auto-submit unlocks at ≤30% HITL (A30), cost per case drops from $0.892 to $0.290 — a 68% reduction. This additional $28K/year saving requires no token engineering, only A19 corpus accumulation and ML ranker validation.

**Finding 3 — Strategic value exceeds the labor saving by orders of magnitude.** The relevant comparison is not "$60K labor saved vs. $60K build" — it is "$60K build vs. $5.72M in additional coordinator headcount required to reach the $200M revenue target" (A1, A4, A7). The agentic pipeline eliminates the headcount scaling requirement entirely.

**Year 1 economic summary (JtD-3 as primary revenue enabler):**

| Scenario | Labor Saving | M3 Revenue Recovery | Year 1 Net | Year 1 ROI |
|---|---|---|---|---|
| Floor (A5=0%, win rate >90%) | ~$60K | $0 | ~−$9K | ~−14% (breaks even Year 2) |
| Base (A5=10%, win rate 75–90%) | ~$60K | $375K–$500K | ~$426K–$551K | ~610%–818% |
| Ceiling (A5=30%, win rate ≤75%) | ~$60K | $1.5M | ~$1.55M | ~2,483% |

Build cost: $60,000 (A21). A5 falsifiable by week 2 (win-rate pull from ServiceNow). In all M3 scenarios, payback < 2 months from deployment.

---

## 2. Baseline Cost Model

### 2.1 Direct Labor Cost

| Parameter | Value | Source |
|---|---|---|
| Active time per case (human) | 5 min (0.083h) | A1, A16 (25% of 20-min end-to-end match) |
| Fully loaded hourly cost | $26.44/hr | A7 ($55K/yr ÷ 2,000 hrs) |
| Baseline cost per case | $2.20 | A1 × A7 |
| Cases per year | 46,000 | A4 (184/day × 250 working days) |
| **Annual baseline cost** | **$101,360** | 46,000 × $2.20 |

```
Annual baseline = 46,000 × (5/60) × $26.44 = $101,360/year
```

### 2.2 Indirect Costs

**Throughput ceiling — capacity constraint:**
- Each coordinator handles ~23 complete matches/day at 20 min/match (A1)
- 8 coordinators × 23 = 184 fills/day — no headroom for volume growth (A4)
- $200M revenue target requires ~209 fills/day, implying ~112 coordinators (A1, A4)
- Headcount scaling cost: (112 − 8) × $55K = **$5.72M/year additional labor** (A7)
- This is the capacity cost the agentic pipeline eliminates entirely

**Queue opportunity cost (A5, A6):**
- 4.2-hour average fill time causes competitive loss of inbound shift requests
- At A5=30% loss rate: 0.30 × 46,000 requests/year × $300/shift (A3) = **$4.14M/year revenue at risk**
- A5 confidence is Low; falsifiable at week 2 (see §6.1)

**Error and rework cost:**
- 7% hospital mismatch rate from credential parsing errors (A10)
- 7% × 46,000 = 3,220 mismatch events/year
- Rework cost: 3,220 × 0.33h × $26.44 = **~$28K/year** in additional coordinator time

---

## 3. Token Economics Model

### 3.1 Token Consumption per Micro-Task

JtD-3 MVP operates without LLM calls in the scoring hot path. All scoring, disqualification, and explanation generation are rule-based and template-driven (capability spec §8, §9). The Phase 2 token budget reflects introduction of LLM-enriched explanations and ML ranker inference after A19 corpus threshold is met (A19, A22).

| MT | Task | LLM Tokens In | LLM Tokens Out | Token Cost (MVP) | Token Cost (Phase 2) | Notes |
|---|---|:---:|:---:|:---:|:---:|---|
| MT-3.0 | Receive/validate CandidatePool | 0 | 0 | $0.000 | $0.000 | Internal pipeline event |
| MT-3.1a | Disqualification pass | 0 | 0 | $0.000 | $0.000 | In-memory boolean logic |
| MT-3.1b | Hospital preference fetch | 0 | 0 | $0.000 | $0.000 | ServiceNow read; no LLM |
| MT-3.1c | Geocoding (proximity score) | 0 | 0 | $0.000 | $0.000 | Maps API call; no LLM (A26) |
| MT-3.2 | Composite score + rank | 0 | 0 | $0.000 | $0.000 | In-memory formula (A25) |
| MT-3.3 | Explanation template | 0 | 0 | $0.000 | $0.000 | String template; no LLM |
| MT-3.4 | Present shortlist at BP4 | 0 | 0 | $0.000 | $0.015 | Phase 2: LLM enriches explanations (A22) |
| MT-3.5 | Write CoordinatorReview | 0 | 0 | $0.000 | $0.000 | ServiceNow write; no LLM |
| MT-3.6 | Write RankerFeedback | 0 | 0 | $0.000 | $0.000 | ServiceNow write; no LLM (A28) |
| MT-3.7 | Trigger JtD-4 | 0 | 0 | $0.000 | $0.000 | Internal event |
| MT-3.8 | BP5 re-rank (~8% of cases) | 0 | 0 | $0.000 | $0.000 | Re-runs MT-3.1–3.3; no LLM |
| **TOTAL** | | **0** | **0** | **$0.000** | **$0.015** | |

**MVP note**: No LLM tokens consumed in the JtD-3 hot path. The $0.015/case in A22 is reserved as a Phase 2 buffer — it is not a current cost. Phase 2 model: Claude Sonnet (claude-sonnet-4-6), ~2,000 input / ~600 output tokens, at $3.00/M input and $15.00/M output (A22).

### 3.2 Tool Call Costs

| Tool | Calls per Case | Unit Cost | Cost per Case | Annual Cost |
|---|---|---|:---:|:---:|
| ServiceNow read (preference history) | 1 batched | License-covered | $0.000 | $0 |
| ServiceNow write (CoordinatorReview) | 1 | License-covered | $0.000 | $0 |
| ServiceNow write (RankerFeedback) | 1 | License-covered | $0.000 | $0 |
| Google Maps Geocoding (post-cache) | ~0.27/case avg | $0.005/call | $0.001 | ~$62/yr |
| Internal pipeline events | 2 | $0.000 | $0.000 | $0 |
| **Total tool calls** | | | **$0.001** | **~$62/yr** |

**Geocoding detail (A26)**: 920 raw proximity calculations/day (184 cases × 5 candidates, A2, A4). ZIP-level 24h cache reduces to ~50 unique API calls/day. At $0.005/call: $0.25/day = $62.50/year. Per-case allocation: $62 ÷ 46,000 = $0.001/case. Remains within Google Maps free tier (40,000 calls/month).

### 3.3 Infrastructure Cost

Platform compute, logging, monitoring, and storage amortized across 46,000 cases/year.

| Component | Monthly Cost | Per-Case Allocation |
|---|:---:|:---:|
| Compute (agent runtime) | ~$20/mo | $0.005/case |
| Storage (audit logs, feedback store, A28) | ~$10/mo | $0.003/case |
| Monitoring + alerting | ~$10/mo | $0.003/case |
| **Total infrastructure** | **~$40/mo ($480/yr)** | **~$0.010/case** |

Infrastructure is negligible relative to HITL cost at current volumes. Becomes material only if volume scales 5×+ (see §7.5).

### 3.4 HITL Cost

**MVP (100% HITL, A13):**
```
HITL rate (MVP):      100% — every case reviewed at BP4 (A13)
Time per review:      2 minutes (A16)
Reviewer hourly cost: $26.44/hr (A7)

HITL cost per case = 1.00 × (2/60) × $26.44 = $0.881/case
Annual HITL cost    = 46,000 × $0.881        = $40,526/year
```

**Phase 2 projection (A30 — ≤30% HITL after auto-submit threshold unlocked):**
```
HITL cost per case (Phase 2) = 0.30 × (2/60) × $26.44 = $0.264/case
Annual HITL cost (Phase 2)   = 46,000 × $0.264        = $12,144/year

Additional annual saving vs. MVP: $40,526 − $12,144 = $28,382/year
Additional annual token cost (Phase 2 LLM): 46,000 × $0.015 = $690/year
Net Phase 2 annual uplift: $28,382 − $690 = $27,692/year
```

### 3.5 Total Agent Cost per Case

| Component | MVP | Phase 2 |
|---|:---:|:---:|
| Token cost | $0.000 | $0.015 |
| Tool call cost | $0.001 | $0.001 |
| Infrastructure cost | $0.010 | $0.010 |
| HITL cost | $0.881 | $0.264 |
| **Total per case** | **$0.892** | **$0.290** |
| **Annual (46,000 cases)** | **$41,072** | **$13,340** |

**Capability spec KPI**: ≤ $0.90/case. MVP result: $0.892 ✓

**Cost composition (MVP):**
- HITL: 99% of total cost
- Infrastructure: 1%
- Token + tool: <1%

This profile confirms: cost optimization in JtD-3 is a **HITL-reduction problem**, not a token-engineering problem. Token price changes of ±50% shift total cost by ±$0.008/case — less than 1% of the HITL component.

---

## 4. ROI and Business Case

### 4.1 Standard Business Case Model

```
Annual volume:         46,000 cases/year (A4)
Annual baseline cost:  $101,360/year (§2.1)
Annual agent cost:     $41,072/year (§3.5 MVP)
Annual labor saving:   $60,288/year

Build cost breakdown (A21):
  Architecture + scoring engine design:   $15,000 (week 1)
  Data models + integration contracts:    $15,000 (week 2)
  Coordinator review UI + API (A27):      $15,000 (week 3)
  Testing, calibration, coordinator UAT:  $15,000 (week 4)
  Total build cost:                       $60,000 (4 weeks × $15K/week)

Annual maintenance (A31):  $9,000/year (15% of $60K build)

Year 1 net (labor saving only):
  $60,288 − $60,000 (build) − $9,000 (maintenance) = −$8,712
  → Labor saving alone does not recover build cost in Year 1
  → Cumulative positive by month 14

Payback period (labor only): ~12 months
3-year ROI (labor only):
  Total saving:     $60,288 × 3 = $180,864
  Total investment: $60,000 + ($9,000 × 3) = $87,000
  Net 3-year value: $93,864
  3-year ROI:       108%

3-year ROI (with M3 base, A5=10% — $375K Year 1 recovery):
  Total saving:     $180,864 + $375,000 = $555,864
  Net 3-year value: $468,864
  3-year ROI:       539%
```

**Revenue recovery (M3) — JtD-3 is the critical path dependency:**

M3 revenue recovery requires the full Wave 1 pipeline (JtD-1 → JtD-3 → JtD-4) to be operational. JtD-3 is the bottleneck: without the ranker and coordinator review UI, the pipeline cannot close matches. M3 is attributed to the pipeline as a whole; JtD-3 build is the enabling investment.

| A5 Scenario | 6-Month M3 Revenue | Year 1 Net (Labor + M3) | Year 1 ROI | Payback |
|---|---|---|---|---|
| Floor (A5=0%, win rate >90%) | $0 | ~−$9K | ~−14% | 14 months |
| Midpoint (A5=10%, win rate 75–90%) | $375K–$500K | ~$426K–$551K | ~610%–818% | <2 months |
| Ceiling (A5=30%, win rate ≤75%) | $1.5M | ~$1.55M | ~2,483% | <1 month |

All M3 scenarios are falsifiable at week 2 via win-rate pull (A5 falsifiable check, `specs/assumptions.md`).

### 4.2 Financial Sensitivity Table

| Scenario | Token Cost/Case | HITL Rate | Agent Cost/Case | Annual Labor Saving | M3 Recovery | Year 1 Net | Payback |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Conservative (higher tokens, no M3) | $0.023 (+50%) | 100% (A13) | $0.915 | $59,270 | $0 | −$9,730 | 14.2 months |
| Base case (A22 budget, A5=10%) | $0.015 | 100% (A13) | $0.907 | $59,638 | $375K | $374,638 | 1.9 months |
| Optimistic (Phase 2, A5=30%) | $0.011 (−30%) | 30% (A30) | $0.286 | $88,220 | $1.5M | $1.53M | 0.5 months |

**Key sensitivity observations:**

1. **HITL rate dominates cost** — a 70-pp HITL reduction (MVP → Phase 2, A30) saves $28K/year; a 50% token price reduction saves only $690/year.
2. **M3 is the dominant return variable** — its presence or absence changes Year 1 ROI from −14% to 2,483%.
3. **Business case is robust to token price increases** — even at +50% token cost, the labor-saving case is unaffected; payback extends from 12 to 14 months only in the no-M3 floor scenario.
4. **Conservative floor is the only negative scenario** — and only marginally (−$9,730/year); breaks even in Year 2 on labor savings alone.

---

## 5. Self-Financing Roadmap

### Wave 1 — Unified Pipeline Build (Weeks 1–8)

JtD-3 does not self-finance on labor savings alone. It is funded as part of the Wave 1 pipeline investment, which self-finances through the faster-payback upstream JtDs.

| JtD | Build Cost | Annual Labor Saving | Payback | Shared Asset Created for JtD-3 |
|---|:---:|:---:|:---:|---|
| JtD-1 Shift Intake Parsing | $30,000 | $126,460 | 2.8 months | ServiceNow read API; LLM domain prompt |
| JtD-2 Candidate Search | $45,000 | $119,350 | 4.5 months | Nurse DB query layer; geocoding cache; preference lookup |
| **JtD-3 Match Selection** | **$60,000** | **$60,288** | **12 months** | **Coordinator review UI; rule-based ranker; A19 feedback loop** |
| JtD-4 Submission | $15,000 | $40,000 | 4.5 months | ServiceNow write API; full audit trail |
| JtD-5a Monitoring | $15,000 | indirect | N/A | RankerFeedback outcome updates (A28) |

```
Wave 1 engagement cost:     ~$120,000 (8-week engagement, A21)
  — JtD-3 build runs in parallel with JtD-1+2 from week 1, not sequentially

Combined annual labor saving: ~$346,138/year
Wave 1 payback:               ~4.2 months (from labor savings alone)

JtD-3's structural role: enables match completion (BP4 → JtD-4 → hospital fill).
Without JtD-3, JtD-1 and JtD-2 produce a candidate pool with no closing mechanism —
all upstream investment generates zero revenue without the ranker and coordinator UI.
```

**Wave 1 → Wave 2 funding bridge:**

```
Wave 1 labor savings by month 6:  $346,138 × 0.5 = $173,069
Wave 1 build cost:                 $120,000
Wave 1 surplus by month 6:         $53,069

Wave 2 estimated build cost:      ~$85,000
  (reduced from ~$120K by ~$35K in reusable Wave 1 assets)
Wave 2 funding gap:               $85,000 − $53,069 = $31,931
  → Covered by months 7–8 labor savings
  → Wave 2 is fully self-financed by month 8 without M3 revenue
```

**Platform assets built in Wave 1 reducing Wave 2 cost:**

| Asset Built | Wave 1 Owner | Wave 2 Reuse | Estimated Wave 2 Build Reduction |
|---|---|---|:---:|
| ServiceNow read/write API client | JtD-1 / JtD-4 | JtD-6 MT-6.2, JtD-5b | ~$15,000 |
| Geocoding cache layer | JtD-3 | JtD-6 MT-6.4 emergency re-fill | ~$5,000 |
| Coordinator review UI + API (A27) | JtD-3 | JtD-3 ML ranker (modified) | ~$10,000 |
| u_pipeline_audit_log | JtD-3 | All Wave 2 JtDs | ~$5,000 |
| A19 labeled feedback store (A28) | JtD-3 | JtD-3 ML ranker training input | ~$20,000 data value |
| **Total Wave 2 build reduction** | | | **~$35,000** |

### Wave 2 — ML Ranker Upgrade + JtD-6 + JtD-5b (Months 3–6 post-MVP)

**JtD-3 ML ranker economic unlock (A19, A30):**

```
Trigger:   A19 corpus reaches ~8,000–11,000 labeled examples
           (184/day × 60 working days × ~50% structured capture)
Timeline:  ~3 months post-MVP launch

Economic impact:
  HITL rate (A30 target): ≤30% auto-submit on high-confidence cases
  Additional labor saving: $28,382/year
  Phase 2 token cost:     +$690/year (46,000 × $0.015)
  Net annual uplift:       $27,692/year incremental
```

| Wave | Investment | Annual Labor Saving | M3 Contribution | Cumulative 3-Year Value |
|---|:---:|:---:|:---:|:---:|
| Wave 1 (Months 0–8) | $120,000 | $346,138 | $375K–$1.5M | $1.0M–$4.7M |
| Wave 2 (Months 3–12) | ~$50,000 net | +$28,382 (JtD-3 Phase 2) | Throughput upside | +$85K labor |
| Wave 3 (Year 2+) | TBD | Progressive autonomy | Full auto-submit potential | Compounds Wave 1+2 |

### Wave 3 — Progressive Auto-Submit (Year 2+)

Trigger: ML ranker accuracy validated above coordinator baseline; composite_score ≥ 0.90 AND edit rate < 10% (capability spec §12).

```
Economic projection at 0% HITL for auto-submit band (~70% of volume):
  Per-case cost:      ~$0.026 (token + tool + infra; no HITL for auto-submit cases)
  Blended cost/case:  0.30 × $0.290 (30% HITL) + 0.70 × $0.026 = $0.105/case
  Annual cost at scale: 46,000 × $0.105 = $4,830/year
  Annual saving vs. baseline: $101,360 − $4,830 = $96,530/year
  ROI vs. Wave 1 build: 1,609% on $60K JtD-3 investment alone
```

---

## 6. Calibration — Making Economics Survive Reality

Business case assumptions must be validated before production release.

### 6.1 Key Calibration Metrics

| Metric | Business Case Target | Impact if Missed | Validation Method |
|---|---|---|---|
| Edit rate (ranker accuracy) | ≤30% coordinator edits | HITL review time increases; A25 weights need recalibration | Shadow run: ranker vs. 200-record historical corpus (A29) |
| HITL review time | ≤2 min/case (A16) | HITL cost exceeds $0.881/case; $0.90 KPI breached | Coordinator UAT session (C2, R1) — timed review |
| Token cost per case | $0.00 MVP; $0.015 Phase 2 (A22) | Negligible in MVP; +$690/year in Phase 2 if over | Dry run with LLM explanations enabled in staging (A29) |
| Geocoding cache hit rate | ≥80% (A26) | Tool cost rises; remains negligible at current volume | Log cache hits during pilot week |
| A5 win-loss rate | ≤75% for M3 hypothesis to hold | If >90%, M3 evaporates; reframe to throughput scaling | ServiceNow win-rate pull at week 2 (A5 falsifiable check) |
| BP5 rejection rate | ≤15% (MT-3.8 frequency) | Re-rank adds latency; coordinator review time increases | Track rejection events from JtD-5a response monitoring |

### 6.2 Mock Environment Testing

Before production release, run against the 200-record calibration corpus (A29):

1. **Accuracy check**: ranker top-ranked candidate matches historical coordinator selection ≥70% of cases (capability spec KPI, month 3 target)
2. **Token verification**: confirm $0.00 in MVP hot path; simulate Phase 2 LLM calls to validate $0.015/case estimate
3. **HITL trigger rate**: measure % of cases that generate `low_confidence = true` (composite_score < 0.40)
4. **Edge case distribution**: all-disqualified rate, escalation rate, BP5 re-rank frequency

**Operating point gate**: only proceed to production when measured edit rate ≤30% AND measured HITL review time ≤2 min in UAT. If edit rate exceeds 30%, recalibrate scoring weights (A25) before launch.

### 6.3 Sigma (Variance) Management

The rule-based ranker produces **narrow sigma** (deterministic output for identical inputs) — the correct profile for a high-volume, regulated matching workflow. Key variance risks to monitor:

- **A25 weight sensitivity**: small changes to the 0.40/0.30/0.20/0.10 weights can flip rank order for closely-scored candidates. Validate with coordinator review before launch; recalibrate after Wave 1 data accumulates.
- **A12 data gaps**: the neutral fallback (0.50) for missing preference history inflates composite scores uniformly — may not differentiate candidates with sparse histories. Monitor average composite_score distribution in calibration run.
- **A17 staleness**: stale availability records surface as coordinator edits (`availability_confidence = 0.30`). High edit rate on stale-availability cases signals the availability_confidence weight (0.30) may need to increase.

---

## 7. Economic Governance — Ongoing

Once in production, treat economics as a live governance instrument.

### 7.1 Monthly Review Dashboard

| Metric | Target | Alert Threshold | Action on Alert |
|---|---|---|---|
| Cost per case | ≤$0.90 (A13, MVP) | >$0.95 | Investigate HITL review time creep; coordinator workflow audit |
| HITL review time | ≤2 min/case (A16) | >3 min/case | Coordinator UI review; consider review workflow redesign |
| Token cost per case | $0.00 (MVP) | >$0.005 | Check for unintended LLM invocations in hot path |
| Edit rate | ≤30% | >40% | Re-examine scoring weights (A25); accelerate A19 corpus accumulation |
| A19 corpus growth | ~184 records/day (A4) | <150/day | Investigate RankerFeedback write failures; check dead-letter queue (A28) |
| BP5 rejection rate | ≤15% | >20% | Review scoring formula; check hospital preference data quality (A12) |

### 7.2 Quarterly Reviews

- **HITL rate trajectory**: is the edit rate declining? If edit rate drops below 20% for 60 consecutive working days, initiate Phase 2 ML ranker development.
- **A5 hypothesis update**: has the week-2 win-rate pull been validated against 6-month outcomes? If M3 revenue recovery has not materialized by month 6, replace M3 metric with throughput-scaling metric (A5 decision gate).
- **Cost per case vs. budget**: re-forecast if volume changes ≥20% from A4 baseline (184/day).
- **Maintenance cost review**: confirm annual $9,000 maintenance budget (A31) is sufficient as integration surface expands.

### 7.3 Model Release Triggers

On Anthropic model releases:
- Re-evaluate Claude Sonnet (claude-sonnet-4-6) for Phase 2 ML scoring — newer models may offer better ranking quality at same or lower token cost (A22 pricing subject to revision)
- Run calibration corpus against new model before production switch; confirm edit rate target holds
- Recalculate Phase 2 token cost per case if pricing changes; update sensitivity table

### 7.4 Phase 2 Economic Unlock Gate

Auto-submit threshold activation requires all of the following (A30):

1. A19 corpus ≥ 8,000 labeled examples (A19)
2. ML ranker accuracy ≥ coordinator baseline (edit rate at top-1 selection < historical coordinator edit rate)
3. Edit rate sustained ≤20% for 30 consecutive working days
4. Phase 2 dry-run cost confirmed ≤$0.30/case (including LLM inference + 30% HITL)

On Phase 2 launch: re-run full business case model with measured cost/case; update A30 if actual auto-submit HITL rate differs from ≤30% target.

### 7.5 Volume Growth Forecasting

If MedFlex executes the $200M revenue target, daily volume scales materially:

```
$200M revenue ÷ $300/shift (A3) ÷ 250 working days = 2,667 fills/day total market
Assuming MedFlex captures ~25% share at scale → ~667 fills/day
Annual volume at scale: 167,000 cases/year

Agent cost at scale (Phase 2 blended):
  167,000 × $0.290/case = $48,430/year

Baseline (unautomated at scale):
  167,000 × $2.20/case = $367,400/year

Annual saving at scale: $318,970/year
Infrastructure cost per case declines at scale:
  ~$480/year platform ÷ 167,000 cases = $0.003/case
```

Volume scaling does not change the per-case economics materially; it amplifies the total saving linearly.

---

## 8. Delegation Qualification Analysis

Economic assessment per workstream: whether the delegation archetype is economically justified and what conditions must hold.

| JtD | Delegation Level | Baseline Cost/Year | Agent Cost/Year | Net Annual Saving | Build Cost | Payback | Economic Verdict |
|---|---|:---:|:---:|:---:|:---:|:---:|---|
| JtD-1 Shift Intake Parsing | Agent-led + HITL (15%) | $142,100 | $15,640 | $126,460 | $30,000 | 2.8 months | **Pass** — strongest standalone ROI; unconditional |
| JtD-2 Candidate Search | Fully Agentic | $121,600 | $2,250 | $119,350 | $45,000 | 4.5 months | **Pass** — highest saving-to-cost ratio; unconditional |
| **JtD-3 Match Selection** | **Agent-led + HITL (100% MVP)** | **$101,360** | **$41,072** | **$60,288** | **$60,000** | **12 months** | **Conditional** — labor alone barely closes; requires M3 |
| JtD-4 Submission | Fully Agentic | $40,480 | $460 | $40,020 | $15,000 | 4.5 months | **Pass** — enables revenue loop closure |
| JtD-5a Monitoring | Fully Agentic | indirect | ~$500 | indirect | $15,000 | strategic | **Strategic** — closes M4 tracking; enables A28 outcome updates |
| JtD-5b Conflict Resolution | Human-led + Agent Support | ~$25,000 | N/A (Wave 2) | N/A | deferred | Wave 2 | **Fail (Wave 1)** — infrastructure gaps; no nurse-decline API (A14) |
| JtD-6 No-Show Management | Human-led + Automation Support | ~$25,000 | N/A (Wave 2) | N/A | deferred | Wave 2 | **Conditional (Wave 2)** — phone intake unautomatable (A14) |

**Qualification rationale by workstream:**

**JtD-3 (primary focus)** — Conditional. The 100% MVP HITL rate constrains direct labor saving to ~$60K/year, which barely covers the $60K build cost. Three factors justify proceeding:
1. M3 revenue recovery ($375K–$1.5M Year 1) closes the case decisively under any M3-plausible scenario
2. Throughput multiplier (10× coordinator capacity per agent review rate) eliminates $5.72M headcount scaling requirement
3. A19 feedback accumulation funds Phase 2 ML ranker, delivering 68% cost reduction and $27K/year additional saving
The condition: A5 win-rate check at week 2 must confirm loss rate ≤75%. If win rate >90%, M3 does not apply and JtD-3 economics must be reframed to throughput-scaling (volume × growth, not fill-speed recovery).

**JtD-1** — Strongest standalone economic case ($126K saving, 2.8-month payback). Qualifies unconditionally on labor savings. Also the pipeline gate — without JtD-1's structured output, JtD-2 and JtD-3 cannot operate. Conditional suitability gate (IS:L) addressed by LLM parser + 15% HITL routing (A10).

**JtD-2** — Highest saving-to-cost efficiency ($119K saving on $45K build). Qualifies unconditionally. Fully Agentic archetype is appropriate given deterministic decision logic (DD:H). No LLM reasoning required; savings come from eliminating manual credential filtering and proximity scoring.

**JtD-4** — Automation (not an agent). Qualifies on $40K/year labor saving and strategic value: enables precise M1 (fill-time) measurement with sub-second audit timestamps and closes the revenue loop after BP4 approval.

**JtD-5a** — No direct labor saving quantified (coordinators do not currently monitor submissions actively). Qualifies on strategic grounds: closes the hospital response confirmation loop, enables M4 (no-show baseline) tracking, and creates the mechanism by which `u_submission_outcome` is updated in RankerFeedback (A28) — the feedback quality that trains the Phase 2 ML ranker depends on JtD-5a completing the outcome record.

**JtD-5b and JtD-6** — Economic qualification deferred to Wave 2. Both face hard infrastructure gaps that are not build-effort problems: JtD-5b has no inbound nurse-decline API and no cross-agency coordination (A14, A20); JtD-6 has phone-only no-show intake with no structured API. Wave 1 integration assets (ServiceNow write, geocoding cache, audit log) are reused by both at marginal cost when Wave 2 proceeds.

---

*See `specs/assumptions.md` for all assumptions referenced (A1–A31).*
*New assumptions A30–A31 added in this session.*
