# Cognitive Load Map — HR Onboarding Coordination
**Aldridge & Sykes Professional Services**

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Lived Process Overview](#lived-process-overview)
3. [Work Stream Decomposition](#work-stream-decomposition)
   - [Work Stream 1: New-Hire System & Access Setup](#work-stream-1-new-hire-system--access-setup)
   - [Work Stream 2: Compliance Training Assignment & Tracking](#work-stream-2-compliance-training-assignment--tracking)
   - [Work Stream 3: Buddy Matching & Welcome Cadence](#work-stream-3-buddy-matching--welcome-cadence)
   - [Work Stream 4: Edge-Case Resolution](#work-stream-4-edge-case-resolution)
4. [Cognitive Zone Mapping](#cognitive-zone-mapping)
5. [Breakpoint Analysis](#breakpoint-analysis)
6. [Micro-Task Inventory](#micro-task-inventory)
7. [Key Findings](#key-findings)

---

## Executive Summary

**Context**: 3-person HR Ops team at Aldridge & Sykes (1,200 employees, 220+ hires/year) managing onboarding across 4 work streams. CFO-directed AI exploration triggered by consulting division complaints about onboarding delays.

**Key finding**: Dual-tracking system (Excel Master Tracker as lived system of record, Workday as documented system) creates 20-30% overhead [A26]. Cognitive load concentrates in exception detection, stakeholder management, and hidden decision context (risk flags, buddy overrides, VIP handling) not captured in documented processes [A15].

**Primary cognitive bottleneck**: Manual monitoring and status translation across 2-week onboarding window with ~20-25 touchpoints per hire [A02].

**Delegation opportunity**: Routine monitoring, status updates, and compliance chasing (55-60% of volume) are agent-suitable with human oversight for VIP cases and edge-case escalation.

---

## Lived Process Overview

### What the SOP says
Standard onboarding follows documented Workday-centric workflow: hire data entry → system provisioning requests → compliance assignment → buddy matching.

### What actually happens
1. **Priya's Excel tracker is system of record** — updated daily; Workday refreshed end-of-week [A13]
2. **Dual status tracking** — "Workday status" (system state) vs "Visible status" (stakeholder-facing) [A14]
3. **Hidden decision columns** — Notes, Risk flags, Buddy overrides contain tacit knowledge not in Workday [A15]
4. **ServiceNow routing gaps** — Auto-routing fails for non-standard specs (e.g., consulting laptop) [A08, A25]
5. **Compliance flowchart stale** — 18+ months old; TEMP-EXT role code retired but not updated [A17]
6. **VIP hire special handling** — Director hires from competitors get accelerated tracking and custom buddy pairing [A30]

### Artefact evidence
- **Artefact 1.1** — 5-day email escalation for Tom Reeves (senior consulting hire from Deloitte) due to ServiceNow routing failure
- **Artefact 1.2** — Master Tracker excerpt showing hidden decision context (risk flags, buddy overrides, edge-case notes)
- **Artefact 1.3** — Compliance Training Routing Flowchart v4.2 with pencilled note about retired role code

### Process topology
```
[Hire confirmed] 
  → [Workday record creation] 
  → [Excel tracker entry + risk assessment] **BREAKPOINT: Human judgment**
  → [IT/badge/access requests] 
  → [Compliance routing] 
  → [Buddy assignment + override check] **BREAKPOINT: VIP detection**
  → [30-day monitoring cadence] **ZONE: 20-25 touchpoints over 2 weeks**
  → [Exception detection + escalation] **BREAKPOINT: Edge case triage**
```

---

## Work Stream Decomposition

### Work Stream 1: New-Hire System & Access Setup

**Volume**: ~190 cases/year  
**Duration**: ~3 hours effective handling spread across 2 weeks [A02]  
**Actors**: HR Coordinators (initial setup), Priya (monitoring + escalations), IT (ticket fulfillment)

#### Job to be Done 1.1: Establish hire record and track provisioning

**Trigger**: Hire confirmed in recruiting system  
**Goal**: Workday record active, all access requests submitted and tracked  
**Key decisions**:
- Hire type classification (FTE vs contractor vs secondment vs returning hire) [A19]
- System access entitlements based on role/division/location
- ServiceNow ticket spec validation (to avoid Tom Reeves routing failure) [A25]
- Risk flag assignment (VIP hire? Sensitive timeline?) [A15, A30]

**Key systems**: Workday, ServiceNow, Badge system [A20], Excel Master Tracker  
**Expected output**: Workday record created, ServiceNow ticket(s) submitted, tracker entry with risk flag  
**Cognitive type**: Execution + monitoring + exception detection

**Micro-tasks**:
1. Extract hire data from recruiting handoff
2. Validate hire type against Workday taxonomy (watch for contractor→FTE, returning hire edge cases) [A18, A19]
3. Create Workday record
4. Generate IT access request (laptop, email, systems)
5. Validate laptop spec against division requirements (consulting vs audit vs tax)
6. Submit ServiceNow ticket with correct routing
7. Order badge and building access
8. Create tracker entry with dual status
9. Flag VIP hires for special handling [A30]
10. Monitor ticket progress 3x/week for 2 weeks
11. Escalate delays (e.g., Tom Reeves scenario)

#### Job to be Done 1.2: Coordinate payroll and compliance foundations

**Trigger**: Workday record active  
**Goal**: Payroll setup complete, right-to-work verified  
**Key decisions**:
- UK vs Ireland payroll routing [A22]
- Right-to-work verification method (Home Office share-code for UK, passport for Ireland) [A21]

**Key systems**: Workday payroll module, Home Office Employer Checking Service (manual) [A21]  
**Expected output**: Payroll record active, compliance documentation filed  
**Cognitive type**: Execution + regulatory compliance check

**Micro-tasks**:
1. Route payroll setup based on location (UK vs Ireland)
2. Verify right-to-work documentation
3. Escalate missing/expired documents
4. File compliance evidence in Workday

---

### Work Stream 2: Compliance Training Assignment & Tracking

**Volume**: ~220 cases/year  
**Duration**: ~45 minutes per case (assignment + chasing) [A28]  
**Actors**: HR Coordinators (assignment), new hires (completion), HR Ops (chasing)

#### Job to be Done 2.1: Assign correct compliance training path

**Trigger**: Hire start date confirmed  
**Goal**: Correct LMS training pack assigned based on role, country, prior certifications  
**Key decisions**:
- Role code → training path mapping (FTE vs CONS-A,B,C vs CONS-D) [A17]
- UK vs Ireland compliance differences [A22]
- Prior employment certification carryover (especially contractor→FTE conversions) [A18]

**Key systems**: Saba LMS (no API) [A07], Workday (hire data), Compliance flowchart (stale) [A17]  
**Expected output**: Training pack assigned in Saba, hire notified via Outlook  
**Cognitive type**: Rule application + exception handling

**Micro-tasks**:
1. Extract hire type and role code from Workday
2. Map role code to training path using flowchart (watch for retired TEMP-EXT code) [A17]
3. Check for prior certifications (contractor→FTE edge case) [A18]
4. Manually assign training pack in Saba LMS (no API workaround) [A07]
5. Send assignment notification email via Outlook [A09]
6. Log assignment in tracker

#### Job to be Done 2.2: Chase incomplete training and escalate blockers

**Trigger**: Training assigned, deadline approaching  
**Goal**: 100% completion before role-specific work begins  
**Key decisions**:
- When to chase (3 days before deadline? 1 day?)
- When to escalate to manager vs direct reminder

**Key systems**: Saba LMS (manual completion check) [A07], Outlook (chasing communication) [A09]  
**Expected output**: Completion confirmed or escalation triggered  
**Cognitive type**: Monitoring + communication

**Micro-tasks**:
1. Check Saba LMS for completion status (manual) [A07]
2. Send first reminder at T-3 days
3. Send second reminder at T-1 day
4. Escalate to hiring manager if incomplete at deadline
5. Update tracker with completion status

---

### Work Stream 3: Buddy Matching & Welcome Cadence

**Volume**: ~220 cases/year  
**Duration**: ~30 minutes initial + ~60 minutes across first 30 days [A27]  
**Actors**: HR Coordinators (matching), buddies (execution), Priya (override decisions)

#### Job to be Done 3.1: Match new hire with appropriate buddy

**Trigger**: Hire confirmed, start date set  
**Goal**: Buddy assigned per policy OR override applied with rationale  
**Key decisions**:
- Standard rule application (peer level, same division, prior buddy experience)
- Override criteria (VIP hire? Special circumstances?) [A16]
- Buddy availability and capacity

**Key systems**: Excel tracker (buddy capacity tracking), SharePoint (buddy policy), Outlook (buddy notification)  
**Expected output**: Buddy assigned, both parties notified, override logged if applicable [A15, A16]  
**Cognitive type**: Rule application + judgment (overrides)

**Micro-tasks**:
1. Extract hire profile (division, seniority, location)
2. Apply standard matching rules
3. Check buddy availability and prior assignment load
4. Detect VIP hire flag → escalate to Priya for override decision [A16, A30]
5. Log buddy assignment in tracker (including override rationale if applicable) [A15]
6. Notify buddy and new hire via Outlook

#### Job to be Done 3.2: Orchestrate 30-day welcome cadence

**Trigger**: Buddy assigned  
**Goal**: Day 1, Day 7, Day 14, Day 30 touchpoints completed [A27]  
**Key decisions**:
- Scheduling adjustments for PTO, sick leave
- Escalation if touchpoint missed

**Key systems**: Outlook (calendar holds + reminders), Excel tracker (cadence monitoring)  
**Expected output**: All touchpoints completed, manager handoff executed  
**Cognitive type**: Scheduling + monitoring

**Micro-tasks**:
1. Schedule Day 1 buddy intro (calendar hold)
2. Schedule Day 7 check-in
3. Schedule Day 14 check-in
4. Schedule Day 30 check-in + manager handoff
5. Monitor completion (3x/week check)
6. Send reminders if touchpoint missed
7. Escalate pattern of missed touchpoints

---

### Work Stream 4: Edge-Case Resolution

**Volume**: ~30-50 cases/year (15-25% of hires) [A04]  
**Duration**: ~4 hours per case, unpredictable [A05]  
**Actors**: Priya (triage + resolution), HR Coordinators (data gathering), IT/Legal/Payroll (specialist support)

#### Job to be Done 4.1: Detect and triage edge cases

**Trigger**: Red flag in standard workflow (e.g., frozen Workday record, missing docs, visa expiry)  
**Goal**: Edge case classified, resolution path identified  
**Key decisions**:
- What type of edge case? (right-to-work, frozen record, contractor→FTE, rehire, visa)
- Who owns resolution? (HR, IT, Legal, manager)
- Timeline sensitivity? (start date at risk?)

**Key systems**: Workday (error signals), Excel tracker (risk flags), Home Office portal (right-to-work) [A21]  
**Expected output**: Edge case logged with classification, owner assigned, timeline flagged  
**Cognitive type**: Diagnosis + escalation routing

**Micro-tasks**:
1. Detect edge case signal (Workday error, missing doc, expired credential)
2. Classify edge case type [A04]
3. Assess timeline risk (start date impact)
4. Route to specialist (IT for frozen records, Legal for visa, manager for reference checks)
5. Log in tracker with Red risk flag [A15]
6. Notify stakeholders (hiring manager, director if VIP) [A29, A30]

#### Job to be Done 4.2: Coordinate edge-case resolution

**Trigger**: Edge case logged  
**Goal**: Resolution completed, hire onboarding resumes or start date adjusted  
**Key decisions**:
- Escalation timing (when to involve director/CFO)
- Workaround acceptability (e.g., loaner laptop)
- Start date delay vs workaround

**Key systems**: Email (coordination), Workday (record correction), ServiceNow (ticket re-routing)  
**Expected output**: Edge case resolved, hire status updated, stakeholders notified  
**Cognitive type**: Coordination + negotiation + judgment

**Micro-tasks**:
1. Gather missing data/documents
2. Coordinate with specialist teams (IT, Legal, Payroll)
3. Negotiate workarounds if needed (e.g., Tom Reeves loaner laptop) [Artefact 1.1]
4. Decide escalation threshold (when to involve director/CFO) [A29]
5. Update Workday and tracker
6. Communicate resolution to all parties

---

## Cognitive Zone Mapping

### Zone 1: Data Intake & Validation
**Activities**: Extract hire data, validate hire type, check for edge-case signals  
**Cognitive demand**: Low (structured data, clear rules)  
**Data dependencies**: Workday, recruiting handoff  
**Error tolerance**: Low (misclassification creates downstream failures)  
**Latency constraint**: <1 day from hire confirmation

### Zone 2: System Provisioning Orchestration
**Activities**: Generate access requests, submit tickets, validate routing  
**Cognitive demand**: Medium (requires spec validation, routing logic)  
**Data dependencies**: Workday, ServiceNow, badge system [A20]  
**Error tolerance**: Medium (delays are visible but correctable, e.g., Tom Reeves)  
**Latency constraint**: Same-day submission preferred; 2-week monitoring window

### Zone 3: Compliance Routing & Chasing
**Activities**: Map role→training path, assign in Saba LMS, chase completion  
**Cognitive demand**: Medium (rules + exceptions, manual Saba interaction) [A07]  
**Data dependencies**: Workday, Saba LMS (no API), compliance flowchart (stale) [A17]  
**Error tolerance**: Low (incorrect training = compliance violation)  
**Latency constraint**: Must complete before role-specific work begins

### Zone 4: Relationship Coordination (Buddy Matching)
**Activities**: Buddy selection, override decisions, cadence scheduling  
**Cognitive demand**: Medium-High (judgment for overrides, VIP detection) [A16, A30]  
**Data dependencies**: Buddy availability tracker, hire profile, VIP flags [A15]  
**Error tolerance**: Medium (poor match impacts experience but correctable)  
**Latency constraint**: Buddy assigned before Day 1; cadence across 30 days

### Zone 5: Exception Detection & Escalation
**Activities**: Monitor for red flags, triage edge cases, coordinate resolution  
**Cognitive demand**: High (requires diagnosis, judgment, stakeholder management) [A05]  
**Data dependencies**: All systems, historical edge-case patterns  
**Error tolerance**: Very Low (missed edge case can delay start date, trigger CFO escalation) [A29]  
**Latency constraint**: Immediate detection required; resolution timeline varies

### Zone 6: Stakeholder Communication & Status Translation
**Activities**: Dual status tracking, VIP escalation, progress reporting  
**Cognitive demand**: High (requires translating system state to stakeholder expectations) [A14]  
**Data dependencies**: Excel tracker, email threads, risk flags [A15]  
**Error tolerance**: Low (communication gaps create political risk) [A11, A29]  
**Latency constraint**: Real-time for VIP cases; daily for standard cases

---

## Breakpoint Analysis

### Breakpoint 1: Hire Confirmation → Workday Record Creation
**Type**: Human → System  
**Control shift**: Recruiting data → structured HR system  
**Risk**: Hire type misclassification (contractor vs FTE, returning hire) [A19]  
**Delegation suitability**: High (rule-based with edge-case detection)

### Breakpoint 2: System Provisioning → ServiceNow Ticket Submission
**Type**: System → System (with validation)  
**Control shift**: Workday data → IT ticket system  
**Risk**: Routing failure due to spec drift (Tom Reeves laptop issue) [A08, A25]  
**Delegation suitability**: Medium (requires spec validation logic; agent-led with human review)

### Breakpoint 3: Standard Buddy Match → VIP Override Decision
**Type**: Rule → Judgment  
**Control shift**: Policy-based matching → Priya's override [A16]  
**Risk**: VIP hire dissatisfaction if standard rule applied [A30]  
**Delegation suitability**: Low (requires human judgment; agent can flag for human decision)

### Breakpoint 4: Routine Monitoring → Edge-Case Detection
**Type**: Execution → Diagnosis  
**Control shift**: Checklist monitoring → problem-solving [A05]  
**Risk**: Missed edge case delays start date, triggers CFO escalation [A29]  
**Delegation suitability**: Medium (agent can detect patterns, must escalate to human for resolution)

### Breakpoint 5: System Status → Stakeholder-Facing Status
**Type**: System → Human (translation)  
**Control shift**: Workday state → "Visible status" for stakeholder communication [A14]  
**Risk**: Misalignment creates confusion, erodes trust [A11]  
**Delegation suitability**: Medium (agent can draft status updates, human reviews for VIP cases)

### Breakpoint 6: Compliance Assignment → Chasing
**Type**: Execution → Communication  
**Control shift**: One-time action → iterative follow-up [A28]  
**Risk**: Incomplete training at deadline  
**Delegation suitability**: High (agent-led chasing with escalation to human if incomplete at deadline)

---

## Micro-Task Inventory

| Micro-Task | Cognitive Load | Input Structure | Decision Determinism | Exception Freq | Turn-Taking | Latency | Risk/Compliance | Tool/API Availability | Delegation Archetype | Assumption Refs |
|------------|----------------|-----------------|----------------------|----------------|-------------|---------|-----------------|----------------------|---------------------|-----------------|
| **WS1: System & Access Setup** |
| Extract hire data from recruiting handoff | L | H (structured) | H (deterministic) | L | L (one-way) | Batch OK | L (reversible) | H (Workday API) | Fully Agentic | A06 |
| Validate hire type (FTE/contractor/returning) | M | M (semi-structured) | M (rules + exceptions) | M (15-25% edge cases) | L | Batch OK | M (impacts downstream) | H | Agent-led + Human Oversight | A04, A18, A19 |
| Create Workday record | L | H | H | L | L | Batch OK | M (data accuracy critical) | H | Fully Agentic | A06 |
| Validate laptop spec against division | M | M (requires reference data) | M (rules + drift detection) | M (Tom Reeves case) | L | Batch OK | M (delays visible) | M (requires spec lookup) | Agent-led + Human Oversight | A08, A25 |
| Submit ServiceNow ticket | L | H | H (after validation) | L | L | Batch OK | L | H (ServiceNow API) | Fully Agentic | - |
| Order badge and building access | L | H | H | L | L | Batch OK | L | M (system unknown) | Agent-led + Human Oversight | A20 |
| Create Excel tracker entry with dual status | M | M | M (requires status translation) | L | L | Daily | M (stakeholder visibility) | L (Excel; could use Sheets API) | Agent-led + Human Oversight | A13, A14 |
| Flag VIP hires for special handling | M | M (requires VIP detection) | M (rules + judgment) | L (5-10% of hires) | L | Real-time | H (political risk) | M (requires VIP criteria) | Human-led + Agent Support | A15, A30 |
| Monitor ticket progress 3x/week | L | H (ServiceNow status) | H | L | L | Batch (3x/week) | L | H | Fully Agentic | - |
| Escalate delays (email stakeholders) | M | M (requires escalation logic) | M (template + context) | M | H (iterative) | Real-time for VIP | H (Tom Reeves → CFO) | H (email integration) | Agent-led + Human Oversight | A09, A29 |
| **WS2: Compliance Training** |
| Map role code → training path | M | M (flowchart + exceptions) | M (stale documentation) | M (retired codes) | L | Batch OK | H (compliance violation risk) | L (Saba no API) | Human-led + Agent Support | A07, A17 |
| Check prior certifications (contractor→FTE) | H | L (manual data reconciliation) | L (judgment required) | M (contractor conversions) | M | Batch OK | H (compliance) | L (data scattered) | Human-led + Agent Support | A18 |
| Manually assign training in Saba LMS | L | H (once path determined) | H | L | L | Batch OK | L | L (no API; UI automation?) | Human-led + Automation Support | A07 |
| Send assignment notification email | L | H (template) | H | L | L | Batch OK | L | H (Outlook) | Fully Agentic | A09 |
| Check Saba LMS for completion (manual) | L | M (requires login + lookup) | H | L | L | Daily | L | L (no API; scraping?) | Human-led + Automation Support | A07 |
| Send chasing reminders (T-3, T-1) | L | H (template + trigger logic) | H | L | M (2-3 rounds) | Batch OK | L | H (Outlook) | Fully Agentic | A09, A28 |
| Escalate incomplete to manager | M | M (requires escalation judgment) | M (template + context) | L | M | Real-time at deadline | M (manager visibility) | H | Agent-led + Human Oversight | - |
| **WS3: Buddy Matching & Welcome Cadence** |
| Apply standard buddy matching rules | M | M (hire profile + buddy availability) | M (rules + capacity constraints) | L | L | Batch OK | L | M (Excel/Sheets tracker) | Agent-led + Human Oversight | - |
| Detect VIP hire → escalate for override | H | M (VIP detection criteria) | L (judgment required) | L (5-10% of hires) | H (requires Priya decision) | Real-time | H (experience risk for VIP) | M (requires VIP flag) | Human-led + Agent Support | A15, A16, A30 |
| Log buddy assignment with override rationale | M | M (structured + free text) | M | L | L | Batch OK | M (audit trail) | L (Excel hidden columns) | Agent-led + Human Oversight | A15 |
| Notify buddy and new hire | L | H (template) | H | L | L | Batch OK | L | H (Outlook) | Fully Agentic | A09 |
| Schedule 30-day cadence touchpoints | M | M (calendar + availability) | M (requires conflict detection) | M (PTO, sick leave) | M | Batch OK | M (missed touchpoint visible) | H (Outlook calendar API) | Agent-led + Human Oversight | A27 |
| Monitor touchpoint completion | L | H (calendar status) | H | L | L | 3x/week | L | H | Fully Agentic | - |
| Send reminders for missed touchpoints | L | H (template) | H | L | M | Real-time | M (manager visibility) | H | Fully Agentic | - |
| **WS4: Edge-Case Resolution** |
| Detect edge-case signal (Workday error, missing doc) | M | M (error patterns + heuristics) | M (pattern recognition) | H (30-50/yr = 15-25%) | L | Real-time | H (start date risk) | M (Workday error logs) | Agent-led + Human Oversight | A04, A05, A19 |
| Classify edge case type | H | L (requires diagnosis) | L (judgment + experience) | H | M | Real-time | H | M (historical pattern data) | Human-led + Agent Support | A04 |
| Assess timeline risk (start date impact) | H | M | L (judgment) | H | M | Real-time | H (CFO escalation if VIP) | M | Human-led + Agent Support | A29, A30 |
| Route to specialist (IT, Legal, Payroll) | M | M (routing rules) | M (rules + exceptions) | M | M | Real-time | M | M (email + assignment) | Agent-led + Human Oversight | - |
| Log in tracker with Red risk flag | M | M | M | L | L | Real-time | H (visibility for Priya) | L (Excel) | Agent-led + Human Oversight | A15 |
| Notify stakeholders (manager, director, CFO) | H | M (requires escalation judgment) | L (political judgment) | M | H (iterative) | Real-time | H (political risk) | H (email) | Human Only | A11, A29, A30 |
| Coordinate edge-case resolution | H | L (unstructured, multi-party) | L (judgment + negotiation) | H | H (high back-and-forth) | Real-time | H (start date impact) | M | Human Only | A05 |
| Negotiate workarounds (e.g., loaner laptop) | H | L | L (judgment) | M | H | Real-time | M | M | Human Only | Artefact 1.1 |
| Decide CFO escalation threshold | H | L (political context) | L (pure judgment) | L | H | Real-time | H (career risk for Priya) | L | Human Only | A11, A29 |

**Legend**:
- **Cognitive Load**: L=Low, M=Medium, H=High
- **Input Structure**: L=Unstructured, M=Semi-structured, H=Structured
- **Decision Determinism**: L=Judgment-dependent, M=Rules with exceptions, H=Deterministic
- **Exception Frequency**: L=Rare (<5%), M=Moderate (5-25%), H=Frequent (>25%)
- **Turn-Taking**: L=One-way, M=2-3 rounds, H=Many rounds
- **Latency**: Batch OK, Daily, Real-time
- **Risk/Compliance**: L=Reversible/low-consequence, M=Visible/moderate, H=Irreversible/high-consequence
- **Tool/API Availability**: L=Manual/no API, M=Partial/workaround, H=Full API available

---

## Key Findings

### 1. Dual-Tracking System Creates 20-30% Overhead
**Evidence**: Artefact 1.2 shows Excel as lived system of record, updated daily; Workday refreshed end-of-week [A13]. Hidden columns (Notes, Risk flags, Buddy overrides) contain decision context not in Workday [A15].

**Implication**: Agent must integrate with Excel (or migrate to structured system) to access real decision context. Workday alone is insufficient for agent effectiveness.

### 2. VIP Hire Detection Is Critical Failure Mode
**Evidence**: Tom Reeves (Deloitte hire) escalated to CFO after 5-day laptop delay [Artefact 1.1]. Tracker shows "Director's hire" note and buddy override [Artefact 1.2].

**Implication**: Agent must flag VIP hires (external senior hires, director-level, competitor poaches) for human oversight [A30]. False negative (treating VIP as standard) = political risk [A11, A29].

### 3. Documentation Lag Creates Silent Failures
**Evidence**: Compliance flowchart 18+ months stale; TEMP-EXT code retired Q1 2024 but flowchart not updated [Artefact 1.3]. ServiceNow routing failed for consulting laptop spec change [Artefact 1.1].

**Implication**: Agent cannot rely on documented processes. Requires validation against current state (spec drift detection, role code reconciliation) [A17, A25].

### 4. Saba LMS "No API" Blocks Full Automation
**Evidence**: Brief explicitly states "no API" for Saba LMS [A07].

**Implication**: Compliance training assignment requires human execution or UI automation workaround. Agent can determine correct path and draft instructions but cannot assign directly.

### 5. Edge-Case Resolution Requires Human Judgment
**Evidence**: 30-50 edge cases/year (15-25% of volume), 4 hours/case, unpredictable [A04, A05]. Examples: frozen Workday records, contractor→FTE conversions, right-to-work issues [Artefact 1.2, A18, A19, A21].

**Implication**: Agent role = early detection + classification + routing. Resolution remains human-led due to diagnosis complexity, multi-party coordination, and political sensitivity.

### 6. 2-Week Monitoring Window Is Automation-Suitable
**Evidence**: 3 hours effective handling spread across 2 weeks implies ~20-25 touchpoints [A02]. Artefact 1.1 shows 5-day email thread for single ticket escalation.

**Implication**: Routine monitoring (ticket status checks, chasing reminders, progress updates) is high-volume, low-judgment work suitable for agent-led execution with human escalation for delays.

### 7. Communication Overhead Is 40-50% of Workload
**Evidence**: "Assignment plus chasing" for compliance training = 45 min [A28]. Email threads for escalation (Tom Reeves 5-day thread). Dual status tracking for stakeholder management [A14].

**Implication**: Agent value proposition = reduce communication overhead via automated chasing, status updates, and stakeholder notifications. Human oversight for VIP cases.
