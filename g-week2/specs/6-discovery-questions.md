# Discovery Questions — DE-3 (ETA Investigation Agent)

**Purpose**: Validate or challenge core design decisions made during Agent Mapping. Each question targets a specific assumption that, if answered differently, would require rework of the agent specification.

---

## 1. Prior Automation Attempts
**Question**: Has Apex Distribution previously attempted automated ETA communication (SMS/email to customers) for delivery delays? If yes, what failed and why was it discontinued?

**Design Impact**: 
- If customers complained about tone/accuracy → add human review to all customer-facing messages (changes autonomy matrix from "Agent Decides Alone" to "Agent Proposes, Human Approves" for communication tasks)
- If system accuracy was poor (<70%) → increases confidence threshold requirement to 85%+, adds more escalation triggers
- If no attempt was made → validates greenfield approach

**Assumption Challenged**: [A042] 95% accuracy target, [A043] 90% customer satisfaction, customer communication autonomy

---

## 2. Sandra's Tacit Knowledge Extraction
**Question**: Walk me through the last 3 times Sandra overrode the Dispatch Console's ETA estimate. What data did she look at that the system doesn't capture? What rules does she apply that aren't documented in SOP v2.3?

**Design Impact**:
- If Sandra uses undocumented data sources (e.g., verbal driver check-ins, weather conditions, traffic patterns by time-of-day) → requires additional API integrations or changes ETA calculation logic to include qualitative factors
- If rules are codifiable → add to decision logic (changes Procedural Memory design)
- If rules are intuition-based → increases HITL rate estimate from 10% to 20-30%, changes economics

**Assumption Challenged**: [A006] Sandra's expertise can be encoded, [A027] 10% HITL rate, ETA calculation logic sufficiency

---

## 3. Driver App API Availability (Go/No-Go)
**Question**: Does the Driver App expose a REST API for real-time GPS location and delivery status? If not, what is the data refresh rate of GPS data in the Dispatch Console, and is it sufficient for ±30 min ETA accuracy?

**Design Impact**:
- If no API exists and Dispatch Console refresh >15 min → project blocked, requires Driver App development (3-6 month delay) or acceptance of lower accuracy (±60 min)
- If API exists but rate-limited → changes polling frequency design, may require webhook architecture
- If Dispatch Console refresh <5 min → removes Driver App API dependency entirely, simplifies integration

**Assumption Challenged**: [A003] Driver App has API, [A053] API availability, [A042] ±30 min accuracy achievable

---

## 4. Customer ETA Tolerance (Actual Business Need)
**Question**: What is the current customer complaint rate for "missed delivery windows," and what ETA precision would meaningfully reduce complaints? Is ±30 minutes acceptable, or do high-priority customers (e.g., medical supplies) require ±15 minutes?

**Design Impact**:
- If high-priority customers need ±15 min → requires real-time traffic API (not optional), changes from £256/year to mandatory cost, may require driver behavior prediction model
- If ±60 min is sufficient → relaxes accuracy target, reduces escalation triggers, simplifies ETA engine
- If complaint rate is <5% → questions ROI, may deprioritize this JtD

**Assumption Challenged**: [A042] ±30 min target, [A043] 90% satisfaction improvement, prioritization of DE-3 in Wave 1

---

## 5. GPS Reliability in Practice
**Question**: In the last 30 days, what percentage of active deliveries had GPS data that was >30 minutes stale? What are the common causes (driver disabling app, connectivity dead zones, device issues)?

**Design Impact**:
- If >20% of cases have stale GPS → 30 min staleness threshold too optimistic, requires fallback ETA logic based on last known location + historical timing, increases HITL escalations
- If <5% stale GPS → validates threshold, may even tighten to 15 min
- If specific routes/areas have systematic GPS issues → adds geographic escalation trigger

**Assumption Challenged**: [A045] 30 min GPS staleness threshold, [A027] 10% HITL rate, feasibility of real-time ETA

---

## 6. Customer Communication History
**Question**: Have customers ever received automated SMS/email updates from Apex Distribution (e.g., dispatch confirmations, delivery notifications)? If yes, what was the response rate, complaint rate, and customer feedback on tone/usefulness?

**Design Impact**:
- If prior automated comms had negative feedback → requires brand voice guidelines, human review of all messages (changes autonomy from "Agent Decides Alone" to "Agent Proposes, Human Approves")
- If no automated comms exist → customers may be surprised/confused, requires explicit opt-in flow (adds new task to agent), changes communication design
- If positive history → validates autonomous communication approach

**Assumption Challenged**: Autonomy Matrix Level 1 (customer communication without approval), customer acceptance of agent-generated messages

---

