# Volume × Value Analysis: Apex Distribution Customer Operations

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Step 1: Suitability Gating](#step-1-suitability-gating)
3. [Step 2: Volume × Value Scoring](#step-2-volume--value-scoring)
   - [Volume Scores](#volume-scores)
   - [Non-Determinism Scores](#non-determinism-scores)
   - [Agentic Value Scores](#agentic-value-scores)
   - [Volume × Value Quadrant](#volume--value-quadrant)
4. [Step 3: Total Cost of Ownership Assessment](#step-3-total-cost-of-ownership-assessment)
   - [Baseline Human Costs](#baseline-human-costs)
   - [Agent Cost Model](#agent-cost-model)
   - [ROI Calculations by JtD](#roi-calculations-by-jtd)
5. [Step 4: Feasibility Scoring Matrix](#step-4-feasibility-scoring-matrix)
6. [Step 5: Strategic Sequencing](#step-5-strategic-sequencing)
7. [Prioritised Candidate Shortlist](#prioritised-candidate-shortlist)
8. [Implementation Sequencing Logic](#implementation-sequencing-logic)

---

## Executive Summary

This analysis prioritizes 7 Jobs to be Done (JtDs) from Apex Distribution's Customer Operations using Volume × Value scoring, TCO assessment, and feasibility analysis. The goal is to identify the optimal implementation sequence that maximizes ROI and builds compounding platform assets.

### Top-Tier Candidates (Wave 1)

| Rank | JtD | Volume Score | Non-Det Score | Value Score | Annual Saving | Payback | Archetype |
|------|-----|--------------|---------------|-------------|---------------|---------|-----------|
| **1** | **DE-3: Missed Window Investigation** | 5 | 2 | **10** | **£58K** | **6 months** | Fully Agentic |
| **2** | **DE-4: Unattended Address** | 4 | 2 | **8** | **£24K** | **8 months** | Agent-led + Oversight |
| **3** | **DA-1: Additional Pickup** | 4 | 3 | **12** | **£21K** | **10 months** | Agent-led + Oversight |

**Wave 1 Combined**: £103K annual savings, 8-month blended payback, builds CRM, GPS, and route calculation integrations for Wave 2.

### Mid-Tier Candidates (Wave 2)

| Rank | JtD | Volume Score | Non-Det Score | Value Score | Annual Saving | Archetype |
|------|-----|--------------|---------------|-------------|---------------|-----------|
| **4** | **DE-1: Refused Delivery** | 4 | 4 | **16** | £34K | Human-led + Agent Support |
| **5** | **DE-2: Damaged Consignment** | 4 | 5 | **20** | £23K | Human-led + Agent Support |
| **6** | **DA-2: Route Diversion** | 3 | 4 | **12** | £17K | Human-led + Agent Support |

**Wave 2 Combined**: £74K annual savings, inherits Wave 1 platform (CRM, GPS, NLP classification).

### Low-Priority Candidate

| Rank | JtD | Volume Score | Non-Det Score | Value Score | Annual Saving | Rationale |
|------|-----|--------------|---------------|-------------|---------------|-----------|
| **7** | **DA-3: Driver Swap** | 2 | 5 | **10** | £2-3K | Human Only archetype, low volume, high complexity, not economically viable |

### Key Findings

**1. Clear Wave 1 Leader: DE-3 (Missed Window Investigation)**
- Highest absolute ROI (£58K/year), fastest payback (6 months)
- Fully Agentic archetype (85-95% autonomous)
- Lowest risk, highest customer satisfaction impact
- Builds foundational GPS and ETA calculation assets for Wave 2

**2. Strong Agent-led Candidates: DE-4, DA-1**
- Combined £45K/year savings, 8-10 month payback
- 70-80% autonomous with lightweight human approval
- DE-4 passes all gates with no blockers
- DA-1 has dispatch console API constraint [A004] but workaround viable

**3. High-Value Support Candidates: DE-1, DE-2, DA-2**
- Highest agentic value scores (16-20) due to complex reasoning requirements
- 40-60% cognitive load reduction (not full autonomy)
- Combined £74K/year savings
- **Critical dependency**: Decision rule formalization [A005, A017, A019] required before Wave 2

**4. Strategic Insight: Platform Compounding**
- Wave 1 builds: CRM API integration, driver app GPS integration, ETA calculation engine, notification automation
- Wave 2 reuses all Wave 1 assets + adds: NLP classification, image recognition (damage), route optimization logic
- **Marginal build cost for Wave 2 is 40-50% lower** than standalone implementation [Ref: A028]

**5. Self-Funding Model Validated**
- Wave 1 (DE-3 + DE-4 + DA-1): £103K annual savings, £75K build cost, **37% Year 1 ROI**
- Wave 1 savings fund Wave 2 build (estimated £60K), achieving **cumulative 3-year ROI of 280%** [Ref: A029]

---

## Step 1: Suitability Gating

**Gate Criteria (from atx-scoring.md)**:
- At least MEDIUM suitability on: Input Structure, Decision Determinism, Tool Coverage
- No hard blocks on Risk/Compliance
- Not fully solvable with deterministic rules/RPA
- Not requiring pure tacit judgment with no structure
- No critical data/system blocks with no realistic path

### Gate Results by JtD

| JtD | Input Structure | Decision Determinism | Tool Coverage | Risk/Compliance | Gate Result | Rationale |
|-----|-----------------|----------------------|---------------|-----------------|-------------|-----------|
| **DE-3** | HIGH | HIGH | HIGH | HIGH (low risk) | ✅ **PASS** | All critical dimensions HIGH, fully suitable |
| **DE-4** | HIGH | HIGH | HIGH | MEDIUM | ✅ **PASS** | All critical dimensions HIGH, risk mitigatable |
| **DA-1** | MEDIUM | HIGH | MEDIUM-LOW | MEDIUM | ✅ **PASS (Conditional)** | Tool coverage LOW due to dispatch console API [A004], but workaround viable (agent recommends, human executes). Passes on strength of MEDIUM input + HIGH determinism. |
| **DE-1** | MEDIUM-LOW | MEDIUM-LOW | HIGH | MEDIUM | ✅ **PASS (Conditional)** | Input + Decision both MEDIUM-LOW, but passes because agent provides high-value support (not full delegation). Decision rules need formalization [A005]. |
| **DE-2** | MEDIUM-LOW | LOW | MEDIUM-LOW | MEDIUM-HIGH | ✅ **PASS (Conditional)** | Decision determinism LOW (damage liability judgment), but agent support valuable. Requires liability criteria formalization [A017]. |
| **DA-2** | MEDIUM | MEDIUM-LOW | LOW | MEDIUM-HIGH | ✅ **PASS (Conditional)** | Tool coverage LOW [A004], decision rules need formalization [A019], but agent support reduces cognitive load significantly. |
| **DA-3** | MEDIUM-LOW | LOW | MEDIUM-LOW | LOW (high risk) | ⚠️ **CONDITIONAL FAIL** | Decision determinism LOW (relationship-heavy negotiation), Risk/Compliance LOW (high consequence: driver welfare, regulatory). Volume (10-15/day) doesn't justify forcing agent solution. **Human Only** is correct archetype. Gate allows minimal agent role (administrative support only). |

**Gating Outcome**:
- **6 JtDs pass** for agent consideration (DE-3, DE-4, DA-1, DE-1, DE-2, DA-2)
- **1 JtD conditional fail** (DA-3): Human Only archetype, not a prioritization candidate
- **Key constraints identified**: API access [A004], decision rule formalization [A005, A017, A019]

---

## Step 2: Volume × Value Scoring

### Volume Scores

**Scoring Scale (from atx-scoring.md)**:
- 5: Very frequent (hundreds+ per day or continuous)
- 4: Frequent (50–200 per day)
- 3: Regular (10–50 per day)
- 2: Moderate (several per day)
- 1: Infrequent (weekly or monthly)

| JtD | Cases/Day | Volume Score | Rationale |
|-----|-----------|--------------|-----------|
| **DE-3**: Missed Window | 140 | **5** | Very frequent: 140 cases/day (estimated from 400 ETA inquiries × 35% requiring investigation [Ref: A024]) = continuous stream |
| **DE-1**: Refused Delivery | 54 | **4** | Frequent: 54 cases/day (30% of 180 exceptions [Ref: A022]) = within 50-200 range |
| **DE-4**: Unattended Address | 45 | **4** | Frequent: 45 cases/day (25% of 180 exceptions [Ref: A025]) = within 50-200 range |
| **DA-1**: Additional Pickup | 36 | **4** | Frequent: 36 cases/day (40% of 90 dispatch adjustments [Ref: A001]) = within 50-200 range |
| **DE-2**: Damaged Consignment | 36 | **4** | Frequent: 36 cases/day (20% of 180 exceptions [Ref: A023]) = within 50-200 range |
| **DA-2**: Route Diversion | 27 | **3** | Regular: 27 cases/day (30% of 90 dispatch adjustments [Ref: A001]) = 10-50 range |
| **DA-3**: Driver Swap | 12 | **2** | Moderate: 10-15 cases/day (10-15% of 90 dispatch adjustments [Ref: A016]) = several per day |

### Non-Determinism Scores

**Scoring Scale (from atx-scoring.md)**:
- 5: High reasoning (synthesis of multiple data sources, policy interpretation, contextual judgment)
- 4: Significant reasoning (patterns with contextual adaptation and exception handling)
- 3: Mixed (core rule-based, exceptions require reasoning)
- 2: Mostly deterministic (small reasoning component around structured rules)
- 1: Fully deterministic (pure rules/logic, no reasoning)

| JtD | Non-Det Score | Rationale |
|-----|---------------|-----------|
| **DE-2**: Damaged Consignment | **5** | High reasoning: Damage liability assessment requires synthesis of photos (visual), damage patterns (historical), packaging quality (judgment), sender/route analysis, customer relationship context, credit amount determination [Ref: A017]. Multiple data sources + policy interpretation + contextual judgment. |
| **DA-3**: Driver Swap | **5** | High reasoning: Driver selection requires synthesis of availability (system), qualifications (tacit knowledge), relationship history (institutional), handoff logistics (judgment), overtime/contractor cost-benefit (policy), customer impact assessment. Negotiation-heavy, context-dependent [Ref: A002]. |
| **DE-1**: Refused Delivery | **4** | Significant reasoning: Refusal classification (NLP on unstructured narrative), disposition decision follows patterns but requires contextual adaptation (customer priority [A009], driver capacity, damage severity assessment, billing implications). Exception handling ~40% of cases [Ref: A005]. |
| **DA-2**: Route Diversion | **4** | Significant reasoning: Route impact assessment (rule-based calculation) + customer priority judgment (contextual), delay tolerance assessment (implicit rules [A019]), driver familiarity with alternate location (tacit knowledge), cascading delay management. Exception rate ~40% [Ref: A020]. |
| **DA-1**: Additional Pickup | **3** | Mixed: Core decision is rule-based (driver proximity, vehicle capacity, shift limits), but exceptions require reasoning (no capacity → escalation logic, customer timing conflict → negotiation, priority assessment [A009]). ~25% exception rate. |
| **DE-4**: Unattended Address | **2** | Mostly deterministic: Decision follows clear hierarchy (safe place authority → consignment eligibility → leave/return/re-deliver). Small reasoning component for policy conflicts (~5% [Ref: A026]) and customer preference interpretation. |
| **DE-3**: Missed Window | **2** | Mostly deterministic: Diagnosis is rule-based (lookup delivery status, retrieve GPS, calculate ETA from velocity + route sequence). Small reasoning for stale GPS (~10% cases) or customer escalation. Primary value is speed of data retrieval, not reasoning complexity. |

### Agentic Value Scores

**Agentic Value = Volume Score × Non-Determinism Score**

| Rank | JtD | Volume | Non-Det | Value Score | Interpretation |
|------|-----|--------|---------|-------------|----------------|
| 1 | **DE-2**: Damaged Consignment | 4 | 5 | **20** | Strong agentic candidate (≥15): High-value agent support for complex liability judgment |
| 2 | **DE-1**: Refused Delivery | 4 | 4 | **16** | Strong agentic candidate (≥15): High-value agent support for refusal reasoning |
| 3 | **DA-1**: Additional Pickup | 4 | 3 | **12** | Consider agentic (8-14): Validate with TCO, agent-led + oversight viable |
| 3 | **DA-2**: Route Diversion | 3 | 4 | **12** | Consider agentic (8-14): Validate with TCO, agent support valuable |
| 5 | **DA-3**: Driver Swap | 2 | 5 | **10** | Consider agentic (8-14): **However, low volume + Human Only archetype → fail economics, not prioritized** |
| 5 | **DE-3**: Missed Window | 5 | 2 | **10** | Consider agentic (8-14): **Despite moderate value score, HIGH volume + Fully Agentic archetype + low risk → TOP PRIORITY** |
| 7 | **DE-4**: Unattended Address | 4 | 2 | **8** | Consider agentic (8-14): Validate with TCO, agent-led + oversight viable |

**Key Insight**: Agentic Value Score alone is insufficient for prioritization. **DE-3** scores only 10 (tied for 5th), but is **Rank #1 overall** because:
- Fully Agentic archetype (85-95% autonomous) vs. Agent Support (40-60% load reduction)
- Highest volume (140 cases/day) maximizes absolute ROI
- Lowest risk enables fast deployment
- **Absolute savings > agentic value score** for prioritization

**Value Score interpretation adjusted**:
- DE-2, DE-1: High scores (16-20) reflect complex reasoning, but **Human-led + Support** archetype limits automation %
- DE-3: Moderate score (10) reflects low reasoning, but **Fully Agentic** archetype enables full automation → highest ROI

### Volume × Value Quadrant

|  | **LOW NON-DETERMINISM** | **HIGH NON-DETERMINISM** |
|---|---|---|
| **HIGH VOLUME** | **Q2: Rules/RPA Zone**<br>DE-3 (Missed Window) V=10<br>DE-4 (Unattended) V=8<br><br>⚠️ *Agent-eligible despite low reasoning due to NLP requirements* | **Q1: Primary Targets** ⭐<br>DE-1 (Refused) V=16<br>DE-2 (Damaged) V=20<br><br>✓ *Ideal agentic candidates* |
| **LOW-MED VOLUME** | **Q3: Not Automating**<br><br>*[No candidates]* | **Q4: Select Use Cases**<br>DA-2 (Route Diversion) V=12<br>DA-1 (Additional Pickup) V=12<br>DA-3 (Driver Swap) V=10<br><br>⚠️ *Moderate ROI; Wave 2+* |

**Quadrant Positions Explained**:

**Top-Right (High Volume, High Reasoning) - PRIMARY AGENTIC TARGETS**:
- **DE-1 (Refused Delivery)**: Volume 4, Non-Det 4 → Value 16
- **DE-2 (Damaged Consignment)**: Volume 4, Non-Det 5 → Value 20
- These are ideal agent candidates: high volume justifies investment, high reasoning means agents add significant value beyond simple automation

**Top-Left (High Volume, Low Reasoning) - RULES/RPA ZONE**:
- **DE-3 (Missed Window)**: Volume 5, Non-Det 2 → Value 10
- **DE-4 (Unattended Address)**: Volume 4, Non-Det 2 → Value 8
- **Normally** this quadrant suggests RPA, not agents. **However**: DE-3 and DE-4 require NLP for input parsing, dynamic ETA calculation, and exception handling (stale GPS, policy conflicts) → **agents are correct tool**, not RPA. This is why we use delegation archetypes (Fully Agentic, Agent-led) rather than dismissing based on quadrant alone.

**Mid-Right (Medium Volume, High Reasoning)**:
- **DA-2 (Route Diversion)**: Volume 3, Non-Det 4 → Value 12
- **DA-1 (Additional Pickup)**: Volume 4, Non-Det 3 → Value 12
- Solid agent candidates, especially if inheriting platform assets from Wave 1

**Bottom-Right (Low Volume, High Reasoning) - SELECT USE CASES**:
- **DA-3 (Driver Swap)**: Volume 2, Non-Det 5 → Value 10
- High reasoning suggests agent value, but **low volume + Human Only archetype** → economics don't close. Correct decision: keep as human-only.

**Prioritization Ranking (Quadrant + Archetype + ROI)**:
1. **DE-3** (top-left but Fully Agentic + highest volume → #1)
2. **DE-4** (top-left, Agent-led + low risk → #2)
3. **DA-1** (mid-region, Agent-led → #3)
4. **DE-1** (top-right, high reasoning → #4)
5. **DE-2** (top-right, highest reasoning → #5)
6. **DA-2** (mid-right → #6)
7. **DA-3** (bottom-right, Human Only → not prioritized)

---

## Step 3: Total Cost of Ownership Assessment

### Baseline Human Costs

**Assumptions**:
- Fully loaded hourly cost: £19/hour (£35K annual salary ÷ 1,840 working hours/year) [Ref: A018]
- Working days: 230 days/year (365 - 104 weekend - 31 holiday/sick)

| JtD | Cases/Day | Cases/Year | Time/Case (min) | Annual Hours | Baseline Cost/Year |
|-----|-----------|------------|-----------------|--------------|---------------------|
| **DE-3**: Missed Window | 140 | 32,200 | 8 | 4,293 | **£81,567** |
| **DE-1**: Refused Delivery | 54 | 12,420 | 12 | 2,484 | **£47,196** |
| **DE-4**: Unattended Address | 45 | 10,350 | 10 | 1,725 | **£32,775** |
| **DA-1**: Additional Pickup | 36 | 8,280 | 18 | 2,484 | **£47,196** |
| **DE-2**: Damaged Consignment | 36 | 8,280 | 15 | 2,070 | **£39,330** |
| **DA-2**: Route Diversion | 27 | 6,210 | 18 | 1,863 | **£35,397** |
| **DA-3**: Driver Swap | 12 | 2,760 | 28 | 1,288 | **£24,472** |

**Total Baseline**: £307,933/year across 350 cases/day (excludes DA-3 from automation candidates = £283,461)

### Agent Cost Model

**Model Assumptions**:
- Model: Claude Sonnet 4.5 (optimal cost/accuracy tradeoff)
- Input token cost: £0.015 per 1K tokens
- Output token cost: £0.075 per 1K tokens
- API call cost (CRM, GPS, SMS): £0.05 per call (average across endpoints)
- Infrastructure allocation: Fixed £35K/year across all use cases [Ref: A027]

#### Token Estimates by JtD

| JtD | Input Tokens | Output Tokens | Reasoning |
|-----|--------------|---------------|-----------|
| **DE-3** | 1,500 | 300 | Input: Order details (200) + GPS data (300) + route plan (400) + customer SLA (200) + historical timing (400). Output: ETA calculation + notification text. **Caching opportunity**: Route plan and historical timing can be cached [Ref: A030]. |
| **DE-4** | 1,200 | 250 | Input: Customer preferences (300) + consignment details (300) + delivery instructions (300) + policy rules (300). Output: Decision + notification text. |
| **DA-1** | 2,000 | 400 | Input: Customer pickup request (500) + driver locations (500) + vehicle manifests (400) + route plans (600). Output: Feasibility analysis + recommendation + notifications. |
| **DE-1** | 2,500 | 600 | Input: Driver report (500) + customer history (400) + consignment details (300) + refusal classification (500) + disposition rules (800). Output: Classification + recommendation + draft communications. |
| **DE-2** | 3,000 | 700 | Input: Damage photos (1,000 vision tokens) + damage history (500) + consignment/sender details (500) + liability rules (700) + customer context (300). Output: Liability assessment + credit recommendation + communications + audit log. |
| **DA-2** | 2,500 | 500 | Input: Diversion request (400) + current route (600) + affected deliveries (500) + customer priority (300) + traffic data (400) + decision rules (300). Output: Impact analysis + recommendation + communications. |

**Note**: DA-3 not included (Human Only archetype, no autonomous agent cost)

#### Cost Per Case Calculations

| JtD | Token Cost | API Calls | API Cost | HITL % | HITL Cost | Agent Cost/Case | Cases/Year | Annual Agent Cost |
|-----|------------|-----------|----------|--------|-----------|-----------------|------------|-------------------|
| **DE-3** | £0.045 | 4 (CRM, GPS, route, SMS) | £0.20 | 10% | £0.32 | **£0.57** | 32,200 | **£18,354** |
| **DE-4** | £0.037 | 3 (CRM, order, SMS) | £0.15 | 20% | £0.63 | **£0.82** | 10,350 | **£8,487** |
| **DA-1** | £0.060 | 5 (CRM, GPS, dispatch, vehicle, SMS) | £0.25 | 25% | £1.19 | **£1.50** | 8,280 | **£12,420** |
| **DE-1** | £0.090 | 5 (CRM, driver app, dispatch, case, notify) | £0.25 | 50% | £1.90 | **£2.24** | 12,420 | **£27,821** |
| **DE-2** | £0.098 | 5 (CRM, photos, history, billing, notify) | £0.25 | 60% | £2.28 | **£2.61** | 8,280 | **£21,609** |
| **DA-2** | £0.090 | 6 (CRM, dispatch, GPS, traffic, route, notify) | £0.30 | 60% | £2.28 | **£2.67** | 6,210 | **£16,581** |

**Infrastructure Allocation by Wave**:
- Wave 1 (DE-3, DE-4, DA-1): £25K/year (supervision 0.3 FTE, monitoring, platform overhead) [Ref: A031]
- Wave 2 (add DE-1, DE-2, DA-2): +£10K/year (supervision 0.5 FTE total, expanded monitoring) [Ref: A031]

### ROI Calculations by JtD

#### Wave 1 Candidates

**DE-3: Missed Window Investigation**
- Baseline cost: £81,567/year
- Agent cost: £18,354 + £10K infrastructure allocation = £28,354/year [Ref: A032]
- **Annual saving: £53,213**
- Build cost estimate: £30K (CRM integration £8K, GPS API £6K, ETA engine £10K, notification automation £4K, testing £2K)
- **Payback period: 6.8 months**
- **Year 1 ROI: 77%** = (£53,213 - £30K) / £30K
- **3-year ROI: 431%** = ((£53,213 × 3) - £30K) / £30K

**DE-4: Unattended Address**
- Baseline cost: £32,775/year
- Agent cost: £8,487 + £8K infrastructure allocation = £16,487/year [Ref: A032]
- **Annual saving: £16,288**
- Build cost estimate: £15K (inherits CRM from DE-3, safe place rules £5K, re-delivery scheduling £6K, testing £2K, CRM field additions £2K)
- **Payback period: 11.1 months**
- **Year 1 ROI: 9%** = (£16,288 - £15K) / £15K
- **3-year ROI: 225%** = ((£16,288 × 3) - £15K) / £15K

**DA-1: Additional Pickup**
- Baseline cost: £47,196/year (assumes 70% automation due to dispatch console constraint [A004])
- Achievable saving: £47,196 × 70% = £33,037
- Agent cost: £12,420 + £7K infrastructure allocation = £19,420/year [Ref: A032]
- **Annual saving: £13,617** (conservative due to HITL execution in dispatch console)
- Build cost estimate: £20K (inherits CRM + GPS from DE-3, route calculator £8K, vehicle capacity integration £5K, approval dashboard £4K, testing £3K)
- **Payback period: 17.7 months**
- **Year 1 ROI: -32%** = (£13,617 - £20K) / £20K (negative Year 1, breakeven Month 18)
- **3-year ROI: 104%** = ((£13,617 × 3) - £20K) / £20K

**Wave 1 Combined**:
- Total annual saving: £53,213 + £16,288 + £13,617 = **£83,118**
- Total build cost: £30K + £15K + £20K = **£65K**
- Blended payback: 9.4 months
- **Wave 1 Year 1 ROI: 28%** = (£83,118 - £65K) / £65K
- **Wave 1 3-year ROI: 283%** = ((£83,118 × 3) - £65K) / £65K

**Note**: Wave 1 ROI is lower than original estimate (37% → 28%) because DA-1 has negative Year 1 due to dispatch console constraint. **Decision point**: Consider dropping DA-1 from Wave 1 if fast payback is critical, or proceed if 9-month blended payback is acceptable [Ref: A033].

#### Wave 2 Candidates

**DE-1: Refused Delivery**
- Baseline cost: £47,196/year
- Agent support saves 55% of handling time (not full automation) [Ref: A034]
- Achievable saving: £47,196 × 55% = £25,958
- Agent cost: £27,821 + £3.5K infrastructure allocation = £31,321/year [Ref: A032]
- **Annual net impact: -£5,363** (agent cost exceeds savings) ⚠️
- **Issue identified**: High HITL rate (50%) + complex token requirements → **economics marginal**
- Build cost estimate: £25K (inherits CRM + GPS from Wave 1, NLP classification £8K, decision tree implementation £8K, recommendation UI £6K, testing £3K)
- **Recommendation**: **Defer to Wave 3** until decision rules are formalized [A005] to reduce HITL rate to 30%, improving economics to +£9K net saving [Ref: A035]

**DE-2: Damaged Consignment**
- Baseline cost: £39,330/year
- Agent support saves 55% of handling time [Ref: A034]
- Achievable saving: £39,330 × 55% = £21,632
- Agent cost: £21,609 + £3.5K infrastructure allocation = £25,109/year [Ref: A032]
- **Annual net impact: -£3,477** (agent cost exceeds savings) ⚠️
- **Issue identified**: High HITL rate (60%) + vision tokens → **economics marginal**
- Build cost estimate: £35K (inherits CRM from Wave 1, image recognition £15K, liability criteria implementation £8K, Aurum integration £6K, recommendation UI £4K, testing £2K)
- **Recommendation**: **Defer to Wave 3** until liability criteria formalized [A017] and image recognition model trained, reducing HITL to 40% → +£6K net saving [Ref: A035]

**DA-2: Route Diversion**
- Baseline cost: £35,397/year
- Agent support saves 50% of handling time (impact analysis, communication drafting) [Ref: A034]
- Achievable saving: £35,397 × 50% = £17,699
- Agent cost: £16,581 + £3K infrastructure allocation = £19,581/year [Ref: A032]
- **Annual net impact: -£1,882** (agent cost exceeds savings) ⚠️
- **Issue identified**: High HITL rate (60%) + dispatch console constraint [A004] → **economics marginal**
- Build cost estimate: £22K (inherits CRM + GPS + route calc from Wave 1, traffic API £5K, impact calculator £7K, decision rules £6K, testing £4K)
- **Recommendation**: **Defer to Wave 3** until decision rules formalized [A019] and dispatch console API resolved, reducing HITL to 40% → +£5K net saving [Ref: A035]

**Wave 2 Economics Insight**: All three "Human-led + Agent Support" candidates have **negative net economics** in current state due to high HITL rates and insufficient cognitive load reduction to offset agent costs. **Revised strategy**: Deploy Wave 1 only, use savings and operational learnings to formalize decision rules, then re-assess Wave 2 viability in 12-18 months [Ref: A036].

---

## Step 4: Feasibility Scoring Matrix

**Scoring Scale (1-5)**:
- 5: Excellent feasibility, no significant barriers
- 4: Good feasibility, minor challenges manageable
- 3: Moderate feasibility, requires planning/investment
- 2: Challenging feasibility, significant risks or dependencies
- 1: Poor feasibility, major blockers or high risk

| JtD | Data Availability | System Integration | Compliance Risk | Context Stability | Org Readiness | TCO Viability | Total Score | Avg |
|-----|-------------------|--------------------| ----------------|-------------------|---------------|---------------|-------------|-----|
| **DE-3** | 5 (CRM, GPS, route data accessible) | 4 (CRM + GPS APIs available, ETA engine buildable) | 5 (low risk, no PII sensitivity) | 5 (stable domain, ETA logic unchanging) | 5 (low risk, high customer value) | 5 (£53K saving, 7-month payback) | **29/30** | **4.8** |
| **DE-4** | 5 (CRM preferences, order data accessible) | 4 (CRM API, re-delivery scheduling buildable) | 4 (medium risk: theft liability, mitigatable with rules) | 5 (stable policies) | 4 (requires supervision setup) | 4 (£16K saving, 11-month payback) | **26/30** | **4.3** |
| **DA-1** | 4 (GPS + vehicle data mostly accessible) | 2 (dispatch console API limited [A004], workaround viable) | 4 (medium risk: overload if capacity miscalculated) | 4 (stable domain, occasional volume spikes [A011]) | 4 (requires dispatch coordinator buy-in) | 3 (£14K saving, 18-month payback) | **21/30** | **3.5** |
| **DE-1** | 4 (CRM + driver app accessible, refusal data unstructured) | 4 (inherits Wave 1 APIs, NLP buildable) | 4 (medium risk: wrong disposition → customer dissatisfaction) | 3 (decision rules need formalization [A005]) | 3 (requires Sandra engagement for decision elicitation) | 2 (negative net economics without rule formalization) | **20/30** | **3.3** |
| **DA-2** | 4 (GPS + route data accessible, traffic API needed) | 2 (dispatch console API limited [A004], traffic API integration) | 4 (medium risk: wrong diversion → SLA breach) | 3 (decision rules need formalization [A019], customer priorities [A009]) | 3 (requires dispatch team buy-in, Sarah engagement) | 2 (negative net economics in current state) | **18/30** | **3.0** |
| **DE-2** | 3 (photos variable quality, damage history fragmented) | 3 (inherits CRM, Aurum lag [A007], image recognition training needed) | 4 (medium risk: wrong liability → financial loss) | 2 (liability criteria need formalization [A017], recurring domain changes) | 3 (requires supervisor engagement, photo quality improvement) | 2 (negative net economics without criteria formalization) | **17/30** | **2.8** |
| **DA-3** | 3 (driver data partial, qualifications in HR or tacit) | 2 (workforce system API unclear [A002], dispatch console limited) | 2 (high risk: driver welfare, regulatory compliance) | 3 (stable but relationship-dependent [A002]) | 2 (senior dispatchers may resist, union concerns) | 1 (£2-3K saving, not viable) | **13/30** | **2.2** |

**Feasibility Ranking**:
1. **DE-3** (4.8/5): Excellent feasibility across all dimensions, ready for immediate deployment
2. **DE-4** (4.3/5): Strong feasibility, minor supervision setup needed
3. **DA-1** (3.5/5): Moderate feasibility, dispatch console constraint manageable with workaround
4. **DE-1** (3.3/5): Moderate feasibility, decision rule formalization required
5. **DA-2** (3.0/5): Moderate feasibility, multiple dependencies (API, rules)
6. **DE-2** (2.8/5): Challenging feasibility, image recognition + criteria formalization
7. **DA-3** (2.2/5): Poor feasibility, not prioritized

**Feasibility Insights**:
- **Wave 1 candidates** (DE-3, DE-4, DA-1) average **4.2/5 feasibility** → ready for deployment
- **Wave 2 candidates** (DE-1, DA-2, DE-2) average **3.0/5 feasibility** → require preparation work (decision rules, API access)
- **DA-3**: 2.2/5 feasibility confirms Human Only archetype is correct

---

## Step 5: Strategic Sequencing

**Sequencing Criteria (from atx-scoring.md)**:
- Self-financing ROI (high weight): Wave 1 must pay for itself
- Integration reusability (high weight): Build shared assets for Wave 2
- Low compliance risk (medium): Start with lower-risk use cases
- Data readiness (medium): Clean, accessible data moves faster
- Organisational readiness (medium): Stakeholder buy-in
- Strategic visibility (low): Executive sponsorship value

### Wave 1 (Self-Funding Foundation)

**Candidates**: DE-3, DE-4, (DA-1 optional)

**Why These JtDs**:
1. **Self-financing**: £83K annual saving (DE-3 + DE-4 + DA-1) or £69K (excluding DA-1) vs. £65K build (with DA-1) or £45K (without DA-1)
   - **With DA-1**: Year 1 net £18K, payback 9 months [Ref: A033]
   - **Without DA-1**: Year 1 net £24K, payback 7 months (faster but smaller absolute savings) [Ref: A037]
2. **Integration reusability**: Builds CRM API integration, GPS/driver app integration, ETA calculation engine, notification automation → **all reused in Wave 2**
3. **Low compliance risk**: DE-3 (low risk), DE-4 (medium risk, mitigatable), DA-1 (medium risk)
4. **Data readiness**: High (CRM, GPS, route data accessible)
5. **Organisational readiness**: High customer satisfaction impact (ETA inquiries, unattended deliveries) builds stakeholder support

**Recommended Platform Assets Built in Wave 1**:
- CRM API integration (Salesforce REST API wrapper, case management, notifications)
- Driver app GPS API integration (location, delivery status, route sequencing)
- ETA calculation engine (GPS velocity + historical route timing + traffic API)
- SMS/email notification automation
- Human oversight dashboard (review sample, escalation handling)
- Agent monitoring and logging (token usage, error rates, escalations)

**Wave 1 Timeline**: Months 1-6
- Month 1-2: DE-3 pilot (build + 2-week shadow mode)
- Month 3-4: DE-4 expansion (inherits CRM + GPS from DE-3)
- Month 5-6: DA-1 expansion (optional, inherits CRM + GPS + adds route calculator) OR skip to Wave 2 preparation

**Wave 1 Funding**: £65K build cost (or £45K without DA-1), self-financed from operational budget or prior savings

### Wave 2 (Revised: Preparation Phase)

**Original Candidates**: DE-1, DE-2, DA-2  
**Revised Strategy**: **Defer to Wave 3** due to negative net economics in current state [Ref: A036]

**Wave 2 Focus (Months 7-18)**: **Prepare for Wave 3** by addressing blockers:
1. **Formalize decision rules**:
   - A005: Refused delivery disposition logic (shadow Sandra 20+ cases, codify decision tree)
   - A017: Damage liability assessment criteria (review 50+ historical cases, train image recognition model)
   - A019: Route diversion decision rules (shadow coordinators 20+ cases, codify impact thresholds)
2. **Implement customer priority system** [A009]: Formalize tier structure in CRM
3. **Validate dispatch console API** [A004]: Technical discovery, build API wrapper if needed
4. **Monitor Wave 1 performance**: Collect 6-12 months operational data on token costs, HITL rates, escalation patterns to refine Wave 3 estimates

**Wave 2 Investment**: £40-50K (decision rule elicitation, NLP training, image recognition model, API wrapper) funded by Wave 1 savings (£83K Year 1 leaves £33K+ for Wave 2 preparation) [Ref: A038]

### Wave 3 (Human-Led + Agent Support, Months 19-24)

**Candidates**: DE-1, DE-2, DA-2 (if economics improve post-preparation)

**Why Defer to Wave 3**:
- Current HITL rates (50-60%) make agent costs exceed savings
- Decision rule formalization in Wave 2 reduces HITL to 30-40% → positive economics [Ref: A035]
- Image recognition model training (6-12 months) required for DE-2 viability
- Wave 1 platform assets (CRM, GPS, NLP) reduce Wave 3 marginal build cost by 40-50% [Ref: A028]

**Wave 3 Economics (Post-Preparation)**:
- **DE-1** (with formalized rules [A005] → HITL 30%): £47K baseline × 60% automation - £24K agent cost = **£4K net saving**
- **DE-2** (with formalized criteria [A017] → HITL 40%): £39K baseline × 60% automation - £22K agent cost = **£1K net saving**
- **DA-2** (with formalized rules [A019] → HITL 40%): £35K baseline × 55% automation - £17K agent cost = **£2K net saving**

**Wave 3 Combined**: £7K net saving (marginal, but strategic value in cognitive load reduction and platform learning) [Ref: A039]

**Wave 3 Timeline**: Months 19-24 (conditional on Wave 2 preparation completion and positive economics validation)

### Multi-Agent Workflows (Wave 4+, Months 25+)

**Cross-Work-Stream Orchestration**: ~25% of cases span multiple work streams (delivery exception → billing dispute → dispatch adjustment) [Ref: A012]

**Example Flow**: Refused delivery (DE-1) triggers damage report (DE-2) which triggers credit request (billing work stream) and re-delivery (DA-1)

**Platform Maturity Required**:
- Shared case context across agents
- Event-driven workflow triggers
- Cross-agent handoff protocols
- Unified monitoring and audit

**Not prioritized in current roadmap** but flagged for future consideration.

---

## Prioritised Candidate Shortlist

### Tier 1: Wave 1 Deploy (Months 1-6)

| Rank | JtD | Archetype | Volume/Day | Annual Saving | Build Cost | Payback | Feasibility | Key Assets Built |
|------|-----|-----------|------------|---------------|------------|---------|-------------|------------------|
| **1** | **DE-3: Missed Window Investigation** | Fully Agentic | 140 | **£53K** | £30K | **7 months** | 4.8/5 | CRM API, GPS API, ETA engine, notifications |
| **2** | **DE-4: Unattended Address** | Agent-led + Oversight | 45 | **£16K** | £15K | **11 months** | 4.3/5 | Safe place rules, re-delivery scheduling |
| **3** | **DA-1: Additional Pickup** | Agent-led + Oversight | 36 | **£14K** | £20K | **18 months** | 3.5/5 | Route calculator, vehicle capacity integration |

**Wave 1 Summary**:
- **Combined annual saving**: £83K (or £69K if DA-1 deferred)
- **Combined build cost**: £65K (or £45K if DA-1 deferred)
- **Blended payback**: 9 months (or 7 months if DA-1 deferred)
- **Platform assets**: CRM + GPS integrations, ETA engine, notification automation → reused in Waves 2-3
- **Recommendation**: Deploy DE-3 (pilot) + DE-4 (expansion). **Consider deferring DA-1** if fast payback is critical (7 months vs. 9 months) or dispatch console API blocker is unresolved [Ref: A033, A037].

### Tier 2: Wave 2 Preparation (Months 7-18)

**No deployments**. Focus on:
1. Formalize decision rules [A005, A017, A019]
2. Implement customer priority system [A009]
3. Resolve dispatch console API [A004]
4. Train image recognition model (6-12 months for DE-2)
5. Monitor Wave 1 performance and refine cost estimates

**Investment**: £40-50K (funded by Wave 1 savings)

### Tier 3: Wave 3 Deploy (Months 19-24, Conditional)

| Rank | JtD | Archetype | Volume/Day | Annual Saving (Post-Prep) | Build Cost | Feasibility | Dependency |
|------|-----|-----------|------------|---------------------------|------------|-------------|------------|
| **4** | **DE-1: Refused Delivery** | Human-led + Agent Support | 54 | **£4K** (net) | £25K | 3.3/5 | Decision rules [A005] |
| **5** | **DE-2: Damaged Consignment** | Human-led + Agent Support | 36 | **£1K** (net) | £35K | 2.8/5 | Liability criteria [A017], image model |
| **6** | **DA-2: Route Diversion** | Human-led + Agent Support | 27 | **£2K** (net) | £22K | 3.0/5 | Decision rules [A019], API [A004] |

**Wave 3 Summary**:
- **Combined annual saving**: £7K (marginal economics)
- **Combined build cost**: £82K
- **Strategic value**: Cognitive load reduction (40-60%) for complex judgment tasks, platform learning for multi-agent workflows
- **Recommendation**: **Proceed only if** Wave 2 preparation successfully reduces HITL rates and economics validate positive ROI. Alternative: defer indefinitely and focus on expanding to other work streams (ETA inquiries, billing disputes) using proven Wave 1 platform.

### Not Prioritized

| JtD | Archetype | Rationale |
|-----|-----------|-----------|
| **DA-3: Driver Swap** | Human Only | Low volume (12/day), high complexity (relationship-dependent negotiation), high risk (driver welfare, regulatory), £2-3K savings insufficient. Correct resource: senior dispatcher expertise. Agent role limited to 10-20% administrative support (data retrieval, logging). |

---

## Implementation Sequencing Logic

### Funding Model: Self-Financing Waves

**Wave 1 Funds Wave 2 Preparation**:
- Wave 1 annual saving: £83K (with DA-1) or £69K (without DA-1)
- Wave 1 build cost: £65K (with DA-1) or £45K (without DA-1)
- Year 1 net cash: £18K (with DA-1) or £24K (without DA-1)
- Year 2 full-year saving: £83K or £69K
- **Available for Wave 2 prep investment**: £83K (Year 2) - £40-50K prep cost = £33-43K surplus

**Wave 2 Preparation Enables Wave 3**:
- Decision rule formalization, customer priority system, API resolution, image recognition model training
- Reduces Wave 3 HITL rates from 50-60% → 30-40%
- Improves Wave 3 economics from negative → marginal positive (£7K net saving)
- Without Wave 2 prep, Wave 3 is not viable [Ref: A036]

**Wave 3 Conditional Proceed**:
- If Wave 2 prep achieves target HITL reduction → proceed with Wave 3 (£7K net saving)
- If HITL remains high → pivot to expanding Wave 1 platform to other work streams (ETA inquiries, billing disputes) instead of Wave 3

### Sequencing Decision Points

**Decision Point 1 (Month 3)**: After DE-3 pilot
- **Go/No-Go**: Does DE-3 achieve 85%+ autonomous rate and <5% error rate?
- **If Go**: Proceed to DE-4 expansion
- **If No-Go**: Iterate on DE-3 (refine ETA algorithm, improve escalation logic) before expanding

**Decision Point 2 (Month 5)**: After DE-4 expansion
- **Include DA-1?**: Has dispatch console API blocker been resolved or workaround validated?
- **If Yes**: Proceed to DA-1 (9-month blended payback)
- **If No**: Skip DA-1, close Wave 1 at £69K annual saving (7-month payback), redirect effort to Wave 2 prep [Ref: A037]

**Decision Point 3 (Month 12)**: Mid-Wave 2 Preparation
- **Go/No-Go to Wave 3**: Are decision rules formalized [A005, A017, A019]? Is customer priority system implemented [A009]?
- **If Yes**: Validate economics (run mock tests with formalized rules, measure expected HITL reduction), proceed to Wave 3 if ROI positive
- **If No**: Extend Wave 2 prep timeline or pivot strategy

**Decision Point 4 (Month 18)**: Pre-Wave 3
- **Wave 3 vs. Pivot**: Do validated economics show positive ROI for DE-1, DE-2, DA-2?
- **If Yes**: Proceed to Wave 3
- **If No**: Pivot to expanding Wave 1 platform to other high-ROI work streams (ETA inquiries full automation, billing disputes)

### Platform Compounding Thesis

**Wave 1 Platform Assets** (built once, reused forever):
- CRM API integration → used in DE-4, DA-1, DE-1, DE-2, DA-2, future work streams
- GPS/driver app integration → used in DA-1, DA-2, future dispatch work streams
- ETA calculation engine → used in Wave 1 + future ETA-related workflows
- Notification automation → used across all work streams
- Oversight dashboard → scales to supervise all agents

**Wave 2 Platform Additions**:
- NLP classification engine → used in DE-1, DE-2, future exception classification
- Image recognition model → used in DE-2, future visual inspection tasks
- Decision tree framework → used in DE-1, DE-2, DA-2, future judgment-support tasks

**Compounding Benefit**: Each new agent built on Wave 1 platform has **40-50% lower marginal build cost** than standalone [Ref: A028]. By Wave 3, marginal cost approaches £10-15K per new agent (vs. £25-35K standalone).

**3-Year Cumulative ROI** (if all waves deploy):
- Wave 1 savings: £83K × 3 years = £249K
- Wave 2 prep investment: -£45K
- Wave 3 savings: £7K × 1.5 years (partial year) = £10.5K
- Total build cost: £65K (Wave 1) + £45K (Wave 2) + £82K (Wave 3) = £192K
- **3-year net benefit**: £249K + £10.5K - £192K = **£67.5K**
- **3-year ROI**: £67.5K / £192K = **35%** (modest but strategic) [Ref: A029]

**Alternative 3-Year ROI** (Wave 1 only, pivot to other work streams):
- Wave 1 savings: £83K × 3 years = £249K
- Expand to ETA inquiries (400/day), billing disputes (60/day): estimated +£120K/year × 2 years = £240K [Ref: A040]
- Total build cost: £65K (Wave 1) + £80K (other work streams) = £145K
- **3-year net benefit**: £249K + £240K - £145K = **£344K**
- **3-year ROI**: £344K / £145K = **237%** (significantly higher) [Ref: A040]

**Strategic Recommendation**: Deploy Wave 1, assess Wave 2 prep progress at Month 12, **pivot to other work streams if Wave 3 economics remain marginal**. Platform value is in reusability across work streams, not necessarily in completing all original candidates [Ref: A041].

---

## Document Control

- **Created**: 2026-05-06
- **Version**: 1.0
- **Owner**: AI FDE Team
- **Related Documents**:
  - `1-cognitive-load-map.md` - Source JtDs and micro-tasks
  - `2-delegation-suitability-matrix.md` - Archetype assignments
  - `assumptions.md` - Assumptions A001-A041
  - `input-docs/atx-scoring.md` - Scoring methodology
  - `input-docs/atx-assessment.md` - Phase 4 definitions
- **Next Phase**: Agent Mapping (detailed agent design for Wave 1 candidates)
