# Specific Rewrite Suggestions — Week 2 Gate Deliverables

**Purpose:** This document provides exact before/after text for the required changes flagged in the peer review.

---

## CHANGE 1: DELIVERABLE-1 Discovery Question Framing

### Location 1A: Add Disclaimer at Top of Document

**FILE:** `DELIVERABLE-1-DISCOVERY-QUESTIONS.md`  
**LINE:** Insert after line 38 (after the situation summary table, before "## Part 1: The Discovery Questions")

**INSERT THIS TEXT:**

```markdown
---

## ⚠️ IMPORTANT: Simulation Context

The answers below were generated through a structured AI role-play exercise to illustrate the *type* of detail discovery questions should surface. They are **hypotheses to validate**, not confirmed facts.

**Key Points:**
- The actual primary stakeholder at Aldridge & Sykes is **Priya Aggarwal (HR Ops Lead)**, not a COO
- The simulated responses demonstrate what lived-work discovery *should* uncover, but have not been validated with Priya
- Several details in the simulated answers are **not confirmed** by the enriched scenario brief (see list below)
- **Before finalizing the agent spec, schedule an actual discovery interview with Priya to validate these hypotheses**

**Details NOT confirmed in scenario (must validate):**
- iPhone Notes app as I-9 tracker
- Legacy HR system from 2014 (scenario lists only 5 systems: Workday, ServiceNow, Saba LMS, SharePoint, Outlook)
- "Mark in IT" as informal contact
- WhatsApp for urgent escalations
- Connections HR recruiter mislabeling hire_type
- Strategy/Finance buddy exclusion rule

**Details CONFIRMED in enriched scenario:**
- Priya's Excel tracker on OneDrive (Artefact 1.2)
- TEMP-EXT hire type retired Q1 2024 (Artefact 1.3)
- CFO involvement (not COO)

**Use of these answers:** Treat each simulated response as a *design hypothesis* that shapes what to ask in the real discovery interview, not as validated design inputs.

---
```

---

### Location 1B: Retitle All Question Answer Sections (6 instances)

**FILE:** `DELIVERABLE-1-DISCOVERY-QUESTIONS.md`  
**LINES:** 59, 79, 99, 119, 139, 162

**FIND (appears 6 times):**
```markdown
**The COO's answer:**
```

**REPLACE WITH:**
```markdown
**Simulated Response (Validation Required):**
```

---

### Location 1C: Update "What Must Be Resolved Before Building" Section

**FILE:** `DELIVERABLE-1-DISCOVERY-QUESTIONS.md`  
**LINE:** 227 (section header "## Part 4: What Must Be Resolved Before Building")

**CURRENT TEXT (lines 227-239):**
```markdown
## What Must Be Resolved Before Building

Three things must be in place before the agent can do its job reliably. Without them, the agent will have less operational knowledge than Priya already has:

**1. Acquire Priya's Excel tracker and make it the schema baseline.**  
The tracker is the real mental model of the work. Every column it has that Workday doesn't is a gap the agent must fill. Get the file, document its schema, and treat it as the primary design input — not the SOP.

**2. Establish the escalation channel with the actual decision-makers.**  
Teams or SMS for anything with a response SLA under 2 hours. This requires IT provisioning of the integration and confirmation from the COO and HR Manager that they will respond to that channel. Without this, the I-9 SLA is structurally unachievable.

**3. Formally document every undocumented rule before launch.**  
The Connections HR hire_type issue, the Strategy/Finance buddy exclusion, Priya's compliance matrix corrections — none of these are encodable from system data alone. They must be captured in structured configuration before the agent goes live. If Priya leaves before this happens, these rules leave with her.
```

**REPLACE WITH:**
```markdown
## What Must Be Resolved Before Building

Four things must be in place before the agent can do its job reliably. Without them, the agent will have less operational knowledge than Priya already has:

**0. Schedule actual discovery interview with Priya Aggarwal (HR Ops Lead).**  
All responses in this document are AI-simulated hypotheses, not validated facts. Before building, validate with Priya:
- Does the Excel tracker exist? What columns does it have? Where is it stored?
- Does the Legacy HR system exist for contractor records pre-2020? If so, does it have an API or batch export?
- What are the actual I-9 status values in Workday? What does "IN_PROGRESS" vs. "PENDING_REVIEW" actually mean?
- What is the actual escalation channel for CRITICAL alerts? (Teams, WhatsApp, phone, email?)
- What compliance matrix corrections has Priya made? Can we get both versions (SharePoint official vs. Priya's annotated copy)?
- What is the actual informal IT contact path? (Is "Mark in IT" real, or is this a generic example?)
- What recruiter-specific data quality issues exist? (Is Connections HR real? Are there others?)

**1. Acquire Priya's Excel tracker and make it the schema baseline.**  
The tracker is the real mental model of the work. Every column it has that Workday doesn't is a gap the agent must fill. Get the file, document its schema, and treat it as the primary design input — not the SOP.

**2. Establish the escalation channel with the actual decision-makers.**  
Teams or SMS for anything with a response SLA under 2 hours. This requires IT provisioning of the integration and confirmation from HR Manager (and CFO, not COO) that they will respond to that channel. Without this, the I-9 SLA is structurally unachievable.

**3. Formally document every undocumented rule before launch.**  
The compliance matrix corrections, any recruiter-specific data quality patterns, and any buddy matching exclusion rules — none of these are encodable from system data alone. They must be captured in structured configuration before the agent goes live. If Priya leaves before this happens, these rules leave with her.
```

