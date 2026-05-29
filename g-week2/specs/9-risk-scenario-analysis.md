# Risk Scenario Analysis: Worst-Case Discovery Outcomes

## Document Purpose

This document models how unfavorable answers to critical discovery questions would change delegation suitability scores, archetype assignments, and Wave 1 candidate prioritization. It provides contingency planning for Week 1 validation outcomes.

**Status**: Hypothetical analysis (pre-discovery validation)

---

## Table of Contents

1. [Risk Scenarios Overview](#risk-scenarios-overview)
2. [Scenario 1: Driver App API Unavailable](#scenario-1-driver-app-api-unavailable)
3. [Scenario 2: High GPS Staleness Rate](#scenario-2-high-gps-staleness-rate)
4. [Scenario 3: Sandra's Tacit Knowledge Non-Codifiable](#scenario-3-sandras-tacit-knowledge-non-codifiable)
5. [Scenario 4: High Route Plan Volatility](#scenario-4-high-route-plan-volatility)
6. [Scenario 5: Stakeholder Trust Threshold](#scenario-5-stakeholder-trust-threshold)
7. [Combined Worst-Case Scenario](#combined-worst-case-scenario)
8. [Revised Wave Sequencing](#revised-wave-sequencing)
9. [Contingency Recommendations](#contingency-recommendations)

---

## Risk Scenarios Overview

| Scenario | Discovery Question | Current Assumption | Worst-Case Answer | Impact Level |
|----------|-------------------|--------------------|--------------------|--------------|
| **1** | Driver App API (Q3) | API exists [A003, A053] | No API, requires 3-6 month build | **CRITICAL** - Blocks DE-3 |
| **2** | GPS Staleness (Q5) | <5% stale, 30-min threshold [A045] | >20% stale, >30 min old | **HIGH** - Economics degrade |
| **3** | Sandra's Rules (Q2) | Expertise codifiable [A006] | Intuition-based, not codifiable | **HIGH** - HITL increases |
| **4** | Route Complexity (Q8) | <10% dynamic changes [A004] | >30% mid-day route changes | **MEDIUM** - Build complexity |
| **5** | Trust Threshold (Q10) | 90% accuracy, 3-mo pilot [A042] | 99% accuracy, 6-mo shadow mode | **MEDIUM** - Timeline delay |

---

## Scenario 1: Driver App API Unavailable

### Discovery Question 3
**Question**: "Does the Driver App expose a REST API for real-time GPS location and delivery status?"

**Worst-Case Answer**: "No, the Driver App is a standalone mobile app with no backend API. GPS data is stored locally on driver phones and synced to the Dispatch Console nightly via batch export."

### Impact on DE-3 Suitability Scores

| Dimension | Baseline Score | Revised Score | Rationale |
|-----------|----------------|---------------|-----------|
| Input Structure | HIGH | MEDIUM | GPS data available, but only via batch (not real-time) |
| Decision Determinism | HIGH | HIGH | (No change - logic remains rule-based) |
| **Tool Coverage** | **HIGH** | **LOW** | **No API available - requires 3-6 month build to create API wrapper** |
| Context Complexity | MEDIUM | MEDIUM | (No change) |
| Exception Rate | MEDIUM | HIGH | Without real-time GPS, more cases become "GPS unavailable" exceptions |
| Latency Constraint | MEDIUM | MEDIUM | (No change - but can't meet 2-min response target without real-time data) |
| Risk/Compliance | HIGH | HIGH | (No change) |

**Archetype Change**: 
- **Baseline**: Fully Agentic (5+ HIGH, 0 LOW)
- **Revised**: **PROJECT BLOCKED** (Tool Coverage = LOW is a blocker)

### Impact on Economics

**Scenario 1A: Build API Wrapper (3-6 months)**
- Additional build cost: **£40K-£60K** (API development, driver app backend integration)
- Total build cost: £38K + £50K = **£88K**
- Payback period: £88K ÷ £53K/year = **20 months** (vs. 7 months baseline)
- **Wave 1 viability**: NO - payback exceeds 18-month threshold

**Scenario 1B: Use Batch GPS Data (nightly refresh)**
- Agent can only calculate ETAs for orders last updated <24 hours ago
- Customer inquiries require human follow-up if GPS data stale
- HITL rate: 10% → **60%** (most inquiries need human contact to driver)
- Net savings: £53K → **£8K/year** (marginal value, mostly automation of lookups)
- **Wave 1 viability**: NO - ROI too low

**Scenario 1C: Abandon DE-3, Prioritize Alternative**
- Move DE-4 (Unattended Address) or DA-1 (Additional Pickup) to Wave 1
- DE-3 deferred to Wave 2 or Wave 3 (after API built)

### Revised Prioritization

**If Driver App API unavailable**:
- **Wave 1 Pilot**: DE-4 (Unattended Address) - £16K/year savings, 11-month payback
- **Wave 1 Expansion**: DA-1 (Additional Pickup) - £14K/year savings, 18-month payback
- **Wave 2 Preparation**: Build Driver App API wrapper (6 months, £50K investment)
- **Wave 3 Deployment**: DE-3 (ETA Investigation) - now viable with API access

**Decision Rule**: Week 1 Go/No-Go on DE-3 depends entirely on Driver App API availability.

---

## Scenario 2: High GPS Staleness Rate

### Discovery Question 5
**Question**: "In the last 30 days, what percentage of active deliveries had GPS data that was >30 minutes stale?"

**Worst-Case Answer**: "22% of deliveries have GPS >30 min stale at any given time. Common causes: drivers disable app to save battery (10% of cases), rural connectivity dead zones (8%), device issues (4%)."

### Impact on DE-3 Suitability Scores

| Dimension | Baseline Score | Revised Score | Rationale |
|-----------|----------------|---------------|-----------|
| Input Structure | HIGH | MEDIUM | GPS data exists but unreliable for 22% of cases |
| Decision Determinism | HIGH | HIGH | (No change) |
| Tool Coverage | HIGH | MEDIUM | GPS API exists but data quality poor |
| Context Complexity | MEDIUM | MEDIUM | (No change) |
| **Exception Rate** | **MEDIUM** | **HIGH** | **22% of cases have stale GPS → auto-escalate** |
| Latency Constraint | MEDIUM | MEDIUM | (No change) |
| Risk/Compliance | HIGH | HIGH | (No change) |

**Archetype Change**: 
- **Baseline**: Fully Agentic (5+ HIGH, 0 LOW)
- **Revised**: **Agent-led + Oversight** (4 HIGH, 2 MEDIUM, 1 HIGH exception rate)

### Impact on Economics

**Revised HITL Rate**:
- Baseline: 10% escalations (stale GPS, SLA breach, lost consignment)
- Revised: **25% escalations** (22% stale GPS + 3% other triggers)

**Revised Cost Model**:
| Cost Component | Baseline | Revised | Change |
|----------------|----------|---------|--------|
| Agent token cost | £2,900/year | £2,900/year | (No change - agent still attempts ETA for all cases) |
| API costs (SMS/email) | £2,076/year | £1,555/year | -25% (fewer notifications sent if escalated) |
| HITL cost (25% vs 10%) | £8,157/year | £20,392/year | +£12,235 (25% × 140 cases × 12 min × £19/hour) |
| **Total agent cost** | **£28,354/year** | **£40,768/year** | **+£12,414** |
| **Net savings** | **£53,213/year** | **£40,799/year** | **-23%** |
| **Payback period** | **7 months** | **11 months** | **+4 months** |

**Wave 1 Viability**: YES - Still positive ROI, but degraded. Payback within 18 months.

### Mitigation Options

**Option A: Relax GPS Staleness Threshold**
- Change threshold from 30 min → 45 min or 60 min
- Rationale: Driver may be between stops (GPS updates on delivery scan, not continuous)
- Risk: Lower ETA accuracy (±30 min target → ±45 min reality)
- Impact: Reduces escalations from 22% to ~12% (split cases: truly stale vs. between-stops)

**Option B: Add Fallback ETA Logic**
- If GPS stale, use last known location + historical timing + "low confidence" flag
- Communicate wider ETA window to customer (±60 min instead of ±30 min)
- Impact: Reduces escalations from 25% to 15% (agent provides "best guess" ETA)

**Option C: Driver Engagement Initiative**
- Train drivers to keep app active (battery optimization tips, provide power banks)
- Add incentive for GPS uptime (driver performance KPI)
- Timeline: 3-6 months to see behavior change
- Impact: Reduces stale GPS from 22% to ~10% over time

**Recommendation**: Pilot with Option A (45-min threshold) + Option B (fallback logic). Launch Option C in parallel (Wave 2 prep).

---

## Scenario 3: Sandra's Tacit Knowledge Non-Codifiable

### Discovery Question 2
**Question**: "Walk me through the last 3 times Sandra overrode the Dispatch Console's ETA estimate. What data did she look at that the system doesn't capture?"

**Worst-Case Answer**: "Sandra uses a combination of verbal driver check-ins (drivers text her updates), personal knowledge of traffic patterns (she's driven these routes for 10 years), customer relationship history (she knows which customers are flexible vs. demanding), and weather conditions (snow, rain). She also relies on 'gut feel' for driver reliability ('Mark always runs 20 min late on Fridays'). None of this is documented."

### Impact on DE-3 Suitability Scores

| Dimension | Baseline Score | Revised Score | Rationale |
|-----------|----------------|---------------|-----------|
| Input Structure | HIGH | MEDIUM | Some inputs are unstructured (verbal check-ins, weather) |
| **Decision Determinism** | **HIGH** | **MEDIUM** | **"Gut feel" and personal relationships reduce codifiability** |
| Tool Coverage | HIGH | MEDIUM | Missing: driver behavior patterns, weather API, customer flexibility flags |
| **Context Complexity** | **MEDIUM** | **HIGH** | **Requires institutional knowledge (10 years of route experience)** |
| Exception Rate | MEDIUM | HIGH | More cases require judgment calls (customer flexibility, driver reliability) |
| Latency Constraint | MEDIUM | MEDIUM | (No change) |
| Risk/Compliance | HIGH | HIGH | (No change) |

**Archetype Change**: 
- **Baseline**: Fully Agentic (5+ HIGH, 0 LOW)
- **Revised**: **Agent-led + Oversight** (2 HIGH, 3 MEDIUM, 2 HIGH context/exception)

### Impact on Economics

**Revised HITL Rate**:
- Baseline: 10% escalations
- Revised: **30% escalations** (agent can't replicate Sandra's tacit knowledge, requires human judgment for edge cases)

**Revised Cost Model**:
| Cost Component | Baseline | Revised | Change |
|----------------|----------|---------|--------|
| Agent token cost | £2,900/year | £2,900/year | (No change) |
| API costs | £2,076/year | £1,453/year | -30% (fewer notifications if escalated) |
| HITL cost (30% vs 10%) | £8,157/year | £24,471/year | +£16,314 (30% × 140 cases × 12 min × £19/hour) |
| **Total agent cost** | **£28,354/year** | **£44,745/year** | **+£16,391** |
| **Net savings** | **£53,213/year** | **£36,822/year** | **-31%** |
| **Payback period** | **7 months** | **12 months** | **+5 months** |

**Wave 1 Viability**: MARGINAL - Still positive ROI, but lower priority. Payback within 18 months, but DE-4 or DA-1 may be better Wave 1 candidates.

### Mitigation Options

**Option A: Shadow Sandra for 3-6 Months (Wave 2 Prep)**
- Capture Sandra's decision-making process for 100+ cases
- Extract codifiable rules from patterns (e.g., "If driver is Mark + Friday + afternoon → add 20 min buffer")
- Build decision tree from shadowing data
- Timeline: 6 months to formalize rules, then deploy agent
- Impact: Reduces HITL from 30% to 15% with formalized rules

**Option B: Agent-in-the-Loop (Not Fully Autonomous)**
- Agent provides draft ETA, Sandra reviews/approves before sending to customer
- Agent automates data gathering (GPS lookup, route retrieval, historical timing), Sandra makes final call
- Impact: Saves 50% of Sandra's time (6 min/case → 3 min/case), not 85%
- Economics: £53K savings → £27K savings (still viable, but lower priority)

**Option C: Defer DE-3 to Wave 2, Prioritize Simpler JtDs**
- Move DE-4 (Unattended Address) or DA-1 (Additional Pickup) to Wave 1
- Use Wave 1 ROI to fund Wave 2 preparation (formalize Sandra's rules)
- Deploy DE-3 in Wave 3 after rules documented

**Recommendation**: If Sandra's knowledge is non-codifiable, implement **Option C** (defer to Wave 2 prep). Use Wave 1 to build platform assets (CRM API, monitoring), then tackle DE-3 in Wave 2 with formalized rules.

---

## Scenario 4: High Route Plan Volatility

### Discovery Question 8
**Question**: "What percentage of routes involve dynamic re-sequencing (mid-route adjustments based on traffic, priority changes, additional pickups)?"

**Worst-Case Answer**: "35% of routes change mid-day due to additional pickups (15% of routes), priority customer urgent requests (10%), traffic diversions (8%), driver swap (2%). The planned route in Dispatch Console is often stale by mid-afternoon."

### Impact on DE-3 Suitability Scores

| Dimension | Baseline Score | Revised Score | Rationale |
|-----------|----------------|---------------|-----------|
| **Input Structure** | **HIGH** | **MEDIUM** | **Route plans are unreliable (35% change mid-day)** |
| Decision Determinism | HIGH | MEDIUM | ETA calculation requires real-time re-routing logic, not static route plans |
| Tool Coverage | HIGH | MEDIUM | Missing: real-time route optimization engine |
| **Context Complexity** | **MEDIUM** | **HIGH** | **Must account for dynamic route changes, not just static plans** |
| Exception Rate | MEDIUM | MEDIUM | (No change - route volatility is predictable pattern, not exception) |
| Latency Constraint | MEDIUM | MEDIUM | (No change) |
| Risk/Compliance | HIGH | HIGH | (No change) |

**Archetype Change**: 
- **Baseline**: Fully Agentic (5+ HIGH, 0 LOW)
- **Revised**: **Agent-led + Oversight** (2 HIGH, 4 MEDIUM, 1 HIGH context)

### Impact on Economics

**Revised Build Cost**:
- Baseline ETA Engine: £10K (GPS + route sequence + historical timing)
- Revised ETA Engine: **£18K** (adds real-time route optimization, traffic API integration mandatory, confidence scoring for route volatility)
- Total build cost: £38K → **£46K** (+£8K)

**Revised Run Cost**:
- Must add Traffic API (no longer optional): +£256/year
- Higher token usage for re-routing logic: +£400/year

**Revised HITL Rate**:
- Baseline: 10% escalations
- Revised: **18% escalations** (35% route changes, but agent can handle some with fallback logic)

**Revised Cost Model**:
| Cost Component | Baseline | Revised | Change |
|----------------|----------|---------|--------|
| Build cost | £38K | £46K | +£8K |
| Agent token cost | £2,900/year | £3,300/year | +£400 (more complex routing) |
| API costs | £2,076/year | £2,332/year | +£256 (Traffic API mandatory) |
| HITL cost (18% vs 10%) | £8,157/year | £14,683/year | +£6,526 (18% escalations) |
| **Total annual cost** | **£28,354/year** | **£36,236/year** | **+£7,882** |
| **Net savings** | **£53,213/year** | **£45,331/year** | **-15%** |
| **Payback period** | **7 months** | **12 months** | **+5 months** |

**Wave 1 Viability**: YES - Still positive ROI, payback within 18 months. But lower priority than baseline.

### Mitigation Options

**Option A: Use GPS as Primary Signal (Ignore Route Plan)**
- Base ETA on GPS location → customer address (direct distance), not route sequence
- Fallback: If GPS fresh, calculate "crow flies" distance + historical avg speed → ETA
- Impact: Simplifies algorithm, avoids route volatility issue
- Accuracy trade-off: ±30 min target → ±45 min reality (route sequence ignored)

**Option B: Add Route Volatility Detection**
- Agent queries Dispatch Console for "last route update timestamp"
- If route updated <30 min ago → trust route plan
- If route stale >30 min ago → use GPS direct distance (Option A logic)
- Impact: Hybrid approach, best of both worlds

**Option C: Require Dispatch Console API (Real-Time Route Access)**
- Agent queries real-time route plan (not cached), gets current stop sequence
- Requires Dispatch Console API with real-time access [A004]
- If API unavailable → fallback to Option A

**Recommendation**: Pilot with **Option A** (GPS direct distance, ignore route plan). Add **Option B** (route volatility detection) in Month 2-3 if accuracy insufficient. **Option C** only if Dispatch Console API available.

---

## Scenario 5: Stakeholder Trust Threshold

### Discovery Question 10
**Question**: "What accuracy rate would Operations leadership require before allowing the agent to send customer-facing ETA updates without human approval? How long of a shadow mode period is needed?"

**Worst-Case Answer**: "Given our prior chatbot failure in 2024, the COO requires 99% accuracy (±15 min precision, not ±30 min) and 6-month shadow mode with weekly review meetings before autonomous deployment. The CEO is skeptical of AI after the RPA billing failure."

### Impact on DE-3 Suitability Scores

**No change to delegation suitability scores** (technical capability unchanged). Impact is on **deployment timeline and economics**.

### Impact on Economics

**Revised Accuracy Target**:
- Baseline: 95% accuracy (±30 min) [A042]
- Revised: **99% accuracy (±15 min)** 
- Feasibility: Requires Traffic API (mandatory, not optional), tighter confidence threshold (85% instead of 70%), more escalations

**Revised HITL Rate**:
- Baseline: 10% escalations (confidence <70%)
- Revised: **25% escalations** (confidence <85% to hit 99% accuracy on autonomous cases)

**Revised Timeline**:
| Phase | Baseline | Revised | Change |
|-------|----------|---------|--------|
| Build | Months 1-2 | Months 1-2 | (No change) |
| Shadow Mode | Month 3 (partial) | **Months 3-8 (6 months)** | **+5 months** |
| Autonomous Pilot | Month 3 | Month 9 | +6 months |
| Full Deployment | Month 4 | Month 10+ | +6 months |

**Revised ROI**:
- Build cost: £38K (no change)
- Time to first savings: Month 3 → **Month 9** (+6 months)
- **Payback period**: 7 months → **13 months** (+6 months)
- Year 1 ROI: 77% → **30%** (6 months of savings lost)

**Wave 1 Viability**: MARGINAL - Still positive ROI, but 13-month payback is borderline for Wave 1 (18-month threshold). Lower priority than DE-4 (11-month payback) or DA-1 (18-month payback).

### Mitigation Options

**Option A: Phased Autonomy Rollout**
- Months 3-4: Shadow mode (agent proposes, Sandra reviews 100% of cases)
- Months 5-6: Graduated autonomy (agent autonomous for high-confidence cases >90%, Sandra reviews <90%)
- Months 7-8: Full autonomy (agent autonomous for >85% confidence, escalate <85%)
- Impact: Reduces shadow mode from 6 months to 4 months, starts ROI in Month 5

**Option B: Low-Risk Customer Segment Pilot**
- Deploy autonomous agent for low-priority customers only (not high-value accounts)
- If error occurs, consequence is lower (no SLA penalties, less brand risk)
- Builds stakeholder trust incrementally (prove accuracy on 80% of volume before expanding)
- Impact: Starts ROI in Month 3 (for 80% of volume), expands to 100% in Month 6

**Option C: Economic Argument to Leadership**
- Present cost of 6-month shadow mode: £0 savings (agent runs, but Sandra reviews all cases → no time saved)
- Alternative: 3-month shadow mode + 3-month graduated autonomy = £26K savings in Year 1 vs. £13K with 6-month shadow
- Impact: Negotiates shadow mode from 6 months → 3 months if leadership sees economic trade-off

**Recommendation**: Propose **Option B** (low-risk segment pilot) + **Option A** (graduated autonomy). Demonstrate 95% accuracy on low-priority customers in Months 3-4, then expand to high-priority in Months 5-6. This addresses trust concerns while preserving economics.

---

## Combined Worst-Case Scenario

**If multiple discovery questions have unfavorable answers simultaneously:**

### Scenario: GPS Stale (22%) + Sandra's Tacit Knowledge + Route Volatility (35%)

**Cumulative Impact on Suitability Scores**:
| Dimension | Baseline | Scenario 2 | Scenario 3 | Scenario 4 | Combined |
|-----------|----------|------------|------------|------------|----------|
| Input Structure | HIGH | MEDIUM | MEDIUM | MEDIUM | **MEDIUM** |
| Decision Determinism | HIGH | HIGH | MEDIUM | MEDIUM | **MEDIUM** |
| Tool Coverage | HIGH | MEDIUM | MEDIUM | MEDIUM | **MEDIUM** |
| Context Complexity | MEDIUM | MEDIUM | HIGH | HIGH | **HIGH** |
| Exception Rate | MEDIUM | HIGH | HIGH | MEDIUM | **HIGH** |
| Latency Constraint | MEDIUM | MEDIUM | MEDIUM | MEDIUM | **MEDIUM** |
| Risk/Compliance | HIGH | HIGH | HIGH | HIGH | **HIGH** |

**Archetype Change**:
- **Baseline**: Fully Agentic (5 HIGH, 2 MEDIUM, 0 LOW)
- **Combined Worst-Case**: **Human-led + Agent Support** (1 HIGH, 5 MEDIUM, 1 HIGH exception)

**Economics**:
- HITL rate: 10% → **50%** (GPS staleness 22% + tacit knowledge 30% + route volatility 18% = overlapping escalations)
- Net savings: £53K/year → **-£5K/year** (NEGATIVE ROI)
- **Result**: DE-3 becomes a **Wave 2 Preparation** candidate, not Wave 1 deployment

**This matches the existing Wave 2 agents (DE-1, DE-2, DA-2)** that have negative economics due to high HITL rates.

---

## Revised Wave Sequencing

### If DE-3 Becomes Unviable (Scenarios 1, or Combined Worst-Case)

**New Wave 1 Pilot**: DE-4 (Unattended Address Agent)
- Delegation: Agent-led + Oversight
- Volume: 45 cases/day
- Net savings: £16K/year
- Payback: 11 months
- **Advantages**:
  - Does NOT depend on Driver App GPS API (uses delivery status only)
  - Does NOT depend on route plans (manages post-delivery, not mid-route)
  - Lower risk profile (re-delivery scheduling, not real-time ETA calculation)

**New Wave 1 Expansion**: DA-1 (Additional Pickup Request Agent)
- Delegation: Agent-led + Oversight
- Volume: 36 cases/day
- Net savings: £14K/year
- Payback: 18 months
- **Advantages**:
  - Uses CRM API + GPS API (already built for DE-4)
  - Reuses platform assets from DE-4 (notification automation, monitoring)

**Wave 2 Preparation** (Months 7-12):
- Formalize Sandra's decision rules (shadow 100 cases, extract patterns)
- Build Driver App API wrapper (if needed for Scenario 1)
- Collect 6 months of clean GPS data, tune staleness threshold
- Formalize route volatility handling (real-time optimization logic)

**Wave 3 Deployment** (Months 13-18):
- DE-3 (ETA Investigation) - now viable with formalized rules, better data
- DE-1 (Refused Delivery) - formalized refusal disposition logic
- DE-2 (Damaged Consignment) - formalized liability criteria

### Comparison: Baseline vs. Worst-Case Wave Sequencing

| Wave | Baseline Plan | Worst-Case Plan | Rationale |
|------|--------------|-----------------|-----------|
| **Wave 1 Pilot** | DE-3 (£53K, 7-mo) | DE-4 (£16K, 11-mo) | DE-4 doesn't depend on Driver App API, GPS reliability, or tacit knowledge |
| **Wave 1 Expansion** | DE-4 (£16K, 11-mo) | DA-1 (£14K, 18-mo) | Reuses Wave 1 assets, positive ROI |
| **Wave 2 Prep** | Formalize DE-1/DE-2/DA-2 rules | Build Driver App API, formalize Sandra's rules, tune GPS | Addresses blockers for DE-3 |
| **Wave 2 Deploy** | DA-1 (£14K, 18-mo) | (Preparation only, no deployment) | Negative economics until rules formalized |
| **Wave 3 Deploy** | DE-1/DE-2/DA-2 (6-12 mo prep first) | DE-3 (£53K, 7-mo), DE-1, DE-2 | DE-3 now viable with improved data and rules |

**Total Wave 1 Savings**:
- Baseline: £53K (DE-3) + £16K (DE-4) = **£69K/year** by Month 6
- Worst-Case: £16K (DE-4) + £14K (DA-1) = **£30K/year** by Month 6 (-57% reduction)

**Platform Compounding Impact**:
- Baseline Wave 1 builds 6 assets → 75% reuse in Waves 2-3
- Worst-Case Wave 1 builds 5 assets (no ETA Engine, no Historical Timing DB) → 60% reuse in Waves 2-3 (DE-3 requires more greenfield build in Wave 3)

---

## Contingency Recommendations

### Week 1 Discovery Decision Tree

```
Week 1: Validate Driver App API availability [Question 3]
├─ API Available?
│  ├─ YES → Validate GPS staleness rate [Question 5]
│  │  ├─ <10% stale → Validate Sandra's rules [Question 2]
│  │  │  ├─ Codifiable → **Proceed with DE-3 as Wave 1 pilot (baseline plan)**
│  │  │  └─ Non-codifiable → **Defer DE-3 to Wave 2 prep, pilot DE-4 in Wave 1**
│  │  └─ >20% stale → Validate route volatility [Question 8]
│  │     ├─ <20% volatile → **Proceed with DE-3, but expect 25% HITL (degraded economics)**
│  │     └─ >30% volatile → **Defer DE-3 to Wave 2 prep, pilot DE-4 in Wave 1**
│  └─ NO → **Immediate pivot: Build API wrapper (3-6 mo) OR pilot DE-4 in Wave 1**
└─ Decision Point: Go/No-Go on DE-3 by end of Week 1
```

### Recommended Week 1 Validation Sequence

**Day 1-2: Driver App API Discovery** (Question 3)
- Technical meeting with IT team: confirm API availability
- If NO API → Immediate escalation to Ops Manager for pivot decision
- If YES → proceed to Day 3-4

**Day 3-4: GPS & Data Quality Validation** (Questions 5, 9)
- Sample 30-day driver app logs: measure GPS staleness rate, data completeness
- If >20% stale GPS OR <80% log completeness → flag for mitigation planning
- If data quality acceptable → proceed to Day 5

**Day 5: Sandra Interview** (Question 2)
- Walk through 3-5 recent ETA override cases
- Attempt to extract codifiable rules vs. intuition-based decisions
- If majority codifiable → proceed with DE-3
- If majority intuition → recommend Wave 2 prep (defer deployment)

### Pivot Decision Framework

**Decision Matrix**: Should we proceed with DE-3 as Wave 1 pilot?

| Criteria | Threshold | Weight | Pass/Fail |
|----------|-----------|--------|-----------|
| Driver App API available | YES | **Mandatory** | Go/No-Go |
| GPS staleness rate | <15% | High | Proceed if pass, mitigate if 15-20%, defer if >20% |
| Sandra's rules codifiable | >70% codifiable | High | Proceed if pass, defer if <50% |
| Route plan volatility | <20% dynamic changes | Medium | Proceed if pass, mitigate if 20-30%, redesign if >30% |
| Stakeholder trust threshold | ≤95% accuracy, ≤4-mo shadow | Medium | Proceed if pass, negotiate if stricter |

**Go Decision**: If Driver App API available AND (GPS staleness <15% OR route volatility <20%) AND (Sandra's rules >70% codifiable OR stakeholder threshold acceptable)

**No-Go Decision**: If Driver App API unavailable OR (GPS staleness >20% AND Sandra's rules <50% codifiable) → Pivot to DE-4 as Wave 1 pilot

### Communication Plan for Pivot

**If Week 1 discovery requires pivot from DE-3 to DE-4:**

**To COO (Sarah Whitmore)**:
- "Week 1 discovery revealed [Driver App API gap / GPS data quality issues / Sandra's tacit knowledge complexity]. DE-3 (ETA Investigation) requires [6-month prep / API build / rule formalization] before deployment."
- "Recommendation: Pivot Wave 1 pilot to DE-4 (Unattended Address Agent). Lower risk, doesn't depend on GPS infrastructure, positive ROI (£16K/year, 11-month payback)."
- "Use Wave 1 to build platform assets (CRM API, monitoring), then deploy DE-3 in Wave 2 with improved data and formalized rules."
- "**No delay to overall program** - Wave 1 still starts Month 1, just with different agent. Total 3-wave ROI unchanged at £85K/year."

**To Engineering Team**:
- "Pivot to DE-4 build. Prioritize CRM API integration, notification automation, monitoring platform."
- "Defer ETA calculation engine, Driver App GPS API, Historical Timing DB to Wave 2 prep."
- "Parallel workstream: Build Driver App API wrapper (if needed) during Wave 1, ready for Wave 2 deployment."

---

## Document Control

- **Created**: 2026-05-06
- **Version**: 1.0
- **Purpose**: Risk scenario analysis for Week 1 discovery contingency planning
- **Owner**: AI FDE Team
- **Related Documents**:
  - `2-delegation-suitability-matrix.md` - Baseline suitability scores
  - `3-volume-x-value-analysis.md` - Baseline Wave sequencing
  - `4-agent-purpose-document.md` - DE-3 baseline specification
  - `6-discovery-questions.md` - Critical discovery questions
  - `assumptions.md` - All assumptions at risk
- **Usage**: Review before Week 1 discovery interviews; use decision tree to make Go/No-Go call on DE-3 by end of Week 1
