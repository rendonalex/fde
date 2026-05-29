# Volume × Value Analysis: Apex Distribution Customer Operations

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Step 1: Suitability Gating](#step-1-suitability-gating)
3. [Step 2: Volume × Value Scoring](#step-2-volume--value-scoring)
   - [Scoring Table](#scoring-table)
   - [Volume × Value Quadrant](#volume--value-quadrant)
4. [Step 3: Total Cost of Ownership Assessment](#step-3-total-cost-of-ownership-assessment)
5. [Step 4: Feasibility Scoring Matrix](#step-4-feasibility-scoring-matrix)
6. [Step 5: Strategic Sequencing Validation](#step-5-strategic-sequencing-validation)
7. [Prioritised Candidate Shortlist](#prioritised-candidate-shortlist)
8. [Implementation Sequencing Logic](#implementation-sequencing-logic)

---

## Executive Summary

Phase 4 prioritises six agentic automation candidates from the seven JtDs identified across Apex Distribution's Dispatch Adjustments and Delivery Exceptions workstreams. DA-3 (Driver Swap) fails the suitability gate and is excluded from scoring.

**Priority summary:**

| Wave | Candidates | Combined Volume | Gross Annual Saving | Build Cost |
|------|-----------|-----------------|---------------------|------------|
| Wave 1 Pilot | DE-3 | 140 cases/day | £89,600 | £25,000 |
| Wave 1 Expansion | DE-4, DA-1 | 81 cases/day | £87,277 | £30,000 |
| Wave 2 | DE-1, DA-2, DE-2 | 117 cases/day | £110,857 | £86,000 |
| **Phase 1 Cumulative** | DE-3, DE-4, DA-1 | **221 cases/day** | **£177K gross / £122K net** | **£55,000** |

**Key tension in this analysis**: The highest agentic value scores belong to judgment-heavy JtDs — DE-1 (16) and DE-2 (15) — which have lower feasibility due to unresolved decision rule gaps and integration blockers. DE-3, the recommended Phase 1 pilot, scores only 12 but has the highest feasibility (26/30) and shortest payback (3.4 months). Wave sequencing must prioritise feasibility over raw value score in early waves to establish funding and reusable infrastructure for Phase 2.

**Implementation sequencing logic**: Wave 1 ROI funds Wave 2 build cost. The three Wave 1 candidates collectively build the CRM + driver app + notification + approval-workflow platform that Wave 2 inherits at ~30% lower marginal cost [A032].

---

## Step 1: Suitability Gating

Pass criteria: at least Medium suitability on Input Structure, Decision Determinism, and Tool Coverage; no hard blocks on Risk/Compliance.

| JtD | Input Structure | Decision Determinism | Tool Coverage | Risk/Compliance | Gate Result |
|-----|-----------------|----------------------|---------------|-----------------|-------------|
| **DE-3** Missed Window | HIGH | HIGH | HIGH | No blocks | **PASS** |
| **DE-4** Unattended Address | HIGH | HIGH | HIGH | No blocks | **PASS** |
| **DA-1** Additional Pickup | MEDIUM | HIGH | MEDIUM-LOW [A004] | No blocks | **CONDITIONAL** |
| **DE-1** Refused Delivery | MEDIUM-LOW | MEDIUM-LOW [A005] | HIGH | No blocks | **CONDITIONAL** |
| **DE-2** Damaged Consignment | MEDIUM-LOW | LOW [A017] | MEDIUM-LOW [A007] | No blocks | **CONDITIONAL** |
| **DA-2** Route Diversion | MEDIUM | MEDIUM-LOW [A019] | LOW [A004] | No blocks | **CONDITIONAL** |
| **DA-3** Driver Swap | MEDIUM-LOW | **LOW** [A002] | MEDIUM-LOW [A004] | **HIGH consequence** | **FAIL** |

**DA-3 fails** on three critical dimensions: Decision Determinism LOW (relationship-driven negotiation), Context Complexity LOW (institutional knowledge not in systems [A002]), and Risk/Compliance LOW (driver welfare, tachograph compliance, union obligations). Volume (10–15/day [A016]) does not justify forcing delegation. Excluded from further scoring.

**Conditional candidates** require blocking assumption resolution before production deployment:

| JtD | Critical Blocker |
|-----|-----------------|
| DA-1 | Dispatch console API write access [A004] — workaround: human-approval model |
| DE-1 | Refused delivery decision tree formalization [A005] |
| DE-2 | Damage liability assessment criteria [A017] + Aurum real-time integration [A007] |
| DA-2 | Diversion decision rules [A019] + customer priority system [A009] |

All conditional candidates are scored and sequenced to Wave 2, with prerequisite formalisation work beginning in parallel with Wave 1 build.

---

## Step 2: Volume × Value Scoring

### Scoring Table

```
Execution Frequency scale: 1 (infrequent/monthly) → 5 (hundreds/day)
Non-Determinism scale:     1 (fully deterministic) → 5 (high synthesis + contextual judgment)
Agentic Value Score = Volume × Non-Determinism (1–25)
```

| JtD | Execution Freq Score | Volume (cases/day) | Non-Determinism Score | Value Score | Recommendation |
|-----|---------------------|--------------------|-----------------------|-------------|----------------|
| **DE-1** Refused Delivery | 4 | 54 | 4 | **16** | Strong agentic candidate |
| **DE-2** Damaged Consignment | 3 | 36 | 5 | **15** | Strong agentic candidate |
| **DE-3** Missed Window | 4 | 140 | 3 | **12** | Consider agentic — validate TCO |
| **DA-2** Route Diversion | 3 | 27 | 4 | **12** | Consider agentic — validate TCO |
| **DA-3** Driver Swap | 2 | 12 | 5 | **10** | *Excluded — gate fail* |
| **DA-1** Additional Pickup | 3 | 36 | 3 | **9** | Consider agentic — validate TCO |
| **DE-4** Unattended Address | 3 | 45 | 2 | **6** | Rule-based / RPA threshold |

**Score thresholds**: ≥15 Strong candidate · 8–14 Consider + validate TCO · <8 Rule-based automation

**Non-determinism score rationale:**
- **DE-2 (5)**: Liability determination from photos, credit amount judgement, sender pattern analysis — highest synthesis requirement
- **DE-1 (4)**: Unstructured driver narrative classification, multi-party conflict resolution, disposition judgement [A005]
- **DA-2 (4)**: Route impact calculation plus customer relationship and delay tolerance judgement [A019]
- **DA-3 (5)**: Relationship negotiation, fatigue assessment, overtime/union judgement — *excluded*
- **DE-3 (3)**: Rule-based GPS lookup + ETA calculation; agent value is speed and exception handling, not complex reasoning [A010]
- **DA-1 (3)**: Capacity/proximity calculation with edge-case escalation; mostly deterministic
- **DE-4 (2)**: Clear rule hierarchy — safe-place authority check → eligibility → instruct driver; minimal reasoning

**Note on DE-4 (score 6 — below RPA threshold)**: Pure scoring places DE-4 in rule-based/RPA territory. However, the multi-system orchestration required (CRM safe-place lookup + consignment eligibility + driver app instruction + SMS/email notification + re-delivery scheduling) exceeds standard RPA capability. The marginal build cost on top of DE-3's Wave 1 infrastructure [A032] makes an agent approach economically superior to standalone RPA at 45 cases/day. DE-4 is included as Wave 1 Expansion despite the low ND score.

### Volume × Value Quadrant

```mermaid
quadrantChart
    title Volume × Value Quadrant: Apex Distribution JtDs
    x-axis "Low Non-Determinism" --> "High Non-Determinism"
    y-axis "Low Volume" --> "High Volume"
    quadrant-1 Primary Agentic Targets
    quadrant-2 Rules / RPA
    quadrant-3 Deprioritise
    quadrant-4 Select Use Cases
    DE-3 Missed Window (12): [0.52, 0.78]
    DE-1 Refused Delivery (16): [0.75, 0.82]
    DE-4 Unattended Address (6): [0.35, 0.60]
    DA-1 Additional Pickup (9): [0.52, 0.58]
    DE-2 Damaged Consignment (15): [0.90, 0.62]
    DA-2 Route Diversion (12): [0.77, 0.54]
    DA-3 Driver Swap (10): [0.92, 0.38]
```

**Quadrant interpretation:**

| Quadrant | JtDs | Implication |
|----------|------|-------------|
| **Top Right** — Primary agentic targets | DE-3, DE-1, DE-2, DA-2, DA-1 | High volume + meaningful reasoning; prioritise for agent build |
| **Top Left** — Rules/RPA | DE-4 | High volume, low reasoning; agent justified by multi-system orchestration [A032] |
| **Bottom Right** — Select use cases | DA-3 | High reasoning, low volume; excluded (gate fail, Human Only) |
| **Bottom Left** — Deprioritise | *(empty)* | No JtDs in this zone |

**Critical insight**: DE-3 (the Phase 1 pilot) and DA-1 sit at the left edge of the Top Right quadrant — their value comes more from volume and feasibility than from reasoning complexity. DE-1 and DE-2 anchor the right side where the reasoning value is highest; feasibility scoring (Step 4) explains why they are Wave 2.

---

## Step 3: Total Cost of Ownership Assessment

**Common assumptions**: £35K fully loaded FTE salary [A018] · 1,750 working hours/year → £20/hr [A031] · 250 working days/year [A030] · Claude Sonnet: £0.003/1K input tokens, £0.015/1K output tokens [A028] · Tool/API call overhead: £0.005/call [A029]

---

### Use Case: DE-3 — Missed Window Investigation

```
Process: Delivery Exceptions / Customer Operations
Volume: 140 cases/day

Suitability gate:
  Input structure:        HIGH
  Decision determinism:   HIGH
  Tool coverage:          HIGH
  Exception rate:         MEDIUM (30% complications — detectable, escalatable)
  Compliance risk:        LOW (reversible, no regulatory exposure)
  Gate result:            PASS

Scoring:
  Execution frequency score:     4   (50–200/day)
  Non-deterministic effort score: 3  (rule-based core; edge cases require reasoning)
  Agentic value score:           12

Economics:
  Avg time per case (human): 8 min (0.133 hrs)
  Cases per year:            35,000 [A030]
  Fully loaded hourly cost:  £20/hr [A031]
  Annual baseline cost:      £93,100

  Tokens per case: 1,100 input / 350 output [A028]
  Model: Claude Sonnet
  Token cost per case:       £0.0086
  Tool calls: ~5 × £0.005 = £0.025 [A029]
  HITL (10% × 2 min × £20/hr): £0.067
  Agent cost per case:       ~£0.10
  Annual agent cost:         £3,500

  Annual saving:     £89,600
  Build cost:        £25,000 [A027]
  Payback period:    3.4 months
  Year 1 ROI:        258%
  3-year ROI:        975%

Sequencing:     Wave 1 Pilot
Key integrations built: CRM (Salesforce REST), Driver App API, SMS/email notifications,
                        oversight dashboard, audit logging
Dependencies:   ETA estimator build [A010]

Delegation archetype: Fully Agentic
Recommended next step: Proceed to build — shadow-mode validation for 2 weeks before go-live
```

---

### Use Case: DE-4 — Unattended Address Exception

```
Process: Delivery Exceptions / Customer Operations
Volume: 45 cases/day

Suitability gate:
  Input structure:        HIGH
  Decision determinism:   HIGH
  Tool coverage:          HIGH
  Exception rate:         LOW-MEDIUM (~20% complications, predictable)
  Compliance risk:        MEDIUM (theft/signature liability — mitigated by rule enforcement)
  Gate result:            PASS

Scoring:
  Execution frequency score:      3  (10–50/day)
  Non-deterministic effort score: 2  (rule hierarchy: safe place → eligibility → instruct)
  Agentic value score:            6

Economics:
  Avg time per case (human): 10 min (0.167 hrs)
  Cases per year:            11,250 [A030]
  Fully loaded hourly cost:  £20/hr [A031]
  Annual baseline cost:      £37,575

  Tokens per case: 800 input / 250 output [A028]
  Tool calls: ~3 × £0.005 = £0.015 [A029]
  HITL (20% × 2 min × £20/hr): £0.133
  Agent cost per case:       ~£0.15
  Annual agent cost:         £1,688

  Annual saving:     £35,887
  Build cost:        £12,000 [A027] (inherits DE-3 CRM + Driver App [A032])
  Payback period:    4.0 months
  Year 1 ROI:        199%
  3-year ROI:        797%

Sequencing:     Wave 1 Expansion
Key integrations built: CRM safe-place/neighbor authority module,
                        consignment eligibility rules engine, re-delivery scheduling
Dependencies:   DE-3 Wave 1 infrastructure [A032]

Delegation archetype: Agent-led + Human Oversight
Recommended next step: Proceed to build in parallel with DA-1 (Months 4–6)
```

---

### Use Case: DA-1 — Process Additional Pickup Request

```
Process: Dispatch Adjustments / Customer Operations
Volume: 36 cases/day

Suitability gate:
  Input structure:        MEDIUM
  Decision determinism:   HIGH
  Tool coverage:          MEDIUM-LOW (dispatch console API constraint [A004])
  Exception rate:         MEDIUM (~25% no-capacity or timing-conflict cases)
  Compliance risk:        MEDIUM (weight limits, driver shift hours compliance)
  Gate result:            CONDITIONAL [A004]

Scoring:
  Execution frequency score:      3  (10–50/day)
  Non-deterministic effort score: 3  (rule-based capacity calc; edge cases need reasoning)
  Agentic value score:            9

Economics:
  Avg time per case (human): 18 min (0.30 hrs)
  Cases per year:            9,000 [A030]
  Fully loaded hourly cost:  £20/hr [A031]
  Annual baseline cost:      £54,000

  Tokens per case: 1,400 input / 450 output [A028]
  Tool calls: ~6 × £0.005 = £0.030 [A029]
  HITL (25% × 3 min × £20/hr): £0.25
  Agent cost per case:       ~£0.29
  Annual agent cost:         £2,610

  Annual saving:     £51,390
  Build cost:        £18,000 [A027] (dispatch console workaround + route feasibility module;
                    inherits CRM + Driver App [A032])
  Payback period:    4.2 months
  Year 1 ROI:        186%
  3-year ROI:        757%

Sequencing:     Wave 1 Expansion
Key integrations built: Route feasibility calculator (GPS proximity + vehicle capacity),
                        one-click approval workflow (agent recommends → dispatcher approves)
Dependencies:   Dispatch console API validation [A004]; if unavailable, deploy human-approval
                workaround (agent recommends, human executes in dispatch console)

Delegation archetype: Agent-led + Human Oversight
Recommended next step: Validate dispatch console API access [A004]; proceed to build Month 4
```

---

### Use Case: DE-1 — Resolve Refused Delivery

```
Process: Delivery Exceptions / Customer Operations
Volume: 54 cases/day

Suitability gate:
  Input structure:        MEDIUM-LOW (unstructured driver narratives, conflicting accounts)
  Decision determinism:   MEDIUM-LOW (decision tree not formalised [A005])
  Tool coverage:          HIGH (Salesforce REST, Driver App messaging)
  Exception rate:         HIGH (~40% complicating factors)
  Compliance risk:        MEDIUM (reversible; >£500 threshold requires manager approval)
  Gate result:            CONDITIONAL [A005]

Scoring:
  Execution frequency score:      4  (50–200/day)
  Non-deterministic effort score: 4  (NLP classification + disposition judgement + conflict resolution)
  Agentic value score:            16

Economics:
  Avg time per case (human): 12 min (0.20 hrs)
  Cases per year:            13,500 [A030]
  Fully loaded hourly cost:  £20/hr [A031]
  Annual baseline cost:      £54,000

  Tokens per case: 1,800 input / 600 output [A028]
  Tool calls: ~7 × £0.005 = £0.035 [A029]
  HITL (100% × 2 min × £20/hr): £0.667 (human decides all dispositions)
  Agent cost per case:       ~£0.72
  Annual agent cost:         £9,720

  Annual saving:     £44,280
  Build cost:        £28,000 [A027] (NLP pipeline, decision tree engine [A005],
                    customer priority integration [A009]; inherits CRM + Driver App [A032])
  Payback period:    7.6 months
  Year 1 ROI:        58%
  3-year ROI:        374%

Sequencing:     Wave 2 (Month 7–9)
Key integrations built: NLP refusal-reason classifier, decision tree engine with confidence scoring,
                        recommendation UI
Dependencies:   Decision tree formalisation [A005] — elicitation work must begin Month 1
                Customer priority/tier system [A009]

Delegation archetype: Human-led + Agent Support
Recommended next step: Begin decision-rule elicitation sessions (Sandra + dispatch team) immediately
```

---

### Use Case: DA-2 — Execute Route Diversion

```
Process: Dispatch Adjustments / Customer Operations
Volume: 27 cases/day

Suitability gate:
  Input structure:        MEDIUM
  Decision determinism:   MEDIUM-LOW (diversion acceptability judgement-heavy [A019])
  Tool coverage:          LOW (dispatch console API [A004]; route optimizer not available)
  Exception rate:         HIGH (~40% complicating factors [A020])
  Compliance risk:        MEDIUM-HIGH (SLA breach risk; priority customer relationships)
  Gate result:            CONDITIONAL [A004, A019]

Scoring:
  Execution frequency score:      3  (10–50/day)
  Non-deterministic effort score: 4  (route impact + customer tolerance + relationship judgement)
  Agentic value score:            12

Economics:
  Avg time per case (human): 18 min (0.30 hrs)
  Cases per year:            6,750 [A030]
  Fully loaded hourly cost:  £20/hr [A031]
  Annual baseline cost:      £40,500

  Tokens per case: 1,600 input / 500 output [A028]
  Tool calls: ~8 × £0.005 = £0.040 [A029]
  HITL (100% × 4 min × £20/hr): £1.333 (human decides all diversions)
  Agent cost per case:       ~£1.39
  Annual agent cost:         £9,383

  Annual saving:     £31,117
  Build cost:        £23,000 [A027] (route impact calculator, traffic API,
                    customer priority integration [A009]; inherits CRM + DA-1 route module [A032])
  Payback period:    8.9 months
  Year 1 ROI:        35%
  3-year ROI:        306%

Sequencing:     Wave 2 (Month 9–11)
Key integrations built: Route impact calculator with downstream delay propagation,
                        traffic API integration
Dependencies:   Diversion decision-rule formalisation [A019]
                Customer priority/tier system [A009] (shared with DE-1)
                DA-1 route feasibility module (inherits)

Delegation archetype: Human-led + Agent Support
Recommended next step: Defer build until customer priority system formalised [A009];
                       route optimization module from DA-1 accelerates build [A032]
```

---

### Use Case: DE-2 — Handle Damaged Consignment Report

```
Process: Delivery Exceptions / Customer Operations
Volume: 36 cases/day

Suitability gate:
  Input structure:        MEDIUM-LOW (photos + narrative; variable quality)
  Decision determinism:   LOW (liability = transit vs. packaging — no formal criteria [A017])
  Tool coverage:          MEDIUM-LOW (Aurum batch lag [A007]; image recognition requires training)
  Exception rate:         MEDIUM-HIGH (~35% complications)
  Compliance risk:        MEDIUM-HIGH (financial liability; audit trail gap [A008])
  Gate result:            CONDITIONAL [A007, A017]

Scoring:
  Execution frequency score:      3  (10–50/day)
  Non-deterministic effort score: 5  (highest reasoning: visual assessment, liability, credit
                                     judgement, relationship sensitivity)
  Agentic value score:            15

Economics:
  Avg time per case (human): 15 min (0.25 hrs)
  Cases per year:            9,000 [A030]
  Fully loaded hourly cost:  £20/hr [A031]
  Annual baseline cost:      £45,000

  Tokens per case: 2,000 input / 700 output + vision tokens [A028]
  Tool calls: ~7 × £0.005 = £0.035 [A029]
  HITL (100% × 3 min × £20/hr): £1.00 (human approves all liability/credit decisions)
  Agent cost per case:       ~£1.06
  Annual agent cost:         £9,540

  Annual saving:     £35,460
  Build cost:        £35,000 [A027] (image recognition model, Aurum credit workflow [A007],
                    liability criteria engine [A017]; inherits CRM [A032])
  Payback period:    11.8 months
  Year 1 ROI:        1.4%
  3-year ROI:        204%

Sequencing:     Wave 2 (Month 11+) — conditional on image recognition model readiness
Key integrations built: Image recognition damage assessment, Aurum credit queue workflow,
                        audit trail (addresses Sandra's manual override gap [A008])
Dependencies:   Liability assessment criteria [A017] — formalisation + decision elicitation
                Image recognition model training (6+ months damage photo data) [A033]
                Aurum billing integration or credit workflow alternative [A007]

Delegation archetype: Human-led + Agent Support
Recommended next step: Begin damage photo data collection immediately (model training lead time);
                       defer full build to Month 11 unless Aurum API is negotiated earlier
```

---

## Step 4: Feasibility Scoring Matrix

Scores 1–5. Compliance risk scored inverted: 5 = minimal regulatory or compliance exposure.

| Factor | DE-3 | DE-4 | DA-1 | DE-1 | DA-2 | DE-2 |
|--------|:----:|:----:|:----:|:----:|:----:|:----:|
| Data availability | 4 | 4 | 3 | 3 | 3 | 3 |
| System integration feasibility | 4 | 4 | 3 | 4 | 2 | 2 |
| Compliance risk (5 = low risk) | 5 | 4 | 4 | 4 | 4 | 3 |
| Context stability | 4 | 4 | 3 | 3 | 3 | 3 |
| Organisational readiness | 4 | 4 | 3 | 4 | 3 | 3 |
| TCO viability | 5 | 5 | 5 | 4 | 3 | 3 |
| **Total (out of 30)** | **26** | **25** | **21** | **22** | **18** | **17** |
| **Wave** | **1 Pilot** | **1 Exp.** | **1 Exp.** | **2** | **2** | **2** |

**Notes by candidate:**

- **DE-3 (26/30)**: All data accessible; ETA estimator buildable [A010]; risk negligible. Highest feasibility of all candidates.
- **DE-4 (25/30)**: Near-identical profile to DE-3. Marginal build cost (DE-3 infrastructure inheritance [A032]).
- **DA-1 (21/30)**: Dispatch console API constraint [A004] reduces integration score. Organisational readiness moderate (dispatchers protective of routing authority). TCO strong at 186% Year 1 ROI with human-approval workaround.
- **DE-1 (22/30)**: CRM tools are available (integration score 4). Context stability at 3 due to unresolved decision rules [A005]. Higher organisational readiness than DA-1 — agents familiar with refusal handling process.
- **DA-2 (18/30)**: Dual blockers — dispatch console API [A004] and customer priority formalization [A009, A019] — drive the lowest integration score among agentic candidates. TCO viability at 3 (35% Year 1 ROI, 8.9-month payback).
- **DE-2 (17/30)**: Lowest feasibility. Image recognition training requirement [A017], Aurum batch integration [A007], and marginal Year 1 ROI (1.4%) drive all lower-tier scores. Three-year ROI (204%) is viable but requires patience.

---

## Step 5: Strategic Sequencing Validation

| Criterion | Weight | DE-3 | DE-4 | DA-1 | DE-1 | DA-2 | DE-2 |
|-----------|--------|------|------|------|------|------|------|
| Self-financing ROI | **High** | ✓✓ 258% | ✓✓ 199% | ✓✓ 186% | ✓ 58% | ✓ 35% | ~ 1.4% |
| Integration reusability | **High** | ✓✓ (CRM + Driver App — base layer) | ✓✓ (inherits DE-3) | ✓ (adds route calc) | ✓ (inherits CRM) | ✓ (inherits route calc) | ~ (new: vision) |
| Low compliance risk | Medium | ✓✓ | ✓ | ✓ | ✓ | ✓ | ~ |
| Data readiness | Medium | ✓✓ | ✓✓ | ✓ | ✓ | ✓ | ~ |
| Organisational readiness | Medium | ✓✓ | ✓✓ | ✓ | ✓✓ | ✓ | ✓ |
| Strategic visibility | Low | ✓✓ (customer ETA improvement highly visible) | ✓ | ✓ | ✓✓ (Sandra's workload) | ✓ | ✓ |
| **Wave assignment** | | **1 Pilot** | **1 Exp.** | **1 Exp.** | **2** | **2** | **2 (late)** |

**Wave 1 funds Wave 2**: Combined Wave 1 gross savings of ~£177K/year against £55K build cost produces net-positive position by Month 4. Wave 2 build cost (£86K) is fully covered by Wave 1 annualised savings before Wave 2 completes (by Month 7, Wave 1 has generated ~£91K net).

**Integration compounding**: DE-3 builds the platform layer (CRM REST, Driver App API, notification automation, oversight dashboard, audit logging). DE-4 and DA-1 inherit with incremental additions only. All Wave 2 candidates inherit the CRM integration. Wave 2 marginal build costs estimated at ~30% lower than greenfield equivalents [A032].

**Sequencing note on DE-1 vs DA-1**: DE-1 scores higher on agentic value (16 vs 9) but is Wave 2. The deciding factor is decision-rule formalization [A005]: the agent cannot produce reliable disposition recommendations without a codified decision tree. Elicitation work (shadow sessions with Sandra and dispatch leads) must begin in Month 1 to be ready for a Month 7 Wave 2 build.

**DE-2 activation gate**: Year 1 ROI of 1.4% is marginal. Full build should not begin until: (a) image recognition model achieves ≥85% damage severity classification accuracy on held-out test set [A033], and (b) Aurum credit workflow alternative is validated [A007]. These conditions are expected to be met by Month 10–11 at earliest.

---

## Prioritised Candidate Shortlist

| Rank | JtD | Volume (cases/day) | Value Score | Feasibility | Wave | Archetype | Key Dependency |
|------|-----|--------------------|-------------|-------------|------|-----------|----------------|
| 1 | **DE-3** Missed Window Investigation | 140 | 12 | 26/30 | **Wave 1 Pilot** | Fully Agentic | ETA estimator build [A010] |
| 2 | **DE-4** Unattended Address | 45 | 6 | 25/30 | **Wave 1 Expansion** | Agent-led + Human Oversight | Inherits DE-3 infra [A032] |
| 3 | **DA-1** Additional Pickup | 36 | 9 | 21/30 | **Wave 1 Expansion** | Agent-led + Human Oversight | Dispatch console API/workaround [A004] |
| 4 | **DE-1** Refused Delivery | 54 | 16 | 22/30 | **Wave 2** | Human-led + Agent Support | Refused delivery decision rules [A005] |
| 5 | **DA-2** Route Diversion | 27 | 12 | 18/30 | **Wave 2** | Human-led + Agent Support | Customer priority + diversion rules [A009, A019] |
| 6 | **DE-2** Damaged Consignment | 36 | 15 | 17/30 | **Wave 2 (late)** | Human-led + Agent Support | Image recognition model [A033] + Aurum [A007] |
| — | **DA-3** Driver Swap | 12 | — | Gate fail | **Excluded** | Human Only | — |

**Supporting analysis:**

The prioritised ranking results from compositing value score and feasibility — neither dimension alone produces the correct sequence. The high-value candidates (DE-1, DE-2) are Wave 2 because their feasibility blockers are not resolved, not because their value is lower. Conversely, DE-3 and DE-4 are Wave 1 precisely because high feasibility enables fast, low-risk deployment that generates the ROI and infrastructure needed to fund DE-1 and DE-2.

DA-3 would not be cost-effective to automate even if the blockers were resolved — at 10–15 cases/day with high institutional knowledge requirements [A002] and significant regulatory exposure, senior dispatcher time is the correct resource allocation.

---

## Implementation Sequencing Logic

### Wave 1 Pilot — Months 1–3: DE-3 (Self-Funding Foundation)

**Objective**: Prove agent value, establish the shared platform, generate ROI that funds all subsequent waves.

**Platform built (inherited by all subsequent waves):**
- Salesforce CRM REST API integration (case intake, customer lookup, history retrieval, case logging)
- Driver App API client (GPS location, delivery status, driver messaging)
- Customer notification automation (SMS/email via CRM)
- Agent oversight dashboard + random sample review workflow
- Audit logging and decision rationale capture infrastructure

**Shadow-mode validation (Weeks 1–2)**: Agent generates ETA estimates in background; human validates before sending to customer. Compare accuracy vs. human "best guess" baseline before live activation.

**Success gate for Wave 1 Expansion**: ≥85% autonomous handling · <5% wrong-ETA rate · ≥90% customer satisfaction · 3.4-month payback trajectory confirmed.

**Output**: £89,600/year saving · 1.75 FTE equivalent freed for higher-value work.

---

### Wave 1 Expansion — Months 4–6: DE-4 + DA-1 (Compounding Returns)

**DE-4 incremental build** (£12,000 on top of DE-3 platform):
- CRM safe-place/neighbor authority lookup module
- Consignment eligibility rules engine (value threshold + signature requirement check)
- Re-delivery scheduling integration (links to DE-3 re-delivery trigger)
- Policy-conflict escalation pathway (supervisor notification)

**DA-1 incremental build** (£18,000 on top of DE-3 platform):
- Route feasibility calculator: driver GPS proximity + vehicle capacity check
- One-click approval workflow: agent presents recommendation → dispatcher approves/overrides
- Dispatch console manual-update workaround (until API available [A004])
- Edge-case escalation: no capacity available → structured escalation with options

**Combined output**: +£87,277/year · Cumulative Wave 1: £177K gross / £122K net.

**Platform state after Wave 1**: CRM + Driver App + Notification + Approval workflow + Route feasibility module → Wave 2 inherits all at ~30% lower marginal cost [A032].

---

### Parallel Track — Months 1–6: Wave 2 Prerequisites

*Begin in Month 1, not Month 7. These are long-lead items that gate Wave 2 build.*

| Workstream | Owner | Target Completion | Dependencies |
|------------|-------|-------------------|--------------|
| Shadow Sandra for DE-1 decision elicitation (20+ cases) | FDE + dispatch lead | Month 3 | A005 |
| Formalise customer priority/tier system | CS ops lead | Month 4 | A009 |
| Formalise route diversion decision rules | Dispatch supervisor | Month 5 | A019 |
| Begin damage photo data collection (image recognition training set) | CS ops | Month 1 (ongoing) | A017, A033 |
| Negotiate Aurum API or design credit workflow alternative | Finance + IT | Month 5 | A007 |
| Formalise damage liability assessment criteria | CS ops + finance | Month 6 | A017 |

---

### Wave 2 — Months 7–12: Decision Support Layer (DE-1, DA-2, DE-2)

**Sequencing within Wave 2:**

**Month 7–9: DE-1 (Refused Delivery)**
- Highest value score (16) of all Wave 2 candidates
- CRM integration already built → incremental NLP and decision tree layer
- Blocked only by decision rule formalization [A005] (completed Month 3)
- Output: +£44,280/year saving

**Month 9–11: DA-2 (Route Diversion)**
- Inherits CRM + DA-1 route feasibility module (low marginal cost)
- Blocked by customer priority system [A009] (completed Month 4) and diversion rules [A019] (Month 5)
- Output: +£31,117/year saving

**Month 11+: DE-2 (Damaged Consignment)**
- Activation gated by image recognition model accuracy ≥85% [A033] and Aurum workflow [A007]
- Addresses the audit trail gap from Sandra's manual overrides [A008]
- Output: +£35,460/year saving

**Combined Wave 2 output**: +£110,857/year · Cumulative Phase 1+2: £288K gross / £205K net.

---

### Wave 3+ — Month 13+: Platform Optimisation

- Elevate DE-1 and DE-2 from Agent Support → Agent-led + Human Oversight as decision rules prove robust
- Expand scope to billing disputes (downstream of DE-2 credit workflow)
- Multi-agent coordination: DE-3 re-delivery trigger → DE-4 unattended handler (end-to-end exception resolution)
- Model routing: Haiku for deterministic rule lookups (DE-4, DA-1 standard cases) · Sonnet for synthesis and recommendation (DE-1, DE-2 complex cases)
- Audit and quality analytics: detect drift between agent recommendations and human overrides; surface patterns for SOP update

---

## Document Control

- **Created**: 2026-05-11
- **Version**: 1.0
- **Owner**: AI FDE Team
- **Related Documents**:
  - `specs/1-cognitive-load-map.md` — JtD definitions and micro-task analysis
  - `specs/2-delegation-suitability-matrix.md` — Delegation archetypes and suitability scores
  - `specs/assumptions.md` — All assumption references (A001–A033)
  - `input-docs/atx/atx-scoring.md` — Scoring methodology (Steps 1–4)
  - `input-docs/atx/atx-assessment.md` — Phase 4 deliverable definitions
- **Next Phase**: Agent Mapping — detailed agent design for Wave 1 candidates (DE-3, DE-4, DA-1)
