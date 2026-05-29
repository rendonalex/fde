# Volume × Value Analysis — MedFlex Shift Matching

> Deliverable for ATX Phase 4: Candidate Prioritisation.
> Input: `specs/cognitive-load-map.md` (6 JtDs, 20 micro-tasks) and `specs/3-agentic-solution-architecture.md` (delegation archetype assignments).
> Assumption IDs reference `specs/assumptions.md`; new assumptions A21–A22 added in this session.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Step 1 — Suitability Gating](#2-step-1--suitability-gating)
3. [Step 2 — Volume × Value Quadrant](#3-step-2--volume--value-quadrant)
4. [Step 3 — TCO Assessment](#4-step-3--tco-assessment)
5. [Step 4 — Feasibility Scoring Matrix](#5-step-4--feasibility-scoring-matrix)
6. [Step 5 — Strategic Sequencing](#6-step-5--strategic-sequencing)
7. [Prioritized Candidate Shortlist](#7-prioritized-candidate-shortlist)

---

## 1. Executive Summary

Three findings shape candidate prioritization:

**Finding 1 — One use case dominates the value equation.** JtD-3 (Match Selection) is the only strong agentic candidate (value score 20/25). It is the primary throughput bottleneck and the primary lever for the <1h fill-time target. All other JtDs in the standard pipeline are infrastructure for — or automation around — this core judgment task.

**Finding 2 — The pipeline foundation (JtD-1, JtD-2) is self-financing.** Together, intake parsing and candidate search eliminate ~$245K/year in direct coordinator labor with a combined payback period of ~4 months — independently of whether the revenue recovery hypothesis (A5, A6) holds.

**Finding 3 — Exception paths (JtD-5b conflict, JtD-6 no-show) cannot be addressed in the 8-week window.** Both have hard infrastructure gaps: no structured nurse-decline API, no cross-agency visibility, and phone intake for no-shows. These are Wave 2 targets, funded by Wave 1 ROI.

**Wave 1 economic summary (8-week MVP)**: Projected Year 1 return of ~$1.85M ($346K direct labor savings + $1.5M conservative revenue recovery target, M3) on a ~$120K build budget (A21). Year 1 ROI: ~1,440%.

---

## 2. Step 1 — Suitability Gating

**Gate criteria** (`atx-scoring.md`): at minimum Medium suitability on Input Structure, Decision Determinism, and Tool Coverage; no hard compliance blocks.

| JtD | Input Structure | Decision Determinism | Tool Coverage | Compliance Risk | Gate Result |
|---|:---:|:---:|:---:|:---:|---|
| JtD-1 Shift Intake Parsing | L | M | M | M | **Conditional** — IS:L mitigated by LLM parser + 15% HITL routing (A10) |
| JtD-2 Candidate Search | H | H | M | M | **Pass** |
| JtD-3 Match Selection | M | L | L | M | **Conditional** — DD:L and TC:L mitigated by Agent-led + HITL archetype (A13, A18, A19) |
| JtD-4 Submission | H | H | M | M | **Pass** |
| JtD-5 MT-5.1/5.2 Monitoring | H | H | M | M | **Pass** |
| JtD-5 MT-5.3/5.4 Conflict | L | L | L | H | **Fail** — 3 Low dimensions + High compliance; infrastructure gaps preclude 8-week delivery |
| JtD-6 No-Show Management | L | M | M | H | **Conditional** — IS:L (phone intake, no API) + High compliance; automation limited to post-intake sub-tasks (MT-6.2, MT-6.4) |

**Outcome**: JtD-1, 2, 3, 4, 5a proceed to scoring. JtD-5b fails the gate for this window (Wave 2). JtD-6 is conditional — automatable downstream sub-tasks only; Wave 2.

---

## 3. Step 2 — Volume × Value Quadrant

### Volume Scoring (Execution Frequency, 1–5)

| JtD | Daily Volume | Score | Basis |
|---|---|:---:|---|
| JtD-1 Shift Intake Parsing | 184 requests/day (A4) | 4 | 50–200/day |
| JtD-2 Candidate Search | 920 filter operations/day (184 searches × ~5 candidate evaluations, A2, A4) | 5 | Hundreds+/day |
| JtD-3 Match Selection | 184 decisions/day (A4) | 4 | 50–200/day |
| JtD-4 Submission | 184 submissions/day (A4) | 4 | 50–200/day |
| JtD-5a Monitoring & Notification | 184 response cycles/day (A4) | 4 | 50–200/day |
| JtD-5b Conflict Resolution | ~22 events/day (~12% of 184, A9) | 2 | Several/day |
| JtD-6 No-Show Management | ~22 events/day (~12% of 184, A4, A9) | 2 | Several/day |

### Non-Deterministic Decision Effort Scoring (1–5)

| JtD | Score | Rationale |
|---|:---:|---|
| JtD-1 Parsing | 3 | Core path is NLP pattern-matching (domain rules teachable); ~15% of inputs require judgment for ambiguous requests (A10) |
| JtD-2 Search | 2 | Mostly deterministic — credential filters, date comparisons, proximity calculation; MT-2.5 preference lookup has minor fallback logic (A12) |
| JtD-3 Selection | 5 | Highest reasoning: undocumented multi-factor weights, tacit hospital knowledge (A18), contextual candidate synthesis |
| JtD-4 Submission | 1 | Fully deterministic — template formatting + API call; zero reasoning |
| JtD-5a Monitoring | 1 | Binary event routing (accepted/rejected); deterministic state machine |
| JtD-5b Conflict | 4 | High reasoning: competitive dynamics, nurse relationship history, shift urgency — no structured data (A20) |
| JtD-6 No-Show | 3 | MT-6.2 has partial rules (threshold); MT-6.4 emergency re-fill is full JtD-1–4 reasoning restart under time pressure |

### Agentic Value Score (Volume × Non-Determinism)

| JtD | Volume | Non-Det | **Value Score** | Interpretation |
|---|:---:|:---:|:---:|---|
| JtD-3 Match Selection | 4 | 5 | **20** | Strong agentic candidate (≥15) |
| JtD-1 Shift Intake Parsing | 4 | 3 | **12** | Consider agentic — validate with TCO (8–14) |
| JtD-2 Candidate Search | 5 | 2 | **10** | Consider agentic — validate with TCO (8–14) |
| JtD-5b Conflict Resolution | 2 | 4 | **8** | Consider agentic — blocked by infrastructure (Wave 2) |
| JtD-6 No-Show Management | 2 | 3 | **6** | Below agentic threshold; automation support only |
| JtD-4 Submission | 4 | 1 | **4** | Rules/automation (≤7); included for pipeline completeness |
| JtD-5a Monitoring & Notification | 4 | 1 | **4** | Rules/automation (≤7); included for pipeline completeness |

### Volume × Value Quadrant

| | **Low Non-Determinism** | **High Non-Determinism** |
|---|---|---|
| **High Volume** | **JtD-2** Candidate Search (10)<br/>920 ops/day, 80% deterministic<br/><br/>**JtD-4** Submission (4)<br/>184/day, fully deterministic<br/><br/>**JtD-5a** Monitoring (4)<br/>184/day, binary routing | **JtD-3** Match Selection (20) ⭐<br/>184 decisions/day, 100% reasoning-based<br/><br/>**JtD-1** Shift Intake Parsing (12)<br/>184 requests/day, 70% rule-based + 30% judgment |
| **Low Volume** | *(No candidates)* | **JtD-5b** Conflict Resolution (8)<br/>22/day, high reasoning, infrastructure gaps<br/><br/>**JtD-6** No-Show Management (6)<br/>22/day, mixed logic |

**Quadrant interpretation:**

- **Top-right** — Primary Agentic Targets (JtD-3, JtD-1): JtD-3 is the clear standout; JtD-1 sits at the boundary (non-det = 3) — high volume justifies LLM build despite moderate non-determinism.
- **Top-left** — Rules / Automation (JtD-2, JtD-4, JtD-5a): High volume with deterministic logic. Not primary agent use cases, but volume mandates automation. Included in the unified agentic pipeline for shared ServiceNow integration and audit trail (see T4, `specs/3-agentic-solution-architecture.md`).
- **Bottom-right** — Select Agentic Cases (JtD-5b, JtD-6): Lower volume but real reasoning required. Both blocked by infrastructure gaps; Wave 2 when dependencies resolve.
- **Bottom-left** — No candidates; all JtDs have sufficient volume or non-determinism to warrant consideration.

---

## 4. Step 3 — TCO Assessment

**Shared inputs:**
- Fully loaded hourly cost: $26.44/hour (A7: 8 coordinators × $55K/year ÷ 2,000h/year)
- Zone time allocation: 35% parsing / 55% search+selection / 10% submission (A16)
- Matches per year: 46,000 (184/day × 250 working days, A4)
- Claude Sonnet (claude-sonnet-4-6) pricing: $3.00/M input tokens, $15.00/M output tokens (A22)
- FDE build rate: $15,000/week all-in (A21)

---

### JtD-1 — Shift Intake Parsing

```
Use Case: Shift Intake Parsing (JtD-1)
Process: Coordinator workflow / Intake Zone
Volume: 184 cases/day; 46,000/year

Suitability gate:
  Input structure: L
  Decision determinism: M
  Tool coverage: M
  Exception rate: M
  Compliance risk: M
  Gate result: Conditional — passes with LLM approach and 15% HITL routing (A10)

Scoring:
  Execution frequency score: 4
  Non-deterministic effort score: 3
  Agentic value score: 12

Economics:
  Avg time per case (human): 7 min / 0.117h (35% × 20 min, A16)
  Cases per year: 46,000
  Fully loaded hourly cost: $26.44 (A7)
  Annual baseline cost: $142,100

  Estimated tokens per case: ~1,500 input / ~400 output (A22)
  Model: Claude Sonnet (claude-sonnet-4-6)
  Estimated token cost per case: $0.011
  HITL rate: 15% (low-confidence routes to coordinator, A10)
  HITL cost per case: 15% × (5 min × $26.44/60) = $0.33
  Estimated agent cost per case: $0.34
  Annual agent cost: $15,640

  Annual saving: $126,460
  Estimated build cost: $30,000 (2 weeks × $15K/week, A21)
  Payback period: 2.8 months
  Year 1 ROI: 322%

Sequencing:
  Wave: 1
  Key integrations built: ServiceNow read API (reused by JtD-2, JtD-5a); LLM domain prompt (reused by JtD-3)
  Dependencies: ServiceNow API credentials (A11); real shift request samples for prompt calibration (A10)

Delegation archetype: Agent-led + Human Oversight
```

---

### JtD-2 — Candidate Search & Evaluation

```
Use Case: Candidate Search & Evaluation (JtD-2)
Process: Coordinator workflow / Search Zone
Volume: 920 filter ops/day (184 searches × ~5 candidate evaluations, A2, A4); 46,000 searches/year

Suitability gate:
  Input structure: H
  Decision determinism: H
  Tool coverage: M
  Exception rate: M (stale availability, A17)
  Compliance risk: M
  Gate result: Pass

Scoring:
  Execution frequency score: 5
  Non-deterministic effort score: 2
  Agentic value score: 10

Economics:
  Avg time per case (human): 6 min / 0.100h (~30% of 20 min, A16)
  Cases per year: 46,000
  Annual baseline cost: $121,600

  Estimated tokens per case: ~500 input / ~200 output (A22)
    — mostly structured ServiceNow API tool calls; minimal LLM token use
  Model: Claude Sonnet orchestrator + ServiceNow tool calls
  Estimated token cost per case: $0.005
  HITL rate: 5% (stale availability correction, A17)
  HITL cost per case: 5% × (2 min × $26.44/60) = $0.044
  Estimated agent cost per case: $0.049
  Annual agent cost: $2,250

  Annual saving: $119,350
  Estimated build cost: $45,000 (3 weeks × $15K/week, A21)
  Payback period: 4.5 months
  Year 1 ROI: 165%

Sequencing:
  Wave: 1
  Key integrations built: ServiceNow nurse DB query (reused by JtD-3, JtD-5b Wave 2); geocoding API; hospital preference lookup (A12)
  Dependencies: JtD-1 structured output; ServiceNow nurse DB API (A11, A15)

Delegation archetype: Fully Agentic
```

---

### JtD-3 — Match Selection

```
Use Case: Match Selection (JtD-3)
Process: Coordinator workflow / Judgment Zone
Volume: 184 decisions/day; 46,000/year

Suitability gate:
  Input structure: M
  Decision determinism: L
  Tool coverage: L
  Exception rate: M
  Compliance risk: M
  Gate result: Conditional — DD:L and TC:L mitigated by MVP HITL design (A13, A18, A19)

Scoring:
  Execution frequency score: 4
  Non-deterministic effort score: 5
  Agentic value score: 20

Economics:
  Avg time per case (human): 5 min / 0.083h (~25% of 20 min, A16)
  With HITL design: 2 min coordinator review per case (BP4)
  Cases per year: 46,000
  Annual baseline cost: $101,360

  Estimated tokens per case: ~2,000 input / ~600 output (A22)
    — multi-candidate comparison with explanation generation
  Model: Claude Sonnet (claude-sonnet-4-6)
  Estimated token cost per case: $0.015
  HITL rate: 100% (coordinator reviews all at BP4, MVP)
  HITL cost per case: 2 min × $26.44/60 = $0.881
  Estimated agent cost per case: $0.896
  Annual agent cost: $41,216

  Annual saving (labor only): $60,144
  Primary value driver: throughput multiplier → ≥230 matches/coordinator/day vs. ~23 today (M2)
  Revenue recovery target: ≥$1.5M in 6 months post-deployment (M3, A5, A6)

  Estimated build cost: $60,000 (4 weeks × $15K/week, A21)
  Payback period (labor only): ~12 months
  Year 1 ROI (labor only): ~0% — economics require revenue recovery to close
  Year 1 ROI (with $1.5M M3 revenue): ~2,500%

Sequencing:
  Wave: 1
  Key integrations built: Coordinator review UI (HITL, BP4); rule-based ranker; labeled outcome feedback loop (A19 accumulation)
  Dependencies: JtD-1 + JtD-2 output; ServiceNow nurse DB (A11); coordinator UAT session (C2/R1)

Delegation archetype: Agent-led + Human Oversight (MVP) → Fully Agentic Phase 2 (progressive as A19 threshold met)
```

---

### JtD-4 — Submission (Automation Component)

```
Use Case: Submission (JtD-4)
Agentic value score: 4 — automation, not agent; included for pipeline completeness

Economics:
  Annual baseline: 46,000 × 2 min × $26.44/60 = $40,480
  Annual agent cost: ~$460 (minimal API calls, A22)
  Annual saving: ~$40,000
  Build cost: $15,000 (1 week, A21)
  Payback: ~4.5 months
  Key value beyond labor: enables precise M1 (fill-time) measurement with sub-second audit timestamps

Delegation archetype: Fully Agentic
```

---

### JtD-5a — Monitoring & Notification (Automation Component)

```
Use Case: Hospital Response Monitoring + Nurse Notification (MT-5.1/5.2)
Agentic value score: 4 — automation, not agent; included for pipeline completeness

Economics:
  Baseline labor: minimal — coordinators not actively monitoring post-submission today
  Build cost: $15,000 (1 week, A21; shared with notification infrastructure)
  Primary value: enables M4 no-show tracking and closes the confirmation loop (A14 dependency)

Delegation archetype: Fully Agentic
```

---

### JtD-5b — Conflict Resolution (Deferred)

```
Use Case: Decline & Multi-Agency Conflict Resolution (MT-5.3/5.4)
Agentic value score: 8 — borderline; blocked by infrastructure gaps

Gate result: Fail for 8-week window
Primary blockers: no structured nurse decline API (A14 low confidence); no cross-agency visibility (A20);
  conflict detected reactively (MT-5.4 CL:H, TT:H, LC:H)

Wave 2 design: Agent surfaces replacement candidate pool (JtD-2 re-query) + shift timeline status
  on coordinator-triggered conflict event. Full automation deferred until A14 resolves.
```

---

### JtD-6 — No-Show Management (Deferred)

```
Use Case: No-Show Management (JtD-6)
Agentic value score: 6 — below agentic threshold; automation support only

Gate result: Conditional — phone intake (MT-6.1) cannot be automated; MT-6.2 and MT-6.4 are Wave 2
Primary blockers: phone intake has no structured API; emergency time constraints (LC:L); High compliance risk (A9)

Wave 2 design: Agent handles MT-6.2 (profile update + offboard threshold check, A11)
  and MT-6.4 (priority re-entry to JtD-1–4 pipeline via BP6) after coordinator logs the phone intake.
  Requires offboard threshold to be numerically defined (currently informal, per discovery).
```

---

## 5. Step 4 — Feasibility Scoring Matrix

**Scale**: 1 = low feasibility / high risk → 5 = high feasibility / low risk
**Compliance risk**: inverted — 5 = low compliance risk (favorable); 1 = high compliance risk.

| Factor | JtD-1 | JtD-2 | JtD-3 | JtD-4 | JtD-5a | JtD-5b | JtD-6 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Data availability** | 3 | 3 | 2 | 5 | 4 | 2 | 3 |
| **System integration feasibility** | 3 | 3 | 3 | 3 | 3 | 1 | 2 |
| **Compliance risk** | 4 | 3 | 4 | 4 | 4 | 2 | 2 |
| **Context stability** | 4 | 4 | 3 | 5 | 5 | 2 | 3 |
| **Organizational readiness** | 4 | 5 | 3 | 5 | 5 | 3 | 3 |
| **TCO viability** | 5 | 5 | 4 | 4 | 4 | 2 | 3 |
| **Total (/30)** | **23** | **23** | **19** | **26** | **25** | **12** | **16** |

**Factor notes:**

- **JtD-3 data availability (2)**: Hospital preference history is partial (A12); labeled training data for Phase 2 ML ranker unconfirmed (A19). Rule-based ranker at MVP avoids blocking on data dependency (T4 in `specs/3-agentic-solution-architecture.md`).
- **JtD-3 organizational readiness (3)**: Two prior AI failures create trust deficit (C2, R1). HITL architecture mitigates; coordinator shadow session required before launch.
- **JtD-3 TCO viability (4)**: Direct labor saving alone barely closes ($60K saving vs. $60K build); primary ROI depends on M3 revenue recovery (A5, A6). If A5/A6 assumptions are wrong, the economic case weakens significantly.
- **JtD-5b system integration (1)**: Hard infrastructure gap — no inbound nurse response API, no cross-agency coordination platform (A14, A20). Not a build effort problem; the external system simply does not exist.
- **JtD-6 compliance risk (2)**: Patient care continuity + hospital relationship + demonstrated commercial consequences (discount given to at least one hospital, per discovery). Emergency time constraints reduce error recovery window.

---

## 6. Step 5 — Strategic Sequencing

### Wave 1 — Self-Funding Foundation (8-week MVP)

All five standard pipeline JtDs (JtD-1, 2, 3, 4, 5a) constitute a single dependency chain. Building any subset without the rest leaves the economic case incomplete.

**Build sequence** (dependency-driven, not value-ranked):

| Build Order | JtD | Rationale | Shared Asset Built |
|:---:|---|---|---|
| 1 | JtD-1 Parsing | BP2 is the pipeline gate; no downstream automation runs without structured parser output | ServiceNow read API; LLM domain prompt |
| 2 | JtD-2 Search | Depends on JtD-1 structured output; builds nurse DB query infrastructure | Nurse DB query layer; geocoding API; preference lookup |
| 3 | JtD-3 Ranker + UI | Depends on JtD-1+2; most complex build; coordinator UAT required | Coordinator review UI; rule-based ranker; labeled feedback loop (A19) |
| 4 | JtD-4 Submission | Depends on JtD-3 BP4 approval event; completes the revenue-generating loop | ServiceNow write API; full audit trail |
| 5 | JtD-5a Monitoring | Depends on JtD-4 submission event; closes the confirmation loop | Notification trigger; response capture (contingent on A14) |

**Wave 1 economics:**
- Total build cost: ~$120,000 (8-week engagement, A21; JtD-3 build overlaps JtD-1+2 in parallel)
- Annual labor savings: ~$346,000/year (JtD-1: $126K + JtD-2: $119K + JtD-3: $60K + JtD-4: $40K + JtD-5a: indirect)
- Revenue recovery (M3, 6-month target): ≥$1.5M (A5, A6 — low confidence; treat as hypothesis)
- Year 1 return: ~$1.85M (labor + conservative M3)
- Year 1 ROI: ~1,440%

**Wave 1 funds Wave 2**: The $346K annual labor saving alone pays back the $120K build in 4.2 months. Wave 2 investment is fully available from Wave 1 operating savings without requiring M3 revenue recovery to materialize.

---

### Wave 2 — Compounding (Months 3–6, post-MVP)

Wave 2 reuses Wave 1 integrations at marginal cost. Lower incremental build cost; higher cognitive complexity.

| JtD | Wave 2 Scope | Dependencies Resolved by Wave 1 |
|---|---|---|
| JtD-3 ML Ranker Upgrade | Replace rule-based ranker with supervised ML model | A19: ~3 months of live coordinator decisions = ~8,000–11,000 labeled examples (184 fills/day × 60 working days × ~50% structured capture) |
| JtD-6 MT-6.2 + MT-6.4 | Profile update automation + emergency re-fill via priority queue (BP6) | ServiceNow write API (JtD-4); JtD-1–4 pipeline for re-entry; offboard threshold must be numerically defined |
| JtD-5b Data Surfacing | Agent surfaces replacement candidates + shift status on conflict trigger | JtD-2 search infrastructure; response tracking (A14 must be resolved) |

---

### Wave 3 — AI-Native Operations (Year 2)

| Capability | Prerequisite |
|---|---|
| JtD-3 progressive autonomy (auto-submit on high-confidence matches) | Ranker accuracy validated above coordinator baseline; threshold lowered progressively |
| JtD-5b full automation | Cross-agency coordination mechanism available; nurse-decline structured API (A14) resolved |
| Multi-agent coordination | Parallel matching at scale; priority queue management; predictive no-show detection |

---

## 7. Prioritized Candidate Shortlist

| Rank | JtD | Name | Value Score | Feasibility (/30) | Gate | Wave | MVP Archetype | Primary Constraint |
|:---:|---|---|:---:|:---:|---|:---:|---|---|
| 1 | JtD-3 | Match Selection | 20 | 19 | Conditional | 1 | Agent-led + HITL | Tacit knowledge unencoded (A18); training data dependency (A19); two prior AI failures (C2) |
| 2 | JtD-1 | Shift Intake Parsing | 12 | 23 | Conditional | 1 | Agent-led + HITL | Free-text input structure (L); 15% HITL rate (A10) |
| 3 | JtD-2 | Candidate Search | 10 | 23 | Pass | 1 | Fully Agentic | Stale availability (~15–20%, A17); ServiceNow API provisioning (A11) |
| 4 | JtD-5a | Monitoring & Notification | 4 | 25 | Pass | 1 | Fully Agentic | Response tracking capability uncertain (A14); indirect ROI |
| 5 | JtD-4 | Submission | 4 | 26 | Pass | 1 | Fully Agentic | ServiceNow write API provisioning (A11) |
| 6 | JtD-6 | No-Show Management | 6 | 16 | Conditional | 2 | Human-led + Automation Support | Phone intake (no API); High compliance risk; offboard threshold undefined |
| 7 | JtD-5b | Conflict Resolution | 8 | 12 | Fail (8-wk) | 2–3 | Human-led + Agent Support | No nurse-decline API; no cross-agency visibility (A14, A20) |

**Ranking rationale:**

- **JtD-3 at #1 despite conditional gate**: Highest value score (20) and the primary economic lever ($200M throughput target, M3 revenue recovery). The conditional gate issues are addressed by HITL design — not by deferral. This is the use case the entire Wave 1 build exists to deliver.
- **JtD-1 at #2 despite lower value score than JtD-2**: JtD-1 is the BP2 pipeline gate. Without the parser, JtD-2 and JtD-3 cannot run. Build sequence requires JtD-1 first regardless of relative value score.
- **JtD-2 at #3**: Highest feasibility score among agentic candidates (23/30); second-largest labor saving ($119K/year); passes the suitability gate outright.
- **JtD-5a at #4 over JtD-4**: Both are automation components (value score 4). JtD-5a (monitoring) closes the confirmation loop and enables M4 tracking — higher strategic value than JtD-4's pure execution function, though JtD-4 must be built first in the dependency chain.
- **JtD-6 at #6 over JtD-5b**: Higher feasibility (16 vs. 12) and a clear automation path for downstream sub-tasks (MT-6.2, MT-6.4). JtD-5b has harder infrastructure blockers.

### Sequencing funding logic

| Wave | Funds Next Wave Via |
|---|---|
| Wave 1 | $346K/year labor savings pays back $120K build in 4.2 months; surplus funds Wave 2 development. JtD-3 feedback loop (A19) accumulates labeled data for Wave 2 ML ranker upgrade. Wave 1 ServiceNow integrations are reused by Wave 2 JtD-6 and JtD-5b at marginal cost. |
| Wave 2 | Expanded throughput from JtD-3 ML ranker (higher auto-submit rate, lower HITL overhead) reduces per-match cost and generates additional labor savings. Wave 2 ROI funds Wave 3 multi-agent architecture. |
| Wave 3 | Progressive JtD-3 autonomy compounds Wave 1 throughput gains. At full autonomy (post-HITL), coordinator capacity equivalent to ~230+ matches/day is reallocated to exception management and relationship work rather than review. |

---

*See `specs/assumptions.md` for all assumptions referenced in this document (A1–A22).*
