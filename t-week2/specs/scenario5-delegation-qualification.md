# Delegation Qualification Matrix: Small-Clinic Patient Intake
## Scenario 5 — Westbridge Family Medicine

**Practice**: Westbridge Family Medicine (6-physician, 2 locations, ~180 patients/day)  
**Function**: 4-person front-desk intake team  
**Analysis**: Delegation suitability assessment for 13 Jobs to be Done across 4 work streams

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Delegation Suitability Framework](#delegation-suitability-framework)
3. [Work Stream 1: Insurance Verification](#work-stream-1-insurance-verification)
4. [Work Stream 2: Prior Authorization](#work-stream-2-prior-authorization)
5. [Work Stream 3: Pre-Visit Questionnaire & Triage](#work-stream-3-pre-visit-questionnaire--triage)
6. [Work Stream 4: Medication Reconciliation & Allergy Review](#work-stream-4-medication-reconciliation--allergy-review)
7. [Summary: Delegation Archetype Distribution](#summary-delegation-archetype-distribution)
8. [Anti-Pattern Check: RPA vs. Agent Decision](#anti-pattern-check-rpa-vs-agent-decision)

---

## Executive Summary

### Delegation Readiness Overview

Of 13 Jobs to be Done analyzed across Westbridge Family Medicine's patient intake workflow, **zero qualify for fully agentic delegation** due to HIPAA compliance constraints, clinical judgment boundaries, and high-consequence error modes. The delegation opportunity lies in **agent-led + human oversight** (5 JtDs) and **human-led + agent support** (6 JtDs) archetypes.

### Key Constraints Shaping Delegation

1. **Hard constraint: No clinical judgment by non-clinical staff** [Scenario constraint #1] — Front-desk staff cannot make clinical decisions; agent cannot either. This rules out autonomous triage, medication change assessment, and visit-reason interpretation.

2. **Hard constraint: Clear human escalation path for visit reasons** [Scenario constraint #2] — Any symptom interpretation must preserve escalation to RN/physician. Agent can flag, not decide.

3. **Hard constraint: HIPAA compliance is non-negotiable** [Scenario constraint #3] — All agent actions must be auditable, reversible where possible, and covered under Business Associate Agreement [A17: Confidence Medium].

4. **Tribal knowledge concentration risk** — Dana's payer-specific PA chase patterns [A05, A06] are high-value but not documented. If Dana leaves, institutional knowledge is lost. Encoding this knowledge into agent rules is feasible but requires elicitation [Discovery Q1, Q2].

### Highest-Value Delegation Opportunities

| JtD | Delegation Archetype | Volume | Key Benefit | Critical Dependency |
|-----|---------------------|--------|-------------|---------------------|
| **2.3: Chase pending PA approvals** | Agent-led + Human Oversight | 25/day | Encodes Dana's tribal knowledge; reduces PA miss risk | Dana can articulate payer-specific rules [Discovery Q1] |
| **1.1: Verify insurance eligibility (automated)** | Agent-led + Human Oversight | 180/day | Detects stale verifications; reduces 30% manual fallback rate | Availity API reliability + stale-verification trigger [A01, A02] |
| **4.2: Reconcile medication changes** | Human-led + Agent Support | 180/day | Structures patient interview; closes DoseSpot gaps | Front-desk documents, physician confirms [A12] |
| **3.2: Triage visit reason** | Human-led + Agent Support | 180/day | Formalizes red-flag escalation; prevents under-triage | Documented triage protocols exist or can be created [A09, A10] |

### Delegation Distribution

- **Human Only**: 0 JtDs (no tasks meet ≥3 Low suitability threshold, but compliance constraints apply)
- **Human-led + Automation Support**: 2 JtDs (low non-determinism; could be RPA but context varies slightly)
- **Human-led + Agent Support**: 6 JtDs (agent synthesizes, recommends; human decides)
- **Agent-led + Human Oversight**: 5 JtDs (agent executes; human reviews outputs or approves escalations)
- **Fully Agentic**: 0 JtDs (HIPAA + clinical judgment constraints prevent full autonomy)

### Non-Agentic Opportunities (RPA Candidates)

**JtD 3.1: Collect pre-visit questionnaire** — Portal adoption is ~70% [A08]; paper intake (30%) requires human data entry. The portal-based path is deterministic automation (patient self-service), not agentic. Agent value is minimal; focus effort on increasing portal adoption (patient communication, ease-of-use improvements).

**JtD 4.1: Pull medication list from DoseSpot** — Already automated (DoseSpot API → athenahealth). Exception handling (DoseSpot gaps for small pharmacies, assistance programs [A11]) requires human interview, but this is not an agentic task—it's structured data collection. Agent can provide interview script, but execution is human-led.

### Critical Assumptions Requiring Resolution

**Before agent design**:
- **A05, A06**: Can Dana articulate her payer-specific PA chase timing rules explicitly? If yes → encodable as agent logic. If no (pure intuition) → agent can only remind, not execute.
- **A09, A10**: Do documented visit-reason triage protocols exist? If yes → agent applies rules. If no → agent must over-escalate (low specificity) or protocols must be formalized before deployment.
- **A01**: What causes the 30% Availity failure rate? If API/system failures → agent retry logic. If patient eligibility → agent prompts patient for updated insurance.

**Before scoping**:
- **A17**: What HIPAA/malpractice insurance constraints exist for AI in patient intake? If human-in-the-loop required for all outputs → no agent-led archetypes viable.
- **A04**: How are PA requirements currently looked up? If athenahealth rules are unreliable → agent needs external PA database (CoverMyMeds, payer portals).

---

## Delegation Suitability Framework

### Scoring Key
- **High**: Favorable for agent delegation
- **Medium**: Moderate; requires design attention
- **Low**: Unfavorable; human judgment or manual processes required

### Delegation Archetypes
1. **Human Only**: ≥3 dimensions at Low suitability, especially risk/compliance and decision determinism
2. **Human-led + Automation Support**: Deterministic sub-tasks can be automated; judgment stays human
3. **Human-led + Agent Support**: Agent provides synthesis, research, recommendations; human decides
4. **Agent-led + Human Oversight**: Agent acts autonomously; human reviews or approves high-stakes outputs
5. **Fully Agentic**: All dimensions at Medium or High; volume justifies full delegation

---

## Work Stream 1: Insurance Verification

### JtD 1.1: Verify Active Insurance Eligibility (Automated Path)

**Volume**: 180/day (~126 auto-success + ~54 manual fallback)  
**Handling time**: 3 min/case automated; 5 min/case for 30% manual fallback

#### Delegation Suitability Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input structure** | High | Structured: patient ID, date of service, payer ID → Availity API call |
| **Decision determinism** | High | Binary: coverage active (proceed) or inactive/error (escalate to manual verification). Rule-based. |
| **Tool coverage** | High | Availity REST API available; athenahealth integration exists. [A15: Confidence Low — API accessibility for PA data unclear, but eligibility API is confirmed.] |
| **Context complexity** | Medium | Requires detecting stale verifications (>6 months) [A02]. Payer-patient linkage can be ambiguous (MCO plan name mismatches) [A03]. |
| **Exception rate** | Medium | 30% failure rate [A01]. Unclear if failures are API issues (retryable) or patient eligibility (requires human). |
| **Latency constraint** | Medium | Real-time at check-in preferred, but 3-min API call is acceptable. Async pre-visit verification possible. |
| **Risk/compliance** | Medium | Billing impact if wrong (patient billed incorrectly). HIPAA applies. Reversible (can re-verify). [A02: Documented failure mode — billing errors from stale verification.] |

#### Delegation Archetype: **Agent-led + Human Oversight**

**Rationale**:
- Agent can execute Availity API calls autonomously (High input structure, High determinism)
- Agent can detect stale verifications (>6 months since last check) and trigger re-verification [A02]
- Agent should escalate to human when: (1) Availity API fails, (2) payer-patient linkage ambiguous (MCO plan name mismatch), (3) verification >6 months old and patient hasn't updated insurance in portal
- Human oversight: Front-desk staff review escalations and handle phone-based manual verification (JtD 1.2)

**Key design decisions**:
1. **Stale verification trigger**: Agent flags any verification >6 months old before patient visit [A02]. Assumption: 6-month threshold is practice standard (artefact evidence supports this). [**New assumption A21** needed: What is the practice's actual verification refresh policy?]
2. **Retry logic for API failures**: If Availity times out, agent retries 2× before escalating to human [A01]. Assumption: Some API failures are transient.
3. **MCO plan identification**: Agent attempts fuzzy match on plan name (patient card vs. Availity database). If confidence <80%, escalate to human [A03].

**Expected value**:
- Reduces manual verification rate from 30% → 15–20% (by catching stale verifications before visit, retrying API failures)
- Prevents billing errors from stale verifications [A02: "third time" — documented recurring failure]

**Anti-pattern check**: This is partially deterministic (API call), but the stale-verification detection and MCO fuzzy matching require contextual reasoning. Agent is justified over pure RPA.

---

### JtD 1.2: Resolve Manual Insurance Verification Cases

**Volume**: ~54/day (30% of 180)  
**Handling time**: 5 min active work + 10–20 min payer phone wait time [A14: Confidence Medium]

#### Delegation Suitability Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input structure** | Low | Unstructured: phone conversation with payer customer service, patient-provided insurance card (photos, verbal), payer portals (20+ different UIs). |
| **Decision determinism** | Low | Judgment-dependent: Accept patient's verbal report? Call payer or trust card? Defer visit or bill as self-pay? Payer rep responses vary. |
| **Tool coverage** | Low | Phone (no API), payer portals (no standard API, manual navigation required). athenahealth manual entry. |
| **Context complexity** | High | Requires institutional knowledge: which payers have reliable portals vs. must call, which MCO plans are legitimate vs. suspected errors [A03]. |
| **Exception rate** | High | Frequent: payer systems down, wait times, ambiguous payer responses ("coverage pending," "call back tomorrow"), patient doesn't have card. |
| **Latency constraint** | High | Patient waiting at desk; visit scheduled. 10–20 min wait time creates patient dissatisfaction. |
| **Risk/compliance** | Medium | Billing impact if wrong. HIPAA applies. Reversible (can re-verify later, refile claim). |

#### Delegation Archetype: **Human-led + Agent Support**

**Rationale**:
- Low input structure (phone, unstructured payer responses) makes agent-led execution impractical
- Agent cannot make judgment calls: "Accept patient's verbal report?" "Defer visit or bill as self-pay?"
- Agent value: Provide decision-support checklist, log prior attempts, suggest next action based on pattern recognition

**Agent role**:
1. **Checklist prompts**: "Have you checked payer portal before calling?" "Did patient provide both front and back of card?" "Is this MCO plan on the known-valid list?"
2. **Payer contact history**: Display prior manual verifications for this patient + payer (e.g., "Last verified 8 months ago via phone with Aetna — coverage was active")
3. **Pattern recognition**: "UHC portal is reliable; call only if portal is down" vs. "Wellpath portal is often stale; call directly" [Extension of A05 logic to eligibility verification]

**Expected value**:
- Reduces decision time for front-desk staff (checklist eliminates forgetting steps)
- Captures tribal knowledge (which payers to call vs. portal) in agent prompts
- Does NOT reduce 10–20 min payer wait time (that's a payer-side constraint)

**Why not agent-led?**: Phone calls and judgment-dependent decisions ("defer visit?") cannot be automated. This is human cognitive work with agent scaffolding.

---

### JtD 1.3: Handle Self-Pay and Medicaid MCO Edge Cases

**Volume**: ~20–30/day (estimated; not stated in scenario) [**New assumption A22**: Self-pay + Medicaid MCO cases represent ~10–15% of daily volume based on "especially complex" designation.]  
**Handling time**: 8–10 min/case (estimated; more complex than standard verification)

#### Delegation Suitability Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input structure** | Low | Unstructured: patient verbal report, inconsistent MCO card formats, payment negotiation (self-pay). |
| **Decision determinism** | Low | Judgment-dependent: Accept self-pay with payment plan? Which MCO plan is this (name mismatches)? Flag for financial counseling? |
| **Tool coverage** | Low | State Medicaid portals (no standard API), manual forms, phone. athenahealth billing flags (UI-based). |
| **Context complexity** | High | Requires state-specific MCO knowledge [A03]. Self-pay negotiation depends on patient financial situation (not system-encoded). |
| **Exception rate** | High | Frequent: MCO eligibility churn (patient moved between plans), plan name doesn't match database, patient unsure which MCO. |
| **Latency constraint** | Medium | Patient waiting at desk, but self-pay arrangements can be deferred to billing team post-visit. |
| **Risk/compliance** | Medium | Billing compliance risk (Medicaid audit exposure if wrong MCO). Financial risk (self-pay no-show). HIPAA applies. |

#### Delegation Archetype: **Human-led + Agent Support**

**Rationale**:
- Low input structure (verbal, inconsistent card formats) + Low determinism (judgment: payment plans, financial counseling)
- Agent cannot negotiate payment arrangements or assess patient financial need
- Agent value: MCO plan lookup assistant, self-pay workflow checklist

**Agent role**:
1. **MCO plan lookup**: Agent searches state Medicaid portal (if API available) or provides fuzzy-match suggestions based on patient's stated plan name [A03]. "Did you mean: Wellpath Maryland Medicaid MCO?"
2. **Self-pay workflow checklist**: "Has patient been offered payment plan? Has financial counseling been mentioned? Is visit urgent or deferrable?"
3. **Historical context**: Display patient's prior insurance (e.g., "Last visit 3 months ago: UnitedHealthcare → now self-pay. Check if coverage lapsed or changed.")

**Expected value**:
- Reduces MCO plan identification time (agent provides lookup, not human googling)
- Standardizes self-pay workflow (checklist ensures staff don't skip steps)
- Does NOT eliminate human judgment (payment plans, financial counseling)

**Why not agent-led?**: Payment negotiation and financial counseling require empathy and judgment. MCO lookup could be automated, but the decision ("Is this the right plan?") requires human confirmation due to audit risk.

---

## Work Stream 2: Prior Authorization

### JtD 2.1: Identify PA Requirement for Scheduled Procedure/Imaging/Referral

**Volume**: ~25/day  
**Handling time**: 10 min/case (lookup + responsibility clarification)

#### Delegation Suitability Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input structure** | High | Structured: CPT code + payer ID + patient coverage effective date. |
| **Decision determinism** | Medium | Rule-based (payer PA matrices: "CPT 70553 + UHC PPO = PA required"), but rules change quarterly and athenahealth is out of date [A04]. Responsibility clarification (practice vs. specialist) is judgment. |
| **Tool coverage** | Low | No centralized PA requirement database. athenahealth rules stale [A04]. Payer portals (20+ different, no API). Third-party databases (CoverMyMeds) exist but not mentioned as in use. |
| **Context complexity** | Medium | Requires knowing payer-specific rules + whether practice has pre-negotiated PA exemptions. Responsibility split (practice vs. imaging center vs. specialist) is not always clear. |
| **Exception rate** | Medium | Payer rules change quarterly (new codes, policy updates). Ambiguous cases: "Is this diagnostic or screening?" (PA requirement differs). |
| **Latency constraint** | Low | Done at scheduling (days before visit). Not time-sensitive. |
| **Risk/compliance** | High | PA miss → denied claim (revenue loss) + delayed patient care [A07: Documented failure mode — patient arrived without PA cleared]. |

#### Delegation Archetype: **Agent-led + Human Oversight**

**Rationale**:
- Input is structured (CPT + payer), decision is mostly rule-based
- Agent can query PA requirement databases (if accessible) or athenahealth rules (with human override for stale rules)
- Human oversight required for: (1) ambiguous cases ("diagnostic vs. screening"), (2) responsibility clarification (practice vs. specialist), (3) rule updates not yet in system

**Agent role**:
1. **PA requirement lookup**: Agent queries CoverMyMeds (if API available) or payer portals (if accessible) or athenahealth rules. Returns: "PA required" or "PA not required" or "Ambiguous — escalate."
2. **Confidence scoring**: Agent flags when athenahealth rule is >6 months old [A04]. "Rule last updated: March 2025. Recommend manual confirmation."
3. **Responsibility routing**: Agent checks if procedure code is typically practice-responsibility vs. facility-responsibility. If unclear, escalate.

**Expected value**:
- Reduces front-desk PA lookup time (agent does lookup, not human navigating 20 payer portals)
- Catches stale athenahealth rules before PA miss [A04]
- Does NOT eliminate judgment (ambiguous diagnostic/screening, responsibility clarification)

**Key dependency**: Access to current PA requirement data. If athenahealth is only source and it's stale [A04], agent needs external database (CoverMyMeds, Change Healthcare PA Navigator) or manual human override pathway.

**Anti-pattern check**: This is mostly rule-based lookup, not agentic reasoning. However, the confidence scoring (rule staleness) and ambiguity detection justify agent over pure RPA.

---

### JtD 2.2: Submit PA Request to Payer

**Volume**: ~25/day  
**Handling time**: 12 min/case (assemble docs, navigate portal, submit)

#### Delegation Suitability Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input structure** | Medium | Semi-structured: payer portal forms (structured fields) + clinical documentation (unstructured physician notes, diagnostic codes). |
| **Decision determinism** | Medium | Mostly deterministic (copy CPT, ICD codes, patient demographics into portal fields), but payer-specific workarounds are judgment [A05: Wellpath colonoscopy — attach prior visit note even though form doesn't ask]. |
| **Tool coverage** | Low | 20+ payer portals (no standard API, each different UI). Fax (manual). Phone (no API). athenahealth has clinical notes (API-accessible), but doc assembly is manual. |
| **Context complexity** | High | Requires Dana's tribal knowledge: payer-specific documentation requirements [A05]. "Wellpath always wants prior visit note for colonoscopy." "Aetna needs specialist referral letter, not just order." |
| **Exception rate** | Medium | Payer portals have errors, require re-login, reject PDFs over certain size. Forms change without notice. Fax confirmation failures. |
| **Latency constraint** | Medium | PA must submit 5 days before visit (not real-time), but portal delays can compress timeline. |
| **Risk/compliance** | High | Incomplete submission → denial → claim denial + delayed care [A05: Wellpath pattern]. Resubmit cycle adds 7–10 days. Clinical documentation must be accurate (HIPAA, malpractice exposure). |

#### Delegation Archetype: **Human-led + Agent Support**

**Rationale**:
- Low tool coverage (20+ portals, no API) makes agent-led submission impractical without RPA-style screen automation (brittle, high maintenance)
- Payer-specific workarounds [A05] require encoding Dana's tribal knowledge — this is agent-appropriate (not RPA)
- Clinical documentation assembly (which notes to attach) requires judgment

**Agent role**:
1. **Documentation checklist**: Agent prompts: "For Wellpath colonoscopy PA, attach prior visit note (required but not on form)." [A05] "For Aetna specialty referrals, include referral letter."
2. **Clinical note retrieval**: Agent pulls relevant physician notes from athenahealth (via API) and displays for human selection. "Most recent visit notes for this patient: [list]. Select which to attach."
3. **Portal navigation guide**: Agent provides step-by-step for each payer portal. "UHC: log in → Clinical Review → Request Authorization → Section 3 for procedure details."
4. **Submission confirmation**: Agent logs submission confirmation number in athenahealth + Dana's PA chase list (replacing Google Sheets).

**Expected value**:
- Encodes Dana's tribal knowledge (payer-specific workarounds) [A05] so other staff can apply them
- Reduces documentation assembly time (agent pulls notes, human selects)
- Does NOT eliminate manual portal navigation (agent guides, human executes)

**Why not agent-led?**: Payer portals have no APIs. Agent-led would require RPA (screen scraping, button clicking) which is brittle and high-maintenance. Human-led with agent guidance is more robust.

**Alternative if RPA investment justified**: Agent-led + Human Oversight with RPA integration. Agent navigates portals, fills forms, submits. Human reviews before final submit. High initial investment, high ongoing maintenance (portal UIs change frequently). Likely not justified for 25 cases/day unless portal navigation time is >50% of handling time.

---

### JtD 2.3: Chase Pending PA Approvals

**Volume**: ~25/day (all PAs require chase monitoring; ~15/day require active chase based on SLA approaching)  
**Handling time**: 5–10 min/case (portal check or phone call)

#### Delegation Suitability Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input structure** | High | Structured: PA submission date, payer ID, visit date, stated SLA. |
| **Decision determinism** | Medium | Rule-based with payer-specific overrides [A05, A06]. "Stated SLA: 5 days. Dana's actual chase timing: Aetna 3 days, UHC 6 days, Wellpath 7 days, Humana exactly 6 days." Rules are articulable. |
| **Tool coverage** | Low | Payer portals (manual status check, no API). Phone (no API). Google Sheets (Dana's shadow system) [A06]. athenahealth PA module exists but Dana doesn't use it [A06]. |
| **Context complexity** | High | Requires Dana's multi-year observational learning [A05, A06]. "Wellpath always denies first submission for colonoscopy." "Aetna is fast this month (unusual)." Context: payer behavior patterns not encoded in systems. |
| **Exception rate** | Medium | Payer response times vary (system load, holidays, staffing). Portals sometimes show stale status. Phone wait times unpredictable [A14]. |
| **Latency constraint** | Medium | Chase must happen 1–3 days before visit to allow reschedule time if PA denied. Not real-time, but time-sensitive. |
| **Risk/compliance** | High | Late chase → PA not cleared by visit date → aborted visit + patient dissatisfaction [A07: Documented failure — "second time this has happened to me"]. Revenue loss (visit cancellation). |

#### Delegation Archetype: **Agent-led + Human Oversight**

**Rationale**:
- Decision determinism is Medium (rules exist and are articulable [A05, A06]), not Low (judgment)
- Agent can encode Dana's payer-specific chase timing rules: "If payer = UHC → chase on day 6, not day 5."
- Agent can automate portal status checks (if portal accessible) or schedule phone chase reminders
- Human oversight: Dana reviews agent's chase recommendations before executing (especially for escalation: "reschedule visit?")

**Agent role**:
1. **Chase timing engine**: Agent applies Dana's payer-specific rules [A05, A06]. "PA submitted to UHC on 10/16. Visit on 10/28. Standard SLA: 5 days. Dana's rule: UHC is always 6 days. Chase date: 10/22 (day 6)."
2. **Status check automation**: Agent checks payer portal status daily (if accessible). If status = "Pending" on chase date → alert Dana. If status = "Approved" → update athenahealth, close chase. If status = "Denied" → escalate immediately.
3. **Escalation logic**: Agent calculates: "Visit in 3 days. PA still pending. Recommend: call payer today + prepare to reschedule visit."
4. **Replace Google Sheets**: Agent logs all chase activity in athenahealth (or agent-managed system), visible to all staff [A06].

**Expected value**:
- Encodes Dana's tribal knowledge [A05, A06] so new staff can apply same logic
- Prevents late chase → prevents aborted visits [A07]
- Reduces Dana's manual chase workload (agent monitors, alerts only when action needed)
- Eliminates shadow system risk [A06] (Google Sheets → shared agent system)

**Key dependency RESOLVED** [Discovery Q1]: Dana articulated payer-specific rules explicitly: UHC day 6 (never day 5, portal says 5 but they never respond until day 6), Aetna 3 days (faster this year), Humana exactly 6 days (like clockwork), Wellpath 7-10 days + always denies colonoscopy first time. Rules are fully encodable. Agent-led + Human Oversight archetype confirmed.

**Anti-pattern check**: This is rule-based with payer-specific overrides. Could be RPA (scheduled checks, alerts), but the payer-pattern reasoning ("Wellpath always denies first time, so chase differently") justifies agent over pure RPA.

---

## Work Stream 3: Pre-Visit Questionnaire & Triage

### JtD 3.1: Collect Pre-Visit Questionnaire (Portal or Paper)

**Volume**: ~180/day (~126 portal + ~54 paper) [A08: Portal adoption ~70%]  
**Handling time**: 2 min/case (portal self-service); 4 min/case (paper entry)

#### Delegation Suitability Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input structure** | High | Structured fields: visit reason, symptom onset date, current medications (checkboxes or free-text), recent hospitalizations. Portal path is fully structured. Paper path is semi-structured (handwriting). |
| **Decision determinism** | High | Deterministic: copy form fields into athenahealth. No judgment required. |
| **Tool coverage** | High | athenahealth patient portal (API available). Paper forms → manual entry (no OCR mentioned). |
| **Context complexity** | Low | No institutional knowledge required. Straightforward data entry. |
| **Exception rate** | Low | Routine: patients skip fields (prompt for completion), handwriting illegible (ask patient to clarify). |
| **Latency constraint** | Medium | Portal: pre-visit (async). Paper: at check-in (real-time, patient waiting). |
| **Risk/compliance** | Low | Data entry error (typo) is reversible. HIPAA applies but low clinical consequence. |

#### Delegation Archetype: **Human-led + Automation Support** (Portal Path) / **Human Only** (Paper Path)

**Rationale**:
- Portal path (70%) is already automated (patient self-service). No agent needed; this is standard software.
- Paper path (30%) requires human data entry (reading handwriting, prompting for missing fields). Agent cannot read handwriting without OCR.
- Agent value is minimal: Could provide data-entry validation ("Symptom onset date is in future — is this correct?"), but this is basic input validation, not agentic reasoning.

**Agent role (minimal)**:
1. **Portal adoption prompts**: Agent sends pre-visit reminders via SMS/email: "Complete your intake form online before your visit on 10/22. [Link]" [A08: Increase portal adoption from 70% → 80%+]
2. **Paper data entry validation**: Agent flags obvious errors during manual entry: "Symptom onset: 2027 (future date) — confirm with patient."

**Expected value**:
- Increasing portal adoption (70% → 85%) via agent reminders reduces paper workload
- Data validation reduces typos, but this is minor (low error rate)

**Anti-pattern check**: This is deterministic data entry, not agentic reasoning. **This is an RPA candidate, not an agent candidate.** Focus effort on increasing portal adoption (UX improvements, patient communication), not building an agent.

**Recommendation**: Deprioritize agent development for JtD 3.1. Invest in portal adoption (patient education, simplified portal UX) instead.

---

### JtD 3.2: Triage Visit Reason (Routine vs. Urgent vs. Same-Day)

**Volume**: ~180/day  
**Handling time**: 3–5 min/case (routine); 10–15 min/case if escalation required

#### Delegation Suitability Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input structure** | Low | Unstructured: patient free-text visit reason ("some chest discomfort," "feeling dizzy," "need med refill"). Symptom descriptions vary (under-reported or over-reported urgency). |
| **Decision determinism** | Low | Requires clinical judgment [A09: Hard constraint #2 — "any contact with visit reason must preserve clear human escalation path"]. Front-desk staff are not clinically trained. Triage protocols not documented [A10]. |
| **Tool coverage** | Medium | athenahealth visit reason field (UI-based). Phone/pager to RN/physician for escalation. No formal triage decision-support system mentioned. |
| **Context complexity** | High | Requires clinical knowledge: "Chest discomfort + shortness of breath = urgent" vs. "Chest discomfort after heavy meal = likely routine but confirm." Context: patient's prior history, current meds, age. |
| **Exception rate** | High | Frequent: patients under-describe urgency ("chest discomfort" = chest pain), mismatch between scheduled visit type and stated reason (scheduled physical, reports acute symptom). |
| **Latency constraint** | High | Urgent cases require immediate escalation to RN/physician. Delayed triage = patient safety risk. |
| **Risk/compliance** | High | Under-triage → delayed care for urgent condition (malpractice exposure). Over-triage → physician alert fatigue, wasted urgent slots. HIPAA applies. |

#### Delegation Archetype: **Human-led + Agent Support**

**Rationale**:
- Low input structure (unstructured symptom descriptions) + Low decision determinism (clinical judgment required) [A09]
- Hard constraint: Front-desk staff cannot make clinical triage decisions; agent cannot either [Scenario constraint #2]
- Agent value: Red-flag symptom detection, escalation prompts, NOT final triage decision

**Agent role**:
1. **Red-flag symptom detection**: Agent scans visit reason for high-risk keywords: "chest pain," "difficulty breathing," "severe bleeding," "suicidal," "sudden vision loss," etc. If detected → immediate escalation prompt: "RED FLAG: Patient reports chest pain. Escalate to RN/physician NOW."
2. **Escalation checklist**: Agent prompts front-desk staff: "Chest discomfort reported. Ask clarifying questions: (1) When did it start? (2) Is it constant or intermittent? (3) Any shortness of breath? (4) Any prior cardiac history?" [A10: Formalize informal triage protocols]
3. **Triage recommendation (non-binding)**: Agent suggests: "Based on keywords, this may be urgent. Recommend escalation to RN for clinical assessment." Human makes final decision.

**Expected value**:
- Prevents under-triage (agent catches red-flag symptoms that front-desk might miss)
- Formalizes informal triage protocols [A10] (agent codifies "chest pain → escalate immediately")
- Does NOT replace clinical judgment (RN/physician makes final triage decision)

**Key dependency**: Documented red-flag criteria must exist or be created [A09, A10: Discovery Q4]. If no protocols exist, agent design must collaborate with clinical staff to define criteria before deployment.

**Why not agent-led?**: Clinical triage requires medical judgment. Front-desk staff and agent lack clinical training. Agent-led triage would violate Hard Constraint #1 ("No clinical judgment by the agent") and create malpractice exposure.

---

## Work Stream 4: Medication Reconciliation & Allergy Review

### JtD 4.1: Pull Current Medication List from DoseSpot/Pharmacy

**Volume**: ~180/day  
**Handling time**: 2 min/case (automated pull + patient confirmation)

#### Delegation Suitability Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input structure** | High | Structured: patient ID → DoseSpot API → med list with NDC codes, dosages, prescriber. |
| **Decision determinism** | High | Deterministic: API call, display results. |
| **Tool coverage** | High | DoseSpot API integrated with athenahealth. Known gaps: small pharmacies, assistance programs, mail-order [A11]. |
| **Context complexity** | Medium | DoseSpot gaps [A11] require human interview to supplement, but the API call itself is straightforward. |
| **Exception rate** | Medium | DoseSpot doesn't capture OTC meds, supplements, medication assistance programs [A11]. Patients forget to mention these. |
| **Latency constraint** | Medium | Done at check-in (real-time), but 2-min API call is acceptable. |
| **Risk/compliance** | Medium | Incomplete med list → prescribing error risk (drug interactions, duplicate therapy). HIPAA applies. |

#### Delegation Archetype: **Human-led + Automation Support**

**Rationale**:
- DoseSpot API call is already automated (not agentic)
- Exception handling (DoseSpot gaps [A11]) requires human interview: "Are you taking any over-the-counter medications, vitamins, or supplements not on this list?"
- Agent value is minimal: This is already automated via DoseSpot integration. Agent can provide interview script for gap-filling, but execution is human-led.

**Agent role (minimal)**:
1. **Interview script for DoseSpot gaps**: Agent prompts: "DoseSpot doesn't show OTC meds or assistance programs. Ask patient: (1) Any vitamins or supplements? (2) Any samples from doctor? (3) Mail-order prescriptions?" [A11]
2. **Reconciliation prompt**: Agent displays: "DoseSpot shows 5 active prescriptions. Ask patient: 'Is this list complete and correct?'"

**Expected value**:
- Structures gap-filling interview [A11] (reduces missed OTC, supplements)
- Minimal value-add (DoseSpot API already automates core task)

**Anti-pattern check**: This is deterministic API call + structured interview. **Not an agent candidate; already automated.** Agent value is interview script only.

**Recommendation**: Deprioritize agent development for JtD 4.1. Focus agent effort on JtD 4.2 (medication change reconciliation), where judgment is required.

---

### JtD 4.2: Reconcile Medication Changes with Patient

**Volume**: ~180/day  
**Handling time**: 4 min/case (patient interview + documentation)

#### Delegation Suitability Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input structure** | Low | Unstructured: patient verbal report ("I stopped taking that one," "my cardiologist added a new pill"). Patient memory varies. |
| **Decision determinism** | Low | Requires judgment [A12: Hard constraint #1 — "No clinical judgment by the agent"]. Front-desk staff document changes but cannot assess clinical significance ("Is it safe to stop this med?"). Physician confirms later. |
| **Tool coverage** | Medium | athenahealth med list (API for read/write). Patient interview (manual). |
| **Context complexity** | High | Requires clinical knowledge: "Patient stopped blood thinner → urgent escalation" vs. "Patient stopped vitamin D → routine flag." Front-desk lacks this knowledge. |
| **Exception rate** | High | Frequent: patients forget med names ("the little white pill"), report changes inconsistently ("I think I stopped it last month?"), confuse dosage changes with med changes. |
| **Latency constraint** | Medium | Done at check-in (real-time), but can flag for physician review during visit (not urgent). |
| **Risk/compliance** | High | Incorrect med list → prescribing error (drug interactions, duplicate therapy, contraindications). Malpractice exposure. HIPAA applies. |

#### Delegation Archetype: **Human-led + Agent Support**

**Rationale**:
- Low input structure (verbal, inconsistent) + Low determinism (requires clinical judgment [A12])
- Front-desk staff cannot assess clinical significance of med changes; agent cannot either [Hard Constraint #1]
- Agent value: Structured interview, cross-reference against DoseSpot, flag discrepancies for physician review

**Agent role**:
1. **Structured interview**: Agent prompts: "DoseSpot shows you're on Lisinopril 10mg. Are you still taking this?" [Repeat for each med.] "Have you started any new medications since your last visit?"
2. **Cross-reference discrepancies**: Agent compares patient report vs. DoseSpot. If patient says "stopped Lisinopril" but DoseSpot shows active prescription filled 7 days ago → flag: "Discrepancy detected. Patient reports stopped, but prescription refilled recently. Confirm with patient."
3. **Physician flag**: Agent generates: "Medication changes reported: (1) Stopped Lisinopril (patient report; refilled 7 days ago — confirm). (2) Started new medication from cardiologist (name unknown — patient to bring bottle). FLAG for physician review."

**Expected value**:
- Structures interview [A11, A12] (reduces missed med changes)
- Cross-references patient report vs. DoseSpot (catches discrepancies)
- Does NOT assess clinical significance (physician reviews during visit)

**Key dependency**: Front-desk staff must understand that med changes are documented but NOT clinically assessed [A12: Discovery Q9]. Agent documentation must clearly indicate "FLAG for physician review," not "APPROVED by front-desk."

**Why not agent-led?**: Assessing clinical significance of med changes requires medical judgment. "Patient stopped blood thinner" is urgent; "Patient stopped vitamin D" is routine. Front-desk and agent lack clinical training [A12].

---

### JtD 4.3: Review and Update Allergy Flags

**Volume**: ~180/day  
**Handling time**: 2 min/case (patient confirmation + updates)

#### Delegation Suitability Scoring

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input structure** | Medium | Semi-structured: athenahealth allergy list (structured) + patient verbal report ("I think I'm allergic to penicillin, I got a rash last year"). |
| **Decision determinism** | Medium | Mostly deterministic (add reported allergy to list), but distinguishing true allergy vs. side effect vs. intolerance requires clinical judgment [A13]. |
| **Tool coverage** | High | athenahealth allergy list (API available for read/write). |
| **Context complexity** | Medium | Requires clinical knowledge to distinguish allergy (immune response: anaphylaxis, hives) vs. intolerance (GI upset, nausea). Front-desk documents symptom; physician confirms. |
| **Exception rate** | Medium | Patients unsure if reaction was allergy ("I felt nauseous") or don't remember which medication caused it ("some antibiotic"). |
| **Latency constraint** | Medium | Done at check-in (real-time), but allergy decision-support fires at prescribing time (physician-facing) [A13]. |
| **Risk/compliance** | High | Missing allergy → adverse drug event (anaphylaxis). False-positive allergy → limits treatment options. Malpractice exposure. HIPAA applies. |

#### Delegation Archetype: **Human-led + Agent Support**

**Rationale**:
- Decision determinism is Medium (add allergy to list is straightforward, but assessing severity requires clinical judgment [A13])
- Agent can structure allergy interview, document reported symptoms, flag for physician confirmation
- Agent cannot make final determination: "Is this true allergy or intolerance?"

**Agent role**:
1. **Structured allergy review**: Agent prompts: "athenahealth shows allergy to Penicillin. Is this still accurate?" "Any new allergies since last visit?"
2. **Symptom documentation**: Agent prompts: "You mentioned a reaction. What symptoms did you have? (Rash, hives, difficulty breathing, nausea, other?)" [A13: Capture detail for physician to assess]
3. **Physician flag**: Agent generates: "Possible new allergy reported: Penicillin. Symptoms: rash last year. FLAG for physician to confirm (allergy vs. intolerance) and document severity."

**Expected value**:
- Structures allergy interview (captures symptom detail [A13] for physician assessment)
- Ensures reported allergies aren't ignored (agent flags for physician review)
- Does NOT determine allergy vs. intolerance (physician decides during visit)

**Key dependency**: Allergy decision-support is physician-facing (fires at prescribing time), not front-desk-facing [A13: Discovery Q13]. Agent's role is documentation + escalation, not clinical decision.

**Why not agent-led?**: Distinguishing true allergy (anaphylaxis risk) vs. intolerance (GI upset) requires clinical judgment. Incorrect allergy entry creates false alerts (alert fatigue) or missed alerts (patient safety risk).

---

## Summary: Delegation Archetype Distribution

### Archetype Assignments by JtD

| JtD ID | JtD Description | Work Stream | Delegation Archetype | Volume | Key Rationale |
|--------|-----------------|-------------|---------------------|--------|---------------|
| 1.1 | Verify active insurance eligibility (automated path) | Insurance Verification | Agent-led + Human Oversight | 180/day | Structured API call; agent detects stale verifications; human handles manual fallback |
| 1.2 | Resolve manual insurance verification cases | Insurance Verification | Human-led + Agent Support | 54/day | Unstructured phone calls; agent provides checklist, pattern recognition |
| 1.3 | Handle self-pay and Medicaid MCO edge cases | Insurance Verification | Human-led + Agent Support | 20–30/day | MCO lookup, self-pay workflow; judgment required for payment plans |
| 2.1 | Identify PA requirement for scheduled procedure/imaging/referral | Prior Authorization | Agent-led + Human Oversight | 25/day | Rule-based PA requirement lookup; agent flags stale rules; human confirms ambiguous cases |
| 2.2 | Submit PA request to payer | Prior Authorization | Human-led + Agent Support | 25/day | Manual portal navigation; agent encodes payer-specific workarounds; human executes |
| 2.3 | Chase pending PA approvals | Prior Authorization | Agent-led + Human Oversight | 25/day | Encodes Dana's chase timing rules; agent monitors status, alerts when action needed; human executes |
| 3.1 | Collect pre-visit questionnaire (portal or paper) | Pre-Visit Questionnaire | Human-led + Automation Support | 180/day | Portal self-service (70%); paper entry (30%); RPA candidate, not agent |
| 3.2 | Triage visit reason (routine vs. urgent vs. same-day) | Pre-Visit Questionnaire | Human-led + Agent Support | 180/day | Clinical triage requires RN/physician; agent flags red-flag symptoms; human decides |
| 4.1 | Pull current medication list from DoseSpot/pharmacy | Medication Reconciliation | Human-led + Automation Support | 180/day | DoseSpot API (already automated); agent provides gap-filling interview script |
| 4.2 | Reconcile medication changes with patient | Medication Reconciliation | Human-led + Agent Support | 180/day | Agent structures interview, cross-references DoseSpot; physician assesses clinical significance |
| 4.3 | Review and update allergy flags | Allergy Review | Human-led + Agent Support | 180/day | Agent structures allergy review; physician confirms allergy vs. intolerance |

### Distribution Summary

| Delegation Archetype | Count | JtDs |
|---------------------|-------|------|
| **Human Only** | 0 | — |
| **Human-led + Automation Support** | 2 | 3.1 (portal adoption), 4.1 (DoseSpot API) |
| **Human-led + Agent Support** | 6 | 1.2, 1.3, 2.2, 3.2, 4.2, 4.3 |
| **Agent-led + Human Oversight** | 5 | 1.1, 2.1, 2.3, (see note below) |
| **Fully Agentic** | 0 | — |

**Note**: No JtDs qualify for Fully Agentic due to HIPAA compliance requirements (all patient data access must be auditable with human accountability [A17]) and clinical judgment constraints (Hard Constraints #1, #2).

### Highest-Value Agent Opportunities (by Expected Impact)

1. **JtD 2.3: Chase pending PA approvals** — Agent-led + Human Oversight
   - **Impact**: Prevents aborted visits [A07]; encodes Dana's tribal knowledge [A05, A06]; eliminates shadow system risk
   - **Volume**: 25/day (all PAs need monitoring)
   - **Dependency**: Dana can articulate payer-specific rules [Discovery Q1]

2. **JtD 1.1: Verify insurance eligibility** — Agent-led + Human Oversight
   - **Impact**: Prevents billing errors from stale verifications [A02: "third time"]; reduces 30% manual fallback rate
   - **Volume**: 180/day
   - **Dependency**: Understand Availity 30% failure root cause [Discovery Q7]

3. **JtD 4.2: Reconcile medication changes** — Human-led + Agent Support
   - **Impact**: Closes DoseSpot gaps [A11]; structures interview; reduces prescribing error risk
   - **Volume**: 180/day
   - **Dependency**: Front-desk understands documentation vs. clinical assessment boundary [A12]

4. **JtD 3.2: Triage visit reason** — Human-led + Agent Support
   - **Impact**: Prevents under-triage (patient safety); formalizes red-flag protocols [A10]
   - **Volume**: 180/day
   - **Dependency**: Red-flag criteria documented or can be created with clinical staff [Discovery Q4]

---

## Anti-Pattern Check: RPA vs. Agent Decision

### RPA Candidates (Not Agent)

**JtD 3.1: Collect pre-visit questionnaire (portal path)**
- **Why RPA, not agent**: Portal self-service is deterministic (patient enters data, system saves). No reasoning required.
- **Recommendation**: Increase portal adoption (70% → 85%) via patient communication, UX improvements. Agent value is minimal.

**JtD 4.1: Pull medication list from DoseSpot**
- **Why RPA, not agent**: DoseSpot API call is already automated. No agentic reasoning required.
- **Recommendation**: Agent can provide gap-filling interview script [A11], but core task is already automated. Low priority for agent development.

### Agent-Justified (Not RPA)

**JtD 2.3: Chase pending PA approvals**
- **Why agent, not RPA**: Payer-specific timing rules [A05, A06] require contextual reasoning. "Wellpath always denies first time → chase differently than UHC."
- **Why not RPA**: RPA would require static schedule (e.g., "chase all PAs on day 5"). Agent encodes dynamic logic: "If payer = Wellpath AND procedure = colonoscopy → chase on day 7, not day 5."

**JtD 1.1: Verify insurance eligibility**
- **Why agent, not RPA**: Stale verification detection [A02] + MCO fuzzy matching [A03] require contextual reasoning.
- **Why not RPA**: RPA would be binary ("Last verified <6 months = OK"). Agent considers: "Patient has chronic condition + stable insurance → 6-month window acceptable" vs. "Patient had recent insurance change → verify even if <6 months."

**JtD 3.2: Triage visit reason**
- **Why agent, not RPA**: Red-flag detection requires NLP (symptom keyword extraction from unstructured text). RPA cannot parse "some chest discomfort" vs. "chest discomfort with shortness of breath."
- **Why not RPA**: RPA would require exact keyword match. Agent uses semantic understanding: "discomfort," "pressure," "tightness" all map to "chest pain" red flag.

---

**Document cross-references**:
- **Assumptions**: See `scenario5-assumptions.md` for detailed rationale on all assumption IDs (A01–A20, A21–A22 added here).
- **Discovery questions**: See `scenario5-discovery-questions.md` for coach elicitation priorities.
- **Cognitive load map**: See `scenario5-cognitive-load-map.md` for full JtD decomposition and process topology.
