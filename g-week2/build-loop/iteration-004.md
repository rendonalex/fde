# Build Loop - Iteration 004

## Date
2026-05-06

## Goal
Complete Agent Mapping for DE-3 (ETA Investigation Agent), the Wave 1 pilot agent. Translate prioritized use case into fully specified agent design ready for development.

## Approach
1. Define agent purpose, objectives, KPIs, and delegation archetype
2. Enumerate all micro-tasks in agent activity catalog with delegation levels and tool requirements
3. Create autonomy matrix (decision authority levels and escalation triggers)
4. Design context engineering (memory architecture, retrieval strategy, prompt principles)
5. Map compounding roadmap showing Wave 1 platform assets reused in Waves 2-3
6. Document all system and data dependencies with integration effort, availability, and gaps
7. Track 21 new assumptions (A042-A062) discovered during agent specification

---

## Deliverables Completed

### 1. Agent Purpose Document (`specs/4-agent-purpose-document.md`)

**Agent Profile**:
- **Name**: ETA Investigation Agent (DE-3)
- **Job**: Investigate missed delivery windows, provide accurate ETAs to customers
- **Volume**: 140 cases/day
- **Delegation Archetype**: Fully Agentic (85-95% autonomous)
- **Annual Saving**: £53,213
- **Payback**: 7 months
- **Year 1 ROI**: 77%

**Why This Agent First**:
1. Highest absolute ROI (£53K/year) across all Wave 1 candidates
2. Fully Agentic archetype enables 85-95% autonomous operation
3. Lowest risk profile (wrong ETA easily corrected, no financial liability)
4. High customer satisfaction impact (reduces 4-hour ETA windows to 20-minute estimates)
5. Builds foundational platform assets (CRM API, GPS API, ETA engine) reused in Waves 2-3

#### Agent Purpose Section

**Cognitive Contract**: Customer receives accurate, timely ETA within 2 minutes of inquiry, with tighter precision than current "best guess" 4-hour windows.

**Primary Objectives**:
1. Provide accurate ETAs (95% within ±30 min of actual delivery [Ref: A042])
2. Reduce ETA window width (from 4-hour to 20-minute precision)
3. Autonomous coverage (85-95% cases without human escalation)
4. Response speed (2 minutes vs. current 5-10 minutes)
5. Customer satisfaction (90%+ satisfaction score [Ref: A043])

**KPIs Defined**:
- Accuracy: 95% target, 90% minimum
- Coverage: 90% target, 85% minimum
- Throughput: 140 cases/day (2 min/case avg)
- Cost per Case: £0.57 target, £0.75 maximum
- HITL Rate: 10% target, 15% maximum
- Customer Satisfaction: 90% target, 85% minimum
- Error Rate: <5% target, <8% maximum

**Failure Modes Identified**:
1. Incorrect ETA (customer misses delivery) → Recovery: callback, reschedule
2. Wrong delivery status (customer waits unnecessarily) → Recovery: human correction
3. Missed escalation (SLA breach not flagged) → Recovery: supervisor review
4. Communication failure (unclear phrasing) → Recovery: clarification call
5. System timeout (>60s response) → Recovery: escalate with context

**Escalation Triggers** (7 types):
1. GPS data stale (>30 min [Ref: A045])
2. Consignment status ambiguous (exception, lost)
3. SLA breach detected (past committed window)
4. High-priority customer + delay >1 hour [Ref: A009]
5. Low confidence ETA (<70% [Ref: A044])
6. Customer requests human agent
7. Driver unreachable (GPS stale >1 hour → dispatch welfare check)

#### Agent Activity Catalog Section

**12 Micro-Tasks Enumerated**:
- **T1-T2**: Reasoning (NLP intent classification, order extraction)
- **T3-T5, T7**: Retrieval (CRM order, delivery status, GPS location, historical timing)
- **T6, T9**: Decision (GPS freshness validation, SLA breach detection)
- **T8**: Reasoning (ETA calculation — core value-add task)
- **T10**: Generation (customer communication drafting)
- **T11-T12**: Action (send notification, log CRM)

**Risk Distribution**:
- Low risk: 7 tasks (standard operations, reversible)
- Medium risk: 4 tasks (GPS validation, ETA calculation, send notification)
- High risk: 1 task (SLA breach detection — compliance risk)

**All 12 tasks scored "Fully Agentic"** → Agent performs entire workflow autonomously for standard cases (90% volume). Escalation triggers handle edge cases (10%).

#### Autonomy Matrix Section

