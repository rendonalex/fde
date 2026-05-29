# Updates Summary Based on Dana's Answers
## Scenario 5 — Westbridge Family Medicine

This document tracks changes to assumptions, cognitive load map, delegation qualification, and candidate prioritization based on Dana's discovery question responses.

---

## Assumptions Updates

### Confirmed Assumptions (No Change)
- **A02**: Stale verification (athenahealth has NO automatic alert - confirmed Q6)
- **A05, A06**: Dana's tribal knowledge exists and is encodable (confirmed Q1, Q2)
- **A07**: PA status not checked at check-in (step is missing - confirmed Q3)
- **A11**: DoseSpot gaps confirmed (small pharmacies, assistance programs, mail-order, OTC - confirmed Q8)
- **A12**: Staff only flag med changes, never update (confirmed Q9)

### Resolved Assumptions (Upgrade Confidence)
- **A01**: 30% Availity failure = 60% patient eligibility + 40% system failures (was Medium, now **High** - Q7)
- **A04**: No centralized PA requirement database (athenahealth PA module inadequate - confirmed Q10, now **High**)
- **A08**: Portal adoption = 65-70% (was "assuming <70%", now **confirmed 65-70%** - Q17)
- **A09**: No documented triage protocols (confirmed Q4, now **High**)
- **A10**: Informal triage rules exist + prior heart attack incident 8 months ago (Q4 + Q5, now **High**)
- **A14**: Payer phone wait times 10-20 min (Q7 context implies this, confidence Medium → **Medium**)
- **A15**: athenahealth PA API accessibility unknown (Q11 - remains **Low**, requires IT validation)
- **A17**: HIPAA/malpractice constraints not yet validated (Q12 - Wave 1 blocker, confidence Low → **Critical Blocker**)
- **A18**: Onboarding 3-4 months (was Medium assumption, now **confirmed 3-4 months** - Q15, confidence **High**)
- **A19**: Volume split 60/40 (110/day main, 70/day second location - Q16, now **High**)
- **A20**: Dana nervous but excited (Q18 - confirmed, confidence **High**)
- **A22**: Self-pay/MCO volume 10-15% (Q7 context confirms Medicaid complexity, remains Medium)

### New Assumptions from Dana's Answers

**A27: Payer-Specific Workarounds Count**
- **Assumption**: 7-8 payer-specific workarounds exist beyond Wellpath colonoscopy pattern.
- **Confidence**: High (Q2 - Dana listed 5 explicitly: Aetna specialty referrals, Humana imaging, BCBS cardiac, Medicaid DME, plus "7-8 total")
- **Impact**: JtD 2.2 (PA submission) ROI increases significantly. Agent PA submission checklist is high-value feature.
- **Discovery source**: Q2

**A28: Prior Under-Triage Incident (Heart Attack)**
- **Assumption**: 8 months ago, patient with "indigestion" complaint had silent heart attack; not flagged by front desk; caught by physician during visit; patient survived.
- **Confidence**: High (Q5 - Dana described specific incident)
- **Impact**: Agent triage design must over-escalate (bias toward false positives). JtD 3.2 risk tolerance is shaped by this incident.
- **Discovery source**: Q5

**A29: Prior Automation Failure (Rigid Call Script)**
- **Assumption**: Practice tried rigid call-handling script 2-3 years ago; front desk rejected it after 1 month because real situations don't follow scripts.
- **Confidence**: High (Q14 - Dana described failure)
- **Impact**: Change management: position agent as "assistant providing information" not "script you must follow." Avoid rigid workflows.
- **Discovery source**: Q14

**A30: BAA Execution Timeline**
- **Assumption**: Business Associate Agreement execution takes 2-3 months (legal review, negotiations) based on prior athenahealth BAA experience.
- **Confidence**: High (Q13 - Dana confirmed athenahealth BAA took "about 2 months")
- **Impact**: Wave 1 schedule must account for BAA lead time. Cannot go live until BAA signed.
- **Discovery source**: Q13

---

## Cognitive Load Map Updates

