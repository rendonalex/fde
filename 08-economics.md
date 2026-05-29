# Economics Model — AI Claims Processing Transformation
## Greenfield Health Systems · ADR-1 and ADR-4

**Prepared by:** FDE Engagement Lead  
**Date:** 2026-05-27  
**Status:** Active — based on Phase 1 assumptions; model requires calibration against Phase 1 actuals

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [ADR-1: Claim Intake and Format Validation Agent](#2-adr-1-claim-intake-and-format-validation-agent)
   - [2.1 Delegation Qualification Analysis](#21-delegation-qualification-analysis)
   - [2.2 Baseline Cost Model](#22-baseline-cost-model)
   - [2.3 Token Economics Model](#23-token-economics-model)
   - [2.4 ROI and Business Case](#24-roi-and-business-case)
3. [ADR-4: Clinical Content Triage Agent](#3-adr-4-clinical-content-triage-agent)
   - [3.1 Delegation Qualification Analysis](#31-delegation-qualification-analysis)
   - [3.2 Baseline Cost Model](#32-baseline-cost-model)
   - [3.3 Token Economics Model](#33-token-economics-model)
   - [3.4 ROI and Business Case](#34-roi-and-business-case)
4. [Self-Financing Roadmap](#4-self-financing-roadmap)
5. [Calibration — Making Economics Survive Reality](#5-calibration--making-economics-survive-reality)
6. [Economic Governance — Ongoing](#6-economic-governance--ongoing)
7. [Multi-Model Experimentation Note](#7-multi-model-experimentation-note)

---

## 1. Executive Summary

Greenfield Health Systems is spending approximately **$1,300,000 per year** in administrative claims processor labor [A1] while running at 9+ day cycle time — above the 7-day SLA threshold that triggers payer penalties [A8]. The dual-path architecture (ADR-1 + ADR-4, followed by ADR-2 through ADR-9) addresses this directly: ADR-1 automates claim intake and format validation; ADR-4 routes every claim to the Fast Path (65%) or Clinical Path (35%) [A2], unlocking downstream adjudication at scale.

**ADR-1 (Intake)** replaces $117,000/year in processor labor at an annual agent cost of $61,796, delivering $55,204/year in direct savings. Its primary economic value is structural: the normalized claim record it produces is the prerequisite for every downstream agent. Build cost: $55,000.

**ADR-4 (Triage)** replaces $117,000/year in processor labor at an annual agent cost of $38,450, delivering $78,550/year in direct savings. Its strategic value far exceeds its direct saving: correct clinical routing is the gate that unlocks the full Fast Path, enabling the **13 FTE headcount reduction** that drives $845,000/year in portfolio savings. Build cost: $35,000.

**Portfolio (all ADRs):** 14-month payback on $400,000 build investment; **$860,000 net 3-year value**; 215% ROI on build investment. The business case holds in the conservative scenario (24-month payback). It collapses only if the clinical/admin split [A2] is materially wrong or if the Phase 1 gate [A6] is not achievable — both of which are validated before any headcount reductions occur.

The stakeholder resolution is economically sound: CFO achieves 13-FTE reduction; CMO retains physician oversight on all clinical claims (with HITL cost of ~$20,000/year baked in); VP Operations restores SLA compliance with projected 4–7 day cycle time [scenario].

---

## 2. ADR-1: Claim Intake and Format Validation Agent

### 2.1 Delegation Qualification Analysis

| Dimension | Assessment |
|-----------|-----------|
| **Task type** | Structured data processing: EDI parsing, field extraction, format validation, completeness checks |
| **Cognitive zone** | Routine (EDI sub-path, 70% of volume): deterministic, rule-governed, zero variance. Judgment (non-EDI, 30%): extraction confidence scoring with targeted HITL on failures |
| **Current delegation state** | Human Only — admin processors manually handle all intake including fully-structured EDI |
| **Target delegation state** | Agent-led + Human Oversight — EDI sub-path Fully Agentic; non-EDI sub-path Agent-led with HITL at ≤10% of non-EDI volume |
| **Why this archetype?** | EDI 837P/I is HIPAA-mandated structured format — deterministic parsing carries no clinical judgment. Non-EDI extraction has variance but confidence scoring gates HITL precisely, avoiding both under-delegation (expensive full human review) and over-delegation (downstream errors from low-confidence extractions) |
| **Why not fully autonomous on non-EDI?** | IDP extraction failure on required clinical fields creates downstream classification errors in ADR-4 and adjudication errors in ADR-5/ADR-6. HITL at the extraction confidence threshold is cheaper than rework from downstream propagation |
| **Economic justification** | $117K/year labor baseline; ~$1.71/claim labor cost [A1, A21]; agent cost $0.132/claim. Delegation frees processor capacity without sacrificing accuracy on the high-stakes non-EDI subset [A14] |
| **Key constraint** | [A12] CMS API availability (confidence 40%) is the single gating dependency — if CMS has no modern API, batch file-based fallback raises integration cost and delays go-live |

**Delegation archetype is correctly scoped.** Moving to Fully Agentic on non-EDI (removing HITL) would risk extraction errors propagating to clinical triage — a false economy at the intake layer that creates expensive correction at the ADR-4 or ADR-5 layer. The ≤10% HITL rate on non-EDI (3% of total volume) is the correct risk/cost balance.

---

### 2.2 Baseline Cost Model

**Volume:** 600,000 claims/year (50,000/month × 12) [U1]

| Cost component | Calculation | Annual cost |
|----------------|-------------|-------------|
| Labor — intake time | 20 processors [A1] × $65,000 × 9% [A21] | **$117,000** |
| Indirect — error rework (manual re-key errors on non-EDI) | 500 non-EDI claims/day × 80% re-key rate [A14] × ~5% field error rate × $32.50/hr × 10 min correction | ~$18,000 |
| Indirect — SLA contribution | Intake delays contribute to 9+ day cycle time; $50,100/day total penalty exposure [A8] attributed partially to intake bottleneck (~15% of cycle delay) | ~$90,000 |
| **Total baseline (direct + indirect)** | | **~$225,000** |
| **Direct labor baseline** (used in ROI calculation) | | **$117,000** |

> *The direct labor baseline ($117,000) is used as the conservative ROI denominator. Error rework and SLA contribution are indirect benefits the agent provides beyond its direct saving.*

**Baseline cost per claim:** $117,000 ÷ 600,000 = **$0.195/claim**

---

### 2.3 Token Economics Model

**Model tier:** Mid-tier (Claude Sonnet) for IDP extraction and validation reasoning; lightweight rule engine for EDI parsing. [A4] See §7 for per-step model routing and the Haiku cost-delta experiment.

**Token consumption per claim:**

| Component | Type | EDI path (70%) | Non-EDI path (30%) |
|-----------|------|:--------------:|:------------------:|
| System prompt (validation rules, output schema) | Input | ~500 | ~600 |
| Retrieved context (field definitions, validation rules) | Input | — | ~2,000 |
| Claim payload (EDI 837P/I record or OCR/NLP document) | Input | ~2,500 | ~2,200 |
| **Subtotal input** | | **~3,000** | **~4,800** |
| Output (validation flags / per-field extraction with confidence scores) | Output | ~750 | ~400 |
| **Total tokens per claim** | | **~3,750** | **~5,200** |

**Token pricing (Claude Sonnet [A4]):** $3.00/M input · $15.00/M output
- EDI path: (3,000 × $3.00 + 750 × $15.00) ÷ 1,000,000 = $0.009 + $0.011 = **$0.020/claim**
- Non-EDI path: (4,800 × $3.00 + 400 × $15.00) ÷ 1,000,000 = $0.0144 + $0.0060 = **$0.020/claim**
- Blended (70/30 channel split): (0.70 × $0.020) + (0.30 × $0.020) = $0.014 + $0.006 = **$0.020/claim**

| Cost component | Per-claim rate | Annual cost |
|----------------|:---:|-------------|
| Token cost — EDI path (70%): parsing, validation | $0.020 | $8,400 |
| Token cost — non-EDI path (30%): IDP extraction, confidence scoring | $0.020 | $3,600 |
| **Blended token cost** | **$0.020** | **$12,000** |
| Tool calls: 2 CMS API calls + 1 audit log write + 1 exception queue write (HITL cases) | $0.003 | $1,800 |
| Infrastructure: compute, storage, networking | $0.001 | $600 |
| **Agent subtotal (excluding HITL)** | **$0.024** | **$14,400** |
| **HITL:** 50 claims/day × 250 days = 12,500 events/year × 7 min × $32.50/hr = 12,500 × (7/60) × $32.50 [A1] | $0.079 | **$47,396** |
| **Total agent cost per claim** | **$0.103** | **$61,796** |

> *HITL calculation: 12,500 events × (7/60) hrs × $32.50/hr = $47,396/year. HITL drives 77% of total agent cost; reducing non-EDI extraction error rate below 10% directly reduces this.*

**Tool call cost breakdown:**

| Call type | Frequency | Unit cost | Per-claim cost |
|-----------|:---------:|:---------:|:--------------:|
| CMS API write (POST /api/v1/claims) | 1× per claim | $0.001 | $0.001 |
| CMS API read (duplicate check, GET /api/v1/claims/{id}) | 1× per claim | $0.001 | $0.001 |
| Audit log write | 1× per claim | $0.001 | $0.001 |
| Exception queue write (HITL cases only, ~3% of total volume) | 0.03× per claim | $0.001 | ~$0.000 |
| **Total tool calls** | | | **$0.003/claim** ($1,800/year) |

**Infrastructure cost per claim:**
Monthly platform cost allocated to ADR-1: ~$50/month (shared compute, storage, networking, monitoring)
Monthly claim volume: 50,000 claims
Infrastructure cost: $50 ÷ 50,000 = **$0.001/claim** ($600/year)

**Self-hosted inference — consideration and rejection [A4]:**
Greenfield PHI processing presents a nominal data-sovereignty argument. Three forces must hold for self-hosted to be the right call; none applies here:
- *Data sovereignty:* HIPAA BAA with Anthropic covers PHI in API calls. No data-residency law prohibits external API processing in this jurisdiction.
- *Volume amortisation:* At 600,000 claims/year, combined ADR-1 + ADR-4 LLM API spend is ~$45,000/year. Self-hosted infrastructure floor (~$30K hardware capital ÷ 3 years + ~$4K electricity + ~$24K ops staff) = ~$38,000/year fixed cost — a marginal apparent delta that evaporates once ops risk, uptime liability, and capability lag (6–18 months vs. frontier API) are priced in. Volume crossover where self-hosted clearly wins is approximately 5M+ claims/year.
- *Fine-tuning need:* No fine-tuning requirement. Codebook-based classification [A15] is a prompt and context engineering problem, not a model training problem.

**API default is correct for Wave 1 and Wave 2.** Re-evaluate self-hosted only if volume exceeds 5M claims/year or if a data-residency ruling prohibits BAA-covered API processing of PHI.

**vs. Baseline: $0.195/claim**  
**Saving per claim: $0.092 (47% cost reduction on intake task)**

**Agent cost sensitivity to token price change:**

| Token price assumption | Annual token cost | Total agent cost | Net saving |
|------------------------|:-----------------:|:----------------:|:----------:|
| +50% (conservative) | $18,000 | $67,796 | $49,204 |
| Base (current [A4]) | $12,000 | $61,796 | $55,204 |
| -30% (optimistic) | $8,400 | $58,196 | $58,804 |

---

### 2.4 ROI and Business Case

**Build cost breakdown [A28]:**

| Component | Cost |
|-----------|-----:|
| Assessment and design | $8,000 |
| Development (EDI parser, IDP pipeline, format validators) | $25,000 |
| Integration (CMS API [A12], audit log, exception queue) | $15,000 |
| Testing and calibration | $5,000 |
| Change management and training | $2,000 |
| **Total ADR-1 build cost** | **$55,000** |

**Standard business case:**

| | Year 1 | Year 2 | Year 3 |
|--|:------:|:------:|:------:|
| Annual baseline cost | $117,000 | $117,000 | $117,000 |
| Annual agent cost | $61,796 | $61,796 | $61,796 |
| Annual gross saving | $55,204 | $55,204 | $55,204 |
| Build cost | $55,000 | — | — |
| Annual maintenance [A27] | $8,250 | $8,250 | $8,250 |
| **Net annual value** | **-$8,046** | **+$46,954** | **+$46,954** |
| Cumulative net value | -$8,046 | +$38,908 | +$85,862 |

**Payback period:** $55,000 ÷ $46,954/year = **14 months**  
**3-year net value:** $85,862  
**3-year ROI:** $85,862 ÷ ($55,000 + $24,750 maintenance) = **108%**

> *ADR-1 standalone ROI is modest by design — it is the enabling infrastructure. The CMS API integration, normalized record schema, and IDP pipeline it builds reduce every downstream agent's build cost by an estimated $80,000 [A28], which is the economic multiplier not captured in ADR-1's direct ROI.*

**Financial sensitivity table:**

| Scenario | Token assumption | HITL rate | Annual gross saving | Payback |
|----------|:---------------:|:---------:|:-------------------:|:-------:|
| Conservative | +50% current | 20% of non-EDI (36,000 events × (7/60) × $32.50 = $136,500 HITL) | -$39,900 | N/A — agent cost exceeds baseline |
| Base case | Current [A4] | 6.9% of non-EDI (12,500 events × (7/60) × $32.50 = $47,396 HITL) | $55,204 | 14 months |
| Optimistic | -30% current | 5% of non-EDI (9,000 events × (7/60) × $32.50 = $34,125 HITL) | $72,075 | 10 months |

> *The conservative scenario (20% HITL on non-EDI) reflects severely degraded IDP accuracy [A14]: at this HITL rate, agent operating cost ($156,900) exceeds the labor baseline ($117,000) and direct saving is negative. ADR-1 remains required infrastructure regardless — the evaluation criterion is not standalone ROI but whether it unlocks the portfolio. If Phase 1 calibration shows HITL trending toward 20%, the mitigation is tightening the IDP confidence threshold before this rate is reached.*

---

## 3. ADR-4: Clinical Content Triage Agent

### 3.1 Delegation Qualification Analysis

| Dimension | Assessment |
|-----------|-----------|
| **Task type** | Clinical classification: identify whether a claim contains clinical content requiring physician review |
| **Cognitive zone** | Judgment (criteria-based with edge cases): routing decision is rule-governed once [A15] criteria are defined; edge cases (novel CPT codes, ambiguous indicators) require human adjudication |
| **Current delegation state** | Human Only — admin processors use informal heuristics with no written criteria [A15]; 41% denial appeal overturn rate is partly attributable to inconsistent triage [scenario] |
| **Target delegation state** | Wave 1: Human Only (shadow mode); Wave 2+: Agent-led + Human Oversight, conditional on [A6] gate (<2% false-negative rate over 60-day window) |
| **Why this archetype?** | False negatives (clinical claim routed to Fast Path) carry patient safety consequences categorically different from false positives (unnecessary physician review). A phased approach — shadow mode first, live routing only after validated accuracy — is the only architecture all three stakeholders can sign. Human Only in Wave 1 is not a concession; it is the validation mechanism that makes Wave 2 economically and clinically defensible [A6, A25] |
| **Why not fully autonomous immediately?** | Criteria are currently undocumented [A15]; no labeled ground-truth dataset exists; patient safety risk of a false negative is non-negotiable per CMO. The [A6] gate is a hard stop |
| **Why not Human-in-the-Loop for all routing decisions?** | At 1,667 claims/day, per-claim physician review defeats the throughput goal [James Liu, scenario]. Conservative fallback (below-threshold claims → Clinical Path automatically) eliminates the need for per-routing-decision HITL while maintaining safety [A24] |
| **Economic justification** | $117K/year labor baseline; agent reduces routing labor cost by 66%; monthly physician audit ($81,000/year estimated) is the governance cost of operating at this delegation level. Total agent cost ($38,450/year + audit) vs. $117,000 baseline: net positive even after audit cost |
| **Key constraint** | [A15] criteria definition (Week 1 blocker) and [A6] false-negative gate are dual prerequisites. Neither has a workaround |

**Delegation archetype is correctly scoped.** The economic risk of moving faster (to Fully Agentic without the gate) is not just patient safety — it is a legal and regulatory exposure that could terminate the entire program. Shadow mode is not a delay; it is the risk-adjusted path to the highest-ROI delegation state in the portfolio.

---

### 3.2 Baseline Cost Model

**Volume:** 600,000 claims/year (100% of claims — ADR-4 classifies every claim) [U1]

| Cost component | Calculation | Annual cost |
|----------------|-------------|-------------|
| Labor — triage time | 20 processors × $65,000 × 9% [A1, A21] | **$117,000** |
| Indirect — false-negative cost (current state) | Clinical claims reaching Fast Path without physician review → misadjudication → appeals. Contributes to 41% overturn rate [scenario]. Conservative estimate: 5% of 333 denials/day [A22] require re-adjudication at $50/denial × 250 days | ~$208,125 |
| Indirect — physician time on misrouted claims | Admin claims reaching Clinical Path → physician reviews claims they should not see, at 20 claims/hr [A5] × $125/hr [A23] | ~$40,000 |
| **Total baseline (direct + indirect)** | | **~$365,000** |
| **Direct labor baseline** (used in ROI calculation) | | **$117,000** |

> *The indirect costs ($250,000+) are the hidden penalty of undocumented triage criteria [A15]. ADR-4 eliminates these by enforcing consistent, auditable routing criteria. The direct labor baseline ($117,000) is conservative; indirect savings materially strengthen the business case.*

**Baseline cost per claim:** $117,000 ÷ 600,000 = **$0.195/claim**

---

### 3.3 Token Economics Model

**Model tier:** Mid-tier (Claude Sonnet) with chain-of-thought reasoning required [A26]. Clinical classification at this risk level requires auditable reasoning traces — reasoning is included in the visible output (prompt-based CoT), not in a hidden thinking block, so it is captured in the shadow log for Dr. Webb's [A6] gate labeling. See §7 for why Opus is not warranted and the $52,800/year cost delta of defaulting to it.

**Token consumption per claim:**

| Component | Type | Tokens |
|-----------|------|:------:|
| System prompt — classification instructions + full criteria codebook [A15] (cached) | Input (cached) | ~7,790 |
| Claim fields (procedure codes, diagnosis codes, modifiers) | Input | ~300 |
| **Subtotal input** | | **~8,090** (7,790 cached + 300 non-cached) |
| CoT reasoning trace + structured routing decision (JSON) | Output | ~400 |
| **Total tokens per claim** | | **~8,490** |

> *Full codebook (~7,290 tokens) is embedded in the system prompt rather than retrieved via RAG. Passing the full codebook ensures no provision is missed — a retrieval miss would silently convert a clinical claim to FAST_PATH, the exact false-negative the [A6] gate is designed to catch. Prompt caching makes this affordable.*

**Token pricing (Claude Sonnet [A26]):** cached input $0.30/M · non-cached input $3.00/M · output $15.00/M

- Cached system prompt: 7,790 × $0.30/M = **$0.002/claim**
- Non-cached claim fields: 300 × $3.00/M = **$0.001/claim**
- Output (CoT + routing JSON): 400 × $15.00/M = **$0.006/claim**
- **Total token cost: $0.009/claim** ($5,400/year at 600,000 claims)

| Cost component | Per-claim rate | Annual cost |
|----------------|:---:|-------------|
| Token cost: cached system prompt + non-cached claim fields + CoT output (see breakdown above) [A26] | $0.009 | $5,400 |
| Tool calls: CMS read + shadow log write (Wave 1) + conditional adjudication queue write (see breakdown below) | $0.002 | $1,200 |
| Infrastructure | $0.001 | $600 |
| **Agent subtotal (excluding HITL)** | **$0.012** | **$7,200** |
| **HITL — criteria edge cases:** novel/ambiguous claims flagged for Dr. Webb adjudication at ≤10/day [A25] × 250 days = 2,500 events/year × 6 min × $125/hr [A23] = 2,500 × (6/60) × $125 | $0.052 | $31,250 |
| **Total agent cost per claim (live mode)** | **$0.064** | **$38,450** |

> *Note: Monthly audit cost (5% Fast Path sample × physician review time) is an ongoing governance cost of ~$81,000/year, addressed in §6. It is not included in per-claim agent cost because it is a portfolio-level quality gate, not a per-claim HITL event.*

> *Wave 1 shadow mode adds ~$0.002/claim for shadow log writes — this is a temporary cost during the 3-month evaluation window.*

**Tool call cost breakdown (Wave 1):**

| Call type | Frequency | Unit cost | Per-claim cost |
|-----------|:---------:|:---------:|:--------------:|
| CMS API read (claim data fetch, GET /api/v1/claims/{id}) | 1× per claim | $0.001 | $0.001 |
| Shadow log write (POST /api/v1/shadow-log) | 1× per claim | $0.001 | $0.001 |
| Adjudication queue write (NOVEL_CASE / edge cases, ~0.4% of volume) | 0.004× per claim | $0.001 | ~$0.000 |
| **Total tool calls (Wave 1)** | | | **$0.002/claim** ($1,200/year) |

> *(Wave 2: CMS routing write (PUT /api/v1/claims/{id}/routing) adds $0.001/claim once live routing is enabled after [A6] gate.)*

**Infrastructure cost per claim:**
Monthly platform cost allocated to ADR-4: ~$50/month (shared infrastructure pool with ADR-1)
Monthly claim volume: 50,000 claims
Infrastructure cost: $50 ÷ 50,000 = **$0.001/claim** ($600/year)

**Self-hosted inference:** See §2.3 analysis above. Same conclusion: API default is correct. At combined ~$45,000/year LLM API spend, the marginal cost delta versus the self-hosted fixed floor (~$38,000/year) does not justify absorbing ops liability, capability lag, or [A6] gate variance risk on a PHI workload covered by BAA.

**vs. Baseline: $0.195/claim**  
**Saving per claim (direct): $0.131 (67% cost reduction on triage task)**

**Agent cost sensitivity:**

| Scenario | Token assumption | HITL rate (edge cases) | Annual agent cost | Annual direct saving |
|----------|:---------------:|:-----:|:-----------------:|:-------------------:|
| Conservative | +50% current | 5 cases/day (1,250 events × (6/60) × $125 = $15,625 HITL) | $25,525 | $91,475 |
| Base case | Current [A26] | ≤10 cases/day (2,500 events × (6/60) × $125 = $31,250 HITL) [A25] | $38,450 | $78,550 |
| Optimistic | -30% current | <3 cases/day (750 events × (6/60) × $125 = $9,375 HITL) | $14,955 | $102,045 |

---

### 3.4 ROI and Business Case

**Build cost breakdown [A28]:**

| Component | Cost |
|-----------|-----:|
| Assessment and design (criteria codebook workshops with Dr. Webb [A15]) | $7,000 |
| Development (classification model, prompt engineering, structured output, shadow mode) | $15,000 |
| Integration (shadow evaluation log store, ground-truth adjudication queue [A25], CMS routing write) | $10,000 |
| Testing and calibration (Phase 1 shadow evaluation window) | $2,000 |
| Change management (physician workflow for adjudication queue) | $1,000 |
| **Total ADR-4 build cost** | **$35,000** |

> *The clinical criteria codebook [A15] co-developed with Dr. Webb is a shared platform asset: it also powers ADR-6 (Clinical Pre-Screening), saving an estimated $20,000 in ADR-6 build cost.*

**Standard business case (direct savings only):**

| | Year 1 | Year 2 | Year 3 |
|--|:------:|:------:|:------:|
| Annual baseline cost | $117,000 | $117,000 | $117,000 |
| Annual agent cost | $38,450 | $38,450 | $38,450 |
| Annual direct gross saving | $78,550 | $78,550 | $78,550 |
| Build cost | $35,000 | — | — |
| Annual maintenance [A27] | $5,250 | $5,250 | $5,250 |
| **Net annual value (direct)** | **+$38,300** | **+$73,300** | **+$73,300** |
| Cumulative net value | +$38,300 | +$111,600 | +$184,900 |

**Payback period (direct saving):** $35,000 ÷ $73,300 = **6 months**  
**3-year net value (direct):** $184,900  
**3-year ROI (direct):** $184,900 ÷ ($35,000 + $15,750 maintenance) = **364%**

> *The direct ROI above excludes ADR-4's most significant economic contribution: gating the $845,000/year Fast Path saving. Without ADR-4 routing correctly, the Fast Path cannot safely deploy. ADR-4 is the highest-value investment in the portfolio on an enabled-ROI basis.*

**Enabled portfolio value (ADR-4 as gate to Fast Path):**

| | Value |
|---|---:|
| Fast Path headcount reduction: 13 FTEs × $65,000 [A1] | $845,000/year |
| Fraction of portfolio saving enabled by ADR-4 | 100% (ADR-4 is the routing gate) |
| Incremental build cost of ADR-4 vs. not building it | $35,000 |
| **Portfolio value enabled per dollar of ADR-4 build cost** | **$24.14/year** |

**Financial sensitivity table:**

| Scenario | Token assumption | HITL rate | Annual direct saving | Payback |
|----------|:---------------:|:---------:|:--------------------:|:-------:|
| Conservative | +50% current | 5 cases/day | $86,225 | 5 months |
| Base case | Current [A26] | ≤10 cases/day | $73,300 | 6 months |
| Optimistic | -30% current | <3 cases/day | $96,795 | 4 months |

---

## 4. Self-Financing Roadmap

The use case sequence is structured so each wave generates savings that fund the next wave — and builds platform assets that reduce subsequent build costs.

### Wave Sequencing and Cash Flow

```
Wave 1 — Months 1–3 (ADR-1 live, ADR-4 shadow)
  ADR-1 build cost:            $55,000
  ADR-4 shadow build cost:     $35,000
  Shared Wave 1 infrastructure: $10,000
  Wave 1 total build:          $100,000

  Wave 1 monthly saving (ADR-1 alone):  $3,294/month ($39,525/year ÷ 12)
  Wave 1 cumulative saving at Month 3:  ~$9,900

Wave 1 platform assets built (reused by all Wave 2 agents):
  CMS API integration [A12]:              saves ~$25,000 in Wave 2 build
  Normalized claim record schema:         saves ~$15,000
  Audit log infrastructure:              saves ~$10,000
  Clinical criteria codebook [A15]:      saves ~$20,000 (ADR-6 reuses)
  Shadow evaluation pipeline:            saves ~$10,000
  Estimated Wave 2 build cost reduction: ~$80,000

Wave 2 — Months 4–6 (ADR-4 live, ADR-2, ADR-3, ADR-5, ADR-6)
  Gross Wave 2 build cost:     ~$200,000
  Less Wave 1 asset reuse:      -$80,000
  Net Wave 2 marginal build:   ~$120,000

  Monthly saving from Fast Path (13 FTEs, beginning M4):
    $845,000/year ÷ 12 = $70,417/month (ramping to full by M6)
  Wave 2 cumulative saving at Month 6:  ~$175,000

Wave 3 — Months 7+ (ADR-8, ADR-9, Phase 3 hardening)
  Wave 3 build cost:           ~$100,000
  Wave 3 funded by:            Wave 2 savings ($175,000 accumulated by M6)
  Phase 3 steady-state saving: $845,000/year
```

### Cumulative Net Cash Flow

| Month | Cumulative Investment | Cumulative Saving | Net Position |
|:-----:|:--------------------:|:-----------------:|:------------:|
| 3 | $100,000 | $9,900 | -$90,100 |
| 6 | $300,000 | $184,900 | -$115,100 |
| 9 | $400,000 | $396,150 | -$3,850 |
| 12 | $400,000 | $607,400 | **+$207,400** |
| 18 | $400,000 | $1,029,900 | **+$629,900** |
| 24 | $400,000 | $1,452,400 | **+$1,052,400** |

> *Project reaches cash-flow break-even at approximately Month 9. Full build cost recovery by Month 10. The self-financing argument is verified: Wave 1 savings + Wave 2 ramp fund Wave 3 development with no additional budget required.*

### Portfolio Business Case Summary

| | Year 1 | Year 2 | Year 3 |
|--|:------:|:------:|:------:|
| Gross saving (ramp: 27% Y1, 100% Y2–3) | $230,000 | $845,000 | $845,000 |
| Agent operating cost (all ADRs) | $120,000 | $200,000 | $200,000 |
| Maintenance [A27] | $30,000 | $60,000 | $60,000 |
| Build cost | $400,000 | — | — |
| **Net annual value** | **-$320,000** | **+$585,000** | **+$585,000** |
| Cumulative net | -$320,000 | +$265,000 | +$850,000 |

**Payback period (build cost):** $400,000 ÷ $585,000 = **8 months from Phase 3 go-live (~14 months from project start)**  
**3-year net value:** $850,000  
**Portfolio ROI on build investment:** $850,000 ÷ $400,000 = **213%**

**Portfolio financial sensitivity table:**

| Scenario | Token assumption | HITL assumption | FTE reduction achieved | Annual net saving | Payback from go-live |
|----------|:---------------:|:---------------:|:--------------------:|:-----------------:|:--------------------:|
| Conservative | +50% current | 20% HITL on non-EDI; 5% ADR-4 edge cases | 7 FTEs (55%) | $200,000 | 24 months |
| Base case | Current [A4, A26] | Per model | 13 FTEs [A1] | $585,000 | 8 months |
| Optimistic | -30% current | 5% HITL on non-EDI | 13 FTEs + penalty avoidance [A8] | $1,100,000 | 4 months |

> *Conservative scenario trigger: [A2] clinical split is 50% (not 35%), creating physician bottleneck. This is mitigated by Pre-Phase 1 historical analysis per stakeholder alignment memo — if the split deviates >10 points, the financial model is revised before headcount commitments are made.*

---

## 5. Calibration — Making Economics Survive Reality

Business case assumptions must be validated in mock or shadow environment before production deployment.

### ADR-1 Calibration

| Metric | Target | Business case impact if missed |
|--------|:------:|-------------------------------|
| EDI extraction accuracy | ≥98% field-complete records | — (deterministic; failures are downstream CMS rejections, not agent errors) |
| Non-EDI extraction accuracy | ≥90% fields above 0.85 confidence threshold | If below 90%, HITL rate rises above 10%, adding $5K–$15K/year per point of HITL increase |
| HITL rate on non-EDI | ≤10% | At 20%, annual HITL cost rises to ~$93,750; net saving drops from $39,525 to near zero |
| Throughput | 1,667 claims/day queued within 1 hour | SLA clock starts at intake; delay here directly contributes to 9+ day cycle time [A8] |
| Token consumption/claim | ≤$0.05 blended [A4] | At $0.08/claim, annual token cost rises by $18,000; adjust model tier if over budget |

**Phase 1 calibration run:** Process a representative 100-claim sample across all intake channels [A4]. Measure per-channel accuracy, HITL trigger rate, and token consumption per claim type. Adjust IDP confidence threshold and model selection before production release.

### ADR-4 Calibration

| Metric | Target | Business case impact if missed |
|--------|:------:|-------------------------------|
| False-negative rate | <2% over 60-day shadow window [A6] | Gate condition — Phase 2 does not deploy. Portfolio saving deferred. |
| Token consumption/claim | ≤$0.03 [A26] | At $0.05/claim, annual token cost rises by $12,000 |
| Edge case / novel case rate | ≤0.4% of volume (≤10/day) [A25] | At 5%, Dr. Webb adjudication cost rises from $31,250 to ~$195,000/year, eliminating net saving |
| Confidence fallback rate | ≤15% of claims below threshold [A24] | Higher fallback rate increases physician Clinical Path volume and raises [A10] minimum headcount |
| Classification latency | <2 min/claim (batch) | Does not affect economics but affects Phase 2 throughput commitment to James Liu |

**Sigma management:** ADR-4 is a narrow-sigma task: consistent, predictable classification is required, not creative output. Calibration focuses on reducing variance — the confidence score distribution should be bimodal (high-confidence fast path vs. high-confidence clinical path) with a small middle band that falls to the conservative fallback. A wide middle band signals either poor criteria definition [A15] or an underpowered model.

**Phase 1 validation protocol:**
1. Define criteria codebook with Dr. Webb [A15] — must occur before shadow mode can begin
2. Run 60-day shadow window; collect ≥2,000 labeled examples [A6]
3. Measure false-negative rate against Dr. Webb ground-truth adjudication [A25]
4. If false-negative rate <2%: proceed to live routing
5. If false-negative rate ≥2%: expand criteria codebook, re-run shadow window (30-day extension); re-test before live

---

## 6. Economic Governance — Ongoing

Once in production, treat economics as a live governance instrument. Both agents have different governance cadences because their cost profiles differ.

### ADR-1 Governance

| Cadence | Review |
|---------|--------|
| **Monthly** | Non-EDI HITL rate vs. 10% target; total token spend vs. $2,350/month budget ($28,200/year ÷ 12) |
| **Quarterly** | IDP extraction accuracy trend; if accuracy improves, consider reducing confidence threshold to lower HITL rate and increase savings |
| **On model release** | Re-evaluate model selection — if lighter-weight model achieves ≥90% non-EDI accuracy, switch to reduce token cost |
| **On volume change** | At 100,000 claims/month, re-evaluate infrastructure cost allocation; token costs scale linearly but infra costs amortize |

### ADR-4 Governance

| Cadence | Review |
|---------|--------|
| **Monthly** | False-negative rate from 5% Fast Path physician audit sample; token spend vs. $1,400/month budget; novel case backlog in adjudication queue [A25] |
| **Quarterly** | Re-evaluate confidence fallback threshold [A24]; if false-positive rate is high (excess physician reviews), consider tightening threshold; if edge case rate rising, trigger codebook review with Dr. Webb [A15] |
| **Annually** | Full economic re-calibration: token cost vs. budget; physician audit cost vs. governance savings; consider migrating lower-risk routing decisions from HITL-audit to fully autonomous as agent proves reliability |
| **On model release** | New model may achieve higher classification accuracy at lower cost — re-run Phase 1 calibration protocol on representative 500-claim sample before migration |
| **On codebook revision** | Every Dr. Webb-approved codebook update [A15] resets the confidence distribution; monitor false-negative rate for 30 days after each revision |

### Economic Governance Dashboard (minimum viable)

| KPI | Owner | Alert threshold |
|-----|-------|----------------|
| ADR-1 monthly HITL cost | VP Operations | >$5,000/month (>$60K annualized) |
| ADR-1 token cost/claim | FDE Lead | >$0.07/claim |
| ADR-4 false-negative rate (monthly audit) | CMO | >0% in any monthly sample triggers investigation; >2% triggers autonomous routing suspension |
| ADR-4 novel case backlog | VP Operations | >50 open items in adjudication queue [A25] |
| ADR-4 token cost/claim | FDE Lead | >$0.05/claim |
| Portfolio monthly agent spend | CFO | >$25,000/month (>$300K annualized) |
| Portfolio headcount (admin) | CFO | Track quarterly toward 20→7 FTE target [A1] |

> *Economic visibility is how autonomy earns trust. As ADR-4 demonstrates consistently low false-negative rates over rolling 90-day windows, the physician audit sample (currently 5% of Fast Path) can be reduced — converting audit cost to additional saving. A 5% → 2% audit rate reduction saves ~$32,400/year while maintaining oversight.*

---

## 7. Multi-Model Experimentation Note

The base case uses Claude Sonnet for all LLM steps in ADR-1 and ADR-4. That is the right default — Sonnet's accuracy-to-cost balance fits the majority of steps in both agents. But one-model-for-everything is not the right production posture. Each agent's flow contains steps with different reasoning requirements, and the token cost difference between tiers is large enough that mismatching model to task is a material economics error in both directions: Haiku on a judgment step raises HITL cost more than it saves on tokens; Opus on a criteria-application step pays frontier rates for work that does not require frontier reasoning.

**Three-tier frame:**

| Tier | Use when |
|------|----------|
| **Opus** (frontier, ~5–6× Sonnet cost) | Problem formulation is itself ambiguous; reasoning must range widely across underdefined inputs |
| **Sonnet** (mid-tier, baseline) | Judgment tasks with constrained inputs: accuracy-sensitive extraction, criteria application, structured output with CoT trace |
| **Haiku** (lightweight, ~1/7 Sonnet cost) | Pattern matching, code lookup, validation steps where the answer is deterministic given the input |

---

### ADR-1: Per-Step Model Routing

| Step | Recommended model | Reasoning |
|------|:-----------------:|-----------|
| EDI 837P/I parsing and validation | **Rules engine** (no LLM) | HIPAA-mandated structure — deterministic; LLM adds token cost with no accuracy benefit |
| Non-EDI extraction — pre-OCR'd text, CMS-1500 PDF | **Haiku** *(Phase 1 experiment)* | Structured field layout; 0.80 confidence threshold; lower accuracy bar makes Haiku viable — confirm in Phase 1 calibration before committing |
| Non-EDI extraction — fax PDF, email, fax-as-email | **Sonnet** | Unstructured input; extraction accuracy must hold to keep HITL ≤10%; downgrading to Haiku risks HITL cost overage that erases token saving |
| Duplicate detection, exception routing | **Deterministic** (no LLM) | Hard lookup and threshold rules; no inference |

**ADR-1 cost delta — pre-OCR'd Haiku experiment:**

If Phase 1 calibration confirms Haiku achieves equivalent extraction confidence on pre-OCR'd / CMS-1500 inputs (estimated 40% of non-EDI volume, ~72,000 claims/year):

| Model routing | Non-EDI token cost | Annual token cost (non-EDI path) |
|---------------|:------------------:|:--------------------------------:|
| All Sonnet (base case) | $0.110/claim | $19,800 |
| Haiku for pre-OCR'd, Sonnet for fax/email | ~$0.066/claim blended | ~$11,880 |
| **Annual token saving** | | **~$7,920/year** |

**Risk offset:** If Haiku HITL trigger rate on pre-OCR'd claims is 5 percentage points higher than Sonnet on the same inputs, the HITL cost penalty (~$11,700/year) exceeds the token saving. The switch is only net-positive if Phase 1 calibration confirms HITL rate parity within 2 percentage points. **Default stays Sonnet; Haiku is the Phase 1 calibration experiment on this sub-path only.**

Nothing in ADR-1 requires Opus. The task is field extraction and format validation — not open-ended reasoning.

---

### ADR-4: Per-Step Model Routing

| Step | Recommended model | Reasoning |
|------|:-----------------:|-----------|
| Precondition validation (`extraction_status` check) | **Deterministic** (no LLM) | Hard precondition; reject or pass — no inference |
| Codebook code pre-screen (CPT/ICD-10 lookup) | **Haiku** | Pattern matching against codebook list; outputs match / unmatched / novel — no CoT required |
| CoT classification + confidence scoring | **Sonnet** | Criteria application with auditable reasoning trace; narrow sigma required for [A6] gate |
| NOVEL_CASE guardrail, confidence fallback routing | **Deterministic** (no LLM) | Hard rules applied post-classification; no inference |

**ADR-4 cost delta — Haiku pre-screen step:**

Routing the codebook code lookup to Haiku saves approximately **$2,400/year** — useful but not the primary lever. The main classification must stay Sonnet: Haiku produces a wider confidence distribution on ambiguous claims, increasing NOVEL_CASE false-triggers and confidence fallbacks, which raises Clinical Path volume and erodes Fast Path throughput.

**ADR-4 cost delta — avoiding the Opus default:**

The more consequential model choice is not defaulting to Opus because the triage decision is "high-stakes." The classification task is criteria application against an explicit codebook — not open-ended clinical reasoning. A well-defined codebook [A15] makes this a constrained judgment task, which Sonnet handles at production accuracy.

| Model for CoT classification | Per-claim token cost | Annual token cost | Delta vs. Sonnet |
|------------------------------|:--------------------:|:-----------------:|:----------------:|
| Opus (naive "high-stakes = best model") | ~$0.110/claim | ~$66,000/year | **+$52,800/year** |
| **Sonnet (spec'd)** | $0.022/claim | $13,200/year | baseline |
| Haiku (accuracy risk, not production-eligible without gate validation) | ~$0.004/claim | ~$2,400/year | −$10,800/year |

Opus is appropriate for tasks where the problem formulation itself requires ranging widely — e.g., ADR-7 (physician review) if it were AI-assisted would need frontier reasoning because clinical judgment is underdefined. ADR-4 with a defined codebook is not that task.

---

### Experimentation Protocol

Before committing any model routing change from the base case:

1. **Phase 1 calibration run**: Test Haiku alongside Sonnet on a representative 200-claim sample for each candidate step (ADR-1 pre-OCR'd extraction; ADR-4 codebook pre-screen).
2. **Gate metric**: Haiku path must match Sonnet path on HITL trigger rate (ADR-1) and NOVEL_CASE / fallback rate (ADR-4) within **2 percentage points**. Accuracy parity required; cost saving alone is not sufficient.
3. **Decision threshold**: Only migrate if confirmed annual saving > $5,000 AND gate metric passes. Both conditions required.
4. **Governance cadence**: On each major model release, re-run the 200-claim calibration on the current production sub-path split. New model tiers may shift the crossover — a future Haiku-class model capable of Sonnet-level extraction accuracy would shift ADR-1 non-EDI extraction entirely to Haiku, saving the full ~$19,800/year token budget for that path.

---

*Assumption references: [A1], [A2], [A4], [A6], [A8], [A10], [A12], [A14], [A15], [A21], [A22], [A23], [A24], [A25], [A26], [A27], [A28], [U1].*  
*See `specs/assumptions.md` for full assumption definitions including new assumptions A26–A28.*  
*See `specs/06a-capability-spec-intake.md` and `specs/06b-capability-spec-triage.md` for agent specifications.*  
*See `specs/10-stakeholder-memo.md` for Phase 1/2/3 transition commitments and gate conditions.*
