# Problem Framing and Success Metrics
**Project:** Greenfield Health Systems — AI Claims Processing Transformation  
**Prepared by:** FDE Engagement Lead  
**Date:** 2026-04-09  
**Assumptions Register:** `specs/assumptions.md`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
   - 2.1 [Stated Request vs. Actual Need](#21-stated-request-vs-actual-need)
   - 2.2 [Current State: Quantified](#22-current-state-quantified)
   - 2.3 [Root Problems](#23-root-problems)
   - 2.4 [Problem Framing: Both Perspectives](#24-problem-framing-both-perspectives)
   - 2.5 [Constraints](#25-constraints)
3. [Success Metrics](#3-success-metrics)
4. [Critical Unknowns](#4-critical-unknowns)

---

## 1. Executive Summary

Greenfield Health Systems presents this as an AI deployment problem. The actual problem is a **structural capacity crisis compounded by a first-pass quality failure**: the team cannot process incoming claims fast enough to prevent a growing backlog, and when claims are denied, 41% of those denials are wrong. These are separate problems that AI alone does not automatically fix.

The math is unambiguous. At 45 processors, 35 minutes per manual claim, and 85% utilization [A3], daily processing capacity is approximately 524 claims. Daily manual review demand is approximately 1,300 claims (78% of ~1,667 daily volume [U1]). The structural daily deficit is ~776 claims/day — and it has compounded into a 9+ day queue that violates payer SLAs.

The CFO's request for AI deployment is the correct directional response. But deploying AI onto the existing workflow without redesigning it will shift the bottleneck, not eliminate it. The solution requires a dual-path workflow where AI adjudicates routine administrative claims end-to-end and pre-screens clinical claims so physicians review summaries — not full files. This architecture can satisfy all three executive mandates simultaneously, but only if one critical assumption holds: that ~35% of claims carry genuine clinical content, not 50% or 60% [A2]. That assumption is currently unvalidated and is the single highest-risk dependency in the entire design.

Success is not "AI is deployed." Success is: cycle time below 7 days on both paths, clinical flagging false-negative rate below 2%, auto-adjudication at or above 65%, and 8 FTE admin reduction confirmed within 6 months.

---

## 2. Problem Statement

### 2.1 Stated Request vs. Actual Need

**What Greenfield asked for:**  
"Deploy an AI claims agent to accelerate processing and reduce errors."

**What Greenfield actually needs:**  
A redesigned end-to-end claims processing workflow where:
1. AI adjudicates routine administrative claims without human review (eliminating the capacity deficit)
2. AI pre-screens clinical claims so physicians review summaries, not full files (preserving oversight while multiplying throughput)
3. The 41% denial appeal overturn rate is addressed at root cause — not papered over with faster incorrect denials

The risk of the stated request — deploy an AI agent — is treating a workflow design problem as a technology procurement problem. An AI agent layered onto the current process will not close the capacity gap unless it substantially reduces which claims require human review and how long each one takes. The workflow must change; the AI is the mechanism for changing it.

**Critical thinking on the solution direction:**  
There is an alternative to AI: hire more processors. Adding 15 FTEs at $65K fully loaded [A1] costs approximately $975K/year — more than AI annually but with much lower implementation risk and no Phase 1 validation requirement. The AI solution is the right call if (a) implementation succeeds within the $400K budget and 6-month timeline, and (b) quality outcomes equal or exceed the current manual process. Neither is guaranteed. The economic case depends on the assumptions in Section 3 holding. The quality case depends on the clinical flagging architecture working as designed.

The FDE recommendation is to proceed with the AI approach — the potential upside (65%+ auto-adjudication, cycle time < 4 days on Fast Path, sustained $520K+/year savings) significantly exceeds the staffing alternative — but to treat Phase 1 as a genuine decision gate, not a formality.

---

### 2.2 Current State: Quantified

**Volume and Throughput**

| Metric | Value | Source |
|--------|-------|--------|
| Monthly claims volume | ~50,000 | Scenario |
| Daily claims volume | ~1,667/day [U1] | Stakeholder calculation (50,000 ÷ 30) |
| Current auto-adjudication rate | 22% (~367 claims/day) | Scenario |
| Claims requiring manual review | ~1,300/day (78% × 1,667 [U1]) | Derived |
| Current average processing time per claim | 35 minutes | Scenario |
| Daily processing capacity [A3] | ~524 claims/day | Derived: 45 × 408 min ÷ 35 min/claim |
| Daily capacity deficit [A3] | ~776 claims/day | Derived: 1,300 − 524 |
| Current average cycle time | 8 days | Scenario |
| Current queue depth | 9+ days | VP Ops (Slack exchange) |
| SLA threshold (penalty trigger) | 7 days | Scenario (implied) |
| Industry auto-adjudication benchmark | 85% | Scenario |

> **Note on volume discrepancy:** The scenario header states "2,000 claims/day with 45 processors." The stakeholder exchange uses 1,667/day (50,000 ÷ 30). These differ by ~20%. This document uses 1,667/day as the planning basis because it is the figure stakeholders explicitly reason from in the financial model. The discrepancy is flagged as Unknown U1.

**Quality**

| Metric | Value | Source |
|--------|-------|--------|
| Claims error rate | ~1.2% | Scenario |
| Denial appeal overturn rate | 41% | Scenario |
| Gap vs. industry auto-adjudication benchmark | 63 percentage points | Derived (85% − 22%) |

The 41% denial appeal overturn rate is a material quality signal. It means roughly 4 in 10 denied claims are subsequently reversed on appeal — indicating systematic first-pass errors. The root cause is unknown [U3]: it may be coding errors, eligibility mismatches, or clinical necessity judgment failures. This distinction determines whether AI adjudication will reduce the overturn rate or replicate it.

**Economics [A1, A8]**

| Metric | Estimated Value | Basis |
|--------|----------------|-------|
| Annual cost of 20 admin processors [A1] | ~$1.3M/year | 20 × $65K |
| Annual cost of full 45-person team [A1] | ~$2.9M/year | 45 × $65K |
| Annual AI operating cost at steady state [A4] | ~$41,000/year | See A4 |
| Daily payer penalty exposure (current, 2 days over SLA) [A8] | ~$50,000/day | 1,667 [U1] × $15 × 2 days |
| Implementation budget | $400,000 | CFO email |

> **Illustrative penalty exposure:** At $15/claim/day [A8] and 1,667 [U1] claims currently running 2 days over the 7-day SLA, the daily penalty exposure is approximately $50,000. Even if actual rates are $5/claim/day, the exposure exceeds $16,000/day. Payer penalty amounts must be confirmed from contracts (Unknown U4), but at any reasonable rate they represent a significant recoverable cost once SLAs are met.

---

### 2.3 Root Problems

**Root Problem 1 — Structural Capacity Mismatch (Primary)**  
The daily volume of claims requiring manual review (~1,300) exceeds the team's daily processing capacity (~524) [A3] by approximately 776 claims/day. This is not a peaks problem or a workflow inefficiency — it is a structural deficit that compounds daily. The 8-day average cycle time and 9+ day current queue are symptoms of this accumulation. Deploying AI is the right response *if* the agent can move a sufficient share of those 1,300 claims/day off the manual review queue.

How much is sufficient? The Fast Path must handle at minimum 776 claims/day — all the claims currently creating the daily deficit — plus enough to begin burning down the existing backlog. At 65% Fast Path [A2], the agent handles approximately 1,083 claims/day, reducing the manual review demand to 583 claims/day (Clinical Path). With 524 claims/day of existing capacity, Clinical Path volume of 583 claims/day still slightly exceeds capacity — meaning physician throughput improvements from pre-screening [A5] are essential to close the last gap.

**Root Problem 2 — First-Pass Quality Failure (Secondary but High Risk)**  
A 41% denial appeal overturn rate indicates a systematic quality problem in the current process, not just a speed problem. Any AI agent trained on — or designed to replicate — the current decision patterns risks encoding these errors at scale. Before designing the AI's adjudication rules, the FDE team must understand why denials are being overturned [U3]. This is a discovery requirement, not an assumption.

If the overturn rate is driven primarily by coding or eligibility errors (administrative domain), the AI agent should resolve it. If driven by clinical necessity judgment errors, and those claims are routed to Fast Path without physician review, the overturn rate could worsen post-deployment — creating regulatory exposure.

**Root Problem 3 — Misaligned Stakeholder Mandates**  
The CFO, CMO, and VP of Operations define success differently and their definitions are arithmetically incompatible at face value. The dual-path architecture proposed in the alignment memo is a negotiated resolution that works only if [A2] holds: that 35% clinical content is real, not wishful math. The stakeholder alignment problem is organizational, not technical. No AI system resolves a governance dispute; only validated data and clear accountability structures do.

---

### 2.4 Problem Framing: Both Perspectives

**From the provider/claimant perspective:**  
Providers submit claims and wait 8+ days for payment or denial — directly impacting cash flow and, for smaller practices, solvency. When a claim is denied, 41% of those denials are incorrect, requiring administrative investment in appeals that should never have been necessary. From a patient perspective: if any of the 50,000 monthly claims involve pre-authorization for care (prospective, not retrospective), a 9-day processing queue may be delaying access to treatment, not just payment. The provider and patient harm is measurable: cash flow delay, administrative burden, and potential care access delay.

**From the business perspective:**  
Greenfield is incurring two forms of cost simultaneously: the fixed cost of a processing team whose capacity cannot match volume, and the variable cost of payer penalties for SLA violations. The $2.9M/year team [A1] is producing a 22% auto-adjudication rate against an 85% industry benchmark — meaning the team is handling manually what well-run peers handle automatically. The 41% overturn rate adds rework cost and possible liability. The $400K AI investment is not a technology purchase; it is the mechanism for closing a 63-point efficiency gap while preserving the clinical oversight the CMO requires.

---

### 2.5 Constraints

| Constraint | Source | Type |
|-----------|--------|------|
| $400K total implementation budget | CFO email | Financial — hard limit |
| 8 FTE admin reduction within 6 months | CFO email | Financial — board requirement |
| Physician review required on all clinical claims | CMO email | Clinical / legal — non-negotiable |
| CMO must certify system before it can deny claims | CMO email | Clinical / legal — non-negotiable |
| Average cycle time must average < 7 days | VP Ops / payer contracts | Operational — hard limit |
| Claims arrive in multiple formats (EDI 837, PDF, portal) | Scenario | Technical — design constraint |
| Phase 1 gate: clinical flagging false-negative rate < 2% | Alignment memo | Quality — hard gate |

---

## 3. Success Metrics

### Metric 1: Average Claims Cycle Time

**Type:** Lagging indicator — operational outcome  
**Current Baseline:** 8.0 days average; 9+ days in current queue (scenario)  
**Target:** ≤ 6.5 days overall by end of Phase 2 (Month 6), with Fast Path ≤ 4 days and Clinical Path ≤ 7 days  
**Why 6.5 days overall:** The 7-day SLA is the hard constraint (U4). A 6.5-day target builds in a 0.5-day buffer against volume spikes and provides headroom to demonstrate compliance before Phase 3.  
**Measurement Method:** Weekly extract from claims management system: timestamp of claim submission vs. timestamp of adjudication decision. Report as rolling 7-day average, segmented by Fast Path vs. Clinical Path. Alert threshold: any 7-day rolling average exceeding 7.0 days triggers remediation review.  
**Dependencies:** A2 (65/35 split must hold — if Clinical Path volume exceeds 35%, physician throughput limits will drive cycle time above 7 days), A3 (physician pre-screening achieves 20 claims/hour as stated by Dr. Webb)

---

### Metric 2: Fast Path Adjudication Rate

**Type:** Leading indicator — efficiency  
**Current Baseline:** 22% auto-adjudication (scenario)  
**Target:** ≥ 65% by end of Phase 2 (Month 6)  
**Definition:** % of total monthly claims adjudicated by the Fast Path agent without human escalation  
**Why 65%:** This is the target derived from the 65/35 clinical split [A2]. The industry benchmark is 85%, which remains the long-term ceiling. If Phase 1 validates that fewer than 35% of claims have clinical content, this target should be revised upward before Phase 2 launch.  
**Measurement Method:** Monthly: (claims completed via Fast Path without human review) ÷ (total claims received). Track escalation rate separately — Fast Path claims escalated to human review should remain below 5% to confirm agent reliability.  
**Dependencies:** A2 (validated clinical split), A6 (flagging accuracy — miscategorization inflates the false Fast Path rate)

---

### Metric 3: Clinical Flagging False-Negative Rate

**Type:** Leading indicator — patient safety gate  
**Current Baseline:** N/A (no automated flagging exists)  
**Target:** < 2% over a minimum 60-day shadow-mode run (Phase 1 gate — hard stop)  
**Definition:** False negative = agent classifies a claim with genuine clinical content as administrative, routing it to Fast Path without physician review  
**Why this is the highest-priority metric:** A false-negative clinical claim processed through Fast Path without physician review is the primary patient safety and regulatory failure mode. It is what the CMO's non-negotiable requirement is designed to prevent. If this rate cannot be driven below 2%, the Fast Path architecture cannot launch.  
**Measurement Method:** During Phase 1 shadow mode, physicians classify a stratified random sample of agent-categorized "administrative" claims. False negative rate = (clinical claims misclassified as administrative) ÷ (total clinical claims in sample). Sample size must be sufficient for statistical significance at the 2% threshold (minimum 200 confirmed clinical claims reviewed).  
**Dependencies:** A6 (achievability of <2% post-tuning), U8 (definition of "clinical content" must be resolved before Phase 1 begins — without it, the metric cannot be measured)

---

### Metric 4: Denial Appeal Overturn Rate

**Type:** Lagging indicator — quality  
**Current Baseline:** 41% (scenario)  
**Phase 2 gate target:** Does not exceed 41% baseline within 90 days of Fast Path launch  
**Phase 3 target:** ≤ 25% by Month 12  
**Why two targets:** The first priority is not worsening the existing quality problem. AI adjudication can fail in new ways that the current manual process does not; the 90-day non-regression gate detects this early. Once non-regression is confirmed, a ≤ 25% target by Month 12 reflects a reasonable improvement from eliminating coding and eligibility errors that AI should reliably catch.  
**Measurement Method:** Monthly: (denied claims successfully appealed and reversed) ÷ (total denied claims). Segment by Fast Path vs. Clinical Path to isolate AI-introduced errors from pre-existing errors in the physician-reviewed path. If Fast Path overturn rate exceeds Clinical Path rate, the agent's adjudication logic requires investigation.  
**Dependencies:** U3 (root cause of current 41% rate must be understood before this target is credible — if caused by clinical necessity errors, AI may not improve it regardless of speed)

---

### Metric 5: Net Admin Headcount Reduction

**Type:** Lagging indicator — financial  
**Current Baseline:** ~20 admin claims processors (inferred: CFO states "8 FTEs = 40% of claims review staff" → 8 ÷ 0.40 = 20 current)  
**Phase 2 target:** 8 FTE reduction (20 → 12) by end of Month 6 — satisfying CFO's board commitment  
**Phase 3 target:** 13 FTE total reduction (20 → 7) by Month 9  
**Clinical review staff:** Excluded from this metric per CMO non-negotiable. Physician headcount is the CMO's decision.  
**Measurement Method:** HR headcount report at Phase 2 close vs. current baseline, role-segmented to confirm only admin processors are included. Reduction must be voluntary separation or redeployment — forced reduction is gated on Phase 1 gate passage (per alignment memo).  
**Financial impact [A1]:** 8 FTE reduction × $65K = **$520K annual savings** vs. $400K implementation cost. Simple payback: **9.2 months.** If payer penalty avoidance is included [A8]: at $50,000/day in current penalty exposure, even one month of SLA compliance adds ~$1.5M in avoided penalties — making the payback period potentially as short as **weeks**, not months.  
**Dependencies:** A1 (salary for ROI math), A2 (65/35 split must hold to sustain reduced admin need), A8 (penalty avoidance for full ROI)

---

## 4. Critical Unknowns

Unknowns are ranked by resolution urgency. **Must Resolve Before Spec** items block architecture finalization. **Resolve in Phase 1** items block Phase 2 launch. **Can Defer** items do not block current work.

---

### U1 — Volume Discrepancy: 2,000/day vs. 1,667/day
**Urgency:** Resolve before Phase 1  
**Gap:** The scenario header states "2,000 claims/day with 45 processors." The stakeholder exchange uses 1,667/day (Sarah Chen's arithmetic from 50,000 ÷ 30). A 20% gap in claim volume materially affects physician headcount requirements [A10], capacity math, and SLA projections.  
**Discovery question:** What is the actual daily claim volume over the past 90 days? Pull claims management system data.

---

### U2 — Current Physician Clinical Review Team Size and Throughput
**Urgency:** Must Resolve Before Spec  
**Gap:** Dr. Webb confirms "20 claims/hour with pre-screening" but does not state (a) current physician headcount, or (b) current throughput without pre-screening. If fewer than 4 physicians currently do clinical review [A10], the Clinical Path SLA cannot be met without hiring — a cost and timeline constraint the scenario does not address.  
**Discovery question:** How many physicians or APPs currently review claims? What is their current throughput (claims/hour, full file review)?

---

### U3 — Root Cause of 41% Denial Appeal Overturn Rate
**Urgency:** Must Resolve Before Spec  
**Gap:** The overturn rate is either an administrative error problem (coding, eligibility — AI-fixable) or a clinical judgment problem (necessity, coverage interpretation — AI may perpetuate or worsen). Designing the agent's adjudication logic without understanding which it is risks building a faster version of a broken process.  
**Discovery question:** Audit 50 denied claims reversed on appeal. Categorize each reversal: coding error, eligibility mismatch, clinical necessity reversal, coverage interpretation dispute, other. What % fall into each category?

---

### U4 — Payer Penalty Rate per Claim per Day
**Urgency:** Resolve in Phase 1  
**Gap:** The financial case is materially incomplete without this number. At $15/claim/day [A8], penalty avoidance alone may justify the entire $400K investment in the first month of SLA compliance. At $5/claim/day, the ROI timeline is still attractive. The actual rate is in the payer contracts.  
**Discovery question:** Pull the 3 largest payer contracts. What is the penalty clause for claims processed past the SLA threshold? What was Greenfield's total penalty liability in the last 90 days?

---

### U5 — Regulatory Constraints on AI-Assisted Adjudication
**Urgency:** Must Resolve Before Spec  
**Gap:** State insurance regulations and CMS requirements may govern what decisions an AI agent can make autonomously. Some states require a licensed physician to review and sign off on clinical necessity denials. If AI-assisted Fast Path denials are non-compliant, the architecture requires physician sign-off on all denials — not just clinical ones — which eliminates most of the throughput benefit.  
**Discovery question:** What states does Greenfield operate in? Has legal counsel reviewed AI adjudication compliance for those jurisdictions? Can the Fast Path legally deny a claim without physician sign-off?

---

### U6 — Claims Format Distribution (EDI 837 vs. Non-EDI)
**Urgency:** Resolve in Phase 1  
**Gap:** EDI 837 claims are structured and machine-parsable; PDFs require extraction that introduces errors. The AI agent architecture depends on knowing what formats it must reliably ingest. A high non-EDI percentage [A7] increases cost, error rates, and time-per-claim on the Fast Path.  
**Discovery question:** What % of 50,000 monthly claims arrive as EDI 837, PDF, and portal submissions?

---

### U7 — Claims Management System and Integration Feasibility
**Urgency:** Must Resolve Before Spec  
**Gap:** The AI agent must integrate with the existing claims management system. If the system is a legacy platform (Facets, TriZetto, custom) with limited API surface, integration may consume a disproportionate share of the $400K budget [A9] before a single claim is processed.  
**Discovery question:** What claims management system does Greenfield use? Is there an API? What does a basic integration assessment look like? Has IT scoped this?

---

### U8 — Definition of "Clinical Content" for Flagging Criteria
**Urgency:** Must Resolve Before Spec  
**Gap:** The alignment memo commits the FDE Team and Dr. Webb to defining clinical flagging criteria, but "clinical content" is undefined. Does a physical therapy claim have clinical content? An imaging claim for a well visit? A mental health claim? The flagging algorithm is only as precise as the criteria it implements. Without a definition, the false-negative rate in Metric 3 cannot be measured.  
**Discovery question:** Work with Dr. Webb to produce an exhaustive taxonomy of claim types with a binary clinical/administrative flag. Which claim types always require physician review? Which never do? Which are ambiguous?

---

### U9 — Relationship Between 45-Processor Headcount and 20 Admin Staff Figure
**Urgency:** Resolve in Phase 1  
**Gap:** The scenario header states "45 processors." The CFO's financial model targets "20 claims review staff." The 25-person gap is unaccounted for. If those 25 include clinical reviewers, supervisors, or other non-administrative roles, the headcount reduction target (8 FTEs from 20 admin staff) may be understating the organizational impact — or the financial model may be targeting the wrong population.  
**Discovery question:** Provide an org chart of the 45-person team with role breakdown: admin claims processors, clinical reviewers, supervisors, QA, and other.

---

### U10 — Budget Allocation Across Phases
**Urgency:** Resolve Before Phase 1 Launch  
**Gap:** The $400K budget is undivided. Phase 1 infrastructure, integration development, and agent tuning all incur costs before any savings are realized [A9]. If Phase 1 consumes $150K+, the remaining budget may be insufficient to deploy both paths in Phase 2, threatening the 6-month headcount reduction timeline.  
**Discovery question:** Prepare a budget breakdown: Phase 1 (integration, shadow infrastructure, agent development, API costs), Phase 2 (live deployment, physician interface, admin transition), Phase 3 (steady-state operations). Identify the largest risks to budget overrun.

---

*End of document. See `specs/assumptions.md` for full assumption register.*
