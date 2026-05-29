# Remediation Checklist — Week 2 Gate Deliverables

**Submission:** ATX Assessment — HR Onboarding Coordination  
**Status:** APPROVED WITH MINOR CHANGES  
**Action Required Before Gate 2:** 2 changes

---

## Priority 1: REQUIRED CHANGES (Must complete before Gate 2)

### ☐ Change 1: DELIVERABLE-1 — Discovery Question Framing

**Issue:** Simulated answers are framed as "The COO's answer:" but the actual stakeholder is Priya Aggarwal (HR Ops Lead), and the answers are AI-generated role-play, not real discovery interviews.

**Impact:** Undermines transparency; readers may assume these are validated facts rather than hypotheses to validate.

**Location:** DELIVERABLE-1-DISCOVERY-QUESTIONS.md, lines 59-238 (all 6 question sections)

**Required Actions:**

1. **Retitle all answer sections** (6 instances)
   - FIND: `**The COO's answer:**`
   - REPLACE WITH: `**Simulated Response (Validation Required):**`

2. **Move simulation disclaimer to top of document**
   - FIND: Line 40 — The disclaimer currently starts mid-document
   - MOVE TO: Immediately after line 38 (before Part 1 begins)
   - ADD this header above it:
     ```markdown
     ## ⚠️ IMPORTANT: Simulation Context
     
     The answers below were generated through a structured AI role-play exercise to illustrate the *type* of detail discovery questions should surface. They are **hypotheses to validate**, not confirmed facts. The actual primary stakeholder at Aldridge & Sykes is **Priya Aggarwal (HR Ops Lead)**. Before finalizing the agent spec, these answers must be validated through an actual discovery interview with Priya.
     ```

3. **Add validation requirement to "What Must Be Resolved Before Building" section**
   - FIND: Section starting at line 227 ("What Must Be Resolved Before Building")
   - ADD as item **#0** (before current items 1-3):
     ```markdown
     **0. Schedule actual discovery interview with Priya Aggarwal (HR Ops Lead).**  
     All simulated responses in this document are hypotheses. Before building, validate:
     - Does Priya's Excel tracker exist? What columns does it have?
     - Does Legacy HR system exist for contractor records pre-2020?
     - What is the actual I-9 status logic in Workday?
     - What is the actual escalation channel (Teams, WhatsApp, phone)?
     - What compliance matrix corrections has Priya made?
     ```

4. **Add "Legacy HR System" to assumptions table**
   - FIND: Table starting at line 213 ("Updated Assumptions After Simulation")
   - ADD row:
     ```markdown
     | Legacy HR system exists for contractor records pre-2020 | **VERY LOW** | Legacy HR is not listed in the scenario's 5-system inventory; validate with IT before assuming it exists | If it doesn't exist, remove all references to Legacy HR from design; contractor data quality risk is lower than assumed |
     ```

**Estimated Time:** 15 minutes

**Verification:**
- [ ] All 6 "COO's answer" headers replaced with "Simulated Response (Validation Required)"
- [ ] Disclaimer moved to top of document with ⚠️ header
- [ ] Validation item added as #0 in "What Must Be Resolved Before Building"
- [ ] Legacy HR assumption added to assumptions table

---

### ☐ Change 2: DELIVERABLE-3 & DELIVERABLE-5 — Buddy Matching Scope Alignment

**Issue:** Buddy matching is labeled "Human-Led + Automation Support" in D3 (with the rationale: "sorting is automation, not agency; selection is human"), but in D5 it's listed as "OUT OF SCOPE (Manual or Human-Driven)" with no mention of the sorting automation being in-scope.

**Impact:** Ambiguity about whether buddy matching sorting is part of Phase 1 CoordinationOrchestrator or not. Cross-deliverable inconsistency.

**Location:** 
- DELIVERABLE-3-DELEGATION-MATRIX.md, lines 107-120 (Cluster 4)
- DELIVERABLE-5-AGENT-PURPOSE.md, lines 54-63 (Scope: OUT OF SCOPE section)

**Required Actions:**

