# Agent Purpose Document: ETA Investigation Agent (DE-3)

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Agent Purpose](#agent-purpose)
3. [Agent Activity Catalog](#agent-activity-catalog)
4. [Autonomy Matrix](#autonomy-matrix)
5. [Context Engineering Design](#context-engineering-design)
6. [Compounding Roadmap](#compounding-roadmap)

---

## Executive Summary

This document specifies the design for the **ETA Investigation Agent**, the Wave 1 pilot agent for Apex Distribution's agentic transformation. This agent automates the investigation of missed delivery window inquiries (DE-3), handling 140 cases/day with 85-95% autonomous coverage.

### Agent Profile

| Attribute | Value |
|-----------|-------|
| **Agent Name** | ETA Investigation Agent |
| **Job to be Done** | Investigate missed delivery windows and provide accurate ETAs to customers |
| **Delegation Archetype** | Fully Agentic |
| **Target Coverage** | 85-95% autonomous (10-15% escalation) |
| **Volume** | 140 cases/day (estimated from 400 ETA inquiries × 35% requiring investigation [Ref: A024]) |
| **Annual Baseline Cost** | £81,567 (4,293 human hours @ £19/hour [Ref: A018]) |
| **Annual Agent Cost** | £28,354 (tokens + APIs + infrastructure [Ref: A032]) |
| **Annual Saving** | **£53,213** |
| **Payback Period** | **7 months** |
| **Year 1 ROI** | **77%** |

### Why This Agent First

1. **Highest absolute ROI** (£53K/year) across all Wave 1 candidates
2. **Fully Agentic archetype** enables 85-95% autonomous operation (lowest HITL rate)
3. **Lowest risk profile**: Wrong ETA is easily corrected, no financial liability, no safety/compliance concerns
4. **High customer satisfaction impact**: Reduces 4-hour ETA windows to 20-minute estimates [Ref: Artefact 3]
5. **Builds foundational platform assets**: CRM API, GPS API, ETA calculation engine → reused in all Wave 2-3 agents

### Key Design Principles

1. **Diagnostic workflow**: Agent performs rule-based diagnosis (status lookup, GPS retrieval, ETA calculation) → fast, deterministic
2. **Exception-aware**: Detects stale GPS (~10% cases), SLA breaches, lost consignments → escalates with full context
3. **Customer-first communication**: Tighter ETA windows (20 min vs. 4 hours), proactive notifications, empathetic tone
4. **Audit-ready**: Every decision logged with reasoning, data sources, confidence scoring
5. **Token-optimized**: Leverages prompt caching for route plans and historical timing [Ref: A030] → 40-50% token cost reduction

---

## Agent Purpose

### Agent Name
**ETA Investigation Agent** (Internal code: `eta-investigation-v1`)

### Job to be Done
When a customer inquires about a missed delivery window ("Where is my delivery?"), the agent:
1. Retrieves order details and delivery status from CRM and driver app
2. Diagnoses delivery status (on-route, delayed, failed attempt, lost)
3. Calculates revised ETA using GPS location, route sequence, and historical timing
4. Communicates ETA to customer via SMS/email/phone response
5. Escalates to human agent if GPS stale, consignment lost, or SLA breach detected

**Cognitive contract**: Customer receives accurate, timely ETA within 2 minutes of inquiry, with tighter precision than current "best guess" 4-hour windows [Ref: Artefact 3].

### Business Context
- **Department**: Customer Operations (35-person team)
- **Process**: Delivery Exceptions work stream (180 cases/day total)
- **Customer Journey Step**: Post-dispatch, pre-delivery — customer awaiting delivery within committed window
- **Pain Point**: Customers frustrated with imprecise ETAs ("13:00–17:00" windows), agents spend 8 min/case manually checking GPS and route plans [Ref: Cognitive Load Map micro-task DE-3.2, DE-3.3, DE-3.5]

### Primary Objectives

1. **Provide accurate ETAs**: 95% of agent-calculated ETAs within ±30 minutes of actual delivery [Ref: A042]
2. **Reduce ETA window width**: From 4-hour "best guess" windows to 20-minute precision windows
3. **Autonomous coverage**: Handle 85-95% of missed window inquiries without human escalation [Ref: Phase 3 analysis]
4. **Response speed**: Respond to customer within 2 minutes (vs. current 5-10 minutes with human lookup)
5. **Customer satisfaction**: Achieve 90%+ customer satisfaction on post-delivery survey for ETA inquiries [Ref: A043]

### Key Performance Indicators (KPIs)

| KPI | Target | Acceptable Ceiling | Measurement Method |
|-----|--------|--------------------|--------------------|
| **Accuracy** | 95% ETAs within ±30 min of actual delivery | 90% minimum | Compare agent ETA to actual delivery timestamp (driver app) |
| **Coverage** | 90% cases handled autonomously | 85% minimum | (Total cases - Escalations) / Total cases |
| **Throughput** | 140 cases/day (avg 2 min/case) | 100 cases/day minimum during pilot | Agent processing log |
| **Cost per Case** | £0.57 (token + API + HITL) | £0.75 maximum | Token usage × pricing + API calls + HITL cost [Ref: TCO calculation] |
| **HITL Rate** | 10% (stale GPS, edge cases) | 15% maximum | Escalations / Total cases |
| **Customer Satisfaction** | 90%+ satisfaction score | 85% minimum | Post-delivery survey: "Was ETA information helpful?" |
| **Error Rate** | <5% (wrong status, incorrect ETA) | <8% maximum | Customer callbacks, delivery mismatches, audit reviews |

### Failure Modes

**What does a bad output look like?**
1. **Incorrect ETA**: Agent calculates ETA of 14:00, delivery arrives at 16:30 (2.5 hour error)
   - **Consequence**: Customer misses delivery, dissatisfaction, potential complaint escalation
   - **Recovery**: Customer calls back, human agent reschedules or provides updated ETA
   - **Mitigation**: Confidence scoring on ETA calculation; escalate if confidence <70% [Ref: A044]

2. **Wrong delivery status**: Agent reports "out for delivery" when consignment is actually "failed attempt" or "return to depot"
   - **Consequence**: Customer waits unnecessarily, calls back upset
   - **Recovery**: Human agent corrects status, arranges re-delivery
   - **Mitigation**: GPS freshness validation (escalate if GPS >30 min stale); delivery event timestamp validation

3. **Missed escalation**: Agent provides ETA for SLA breach case (delivery past committed window) without escalating to supervisor
   - **Consequence**: Customer escalates to complaints, SLA penalty not proactively managed
   - **Recovery**: Supervisor reviews sample of cases, identifies missed escalation patterns
   - **Mitigation**: Explicit SLA breach detection rule; auto-escalate if delivery past committed window + customer is high-priority [Ref: A009]

4. **Communication failure**: Agent sends SMS/email with technical jargon, unclear phrasing, or wrong customer contact
   - **Consequence**: Customer confusion, doesn't understand ETA update
   - **Recovery**: Customer calls back for clarification
   - **Mitigation**: Communication template validation; empathy tone guidelines in prompt; contact validation before send

5. **System timeout**: Agent takes >60 seconds to respond due to API latency or retry loops
   - **Consequence**: Customer on hold (phone) or abandons inquiry (SMS/email)
   - **Recovery**: Timeout triggers fallback to human agent
   - **Mitigation**: API timeout limits (5s per API call); circuit breaker after 2 failed retries; escalate to human with context

### Delegation Archetype
**Fully Agentic**

**Rationale** (from Phase 3 analysis):
- Input structure: HIGH (clear intent "where is my delivery?", structured order data)
- Decision determinism: HIGH (rule-based diagnosis logic, ETA calculation algorithmic)
- Tool coverage: HIGH (CRM API, GPS API, route data accessible)
- Context complexity: MEDIUM (requires customer SLA, historical timing, but no institutional knowledge)
- Exception rate: MEDIUM (10-15% stale GPS, SLA breaches, lost consignments — detectable patterns)
- Risk/Compliance: HIGH (low consequence — wrong ETA is easily corrected, no financial liability)

**No dimensions scored LOW** → Fully Agentic delegation viable. Human oversight required only for edge cases (stale GPS, SLA breaches) that are predictable and escalatable.

### Escalation Triggers

**Agent escalates to human Customer Service Agent if:**
1. **GPS data stale**: Last GPS update >30 minutes old → "Unable to calculate precise ETA due to GPS lag. Human agent investigating. You'll receive update within 15 minutes." [Ref: A045]
2. **Consignment status ambiguous**: Delivery status in driver app is "exception" or "pending" without clear resolution path → Escalate with context: "Status unclear, may require driver contact"
3. **SLA breach detected**: Delivery is past committed window (e.g., committed 14:00, now 15:30) → Auto-escalate to supervisor with customer context and suggested goodwill actions [Ref: Cognitive Load Map micro-task DE-3.8]
4. **Consignment marked "lost" or "return to depot"**: Requires re-delivery scheduling or depot pickup arrangement → Escalate with customer preference data
5. **High-priority customer + delay >1 hour**: Customer tier is "high-value" [Ref: A009] AND current delay is >1 hour beyond original ETA → Escalate to senior agent for white-glove handling
6. **Low confidence ETA (<70%)**: Agent's confidence score on ETA calculation is below threshold (due to route timing variability, traffic anomaly) → Escalate with "ETA range uncertain, human review requested" [Ref: A044]
7. **Customer requests human agent**: Customer explicitly says "speak to human" or "not satisfied" in follow-up message → Immediate escalation, no retry

**Agent escalates to Dispatch Coordinator if:**
1. **Driver unreachable**: GPS data stale >1 hour, no delivery events logged, suggests driver app offline or driver issue → Escalate to dispatch for driver welfare check

**Agent returns to customer for clarification if:**
1. **Order number ambiguous**: Customer provides partial/incorrect order number, multiple matches found → "We found 2 orders matching your reference. Please confirm: [order details]"
2. **Customer contact missing**: No SMS/email on file for customer → "To send you ETA updates, please reply with your preferred contact method (SMS/email)"

---

## Agent Activity Catalog

The ETA Investigation Agent performs 12 micro-tasks, decomposed from cognitive load map analysis (DE-3.1 through DE-3.8). Each task is classified by type, delegation level, data requirements, tool requirements, and risk level.

### Micro-Task Inventory

| Task ID | Task Description | Type | Delegation Level | Data Required | Tool Required | Risk Level | Rationale |
|---------|------------------|------|------------------|---------------|---------------|------------|-----------|
| **T1** | **Parse customer inquiry intent** | Reasoning | Fully Agentic | Customer message (SMS, email, phone transcript) | NLP intent classifier | Low | Clear intent ("where is my delivery?"), low ambiguity. Agent classifies as "ETA inquiry" vs. "complaint" vs. "other". |
| **T2** | **Extract order number** | Reasoning | Fully Agentic | Customer message, CRM customer ID | CRM API (customer orders) | Low | Customer provides order number in message (80% cases [Ref: A046]) or agent retrieves from recent orders if customer authenticated. Escalate if ambiguous. |
| **T3** | **Retrieve order details** | Retrieval | Fully Agentic | Order number | CRM API (`GET /orders/{id}`) | Low | Fetch order details: customer, consignment value, delivery address, committed window, priority tier [Ref: A009]. Standard API call. |
| **T4** | **Retrieve delivery status from driver app** | Retrieval | Fully Agentic | Order number, route assignment | Driver App API (`GET /deliveries/{id}/status`) | Low | Fetch current delivery status: "out for delivery", "delivered", "failed attempt", "return to depot", "exception". Standard API call. |
| **T5** | **Retrieve GPS location and route sequence** | Retrieval | Fully Agentic | Driver ID (from order), route ID | Driver App API (`GET /drivers/{id}/location`, `GET /routes/{id}/sequence`) | Low | Fetch driver's current GPS coordinates, last update timestamp, and route sequence (stop 4 of 9, etc.). Standard API call. |
| **T6** | **Validate GPS freshness** | Decision | Fully Agentic | GPS timestamp, current time | None (logic rule) | Medium | Calculate time since last GPS update. If >30 min → escalate (stale GPS [Ref: A045]). If <30 min → proceed. Rule-based decision. |
| **T7** | **Retrieve historical route timing** | Retrieval | Fully Agentic | Route ID, time of day, day of week | Historical Timing DB (built from driver app logs) | Low | Fetch average stop duration for this route (e.g., stop 3-4 takes 15 min avg) and traffic patterns. **Cacheable** [Ref: A030]. |
| **T8** | **Calculate revised ETA** | Reasoning | Fully Agentic | GPS location, route sequence, historical timing, traffic data (optional) | ETA Calculation Engine (custom logic) | Medium | Algorithm: (1) Calculate distance from GPS to customer address, (2) Estimate remaining stops × avg stop duration, (3) Add traffic buffer (if traffic API available), (4) Output ETA range (e.g., 14:15–14:35). **Core value-add task**. |
| **T9** | **Detect SLA breach** | Decision | Fully Agentic | Committed delivery window (from order), calculated ETA, current time | None (logic rule) | High | Rule: If current time > committed window end → SLA breach. If customer is high-priority [Ref: A009] → escalate to supervisor. If standard customer → flag in response ("apologies for delay"). |
| **T10** | **Generate customer communication** | Generation | Fully Agentic | Delivery status, ETA range, customer name, order number | None (LLM generation) | Low | Draft SMS/email response with: (1) Delivery status ("out for delivery"), (2) ETA range ("14:15–14:35"), (3) Empathetic tone ("We'll notify you 30 min before arrival"). Uses communication template. |
| **T11** | **Send notification to customer** | Action | Fully Agentic | Customer contact (SMS/email from CRM), drafted message | SMS Gateway API / Email API | Medium | Send notification via preferred channel. Validate contact info exists. Log send confirmation. **Action with external effect**. |
| **T12** | **Log case in CRM** | Action | Fully Agentic | Order number, inquiry details, agent actions, ETA provided | CRM API (`POST /cases`, `PUT /orders/{id}/notes`) | Low | Create case record for audit trail: inquiry timestamp, agent decision reasoning, ETA calculation details, communication sent. **Governance requirement**. |

### Task Type Distribution
- **Reasoning**: 3 tasks (T1, T2, T8) — NLP, ETA calculation
- **Retrieval**: 4 tasks (T3, T4, T5, T7) — API calls to CRM, driver app, historical DB
- **Decision**: 2 tasks (T6, T9) — Rule-based logic (GPS freshness, SLA breach)
- **Generation**: 1 task (T10) — LLM drafts customer message
- **Action**: 2 tasks (T11, T12) — External effects (send SMS, log CRM)

### Risk Level Distribution
- **Low**: 7 tasks (T1, T2, T3, T4, T5, T7, T10, T12) — Standard operations, reversible
- **Medium**: 4 tasks (T6, T8, T11) — GPS validation, ETA calculation (core accuracy), send notification (external action)
- **High**: 1 task (T9) — SLA breach detection (compliance, customer relationship risk)

### Delegation Assessment
**All 12 tasks scored "Fully Agentic"** → Agent can perform entire workflow autonomously for standard cases (90% of volume). Escalation triggers (T6 stale GPS, T9 SLA breach) handle edge cases (10% of volume).

---

## Autonomy Matrix

This matrix defines the operational contract between the ETA Investigation Agent and Apex Customer Operations. It specifies what the agent decides alone vs. what requires human approval or triggers escalation.

### Agent Decides Alone (No HITL Required)

The agent performs these actions autonomously without human approval:

**Data Retrieval & Diagnosis**:
- Retrieve order details from CRM
- Retrieve delivery status from driver app
- Retrieve GPS location and route sequence
- Retrieve historical route timing patterns
- Classify customer inquiry intent ("ETA inquiry" vs. "complaint" vs. "other")
- Extract order number from customer message or recent order history

**ETA Calculation**:
- Calculate revised ETA using GPS velocity + route sequence + historical timing
- Generate ETA range (e.g., "14:15–14:35") with confidence score
- Determine ETA precision (20-minute window) based on GPS freshness and route predictability

**Customer Communication**:
- Draft SMS/email response with delivery status + ETA
- Apply empathetic tone and clear language per communication templates
- Send notification to customer via preferred contact method (SMS/email)
- Provide proactive updates ("We'll notify you 30 min before arrival")

**Administrative Actions**:
- Log case in CRM with inquiry details, agent reasoning, and ETA provided
- Update order notes with customer interaction history
- Record token usage, API calls, and processing time for monitoring

**Threshold**: Agent autonomy applies to **standard cases** where:
- GPS data is fresh (<30 min old)
- Delivery status is clear ("out for delivery", "delivered")
- ETA confidence is ≥70% [Ref: A044]
- No SLA breach detected
- Customer is standard-priority or low-priority [Ref: A009]

### Agent Acts, Human Notified After

The agent takes action autonomously but notifies a human agent asynchronously (no approval required, but human can review and intervene if needed):

**Edge Case Resolutions**:
- **Failed delivery attempts**: If delivery status is "failed attempt" (recipient unavailable), agent sends re-delivery scheduling link to customer and notifies Customer Service Agent of pending re-delivery coordination
- **Minor delays (<30 min)**: If calculated ETA is 10-30 minutes past committed window (minor SLA breach) for standard-priority customer, agent apologizes in message and logs case for supervisor review (no immediate escalation)
- **Standard acknowledgments**: If delivery is already "delivered" (customer inquiry after delivery completed), agent confirms delivery timestamp and asks if customer needs further assistance

**Notification Mechanism**: Agent adds case to "Review Queue" dashboard visible to Customer Service Agents. Notification appears in Slack channel: "ETA Agent handled [case ID], minor delay detected, no action required unless customer escalates."

**Supervisor Access**: Human agents can review agent decisions in CRM case log and override/correct if customer calls back dissatisfied.

### Agent Proposes, Human Approves Before Action

The agent generates a recommendation but requires explicit human approval before proceeding:

**SLA Breach Escalations** (High-Priority Customers):
- If delivery is >1 hour past committed window AND customer is high-priority [Ref: A009]:
  - Agent drafts: (1) ETA update message to customer, (2) Suggested goodwill action (e.g., "Offer £20 credit for delay")
  - Human supervisor reviews recommendation in approval dashboard
  - Supervisor clicks "Approve" (agent sends message + logs goodwill offer) or "Override" (supervisor takes over case)

**Ambiguous Order Identification**:
- If multiple orders match customer's partial order number:
  - Agent presents options to human: "Customer provided 'AX-771', found 2 matches: [order 1 details] [order 2 details]"
  - Human selects correct order → agent proceeds with ETA calculation

**Policy Exceptions**:
- If agent calculates ETA is >2 hours beyond committed window (severe delay) for any customer priority:
  - Agent proposes escalation to supervisor with suggested actions (re-route driver, arrange urgent re-delivery, offer compensation)
  - Human approves/modifies action plan

**Approval Mechanism**: Approval dashboard shows pending cases requiring approval. Human approves with one click (avg 30 seconds per approval [Ref: A047]). Agent waits max 5 minutes for approval; if no response, escalates to general Customer Service queue.

### Human Takes Over (Agent Supports)

The agent immediately escalates to a human agent and provides supporting information but does not take action:

**GPS/System Issues**:
- **GPS data stale** (>30 min since last update [Ref: A045]): Agent cannot calculate reliable ETA → escalates with message: "GPS last updated 10:48 (47 min ago), unable to provide precise ETA. Recommend dispatch coordinator contact driver for status."
- **Consignment status "exception" or "lost"**: Delivery status is ambiguous or indicates problem → escalates with full order context and suggested next steps (driver contact, depot search)
- **Driver app offline**: No GPS data available for assigned driver → escalates to dispatch coordinator for driver welfare check

**Customer Escalation Requests**:
- Customer explicitly requests human agent ("I want to speak to someone", "This is unacceptable")
- Customer replies with dissatisfaction to agent's ETA message ("This is the third delay!", "I need this today")
- Agent detects complaint sentiment in follow-up message (NLP sentiment classifier flags negative tone)

**Complex Re-Delivery Scenarios**:
- Customer needs special delivery instructions (e.g., "Can driver call me 30 min before arrival?")
- Customer requests depot pickup instead of re-delivery
- Customer unavailable for original delivery window, needs rescheduling coordination

**Regulatory/Compliance Flags**:
- Consignment contains regulated goods (flagged in order metadata) → human must verify delivery authorization
- Customer is on sanctions list or restricted delivery address → compliance review required before providing ETA

**Low Confidence ETA**:
- Agent's confidence score on ETA calculation is <70% [Ref: A044] (due to unusual route timing, traffic anomaly, missing historical data) → escalates with: "ETA uncertain due to [reason], human review recommended"

**Escalation Mechanism**: Agent creates escalation case in CRM, assigns to appropriate queue (Customer Service, Dispatch, Supervisor), and sends notification. Agent provides full context: customer inquiry, order details, GPS data, attempted diagnosis, reason for escalation.

**Human Agent Tooling**: Human agent sees agent's work in CRM: data retrieved, ETA calculation attempt, escalation reasoning. Human can leverage agent's data gathering (no need to re-query CRM/GPS) and complete the workflow.

---

## Context Engineering Design

Context quality determines agent accuracy and cost. The ETA Investigation Agent requires four types of memory and a structured retrieval strategy to operate effectively.

### Memory Architecture

| Memory Type | Content | Storage | Lifecycle | Size Estimate | Rationale |
|-------------|---------|---------|-----------|---------------|-----------|
| **In-Context (Short-Term)** | Current inquiry details: customer message, order number, parsed intent, retrieval results (order data, GPS, route), ETA calculation, draft response | Prompt window | Per inquiry (2-3 min session) | 1,500 tokens input + 300 tokens output [Ref: TCO calculation] | All data needed for single ETA inquiry workflow. Discarded after response sent. |
| **Episodic (Medium-Term)** | Customer inquiry history: prior ETA inquiries for this customer (timestamps, delays reported, satisfaction feedback) | CRM case history (retrieved on demand) | Per customer (indefinite) | 200-500 tokens per retrieval (last 3-5 inquiries) | Helps agent detect patterns (repeat inquiries = escalation signal). Retrieved if customer has >1 inquiry in past 30 days [Ref: A048]. |
| **Semantic (Long-Term)** | **Historical route timing patterns**: Avg stop duration by route ID, time of day, day of week. **Traffic patterns**: Known congestion zones, rush hour delays. **SLA rules**: Committed delivery windows by customer tier, escalation thresholds. | Historical Timing DB (PostgreSQL), Traffic API (optional), CRM customer tier lookup | Updated nightly (route timing), real-time (traffic), static (SLA rules) | 400-800 tokens per route plan (cacheable [Ref: A030]) | **Key cost optimization**: Route plans cached across 140 daily inquiries. Historical timing enables accurate ETA calculation. |
| **Procedural (Static)** | **Agent instructions**: System prompt defining role, workflow steps, escalation rules, communication tone guidelines. **Decision rules**: GPS freshness threshold (30 min), SLA breach detection logic, confidence scoring algorithm. **Guardrails**: "Do not provide ETA if GPS >30 min stale", "Escalate SLA breach for high-priority customers", "Use empathetic tone in delays". | System prompt (version-controlled in GitHub) | Static per agent version (updated with deployments) | 1,200-1,500 tokens (system prompt) | Defines agent behavior. Version-controlled for reproducibility and audit. |

**Total Context Window Usage** (per inquiry, excluding caching):
- System prompt: 1,200 tokens
- In-context (customer inquiry + order + GPS + route): 1,500 tokens
- Semantic retrieval (historical timing, non-cached): 800 tokens
- **Total input**: 3,500 tokens
- **Output** (ETA calculation + response): 300 tokens

**With Prompt Caching** [Ref: A030]:
- Historical timing (800 tokens) cached → reduced to ~160 tokens (20% cost)
- **Total input**: 2,860 tokens
- **Cost reduction**: 18% per inquiry

### Retrieval Strategy

**What Triggers Retrieval?**
1. **Order number extraction** → Query CRM for order details (`GET /orders/{id}`)
2. **Driver assignment identified** → Query driver app for GPS location and delivery status (`GET /drivers/{id}/location`, `GET /deliveries/{id}/status`)
3. **Route ID identified** → Query historical timing DB for route plan and avg timings (`SELECT * FROM route_timings WHERE route_id = X AND time_bucket = 'afternoon'`)
4. **Customer inquiry history flag** → Query CRM for customer's recent case history (if >1 inquiry in past 30 days [Ref: A048])
5. **Traffic data integration** (optional Wave 1, planned Wave 2) → Query traffic API for current conditions on route (`GET /traffic/{route_coordinates}`)

**Retrieval Target**:
- **Exact record retrieval**: Order details, delivery status, GPS location (structured data, not vector search)
- **Top-K retrieval** (not used in Wave 1): Historical timing is aggregated (avg stop duration), not individual case retrieval
- **Vector search** (not used in Wave 1): No unstructured text retrieval (e.g., KB articles) required for ETA calculation

**Retrieval Quality Evaluation**:
- **Accuracy**: Order ID match 100% (validated by customer or order history lookup)
- **Freshness**: GPS timestamp validated (<30 min for high confidence, escalate if stale [Ref: A045])
- **Completeness**: All required fields present in CRM/driver app response (order, GPS, route sequence). If missing → escalate with "data incomplete" error

**Cost Management**:
- **Caching**: Historical route timing cached for 24 hours (route plans are stable intraday) → 40-50% token reduction [Ref: A030]
- **Chunking** (not applicable): No large documents retrieved, all structured API responses
- **Index structure** (not applicable): Relational DB query, not vector index

### Prompt / Context Engineering Principles

#### 1. Role and Purpose First
```
You are the ETA Investigation Agent for Apex Distribution's Customer Operations team.

Your job: When a customer inquires about a missed delivery window, you investigate 
delivery status, calculate a revised ETA, and communicate it clearly to the customer.

Success criteria:
- Provide accurate ETA (within ±30 min of actual delivery)
- Respond within 2 minutes
- Handle 90% of inquiries autonomously
- Escalate edge cases (stale GPS, SLA breach, lost consignment) to human agents
```

#### 2. Explicit Scope
```
What you MAY do:
- Retrieve order and delivery data from CRM and driver app
- Calculate revised ETA using GPS + route timing
- Send ETA updates to customers via SMS/email
- Log all actions in CRM for audit

What you MAY NOT do:
- Provide ETA if GPS data is >30 minutes stale (escalate instead)
- Modify delivery routes or driver assignments (escalate to dispatch)
- Promise specific delivery times without ETA calculation (no guessing)
- Issue refunds or credits (escalate SLA breaches to supervisor)
```

#### 3. Few-Shot Examples
```
Example 1 - Standard ETA Inquiry:
Customer: "Hi, where is order AX-771-3344? Expected by 2pm."
Agent retrieves: GPS shows driver at stop 4 of 9, 8km from customer, last update 11:10 (fresh).
Agent calculates: Remaining stops (5) × 12 min avg = 60 min. Distance 8km ≈ 15 min. ETA: 12:25.
Agent responds: "Your delivery (order AX-771-3344) is out for delivery on route 028. 
Driver is currently at stop 4 of 9, last update 11:10. Estimated arrival: 12:15–12:35. 
We'll notify you 30 min before arrival."

Example 2 - Stale GPS Escalation:
Customer: "Where is my delivery? It's 3pm and I haven't heard anything."
Agent retrieves: GPS last update 10:48 (2 hours 12 minutes ago).
Agent detects: GPS stale >30 min → escalate.
Agent responds: "We're investigating the status of your delivery (order AX-771-3344). 
Our GPS data is temporarily unavailable. A Customer Service agent is contacting the 
driver now and will update you within 15 minutes. Order ref: CS-2026-04-14-00342."
Agent escalates: Creates CRM case, assigns to Customer Service queue.
```

#### 4. Guardrail Instructions
```
CRITICAL RULES:
1. GPS Freshness: If GPS last update >30 min ago → ESCALATE. Do not calculate ETA.
2. SLA Breach: If current time > committed delivery window → flag in response. 
   If customer is high-priority [tier A/B] → ESCALATE to supervisor.
3. Confidence Threshold: If your ETA confidence score <70% → ESCALATE with reasoning.
4. Lost/Exception Status: If delivery status is "lost", "exception", or "return to depot" 
   → ESCALATE to Customer Service.
5. Customer Escalation Request: If customer says "speak to human" or expresses 
   dissatisfaction → ESCALATE immediately.

When escalating:
- Create CRM case with full context (order, GPS, reason for escalation)
- Assign to appropriate queue (Customer Service, Dispatch, Supervisor)
- Inform customer: "A [role] is reviewing your inquiry and will respond within [time]."
```

#### 5. Structured Output for Downstream Processing
```
Your final output must be valid JSON with this schema:

{
  "inquiry_id": "string (UUID)",
  "order_number": "string",
  "delivery_status": "out_for_delivery | delivered | failed_attempt | exception | lost",
  "gps_freshness": "fresh | stale | unavailable",
  "eta_calculation": {
    "eta_range_start": "ISO 8601 timestamp",
    "eta_range_end": "ISO 8601 timestamp",
    "confidence_score": "float 0-1",
    "calculation_method": "gps_velocity | historical_avg | fallback_estimate"
  },
  "escalation": {
    "required": "boolean",
    "reason": "string (stale_gps | sla_breach | lost_consignment | customer_request | low_confidence)",
    "assigned_to": "customer_service | dispatch | supervisor"
  },
  "customer_communication": {
    "channel": "sms | email | phone",
    "message_text": "string (drafted response)",
    "sent": "boolean"
  },
  "audit_trail": {
    "data_sources_queried": ["crm", "driver_app", "historical_timing_db"],
    "api_calls_count": "integer",
    "processing_time_ms": "integer",
    "token_usage": {"input": integer, "output": integer}
  }
}
```

#### 6. Chain of Thought for Complex Reasoning
```
For ETA calculation, reason step-by-step:

Step 1: Validate GPS freshness
- GPS timestamp: [timestamp]
- Current time: [timestamp]
- Time since update: [duration]
- Assessment: [fresh <30min | stale >30min → escalate]

Step 2: Determine driver progress
- Route sequence: [current stop] of [total stops]
- GPS location: [lat, lon]
- Distance to customer: [km]
- Stops remaining: [count]

Step 3: Estimate remaining time
- Historical avg per stop: [X min]
- Remaining stops × avg: [Y min]
- Distance to customer: [Z km] ≈ [W min]
- Traffic buffer (if available): [T min]
- Total remaining time: Y + W + T = [total]

Step 4: Calculate ETA
- Current time: [timestamp]
- Add remaining time: [timestamp + total min]
- ETA range: [start] to [end] (20-min window)
- Confidence: [score] (based on GPS freshness, route predictability)

If confidence <70% → escalate. Otherwise → proceed with customer communication.
```

#### 7. Token Discipline
**Minimize Verbosity**:
- System prompt: 1,200 tokens (concise instructions, no repetition)
- Examples: 2 representative cases (not exhaustive edge cases)
- Retrieval results: Structured JSON (not verbose prose)

**Caching Strategy** [Ref: A030]:
- Route plans (400 tokens) cached for 24 hours → reused across 140 inquiries/day
- Historical timing patterns (400 tokens) cached for 24 hours
- **Total cached**: 800 tokens → saves 640 tokens per inquiry (80% reduction on cached content)

---

## Compounding Roadmap

The ETA Investigation Agent (Wave 1) builds foundational platform assets that amplify Wave 2 and Wave 3 agents, reducing marginal build cost by 40-50% [Ref: A028].

### Wave 1 — Foundation Agent (ETA Investigation)

**Agent**: ETA Investigation Agent (DE-3)
**Purpose**: Investigate missed delivery windows, provide accurate ETAs to customers
**Volume**: 140 cases/day
**Delegation Archetype**: Fully Agentic
**Build Timeline**: Months 1-3 (pilot Month 1-2, production Month 3)

**Key Integrations Built** (Reusable Platform Assets):
1. **CRM API Integration** (Salesforce REST API):
   - Authentication: OAuth 2.0 client
   - Order retrieval: `GET /orders/{id}`, `GET /customers/{id}/orders`
   - Case creation: `POST /cases`
   - Order notes: `PUT /orders/{id}/notes`
   - **Reuse potential**: All Wave 2-3 agents requiring customer data (DE-4, DA-1, DE-1, DE-2, DA-2)

2. **Driver App GPS API Integration**:
   - Authentication: API key
   - GPS location: `GET /drivers/{id}/location`
   - Delivery status: `GET /deliveries/{id}/status`
   - Route sequence: `GET /routes/{id}/sequence`
   - **Reuse potential**: DA-1 (pickup routing), DA-2 (route diversion), future dispatch agents

3. **ETA Calculation Engine** (Custom Logic):
   - Algorithm: GPS velocity + route sequence + historical timing + traffic buffer
   - Confidence scoring: Based on GPS freshness, route predictability, traffic anomalies
   - **Reuse potential**: Any agent providing ETAs (DE-4 re-delivery scheduling, DA-1 pickup timing)

4. **Historical Timing Database**:
   - Schema: `route_timings(route_id, time_bucket, avg_stop_duration, stddev)`
   - Nightly ETL: Driver app delivery logs → aggregated timing patterns
   - **Reuse potential**: DA-1 (pickup feasibility), DA-2 (route impact calculation)

5. **SMS/Email Notification Automation**:
   - SMS Gateway API integration (Twilio or similar)
   - Email API integration (SendGrid or similar)
   - Template engine: Parameterized messages with tone guidelines
   - **Reuse potential**: All agents communicating with customers (DE-4, DE-1, DE-2)

6. **Agent Monitoring & Logging Infrastructure**:
   - Token usage tracking (input/output per inquiry)
   - API call logging (endpoint, latency, error rate)
   - Escalation dashboard (HITL queue, escalation reasons)
   - Audit trail logging (agent decisions, data sources, reasoning)
   - **Reuse potential**: All Wave 2-3 agents (platform-level monitoring)

**Build Cost**: £30K (CRM integration £8K, GPS API £6K, ETA engine £10K, notification automation £4K, testing £2K)  
**Annual Saving**: £53K  
**Payback**: 7 months

### Wave 2 — Expansion Agents (Compounding on Wave 1)

**Agent 1**: Unattended Address Agent (DE-4)
**Purpose**: Manage unattended delivery addresses (recipient unavailable)
**Volume**: 45 cases/day
**Delegation Archetype**: Agent-led + Oversight

**Reuses from Wave 1**:
- ✅ CRM API integration (customer preferences, order details)
- ✅ Driver app GPS API (delivery confirmation, route impact)
- ✅ SMS/Email notification automation (customer communication)
- ✅ Agent monitoring infrastructure

**New Integrations** (Marginal Build):
- Safe place authority rules (CRM field lookup + policy logic)
- Re-delivery scheduling API (CRM appointment booking)

**Marginal Build Cost**: £15K (inherits £14K of Wave 1 assets → 48% cost reduction [Ref: A028])  
**Build Timeline**: Month 4-5

---

**Agent 2**: Additional Pickup Request Agent (DA-1)
**Purpose**: Process mid-route additional pickup requests
**Volume**: 36 cases/day
**Delegation Archetype**: Agent-led + Oversight

**Reuses from Wave 1**:
- ✅ CRM API integration (customer pickup details)
- ✅ Driver app GPS API (driver locations, current load)
- ✅ **ETA calculation engine** (pickup timing, route impact)
- ✅ **Historical timing database** (route feasibility assessment)
- ✅ SMS/Email notification automation
- ✅ Agent monitoring infrastructure

**New Integrations** (Marginal Build):
- Vehicle capacity integration (driver app or dispatch console API [Ref: A004])
- Route calculator (extends ETA engine with multi-stop optimization)
- Approval dashboard (human-in-loop for dispatch execution)

**Marginal Build Cost**: £20K (inherits £15K of Wave 1 assets → 43% cost reduction)  
**Build Timeline**: Month 5-6 (or deferred if dispatch console API unresolved [Ref: A033])

### Wave 3 — Agent Support Agents (Conditional, Months 19-24)

**Agent 3**: Refused Delivery Agent (DE-1)
**Purpose**: Resolve refused deliveries (damage, incorrect consignment, disputes)
**Volume**: 54 cases/day
**Delegation Archetype**: Human-led + Agent Support

**Reuses from Wave 1**:
- ✅ CRM API integration
- ✅ Driver app GPS API (driver reports, route impact)
- ✅ SMS/Email notification automation
- ✅ Agent monitoring infrastructure

**Reuses from Wave 2**:
- ✅ Re-delivery scheduling (from DE-4)

**New Integrations** (Marginal Build):
- NLP classification engine (refusal reason extraction from driver narratives)
- Decision tree framework (refused delivery disposition logic [Ref: A005])
- Customer priority system (tier-based escalation rules [Ref: A009])

**Marginal Build Cost**: £25K (inherits £18K of Wave 1-2 assets → 42% cost reduction)  
**Conditional on**: Decision rules formalization in Wave 2 prep [Ref: A035, A036]

---

**Agent 4**: Damaged Consignment Agent (DE-2)
**Purpose**: Handle damage reports, assess liability, recommend credits
**Volume**: 36 cases/day
**Delegation Archetype**: Human-led + Agent Support

**Reuses from Wave 1**:
- ✅ CRM API integration
- ✅ Driver app GPS API (photo upload)
- ✅ SMS/Email notification automation
- ✅ Agent monitoring infrastructure

**Reuses from Wave 3**:
- ✅ NLP classification engine (damage description parsing)
- ✅ Customer priority system

**New Integrations** (Marginal Build):
- Image recognition model (damage severity assessment from photos)
- Liability decision tree (transit vs. packaging fault [Ref: A017])
- Aurum billing integration (credit request workflow [Ref: A007])

**Marginal Build Cost**: £35K (inherits £15K of Wave 1-3 assets → 30% cost reduction)  
**Conditional on**: Liability criteria formalization + image model training (6-12 months [Ref: A035, A036])

---

**Agent 5**: Route Diversion Agent (DA-2)
**Purpose**: Assess route diversion requests, recommend approve/reject
**Volume**: 27 cases/day
**Delegation Archetype**: Human-led + Agent Support

**Reuses from Wave 1**:
- ✅ CRM API integration
- ✅ Driver app GPS API
- ✅ **ETA calculation engine** (route impact assessment)
- ✅ **Historical timing database** (delay propagation calculation)
- ✅ SMS/Email notification automation
- ✅ Agent monitoring infrastructure

**Reuses from Wave 2**:
- ✅ Route calculator (from DA-1)

**Reuses from Wave 3**:
- ✅ Customer priority system (delay tolerance by tier)

**New Integrations** (Marginal Build):
- Traffic API integration (real-time congestion data)
- Diversion decision rules (impact thresholds, customer priority logic [Ref: A019])

**Marginal Build Cost**: £22K (inherits £20K of Wave 1-3 assets → 48% cost reduction)  
**Conditional on**: Decision rules formalization, dispatch console API resolution [Ref: A035, A036]

### Integration Reuse Matrix

| Integration / Asset | Wave 1 (DE-3) | Wave 2a (DE-4) | Wave 2b (DA-1) | Wave 3a (DE-1) | Wave 3b (DE-2) | Wave 3c (DA-2) | Notes |
|---------------------|---------------|----------------|----------------|----------------|----------------|----------------|-------|
| **CRM API (Salesforce)** | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | Shared OAuth client, rate limit management |
| **Driver App GPS API** | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | Shared API key, caching strategy |
| **ETA Calculation Engine** | ✓ Build | ✓ Reuse | ✓ Reuse | | | ✓ Reuse | Core algorithm reusable for pickup timing, route impact |
| **Historical Timing DB** | ✓ Build | | ✓ Reuse | | | ✓ Reuse | Nightly ETL from driver app logs |
| **SMS/Email Notification** | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | Shared gateway, template engine |
| **Agent Monitoring** | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | ✓ Reuse | Platform-level (token, API, escalations) |
| **Re-Delivery Scheduling** | | ✓ Build | | ✓ Reuse | | | CRM appointment booking API |
| **Vehicle Capacity API** | | | ✓ Build | | | | Driver app or dispatch console [A004] |
| **Route Calculator** | | | ✓ Build | | | ✓ Reuse | Multi-stop optimization (extends ETA engine) |
| **Approval Dashboard** | | | ✓ Build | | | | Human-in-loop queue for dispatch execution |
| **NLP Classification** | | | | ✓ Build | ✓ Reuse | | Refusal/damage reason extraction |
| **Decision Tree Framework** | | | | ✓ Build | ✓ Reuse | ✓ Reuse | Formalized rules engine [A005, A017, A019] |
| **Customer Priority System** | | | | ✓ Build | ✓ Reuse | ✓ Reuse | Tier-based escalation [A009] |
| **Image Recognition** | | | | | ✓ Build | | Damage assessment (6-12 month training) |
| **Aurum Billing API** | | | | | ✓ Build | | Credit workflow [A007] |
| **Traffic API** | | | | | | ✓ Build | Real-time congestion (optional Wave 1, planned Wave 3) |

**Compounding Metric**: 
- Wave 1: 100% new build (£30K for 6 integrations)
- Wave 2a (DE-4): 79% reuse (£15K for 2 new integrations, reuses 4 from Wave 1)
- Wave 2b (DA-1): 75% reuse (£20K for 3 new integrations, reuses 6 from Wave 1)
- Wave 3a (DE-1): 72% reuse (£25K for 3 new integrations, reuses 8 from Wave 1-2)
- **Average Wave 2-3 reuse: 75%** → validates 40-50% marginal cost reduction estimate [Ref: A028]

### Platform Value Proposition

**Scenario 1**: Build all 6 agents standalone (no reuse)
- Total build cost: £30K + £27K + £35K + £42K + £52K + £46K = **£232K**

**Scenario 2**: Build with compounding (Wave 1 → Wave 2 → Wave 3)
- Total build cost: £30K + £15K + £20K + £25K + £35K + £22K = **£147K**
- **Savings: £85K (37% reduction)**

**Key Insight**: Platform value is not just in individual agent ROI, but in **reducing the marginal cost of future agents**. Every shared integration built in Wave 1 amplifies Wave 2-3 by eliminating redundant build effort.

**Strategic Recommendation** (from Phase 4 [Ref: A041]): Maximize platform ROI by reusing Wave 1 assets across **highest-ROI work streams** (ETA inquiries 400/day full automation, billing disputes 60/day), not just original 7 JtDs if Wave 3 economics remain marginal.

---

## Document Control

- **Created**: 2026-05-06
- **Version**: 1.0
- **Agent**: ETA Investigation Agent (DE-3)
- **Owner**: AI FDE Team
- **Related Documents**:
  - `1-cognitive-load-map.md` - Source JtD (DE-3) and micro-tasks
  - `2-delegation-suitability-matrix.md` - Archetype assignment (Fully Agentic)
  - `3-volume-x-value-analysis.md` - Prioritization (Rank #1, Wave 1 pilot)
  - `5-system-data-inventory.md` - Detailed system and data specifications
  - `assumptions.md` - All assumptions referenced with [Ref: A###]
- **Next Steps**: 
  - System and Data Inventory (detailed API specs, data schemas)
  - Agent Mapping for DE-4 (Wave 1 expansion)
  - Build sprint planning for Wave 1 pilot