---

### Location 1D: Add Legacy HR System to Assumptions Table

**FILE:** `DELIVERABLE-1-DISCOVERY-QUESTIONS.md`  
**LINE:** 213 (table "## Part 4: Updated Assumptions After Simulation")

**FIND the table starting at line 213, and ADD this row at the end:**

```markdown
| Legacy HR system exists for contractor records pre-2020 | **VERY LOW** | Legacy HR is not listed in the scenario's 5-system inventory (Workday, ServiceNow, Saba LMS, SharePoint, Outlook); this detail appears only in the simulated response; validate with IT before assuming it exists | If it doesn't exist, remove all references to Legacy HR from the design; contractor data quality risk may be lower than assumed; if it does exist but has no API, add it to system inventory with "batch-only" or "manual lookup" integration path |
```

---

## CHANGE 2: DELIVERABLE-3 & DELIVERABLE-5 — Buddy Matching Scope Alignment

### Location 2A: Update DELIVERABLE-3 Cluster 4 Rationale

**FILE:** `DELIVERABLE-3-DELEGATION-MATRIX.md`  
**LINE:** 117-120 (Cluster 4 rationale)

**CURRENT TEXT:**
```markdown
**Rationale for archetype:** The "agent" part of buddy matching is a sort function. Seniority_delta is arithmetic. Tenure comparison is arithmetic. Department filtering is a rule. None of this requires LLM reasoning. Calling it "Agent-Led" would imply the agent is reasoning about candidates — it isn't. HR Ops sees a sorted list and makes the decision that cannot be automated: whether this specific person is the right fit for this specific hire given team dynamics the system cannot observe.
```

**REPLACE WITH:**
```markdown
**Rationale for archetype:** The "agent" part of buddy matching is a sort function. Seniority_delta is arithmetic. Tenure comparison is arithmetic. Department filtering is a rule. None of this requires LLM reasoning. Calling it "Agent-Led" would imply the agent is reasoning about candidates — it isn't. HR Ops sees a sorted list and makes the decision that cannot be automated: whether this specific person is the right fit for this specific hire given team dynamics the system cannot observe.

**Scope clarification:** The sorting automation (query eligible employees, calculate seniority_delta, sort by [delta ASC, tenure DESC], return top 5) is **in-scope for Phase 1 CoordinationOrchestrator** (Activity 10: Generate Sorted Buddy Candidate List). The *selection* from that sorted list is **Human-Led**. This is deterministic automation (not agentic) that assists the human decision-maker.
```

---

### Location 2B: Update DELIVERABLE-5 OUT OF SCOPE Section

**FILE:** `DELIVERABLE-5-AGENT-PURPOSE.md`  
**LINE:** 59 (buddy matching row in OUT OF SCOPE table)

**CURRENT TEXT:**
```markdown
| **Buddy matching** | Ranking is deterministic (sort by seniority_delta, tenure, department); team fit selection is human-only judgment | HR Ops (receives sorted candidate list from automation; makes selection based on team dynamics) |
```

**REPLACE WITH:**
```markdown
| **Buddy matching selection** | Team fit selection is human-only judgment; agent cannot reason about team dynamics the system cannot observe | HR Ops (receives sorted candidate list from agent Activity 10; makes selection based on team dynamics) |
```

---

### Location 2C: Add Activity 10 to DELIVERABLE-5 Activity Catalog

**FILE:** `DELIVERABLE-5-AGENT-PURPOSE.md`  
**LINE:** 100 (section header "## 4. Activity Catalog: The 9 Things the Agent Does")

**STEP 1: Update the header**

**CURRENT TEXT (line 100):**
```markdown
## 4. Activity Catalog: The 9 Things the Agent Does
```

**REPLACE WITH:**
```markdown
## 4. Activity Catalog: The 10 Things the Agent Does
```

**STEP 2: Add Activity 10 after Activity 9**

