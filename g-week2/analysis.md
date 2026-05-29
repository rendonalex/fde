# Executive Summary: Agent Selection and Strategic Decisions

## Overview

Analyzed 7 Jobs to be Done (JtDs) across Apex Distribution's Customer Operations, decomposing 48 micro-tasks and evaluating delegation suitability. **Selected DE-3 (ETA Investigation Agent) as Wave 1 pilot** based on highest ROI, lowest risk, and strongest platform compounding potential.

---

## Key Decisions Made

### 1. Delegation Archetype Framework
**Decision**: Used 7-dimension suitability scoring (Input Structure, Decision Determinism, Tool Coverage, Context Complexity, Exception Rate, Latency Constraint, Risk/Compliance) to classify JtDs into 4 archetypes.

**Rationale**: Prevents over-automation of unsuitable tasks. Only 1 of 7 JtDs scored "Fully Agentic" — attempting to automate all would have failed.

**Outcome**:
- 1 Fully Agentic: DE-3 (ETA Investigation - Missed window investigation)
- 2 Agent-led + Oversight: DE-4 (Unattended Address), DA-1 (Additional Pickups)
- 3 Human-led + Agent Support: DE-1, DE-2, DA-2
- 1 Human Only: DA-3 (Driver Swap)

### 2. Prioritization Methodology
**Decision**: Used Volume × Value scoring, weighing both annual savings AND non-determinism (agentic value). Rejected pure ROI ranking.

**Rationale**: DA-3 had highest volume (85 cases/day) but scored "Human Only" — high volume doesn't justify automation if delegation is unsuitable.

**Outcome**: DE-3 ranked #1 despite DA-3 having higher volume, because DE-3 is fully autonomous (10% HITL) vs DA-3 requiring 100% human judgment.

### 3. Wave Sequencing Strategy
**Decision**: Wave 1 = Self-financing pilot (DE-3 + DE-4 + DA-1). Wave 2 = **Preparation, not deployment** (formalize decision rules, no new agents).

**Rationale**: Wave 3 agents (DE-1, DE-2, DA-2) have negative economics if built immediately due to:
- High HITL rates (30-40%) from tacit knowledge gaps
- 18-23 month payback periods
- Decision rule formalization required (6-12 months, £50K investment)

**Outcome**: Wave 2 prep de-risks Wave 3 by formalizing liability rules, priority systems, and diversion criteria. Breaks even in Month 12 when Wave 2 infrastructure enables Wave 3 deployment.

### 4. Platform Compounding Approach
**Decision**: Built reusable integrations in Wave 1 (CRM API, GPS API, ETA engine, notification automation, monitoring platform) to reduce Wave 2-3 build costs 40-50%.

**Rationale**: Building 6 agents standalone = £232K total. Building with platform reuse = £147K (£85K savings).

**Outcome**: Every £1 spent on Wave 1 yields £1.77 in avoided Wave 2-3 build costs.

---

## Why DE-3 (ETA Investigation Agent) is the Right Choice

### Quantitative Reasons
1. **Highest absolute savings**: £53K/year (vs. DE-4 £16K, DA-1 £14K)
2. **Fastest payback**: 7 months (vs. 11-18 months for other candidates)
3. **Highest Year 1 ROI**: 77%
4. **Lowest HITL rate**: 10% (90% autonomous coverage)

### Qualitative Reasons
1. **Fully Agentic archetype**: All 7 suitability dimensions scored HIGH or MEDIUM. No LOW dimensions = predictable, rule-based workflow with clear escalation triggers.

2. **Lowest risk profile**: 
   - Wrong ETA is easily corrected (customer calls back)
   - No financial liability (no refunds, no contract penalties)
   - No safety/compliance concerns
   - No irreversible actions

3. **Strongest platform compounding**:
   - CRM API → reused by all 6 future agents
   - GPS API → reused by DA-1, DA-2 (dispatch agents)
   - ETA engine → reused by DE-4 (re-delivery timing), DA-1 (pickup feasibility)
   - Notification automation → reused by all customer-facing agents
   - **75% of Wave 1 assets reused in Waves 2-3**

4. **Clear success metrics**: 
   - ±30 min accuracy target (measurable via delivery timestamp comparison)
   - 90% autonomous coverage (measurable via escalation rate)
   - 2-min response time (measurable via processing logs)

5. **Customer satisfaction impact**: Reduces 4-hour ETA windows to 20-minute precision — tangible value-add over current "best guess" approach.

---

## Discovery Questions That Could Change the Decision

### Go/No-Go Blockers (Would Kill DE-3 as Wave 1 Pilot)