**Four Decision Authority Levels**:

1. **Agent Decides Alone** (No HITL):
   - Data retrieval (CRM, GPS, driver app, historical timing)
   - ETA calculation (GPS velocity + route sequence + historical patterns)
   - Customer communication (draft + send SMS/email)
   - Administrative actions (log CRM, update order notes)
   - **Threshold**: GPS fresh, status clear, confidence ≥70%, no SLA breach, standard-priority customer

2. **Agent Acts, Human Notified After**:
   - Failed delivery attempts (send re-delivery link, notify CS agent)
   - Minor delays <30 min (apologize, log for supervisor review)
   - Delivery already completed (confirm timestamp, offer assistance)
   - **Mechanism**: "Review Queue" dashboard + Slack notification

3. **Agent Proposes, Human Approves Before Action**:
   - SLA breach escalations (high-priority customers: draft ETA + goodwill offer → supervisor approves)
   - Ambiguous order identification (multiple matches → human selects)
   - Policy exceptions (ETA >2 hours beyond window → human approves action plan)
   - **Mechanism**: Approval dashboard, 5-minute timeout, avg 30 sec approval time [Ref: A047]

4. **Human Takes Over** (Agent Supports):
   - GPS/system issues (stale GPS, consignment lost, driver app offline)
   - Customer escalation requests (explicit request or dissatisfaction detected)
   - Complex re-delivery scenarios (special instructions, depot pickup, rescheduling)
   - Regulatory/compliance flags (regulated goods, sanctions list)
   - Low confidence ETA (<70% due to route timing variability [Ref: A044])
   - **Mechanism**: CRM escalation case + queue assignment + notification

#### Context Engineering Design Section

**Memory Architecture** (4 types):
1. **In-Context (Short-Term)**: Current inquiry details (1,500 input + 300 output tokens per inquiry)
2. **Episodic (Medium-Term)**: Customer inquiry history (200-500 tokens, retrieved if >1 inquiry in 30 days [Ref: A048])
3. **Semantic (Long-Term)**: Historical route timing, traffic patterns, SLA rules (400-800 tokens, cacheable [Ref: A030])
4. **Procedural (Static)**: Agent instructions, decision rules, guardrails (1,200-1,500 tokens system prompt)

**Token Optimization with Caching** [Ref: A030]:
- Route plans (400 tokens) + historical timing (400 tokens) = 800 tokens cached
- Cache hit rate: 80% (same routes queried multiple times/day)
- Token savings: 44,800 tokens/day = £369/year (18% cost reduction)

**Retrieval Strategy**:
- **Triggers**: Order extraction → CRM query, driver assignment → GPS query, route ID → historical timing query, customer history flag → CRM case query
- **Target**: Exact record retrieval (structured data, not vector search)
- **Quality**: Order ID 100% match, GPS timestamp <30 min for high confidence, completeness validation (all fields present)
- **Cost Management**: Caching (24-hour cache for route plans), no vector search (not needed for ETA calculation)

**Prompt Engineering Principles** (7 guidelines):
1. Role and purpose first (clear statement of agent job)
2. Explicit scope (what agent may/may not do)
3. Few-shot examples (2 representative cases: standard ETA, stale GPS escalation)
4. Guardrail instructions (GPS freshness >30 min → escalate, confidence <70% → escalate, etc.)
5. Structured output (JSON schema for downstream processing)
6. Chain of thought for ETA calculation (step-by-step reasoning: GPS freshness → driver progress → remaining time → ETA range)
7. Token discipline (1,200-token system prompt, concise instructions, caching)

#### Compounding Roadmap Section

**Wave 1 Platform Assets Built** (Reusable):
1. **CRM API Integration** (OAuth 2.0, order/contact/case endpoints) → Reused in DE-4, DA-1, DE-1, DE-2, DA-2
2. **Driver App GPS API** (location, delivery status, route sequence) → Reused in DA-1, DA-2
3. **ETA Calculation Engine** (GPS + historical timing + traffic buffer) → Reused in DA-1 (pickup timing), DA-2 (route impact)
4. **Historical Timing DB** (nightly ETL from driver app logs) → Reused in DA-1, DA-2
5. **SMS/Email Notification** (Twilio + SendGrid) → Reused in all customer-facing agents
6. **Agent Monitoring** (token usage, API calls, escalations, audit logs) → Reused across all agents (platform-level)

