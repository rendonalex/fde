# Delegation Suitability Matrix: Apex Distribution Customer Operations

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Methodology](#methodology)
3. [Delegation Suitability Matrix](#delegation-suitability-matrix)
   - [Dispatch Adjustments](#dispatch-adjustments)
   - [Delivery Exceptions](#delivery-exceptions)
4. [Archetype Assignment Rationale](#archetype-assignment-rationale)
5. [Trade-Off Analysis](#trade-off-analysis)
6. [Implementation Sequencing Recommendations](#implementation-sequencing-recommendations)

---

## Executive Summary

This delegation qualification analysis evaluates **Dispatch Adjustments** (~90/day, 18 min avg) and **Delivery Exceptions** (~180/day, 12 min avg) for agentic transformation at Apex Distribution.

### Key Findings

**Dispatch Adjustments**: **Human-led + Agent Support** archetype dominates. Real-time route optimization and driver messaging can be agent-assisted, but final dispatch decisions—especially driver swaps and complex diversions—require human judgment due to safety, driver welfare, and customer relationship factors.

**Delivery Exceptions**: **Mixed archetype by sub-type**. Standard refused deliveries (60% of volume) and damage reports (25% of volume) can be **Agent-led + Human Oversight**. Complex multi-party disputes (10%) and high-value escalations (5%) remain **Human-led + Agent Support**.

### Critical Constraints

1. **Dispatch console API**: Limited/no write access blocks autonomous route updates → HITL required for execution
2. **Aurum billing lag**: 24-48h batch delay prevents real-time credit validation → agents work with stale data
3. **Decision rule gaps**: Refused delivery disposition, customer tier logic, damage liability assessment not codified → requires structured elicitation before agent build
4. **Driver interaction preference**: Voice calls preferred over app messaging for complex negotiations → limits full automation

### Delegation Potential

- **Dispatch Adjustments**: 35-50% cognitive work elimination (contingent on dispatch console API and decision rule formalization)
- **Delivery Exceptions**: 40-60% cognitive work elimination (higher volume, better system access, more rule-based sub-tasks)

**Conservative estimate**: 2.4 FTE equivalent savings (~£84K annual labour cost reduction)  
**Best case estimate**: 3.4 FTE equivalent savings (~£120K annual labour cost reduction)

### Recommended Phasing

**Phase 1** (3-6 months): Agent-led on CRM-centric Delivery Exception tasks (case logging, customer communication, data retrieval, standard disposition recommendations). Human-led on dispatch console and billing tasks.

**Phase 2** (6-12 months): Dispatch Adjustments with agent-driven route impact analysis and driver messaging. Build dispatch console API wrapper or separate route optimization service.

**Phase 3** (12-18 months): Billing integration via real-time credit workflow outside Aurum with batch reconciliation.

---

## Methodology

This analysis follows **Phase 3: Delegation Qualification** from the ATX Assessment Reference, scoring each Job to be Done (JtD) and micro-task on seven suitability dimensions:

1. **Input Structure**: Structured → Semi-structured → Unstructured
2. **Decision Determinism**: Clear rules → Judgment-dependent → Contextual/implicit
3. **Tool Coverage**: APIs available → Buildable → Inaccessible/black-box
4. **Context Complexity**: State explicit → Institutional knowledge required
5. **Exception Rate**: Rare/predictable → Frequent/unpredictable
6. **Latency Constraint**: Batch/async acceptable → Real-time required
7. **Risk/Compliance**: Reversible/low consequence → Irreversible/regulated/high-consequence

**Scoring**: High (H), Medium (M), Low (L) suitability for delegation.

**Archetype Assignment Logic**:
- **Human Only**: ≥3 dimensions at Low suitability, especially risk/compliance and decision determinism
- **Human-led + Automation Support**: Deterministic sub-tasks automated; judgment stays human
- **Human-led + Agent Support**: Agent provides synthesis, research, recommendations; human decides
- **Agent-led + Human Oversight**: Agent acts autonomously; human reviews or approves high-stakes outputs
- **Fully Agentic**: All dimensions at Medium or High; volume justifies full delegation

**Anti-pattern check**: If a task could be solved with static rules, RPA, or a simple script → do not build an agent.

---

## Delegation Suitability Matrix

### Dispatch Adjustments

#### JtD-DA-1: Process Additional Pickup Request

| Micro-Task | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency | Risk | **Suitability** | **Archetype** |
|------------|----------------|---------------------|---------------|-------------------|---------------|---------|------|----------------|--------------|
| **DA-1.1**: Validate pickup request details | Semi-structured (phone/email) | M (validation rules exist but may need clarification) | H (CRM API) | L (explicit fields) | M (15% require callback) | H (real-time) | L (reversible) | **Medium** | Agent-led + Human Oversight |
| **DA-1.2**: Identify candidate drivers with route proximity | Structured (GPS data) | H (rule-based: distance + capacity) | M (driver app read-only API) | L (GPS data available) | L (data usually available) | H (seconds) | L | **High** | Fully Agentic |
| **DA-1.3**: Calculate route impact and time feasibility | Structured (route data) | M (requires route optimization logic) | L (dispatch console limited API) | M (traffic, driver pace unpredictable) | M | H | M (affects SLAs) | **Low-Medium** | Human-led + Agent Support |
| **DA-1.4**: Assess vehicle capacity for additional load | Structured (vehicle manifest) | H (weight/volume calculation) | M (driver app partial data) | L | L | M | M (overload = safety) | **High** | Fully Agentic |
| **DA-1.5**: Select optimal driver and confirm acceptance | Semi-structured (driver response) | L (requires judgment on driver capability, fatigue, relationship) | M (messaging via app, but calls common) | H (driver relationships, tacit knowledge) | H (driver may refuse/negotiate) | H | H (driver welfare, hours compliance) | **Low** | Human Only |
| **DA-1.6**: Update route in dispatch console | Structured (system input) | H (data entry) | L (manual entry via Citrix) | L | L | M | M (audit trail required) | **Medium** | Human-led + Automation Support |
| **DA-1.7**: Notify driver via app with new pickup instructions | Structured (message template) | H (standard notification) | H (driver app messaging API) | L | L | H | L | **High** | Fully Agentic |
| **DA-1.8**: Update affected customer ETAs in CRM | Structured (ETA data) | M (ETA calculation may be manual) | H (CRM API) | M (customer priority handling) | M (high-value customers need calls) | M | M (customer expectation management) | **Medium** | Agent-led + Human Oversight |

**JtD-DA-1 Overall Archetype**: **Human-led + Agent Support**

**Rationale**: Driver selection (DA-1.5) is the critical bottleneck—requires tacit knowledge of driver capability, willingness, and relationship history. Route impact calculation (DA-1.3) is constrained by dispatch console API limitations. Agent can handle validation (DA-1.1), candidate identification (DA-1.2), capacity checks (DA-1.4), and notifications (DA-1.7, DA-1.8) autonomously, but human must make final driver selection and route approval.

---

#### JtD-DA-2: Execute Route Diversion

| Micro-Task | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency | Risk | **Suitability** | **Archetype** |
|------------|----------------|---------------------|---------------|-------------------|---------------|---------|------|----------------|--------------|
| **DA-2.1**: Receive and validate diversion request | Semi-structured (customer call/email) | M | H (CRM) | M (may need clarification) | M | H | L | **Medium** | Agent-led + Human Oversight |
| **DA-2.2**: Assess impact on remaining route deliveries | Structured (route data) | M (requires judgment on delay tolerance) | L (manual route analysis) | M (customer priority levels vary) | M | H | H (SLA breach risk) | **Low-Medium** | Human-led + Agent Support |
| **DA-2.3**: Confirm driver awareness of new location | Semi-structured (driver response) | H | M (driver app messaging) | M (driver may be unfamiliar with area) | M | H | M (wrong address = failed delivery) | **Medium** | Agent-led + Human Oversight |
| **DA-2.4**: Execute route update in dispatch console | Structured | H | L (manual) | L | L | M | M | **Medium** | Human-led + Automation Support |
| **DA-2.5**: Trigger ETA notifications to affected customers | Structured | M (may need custom messaging for priority customers) | H (CRM automation) | M (high-value customers may call) | M | M | M | **Medium** | Agent-led + Human Oversight |

**JtD-DA-2 Overall Archetype**: **Human-led + Agent Support**

**Rationale**: Route impact assessment (DA-2.2) requires judgment on customer priority and SLA tolerance—not fully codified. Dispatch console write access (DA-2.4) is manual. Agent can validate requests (DA-2.1), confirm driver awareness (DA-2.3), and send notifications (DA-2.5), but human must approve route changes due to SLA risk and system constraints.

---

#### JtD-DA-3: Manage Driver Swap

| Micro-Task | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency | Risk | **Suitability** | **Archetype** |
|------------|----------------|---------------------|---------------|-------------------|---------------|---------|------|----------------|--------------|
| **DA-3.1**: Receive driver unavailability report | Semi-structured (call/message) | H | M | M (details may be incomplete) | M | H | H (time-critical) | **Medium** | Agent-led + Human Oversight |
| **DA-3.2**: Identify available replacement drivers | Structured (workforce system) | M (requires judgment on driver qualifications, hours, location) | M (workforce system API may not exist) | H (driver capability, willingness, location) | H (limited pool, especially short notice) | H | H (hours compliance, safety) | **Low** | Human-led + Agent Support |
| **DA-3.3**: Determine optimal handoff location and time | Structured (GPS, route data) | L (judgment-heavy: driver convenience, customer impact, security) | L (manual judgment) | H (safety, cargo security, driver convenience) | M | H | H (handoff location safety, cargo security) | **Low** | Human Only |
| **DA-3.4**: Negotiate with drivers on handoff logistics | Unstructured (driver conversation) | L (relationship-dependent, requires persuasion) | L (phone calls) | H (driver relationships, union rules) | H (drivers may resist due to fatigue, location) | H | H (driver welfare, union rules) | **Low** | Human Only |
| **DA-3.5**: Authorize overtime or contractor call-out if needed | Semi-structured (workforce system + approval) | L (cost vs. SLA tradeoff, requires manager judgment) | M (approval workflow may be manual) | M (budget constraints) | M | M | H (budget, compliance) | **Low** | Human Only |
| **DA-3.6**: Update both driver routes and communicate handoff | Structured | M | L (manual dispatch console update) | M | M | H | M | **Medium** | Human-led + Automation Support |
| **DA-3.7**: Document incident and log shift adjustments | Structured | H | M (CRM/incident system) | L | L | L | H (audit, compliance) | **High** | Fully Agentic |

**JtD-DA-3 Overall Archetype**: **Human Only** (with automation support for documentation)

**Rationale**: Driver swaps are the highest-complexity, highest-risk dispatch adjustment. Replacement driver identification (DA-3.2) requires tacit knowledge of driver capability and willingness. Handoff location determination (DA-3.3) and negotiation (DA-3.4) require human judgment on safety, driver welfare, and relationship management. Overtime authorization (DA-3.5) requires manager-level cost/SLA tradeoff decisions. Agent can handle incident logging (DA-3.7) and assist with route updates (DA-3.6), but core decision-making must remain human.

---

### Delivery Exceptions

#### JtD-DE-1: Resolve Refused Delivery

| Micro-Task | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency | Risk | **Suitability** | **Archetype** |
|------------|----------------|---------------------|---------------|-------------------|---------------|---------|------|----------------|--------------|
| **DE-1.1**: Receive refused delivery report from driver | Semi-structured (driver call/app message) | H | M (driver app API) | M (driver may omit key details) | M | H | L | **Medium** | Agent-led + Human Oversight |
| **DE-1.2**: Classify refusal reason | Unstructured (driver narrative, customer claim) | M (requires interpretation) | L (manual classification) | H (conflicting accounts common) | H | M | M (affects downstream process) | **Low-Medium** | Human-led + Agent Support |
| **DE-1.3**: Retrieve customer account and delivery history | Structured (CRM lookup) | H | H (CRM API) | L | L | M | L | **High** | Fully Agentic |
| **DE-1.4**: Determine if high-value escalation threshold met | Structured (consignment value) | H (>£500 rule) | M (consignment data may be in multiple systems) | L | L | M | H (manager oversight required) | **High** | Fully Agentic |
| **DE-1.5**: Assess driver route impact | Structured (GPS, route plan) | M | L (dispatch console) | M | M | H | M (affects other deliveries) | **Medium** | Human-led + Agent Support |
| **DE-1.6**: Decide disposition (return, hold, re-attempt) | Semi-structured | L (judgment-dependent: customer priority, refusal reason, driver capacity) | L (human judgment) | H (customer priority not codified) | H (edge cases frequent) | H | H (wrong decision = escalation or loss) | **Low** | Human-led + Agent Support |
| **DE-1.7**: Communicate decision to driver via app | Structured (instruction message) | H | H (driver app messaging) | L | L | H | M | **High** | Fully Agentic |
| **DE-1.8**: Create case in CRM and log refusal details | Structured (form entry) | H | H (CRM API) | L | L | L | M (audit trail) | **High** | Fully Agentic |
| **DE-1.9**: Initiate customer follow-up | Semi-structured (customer communication) | M | H (CRM email/call integration) | M (customer may be upset) | M | M | M (reputation risk) | **Medium** | Agent-led + Human Oversight |
| **DE-1.10**: Coordinate billing adjustment if applicable | Semi-structured (credit request) | M (credit policy may be ambiguous) | L (Aurum batch only) | M | M | L (24-48h batch window) | H (audit, compliance) | **Low-Medium** | Human-led + Agent Support |

**JtD-DE-1 Overall Archetype**: **Agent-led + Human Oversight** (for standard refusals), **Human-led + Agent Support** (for complex/high-value)

**Rationale**: 60% of refused deliveries follow predictable patterns (damaged goods with clear evidence, incorrect consignment with proof, administrative errors). Agent can handle data retrieval (DE-1.3), escalation threshold checks (DE-1.4), driver messaging (DE-1.7), case logging (DE-1.8), and standard customer communication (DE-1.9) autonomously. Refusal classification (DE-1.2) and disposition decision (DE-1.6) require human judgment when conflicting accounts or customer priority considerations arise. Billing coordination (DE-1.10) is constrained by Aurum batch lag.

**Delegation split**:
- **Standard refusals** (60%): Agent-led + Human Oversight (agent recommends disposition based on decision tree, human approves before execution)
- **Complex refusals** (40%): Human-led + Agent Support (agent gathers data and presents options, human decides)

---

#### JtD-DE-2: Handle Damaged Consignment Report

| Micro-Task | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency | Risk | **Suitability** | **Archetype** |
|------------|----------------|---------------------|---------------|-------------------|---------------|---------|------|----------------|--------------|
| **DE-2.1**: Receive damage report | Semi-structured (report + photos) | H | M (driver app photo upload) | M (photos may be poor quality) | M | M | L | **Medium** | Agent-led + Human Oversight |
| **DE-2.2**: Assess damage severity and liability | Unstructured (visual assessment, narrative) | L (requires judgment: transit vs. packaging fault) | L (manual assessment) | H (frequent ambiguity) | H | M | H (financial liability, insurance) | **Low** | Human-led + Agent Support |
| **DE-2.3**: Retrieve consignment and sender details | Structured | H | M (CRM, dispatch system) | L | L | M | L | **High** | Fully Agentic |
| **DE-2.4**: Determine credit amount | Semi-structured | L (policy exists but judgment-heavy) | L (manual) | M (supervisor approval for high amounts) | M | M | H (financial impact, customer satisfaction) | **Low** | Human-led + Agent Support |
| **DE-2.5**: Check for recurring damage patterns | Structured (historical data) | M | M (CRM analytics, but may be manual) | M (data may be fragmented) | M | L | M (quality improvement opportunity) | **Medium** | Agent-led + Human Oversight |
| **DE-2.6**: Initiate credit in Aurum billing system | Structured (credit entry) | H | L (batch export, manual ticket) | M (Aurum ticket required for non-standard) | M | L (batch process) | H (audit, compliance) | **Low-Medium** | Human-led + Automation Support |
| **DE-2.7**: Communicate resolution to customer | Semi-structured | M | H (CRM) | M | M | M | M | **Medium** | Agent-led + Human Oversight |
| **DE-2.8**: Coordinate return logistics if needed | Structured | M | L (dispatch console) | M (driver availability) | M | M | M (cost of return) | **Medium** | Human-led + Agent Support |

**JtD-DE-2 Overall Archetype**: **Human-led + Agent Support**

**Rationale**: Damage liability assessment (DE-2.2) and credit amount determination (DE-2.4) are judgment-heavy and high-risk—require human expertise. Agent can handle data retrieval (DE-2.3), pattern detection (DE-2.5), customer communication (DE-2.7), and assist with return logistics (DE-2.8). Billing integration (DE-2.6) is constrained by Aurum batch architecture. This JtD has lower volume (~45/day, 25% of exceptions) but higher complexity than refused deliveries.

---

#### JtD-DE-3: Investigate Missed Delivery Window

| Micro-Task | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency | Risk | **Suitability** | **Archetype** |
|------------|----------------|---------------------|---------------|-------------------|---------------|---------|------|----------------|--------------|
| **DE-3.1**: Receive missed window inquiry from customer | Semi-structured (call/email) | H | H (CRM) | M | M | H | L | **Medium** | Agent-led + Human Oversight |
| **DE-3.2**: Look up delivery status in driver app and dispatch system | Structured | H | M (driver app API read-only) | M (data may be stale) | M | H | L | **High** | Fully Agentic |
| **DE-3.3**: Retrieve GPS history and route plan | Structured | H | M (driver app API) | M (GPS lag, driver may be offline) | M | H | L | **High** | Fully Agentic |
| **DE-3.4**: Diagnose delay cause | Semi-structured (data + judgment) | M | L (manual analysis) | H (root cause often unclear) | H | H | M | **Low-Medium** | Human-led + Agent Support |
| **DE-3.5**: Calculate revised ETA or confirm failure | Structured (GPS + route knowledge) | M (requires tacit knowledge of route timing) | L (manual calculation) | M (dispatch consultation) | M | H | M (customer expectation) | **Medium** | Human-led + Agent Support |
| **DE-3.6**: Communicate updated ETA to customer | Semi-structured | M (may need to manage upset customer) | H (CRM) | M | M | H | M (reputation) | **Medium** | Agent-led + Human Oversight |
| **DE-3.7**: Schedule re-delivery if delivery failed | Structured (scheduling system) | M | M (CRM + dispatch console) | M (customer availability) | M | M | M | **Medium** | Agent-led + Human Oversight |
| **DE-3.8**: Escalate if SLA breach or high-value customer | Semi-structured | M (SLA rules + customer tier) | M (CRM escalation workflow) | M | M | M | H (contract penalty) | **Medium** | Agent-led + Human Oversight |

**JtD-DE-3 Overall Archetype**: **Agent-led + Human Oversight**

**Rationale**: 70% of missed window inquiries are straightforward status lookups with predictable delay causes (traffic, driver running behind schedule). Agent can handle data retrieval (DE-3.2, DE-3.3), standard customer communication (DE-3.6), re-delivery scheduling (DE-3.7), and escalation threshold checks (DE-3.8) autonomously. Delay diagnosis (DE-3.4) and ETA calculation (DE-3.5) require human judgment when root cause is unclear or customer is high-value. This is the highest-volume exception sub-type (~63/day, 35% of exceptions).

---

#### JtD-DE-4: Manage Unattended Address Exception

| Micro-Task | Input Structure | Decision Determinism | Tool Coverage | Context Complexity | Exception Rate | Latency | Risk | **Suitability** | **Archetype** |
|------------|----------------|---------------------|---------------|-------------------|---------------|---------|------|----------------|--------------|
| **DE-4.1**: Receive unattended address report from driver | Semi-structured (driver app) | H | M (driver app) | L | M | H | L | **Medium** | Agent-led + Human Oversight |
| **DE-4.2**: Check customer file for safe place/neighbor authority | Structured (CRM lookup) | H | H (CRM API) | M (data may be missing) | M | H | M (theft risk if wrong decision) | **High** | Fully Agentic |
| **DE-4.3**: Verify consignment eligibility for unattended delivery | Structured (value, signature requirement) | H | M (consignment data) | L | L | H | H (high-value items must have signature) | **High** | Fully Agentic |
| **DE-4.4**: Decide action (leave safe place, return, re-attempt) | Semi-structured | M (rule-based but judgment required) | L (manual) | M | M | H | H (theft, loss liability) | **Medium** | Agent-led + Human Oversight |
| **DE-4.5**: Instruct driver via app | Structured | H | H (driver app) | L | L | H | M | **High** | Fully Agentic |
| **DE-4.6**: Notify customer of delivery attempt and next steps | Semi-structured (SMS, email) | H | H (CRM automation) | M (customer may call back) | M | M | M | **High** | Fully Agentic |
| **DE-4.7**: Schedule re-delivery or depot pickup | Structured | M | M (CRM + dispatch) | M (customer availability) | M | M | M | **Medium** | Agent-led + Human Oversight |

**JtD-DE-4 Overall Archetype**: **Agent-led + Human Oversight**

**Rationale**: 80% of unattended address exceptions follow clear rules (safe place authority on file, low-value consignment eligible for unattended delivery). Agent can handle data retrieval (DE-4.2, DE-4.3), driver instructions (DE-4.5), customer notifications (DE-4.6), and re-delivery scheduling (DE-4.7) autonomously. Action decision (DE-4.4) requires human oversight when customer preference is unclear or consignment is high-value. This is moderate volume (~36/day, 20% of exceptions).

---

## Archetype Assignment Rationale

### Dispatch Adjustments: Human-led + Agent Support

**Delegation Breakdown**:
- **Fully Agentic** (20% of cognitive work): Data retrieval, capacity checks, driver notifications, incident logging
- **Agent-led + Human Oversight** (15%): Request validation, ETA updates
- **Human-led + Agent Support** (50%): Route impact analysis, driver selection assistance, diversion approval
- **Human Only** (15%): Driver swaps, handoff negotiations, overtime authorization

**Why not Agent-led?**
1. **Dispatch console API constraint**: No write access → human must execute route updates manually
2. **Driver selection complexity**: Tacit knowledge of driver capability, willingness, and relationships not codified
3. **Real-time safety/welfare decisions**: Driver swap handoff locations, fatigue assessment, union rules require human judgment
4. **High-stakes SLA risk**: Route diversions that affect multiple customers require human approval

**Agent value proposition**: Agents eliminate 7 minutes of system-hopping and data retrieval per case (from 18 min avg to ~11 min). They provide route impact analysis and driver candidate recommendations, but humans make final decisions.

**Critical path to higher delegation**: 
1. Build dispatch console API wrapper or separate route optimization service
2. Formalize driver selection criteria (capability matrix, willingness scoring, location-based availability)
3. Codify customer priority tiers and SLA tolerance thresholds

---

### Delivery Exceptions: Mixed Archetype by Sub-Type

**Delegation Breakdown by Sub-Type**:

| Sub-Type | Volume | Archetype | Delegation % |
|----------|--------|-----------|-------------|
| Missed delivery window (DE-3) | 35% (~63/day) | Agent-led + Human Oversight | 70% |
| Refused delivery (DE-1) | 35% (~63/day) | Agent-led + Human Oversight (standard), Human-led + Agent Support (complex) | 60% |
| Unattended address (DE-4) | 20% (~36/day) | Agent-led + Human Oversight | 75% |
| Damaged consignment (DE-2) | 10% (~18/day) | Human-led + Agent Support | 40% |

**Why Agent-led + Human Oversight for standard cases?**
1. **High input structure**: 70% of exceptions have structured triggers (driver app reports, customer CRM inquiries)
2. **Decision determinism**: 60% follow predictable rules (high-value threshold, safe place authority, standard refusal reasons)
3. **Good tool coverage**: CRM API, driver app API, and GPS data available
4. **Low context complexity**: Standard cases don't require institutional knowledge or relationship management
5. **Moderate risk**: Errors are reversible (re-delivery can be scheduled, customer can be called back)

**Why Human-led + Agent Support for complex cases?**
1. **Judgment-dependent decisions**: Damage liability assessment, credit amount determination, complex refusal reasoning
2. **High exception rate**: 40% of refused deliveries have conflicting accounts or ambiguous causes
3. **High risk**: Financial liability (credits, insurance claims), reputation risk (high-value customers)
4. **Billing system constraint**: Aurum 24-48h lag prevents real-time credit validation

**Agent value proposition**: Agents eliminate 5-7 minutes of data retrieval and case logging per exception (from 12 min avg to ~5-7 min for standard cases). They provide disposition recommendations and draft customer communications, but humans approve high-risk decisions.

**Critical path to higher delegation**:
1. Formalize refused delivery disposition decision tree (codify Sandra's 400 cases this quarter)
2. Build real-time credit workflow outside Aurum with batch reconciliation
3. Formalize customer tier system (Hayes & Sons pattern → explicit priority scoring)
4. Train damage liability assessment model on historical photo + outcome data

---

## Trade-Off Analysis

### Trade-Off 1: Dispatch Console API vs. Human Execution Bottleneck

**Current State**: Dispatch console has limited/no API for route updates. Humans must manually enter route changes via Citrix.

**Option A: Build API wrapper or separate route optimization service**
- **Pros**: Enables agent-driven route updates, eliminates manual entry bottleneck, unlocks 35-50% delegation potential
- **Cons**: Requires 3-6 months engineering effort, risk of dispatch console schema changes, ongoing maintenance burden
- **Cost**: £50-80K engineering + £10K/year maintenance
- **Payoff**: Enables Phase 2 Dispatch Adjustments delegation (1.5 FTE equivalent savings = £52K/year)

**Option B: Keep human-in-the-loop for route execution**
- **Pros**: No upfront engineering cost, no schema change risk, faster Phase 1 deployment
- **Cons**: Caps delegation at 15-20% (CRM automation only), manual entry remains bottleneck, lower ROI
- **Cost**: £0 upfront
- **Payoff**: Phase 1 only (0.5 FTE equivalent savings = £17K/year)

**Recommendation**: **Option A** if ROI justifies investment (payoff period ~18 months). **Option B** for Phase 1 pilot, revisit after proving Delivery Exceptions value.

---

### Trade-Off 2: Decision Rule Formalization vs. Agent Judgment Capability

**Current State**: Core decisions (refused delivery disposition, customer priority, damage liability) rely on implicit rules in Sandra's head and senior dispatchers' tacit knowledge.

**Option A: Structured elicitation to codify decision rules**
- **Pros**: Enables agent-led decisions with human oversight, reduces knowledge concentration risk, scales expertise across team
- **Cons**: Requires 20+ case shadowing sessions, 2-3 months elicitation effort, rules may drift over time
- **Cost**: £20-30K (FDE time + SME time)
- **Payoff**: Unlocks 40-60% delegation for Delivery Exceptions (2.0 FTE equivalent savings = £70K/year)

**Option B: Keep human judgment, use agents for data retrieval only**
- **Pros**: No elicitation cost, no risk of rule drift, faster deployment
- **Cons**: Caps delegation at 20-30%, knowledge concentration risk remains, lower ROI
- **Cost**: £0 upfront
- **Payoff**: Limited to data retrieval and case logging (0.8 FTE equivalent savings = £28K/year)

**Recommendation**: **Option A**. Decision rule formalization is the highest-leverage investment. Sandra's 400 cases this quarter are a goldmine—capture them before she moves on or gets promoted. Payoff period ~5 months.

---

### Trade-Off 3: Aurum Billing Integration vs. Batch Reconciliation Workaround

**Current State**: Aurum billing has 24-48h batch lag, no real-time API. Credits require manual tickets (48h turnaround).

**Option A: Negotiate Aurum API access or build real-time integration**
- **Pros**: Enables real-time credit validation, eliminates billing dispute lag, unlocks billing-adjacent delegation
- **Cons**: Aurum vendor may not provide API, integration fragile to schema changes, high engineering cost
- **Cost**: £80-120K (if API available) or £150-200K (if custom integration required)
- **Payoff**: Enables billing dispute delegation (0.5 FTE equivalent savings = £17K/year) + reduces dispute resolution time (customer satisfaction benefit)

**Option B: Build real-time credit workflow outside Aurum with batch reconciliation**
- **Pros**: Faster deployment, no vendor dependency, agent can queue credits and track status
- **Cons**: Introduces reconciliation complexity, audit trail split across systems, 24-48h lag remains
- **Cost**: £30-50K (workflow + reconciliation logic)
- **Payoff**: Partial billing delegation (0.3 FTE equivalent savings = £10K/year)

**Option C: Keep billing human-led, focus agent delegation on non-billing exceptions**
- **Pros**: No upfront cost, no reconciliation complexity, faster Phase 1 deployment
- **Cons**: Billing disputes remain manual (28 min avg handling time), cross-stream handoffs remain painful
- **Cost**: £0 upfront
- **Payoff**: No billing savings, but Delivery Exceptions delegation still viable

**Recommendation**: **Option C** for Phase 1-2. **Option B** for Phase 3 if billing dispute volume increases or customer satisfaction metrics justify investment. **Option A** only if Aurum vendor provides API (unlikely given legacy architecture).

---

### Trade-Off 4: Driver Interaction: App Messaging vs. Voice Calls

**Current State**: Drivers prefer voice calls for complex negotiations (driver swaps, handoff logistics). App messaging works for simple instructions.

**Option A: Build agent-driven voice call capability**
- **Pros**: Enables agent-led driver negotiations, eliminates voice call bottleneck, unlocks driver swap delegation
- **Cons**: Voice AI quality risk (driver frustration if agent misunderstands), high engineering cost, driver union may resist
- **Cost**: £100-150K (voice AI integration + testing)
- **Payoff**: Enables driver swap delegation (0.4 FTE equivalent savings = £14K/year) but high risk of driver dissatisfaction

**Option B: Keep voice calls human-led, use agents for app messaging only**
- **Pros**: No voice AI risk, no driver union resistance, faster deployment
- **Cons**: Caps driver interaction delegation at 50%, driver swaps remain human-only
- **Cost**: £0 upfront
- **Payoff**: Partial driver interaction delegation (0.2 FTE equivalent savings = £7K/year)

**Recommendation**: **Option B**. Voice AI for driver negotiations is high-risk, low-ROI. Focus agent delegation on app messaging (notifications, simple instructions) and keep complex negotiations human-led. Revisit if driver app adoption increases or union rules change.

---

### Trade-Off 5: Phased Deployment vs. Big Bang

**Option A: Phased deployment (Phase 1 → Phase 2 → Phase 3)**
- **Pros**: Lower risk, faster time-to-value, learn from Phase 1 before scaling, easier change management
- **Cons**: Slower overall deployment, partial benefits in early phases, requires interim handoff protocols
- **Cost**: £50-80K Phase 1 (6 months), £80-120K Phase 2 (6 months), £50-80K Phase 3 (6 months)
- **Payoff**: Phase 1 = £28K/year, Phase 2 = £52K/year additional, Phase 3 = £10K/year additional (cumulative £90K/year)

**Option B: Big bang deployment (all work streams, all delegation archetypes)**
- **Pros**: Faster overall deployment, higher total benefits, no interim handoff protocols
- **Cons**: Higher risk, longer time-to-value, harder change management, higher upfront cost
- **Cost**: £180-280K upfront (12-18 months)
- **Payoff**: £90K/year but delayed 12-18 months

**Recommendation**: **Option A**. Phased deployment reduces risk, proves value incrementally, and allows course correction. Phase 1 focuses on highest-volume, lowest-risk Delivery Exceptions. Phase 2 adds Dispatch Adjustments after dispatch console API is addressed. Phase 3 adds billing integration if justified.

---

## Implementation Sequencing Recommendations

### Phase 1: Delivery Exceptions (Agent-led + Human Oversight) — Months 1-6

**Scope**: 
- Missed delivery window inquiries (DE-3): 70% delegation
- Standard refused deliveries (DE-1): 60% delegation
- Unattended address exceptions (DE-4): 75% delegation
- CRM-centric tasks: case logging, customer communication, data retrieval

**Delegation Archetype**: Agent-led + Human Oversight

**Prerequisites**:
1. Formalize refused delivery disposition decision tree (20 case shadowing sessions with Sandra)
2. Formalize customer tier system (explicit priority scoring)
3. Build agent specification for CRM API integration and driver app read-only API

**Expected Outcomes**:
- 40-60% cognitive work elimination for Delivery Exceptions
- 1.5-2.0 FTE equivalent savings (~£52-70K/year)
- Proof of concept for agent-led delegation with human oversight

**Success Metrics**:
- Average handling time: 12 min → 5-7 min for standard cases
- Human override rate: <15% (target: agent recommendations accepted 85%+ of the time)
- Customer satisfaction: maintain or improve (NPS, CSAT)
- Error rate: <2% (agent disposition errors requiring human correction)

---

### Phase 2: Dispatch Adjustments (Human-led + Agent Support) — Months 7-12

**Scope**:
- Additional pickup requests (DA-1): 35-50% delegation
- Route diversions (DA-2): 35-50% delegation
- Route impact analysis, driver candidate identification, ETA calculations

**Delegation Archetype**: Human-led + Agent Support

**Prerequisites**:
1. Build dispatch console API wrapper or separate route optimization service
2. Formalize driver selection criteria (capability matrix, willingness scoring)
3. Validate Phase 1 success metrics before scaling

**Expected Outcomes**:
- 35-50% cognitive work elimination for Dispatch Adjustments
- 1.0-1.5 FTE equivalent savings (~£35-52K/year additional)
- Agent-driven route impact analysis and driver recommendations

**Success Metrics**:
- Average handling time: 18 min → 10-12 min
- Human override rate: <20% (target: agent recommendations accepted 80%+ of the time)
- SLA compliance: maintain or improve (on-time delivery %)
- Driver satisfaction: maintain or improve (driver feedback on app messaging vs. calls)

---

### Phase 3: Billing Integration (Human-led + Automation Support) — Months 13-18

**Scope**:
- Billing dispute coordination (DE-1.10, DE-2.6)
- Real-time credit workflow outside Aurum with batch reconciliation
- Cross-stream handoff automation (delivery exception → billing dispute → dispatch adjustment)

**Delegation Archetype**: Human-led + Automation Support

**Prerequisites**:
1. Validate Phase 1-2 success metrics
2. Build real-time credit workflow and batch reconciliation logic
3. Formalize credit approval thresholds and audit trail requirements

**Expected Outcomes**:
- 20-30% cognitive work elimination for billing-adjacent tasks
- 0.3-0.5 FTE equivalent savings (~£10-17K/year additional)
- Reduced billing dispute resolution time (9 days → 2-3 days target)

**Success Metrics**:
- Billing dispute resolution time: 9 days → 2-3 days
- Credit approval accuracy: >95% (agent-queued credits approved without revision)
- Audit compliance: 100% (all credits logged with rationale and approval trail)
- Customer satisfaction: improve (billing dispute NPS)

---

### Total Program Economics

**Total Investment**: £180-280K over 18 months (phased)

**Total Annual Savings**: £97-139K/year (conservative: £84K, best case: £120K)

**Payoff Period**: 18-24 months (conservative), 15-18 months (best case)

**ROI**: 35-50% annual return after payoff period

**Risk-Adjusted NPV** (3-year horizon, 10% discount rate): £120-180K

---

## Document Control

- **Created**: 2025-01-27
- **Version**: 1.0
- **Owner**: AI FDE Team
- **Related Documents**:
  - `cognitive-load-map.pdf` - Source micro-task analysis
  - `scenario.pdf` - Source scenario and artefacts
  - `atx-assessment.pdf` - Phase 3 methodology
  - `assumptions.md` - All assumptions referenced
- **Next Phase**: Agent Mapping and Business Case Development (Phase 4)