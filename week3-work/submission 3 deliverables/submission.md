# Problem Framing & Success Metrics — MedFlex Agentic Transformation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
   - 2.1 [What Was Asked vs. What Is Actually Needed](#21-what-was-asked-vs-what-is-actually-needed)
   - 2.2 [Current State Quantification](#22-current-state-quantification)
   - 2.3 [Stakeholder Perspectives](#23-stakeholder-perspectives)
   - 2.4 [Constraints](#24-constraints)
3. [Success Metrics](#3-success-metrics)
4. [Critical Unknowns](#4-critical-unknowns)

---

## 1. Executive Summary

MedFlex is a 200-person healthcare staffing agency running $14M in annual revenue against a 24-month board mandate to reach $200M — a 14.3x growth target. The core operational constraint is a shift-matching process that takes 4.2 hours on average in a market where speed determines who fills the shift. Eight coordinators manually process ~120 matching decisions each per day against free-text inbound requests in ServiceNow, producing a 7% credential mismatch rate and a 12% no-show rate. The CEO has framed this as "10x the business without 10x-ing the coordinators" and is asking for an agentic workflow transformation.

The stated request is correct in direction but incomplete in diagnosis. The primary constraint is not *administrative overload* — it is **response latency in a winner-takes-first competitive market**. The secondary constraint is **throughput capacity**: the current human-labor ceiling cannot reach 14x shift volume without a step-change in automation. A third, underappreciated constraint is **change management risk**: two prior AI projects failed (a chatbot rejected by hospital staff; a recommendation engine with unacceptable error rates), and coordinators have explicit job-security concerns.

A technically sound agentic architecture that ships without a trust-building strategy will fail a third time. The 8-week engagement must deliver a working increment that coordinators *use*, not a full transformation they *reject*.

---

## 2. Problem Statement

### 2.1 What Was Asked vs. What Is Actually Needed

**What Marcus asked for**: Design the agentic transformation of MedFlex's matching + compliance + coordination workflow.

**What the evidence shows MedFlex actually needs**:

1. **A speed intervention first.** The 4.2-hour fill time is the primary revenue leak. Hospitals submit requests to multiple agencies simultaneously; the first credible match wins. Every hour of delay is a competitive loss (A5). Agentic automation is one path to <1 hour — but the mechanism matters: it is automated *candidate retrieval and scoring* that unlocks speed, not full end-to-end autonomy.

2. **A throughput multiplier, not just an efficiency gain.** To go from $14M to $200M (14.3x), the matching operation must handle ~14x the current volume (~2,600 fills/day from the current ~184, per A3 and A4) with the same 8-coordinator team. This requires AI to handle the bulk of work per match, with coordinators shifting from *doing* the matching to *reviewing and escalating* AI recommendations. At 2 minutes of coordinator review per match (down from 20 minutes per A1), 8 coordinators could theoretically handle ~1,920 reviews/day — approaching the required scale.

3. **A compliance non-problem correctly scoped out.** Marcus and the discovery session both confirmed that credential verification is handled by a separate compliance team before a nurse enters the roster. Coordinators do not re-verify credentials — they read pre-validated status from the nurse profile. Compliance is not the coordinator's bottleneck. Automating credential re-verification is not in v1 scope and was explicitly deprioritized by Marcus.

4. **A no-show mitigation that addresses root cause.** The 12% no-show rate (A9: ~60% attributable to competitive poaching via passive confirmation) is *not* primarily a matching quality problem. It is a commitment-gap problem: nurses are notified by SMS/email and silence is treated as acceptance. An automated early-confirmation workflow (ask for explicit acknowledgment 48h and 24h before shift) may reduce the portion of no-shows MedFlex can actually influence — but will not eliminate competitive poaching.

5. **A change management strategy, not just a technical deployment.** The recommendation engine failure was attributed to inaccuracy *and* lack of staff training and trust, compounded by job-security fears. Any agentic design that removes coordinators from the loop entirely in week one will face the same resistance. A confidence-scored, human-in-the-loop design that starts coordinators as reviewers and progressively increases AI autonomy is lower risk than a full handover.

---

### 2.2 Current State Quantification

All figures drawn directly from scenario and discovery unless labeled with an assumption reference (Ax).

| Metric | Current Value | Source |
|---|---|---|
| Coordinators | 8 | Scenario |
| Matching decisions per coordinator/day | ~120 | Scenario |
| Total daily matching decisions | ~960 | Scenario (8 × 120) |
| Average time to fill (request → placement) | 4.2 hours | Scenario |
| Target time to fill | <1 hour | Scenario |
| Credential mismatch rate | 7% | Scenario |
| No-show rate | 12% | Scenario |
| Current annual revenue | $14M | Discovery |
| 24-month revenue target | $200M | Discovery |
| Growth required | 14.3× | Derived |
| Active coordinator work per match | ~20 min | A1 |
| Candidate evaluations per match | ~5 | A2 |
| Estimated filled shifts per day | ~184 | A4 |
| Agency revenue per filled shift | ~$300 | A3 |
| Coordinator fully-loaded annual cost | ~$55,000 | A7 |
| Total coordination labor cost (8 FTEs) | ~$440,000/year | A7 |

**Revenue at risk from known inefficiencies (at current scale):**

- **Mismatch rate**: 7% × 184 fills/day = 13 failed placements/day × $300 × 250 days = **~$975K/year** in missed revenue (A3, A4)
- **No-show rate**: 12% × 184 = 22 no-shows/day. Each no-show is lost revenue plus emergency re-fill cost. Conservatively: 22 × $300 × 250 = **~$1.65M/year** in lost placement revenue (A3, A4)
- **Slow response (competitive loss)**: If 30% of inbound requests are lost to faster competitors (A5) and recovering half requires <1h fill time (A6): 184 current fills / 0.70 × 0.30 × 0.50 = **~40 additional fills/day recoverable** = 40 × $300 × 250 = **~$3M/year** in addressable revenue (A3, A5, A6)

**Total addressable improvement at current scale: ~$5.6M/year** — a 40% revenue uplift before any volume scaling. This is the floor-case business case for automation.

---

### 2.3 Stakeholder Perspectives

**Marcus Reyes (CEO) — business perspective**

The problem is growth velocity. The board has a 24-month, $200M revenue commitment following a Series B. At $14M today, reaching $200M requires either (a) growing the coordinator team 14x (from 8 to 112 people, at ~$6M additional annual labor cost, with 3-month ramp-ups per A8), or (b) making each coordinator capable of handling 14x the work through automation. Option (a) is not viable at the growth rate required. Option (b) requires AI. The secondary concern is the two prior AI failures — Marcus needs a result that works, builds trust, and doesn't become a third failed project.

**Coordinators — operational perspective**

The problem is cognitive load and inconsistency. Coordinators spend their day manually cross-referencing free-text shift requests against nurse profiles in ServiceNow — matching specialty, availability, proximity, and hospital preferences. Senior coordinators have built pattern recognition over 10+ years; junior coordinators take significantly longer per match. The process produces inconsistent quality (7% mismatch) and creates a competitive disadvantage (4.2h response). These workers also have legitimate concerns about job security in an AI transformation — a concern Marcus acknowledged and that the prior recommendation engine failure has primed.

**Hospitals (indirect stakeholders, not in engagement scope)**

The problem is reliability. Hospitals submit shift requests to multiple agencies and select the fastest credible response. A 7% mismatch rate and 12% no-show rate create operational risk for hospitals. Better matching quality and proactive no-show mitigation would strengthen MedFlex's position as a preferred supplier — a commercial lever noted in the discovery session.

---

### 2.4 Constraints

**Explicit (stated in scenario):**
- Out of scope: hospital-facing portal, nurse-facing mobile app, pricing engine, CE renewal automation
- Engagement duration: 8 weeks
- Marcus is the sole point of contact (no CTO, no head of operations in the loop)

**Implicit (identified through analysis):**
- **Change management ceiling**: Two prior AI failures with staff resistance mean the solution must build trust incrementally. Full automation on week one is a risk multiplier, not an accelerant.
- **Data quality**: Inbound shift requests arrive as free text in ServiceNow. There is no structured intake form. Automation requires reliable parsing before matching can work (A10).
- **CEO knowledge boundary**: Marcus explicitly deferred technical and operational detail questions to people not present. Architecture assumptions about data schemas, ServiceNow integration capabilities, and nurse profile completeness cannot be validated through Marcus alone.
- **Competitive market dynamics**: Even with <1h fill time, MedFlex competes against other agencies submitting the same nurses. Speed is necessary but not sufficient — match quality (right nurse, right credentials) is the differentiator once speed parity is achieved.
- **No-show rate partially outside MedFlex's control**: Competitive poaching of nurses (same nurse assigned by two agencies) is inherent to the market structure and cannot be fully resolved by workflow automation.

---

## 3. Success Metrics

Five metrics, organized from leading indicators (process) to lagging indicators (outcome).

---

**M1 — Time to First Credible Match Submission** *(Leading — Speed)*

**Metric**: Elapsed time from a shift request entering ServiceNow to MedFlex's first candidate submission to the hospital.

**Current Baseline**: 4.2 hours average (stated in scenario). Note: this is total calendar time, not coordinator active work time (~20 min per A1). The gap is queue time and multi-step handoffs.

**Target**: ≤60 minutes for ≥90% of standard requests (defined as requests with structured specialty + date + location fields parseable at >85% confidence per A10).

**Measurement Method**: Timestamp delta between ServiceNow ticket creation and hospital submission event log. Requires confirmed logging of submission timestamp in the system of record. Segmented by request complexity (standard vs. non-standard).

**Dependencies**: A1 (current active work time establishes baseline), A10 (parser accuracy determines what counts as "standard").

**Why this matters**: In a winner-takes-first market (discovery confirmed), every hour of latency is a loss event. Reducing from 4.2h to <1h is not an efficiency goal — it is a competitive survival goal at scale.

---

**M2 — Coordinator Effective Throughput** *(Leading — Scale)*

**Metric**: Number of complete shift matches processed per coordinator per 8-hour day (including AI-assisted matches reviewed and submitted, not just unaided manual matches).

**Current Baseline**: ~23 complete matches per coordinator per day (derived from A1, A4). This is the ceiling of manual throughput.

**Target**: ≥230 complete matches per coordinator per day (10x) within 12 months of go-live. This requires AI to reduce coordinator active time per match from ~20 min to ~2 min (review + approve or escalate).

**Measurement Method**: Count of completed match submissions per coordinator ID per day, sourced from ServiceNow workflow logs. Requires attribution of AI-assisted vs. manual matches. Separate tracking for new coordinators (ramp effect per A8).

**Dependencies**: A1 (baseline active time per match), A2 (candidate evaluations per match, reduced to 1 by AI pre-ranking), A7 (labor cost, to show ROI), A8 (ramp time, to plan capacity additions).

**Why this matters**: 10x throughput with 8 coordinators is the operational prerequisite for the $200M revenue target. Without this, MedFlex must hire 112 coordinators — each taking 3 months to ramp (A8), at $55K/year each (A7) = $6.2M additional annual labor cost.

---

**M3 — Incremental Revenue from Speed Recovery** *(Lagging — Revenue)*

**Metric**: Monthly revenue attributable to shift requests that MedFlex wins after reducing fill time to <1 hour, measured against the prior 12-month baseline win rate for the same hospital accounts.

**Current Baseline**: ~$14M annual revenue. Estimated ~$3M/year addressable from competitive speed recovery (A3, A5, A6). At current 4.2h fill time, ~30% of inbound requests are estimated to be lost to competitors (A5).

**Target**: Recover ≥$1.5M in annualized incremental revenue within 6 months of go-live (represents recovering ~50% of the speed-sensitive lost opportunity per A6).

**Measurement Method**: Compare win rate (filled shifts / shift requests received) before and after go-live for the same hospital panel. Requires MedFlex to log all inbound requests, including those ultimately filled by competitors or not filled — currently not confirmed to be tracked.

**Dependencies**: A3 (revenue per shift), A4 (baseline fill volume), A5 (% requests currently lost), A6 (recovery rate from speed improvement). A5 and A6 are low-confidence — this metric will be the first to either validate or invalidate those assumptions.

**Why this matters**: This is the business case metric. If the real competitive loss rate is 10% (not 30% per A5), the incremental revenue case is ~$1M, not $3M, and the ROI timeline changes.

---

**M4 — No-Show Rate (Addressable Segment)** *(Lagging — Quality)*

**Metric**: The rate of nurse no-shows among shifts where MedFlex sent an explicit confirmation request (SMS/email with required acknowledgment) 48 hours before the shift, compared to the current passive-notification baseline.

**Current Baseline**: 12% no-show rate overall (stated in scenario). Estimated ~40% of no-shows are in the addressable segment (not competitive poaching — per A9, ~60% of no-shows are attributed to nurses taking competing agency offers). Addressable baseline: ~4.8% of filled shifts.

**Target**: Reduce the addressable no-show segment by ≥50% (from ~4.8% to ≤2.4%) within 3 months of deploying proactive confirmation workflow.

**Measurement Method**: A/B comparison — shifts with proactive confirmation request sent vs. control group with current passive notification. Requires tracking confirmation response (acknowledged / no response / declined) and actual show-up outcome per shift.

**Dependencies**: A9 (60% of no-shows are competitive poaching, not addressable by confirmation workflow). If A9 is wrong and competitive poaching is only 30% of no-shows, the addressable segment is larger (8.4%) and the target becomes more impactful.

**Why this matters**: At 12% no-show and ~184 fills/day, MedFlex absorbs ~22 last-minute failures per day. Each triggers a hospital notification and emergency re-fill attempt. Even a partial reduction has reputational and operational value. The metric is scoped to the addressable segment to avoid claiming credit for what automation cannot fix.

---

**M5 — Credential Mismatch Rate** *(Lagging — Quality)*

**Metric**: Rate of coordinator submissions rejected by hospitals due to credential or qualification mismatches.

**Current Baseline**: 7% (stated in scenario). At ~184 fills/day baseline, this represents ~13 failed placements/day = ~$975K/year in lost revenue (A3, A4).

**Target**: ≤2% within 6 months of go-live (3.5x quality improvement). This assumes the AI matching system performs systematic credential cross-checks that human coordinators currently do inconsistently across 8 different judgment patterns.

**Measurement Method**: Hospital rejection reason codes in ServiceNow, specifically filtering for "credential mismatch" or "qualification not met" reasons. Requires MedFlex to capture structured rejection reasons today — not confirmed in discovery (currently tracked as aggregate rejected candidates).

**Dependencies**: A2 (baseline mismatch driven partly by evaluating wrong-fit candidates), A10 (parser must extract credential requirements correctly for the system to check against nurse profiles). If the 7% includes hospitals selecting preferred nurses for non-credential reasons (mentioned in discovery), the true credential-mismatch-only rate may be lower than 7% and the target needs adjustment.

**Why this matters**: This is the quality metric most directly under MedFlex's control. It is also the metric where AI has a structural advantage over humans — systematic rule-checking against a credential database does not degrade with fatigue, tenure gaps, or inconsistent judgment.

---

## 4. Critical Unknowns

Ranked by risk: how badly does being wrong about this block the solution design?

---

**U1 — Actual win/loss rate on competitive requests** *(Must resolve before specification)*

What % of inbound requests does MedFlex currently lose to competitors, and for what reason (speed vs. price vs. nurse preference)? This drives the entire revenue-at-stake calculation (A5, A6). If competitive loss is 10% rather than 30%, the financial case shrinks dramatically and the solution priority changes. **Discovery action**: Request 3 months of ServiceNow data showing requests received vs. filled vs. lost.

---

**U2 — ServiceNow data schema and field completeness** *(Must resolve before specification)*

What structured data fields exist in ServiceNow for nurse profiles (credentials, specialty, availability), hospital preferences, and shift requests? How complete are they (% null values)? Discovery confirmed data is in "pretty much raw format" with free text. If the underlying nurse profile database is well-structured and only the intake is free text, the problem is tractable (A10). If nurse profiles are also unstructured or incomplete, the prerequisite data work is multi-month, not multi-week. **Discovery action**: Direct data audit with head of operations, not CEO.

---

**U3 — Real root cause of the 7% mismatch rate** *(Must resolve before specification)*

Is the 7% mismatch driven by coordinators not checking credentials correctly, or by hospitals changing requirements after submission, or by the scenario Marcus described (hospitals sometimes prefer a familiar nurse over a technically better match)? If the mismatch is partly hospitals exercising subjective preference post-submission, an AI system optimized for credential matching will not reduce it to 2% and the M5 target is wrong. **Discovery action**: Pull a sample of rejected submissions and classify rejection reasons.

---

**U4 — Confirmation/acknowledgment mechanism for nurses** *(Can defer, but affects M4)*

Discovery revealed nurses are notified by SMS/email and silence = acceptance. Can the current system be configured to require explicit acknowledgment? Is there an API into the notification system? If nurse confirmation requires building new outbound infrastructure, the no-show mitigation workstream is out of 8-week scope. **Discovery action**: Ask head of operations what system sends nurse notifications and whether it supports response tracking.

---

**U5 — API access to state licensing databases** *(Can defer — compliance is separate team)*

Marcus confirmed compliance verification is a separate team's process and "not an issue." However, at 14x scale, that team will also be 14x loaded. If MedFlex's compliance team doesn't have automated API access to state licensing databases today (5-state region), scaling compliance will become the next bottleneck even if matching is automated. Not in v1 scope, but needs flagging as a v2 dependency. **Discovery action**: Confirm whether compliance team uses API checks or manual portal lookups.

---

**U6 — Coordinator resistance and change management readiness** *(Must resolve before specification)*

Marcus acknowledged that the recommendation engine failure was partly due to lack of training and job-security fears. Have any of the 8 current coordinators been informed an AI engagement has started? What is their current relationship with the ServiceNow tooling? A solution designed without coordinator input risks a third rejection. **Discovery action**: Request one coordinator shadowing session before finalizing the architecture.

---

**U7 — How "120 decisions per coordinator per day" is defined** *(Must resolve before specification)*

Does "120 decisions" mean 120 complete shift placements, or 120 individual sub-tasks within the matching workflow (candidate evaluations, credential checks, availability confirmations)? The answer changes the throughput math by 5x (A1, A2). If each coordinator actually completes 120 full placements per day, the current daily fill volume is 960 — not 184 — and the revenue-per-shift assumption (A3) is wrong by a factor of 5. **Discovery action**: Ask head of operations to define what constitutes a "decision" and time 5–10 real matches.

---

**U8 — Nurse explicit acceptance vs. passive confirmation model** *(Can defer)*

Discovery surfaced a contradiction: nurses are notified of accepted shifts by SMS/email, with silence treated as acceptance, but no-shows are then discovered by the hospital calling MedFlex. Does MedFlex have a record of which nurses explicitly confirmed vs. silently accepted? This data would make the no-show segment analysis (A9) empirical rather than estimated. **Discovery action**: Check ServiceNow for confirmation event records.

---

**U9 — Hospital preference data: structured or tribal knowledge?** *(Can defer)*

Coordinators match on "hospital preferences" — but this data is stored manually and unevenly. Senior coordinators (10+ years) carry hospital-specific preferences in memory. Is this anywhere in the database, or is it entirely in people's heads? If lost when a coordinator leaves, the AI system must learn it from scratch. **Discovery action**: Ask head of operations whether hospital preference profiles exist in any structured format in ServiceNow.

---

**U10 — What "8 weeks" scope actually means to Marcus** *(Must resolve before specification)*

Marcus said he wants the agentic transformation designed in 8 weeks. In the discovery session, when asked what he expects in 8 weeks, he said: "Tell me what is the best to do in 8 weeks so I could get my money back. Starting to get my money back." This is not "full production deployment" — it is a working increment that begins generating ROI. The distinction matters enormously for scoping: a production-ready agentic matching system requires data work (U2), integration work, testing, and coordinator training that almost certainly exceeds 8 weeks. The 8-week deliverable is likely an MVP demonstrating the speed improvement on a subset of request types, with a roadmap to full deployment. **Discovery action**: Align explicitly with Marcus on the definition of "done" at week 8.
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

The 8-week timeline is CEO-driven and tied to a Series B growth commitment — Marcus expects the engagement to "start getting money back" within the window, not at full deployment. Every week at 4.2h fill time is a week of continued competitive losses in a market where the fastest-responding agency wins.

---

## 3. Stakeholder Map

| Stakeholder | Role / Title | Influence | Interest | Primary Concerns | Engagement Strategy |
|---|---|:---:|:---:|---|---|
| Marcus Reyes | CEO / Executive Sponsor | H | H | $200M growth mandate, ROI speed, prior AI failures, no technical depth | Weekly alignment; frame every decision in terms of revenue and risk, not technical detail |
| Head of Operations | Ops Lead (unnamed) | H | H | Process accuracy, data access, coordinator capacity, system feasibility | Must engage in week 1; Marcus deferred all operational/data questions to this person — engagement is blocked without them |
| 8 Coordinators | Shift Matching Team | M | H | Job security, tool usability, being blamed for AI errors | Shadow session before finalizing architecture; position AI as "matching superpower" — coordinator remains decision-maker in MVP |
| Compliance Team | Credential Verification | L | M | Regulatory correctness at scale, handoff clarity | Brief on v1 scope boundary; flag v2 dependency when volume scales to 14x |
| Hospital Partners | B2B Clients (indirect) | L | H | Reliable and fast response, low no-show rate | Not in engagement scope; their satisfaction is the lagging indicator for M1, M4, M5 |
| Nurses (pool) | B2C Workforce (indirect) | L | L | Schedule clarity, notification reliability | Not in engagement scope; impacted by Shift Confirmation Notifier (MVP Feature 5) |
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

**R3 — Head of Operations Unavailable (Probability: M / Impact: H)**

- **Early warning indicators**: Marcus cannot arrange data access or ops introduction by end of week 1.
- **Contingency plan**: Proceed with architecture based on A1–A10 and A11–A15 assumptions; flag all decisions as provisional; limit week-8 deliverable to intake parsing only (feature 1) until data access is granted.
- **Decision point**: If ops access is not confirmed by week 2, formally downscope the 8-week deliverable and reset Marcus's expectations.

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
- **Effort Estimate**: Large (3–4 weeks; highly dependent on data structure quality per U2 and U9)
- **Dependencies**: Feature 1 output; ServiceNow nurse database API access (A11); structured hospital preference data (A12/U9)

---

**3. Coordinator Review Interface (Human-in-the-Loop)**

- **Description**: A lightweight dashboard presenting the parsed request summary and ranked candidate shortlist with one-click approve / edit / escalate actions; captures coordinator decisions as training signal
- **Business Value**: Keeps coordinators as decision-makers in MVP — directly addresses the trust and job-security concerns that killed the prior recommendation engine; captures feedback data for model improvement
- **Acceptance Criteria**: Coordinator can review and approve or edit a match in ≤2 minutes; edge cases (confidence below threshold, no qualifying candidates) route to a senior coordinator escalation queue; all coordinator decisions logged
- **Technical Approach**: Minimal web UI (or ServiceNow embedded widget) over ServiceNow API; confidence-threshold routing — above threshold shows ranked shortlist for one-click approval, below threshold flags for manual review
- **Effort Estimate**: Medium (2–3 weeks including ServiceNow integration and coordinator UAT)
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

**5. Shift Confirmation Notifier**

- **Description**: Automated proactive confirmation request sent to the assigned nurse 48h and 24h before shift start, requiring explicit acknowledgment rather than passive silence-as-acceptance
- **Business Value**: Reduces the addressable ~4.8% no-show rate (A9); creates the first explicit confirmation record in the system; enables empirical measurement of M4 via A/B comparison
- **Acceptance Criteria**: Confirmation request sent to 100% of assigned nurses at T-48h and T-24h; nurse response (acknowledged / declined / no response) captured in ServiceNow; no-show outcome tracked per shift
- **Technical Approach**: Triggered notification from ServiceNow at T-48h and T-24h; response tracking via inbound webhook or reply-code SMS/email; dependent on whether current notification infrastructure supports response capture (U4)
- **Effort Estimate**: Medium (2–3 weeks)
- **Dependency Risk**: **HIGH** — if the nurse notification system cannot be programmatically triggered with response tracking (U4 unresolved), this feature is out of 8-week scope and moves to Phase 2

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
# Agentic Solution Architecture — MedFlex Shift Matching

> Deliverable for ATX Phase 3: Delegation Qualification.
> Input: `specs/cognitive-load-map.md` (6 JtDs, 20 micro-tasks).
> Assumption IDs reference `specs/assumptions.md`; new assumptions A19–A20 added in this session.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Delegation Qualification Framework](#2-delegation-qualification-framework)
3. [Delegation Suitability Matrix](#3-delegation-suitability-matrix)
   - 3.1 [JtD-1 — Shift Intake Parsing](#31-jtd-1--shift-intake-parsing)
   - 3.2 [JtD-2 — Candidate Search & Evaluation](#32-jtd-2--candidate-search--evaluation)
   - 3.3 [JtD-3 — Match Selection](#33-jtd-3--match-selection)
   - 3.4 [JtD-4 — Submission](#34-jtd-4--submission)
   - 3.5 [JtD-5 — Confirmation & Conflict Resolution](#35-jtd-5--confirmation--conflict-resolution)
   - 3.6 [JtD-6 — No-Show Management](#36-jtd-6--no-show-management)
4. [Archetype Summary](#4-archetype-summary)
5. [Trade-off Analysis](#5-trade-off-analysis)
6. [Architecture Implications](#6-architecture-implications)

---

## 1. Executive Summary

The MedFlex coordinator workflow decomposes into six JtDs with meaningfully different delegation profiles. Three findings shape the MVP architecture:

**Finding 1 — JtD-2 and JtD-4 are unconditionally agentic.** Candidate search and submission are deterministic, structured, and fully API-accessible. Automating them removes the operational bulk of coordinator time and the primary source of fill-time latency — independently of whether the ranker performs well.

**Finding 2 — JtD-3 (Match Selection) is the highest-value, hardest delegation target.** Two dimensions score Low (decision determinism, context complexity) because the ranking logic is undocumented and tacit (A18). MVP design must be Agent-led + Human Oversight (coordinator approves the ranker shortlist at BP4), with a clear upgrade path to Fully Agentic as labeled outcome data accumulates (A19). Skipping the HITL guard in MVP would risk a third AI failure (C2, R1).

**Finding 3 — Exception paths are not MVP delegation targets.** JtD-5 conflict resolution and JtD-6 no-show management score multiple Low dimensions simultaneously (input structure, tool coverage, risk). These tasks require human judgment by design; agent value here is data surfacing and structured intake, not autonomous action.

**Critical path to <1h fill time**: Automating JtD-1 (parsing) + JtD-2 (search) removes the queue accumulation and search delay that drives 4.2h fills. JtD-3 HITL at BP4 adds only ~2 minutes. Fill time target is achievable with three JtDs automated and one HITL gate — not requiring full autonomy.

---

## 2. Delegation Qualification Framework

Suitability is scored per JtD on seven dimensions. Scores reflect delegation readiness, not task importance.

| Dimension | High suitability | Low suitability |
|---|---|---|
| **Input structure** | Structured, machine-readable | Unstructured, ambiguous, requires interpretation |
| **Decision determinism** | Clear rules, predictable outputs | Judgment-dependent, contextual, implicit |
| **Tool coverage** | APIs available or buildable | Inaccessible, black-box, or manual |
| **Context complexity** | State can be made explicit | Requires institutional knowledge or relationship history |
| **Exception rate** | Rare, predictable exceptions | Frequent, unpredictable edge cases |
| **Latency constraint** | Batch or async acceptable | Real-time, sub-second response required |
| **Risk/compliance** | Reversible, low consequence | Irreversible, regulated, high-consequence |

**Archetype thresholds** (from ATX Phase 3):
- **Human Only**: ≥3 Low dimensions, especially risk/compliance and decision determinism
- **Human-led + Automation Support**: deterministic sub-tasks automated; judgment stays human
- **Human-led + Agent Support**: agent synthesizes and recommends; human decides
- **Agent-led + Human Oversight**: agent acts; human reviews or approves high-stakes outputs
- **Fully Agentic**: all dimensions Medium or High; volume justifies full delegation

---

## 3. Delegation Suitability Matrix

---

### 3.1 JtD-1 — Shift Intake Parsing

**Micro-tasks**: MT-1.1 (queue triage), MT-1.2 (specialty/schedule parse), MT-1.3 (credential extraction), MT-1.4 (confidence routing)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | L | Free-text hospital requests with no schema; inconsistent formats across email, portal, and phone transcriptions |
| Decision determinism | M | Specialty and credential code mapping follows domain rules (largely teachable); ambiguous requests require hospital clarification |
| Tool coverage | M | ServiceNow webhook/polling is buildable (A11); LLM parsing is feasible at ≥85% accuracy (A10); confidence-threshold routing requires new build |
| Context complexity | M | Domain vocabulary (specialty shorthand, credential names) is encodable in system prompt; no deep institutional knowledge required |
| Exception rate | M | ~15% of parses expected below confidence threshold (A10); non-standard or incomplete requests require escalation (BP1) |
| Latency constraint | M | LLM processing in 2–5 seconds is acceptable for <1h target; sub-second not required |
| Risk/compliance | M | Parse errors propagate to credential mismatches downstream (currently 7%); moderate consequence; recoverable via BP1 human review |

**Archetype**: **Agent-led + Human Oversight**

**Rationale**: The LLM parser runs autonomously on all inbound requests. High-confidence parses proceed to JtD-2 automatically (BP2). Low-confidence parses route to the human review queue (BP1) — coordinator clarifies with hospital and corrects. The only human action is exception resolution, not routine parsing. This directly attacks the first manual step driving fill-time latency (A16: ~35% of coordinator active work).

**Anti-pattern check**: Not a candidate for static rules or RPA. The free-text format (confirmed in discovery: "free text, free text") requires non-deterministic NLP. Templated intake forms would improve accuracy but require hospital behavior change — excluded from MVP scope.

---

### 3.2 JtD-2 — Candidate Search & Evaluation

**Micro-tasks**: MT-2.1 (specialty query), MT-2.2 (availability filter), MT-2.3 (credential expiry), MT-2.4 (proximity scoring), MT-2.5 (hospital preference lookup)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | H | Structured requirement object from JtD-1; nurse profiles contain structured credential fields, availability windows, and location data |
| Decision determinism | H | MT-2.1–2.4 are binary or algorithmic filters; credential expiry is a structured date comparison; proximity is a distance calculation |
| Tool coverage | M | ServiceNow nurse database requires API build (A11); proximity requires geocoding API (low build effort); hospital preference is partially structured (A12) |
| Context complexity | M | MT-2.5 hospital preference history has data gaps (A12: completeness unconfirmed); missing preference records require fallback logic, not judgment |
| Exception rate | M | Stale availability records (~15–20%, A17) cause false positives — candidate appears available but cannot attend; agent must handle gracefully |
| Latency constraint | M | Structured DB query + proximity calculation completes in <5 seconds; not sub-second |
| Risk/compliance | M | MT-2.3 (credential expiry) carries compliance significance; but it is fully deterministic — expiry date is a structured field on the nurse card (confirmed in discovery) |

**Archetype**: **Fully Agentic**

**Rationale**: MT-2.1 through MT-2.4 are deterministic filters with no judgment required. MT-2.5 is a structured lookup with a fallback (if preference data is missing, fall back to MT-2.4 proximity ranking). The combination of six M/H suitability scores and high volume (~184 fills/day requiring ~5 candidate evaluations each = ~920 filter operations/day, A2, A4) makes full automation both safe and economically mandatory. The stale availability issue (A17) is handled via re-queue logic when a candidate fails an availability confirmation — not a reason to add human oversight.

**Anti-pattern check**: MT-2.1–2.4 could theoretically be implemented as a simple SQL query + rules engine without an agent. However, coordinating across five data sources (credential DB, availability, proximity, hospital preference history), handling missing/stale records, and producing a ranked pool with per-candidate confidence flags benefits from an orchestrating agent that can branch on intermediate results.

---

### 3.3 JtD-3 — Match Selection

**Micro-tasks**: MT-3.1 (multi-factor ranking), MT-3.2 (tacit knowledge application), MT-3.4 (submit vs. escalate decision)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | M | Structured candidate pool as input; but ranking criteria are undocumented and vary across 8 coordinators |
| Decision determinism | L | Ranking weights are undocumented; MT-3.2 (tacit knowledge) is entirely unencoded; "feeling" cannot be extracted from coordinator behavior without labeled training data (A18) |
| Tool coverage | L | No API encodes senior coordinator pattern recognition; historical outcome data needed to train a ranking model (A19) — completeness unconfirmed |
| Context complexity | L | Senior coordinators' 10-year institutional knowledge (A18) — hospital specialization, nurse relationship history, competitive timing — is the core decision asset; entirely absent from current systems |
| Exception rate | M | Borderline and escalation cases estimated at 10–20% of total matches (MT-3.4 routing) |
| Latency constraint | M | Ranker scoring in seconds is acceptable; coordinator review at BP4 adds ~2 minutes |
| Risk/compliance | M | Wrong selection = reputational risk + potential relationship damage (no direct financial consequence confirmed); reversible via hospital rejection |

**Archetype (MVP)**: **Agent-led + Human Oversight**

**Archetype (Phase 2, post-training)**: **Fully Agentic** (progressive as ranker accuracy increases)

**Rationale**: Three suitability dimensions score Low (decision determinism, tool coverage, context complexity), disqualifying Fully Agentic for MVP. The agent provides a scored and ranked shortlist of 1–3 candidates with explanation; the coordinator reviews at BP4 and approves or edits before submission. This is the natural HITL boundary identified in the cognitive load map.

The upgrade path is data-driven: as the ranker accumulates labeled selections + outcomes (A19), model accuracy improves and the confidence threshold for auto-submit can be progressively lowered. Marcus explicitly delegated the HITL decision to FDE expertise (A13), and both of his stated concerns — matching accuracy and coordinator adoption — are directly addressed by starting with human oversight.

**Anti-pattern check**: Not a candidate for static rules or RPA. The tacit knowledge in MT-3.2 (A18) is the sole source of senior coordinator speed advantage; replicating it requires ML, not rules. A rules-only ranker produces junior-coordinator-level accuracy with no improvement pathway.

---

### 3.4 JtD-4 — Submission

**Micro-tasks**: MT-4.1 (format, submit & log)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | H | Structured approved-candidate object from JtD-3; templated hospital-facing submission format |
| Decision determinism | H | Pure execution; no judgment; format → submit → log |
| Tool coverage | M | ServiceNow write API required (A11); standard licensed capability; requires provisioning |
| Context complexity | H | No institutional knowledge required; deterministic mapping to submission template |
| Exception rate | L | Rare failures (API error, duplicate submission); handled by standard retry/error logging |
| Latency constraint | M | Seconds acceptable after coordinator approval event at BP4 |
| Risk/compliance | M | Submission is the revenue-generating action; errors are recoverable (submission can be retracted before hospital confirms); not regulated |

**Archetype**: **Fully Agentic**

**Rationale**: Six of seven dimensions score M or H. MT-4.1 is the clearest fully-agentic candidate in the workflow. After coordinator approval at BP4, submission fires automatically with a full event audit trail (parse → rank → review → submission timestamps), enabling precise M1 measurement.

**Anti-pattern check**: This is structurally an RPA task (format + API call). It is included as an agent step rather than a standalone script to maintain a unified event-driven architecture and shared audit trail with JtD-1–3. A separate submission script would fragment observability and make re-entry (BP5 rejection cycle, BP6 emergency re-fill) harder to coordinate.

---

### 3.5 JtD-5 — Confirmation & Conflict Resolution

JtD-5 has two structurally different sub-tasks that warrant separate archetype assignments.

#### Sub-task A — Monitoring & Notification (MT-5.1, MT-5.2)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | H | Binary hospital response (accepted/rejected); notification is templated |
| Decision determinism | H | Accepted → notify nurse; rejected → return to JtD-3 (BP5); no judgment |
| Tool coverage | M | ServiceNow polling/webhook buildable; notification system exists (A14) |
| Context complexity | H | No institutional knowledge required; event-driven routing |
| Exception rate | M | Hospital non-response requires follow-up; rejection triggers re-rank cycle |
| Latency constraint | M | Response polling on short intervals (minutes) is sufficient |
| Risk/compliance | M | Notification accuracy matters for nurse trust; recoverable errors |

**Archetype (MT-5.1/5.2)**: **Fully Agentic**

#### Sub-task B — Decline & Multi-Agency Conflict (MT-5.3, MT-5.4)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | L | Nurse decline requires inbound phone call (no API); multi-agency conflict discovered reactively (no cross-agency visibility) |
| Decision determinism | L | Conflict resolution depends on timing, nurse relationships, and competitive dynamics; no rule set applies |
| Tool coverage | L | No cross-agency coordination API exists; nurse decline has no structured inbound channel (A14 low confidence); conflict detected post-facto |
| Context complexity | L | Requires knowledge of competitive landscape, nurse relationship history, and shift urgency — all unencoded |
| Exception rate | M | ~12% no-show rate includes conflict-driven subset (A9: ~60% of no-shows attributable to passive model + competitive poaching) |
| Latency constraint | L | Time-sensitive — shift window may be closing; sub-hour recovery required |
| Risk/compliance | H | Hospital relationship and patient care continuity at risk; partially irreversible once shift window closes |

**Archetype (MT-5.3/5.4)**: **Human-led + Agent Support**
- Agent surfaces relevant data on trigger: nurse's prior no-show history, available replacement candidates (re-entry to JtD-2), shift timeline status, competing submissions in-flight (A20)
- Human coordinator makes the conflict resolution decision and initiates replacement if needed

**Overall JtD-5 Archetype**: **Human-led + Agent Support** (with fully-agentic sub-path for routine monitoring)

**Rationale**: Sub-task B has three Low-scoring dimensions including risk/compliance and two infrastructure gaps (no decline API, no cross-agency visibility) that cannot be resolved within the 8-week engagement. Attempting to automate MT-5.3/5.4 would require building capabilities that do not exist (inbound structured nurse response, cross-agency deconfliction) and introduce high-consequence errors in low-headroom situations. The safe design is an agent that arms the coordinator with structured data and candidate alternatives, not one that acts autonomously under conflict conditions.

---

### 3.6 JtD-6 — No-Show Management

**Micro-tasks**: MT-6.1 (reactive intake), MT-6.2 (profile update + offboard threshold), MT-6.4 (emergency re-fill)

| Dimension | Score | Rationale |
|---|:---:|---|
| Input structure | L | Hospital reports no-show via inbound phone call; no structured API for intake |
| Decision determinism | M | Profile update rule is partially defined ("too many no-shows → offboard"); MT-6.2 is automatable if threshold is encoded; MT-6.4 re-entry to JtD-1–4 follows a known pattern |
| Tool coverage | M | ServiceNow profile write via API feasible (A11); MT-6.4 re-entry re-uses JtD-1–4 agent pipeline; no automation for MT-6.1 phone intake |
| Context complexity | M | Offboard threshold is informal (confirmed in discovery: "we offboard them if we see it happening too often") — encodable once threshold is defined |
| Exception rate | M | ~12% no-show rate; subset involves concurrent competitive conflicts (A9, A20) |
| Latency constraint | L | Emergency re-fill is time-critical — shift window may have <2 hours remaining |
| Risk/compliance | H | Patient care continuity; hospital relationship; repeated no-shows have commercial consequences (discount given to at least one client, per discovery) |
| | | |

**Archetype**: **Human-led + Automation Support**

**Rationale**: MT-6.1 cannot be automated — it is triggered by an inbound hospital phone call with no structured API. The coordinator receives the call, logs the incident, and the agent takes over for the downstream structured work: MT-6.2 (profile update, check offboard threshold) and MT-6.4 (priority re-entry to the JtD-1–4 pipeline with urgency flag and reduced candidate pool).

The two Low-scoring dimensions (input structure, latency constraint) combined with High risk/compliance preclude anything beyond automation support for this JtD. The emergency re-fill is the highest-stress task in the workflow (MT-6.4: CL:H, TT:H, LC:H) and executes under time constraints that reduce the coordinator's ability to catch agent errors — a further reason for human-in-the-loop throughout.

**Anti-pattern check**: MT-6.2 threshold enforcement is a candidate for simple rules once the offboard threshold is numerically defined. No agent is needed for that specific sub-step; it is included here because it sits within a broader exception-handling JtD where context switching between sub-tasks benefits from orchestration.

---

## 4. Archetype Summary

| JtD | Name | MVP Archetype | Phase 2 Target | Primary Constraint |
|---|---|---|---|---|
| JtD-1 | Shift Intake Parsing | Agent-led + Human Oversight | Agent-led + Human Oversight (stable) | Free-text input structure (L); 15% exception rate |
| JtD-2 | Candidate Search & Evaluation | Fully Agentic | Fully Agentic | Stale availability data (A17); API provisioning (A11) |
| JtD-3 | Match Selection | Agent-led + Human Oversight | Fully Agentic (progressive) | Unencoded tacit knowledge (A18); training data dependency (A19) |
| JtD-4 | Submission | Fully Agentic | Fully Agentic | ServiceNow write API (A11) |
| JtD-5 | Confirmation & Conflict Resolution | Human-led + Agent Support | Human-led + Agent Support (stable for conflict path) | No decline API; no cross-agency visibility; high-consequence errors |
| JtD-6 | No-Show Management | Human-led + Automation Support | Human-led + Automation Support (stable) | Phone intake; emergency time constraints; High risk/compliance |

**Throughput impact by archetype**:
- Fully Agentic JtDs (JtD-2, JtD-4, MT-5.1/5.2): These run without coordinator action; the throughput ceiling is system capacity, not human capacity.
- Agent-led + Human Oversight JtDs (JtD-1 for exceptions, JtD-3): Coordinator action is required only for the review step; time per match drops from ~20 min (A1) to ~2 min at BP4.
- Human-led JtDs (JtD-5 conflicts, JtD-6): Coordinator load is unchanged but is scoped to genuine exception cases, freeing capacity for the high-volume standard path.

---

## 5. Trade-off Analysis

### T1 — JtD-3 MVP HITL vs. Fully Agentic at Launch

**Option A (Selected): Agent-led + Human Oversight**
- Coordinator reviews ranked shortlist at BP4; adds ~2 min per match
- Preserves coordinator trust and job role in MVP (addresses C2, R1)
- Captures coordinator approval decisions as training signal for ranker improvement (A19)
- Risk: Throughput multiplier is smaller (~10× per coordinator vs. theoretical ~50×+ fully agentic)

**Option B (Deferred): Fully Agentic from day 1**
- Eliminates coordinator review step; maximum throughput immediately
- Risk: Third AI failure — Marcus explicitly cited accuracy and coordinator adoption as the two red flags (A13); no training data at launch means ranker accuracy is below coordinator level initially
- Risk: Reputational errors with hospitals are not recoverable within the engagement window
- **Decision: Option A. The 2-minute overhead per match is acceptable given the failure risk of Option B.**

### T2 — JtD-1 Parsing: LLM vs. Structured Intake Overlay

**Option A (Selected): LLM parser on existing free-text input**
- Hospital behavior unchanged; no new submission channel required
- Risk: Accuracy ceiling determined by input ambiguity; sub-85% accuracy requires higher human review rate
- Contingency: If accuracy is below threshold after pilot, propose structured intake template for high-volume hospital partners (out of MVP scope, see `specs/2-engagement-intake-and-scope-definition.md`)

**Option B (Deferred): Structured intake form replacing free text**
- Higher parser accuracy; simpler downstream processing
- Risk: Requires hospitals to change submission behavior; may require commercial negotiation; estimated 2–3 weeks additional MVP timeline
- **Decision: Option A for MVP. Option B as Phase 2 enhancement for high-volume hospital partners.**

### T3 — JtD-2 Stale Availability (A17): Speed vs. Accuracy

**Option A (Selected): Trust availability records; handle staleness reactively**
- Agent queries availability as displayed; re-queues candidate on contact failure
- Faster candidate pool generation; minor re-work when stale record surfaces
- Risk: 15–20% of records may be stale (A17); false positives in candidate pool

**Option B: Freshness check before including candidate in pool**
- Agent pings nurse for availability confirmation before shortlisting
- Lower false-positive rate; increases nurse-facing notification volume
- Risk: Adds latency to candidate pool generation; degrades fill-time metric
- **Decision: Option A. Stale availability is a recoverable failure; latency is not.**

### T4 — JtD-3 Ranker Cold-Start: Rule-Based vs. ML

**Option A (Selected): Rule-based ranker with deterministic scoring at launch**
- Implementable without labeled training data dependency
- Scores on: credential match score, availability confidence, proximity, preference history weight (A12)
- Lower accuracy than trained ML model initially; no personalization for hospital-specific preferences
- Provides immediate value and begins accumulating labeled outcomes (A19) for model training

**Option B: ML ranker at launch**
- Higher accuracy potential; replicates tacit knowledge (A18) if training data is sufficient
- Risk: Dependent on A19 (labeled data availability) — if data is insufficient, launch is blocked or accuracy is poor
- **Decision: Option A at launch (rule-based), with ML upgrade in Phase 2 once A19 is validated. The rule-based ranker is not a permanent solution — it is a viable MVP that does not block the build.**

---

## 6. Architecture Implications

Four structural implications follow from the delegation assignments above:

**1. BP2 is the pipeline gate**: The shift intake parser (JtD-1) produces the structured object that enables all downstream automation. If the parser fails or routes to human review, JtD-2 through JtD-4 cannot proceed for that request. Parser reliability and confidence-threshold calibration are the most critical operational parameters in the system — not the ranker.

**2. BP4 is the designed HITL boundary for MVP**: All fully-agentic downstream work (submission, notification, hospital response monitoring) depends on a single coordinator approval action. This design concentrates human labor at one point, maximizes automation above and below it, and provides a clean audit trail. The boundary is designed to move: as JtD-3 ranker accuracy improves, the confidence threshold for auto-approval can be raised progressively without re-architecting the pipeline.

**3. JtD-3 requires a labeled feedback loop from day 1**: The rule-based ranker selected for MVP (T4) must log coordinator approval/edit decisions and submission outcomes to build the training corpus (A19). This is not optional — without the feedback loop, the upgrade path to ML ranking in Phase 2 is blocked. The coordinator review interface (MVP Feature 3) must capture: ranked shortlist presented, coordinator's final selection, whether coordinator edited the ranking, and submission outcome.

**4. Exception paths must be isolated from the standard pipeline**: JtD-5 conflict resolution and JtD-6 no-show management both involve partial re-entry to JtD-1–4 (BP5 rejection cycle, BP6 emergency re-fill). These re-entry paths must operate on a priority queue that does not block or delay standard in-flight requests. A shared queue without priority routing would cause exception handling to increase queue depth for new requests — compounding the latency problem the system is designed to solve.

---

*See `specs/assumptions.md` for all assumptions referenced in this document (A1–A20).*
# Assumptions

> All assumptions go beyond what is explicitly stated in `scenario.md` and `discovery-session.md`.
> Each entry includes: assumed value, reasoning, and confidence level.

---

## A1 — Active coordinator work time per complete shift match: ~20 minutes

**Assumed value**: 20 minutes of active work per complete end-to-end match (request intake → candidate selection → submission).

**Reasoning**: $14M annual revenue back-solves to ~184 filled shifts/day (see A3, A4). With 8 coordinators and an 8-hour day, each handles ~23 matches/day → 8h × 60min / 23 ≈ 20 min/match net of admin overhead. This is consistent with a manual multi-step workflow (parse request, search candidates, check credentials, confirm availability, select best fit, submit). The 4.2-hour average *fill time* is elapsed calendar time including queue wait, nurse response latency, and hospital confirmation — not coordinator active work time.

**Confidence**: Medium. CEO deferred to head of operations for exact numbers. Direct timing study would validate or invalidate.

**Referenced in metrics**: M1, M2

---

## A2 — Candidate evaluations per match: ~5

**Assumed value**: A coordinator evaluates approximately 5 nurse candidates before selecting and submitting one.

**Reasoning**: 120 decisions/coordinator/day ÷ ~23 complete matches/day (A1) ≈ 5.2 evaluations per match. Each evaluation involves checking credentials, proximity, and availability for one candidate. This also explains why senior coordinators are faster — they pattern-match to the right candidates immediately, reducing evaluations to 1-2.

**Confidence**: Medium. Consistent with the math but not directly confirmed in discovery.

**Referenced in metrics**: M2

---

## A3 — MedFlex agency revenue per filled shift: ~$300

**Assumed value**: MedFlex earns approximately $300 net agency revenue per filled shift.

**Reasoning**: Travel nurse single-shift billing rate typically $100–200/hour × 12-hour shift = $1,200–$2,400 billed to hospital. Staffing agency margin: 15–25%. Mid-range: $1,800 × 17% ≈ $306. Cross-check: $14M annual revenue / 250 working days / ~184 fills/day ≈ $304/shift. Both methods converge at ~$300.

**Confidence**: Medium-High. Revenue figure is given ($14M); fills/day is inferred (see A4). Margin assumption is industry standard but unverified for MedFlex specifically.

**Referenced in metrics**: M3, M4, M5

---

## A4 — Current filled shifts per day: ~184

**Assumed value**: MedFlex fills approximately 184 shifts per day under current operations.

**Reasoning**: $14M annual revenue / $300 per shift (A3) / 250 working days = 186.7 ≈ 184 shifts/day net of ~1% variance. With a 12% no-show rate applied post-acceptance, the raw accepted placements are higher (~209/day), but only ~184 result in revenue-generating fills.

**Confidence**: Medium. Derived entirely from A3. If agency margin is higher (e.g., $500/shift), volume would be lower (~112/day). This is the most load-bearing derived figure in the model.

**Referenced in metrics**: M1, M2, M3, M4, M5

---

## A5 — Share of inbound requests currently lost to competitors due to slow fill time: ~30%

**Assumed value**: Approximately 30% of shift requests submitted to MedFlex are ultimately filled by a competing agency because MedFlex responds too slowly.

**Reasoning**: Marcus explicitly confirmed that hospitals submit requests to multiple agencies simultaneously and that "if we don't supply, then someone else will." The 4.2-hour average fill time vs. the <1-hour target implies significant competitive loss. A 30% loss rate is conservative (industry studies on competitive staffing suggest first-response wins in 40–60% of contested cases). No direct MedFlex data exists.

**Confidence**: Low. Highest-risk assumption in this document. Needs direct measurement (e.g., win/loss tracking by request). If the real loss rate is 10%, the revenue-at-stake calculation drops by two-thirds.

**Referenced in metrics**: M3

---

## A6 — Reducing fill time to <1 hour recovers ~50% of currently lost requests

**Assumed value**: Cutting fill time from 4.2h to <1h would allow MedFlex to capture approximately 50% of the shift requests currently lost to competitors (A5).

**Reasoning**: First-response advantage in competitive staffing is significant but not absolute — hospitals have preferred agency relationships, nurse preferences, and price sensitivity. Achieving <1h response will not win every contested request, but it eliminates the primary disqualifier. Assuming roughly half of lost requests are speed-sensitive (vs. preference or price-sensitive), 50% recovery is reasonable.

**Confidence**: Low. Depends on competitive dynamics not disclosed. Named here to make the revenue case falsifiable.

**Referenced in metrics**: M3

---

## A7 — Fully-loaded coordinator cost: $55,000/year ($26.44/hour)

**Assumed value**: Each coordinator costs MedFlex approximately $55,000/year fully loaded (salary + benefits + overhead).

**Reasoning**: Healthcare staffing coordinator median base salary in the US: $42,000–$52,000 (BLS 2024). Adding 30–35% employer costs (payroll taxes, health benefits, 401k, overhead): $55,000–$70,000 fully loaded. Using the lower bound ($55,000) to be conservative. 8 coordinators = $440,000/year in coordination labor.

**Confidence**: Medium. Standard labor cost model; actual MedFlex salaries unknown.

**Referenced in metrics**: M2

---

## A8 — New coordinator ramp-to-productivity time: ~3 months

**Assumed value**: A new coordinator requires approximately 3 months before reaching full matching productivity.

**Reasoning**: Marcus explicitly stated training is "one of my biggest problems" and that "newcomers usually take longer" while experienced coordinators have internalized 10+ years of pattern recognition. Healthcare staffing matching involves multi-state credential rules, hospital preferences, and nurse relationship knowledge. Three months is a standard ramp for knowledge-worker roles with comparable complexity.

**Confidence**: Medium-High. Directly supported by discovery session language.

**Referenced in metrics**: M2

---

## A9 — Share of no-shows attributable to competitive poaching: ~60%

**Assumed value**: Approximately 60% of the 12% no-show rate is caused by nurses accepting competing agency offers after being notified by MedFlex (passive confirmation model + multi-agency dynamics).

**Reasoning**: Marcus stated that nurses sometimes don't show up because they attended a hospital submitted by another agency. The passive confirmation model (silence = acceptance, no explicit acknowledgment required) amplifies this: nurses may not feel committed. The remaining ~40% of no-shows are genuine scheduling conflicts, illness, or unreachable nurses.

**Confidence**: Low. No MedFlex data to support the split. This matters for solution design — competitive poaching is only partially addressable by automation (earlier confirmation requests, but nurses can still defect).

**Referenced in metrics**: M4

---

## A10 — Free-text ServiceNow records are parseable with >85% accuracy using LLM extraction

**Assumed value**: An LLM-based intake parser can extract structured shift requirements (specialty, date, location, credential requirements) from free-text hospital requests in ServiceNow with >85% field-level accuracy.

**Reasoning**: Hospital shift requests follow domain-specific patterns (e.g., "ICU RN needed Friday 7am–7pm, BLS/ACLS required, St. David's North Austin"). Modern LLMs with domain-specific prompting achieve >90% extraction accuracy on similarly structured free text in comparable healthcare intake workflows. The 85% threshold accounts for ambiguous or non-standard submissions. Sub-85% accuracy would require too much human correction to achieve speed gains.

**Confidence**: Medium-High on technical feasibility. Low on whether 85% is sufficient for downstream automation without human review on low-confidence parses.

**Referenced in metrics**: M1, M2

---

## A11 — ServiceNow has a programmatic REST API available for agent read/write access

**Assumed value**: MedFlex's ServiceNow instance exposes a REST API that an external agent can use to read shift requests, read nurse profiles, and write candidate submissions — and that IT/admin can configure agent credentials within the 8-week engagement window.

**Reasoning**: ServiceNow is an enterprise platform where REST API access is a standard licensed capability. However, whether MedFlex's specific instance is configured for external API access, and whether their IT function can provision credentials on an 8-week engagement timeline, is unknown. Without this, the parser, ranker, review interface, and submission automation cannot integrate with the system of record.

**Confidence**: Medium. Technically standard for ServiceNow; operationally depends on MedFlex IT capacity and licensing tier.

**Referenced in metrics**: M1, M2

---

## A12 — Hospital feedback on nurses (acceptance/rejection events) is partially captured in ServiceNow

**Assumed value**: MedFlex records at minimum candidate acceptance and rejection events per nurse per hospital in ServiceNow, enabling the AI ranker to weight hospital preference history in candidate scoring.

**Reasoning**: Marcus stated "we marked this in our systems" when asked about tracking nurse-hospital feedback. Rejection events are also reported as the source of the 7% mismatch statistic ("purely based on the data we get from the hospital"). At minimum, accepted/rejected outcomes per nurse-hospital pair are likely present. Whether these are structured fields or free-text notes is unknown.

**Confidence**: Medium-Low. Presence of some event data is confirmed; completeness, structure, and historical depth are unknown.

**Referenced in metrics**: M5

---

## A13 — Marcus will accept a human-in-the-loop MVP architecture and not push for full autonomy at launch

**Assumed value**: Marcus will approve a design where coordinators review and approve AI-ranked recommendations in MVP, rather than requiring the agent to submit to hospitals without human approval from day one.

**Reasoning**: Marcus deferred the human-in-the-loop decision entirely to FDE expertise ("I'm not an expert in this area — if you say you don't need human in the loop, then I would rely on you"). He also expressed the only two concerns as matching accuracy and coordinator trust/adoption — both of which the HITL design directly addresses. The two prior AI failures and his stated skepticism about accuracy make a full-autonomy launch commercially and operationally risky in a way he has implicitly acknowledged.

**Confidence**: Medium-High. Marcus explicitly delegated this decision and his concerns align with the HITL rationale.

**Referenced in metrics**: M2

---

## A14 — The nurse notification system supports programmatic triggering and response capture

**Assumed value**: The system that sends SMS/email notifications to nurses when a placement is confirmed can be triggered via API or ServiceNow workflow automation, and can capture nurse acknowledgment/decline responses (not just send one-way notifications).

**Reasoning**: Marcus confirmed that nurses are automatically notified via SMS/email when a shift placement is confirmed. The mechanism is either ServiceNow-native or an integrated notification service. However, whether response tracking (capturing explicit acknowledgment vs. no-response) is currently enabled or buildable within 8 weeks is explicitly unconfirmed (U4). The passive confirmation model (silence = acceptance) suggests response capture has not been implemented.

**Confidence**: Low. Trigger capability is plausible; response tracking is unconfirmed and likely requires new infrastructure.

**Referenced in metrics**: M4

---

## A15 — All 8 coordinators share a single ServiceNow instance with no per-coordinator data silos

**Assumed value**: All 8 coordinators work from the same ServiceNow instance and access the same nurse profile database — there are no regional, team-level, or per-coordinator data partitions that would require separate agent configurations or data reconciliation.

**Reasoning**: Discovery confirmed a centralized ServiceNow system ("there is a centralized system around ServiceNow — all requests go through"). The "8 different judgment patterns" observation refers to decision-making style, not data access segregation. No indication of per-coordinator specialization or regional data splits was given.

**Confidence**: High. Standard enterprise deployment pattern; would only fail if coordinators have undisclosed regional or specialty-based data partitions.

**Referenced in metrics**: M1, M2

---

## A16 — Coordinator active work time distribution across cognitive zones: ~35% parsing, ~55% search/evaluation, ~10% submission

**Assumed value**: Of the ~20 minutes of active coordinator work per match (A1), approximately 35% is consumed by intake parsing (JtD-1), 55% by candidate search and evaluation (JtD-2 + JtD-3), and 10% by submission and documentation (JtD-4).

**Reasoning**: Marcus described "matching availability and profile" as the biggest time-consuming step, which maps to JtD-2–3. The ~5 candidate evaluations (A2) at ~2 minutes each account for ~10 minutes / ~20 minutes = ~50% of active time. Parsing is explicitly the first cognitive step per discovery ("scan request"). Submission is near-clerical (format + click). The 35/55/10 split approximates this without a direct time study.

**Confidence**: Low. No time-study data exists. This matters for ROI-by-zone calculations — if parsing is less than 35%, the parser's standalone throughput impact is smaller than projected.

**Referenced in metrics**: M1, M2

---

## A17 — Nurse availability data staleness rate: ~15–20%

**Assumed value**: Approximately 15–20% of nurse availability records in ServiceNow are not current at any given time.

**Reasoning**: Marcus confirmed nurse availability is entirely self-managed ("up to them to update"). No automated prompts, no enforcement mechanism, no freshness timestamp is mentioned. The 12% no-show rate (partly from genuine scheduling conflicts per A9) and the implicit possibility of stale data in a self-managed system support a meaningful staleness estimate. 15–20% is conservative for a large pool without automated reminders. Stale availability directly causes false positives in MT-2.2 (availability filter), wasting search time and occasionally producing matched candidates who cannot actually attend.

**Confidence**: Low. No MedFlex data on record freshness. Key for understanding actual reliability of the availability filter and the value of automated staleness detection.

**Referenced in metrics**: M1, M4

---

## A18 — Senior coordinator pattern recognition is concentrated in Zone 3 (candidate pre-selection), not parsing or submission

**Assumed value**: The speed advantage of senior coordinators (10+ years) is primarily located in MT-3.2 (tacit knowledge application) — specifically, the ability to skip MT-2.1 through MT-2.5 by going directly to 1–3 known candidates, reducing effective evaluations from ~5 (A2) to ~1–2.

**Reasoning**: Marcus explicitly stated experienced coordinators "know how to act better in specific cases" and named the specialization of hospitals and nurses as the domain of their pattern recognition. Discovery confirmed they work faster than newcomers, and this advantage is undocumented. The inference is that the speed differential is in candidate pre-selection, not in parsing speed (both senior and junior coordinators read the same free-text requests) or submission speed (both use the same ServiceNow interface). The AI Candidate Ranker is a direct attempt to replicate this Zone 3 advantage systemically.

**Confidence**: Medium. Supported by discovery language but never confirmed with a direct time breakdown per coordinator tier.

**Referenced in metrics**: M2

---

## A19 — Historical shift outcome records in ServiceNow are sufficient to cold-start the AI candidate ranker

**Assumed value**: At least 3–6 months of coordinator selection records with outcomes (hospital accepted / rejected per candidate submission) are accessible in ServiceNow — estimated at 8,000–16,000 labeled examples at current volume (A4: ~184 fills/day × 90–180 working days).

**Reasoning**: At $14M revenue and ~184 fills/day (A4), MedFlex generates substantial historical volume. Even if only 50% of outcome records are structured enough to serve as labeled training examples (consistent with the "raw format" characterization in discovery), the corpus is sufficient to cold-start a supervised ranking model. The critical unknown is whether coordinator selection records link the specific candidate selected to the submission outcome — A12 confirms hospital acceptance/rejection events exist, but whether the full selection + outcome tuple is available per match is unconfirmed. If data is insufficient, the MVP ranker uses a rule-based scoring approach (T4) while accumulating labeled data from live coordinator review decisions.

**Confidence**: Low-Medium. A12 confirms outcome data exists; completeness and tuple structure are unknown. Key dependency for the Phase 2 ML ranker upgrade.

**Referenced in metrics**: M2, M5

---

## A20 — The same nurse can be submitted to multiple MedFlex requests simultaneously with no internal reservation lock

**Assumed value**: When multiple coordinators process concurrent requests, the same nurse can be independently selected and submitted to different hospitals in the same session. There is no internal reservation mechanism or nurse-lock in ServiceNow that prevents duplicate submissions before hospital acceptance.

**Reasoning**: Marcus explicitly confirmed MedFlex submits the same nurse to multiple hospitals and deconflicts post-acceptance: "we submit a couple of nurses to different hospitals, and then as soon as someone is confirmed, then we remove it from other hospital submission." While described in the context of cross-agency competition, the same dynamic applies internally — 8 coordinators processing the queue concurrently can independently select the same qualified nurse for different shift requests. This creates internal race conditions (A9 is primarily framed as cross-agency; A20 captures the internal version) that manifest as MT-5.4-style conflicts or as wasted submissions after a nurse is already committed.

**Confidence**: Medium. Internal race condition is inferred from the confirmed cross-agency model; not directly confirmed for intra-MedFlex submissions.

**Referenced in metrics**: M4

---

## A21 — FDE engagement delivery cost: ~$15,000/week all-in

**Assumed value**: The 8-week engagement build cost is approximately $15,000 per week all-in (FDE team time + platform overhead + tooling), totaling ~$120,000 for the full engagement.

**Reasoning**: Standard small-team FDE delivery model for a specialized AI sprint (2 FDE engineers + engagement management overhead). Used as the basis for per-JtD build cost estimates in TCO calculations: JtD-1 ~$30K (2 weeks), JtD-2 ~$45K (3 weeks), JtD-3 ~$60K (4 weeks), JtD-4 ~$15K (1 week), JtD-5a ~$15K (1 week). Overlapping parallel builds keep total within the 8-week budget. MedFlex-specific contract terms are unknown.

**Confidence**: Low-Medium. Reasonable for a small specialized AI delivery engagement; actual FDE contract terms and team composition are unconfirmed.

**Referenced in metrics**: TCO calculations in `specs/volume-×-value-analysis.md`

---

## A22 — Claude Sonnet API cost model per matching case

**Assumed value**: Claude Sonnet (claude-sonnet-4-6) pricing: $3.00/M input tokens, $15.00/M output tokens. Per-case token estimates: JtD-1 parsing ~1,500 input / 400 output tokens ($0.011/case); JtD-2 search ~500 input / 200 output tokens ($0.005/case); JtD-3 ranking ~2,000 input / 600 output tokens ($0.015/case).

**Reasoning**: Based on published Anthropic pricing as of May 2026 for Sonnet models. Per-case token estimates derived from domain analysis: JtD-1 requires system prompt (~700 tokens) + shift request (~200 tokens) + context + structured JSON output; JtD-2 orchestrates structured ServiceNow API tool calls with minimal LLM text; JtD-3 requires multi-candidate comparison with explanation generation. Actual token usage will vary with prompt engineering, caching, and context window size.

**Confidence**: Medium on pricing (published rates); Medium-Low on per-case token estimates (validated through mock testing, not live runs).

**Referenced in metrics**: TCO calculations in `specs/volume-×-value-analysis.md`

---

## A23 — ServiceNow REST API rate limit: ≥60 requests/minute per MedFlex instance

**Assumed value**: MedFlex's ServiceNow enterprise instance supports at least 60 API requests per minute without throttling, sufficient for the combined JtD-1 queue poll + JtD-2 profile fetch + JtD-3 preference history read workload at 184 shifts/day.

**Reasoning**: Standard ServiceNow enterprise tiers support 60–300 requests/minute depending on instance size and licensing. At 184 fills/day across an 8-hour active window, peak throughput is ~0.64 requests/second for queue polls, well under even the conservative 60 req/min floor. The assumption becomes binding only if MedFlex runs a constrained developer-tier instance or if multi-agent polling creates burst spikes. Circuit breaker logic (20% error rate in 5-minute window) provides a safety valve if this assumption fails.

**Confidence**: Low. MedFlex IT must confirm instance tier and API rate limit configuration before agent integration is finalized.

**Referenced in metrics**: Integration contracts in `specs/04a-capability-spec-match-selection.md`, `specs/04b-capability-spec-shift-intake-parsing.md`

---

## A24 — ServiceNow table and field naming convention for MedFlex instance

**Assumed value**: Shift requests are stored in table `u_shift_request`; nurse profiles in `sys_user` with custom fields prefixed `u_`; hospital preference history in `u_nurse_hospital_outcome` with fields `u_nurse_id`, `u_hospital_id`, `u_outcome` (ACCEPTED/REJECTED), and `u_placement_date`.

**Reasoning**: ServiceNow custom tables use the `u_` prefix convention by platform standard. The table names and field names used throughout the capability specs are informed estimates based on standard ServiceNow healthcare staffing implementations. Actual table names depend on how MedFlex's ServiceNow admin originally configured the instance — these may differ significantly. All integration contracts in 04a and 04b must be validated against MedFlex's actual ServiceNow schema before development begins.

**Confidence**: Low. Requires MedFlex IT or ServiceNow admin confirmation. Invalidating this assumption would require updating all endpoint paths and field mapping logic in both specs before any integration code is written.

**Referenced in metrics**: Integration contracts in `specs/04a-capability-spec-match-selection.md`, `specs/04b-capability-spec-shift-intake-parsing.md`

---

## A25 — Rule-based ranker scoring weights (Wave 1 MVP)

**Assumed value**: The composite_score formula weights are: credential_match = 0.40, availability_confidence = 0.30, proximity_score = 0.20, hospital_preference_weight = 0.10. Weights sum to 1.00. These are configurable parameters stored outside model code, not hardcoded constants.

**Reasoning**: Credential compliance is non-negotiable (disqualifies candidates outright if failed, then highest ranking weight among eligible candidates). Availability confidence is second because a credentialed but unavailable nurse produces a no-show (A9). Proximity reduces travel cost and latency risk. Hospital preference is weighted lowest because data is sparse at launch (A12: partial coverage). The 40/30/20/10 split reflects the relative cost of getting each dimension wrong: a credential mismatch produces a regulatory incident; an availability mismatch produces a no-show; a proximity mismatch wastes cost; a preference mismatch produces mild hospital friction. Weights should be reviewed with coordinators before launch and recalibrated after Wave 1 data accumulates (A19 labeled feedback store).

**Confidence**: Low. Initial weights derived from first-principles reasoning, not coordinator validation or historical data. Senior coordinator review before Wave 1 launch is required to validate or adjust. Key dependency for the Phase 2 ML ranker upgrade where weights become learned parameters.

**Referenced in metrics**: `specs/04a-capability-spec-match-selection.md` (Activity Catalog MT-3.2, Context Engineering)