1. **Update DELIVERABLE-3 Cluster 4 rationale** to clarify sorting is in-scope
   - FIND: Line 117-120 (Cluster 4 rationale)
   - REPLACE:
     ```markdown
     **Rationale for archetype:** The "agent" part of buddy matching is a sort function. Seniority_delta is arithmetic. Tenure comparison is arithmetic. Department filtering is a rule. None of this requires LLM reasoning. Calling it "Agent-Led" would imply the agent is reasoning about candidates — it isn't. HR Ops sees a sorted list and makes the decision that cannot be automated: whether this specific person is the right fit for this specific hire given team dynamics the system cannot observe.
     
     **Scope:** The sorting automation is **in-scope for Phase 1 CoordinationOrchestrator** (Activity 10: Generate Sorted Buddy Candidate List). The selection from that sorted list is **Human-Led**.
     ```

2. **Update DELIVERABLE-5 OUT OF SCOPE section** to reflect sorting is in-scope
   - FIND: Lines 54-63 (OUT OF SCOPE table)
   - FIND the "Buddy matching" row
   - REPLACE:
     ```markdown
     | **Buddy matching selection** | Team fit selection is human-only judgment; agent cannot reason about team dynamics | HR Ops (receives sorted candidate list from agent; makes selection based on team dynamics the system cannot observe) |
     ```

3. **Add Activity 10 to DELIVERABLE-5 Activity Catalog**
   - FIND: Section "## 4. Activity Catalog: The 9 Things the Agent Does" (currently lists Activities 1-9)
   - UPDATE header: `## 4. Activity Catalog: The 10 Things the Agent Does`
   - ADD after Activity 9 (before line 184):
     ```markdown
     ### Activity 10: Generate Sorted Buddy Candidate List
     - **Input:** hire.department, hire.seniority_level, employee directory
     - **Process:**
       - Query employee directory: `tenure_months >= 6 AND buddy_eligible = true AND department = hire.department AND NOT assigned_as_buddy_in_last_90_days`
       - For each candidate, calculate `seniority_delta = abs(hire.seniority_level - candidate.seniority_level)`
       - Sort by: seniority_delta ASC, tenure_months DESC (prefer closer seniority match; break ties with longer tenure)
       - Return top 5 candidates with scores
     - **Output:** Sorted candidate list {candidate_id, seniority_delta, tenure_months, last_buddy_assignment_date} × 5
     - **Frequency:** Once per hire (triggered by BUDDY_ASSIGNMENT task becoming READY)
     - **Edge cases:**
       - If result set = 0 → escalate NO_ELIGIBLE_BUDDY
       - If best match has seniority_delta > 2 → flag SENIORITY_GAP in escalation
       - If result set < 5 → return all candidates (do not pad)
     ```

4. **Update DELIVERABLE-5 "IN SCOPE" table** to include buddy sorting
   - FIND: Line 42-51 ("IN SCOPE (Agent Executes Autonomously)" table)
   - ADD row after "Generate manager handoff":
     ```markdown
     | **Generate sorted buddy candidate list** | Deterministic sort: query eligible employees, calculate seniority_delta per candidate, sort by [delta ASC, tenure DESC], return top 5 | Sorted candidate list sent to HR Ops for selection |
     ```

**Estimated Time:** 20 minutes

**Verification:**
- [ ] D3 Cluster 4 rationale updated to state "sorting is in-scope for Phase 1"
- [ ] D5 OUT OF SCOPE row retitled to "Buddy matching **selection**"
- [ ] D5 Activity Catalog updated to include Activity 10 (buddy sorting)
- [ ] D5 IN SCOPE table includes buddy sorting row
- [ ] Total activity count updated from 9 → 10

---

## Priority 2: OPTIONAL IMPROVEMENTS (Recommended but not required)

### ☐ Optional Change 1: DELIVERABLE-4 — Cluster 6 Volume Score Footnote

**Issue:** Cluster 6 (Task Monitoring) scores Volume: 5 with the calculation "3,500 monitoring events per person/year." However, the rubric defines volume as "how many times per year does this task cluster occur per HR Ops person?" — meaning discrete human actions. If the agent polls automatically every 2 hours, that's continuous operation, not 3,500 discrete human interventions.

**Impact:** Minor — The formula (Volume × Non-Determ = 5 × 2 = 10) still produces the highest score, so this doesn't change the primary target designation. But the volume score interpretation could be clearer.

**Location:** DELIVERABLE-4-VOLUME-VALUE.md, lines 96-105 (Cluster 6 volume calculation)