**Wave 2-3 Reuse Metrics**:
- DE-4: 79% reuse (inherits 4 of 6 Wave 1 assets)
- DA-1: 75% reuse (inherits 6 of 8 total assets)
- DE-1: 72% reuse (inherits 8 of 11 total assets)
- **Average reuse: 75%** → validates 40-50% marginal cost reduction estimate [Ref: A028]

**Integration Reuse Matrix**:
- CRM API: ✓ Build (Wave 1) → Reuse (all 5 future agents)
- GPS API: ✓ Build (Wave 1) → Reuse (DA-1, DA-2, DE-1, DE-2)
- ETA Engine: ✓ Build (Wave 1) → Reuse (DA-1, DA-2)
- Historical Timing DB: ✓ Build (Wave 1) → Reuse (DA-1, DA-2)
- SMS/Email: ✓ Build (Wave 1) → Reuse (all 5 future agents)
- Agent Monitoring: ✓ Build (Wave 1) → Reuse (all 5 future agents)

**Compounding Savings**: Building all 6 agents standalone = £232K. With compounding = £147K. **£85K saved (37% reduction)**.

### 2. System and Data Inventory (`specs/5-system-data-inventory.md`)

**Systems Required**: 4 primary, 2 supporting, 3 data sources, 2 external services

#### Primary Systems

**1. Salesforce CRM**:
- **Purpose**: Customer records, order details, case management
- **Access**: REST API (read/write), OAuth 2.0
- **Data Needed**: Orders (order_number, customer, delivery_address, committed_window, priority_tier [A009]), Contacts (email, SMS, communication_preference), Cases (inquiry logging, escalations)
- **Availability**: ✅ Available
- **Build Effort**: Medium (2 weeks: OAuth setup, SOQL queries, custom fields)
- **Rate Limits**: 100,000 calls/24h (Enterprise Edition [Ref: A052]), agent uses 420 calls/day (0.4% of limit)
- **Gaps**: Customer priority tier field may not exist [A009] → use revenue proxy or hard-code known accounts [A057]. SLA window fields may be missing [A056] → use default windows by tier.

**2. Driver App (iOS/Android)**:
- **Purpose**: GPS location, delivery status, route sequence
- **Access**: REST API (read-only, assumed [Ref: A003]), API key (assumed)
- **Data Needed**: Driver GPS (lat, lon, timestamp), Delivery status (out_for_delivery, delivered, failed_attempt, exception, lost), Routes (stop sequence)
- **Availability**: ⚠️ **Assumed Available** [A003] — **Critical blocker validation** required [Ref: A053]
- **Build Effort**: Medium (2 weeks: 3 days discovery, 1.5 weeks integration, 3 days testing)
- **Gaps**: **API availability unknown** → If no API, requires wrapper build (+2-3 weeks) or direct DB query. GPS freshness may be event-based (15-30 min gaps between stops) → tune "stale" threshold [A045].

**3. Dispatch Console (Java/Citrix)**:
- **Purpose**: Route planning (read-only context, no writes required for DE-3)
- **Access**: Limited API (read-only [Ref: A004]) or DB query
- **Data Needed**: Route plans (stops, sequence, timing)
- **Availability**: ⚠️ **Constrained** [A004] — May require API wrapper or DB query
- **Build Effort**: Low (1 week, read-only)
- **Gaps**: **Limited API** → Fallback: rely on driver app route data only (sufficient for 90%+ accuracy [A042])

**4. Historical Timing Database**:
- **Purpose**: Route timing patterns for ETA calculation
- **Access**: PostgreSQL DB (read-only for agent, nightly ETL writes)
- **Data Needed**: route_timings (avg_stop_duration by route, time_bucket, day_of_week)
- **Availability**: ❌ **Build Required** — New system (no existing historical timing at Apex)
- **Build Effort**: High (3 weeks: schema design, ETL pipeline, backfill 6-12 months logs [Ref: A054])
- **Gaps**: **Historical data completeness** [A054] → If driver app logs incomplete, historical timing sparse → ETA accuracy degraded. Fallback: default 15 min/stop [A055].

#### Supporting Systems

**5. SMS Gateway (Twilio)**:
- **Availability**: ✅ Available
- **Build Effort**: Low (1 week)
- **Cost**: £0.04/SMS × 140/day = £2,044/year [Ref: A058]
- **Gaps**: ~20% customers missing phone number [Ref: A059] → fallback to email or escalate

**6. Email Service (SendGrid)**:
- **Availability**: ✅ Available
- **Build Effort**: Low (1 week)
- **Cost**: £0.001/email × 32,200/year = £32/year [Ref: A060]
- **Gaps**: ~10% email bounce rate [Ref: A061] → log and escalate

