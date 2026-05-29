# Apex Distribution — Assumptions Register

**Phase:** Cognitive Load Mapping  
**Last updated:** 2026-05-11

---

## ID Schema

`A-[WS]-[SEQ]` where WS = workstream code: **GEN** (cross-cutting), **DE** (delivery exceptions), **ETA** (ETA inquiries), **DA** (dispatch adjustments), **BD** (billing disputes).

---

## Cross-Cutting Assumptions

| ID | Assumption | Confidence | Impact if Wrong | Source |
|----|-----------|------------|-----------------|--------|
| A-GEN-01 | 35 agents handle all 4 streams collectively (no dedicated stream teams) | Medium | Interruption patterns, cognitive switching cost, and JtD ownership differ significantly | Scenario text |
| A-GEN-02 | Volume figures (180/400/90/60/day) are weekday averages; actual variance ±30% | Medium | Capacity and latency constraints need recalibration at peak | Not stated |
| A-GEN-03 | Avg handling times (12/4/18/28 min) include all micro-tasks from triage to documentation | High | Automation ROI and task decomposition ratios shift | Implied by framing |
| A-GEN-04 | Salesforce CRM is the system of record for all customer-facing communications across all 4 streams | High | Integration architecture changes significantly | Scenario tooling section |
| A-GEN-05 | B2B and DTC deliveries follow the same exception handling process (no dedicated B2B track) | Low | DE and ETA streams would need separate cognitive maps per segment | Not distinguished in scenario |
| A-GEN-06 | The Driver App is the primary driver-to-dispatch channel; phone calls are an informal fallback, not a secondary official channel | Medium | Breakpoint BP2 (driver data retrieval) is more fragile and asynchronous than assumed | Artefact 1: driver calls dispatch on phone, not through app |
| A-GEN-07 | Shift hours are standard UK business hours (08:00–18:00 GMT); Aurum batch data is available before shift start | Medium | If agents start before 04:00 or batch runs late, billing data availability changes | Not stated |
| A-GEN-08 | Sarah Whitmore has final authority on automation scope; no separate IT governance body blocks or delays deployment | Low | Governance approval workflow could extend implementation timeline by months | Scenario: 2 prior failed initiatives |

---

## Delivery Exceptions (DE)

| ID | Assumption | Confidence | Impact if Wrong | Source |
|----|-----------|------------|-----------------|--------|
| A-DE-01 | "Dispatcher discretion" means individual agents make final resolution decisions without a required approval step in normal cases | High | Escalation rate and HITL design changes; automation boundary shifts inward | Scenario: "Dispatcher discretion drives most decisions" |
| A-DE-02 | Duty Manager escalation (consignments >£500) is infrequent (<5% of exceptions); no data on actual rate | Low | Escalation path cognitive load is underweighted in the micro-task table | SOP 4.2 |
| A-DE-03 | The incomplete SOP section 4.3 (damaged consignments "TBD") means agents improvise; no de facto protocol exists | High | Cognitive load on DE-MT5/DE-MT6 is understated; agent judgment replaces documented rule | Artefact 4: "Section incomplete — TBD" |
| A-DE-04 | Driver App messages are asynchronous (push notification, not real-time chat); voice calls are used when time pressure is acute | Medium | Latency constraint for DE-MT7 (driver communication) changes from M to H | Artefact 1: driver leaves voicemail, does not use app |
| A-DE-05 | Approximately 15–20% of delivery exceptions involve damage elements that create a downstream billing dispute (DE↔BD overlap) | Low | JtD boundary between DE and BD needs an explicit handoff protocol; volume overlap affects DE avg handling time | Artefacts 1+2 suggest linkage |

---

## ETA Inquiries (ETA)