**INSERT after line 183 (after Activity 9's description ends, before "## 5. Key Performance Indicators"):**

```markdown
### Activity 10: Generate Sorted Buddy Candidate List
- **Input:** hire_id, hire.department, hire.seniority_level, employee directory
- **Process:**
  1. Query employee directory with filters:
     - `tenure_months >= 6` (minimum tenure requirement)
     - `buddy_eligible = true` (excludes employees on leave, contractors, probation)
     - `department = hire.department` (same department match)
     - `NOT assigned_as_buddy_in_last_90_days` (fairness: distribute buddy assignments)
  2. For each candidate, calculate: `seniority_delta = abs(hire.seniority_level - candidate.seniority_level)`
  3. Sort candidates by:
     - `seniority_delta ASC` (prefer closer seniority match — primary sort key)
     - `tenure_months DESC` (break ties with longer tenure)
  4. Return top 5 candidates with metadata: {candidate_id, name, seniority_level, seniority_delta, tenure_months, last_buddy_assignment_date}
- **Output:** Sorted candidate list (max 5 candidates) sent to HR Ops for selection
- **Frequency:** Once per hire (triggered when BUDDY_ASSIGNMENT task status becomes READY)
- **Edge cases:**
  - If result set = 0 → escalate NO_ELIGIBLE_BUDDY (see Escalation Triggers § 3)
  - If best match has seniority_delta > 2 → flag SENIORITY_GAP in escalation metadata
  - If result set < 5 → return all candidates (do not pad or retry query)
  - If hire.seniority_level is NULL → escalate SENIORITY_UNMAPPED; do not attempt matching
- **Why this is automation, not agentic:** Every step is deterministic (filter, calculate, sort, return). No LLM reasoning. No judgment. A simple SQL query + sort function can implement this. The *selection* from the sorted list (which candidate is the best team fit?) is the human-only judgment that remains out of scope.

---
```

---

### Location 2D: Update DELIVERABLE-5 IN SCOPE Table

**FILE:** `DELIVERABLE-5-AGENT-PURPOSE.md`  
**LINE:** 42-51 (table "### IN SCOPE (Agent Executes Autonomously)")

**INSERT this row after the "Generate manager handoff" row (before the table closes):**

```markdown
| **Generate sorted buddy candidate list** | Deterministic sort: query eligible employees with filters (department, tenure ≥6 months, not assigned in last 90 days), calculate seniority_delta per candidate, sort by [seniority_delta ASC, tenure DESC], return top 5 | Sorted candidate list sent to HR Ops for team fit selection |
```

---

## OPTIONAL CHANGE 1: DELIVERABLE-4 Cluster 6 Volume Score Footnote

### Location: DELIVERABLE-4 Cluster 6 Volume Calculation

**FILE:** `DELIVERABLE-4-VOLUME-VALUE.md`  
**LINE:** 105 (Cluster 6 volume score)

**CURRENT TEXT:**
```markdown
**Volume Score: 5** (>200/year; continuous operation)
```

**REPLACE WITH:**
```markdown
**Volume Score: 5** (>200/year; continuous operation)*

*Note: Volume score reflects agent polling frequency (continuous operation = 3,500+ status checks per person/year). The *human* equivalent is ~15 manual coordination sessions per week (~760/year based on 183 hours/year of coordination work), but the agent performs 3,500+ discrete checks to achieve the same monitoring coverage. The score reflects operational workload (agent checks required to replicate human oversight), not direct 1:1 human action replacement. This still produces the highest volume score (5), which combined with low non-determinism (2) yields the top agentic value score (10) among all clusters.
```

---

## OPTIONAL CHANGE 2: DELIVERABLE-3 Split IT Provisioning into 5a/5b

### Location: DELIVERABLE-3 Cluster 5

**FILE:** `DELIVERABLE-3-DELEGATION-MATRIX.md`  
**LINE:** 124-136 (Cluster 5 section)

**CURRENT TEXT:**
```markdown
#### Cluster 5: IT Provisioning Request Generation (JtD 3, Zone 3)

[Full scoring table with Suitability Score: 3.7]

**Delegation Archetype** | **Fully Automated** (main path) **+ Agent-Led + Oversight** (unmapped role exception)

[Rationale paragraph]
```

**REPLACE WITH:**

```markdown
#### Cluster 5a: IT Provisioning Request Generation — Mapped Roles (JtD 3, Zone 3)

**Scope:** ~90% of hires — role exists in IT access matrix

| Dimension | Score | Rationale |
|---|---|---|
| **Input Structure** | 5 | Hire has role (in HRIS). IT role-access matrix is structured (role → access_package_id). |
| **Decision Determinism** | 5 | Lookup is fully deterministic: `hire.role → access_package_id` (rule-based). |
| **Exception Rate** | 5 | <5% of mapped-role requests hit exceptions (IT system downtime only). |
| **Tool Coverage** | 4 | Can query IT role-access matrix. Can call IT provisioning API to submit request. IT system has approval gate (external), so not fully autonomous. |
| **Risk/Reversibility** | 2 | Incorrect access grant = security incident ($1,000–$5,000 remediation) or compliance violation. Reversible (revoke access) but requires security team. |
| **Suitability Score** | 4.7 | (5+5+4)/3 |
| **Delegation Archetype** | **Fully Automated (rule engine)** | Deterministic lookup + API submit. The IT approval gate is IT's governance, not agent reasoning. No LLM needed. |

**Rationale for archetype:** The main path (role found in matrix) needs no LLM — a simple lookup table and API call. Implement as a deterministic rule in the Phase 1 Orchestrator.

---

#### Cluster 5b: IT Provisioning Request Generation — Unmapped Roles (JtD 3, Zone 3)

**Scope:** ~10% of hires — role not found in IT access matrix

| Dimension | Score | Rationale |
|---|---|---|
| **Input Structure** | 3 | Hire has role and department, but role is not in matrix. Context is partial. |
| **Decision Determinism** | 3 | Choosing "nearest" access package requires similarity reasoning across role titles + department context. Not deterministic. |
| **Exception Rate** | 1 | 100% of cases in this path are exceptions by definition (role not mapped). |
| **Tool Coverage** | 3 | Can query matrix to find similar roles. Can call LLM to reason about similarity. IT Manager must approve proposal. |
| **Risk/Reversibility** | 2 | Same as 5a — incorrect access = security incident. |
| **Suitability Score** | 3.0 | (3+3+3)/3 |
| **Delegation Archetype** | **Agent-Led + Oversight (Phase 2 Proposal Router)** | LLM reads unmapped role title (e.g., "Head of ESG Compliance") and department, compares to existing matrix entries, proposes nearest access package with similarity score and rationale (e.g., "Closest match: Compliance Manager, 85% similarity. Suggested package: Compliance_Senior"). IT Manager approves or adjusts. This is genuine LLM reasoning over ambiguous input. |

**Rationale for archetype:** Unlike 5a, this path cannot be solved with a lookup table — the role *isn't in* the table. An LLM can reason about role title similarity and propose a match, but IT Manager must approve before the request is submitted. This is the Phase 2 Proposal Router pattern.

---
```

**THEN UPDATE the Summary Scoring Table (line 209) to split the row:**

**FIND this row in the summary table:**
```markdown
| 5. IT Provision | 4 — deterministic lookup (main path); LLM proposes for unmapped roles | 3 — main path: automation; unmapped: LLM proposes nearest package for IT to approve | 2 — 15–20% unmapped | 2 — security risk | **3.7** | Fully Automated (main) + Agent-Led + Oversight (unmapped) |
```

**REPLACE WITH two rows:**
```markdown
| 5a. IT Provision (mapped) | 5 — fully deterministic | 4 — main path API submit | 5 — <5% exceptions | 2 — security risk | **4.7** | Fully Automated |
| 5b. IT Provision (unmapped) | 3 — similarity reasoning | 3 — LLM proposes, IT approves | 1 — 100% exceptions by definition | 2 — security risk | **3.0** | Agent-Led + Oversight (Phase 2) |
```

---

## Verification After Rewriting

After implementing these changes, verify:

### ☐ DELIVERABLE-1 Checks
- [ ] Simulation disclaimer appears at top (before Part 1)
- [ ] All 6 "COO's answer" headers changed to "Simulated Response (Validation Required)"
- [ ] "What Must Be Resolved Before Building" has item #0 (discovery interview)
- [ ] Assumptions table includes "Legacy HR system" row with VERY LOW confidence

### ☐ DELIVERABLE-3 & DELIVERABLE-5 Checks
- [ ] D3 Cluster 4 rationale includes "Scope clarification" paragraph
- [ ] D5 OUT OF SCOPE row retitled to "Buddy matching **selection**"
- [ ] D5 Activity Catalog header updated: "10 Things" (not 9)
- [ ] D5 Activity 10 added with full Input/Process/Output/Edge cases
- [ ] D5 IN SCOPE table includes buddy sorting row
- [ ] No conflicts between D3 and D5 on buddy matching scope

### ☐ Optional Changes (if implemented)
- [ ] D4 Cluster 6 volume score has footnote explaining continuous operation
- [ ] D3 Cluster 5 split into 5a (mapped, 4.7) and 5b (unmapped, 3.0)
- [ ] D3 summary scoring table updated with 5a/5b rows

---

**Prepared by:** Claude Opus 4.6 (AI FDE)  
**Date:** 2026-05-05
