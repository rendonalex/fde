# 02 — Engagement Intake and Scope Definition
**Project:** Greenfield Health Systems — AI Claims Processing Transformation  
**Prepared by:** FDE Engagement Lead  
**Date:** 2026-04-09  
**Assumptions Register:** `specs/assumptions.md`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Context](#2-business-context)
3. [Stakeholder Map](#3-stakeholder-map)
4. [Constraints](#4-constraints)
5. [Risks](#5-risks)
6. [MVP Scope](#6-mvp-scope)
7. [Out of Scope](#7-out-of-scope)
8. [Assumptions Management](#8-assumptions-management)

---

## 1. Executive Summary

This engagement delivers a dual-path AI claims processing transformation for Greenfield Health Systems against an active operational crisis: 9+ day cycle times, ~$50K/day in estimated payer penalty exposure [A8, U1], and a structural 776-claim/day capacity deficit. The core architecture routes ~65% of daily claims to an AI-adjudicated Fast Path and ~35% to a physician-reviewed Clinical Path with AI pre-screening, targeting cycle time ≤7 days, 8 FTE admin reduction within 6 months, and ≥65% auto-adjudication against a current 22% rate.

The engagement is gated by Phase 1 shadow mode validation: Fast Path cannot launch until the clinical flagging false-negative rate reaches <2% over 60 days. The MVP covers five capabilities — claims ingestion, clinical triage, Fast Path adjudication, Clinical Path pre-screening, and shadow infrastructure — that together close the daily capacity deficit without compromising physician oversight.

Three risks require early executive attention before technical work is committed: the 35%/65% clinical split [A2] is unvalidated and is the highest-risk single dependency in the design; CMS integration feasibility [U7, A12] must be scoped in Week 1 before the Phase 1 architecture is finalized; and regulatory permissibility of AI-generated claim denials [U5, A11] must be confirmed before the Fast Path specification is written.

---

## 2. Business Context

**Problem Statement:**  
Greenfield faces a structural capacity deficit of ~776 manual review claims/day — processing capacity (~524/day) is less than half the daily demand (~1,300 claims requiring manual review) — compounded by a 41% denial appeal overturn rate that indicates systematic first-pass quality failure. See `specs/01-problem-framing-and-success-metrics.md` Section 2 for full quantification.

**Current State:**  
45 processors handle claims at 35 minutes each [A3], achieving 22% auto-adjudication against an 85% industry benchmark; the resulting backlog sits at 9+ days, actively triggering payer SLA penalties estimated at ~$50K/day [A8, U1].

**Desired Future State:**  
A dual-path workflow where AI adjudicates ≥65% of claims end-to-end (Fast Path) and pre-screens the remaining 35% for physician review (Clinical Path), achieving ≤7-day average cycle time on both paths and enabling a 13 FTE admin reduction by Month 9 [A2].

**Strategic Alignment:**  
AI claims transformation closes a 63-point auto-adjudication gap from the industry benchmark (22% vs. 85%), eliminates active payer contract liability, and delivers a board-presentable ROI within 6 months — demonstrating operational modernization against a measurable outcome.

**Success Metrics:**  
Five KPIs govern success: cycle time ≤6.5 days overall, Fast Path rate ≥65%, clinical flagging false-negative rate <2% (Phase 1 gate), denial appeal overturn rate non-regression at 41% then ≤25% by Month 12, and 8 FTE admin reduction by Month 6. See `specs/01-problem-framing-and-success-metrics.md` Section 3 for full definitions, baselines, and measurement methods.

**Business Value:**  
8 FTE reduction × $65K [A1] = $520K/year in labor savings against a $400K investment (9.2-month simple payback); payer penalty avoidance at ~$50K/day [A8, U1] may compress effective payback to weeks once the 7-day SLA is restored.

**Timeline & Urgency:**  
Payer SLA penalties are accruing today (9+ day queue); the CFO has committed to an 8-FTE reduction within 6 months as a board deliverable, creating a hard Phase 2 launch deadline of approximately Month 4 and leaving no margin for Phase 1 overruns.

---

## 3. Stakeholder Map

| Stakeholder | Role/Title | Influence Level | Interest Level | Primary Concerns | Engagement Strategy |
|---|---|---|---|---|---|
| Sarah Chen | CFO | H | H | 8 FTE reduction in 6 months; board ROI narrative; $400K budget ceiling | Weekly budget/milestone check-in; Phase 1 gate data reviewed before Phase 2 commitment |
| Dr. Marcus Webb | CMO | H | H | Patient safety; physician sign-off on all clinical claims; CMO system certification | Co-develop clinical flagging criteria [U8]; weekly false-negative rate review during Phase 1 |
| James Liu | VP Operations | H | H | SLA compliance; payer penalty elimination; no new throughput bottlenecks | Real-time cycle time dashboard access; SLA metrics in weekly ops review |
| IT / Engineering | Technical | M | H | CMS integration feasibility; system stability; HIPAA-compliant data handling | Week 1 discovery sprint; integration architecture review before Phase 1 commitment [U7, A12] |
| Legal / Compliance | Governance | M | M | HIPAA compliance; AI adjudication authority in operating states [U5, A11]; CMO certification scope | Legal review of Fast Path denial authority by Day 30; HIPAA assessment before Phase 1 data access |
| Claims Admin Processors (20) | End Users — Admin | L | H | Job security; workflow disruption during shadow mode | Transparent timeline communication before Phase 1 starts; voluntary separation/redeployment plan [A13] |
| Physicians / APPs | End Users — Clinical | M | M | Review burden; AI summary quality; trust in flagging accuracy | Co-design summary template [U8]; measure and report throughput weekly in Phase 2 |
| HR | Adjacent | L | M | Transition plan timing; voluntary vs. forced reduction; severance exposure | Engage after Phase 1 gate passage; conditional transition plan prepared by 2026-05-01 |

**Veto authority:**
- CFO: Budget continuation and board commitment
- CMO: System certification required before any live adjudication — explicit veto in scenario
- Legal: Regulatory compliance blocks Fast Path denial authority if AI denials are non-permissible [U5, A11]

**Champions vs. Skeptics:**
- Champions: CFO (financial urgency), VP Operations (SLA pressure)
- Conditional: CMO — supportive provided physician oversight is preserved per alignment memo
- Skeptics: Admin processors (job reduction exposure); Legal (unknown stance until regulatory review)

**Change management note:** Twenty admin processors face role reduction or elimination. HR must communicate before Phase 1 begins with a clear policy: no reductions until Phase 1 gate is passed and Phase 2 is formally authorized. Ambiguity on this point increases voluntary attrition during shadow mode, which degrades the comparison dataset [A13].

---

## 4. Constraints

**1. $400K Total Implementation Budget (Financial — Hard Ceiling)**  
The entire engagement — integration, agent development, shadow infrastructure, API operating costs, and Phase 1–3 deployment — must fit within $400K [CFO email]. Phase 1 infrastructure is estimated at $80–100K [A9], leaving ~$300K for Phase 2 and steady-state operations. Any integration complexity that consumes above $100K in Phase 1 [U7, A12] directly compresses Phase 2 scope or forces a timeline extension past the CFO's 6-month board commitment.

**2. Physician Sign-Off Required on All Clinical Claims (Clinical/Legal — Non-Negotiable)**  
The CMO will not certify any system that adjudicates clinically complex claims without physician review [CMO email]. Fast Path is limited strictly to claims with no clinical content; the boundary is defined by the clinical flagging criteria [U8]. This constraint is binary: a single confirmed violation of the clinical boundary risks CMO certification withdrawal and exposes Greenfield to clinical liability.

**3. Phase 1 False-Negative Gate: <2% Before Fast Path Launches (Quality — Hard Stop)**  
The Fast Path cannot go live until clinical flagging achieves <2% false-negative rate over a 60-day shadow run [Alignment Memo, A6]. This gate is non-negotiable regardless of timeline or financial pressure. If the gate is not met, Phase 2 is blocked; the project may proceed with Clinical Path pre-screening only until flagging accuracy is demonstrated.

**4. HIPAA and State AI Adjudication Regulations (Regulatory — Scope Unknown [U5, A11])**  
All claims data handling must comply with HIPAA. Additionally, state insurance regulations may require physician authorization for AI-generated claim denials. This constraint's full scope is unknown until legal review completes [U5]; if Fast Path denials require physician sign-off under applicable regulations, the architecture must be redesigned before Phase 2 specification is finalized. The $400K budget does not currently include legal remediation scope.

**5. Multi-Format Ingestion Requirement (Technical — Design Constraint [A7])**  
Claims arrive in EDI 837, PDF, and portal submission formats [Scenario]. The ingestion layer must reliably normalize all three before any downstream processing can occur. PDF extraction introduces error and cost risk; at an estimated 30% non-EDI rate [A7], a high extraction failure rate directly raises manual exception queue volume and undermines Fast Path throughput projections.

---

## 5. Risks

| Risk | Category | Probability | Impact | Mitigation Strategy | Owner | Status |
|---|---|---|---|---|---|---|
| A2 clinical split is materially wrong (>40% clinical volume) | Delivery | H | H | Phase 1 shadow mode measures actual split; revise financial model before Phase 2 commitment | FDE Lead + CFO | Open |
| CMS is legacy with no usable API [U7, A12] | Technical | M | H | Week 1 IT discovery sprint; integration cost re-scoped before Phase 1 commitment | FDE Lead + IT | Open |
| AI Fast Path denials legally require physician sign-off [U5, A11] | Regulatory | M | H | Legal review by Day 30; if blocked, Fast Path scope limited to approvals only; CFO financial model revised | FDE Lead + Legal | Open |
| Clinical flagging false-negative rate cannot reach <2% in Phase 1 [A6] | Delivery | M | H | Phase 1 gate is a hard stop; extend tuning window 30 days if not converging; escalate to CMO + CFO if no trend | FDE Lead + CMO | Open |
| Admin processor attrition disrupts Phase 1 shadow mode data quality [A13] | Organizational | L | M | HR communicates no-reduction-before-gate policy before Phase 1 launch; supervisor weekly check-ins | HR + James Liu | Open |

---

### Risk Detail: High-Impact Risks

#### Risk 1 — A2 Clinical Split Wrong

**Early warning indicators:**
- Phase 1 shadow mode shows clinical flag rate >40% consistently in first 4 weeks
- Dr. Webb's team requests capacity expansion before Phase 1 ends

**Contingency plan:**
- Immediately revise CFO financial model — headcount savings shrink proportionally with clinical volume
- Evaluate hybrid triage category (e.g., "administrative with clinical elements" routed to APP lightweight review rather than full physician review)
- Delay Phase 2 launch until revised physician headcount plan and financial model are confirmed [A10]

**Decision point:** Day 45 Phase 1 midpoint review — CFO, CMO, and VP Operations review actual split data. If clinical volume exceeds 40%, Phase 2 budget and staffing plans are revised before proceeding.

---

#### Risk 2 — Legacy CMS with No Usable API

**Early warning indicators:**
- IT cannot produce an API specification or data dictionary within 10 business days of engagement start
- CMS vendor confirms no REST or HL7 FHIR API exists in current contract tier

**Contingency plan:**
- Reallocate Phase 1 budget toward custom integration middleware (assess whether $400K total is sufficient)
- Explore batch export + file-based shadow mode as a fallback for Phase 1 comparison logging
- If integration cost exceeds $150K, present re-scoping memo to CFO before committing Phase 2 budget

**Decision point:** Week 2 IT discovery assessment determines Phase 1 architecture. If API-less, Phase 1 timeline and budget [A9] are revised before any development work is committed.

---

#### Risk 3 — Regulatory Block on AI-Generated Denials

**Early warning indicators:**
- Legal review identifies one or more operating states with physician authorization requirements for claim denials
- CMO raises additional certification concerns tied to state physician licensing requirements

**Contingency plan:**
- Redesign Fast Path to issue approvals only; all potential denials route to Clinical Path queue for physician sign-off
- Revise CFO financial model: reduced throughput gain on denial-heavy claim types narrows headcount reduction target
- Document compliance rationale for Fast Path approval decisions to preserve available ROI

**Decision point:** Day 30 legal review complete. If denial authority is blocked, CFO presents revised ROI to board before Phase 2 budget is formally committed.

---

#### Risk 4 — False-Negative Rate Cannot Reach <2%

**Early warning indicators:**
- Day 30 shadow mode: false-negative rate above 5% with no downward trend
- Clinical criteria taxonomy [U8] still under active dispute with Dr. Webb at Day 20

**Contingency plan:**
- Extend Phase 1 by 30 days; re-engage Dr. Webb to tighten and operationalize flagging criteria
- If rate remains ≥2% at Day 90, launch Clinical Path only (pre-screening and summaries, no Fast Path adjudication)
- CMO and CFO review adjusted timeline and reduced financial impact before any further spend

**Decision point:** Day 60 formal Phase 1 gate review. Go/no-go is a hard binary: <2% proceeds to Phase 2; ≥2% does not.

---

## 6. MVP Scope

### MVP Objectives

The MVP is the smallest set of capabilities that closes the daily capacity deficit and validates the dual-path architecture before Phase 3 steady-state commitment:

1. **Hypothesis validation (Phase 1):** Confirm that ≥65% of claims are non-clinical [A2] and that clinical flagging achieves <2% false-negative rate [A6] on real claim data before any live adjudication begins
2. **Capacity deficit closure (Phase 2):** Fast Path handles ≥65% of daily volume end-to-end; Clinical Path pre-screening enables physician review at ≥20 claims/hour [A5]
3. **SLA compliance:** Both paths deliver ≤7-day average cycle time, eliminating active payer penalty exposure [A8]

**Hypotheses being tested:**
- 65% of claims are administrative and AI-adjudicable without physician review [A2]
- Clinical flagging achieves <2% false-negative rate after Phase 1 tuning [A6]
- Physician throughput reaches ≥20 claims/hour with AI-generated pre-screening summaries [A5]
- Fast Path adjudication quality is at least as good as current manual process (denial overturn rate non-regression) [U3]

**"Viable" definition:** The system handles full daily volume [1,667/day, U1] without expanding human review staff, meets the 7-day SLA within 30 days of Phase 2 launch, and demonstrates non-regression on denial quality at the 90-day mark.

---

### Core Features

**1. Claims Ingestion and Format Normalization**
- **Description:** Parse incoming claims (EDI 837, PDF, portal submissions) into a unified internal data model consumed by all downstream agent components
- **Business Value:** The foundation for all agent processing — without normalized data, neither Fast Path nor Clinical Path can operate; enables coverage of the estimated ~30% non-EDI volume [A7]
- **Acceptance Criteria:** 100% of claims parsed within 5 minutes of receipt; EDI 837 parse failure rate <0.1%; PDF extraction quality measured and baseline established in Phase 1; unparseable claims routed to human exception queue with error classification
- **Technical Approach:** EDI 837 library parser; Claude API PDF extraction with structured output schema; unified claim data model; exception queue routing for unrecognized formats
- **Dependencies:** U7 (CMS integration API must be confirmed in Week 1), A7 (actual format distribution validated in Phase 1)
- **Effort Estimate:** L — integration-heavy; 4–6 weeks

**2. Clinical Flagging Engine**
- **Description:** Classify every normalized claim as Fast Path (administrative, no clinical content) or Clinical Path (physician review required) using a criteria taxonomy co-developed with Dr. Webb before Phase 1 begins
- **Business Value:** The patient safety gate — all Fast Path throughput depends on this classification being accurate; false negatives are the CMO's primary concern and the Phase 1 go/no-go gate [A6, U8]
- **Acceptance Criteria:** <2% false-negative rate over 60-day Phase 1 shadow run on ≥200 confirmed clinical claims; conservative default (uncertain or near-threshold cases route to Clinical Path)
- **Technical Approach:** Claude API classification with structured clinical criteria input; confidence scoring; below-threshold claims default to Clinical Path; iteratively tuned against Phase 1 labeled data
- **Dependencies:** U8 (clinical content definition finalized with Dr. Webb before Phase 1); A6 (tuning achievability)
- **Effort Estimate:** M — 3–4 weeks initial + ongoing Phase 1 tuning cycles

**3. Fast Path Administrative Adjudication Agent**
- **Description:** End-to-end adjudication of non-clinical claims: eligibility verification, coding validation, prior auth completeness check, payment determination, and structured audit-trail output
- **Business Value:** Directly eliminates the ~776 claim/day capacity deficit; primary source of $520K/year labor savings [A1] and payer penalty avoidance [A8]; target ≥65% of daily volume processed without human review [A2]
- **Acceptance Criteria:** Structured adjudication output (decision + rationale + confidence) for 100% of Fast Path claims; denial overturn rate ≤41% within 90 days of live launch (non-regression gate); escalation rate to human review ≤5%; Fast Path average cycle time ≤4 days
- **Technical Approach:** Multi-step Claude agent with tool calls for eligibility lookup, coding cross-reference, prior auth rules; structured output with full audit trail; confidence-below-threshold escalation to human exception queue
- **Dependencies:** Feature 1 (normalized claim), Feature 2 (confirmed non-clinical routing), U3 (overturn rate root cause informs adjudication rules), U5/A11 (denial authority legally confirmed before spec is written)
- **Effort Estimate:** XL — core agent, business rules, exception handling; 6–8 weeks

**4. Clinical Path Pre-Screening and Summary Generation**
- **Description:** Generate a structured, physician-ready summary for each Clinical Path claim: clinical data highlights, medical necessity context, coding flags, prior auth status, and recommended review focus areas
- **Business Value:** Enables Dr. Webb's confirmed 20-claims/hour throughput — without pre-screening, physicians read full files and the Clinical Path cannot maintain the 7-day SLA at any feasible headcount [A5, A10]; eliminates the physician bottleneck that would otherwise make the dual-path architecture unworkable
- **Acceptance Criteria:** Summary generated within 30 seconds per claim; physician review rate ≥15 claims/hour measured in Phase 2 days 1–30 (target: 20/hour); physician summary quality rating ≥3.5/5 in 30-day survey; Clinical Path average cycle time ≤7 days
- **Technical Approach:** Claude API structured extraction from normalized claim to standardized summary template (co-designed with Dr. Webb as part of U8 taxonomy work); lightweight web-based physician review queue interface
- **Dependencies:** Feature 1 (normalized claim), Feature 2 (routing classification), U2 (physician headcount confirmed before Phase 2 capacity planning), U8 (clinical criteria)
- **Effort Estimate:** L — 4–5 weeks including template co-design and basic physician interface

**5. Shadow Mode Infrastructure and Phase 1 Audit Dashboard**
- **Description:** Parallel agent pipeline running all incoming claims through adjudication logic without executing decisions; comparison logs capture agent decision vs. actual processor decision for each claim; a real-time dashboard tracks false-negative rate, decision concordance, and processing volume metrics
- **Business Value:** The validation mechanism for the Phase 1 gate — without it there is no data-driven basis for the Phase 2 go/no-go decision; also generates the labeled dataset for ongoing clinical flagging tuning and post-launch audit
- **Acceptance Criteria:** 100% of incoming claims processed in shadow mode with decisions logged; false-negative rate calculated and dashboard-visible within 24 hours of each claim decision; 60-day Phase 1 gate report auto-generated with full statistical summary; audit log retained for CMO and CFO review
- **Technical Approach:** Agent pipeline in null-execution mode with full decision logging; comparison log to structured database; lightweight dashboard (Metabase or equivalent); automated 60-day audit report export
- **Dependencies:** U7 (CMS integration required for real-time claim data access), U1 (actual daily volume confirmed for statistical sample sizing)
- **Effort Estimate:** M — 3–4 weeks

---

## 7. Out of Scope

**1. Physician Review Workflow Interface**
- **Why Out of Scope:** Phase 1 requires only shadow mode validation; the web interface for physicians to receive, review, and act on AI-generated summaries is a Phase 2 build dependency, not a Phase 1 one; building it before summary quality is validated adds cost without contributing to the go/no-go gate (Timing)
- **Future Consideration:** Required for Phase 2 Clinical Path launch; interface design should be informed by physician feedback on summary content and structure gathered during Phase 1 dry runs; clinical usability testing recommended before building

**2. Denial Appeal Workflow Automation**
- **Why Out of Scope:** The root cause of the 41% overturn rate is unknown [U3]; automating the appeal response workflow before the source of first-pass errors is understood risks encoding and scaling those errors; appeal volume and character also depend on Fast Path adjudication quality, which is unknown until Phase 2 delivers real data (Uncertainty)
- **Future Consideration:** Phase 3 candidate if Fast Path denial accuracy is confirmed and overturn rate drops below 25%; would materially reduce administrative rework and cycle time on the appeal path

**3. Provider Portal Integration for Claim Status Feedback**
- **Why Out of Scope:** Providers benefit most from accurate and fast adjudication; real-time status feedback is a quality-of-service enhancement that does not affect cycle time, SLA compliance, or the Phase 1 gate; CMS integration [U7] must be established before extending outbound integrations (Dependencies)
- **Future Consideration:** High provider satisfaction and cash flow value; Phase 3 or post-MVP; design informed by the CMS API surface confirmed in Phase 1 integration work

**4. Claims Analytics Data Warehouse**
- **Why Out of Scope:** Phase 1 audit dashboard requires decision comparison logs, not a full analytics platform; a data warehouse for historical quality analysis and actuarial use is a strategic investment that does not contribute to the 7-day SLA or 8-FTE reduction targets within the $400K budget [A9] (Resources / Timing)
- **Future Consideration:** Natural Phase 3 investment once the agent generates structured, labeled adjudication data at scale; lays the foundation for quality improvement, fraud detection, and population health analytics

**5. Multi-Region Deployment and Disaster Recovery Infrastructure**
- **Why Out of Scope:** Phase 1 is shadow mode with no production decisions; Phase 2 is a single-site operational deployment; multi-region DR adds infrastructure cost and engineering complexity before the MVP architecture is even validated (Complexity / Timing)
- **Future Consideration:** Required before enterprise-wide deployment or HIPAA-mandated high-availability SLA; Phase 3 architecture review should specify DR requirements and budget separately from the claims AI system

---

### Future Roadmap (Phase 3 and Beyond)

- Physician review interface with EHR-adjacent workflow integration
- Denial appeal triage and response automation (after U3 root cause is resolved)
- Provider-facing claim status API
- Claims quality analytics and adjudication trend dashboards
- Multi-region HA deployment with formal DR testing

---

## 8. Assumptions Management

Three new assumptions were identified through this scope analysis. Full entries are in `specs/assumptions.md` (A11–A13).

| ID | Description | Value | Confidence | Must Validate By |
|---|---|---|---|---|
| A11 | AI Fast Path denials are legally permissible without per-claim physician sign-off | Assumed permissible pending legal review | Low (45%) | **Day 30 of engagement** |
| A12 | Claims management system has a usable read/write API for Phase 1 integration | Assumed present pending IT assessment | Low (40%) | **Week 2 IT discovery sprint** |
| A13 | Admin processors remain cooperative and productive through Phase 1 shadow mode | Assumed; depends on clear HR communication | Medium (65%) | Before Phase 1 launch |

**Critical dependency:** A11 and A12 are the two highest-urgency new assumptions in this document. Both must be validated in the first two weeks of engagement. If A11 fails (denials require physician sign-off), the Fast Path specification must be revised before build begins. If A12 fails (no CMS API), the Phase 1 architecture and budget [A9] require revision before any development is committed.

---

*End of document. See `specs/assumptions.md` for full assumption register including A1–A13.*