**7. Traffic API (Google Maps)** — Optional Wave 1:
- **Availability**: ✅ Available
- **Build Effort**: Low (1 week)
- **Cost**: £0.005/request × 140/day = £256/year [Ref: A062]
- **Decision**: Optional Wave 1 (pilot without traffic, add if accuracy <90%)

**8. Agent Monitoring Platform**:
- **Availability**: ❌ Build Required
- **Build Effort**: Medium (2 weeks: token tracker, API logger, escalation dashboard, audit trail, KPIs)
- **Reusability**: ✅ High — Shared across all Wave 2-3 agents

#### Integration Summary

**Total Build Effort**: 12-14 weeks (parallelizable: CRM + Driver App + SMS/Email concurrent)

**Critical Path Blockers** (Must Resolve Before Pilot):
1. **Driver App API Availability** [A003, A053] — **HIGH RISK** → Week 1 discovery to confirm API or plan wrapper build
2. **Historical Timing Data Completeness** [A054] — **MEDIUM RISK** → Validate driver app log quality, use fallback if needed

**Medium Priority Gaps**:
3. Customer Priority Tier Field [A009, A057] — Use revenue proxy or hard-code for pilot
4. SLA Committed Window Fields [A056] — Use default windows by tier
5. Customer Contact Data Completeness [A059, A061] — Agent handles missing data gracefully

**Data Quality Assessment**:
- CRM Orders: High (addresses may vary)
- CRM Contacts: Medium-High (~20% missing phone, ~10% invalid email)
- Driver App GPS: Medium (accuracy depends on signal, rural areas may have poor coverage)
- Historical Timing: Medium (depends on log completeness)

### 3. Assumptions Register Update (`specs/assumptions.md`)

**21 New Assumptions Added** (A042-A062):

**Agent Design Assumptions**:
- A042: ETA accuracy target (95% within ±30 min)
- A043: Customer satisfaction target (90%+ score)
- A044: ETA confidence threshold (70% for autonomous action)
- A045: GPS staleness threshold (30 min)
- A046: Order number provision rate (80% customers provide explicitly)
- A047: Human approval time (30 seconds per case)
- A048: Customer inquiry history threshold (3 inquiries in 30 days → escalate)

**System Integration Assumptions**:
- A049: Salesforce API base URL (low confidence — confirm with IT)
- A050: Customer inquiry history count field (custom field may be needed)
- A051: Agent actions JSON field (custom field required for audit trail)
- A052: Salesforce API rate limits (100K calls/day Enterprise Edition)
- A053: Driver app API base URL (low confidence — **critical blocker validation**)
- A054: Historical timing data completeness (medium confidence — validate log quality)
- A055: Default timing fallback (15 min/stop for sparse data routes)

**Data Quality Assumptions**:
- A056: SLA committed window fields (may not exist in CRM → use defaults)
- A057: Hard-coded high-priority accounts (fallback for priority tier [A009])
- A059: Customer phone number completeness (~20% missing)
- A061: Customer email bounce rate (~10% invalid)

**Cost Assumptions**:
- A058: Twilio SMS pricing (£0.04/SMS, £2,044/year)
- A060: SendGrid email pricing (£0.001/email, £32/year)
- A062: Google Maps Traffic API pricing (£0.005/request, £256/year optional)

**Total Assumptions**: 62 (13 High, 32 Medium, 7 Low confidence)

---

## Key Findings from Agent Mapping

### Agent Specification Completeness

**All 6 Required Deliverables Completed**:
1. ✅ Agent Purpose Document (name, JtD, objectives, KPIs, failure modes, delegation archetype, escalation triggers)
2. ✅ Agent Activity Catalog (12 micro-tasks with type, delegation level, data/tool requirements, risk level)
3. ✅ Autonomy Matrix (4 decision authority levels: agent alone, notify after, approve before, human takes over)
4. ✅ System and Data Inventory (8 systems, integration effort, availability, gaps/risks)
5. ✅ Context Engineering Design (4 memory types, retrieval strategy, 7 prompt principles, token optimization)
6. ✅ Compounding Roadmap (Wave 1 platform assets → 75% avg reuse in Waves 2-3 → £85K savings)

**Agent is Production-Ready Specification** → Development team can begin build sprint with complete design (no scope creep, all integrations identified, governance requirements defined).

### Agent Design Strengths

