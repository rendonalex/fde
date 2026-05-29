# Engagement Intake & Scope Definition — MedFlex Agentic Transformation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Context](#2-business-context)
   - 2.1 [Problem Statement](#21-problem-statement)
   - 2.2 [Current State](#22-current-state)
   - 2.3 [Desired Future State](#23-desired-future-state)
   - 2.4 [Strategic Alignment](#24-strategic-alignment)
   - 2.5 [Success Metrics](#25-success-metrics)
   - 2.6 [Business Value](#26-business-value)
   - 2.7 [Timeline & Urgency](#27-timeline--urgency)
3. [Stakeholder Map](#3-stakeholder-map)
4. [Constraints](#4-constraints)
5. [Risks](#5-risks)
6. [MVP Scope](#6-mvp-scope)
7. [Out of Scope](#7-out-of-scope)

---

## 1. Executive Summary

MedFlex is a 200-person healthcare staffing agency with $14M in annual revenue and a board-mandated target of $200M in 24 months — a 14.3x growth requirement. The path to that target runs through a single operational bottleneck: shift-matching response latency. Eight coordinators manually processing free-text requests in ServiceNow produce a 4.2-hour average fill time in a market where the fastest credible response wins the placement.

The 8-week engagement must deliver a working increment — not a full transformation — that demonstrably improves fill time, builds coordinator trust (two prior AI projects failed due to accuracy gaps and staff resistance), and validates the revenue recovery hypothesis before further investment. The MVP is an AI-assisted matching system where coordinators review ranked recommendations rather than doing the search manually: this maintains human oversight while cutting active work per match from ~20 minutes to ~2 minutes and establishing the throughput foundation required for scale.

---

## 2. Business Context

### 2.1 Problem Statement

MedFlex's primary operational constraint is response latency in a winner-takes-first competitive market: at 4.2h average fill time against a <1h target, an estimated 30% of inbound shift requests are lost to faster-responding competitors (A5). The secondary constraint is a throughput ceiling — 8 coordinators at ~23 complete matches each per day cannot reach the ~14x volume required to hit the $200M revenue target without a step-change in automation.

### 2.2 Current State

Eight coordinators manually parse free-text shift requests from ServiceNow, search the nurse database, and cross-reference credentials, availability, and hospital preferences — a process requiring ~20 minutes of active work per match (A1) that accumulates to 4.2h elapsed fill time due to queue depth and manual sequencing. The process produces a 7% credential mismatch rate, a 12% no-show rate (partly driven by passive confirmation: silence treated as acceptance), and an untracked competitive win/loss rate that likely understates revenue leakage.

### 2.3 Desired Future State

Coordinators operate as reviewers — approving AI-ranked candidate recommendations rather than executing the search manually — enabling ≥230 complete matches per coordinator per day (vs. ~23 today) and reducing fill time to <1 hour for ≥90% of standard requests. With the matching bottleneck removed, MedFlex scales shift volume toward the $200M target without proportionally growing the coordination team.

### 2.4 Strategic Alignment

This engagement directly enables the board's 24-month growth mandate by removing the coordination bottleneck, the single most capacity-constrained variable in MedFlex's scale equation. Sub-one-hour fill time also repositions MedFlex commercially: being first-to-respond in a multi-agency competitive market is a revenue multiplier independent of the volume growth target.

### 2.5 Success Metrics

Five metrics from leading to lagging: M1 — fill time ≤60 min for ≥90% of standard requests (baseline: 4.2h); M2 — coordinator throughput ≥230 matches/coordinator/day (baseline: ~23); M3 — incremental revenue from speed recovery ≥$1.5M in 6 months; M4 — addressable no-show rate ≤2.4% (baseline: ~4.8% of addressable segment); M5 — credential mismatch rate ≤2% (baseline: 7%). Full baselines, targets, and measurement methods in `specs/1-problem-framing-and-success-metrics.md`.

### 2.6 Business Value

Total addressable improvement at current scale is ~$5.6M/year: competitive speed recovery (~$3M), no-show reduction (~$1.65M), and mismatch elimination (~$975K). The primary long-term value is the throughput multiplier — without AI-assisted matching, reaching $200M requires scaling from 8 to ~112 coordinators at ~$6.2M additional annual labor cost and a 3-month ramp lag per hire (A7, A8).

### 2.7 Timeline & Urgency

The 8-week timeline is CEO-driven and tied to a Series B growth commitment — Marcus expects the engagement to "start getting money back" within the window, not at full deployment. Every week at 4.2h fill time is a week of continued competitive losses in a market where the fastest-responding agency wins. *[Rev. 2026-05-13 — CEO Pushback]* The primary milestone within the 8-week engagement is a 6-week board demo: Features 1–4 live on real shift requests, with a ranked shortlist visible to coordinators and end-to-end timestamps on each stage of the pipeline. Feature 5 is Wave 2. See `specs/06-client-feedback.md` Item 1 for the full 6-week scope definition.

---

## 3. Stakeholder Map

| Stakeholder | Role / Title | Influence | Interest | Primary Concerns | Engagement Strategy |
|---|---|:---:|:---:|---|---|
| Marcus Reyes | CEO / Executive Sponsor | H | H | $200M growth mandate, ROI speed, prior AI failures, no technical depth | Weekly alignment; frame every decision in terms of revenue and risk, not technical detail |
| Head of Operations | Ops Lead (unnamed) | H | H | Process accuracy, data access, coordinator capacity, system feasibility | Must engage in week 1; Marcus deferred all operational/data questions to this person — engagement is blocked without them |
| 8 Coordinators | Shift Matching Team | M | H | Job security, tool usability, being blamed for AI errors | Shadow session before finalizing architecture; position AI as "matching superpower" — coordinator remains decision-maker in MVP |
| Compliance Team | Credential Verification | L | M | Regulatory correctness at scale, handoff clarity | Brief on v1 scope boundary; flag v2 dependency when volume scales to 14x |
| Hospital Partners | B2B Clients (indirect) | L | H | Reliable and fast response, low no-show rate | Not in engagement scope; their satisfaction is the lagging indicator for M1, M4, M5 |
| Nurses (pool) | B2C Workforce (indirect) | L | L | Schedule clarity, notification reliability | Not in engagement scope; impacted by Shift Confirmation Notifier (Wave 2 Feature 5, deferred from MVP — *Rev. 2026-05-13 — CEO Pushback*) |
| FDE Delivery Team | Technical Delivery | M | H | Spec precision, data access, scope discipline | Internal; owns specification lifecycle and build-loop oversight |

**Key considerations:**
- Marcus holds all veto authority. Head of Operations has de facto veto on operational feasibility.
- Coordinators are the highest-risk blockers: the recommendation engine failure was partly attributed to job-security fears and insufficient training. No coordinator has been briefed on this engagement (assumption — Marcus did not confirm otherwise).
- No CTO, no internal engineering team, and no technical point of contact have been named. All infrastructure access depends on Marcus escalating internally.

---

## 4. Constraints

Five most critical constraints for this engagement:

### C1 — ServiceNow Data Quality (Technical)

Inbound shift requests arrive as unstructured free text in ServiceNow — no intake form, no field schema. Matching automation requires LLM parsing with >85% field-level accuracy (A10) before the candidate ranker can operate. Unknown: whether nurse profiles are well-structured or also partially free text (U2). If the underlying nurse database is incomplete, the prerequisite data remediation work is multi-month.

### C2 — Change Management Ceiling (Organizational)

Two prior AI failures — a hospital-facing chatbot rejected for being the wrong channel, and a recommendation engine that collapsed due to accuracy issues and coordinator resistance — mean the organization has a demonstrated rejection pattern for AI that doesn't fit the workflow or earn trust incrementally. A full-autonomy design at launch will face active coordinator resistance and risks a third failure; human-in-the-loop is not optional for MVP.

### C3 — Single POC, No Technical Stakeholder (Resource)

Marcus is the sole point of contact. All operational and technical questions (data schemas, API access, ServiceNow configuration, notification system capabilities) were deferred to a Head of Operations who is not yet in the engagement. Without operational access, critical unknowns U2, U4, U7, and U9 cannot be resolved, and specifications will rest on unvalidated assumptions.

### C4 — 8-Week Scope with Undefined "Done" (Timeline)

Marcus's expectation for week 8 is to "start getting money back" — a working ROI-generating increment, not full production deployment. The definition of what constitutes a shippable 8-week increment has not been aligned on (U10). Without this alignment by week 1, the engagement risks delivering something Marcus considers incomplete or something the FDE team over-engineers.

### C5 — Passive Nurse Confirmation Model (Technical/Operational)

Nurses are notified of placements by SMS/email, and silence is treated as acceptance. No explicit acknowledgment is captured. This creates the addressable portion of the 12% no-show rate and constrains any confirmation automation: building response tracking requires either a change to the notification system or a new workflow — both depend on infrastructure access not yet confirmed (U4).

---

## 5. Risks

| Risk | Category | Probability | Impact | Mitigation Strategy | Owner | Status |
|---|---|:---:|:---:|---|---|---|
| Coordinator resistance causes third AI failure | Organizational | H | H | Launch in human-in-the-loop mode; conduct shadow session before architecture; communicate AI as amplifier, not replacement | FDE Lead | Open |
| ServiceNow data not parseable at >85% accuracy (A10 fails) | Technical | M | H | LLM parsing pilot on real data in week 1 before committing to matching architecture; structured intake overlay as contingency | FDE Lead | Open |
| Head of Operations unavailable; critical unknowns block spec | Resource | M | H | Escalate to Marcus in week 1 as a go/no-go dependency; document what cannot be specified without ops access | FDE Lead | Open |
| A5/A6 assumptions wrong; revenue case is overstated | Delivery | H | M | Instrument win/loss tracking from day 1; treat M3 as a hypothesis-validation metric, not a committed target | Marcus | Open |
| Scope creep into compliance, nurse app, or pricing | Delivery | M | M | Maintain explicit out-of-scope list; any expansion request requires revised timeline and cost estimate before acceptance | FDE Lead | Open |

---

### High-Risk Mitigations in Detail

**R1 — Coordinator Resistance (Probability: H / Impact: H)**

- **Early warning indicators**: Coordinator shadow session denied or coordinators express that they don't want to participate; Marcus cannot confirm whether coordinators know this engagement has started.
- **Contingency plan**: Pilot with 1–2 volunteer coordinators only; reduce AI autonomy thresholds; increase minimum human review requirement until trust builds.
- **Decision point / escalation**: If no coordinator buy-in by week 3, escalate to Marcus and reassess the week-8 definition of done — the MVP may need to be scoped to the parser alone.

**R2 — ServiceNow Data Quality Failure (Probability: M / Impact: H)**

- **Early warning indicators**: LLM parsing pilot on 100 real shift request records shows <75% field-level accuracy; nurse profiles contain significant null or free-text fields.
- **Contingency plan**: Propose a structured intake overlay (template-guided email form sent to hospitals as a first step) that standardizes input before it hits ServiceNow — this recovers parser accuracy but adds 2–3 weeks to MVP timeline.
- **Decision point**: Data quality assessment result by end of week 2; if unacceptable, revise architecture scope before starting the ranker build.

**R3 — Head of Operations Unavailable (Probability: M / Impact: H)** *[Rev. 2026-05-13 — CEO Pushback]*

- **Early warning indicators**: Marcus cannot provide a ServiceNow data export, nurse profile schema, or ServiceNow admin contact name by end of week 1.
- **Contingency plan**: Week 1 does not require the Head of Operations. Required from Marcus directly: (1) ServiceNow data export (200–300 historical shift records), (2) nurse profile field list or screenshot, (3) ServiceNow admin contact for API credentials. Head of Operations needed only for: API credentials setup (week 2–3) and coordinator shadow session (week 4). If live ServiceNow write API access is not provisioned by end of week 3, the week 6 deliverable scopes to parser + rule-based ranker prototype tested against a static nurse database snapshot — not live on real matches.
- **Decision point**: Read API access confirmed by end of week 2; write API access confirmed by end of week 3 (gates Features 3 and 4 simultaneously per A11-write). If neither is achieved, the floor case is named explicitly to Marcus, not absorbed quietly into the scope.

---

## 6. MVP Scope

### MVP Objectives

- Deliver a working human-in-the-loop matching increment that measurably reduces fill time to <1 hour for standard requests within the 8-week window
- Validate A10 (parser accuracy) and begin validating A5/A6 (competitive speed recovery) in live operating conditions
- Build coordinator trust before increasing AI autonomy — the MVP succeeds if coordinators *use* it, not only if the metrics improve
- "Viable" means: coordinators adopt the tool, fill time drops, and no trust collapse occurs

### Core Features (Must-Have)

---

**1. Shift Request Parser**

- **Description**: LLM-based extraction of structured fields (specialty, date/time, location, credential requirements) from free-text ServiceNow shift requests into a structured object for downstream processing
- **Business Value**: Eliminates the first manual parsing step that creates queue delay and inconsistency; prerequisite for all downstream automation
- **Acceptance Criteria**: ≥85% field-level extraction accuracy on a 200-request held-out validation set from real ServiceNow data; low-confidence parses (below configurable threshold) routed to coordinator review queue rather than auto-processed
- **Technical Approach**: Claude API with domain-specific system prompt; structured JSON output with confidence scores per field; ServiceNow webhook or polling integration; confidence-threshold routing logic
- **Effort Estimate**: Medium (2–3 weeks including data validation)
- **Dependencies**: ServiceNow read access; real shift request samples for prompt tuning (U2)

---

**2. AI Candidate Ranker**

- **Description**: Automated scoring and ranking of qualified nurse candidates against a parsed shift request, based on credential match, availability, proximity, and hospital preference history
- **Business Value**: Reduces coordinator work from 5 candidate evaluations (~20 min per A1, A2) to reviewing a pre-ranked shortlist of 1–3 options (~2 min); this is the primary throughput multiplier
- **Acceptance Criteria**: Top-ranked candidate matches coordinator's final selection ≥70% of the time; ranked shortlist generated in <30 seconds; explanation of ranking visible to coordinator
- **Technical Approach**: Structured query against ServiceNow nurse profile database; multi-factor scoring (credential match, availability window, proximity score, preference history per A12); confidence score output; nurse profile data must be accessible via API (A11)
- **Effort Estimate**: Medium (1–2 weeks) *[Rev. 2026-05-13 — CEO Pushback]* — rule-based scoring only for MVP (no ML dependency, no training data pipeline). The 3–4 week estimate assumed an ML ranker; the MVP ranker is a deterministic weighted formula (credential match 40%, availability 30%, proximity 20%, preference history 10%, per A25) that runs on existing ServiceNow data. ML upgrade is Phase 2 pending A19 labeled data accumulation.
- **Dependencies**: Feature 1 output; ServiceNow nurse database API access (A11); structured hospital preference data (A12/U9)

---

**3. Coordinator Review Interface (Human-in-the-Loop)**

- **Description**: A lightweight dashboard presenting the parsed request summary and ranked candidate shortlist with one-click approve / edit / escalate actions; captures coordinator decisions as training signal
- **Business Value**: Keeps coordinators as decision-makers in MVP — directly addresses the trust and job-security concerns that killed the prior recommendation engine; captures feedback data for model improvement
- **Acceptance Criteria**: Coordinator can review and approve or edit a match in ≤2 minutes; edge cases (confidence below threshold, no qualifying candidates) route to a senior coordinator escalation queue; all coordinator decisions logged
- **Technical Approach**: Minimal web UI (or ServiceNow embedded widget) over ServiceNow API; confidence-threshold routing — above threshold shows ranked shortlist for one-click approval, below threshold flags for manual review
- **Effort Estimate**: ~1 week for core interface build *[Rev. 2026-05-13 — CEO Pushback]* — compresses from 2–3 weeks because ServiceNow APIs are built upstream in the same sprint (weeks 4–5); interface scoped to: display ranked shortlist, approve/edit selection, escalate. Coordinator UAT session is still required at week 4–5 and is not optional (see R1).
- **Dependencies**: Features 1 and 2; Head of Operations involvement for coordinator UAT session

---

**4. Automated Match Submission**

- **Description**: System submits the coordinator-approved candidate to the hospital via the existing ServiceNow workflow with full event audit trail (parse → rank → review → submission timestamps)
- **Business Value**: Closes the loop from request intake to hospital submission without manual copy-paste; enables precise M1 (fill time) measurement with sub-second timestamp resolution
- **Acceptance Criteria**: Submission occurs within 60 seconds of coordinator approval; audit log captures all four event timestamps per match; submission format matches current hospital-facing output
- **Technical Approach**: ServiceNow write API; submission formatted to existing hospital-facing template (A11)
- **Effort Estimate**: Small (1 week; dependent on ServiceNow write API access)
- **Dependencies**: Feature 3 approval event; ServiceNow write API credentials (A11)

---

**5. Shift Confirmation Notifier** *(Deferred to Wave 2 — Rev. 2026-05-13 — CEO Pushback)*

- **Description**: Automated proactive confirmation request sent to the assigned nurse 48h and 24h before shift start, requiring explicit acknowledgment rather than passive silence-as-acceptance
- **Business Value**: Reduces the addressable ~4.8% no-show rate (A9); creates the first explicit confirmation record in the system; enables empirical measurement of M4 via A/B comparison
- **Acceptance Criteria**: Confirmation request sent to 100% of assigned nurses at T-48h and T-24h; nurse response (acknowledged / declined / no response) captured in ServiceNow; no-show outcome tracked per shift
- **Technical Approach**: Triggered notification from ServiceNow at T-48h and T-24h; response tracking via inbound webhook or reply-code SMS/email; dependent on whether current notification infrastructure supports response capture (U4)
- **Effort Estimate**: Medium (2–3 weeks)
- **Dependency Risk**: **HIGH** — U4 (bidirectional notification infrastructure) is unresolved within the 6-week window. *[Rev. 2026-05-13 — CEO Pushback]* Feature 5 is explicitly out of 6-week MVP scope and deferred to Wave 2. MT-5.1/5.2 (hospital response monitoring + initial nurse placement notification) remain in Wave 1 as JtD-5a. Wave 1 instruments M4 tracking baseline; the M4 intervention (Feature 5) is Wave 2 pending U4 resolution.

---

## 7. Out of Scope

---

**1. Hospital-Facing Submission Portal**

- **Why Out of Scope**: Explicitly excluded in the scenario brief; hospitals submit via email, portal, and phone today — changing the submission channel is not in this engagement's mandate
- **Future Consideration**: A structured intake template (guided email form) could materially improve parser accuracy at scale; candidate for Phase 2 as an optional upgrade path for high-volume hospital partners

---

**2. Nurse-Facing Mobile App**

- **Why Out of Scope**: Explicitly excluded in the scenario brief; nurses are reached by SMS/email today — building a new communication channel is out of scope and exceeds 8-week budget and timeline
- **Future Consideration**: Phase 2, if nurse-side experience becomes a meaningful no-show reduction lever once Confirmation Notifier data is collected

---

**3. Compliance Process Automation**

- **Why Out of Scope**: Marcus explicitly confirmed compliance verification is a separate team's responsibility and "not an issue" for this engagement; coordinator workflow reads pre-validated credential status from nurse profiles without re-verifying
- **Future Consideration**: Named as a v2 dependency — at 14x shift volume, the compliance team faces 14x load; API-based credential freshness checking is the logical next bottleneck once matching is automated

---

**4. Pricing Engine / Margin Optimization**

- **Why Out of Scope**: Explicitly excluded in the scenario brief; the agent submits a candidate match — pricing and margin are MedFlex's existing bilateral process with hospitals and are not part of the coordinator workflow
- **Future Consideration**: Outside the FDE engagement scope under any foreseeable roadmap

---

**5. Full Change Management Program**

- **Why Out of Scope**: A complete organizational change program (role redesign, retraining curriculum, performance management updates, coordinator career pathing) requires HR engagement and a timeline that exceeds 8 weeks; FDE scope covers tool delivery and coordinator onboarding to the MVP workflow
- **Future Consideration**: Phase 2 must include a structured adoption program if MVP data validates coordinator buy-in is achievable — without this, scaling AI autonomy will face the same resistance that ended the recommendation engine

---

*See `specs/assumptions.md` for all assumptions referenced in this document (A1–A15).*