**1. Driver App API Unavailable** (Discovery Q3)
- **If**: Driver app backend has no API and database access denied
- **Impact**: Agent cannot retrieve GPS/delivery status (blocks ETA calculation entirely)
- **Contingency**: 
  - Option A: Build API wrapper (adds 2-3 weeks, increases build cost £30K→£35K, payback 7→8 months) — **still viable**
  - Option B: Pivot to **DE-4 (Unattended Address)** as Wave 1 pilot (£16K/year, 11-month payback, lower ROI but no GPS dependency)

**2. Historical Timing Data Completeness <20 samples/route** (Discovery Q5, Q8)
- **If**: Driver app logs incomplete (timestamps missing, <6 months history)
- **Impact**: ETA calculation accuracy drops to 70-80% (below 95% target), HITL rate increases 10%→25%, savings drop £53K→£41K
- **Delegation archetype shift**: Fully Agentic → Agent-led + Oversight (human reviews all ETAs before sending)
- **Contingency**: Use default timing assumptions (15 min/stop), deploy in shadow mode for 3-6 months to collect clean data, then launch production

### Archetype Downgrades (Would Reduce Autonomy)

**3. Sandra's Tacit Knowledge Non-Codifiable** (Discovery Q2)
- **If**: Sandra uses undocumented rules that cannot be encoded (e.g., "I just know when Hayes & Sons needs a call")
- **Impact**: HITL rate increases 10%→30%, savings drop £53K→£37K, payback 7→10 months
- **Delegation archetype shift**: Fully Agentic → Agent-led + Oversight
- **Decision impact**: DE-3 remains viable but less attractive. **DE-4 or DA-1 may have similar economics at that point**, so Wave 1 prioritization changes.

**4. 99% Accuracy + 6-Month Shadow Mode Required** (Discovery Q10)
- **If**: Ops leadership demands 99% accuracy (vs. 95%) and 6-month shadow mode before autonomous communication
- **Impact**: Payback extends 7→13 months, ROI drops 77%→41%, shadow mode adds £15K build cost
- **Decision impact**: DE-3 still viable but **delayed autonomy reduces Year 1 savings**. May prefer quick-win agent (DE-4) for pilot, then graduate DE-3 to production in Wave 2.

### Economics Shifts (Would Change Prioritization)

**5. Customer ETA Tolerance ±60 min (not ±30 min)** (Discovery Q4)
- **If**: Customers satisfied with ±60 min accuracy (relaxed precision target)
- **Impact**: Traffic API becomes unnecessary (removes £256/year cost), ETA engine simpler (reduces build cost £10K→£7K)
- **Decision impact**: DE-3 becomes **even more attractive** (cheaper to build, faster payback)

**6. GPS Reliability 22% Stale Cases** (Discovery Q5)
- **If**: >20% of deliveries have GPS >30 min stale (vs. assumed 10%)
- **Impact**: HITL rate increases 10%→25%, confidence threshold must tighten (70%→85%), savings drop £53K→£41K
- **Delegation archetype shift**: Fully Agentic → Agent-led + Oversight
- **Decision impact**: DE-3 remains #1 but economics weaken. If GPS issues are geographic (e.g., rural routes only), **pilot in urban-only routes** to maintain autonomy.

---

## Combined Worst-Case Scenario

**If 3+ discovery questions answered unfavorably**:
- Driver App API requires wrapper build (+3 weeks)
- GPS stale 22% of cases (HITL +15%)
- Sandra's rules 30% non-codifiable (HITL +20%)
- 99% accuracy demanded (shadow mode 6 months)

**Outcome**: 
- DE-3 archetype: Fully Agentic → Human-led + Agent Support
- HITL rate: 10% → 50%
- Savings: £53K → £26K/year
- Payback: 7 months → 20 months
- **ROI becomes negative in Year 1**

**Contingency**: **Pivot to DE-4 as Wave 1 pilot**
- DE-4 less dependent on GPS accuracy (re-delivery scheduling, not real-time ETA)
- DE-4 savings: £16K/year, 11-month payback
- Lower absolute ROI but **positive economics even in worst-case**
- Allows team to validate platform integrations (CRM API, notification automation) while deferring DE-3 until GPS/data issues resolved

---

## Recommendation

**Proceed with DE-3 as Wave 1 pilot** contingent on **Week 1 discovery validation**:
1. Confirm Driver App API availability (Go/No-Go gate)
2. Sample 1 month of driver app logs to validate timing data completeness
3. Interview Sandra to map ETA calculation rules (assess codifiability)

**Decision point Week 1**: If blockers detected (no API, poor data), pivot to DE-4. Otherwise, proceed with DE-3 build sprint (Months 1-3).

---

**Document Control**
- Created: 2026-05-06
- Version: 1.0
- Owner: AI FDE Team