### Work Stream 1: Insurance Verification

**JtD 1.1**: Add clarification - 60% of 30% failure rate (18% of total) is patient eligibility issues (not fixable by agent), 40% of 30% (12% of total) is system failures (agent can retry, fuzzy match). Agent can reduce manual fallback from 30% → ~18-20% (by fixing system failures).

**JtD 1.2**: Add Dana's pattern recognition examples from Q7 (payer portal reliability varies, phone wait times confirmed 10-20 min).

### Work Stream 2: Prior Authorization

**JtD 2.1**: No changes (Q10 confirms athenahealth PA module inadequate, but doesn't change JtD 2.1 scope).

**JtD 2.2**: **Significant update** - Add 7-8 payer-specific workarounds from Q2:
- Aetna specialty referrals: include referral letter
- Humana imaging: add clinical rationale narrative
- BCBS cardiac: include most recent EKG/stress test
- Medicaid DME: require face-to-face visit note <6 months
- Plus 3-4 more not detailed

Agent checklist for JtD 2.2 becomes high-value feature (not just Wellpath workaround).

**JtD 2.3**: **Significant update** - Dana's chase rules are fully encodable (Q1). Specific timing per payer:
- UHC Choice: Always day 6 (never day 5)
- Aetna: 3 days (faster this year)
- Humana Medicare Advantage: Exactly 6 days
- Wellpath Medicaid: 7-10 days + always deny colonoscopy first time

Agent can execute autonomous chase (not just remind Dana). JtD 2.3 archetype confirmed as **Agent-led + Human Oversight** (not downgrade to Human-led).

Dana's Google Sheets has 4 critical features missing from athenahealth (Q10):
1. Custom chase date per payer
2. Payer-specific notes
3. Visit linkage
4. List view sorted by chase date

Agent must build full PA chase management (not integrate with athenahealth PA module).

### Work Stream 3: Pre-Visit Questionnaire & Triage

**JtD 3.1**: Portal adoption confirmed 65-70% (Q17), paper 30-35%. Update volume split: 117-126 portal, 54-63 paper (was 126/54). Paper workflow is permanent (not temporary).

**JtD 3.2**: **Major updates**:
- No documented triage protocols (Q4 confirmed)
- Dana has informal red-flag list: chest pain, difficulty breathing, severe bleeding, "sudden" symptoms
- Prior incident 8 months ago: heart attack presented as "indigestion" (Q5)
- Agent design must formalize red-flag list with Dana + physicians (Wave 1 planning)
- Agent must over-escalate (bias toward false positives after heart attack incident)

### Work Stream 4: Medication Reconciliation

**JtD 4.1**: DoseSpot gaps confirmed (Q8) - add specific categories:
1. Small independent pharmacies (especially in lower-income areas)
2. Manufacturer assistance programs (discount cards, samples)
3. Mail-order (sync delays of weeks)
4. OTC/supplements (patients don't self-report)

**JtD 4.2**: Confirmed - staff only flag, never update med list (Q9). Agent must document in comments/flags, NOT update athenahealth med list directly. Physician updates during visit.

**JtD 4.3**: No changes.

---

## Delegation Qualification Updates

### Feasibility Score Changes

**JtD 2.3 (PA Chase)**: Feasibility increases from 21/30 → **25/30**
- **Data availability**: 4 → **5** (Dana's rules are fully encodable per Q1)
- **System integration**: 3 → **4** (Google Sheets replacement confirmed; athenahealth PA module inadequate per Q10, so parallel system is correct approach)
- **New total**: 25/30 (Medium risk → **Low-Medium risk**)

**JtD 2.2 (PA Submission)**: Value score increases due to Q2 (7-8 workarounds, not just 1)
- **Non-Determinism score**: 3 → **4** (more workarounds = more reasoning required)
- **Value score**: 9 → **12** (3 × 4 = 12)
- Moves from "Medium value" to "Medium-High value" (closer to agent priority threshold)

**JtD 3.2 (Triage)**: Compliance risk increases due to Q5 (prior heart attack incident)
- **Compliance risk**: 2 → **1** (prior incident shapes high malpractice exposure)
- **Org readiness**: 2 → **3** (Dana + physicians aware of risk; receptive to formalizing protocols)
- **New total**: 18/30 → **19/30** (still High risk, but org readiness improved)

### Archetype Confirmation

All archetypes remain unchanged - Dana's answers confirm existing assignments:
- **JtD 2.3**: Agent-led + Human Oversight (Q1 confirms encodable rules)
- **JtD 3.2**: Human-led + Agent Support (Q4 confirms no protocols; Q5 confirms safety-first requirement)
- **JtD 1.1**: Agent-led + Human Oversight (Q6 confirms no athenahealth alert)

---

## Candidate Prioritization Updates

### Volume Score Changes

**JtD 2.2 (PA Submission)**: Value score 9 → **12** (due to Q2 - more workarounds)
- Still below Value ≥ 15 threshold for "Strong agentic candidate"
- Remains Medium priority, Wave 2

### Feasibility Adjustments

**JtD 2.3 (PA Chase)**: Feasibility 21/30 → **25/30**
- Gating risk from Q1 is **RESOLVED** (Dana can articulate rules)
- Move from "Medium feasibility" to "Low-Medium risk"
- **Confirms Wave 1 placement** (strategic value + feasibility now aligned)

**JtD 3.2 (Triage)**: Compliance risk increases (prior incident Q5), but org readiness improves (Dana receptive to formalizing protocols Q4)
- Gating requirement confirmed: Must formalize red-flag protocols in Wave 1 planning phase (1-3 months) before deploying agent in Wave 2
- **Remains Wave 2** (after protocols formalized)

### Economic Validation Updates

**Q15 impacts A26 (time saved)**:
- Dana confirms onboarding is 3-4 months, with tribal knowledge as bottleneck
- Agent ROI now includes: **50% onboarding time reduction** (16 weeks → 6-8 weeks)
- Additional annual saving beyond time-per-case: **Reduced onboarding cost**
  - New hire cost (recruitment, training, productivity ramp) ≈ $15k-20k per hire
  - If turnover is 30%/year (1.2 hires/year for 4-person team), onboarding reduction saves: 1.2 × 8 weeks × $35/hr × 40 hrs/week = $13,440/year
  - **Wave 1 annual saving increases from $234k → $248k** (preliminary)

**Q20 impacts ROI narrative**:
- Senior physician prioritizes patient experience > efficiency
- Re-frame ROI: "Prevent visit cancellations + billing errors" (patient-facing) not just "Reduce staff time"
- Quantify patient dissatisfaction cost:
  - Lost patient (TJ example): lifetime value ≈ $5k-10k (4 visits/year × $150 revenue/visit × 10 years)
  - Negative online review: acquisition cost impact ≈ $2k-5k (reduced new patient flow)
  - Wave 1 prevents: ~5-10 PA-related cancellations/year + ~10-15 billing errors/year = $20k-50k patient experience value

**Revised Wave 1 TCO** (preliminary):
- Annual saving: $248k (time saved) + $35k (patient experience) = **$283k/year**
- Build cost: $740k (unchanged)
- Payback: $740k / $283k = **2.6 years** (was 3.2 years)
- Still exceeds 12-month target, but improved
- **Action**: Validate time-saved assumptions (A26) via time-motion study before Wave 1 kickoff

### Wave Sequencing Updates

**Wave 1** (Months 1-6): No changes to JtD selection
- JtD 1.1 (insurance verification) - Q6 confirms high value
- JtD 2.3 (PA chase) - Q1 confirms feasibility, Q19 confirms Dana's pain point
- JtD 4.2 (med reconciliation) - Q8 confirms DoseSpot gaps

**Wave 1 planning phase** (Months 1-3): Add new workstream
- Formalize visit-reason red-flag protocols with Dana + physicians (Q4 + Q5)
- Required before JtD 3.2 deployment in Wave 2
- Includes: red-flag symptom list, escalation thresholds, follow-up questions checklist

**Wave 2** (Months 7-12): No changes to JtD selection, but add prerequisite
- JtD 3.2 (triage) - **Prerequisite**: Red-flag protocols formalized in Wave 1 planning
- JtD 1.2 (manual verification) - unchanged
- JtD 2.2 (PA submission) - Q2 increases value (7-8 workarounds), but still Wave 2

**Critical Blockers Identified**:
1. **Q12**: HIPAA/malpractice approval **not yet obtained** - Must resolve before Wave 1 kickoff (2-4 week validation)
2. **Q13**: BAA execution requires 2-3 months - Start BAA process in parallel with Wave 1 design (Months 1-3)
3. **Q11**: athenahealth PA API accessibility unknown - IT validation required (1-2 weeks)

---

## Change Management Implications

### From Q14: Prior Automation Failure
- **Dana's mental model**: "Automation works for predictable tasks, fails when it replaces judgment"
- **Positioning**: Agent provides information/recommendations; human makes final decisions
- **Avoid**: Presenting agent as "AI decides for you" or rigid scripts
- **Messaging**: "Agent is your assistant, not your replacement"

### From Q18: Dana's Motivation
- **Dana is excited but nervous** (bus factor concern: "Am I automating myself out of a job?")
- **Success for Dana**: "Agent handles routine, I handle complex cases + strategic work"
- **Critical**: Involve Dana in design (encode her rules, validate agent behavior)
- **Positioning**: "Agent scales your expertise, frees you for strategic ops" (NOT "Agent replaces you")

### From Q19: PA Chase is Dana's Pain Point
- **Highest pain**: PA chase (mental load + non-delegatable + patient-facing consequences)
- **Dana's desired outcome**: "Agent monitors status, alerts me only when action needed"
- **Wave 1 narrative**: "Eliminate your daily PA chase burden; shift from firefighting to strategic planning"

### From Q20: Senior Physician's Priorities
- **Priority**: Patient experience > Compliance risk > Staff efficiency
- **ROI narrative**: Emphasize "prevent patient-facing failures" (visit cancellations, billing errors) not just "reduce staff time"
- **Executive summary**: "AI prevents embarrassing mistakes; improves patient satisfaction; reduces compliance risk"

---

## Summary: Key Decisions Confirmed

### ✅ Proceed to Wave 1 (Green Light)
1. **JtD 2.3 (PA chase)**: Dana's rules are encodable (Q1) + feasibility improved (Q10)
2. **JtD 1.1 (insurance verification)**: athenahealth has no staleness alert (Q6) + agent provides high-value feature
3. **JtD 4.2 (med reconciliation)**: DoseSpot gaps confirmed (Q8) + staff boundary clarified (Q9)

### ⚠️ Gating Dependencies (Yellow Light)
1. **HIPAA/malpractice approval** (Q12): Must validate before Wave 1 kickoff (2-4 weeks)
2. **BAA execution** (Q13): 2-3 month lead time; start in parallel with Wave 1 design
3. **athenahealth PA API** (Q11): IT validation required (1-2 weeks)

### 📋 Wave 1 Planning Phase (New Workstream)
1. **Formalize red-flag triage protocols** (Q4 + Q5): Collaborate with Dana + physicians to document red-flag symptoms, escalation thresholds, follow-up questions (required before JtD 3.2 in Wave 2)

### 📈 Economic Model Adjustments
1. **Onboarding time reduction** (Q15): Add 50% onboarding savings to ROI ($13k/year)
2. **Patient experience value** (Q20): Quantify prevented visit cancellations + billing errors ($35k/year)
3. **Revised payback**: 2.6 years (was 3.2 years) - still exceeds 12-month target; requires time-motion validation

### 🎯 Change Management Strategy
1. **Position agent as Dana's assistant** (Q14 + Q18): "Scales your expertise" not "Replaces you"
2. **Involve Dana in design** (Q18): Encode her rules, validate agent behavior, maintain her ownership
3. **Frame ROI for senior physician** (Q20): "Prevents patient dissatisfaction" not just "Reduces staff time"