1. **Fully Agentic Archetype Validated**: All 12 micro-tasks scored as agent-autonomous for standard cases (90% volume). Only 10% escalations (edge cases: stale GPS, SLA breach, low confidence) → achieves 85-95% coverage target.

2. **Token Optimization Designed**: Prompt caching strategy [A030] reduces token costs by 18% (£369/year savings). Total agent cost per case: £0.57 (within £0.75 target).

3. **Clear Escalation Logic**: 7 escalation triggers defined with explicit thresholds (GPS >30 min, confidence <70%, SLA breach). Human agents receive full context (order, GPS, ETA calculation attempt, reasoning) → efficient handoff.

4. **Platform Compounding Thesis Confirmed**: 6 Wave 1 assets (CRM, GPS, ETA engine, historical timing, notification, monitoring) reused across 5 future agents → 75% avg reuse → £85K marginal cost reduction (37%) vs. standalone builds [A028].

5. **Governance Built-In**: Audit trail logging (agent actions JSON in CRM [A051]), confidence scoring (ETA calculation transparency), HITL supervision (approval dashboard for SLA breaches), GDPR compliance (data minimization, 90-day retention).

### Critical Blockers Identified

**Two Critical Path Blockers Require Week 1 Validation**:

1. **Driver App API Availability** [A003, A053]
   - **Risk**: **HIGH** — If API does not exist, agent cannot retrieve GPS/delivery status → cannot calculate ETAs (core function blocked)
   - **Mitigation**: Week 1 IT discovery to confirm API. If unavailable:
     - Option 1: Build API wrapper (+2-3 weeks to build effort)
     - Option 2: Direct DB query (if permissions granted)
     - **Decision Point**: Go/No-Go on pilot at end of Week 1 if API blocked

2. **Historical Timing Data Completeness** [A054]
   - **Risk**: **MEDIUM** — If driver app logs are incomplete (<50% have timestamps), historical timing patterns will be sparse → ETA accuracy degraded (85-90% vs. 95% target [A042])
   - **Mitigation**: Week 1 discovery to validate log quality (query 1 month sample). If incomplete:
     - Option 1: Use default timing assumptions (15 min/stop [A055]) for pilot, collect 3-6 months post-pilot data, then retrain ETA engine
     - Option 2: Proceed with sparse data, flag "low confidence" ETAs, accept higher escalation rate (15% vs. 10% target)

**Recommendation**: Prioritize Week 1 discovery on these two blockers. If both validate (API accessible, logs complete), pilot is green-lit. If one or both block, add 2-4 weeks to build timeline or adjust agent scope (e.g., pilot with default timing assumptions, accept lower accuracy in Month 1-2).

### Medium-Priority Data Gaps

**Four Medium-Priority Gaps (Address in Build Phase, Not Blocking)**:

3. **Customer Priority Tier Field** [A009, A057]
   - **Risk**: MEDIUM — Affects SLA breach escalation prioritization (high-priority customers should escalate to supervisor)
   - **Mitigation**: Wave 1 pilot uses revenue proxy (>£500K = high-priority) or hard-codes known accounts (Hayes & Sons, Northstar Foods, etc.). Wave 2 prep formalizes priority system.

4. **SLA Committed Window Fields** [A056]
   - **Risk**: MEDIUM — Affects SLA breach detection accuracy
   - **Mitigation**: Use default windows by customer tier (high-priority = 2-hour, standard = 4-hour). Wave 2 prep migrates SLA data from contracts into CRM.

5. **Customer Contact Data Completeness** [A059, A061]
   - **Risk**: LOW — ~20% missing phone, ~10% invalid email
   - **Mitigation**: Agent detects missing contact → requests from customer or escalates to human. Post-pilot CRM cleanup initiative.

6. **Traffic API Integration** [A062]
   - **Risk**: LOW — ETA accuracy may be 90-93% without traffic vs. 95% target
   - **Mitigation**: Pilot without traffic API (saves £256/year). Add in Month 2-3 if accuracy falls below 90%.

### Platform Value Validation

**Compounding Strategy Confirmed**:
- Wave 1 builds 6 reusable assets (CRM, GPS, ETA, timing, notification, monitoring)
- Wave 2-3 inherits assets → 75% avg reuse across 5 future agents
- **Marginal cost reduction**: £85K (37%) vs. building all agents standalone
- **3-year platform ROI**: If all waves deploy = 35% ROI. If pivot to high-ROI work streams = 237% ROI [A040, A041].