| ID | Assumption | Confidence | Impact if Wrong | Source |
|----|-----------|------------|-----------------|--------|
| A-ETA-01 | GPS data in the Driver App refreshes every 5–15 minutes; the 26-minute stale reading in Artefact 3 is representative, not exceptional | High | Real-time ETA accuracy is structurally limited; automation of ETA-MT4 must account for data staleness | Artefact 3: last GPS ping 10:48, inquiry at 11:14 |
| A-ETA-02 | Approximately 10–15% of ETA inquiries require a driver call (edge cases referenced in the scenario) | Medium | Volume × turn-taking calculation for ETA stream shifts; agent capacity for ETA is understated | Scenario: "edge cases requiring driver call" |
| A-ETA-03 | "Where is my order" is the dominant inquiry intent; rescheduling, access instructions, and multi-order queries are handled as separate case types | Medium | Intent recognition complexity increases if mixed intents are common | Not stated |

---

## Dispatch Adjustments (DA)

| ID | Assumption | Confidence | Impact if Wrong | Source |
|----|-----------|------------|-----------------|--------|
| A-DA-01 | Dispatch adjustments are primarily inbound requests (from customers or operations); they are not proactively system-triggered | Medium | Trigger ownership and DA-MT1 design change if the system initiates adjustments | Not explicitly stated |
| A-DA-02 | The dispatch console (Java/Citrix) requires fully manual input for route changes; no API or scripted automation currently exists for writes | High | Tool availability score for DA-MT5 changes; current state is human-only for execution | Scenario: "Limited API surface" |
| A-DA-03 | Downstream ripple-effect assessment (which subsequent drops are affected by a diversion or driver swap) is done mentally by dispatchers; no decision-support tool exists | High | DA-MT3 is the highest-value automation candidate; without tool support it is pure tacit judgment | Inferred from "limited API surface" and no DSS mentioned |
| A-DA-04 | The 18-min average masks significant variance: simple driver swaps may resolve in ~5 min; complex multi-drop diversions may take 30+ min | Medium | A single avg handling time is misleading for automation sizing; scoring should weight the high-complexity tail | Not stated |

---

## Billing Disputes (BD)

| ID | Assumption | Confidence | Impact if Wrong | Source |
|----|-----------|------------|-----------------|--------|
| A-BD-01 | Manual credit overrides (as in Artefact 2) are a common workaround, not an edge case; agents apply small credits informally to avoid the 48h Aurum ticket process | High | Risk exposure and audit trail gaps are systemic; compliance risk score rises materially | Artefact 2: Sandra's £170 credit with no audit log entry |
| A-BD-02 | Fuel surcharges cannot be adjusted at the line-item level without an Aurum support ticket (48h); the goodwill credit workaround is the only expedient resolution path | High | BD-MT6 and BD-MT7 decision logic depends on this structural constraint | Artefact 2: billing team message; Artefact 5 batch schema |
| A-BD-03 | Aurum schema changes ~quarterly without advance notice; this is the primary cause of the prior RPA failure | High | Any automation touching Aurum batch CSV must be schema-change-resilient; brittle parsing is an anti-pattern here | Scenario: "an RPA project for billing reconciliation that broke whenever Aurum's schema changed" |
| A-BD-04 | The APEX_CREDITS_YYYYMMDD.csv export does not capture credits applied via manual override outside Aurum's standard credit workflow | High | Reconciliation gap between credits applied and credits logged is larger than the batch files suggest | Artefact 2: "no entry in the credits audit log" |
| A-BD-05 | Approximately 25–35% of billing disputes involve a fuel surcharge on a damaged or refused delivery (DE↔BD overlap) | Low | BD volume tied to delivery quality is a shared root cause; siloed handling inflates total case volume | Artefact 2 as single data point |
| A-BD-06 | The 28-min avg handling time reflects elapsed agent effort across the full dispute lifecycle, not per-session time; individual contacts may be <5 min but the case spans multiple days | Medium | Agent effort and elapsed resolution time must be disaggregated; automation opportunity differs for each | Artefact 2: 9-day thread, 4 messages |