## 7. SLA Breach Definition and Frequency
**Question**: How is "SLA breach" defined for delivery windows (e.g., >30 min late, >1 hour late, any delay)? For high-priority customers, what is the current SLA breach rate, and what are the commercial consequences (refunds, contract penalties)?

**Design Impact**:
- If SLA breach = any delay → all delays require human approval before communication (changes autonomy matrix), increases HITL rate
- If SLA breach = >2 hours late → relaxes escalation trigger from "delay >1 hour" to "delay >2 hours," reduces escalation volume
- If commercial penalties are severe (>£100/breach) → adds mandatory human approval for all high-priority SLA breaches, changes risk assessment from Medium to High

**Assumption Challenged**: Escalation trigger logic (SLA breach definition), risk assessment, autonomy for high-priority customers

---

## 8. Route Plan Complexity
**Question**: What percentage of routes involve dynamic re-sequencing (mid-route adjustments based on traffic, priority changes, additional pickups)? How often does the planned route in the Dispatch Console differ from the actual route driven?

**Design Impact**:
- If >30% of routes change mid-day → static route plan from Dispatch Console insufficient for ETA calculation, requires real-time re-routing logic, adds complexity to ETA engine
- If <10% dynamic changes → validates use of cached route plans (Semantic Memory), simplifies design
- If route sequence is unreliable → ETA calculation must be based on direct distance to customer (not route position), changes algorithm fundamentally

**Assumption Challenged**: ETA calculation based on route plan + historical timing, Semantic Memory caching strategy, [A004] Dispatch Console route plan reliability

---

## 9. Driver Behavior Patterns (Data Trust)
**Question**: Do drivers ever mark deliveries as "completed" before actually delivering (to hit KPIs)? How often do drivers deviate from planned routes without updating the system? What is the error rate of driver-entered data (e.g., "Refused Delivery" reason codes)?

**Design Impact**:
- If drivers game the system (>10% false "completed" marks) → requires cross-validation logic (e.g., GPS proximity check before trusting completion status), adds data validation tasks to agent
- If drivers frequently deviate without updating → GPS is only reliable signal, changes ETA calculation to ignore route plan entirely
- If reason codes are unreliable → agent cannot trust "Refused Delivery" vs. "Missed Window" categorization, requires reclassification logic

**Assumption Challenged**: [A001] JtD volume accuracy (if miscategorized), data quality assumptions, ETA calculation inputs (GPS vs. route plan priority)

---

## 10. Stakeholder Trust Threshold for Autonomous Communication
**Question**: What accuracy rate (e.g., 95%, 99%) would Operations leadership require before allowing the agent to send customer-facing ETA updates *without* human approval? How long of a shadow mode period (weeks, months) is needed to build trust?

**Design Impact**:
- If 99% accuracy required → increases confidence threshold from 70% to 85%, adds more escalation triggers (e.g., new customer, new route), increases HITL rate from 10% to 25%, changes economics (may delay Wave 1)
- If 6+ month shadow mode required → delays ROI timeline, may need to redesign pilot as "ETA recommendation tool" for humans first, then graduate to autonomous communication in Wave 2
- If 90% acceptable → validates current design

**Assumption Challenged**: [A044] 70% confidence threshold, [A027] 10% HITL rate, autonomy matrix design, Wave 1 timeline (Month 3 pilot deployment)

---

## Summary of Design Risks

| Question | Assumption at Risk | Design Change if Answer is Unfavorable |
|----------|-------------------|----------------------------------------|
| 1. Prior Automation | [A042, A043] Accuracy/satisfaction | Add human review to all customer comms |
| 2. Sandra's Rules | [A006, A027] Encodability, HITL | Increase HITL 10%→30%, add data sources |
| 3. Driver App API | [A003, A053] API exists | 3-6 month delay or ±60 min accuracy |
| 4. Customer Tolerance | [A042] ±30 min target | Add traffic API (£256→mandatory) or relax to ±60 min |
| 5. GPS Reliability | [A045] 30 min staleness | Add geographic escalations, fallback ETA logic |
| 6. Comm History | Autonomy Level 1 | Require approval before customer comms |
| 7. SLA Breach | Escalation triggers | Relax/tighten triggers, add mandatory approvals |
| 8. Route Complexity | [A004] Route plan use | Redesign ETA engine (direct distance, not route) |
| 9. Driver Behavior | [A001] Volume accuracy, data quality | Add cross-validation logic, GPS proximity checks |
| 10. Trust Threshold | [A044, A027] Confidence 70%, HITL 10% | Increase to 85% confidence, 25% HITL, 6-mo shadow |

**Next Step**: Week 1 stakeholder interviews (Sandra, Operations Manager, 2-3 drivers, Customer Service Lead) to answer these 10 questions before finalizing build sprint plan.