**Suggested Action:**

- FIND: Line 105 (`**Volume Score: 5** (>200/year; continuous operation)`)
- REPLACE WITH:
  ```markdown
  **Volume Score: 5** (>200/year; continuous operation)*
  
  *Note: Volume score reflects agent polling frequency (continuous operation = 3,500+ status checks per year). The *human* equivalent is ~15 manual coordination sessions per week (760/year), but the agent performs 3,500+ discrete checks to achieve the same monitoring coverage. The score reflects operational workload, not direct human time replacement.
  ```

**Estimated Time:** 5 minutes

**Verification:**
- [ ] Footnote added to Cluster 6 volume score explaining continuous-operation scoring

---

### ☐ Optional Change 2: DELIVERABLE-3 — Split IT Provisioning into 5a/5b

**Issue:** Cluster 5 (IT Provisioning) has a dual archetype: "Fully Automated (main path) + Agent-Led + Oversight (unmapped role exception)." This is correct but may confuse readers who expect one archetype per cluster.

**Impact:** Minor — Doesn't affect scoring or design, just presentation clarity.

**Location:** DELIVERABLE-3-DELEGATION-MATRIX.md, lines 124-136 (Cluster 5)

**Suggested Action:**

- FIND: Cluster 5 section (lines 124-136)
- SPLIT into two rows in the scoring table:
  ```markdown
  #### Cluster 5a: IT Provisioning Request Generation (Mapped Roles — 90% of cases)
  
  [Keep existing scores: Input Structure 4, Decision Determinism 4, etc.]
  
  **Delegation Archetype:** **Fully Automated** — Deterministic lookup (`hire.role → access_package_id`) + API submit. No LLM reasoning needed.
  
  ---
  
  #### Cluster 5b: IT Provisioning Request Generation (Unmapped Roles — 10% of cases)
  
  [Adjust scores for exception path: Input Structure 2, Decision Determinism 3, Tool Coverage 3, Exception Rate 5, Risk 2]
  
  **Delegation Archetype:** **Agent-Led + Oversight** — LLM reads role title and department, compares to similar roles in matrix, proposes nearest access package with rationale. IT Manager approves or adjusts. Part of Phase 2 Proposal Router.
  ```

**Estimated Time:** 10 minutes

**Verification:**
- [ ] Cluster 5 split into 5a (mapped) and 5b (unmapped) with separate archetype rows

---

## Post-Remediation Validation

After completing required changes, verify:

### ☐ Cross-Deliverable Consistency Check
- [ ] Read D1, D3, D5 sequentially
- [ ] Confirm buddy matching scope is consistent across all three
- [ ] Confirm discovery question framing is consistent (all labeled as "Simulated Response")
- [ ] Confirm no other cross-deliverable archetype conflicts

### ☐ Build Loop Re-Verification
- [ ] Re-read DELIVERABLE-5 Activity Catalog
- [ ] Confirm Activity 10 (buddy sorting) is implementable with the data available
- [ ] Confirm Activity 10 doesn't conflict with existing activities

### ☐ Final Read-Through
- [ ] Read PEER-REVIEW-ASSESSMENT.md
- [ ] Confirm all flagged issues have been addressed
- [ ] No new issues introduced by remediation edits

---

## Estimated Total Time

| Priority | Changes | Time |
|---|---|---|
| **Priority 1 (Required)** | 2 changes | 35 minutes |
| **Priority 2 (Optional)** | 2 changes | 15 minutes |
| **Validation** | Cross-check | 10 minutes |
| **TOTAL** | | **60 minutes** |

---

## Submission Checklist

Before submitting to Gate 2:

- [ ] All Priority 1 changes implemented
- [ ] Cross-deliverable consistency verified
- [ ] PEER-REVIEW-ASSESSMENT.md issues resolved
- [ ] Optional changes considered (not required)
- [ ] Final read-through completed
- [ ] Ready for sealed Gate 2 scenario

---

## Questions or Clarifications

If any remediation step is unclear:
1. Re-read the relevant section in PEER-REVIEW-ASSESSMENT.md
2. Check the "🔧 Action Needed" notes in the assessment
3. Refer to the ATX guideline documents in `/input-docs/` for methodology clarification

---

**Prepared by:** Claude Opus 4.6 (AI FDE)  
**Date:** 2026-05-05