**Strategic Insight**: Platform value is in **reusability across work streams**, not in completing original 7 JtDs. After Wave 1 pilot, assess whether Wave 2-3 original candidates (DE-1, DE-2, DA-2) or alternative work streams (ETA inquiries 400/day full automation, billing disputes 60/day) deliver better ROI using Wave 1 platform.

---

## Build Quality Notes

### Strengths

- **Complete agent specification**: All 6 deliverables (purpose, activity catalog, autonomy matrix, system inventory, context engineering, compounding roadmap) with full detail
- **21 new assumptions tracked**: All unknowns explicitly documented with confidence levels, rationale, validation needs
- **Explicit escalation logic**: 7 triggers with thresholds, 4 decision authority levels, clear human handoff protocols
- **Token optimization**: Caching strategy designed (18% cost reduction [A030]), prompt engineering principles defined
- **Platform compounding**: Integration reuse matrix shows 75% avg reuse → validates marginal cost reduction thesis [A028]
- **Governance built-in**: Audit trail, confidence scoring, HITL supervision, GDPR compliance

### Critical Blockers Highlighted

- **Driver app API availability** [A003, A053]: **HIGH RISK** — Week 1 validation required, Go/No-Go decision point
- **Historical timing data completeness** [A054]: **MEDIUM RISK** — Week 1 validation, fallback plan if logs incomplete

### Next Steps (Week 1 Discovery Phase)

**Priority 1 (Critical Path)**:
1. **Driver app API validation** [A053]:
   - Confirm API exists and is accessible
   - Obtain API documentation (endpoints, auth method, rate limits)
   - Test sample API calls (GPS location, delivery status, route sequence)
   - If API unavailable: Assess DB query permissions or plan API wrapper build
   - **Decision**: Go/No-Go on pilot by end of Week 1

2. **Historical timing data validation** [A054]:
   - Query driver app DB for 1-month sample of delivery logs
   - Assess timestamp completeness (% of logs with arrival/departure/delivery times)
   - Calculate sample historical timing patterns (avg stop duration by route)
   - If logs incomplete: Decide default timing assumption strategy [A055]

**Priority 2 (Build Phase)**:
3. CRM schema validation: Confirm priority tier [A009, A057], SLA window [A056], custom fields [A050, A051]
4. Salesforce API confirmation: Base URL [A049], rate limits [A052], authentication setup
5. SMS/email integration: Twilio account setup [A058], SendGrid account [A060]
6. Agent monitoring build: Token tracker, API logger, escalation dashboard, audit trail (2 weeks)

**Priority 3 (Optional Wave 1)**:
7. Traffic API integration [A062]: Deferred to Month 2-3 based on pilot ETA accuracy results

---

## Next Phase

**Build Sprint Planning** (Months 1-3):
- **Month 1**: Discovery + Foundation (Week 1 validation, CRM integration, GPS API, historical timing DB build)
- **Month 2**: Agent Development + Testing (ETA calculation engine, prompt engineering, autonomy logic, shadow mode)
- **Month 3**: Pilot Deployment + Monitoring (production rollout, KPI measurement, iteration based on feedback)

**Success Criteria for Pilot**:
- 85%+ autonomous coverage (10-15% escalation rate)
- 95% ETA accuracy (±30 min of actual delivery [A042])
- 90%+ customer satisfaction score [A043]
- <5% error rate (wrong status, incorrect ETA)
- £0.57 cost per case (within £0.75 target)

**Measurement Plan**:
- Week 2-4 shadow mode (agent generates ETA, human validates before sending)
- Week 5-8 pilot production (agent autonomous, 10% random sample human review)
- Week 9-12 full production (agent autonomous, escalation-only human involvement)

---

## Document Control
- **Created**: 2026-05-06
- **Phase**: Agent Mapping (DE-3 ETA Investigation Agent)
- **Related Documents**:
  - `specs/1-cognitive-load-map.md` - Source JtD (DE-3) and micro-tasks
  - `specs/2-delegation-suitability-matrix.md` - Archetype (Fully Agentic)
  - `specs/3-volume-x-value-analysis.md` - Prioritization (Rank #1, Wave 1 pilot)
  - `specs/4-agent-purpose-document.md` - Main deliverable (purpose, catalog, autonomy, context, compounding)
  - `specs/5-system-data-inventory.md` - System integration specifications
  - `specs/assumptions.md` - A042-A062 added
  - `build-loop/iteration-001.md` - Phase 2 (Cognitive Load Mapping)
  - `build-loop/iteration-002.md` - Phase 3 (Delegation Qualification)
  - `build-loop/iteration-003.md` - Phase 4 (Candidate Prioritization)
