# Assumptions Log: Scenario 5 — Small-Clinic Patient Intake
## Westbridge Family Medicine

**Purpose**: Track all inferences made beyond what the scenario and artefacts explicitly state. Each assumption is marked with an ID, confidence level, and rationale.

**Confidence levels**:
- **High**: Directly supported by artefact evidence or standard industry practice
- **Medium**: Reasonable inference from partial evidence; would benefit from coach confirmation
- **Low**: Speculative; requires coach elicitation to validate or reject

---

## Insurance Verification Assumptions

### A01: Composition of 30% Manual Verification Rate
**Assumption**: The 30% manual-verification rate includes both true eligibility failures (patient coverage lapsed, changed plans) and system integration failures (Availity timeout, missing payer configuration, stale payer contracts).  
**Confidence**: Medium  
**Rationale**: Scenario states "~30% that fail auto-verify" but doesn't distinguish between patient-side failures (no active coverage) and system-side failures (API issues). Industry pattern: commercial eligibility APIs like Availity have 5–10% technical failure rate; remaining failures are patient eligibility issues.  
**Impact on design**: If system failures dominate, solution is API retry logic + payer configuration maintenance. If patient failures dominate, solution is patient communication (portal reminders, phone outreach before visit).  
**Discovery question to resolve**: "Of the 30% of cases that require manual verification, how many are due to Availity API timeouts or missing payer setups vs. actual patient eligibility issues?"

---

### A02: Six-Month Verification Staleness is a Known Failure Mode
**Assumption**: athenahealth does not automatically refresh patient insurance verification after 6 months; front-desk staff are responsible for visual review of "last verified" date, but this check is inconsistently performed.  
**Confidence**: High  
**Rationale**: Artefact 5.3 explicitly documents a case where a patient with continuous Aetna coverage was billed as self-pay because verification was 10 months old. Front-desk note states: "Patient verification refresh window > 6 months caused billing miss. We don't refresh for chronic patients on stable insurance — Dana said this is the third time."  
**Impact on design**: Agent can automate stale-verification detection and trigger pre-visit re-verification (via Availity API or patient portal prompt).  
**Discovery question to resolve**: "Does athenahealth have a built-in staleness alert that's not being used, or is this functionality missing entirely?"

---

### A03: Self-Pay and Medicaid MCO Complexity Sources
**Assumption**: Self-pay and Medicaid managed-care complexity stems from: (1) multiple MCO plans with different coverage rules, (2) frequent eligibility churn (patients move between MCOs or in/out of eligibility), (3) missing or inconsistent plan identifiers on patient cards.  
**Confidence**: Medium  
**Rationale**: Scenario states these cases are "especially complex" but doesn't specify why. Industry pattern: Medicaid MCO eligibility is state-specific, changes monthly, and plan names on cards often don't match payer databases. Self-pay patients require payment arrangement negotiation, not just eligibility verification.  
**Impact on design**: Agent can assist with MCO plan lookup (if state portal APIs exist) but may still require human negotiation for self-pay arrangements.  
**Discovery question to resolve**: "What specifically makes Medicaid managed-care verification complex? Is it plan identification, eligibility churn, or something else?"

---

## Prior Authorization Assumptions

### A04: PA Requirement Database is Incomplete or Stale
**Assumption**: No centralized, current PA requirement database exists. Staff rely on athenahealth's built-in payer rules (which are frequently out of date) or informal lists/tribal knowledge.  
**Confidence**: High  
**Rationale**: Artefact 5.2 shows a PA-pending case that wasn't flagged at check-in, indicating tracking gaps. No mention of a real-time PA requirement lookup tool. Industry pattern: PA requirements change quarterly but EHR rule sets are manually updated (lag time 3–6 months).  
**Impact on design**: Agent needs access to current PA requirements (payer portals, third-party PA databases like CoverMyMeds, or manual lookup with human override).  
**Discovery question to resolve**: "How do you currently look up PA requirements? Is athenahealth's rule set accurate, or do you use external resources?"

---

### A05: Dana Has Built Payer-Specific Behavioral Models
**Assumption**: Dana's Google Sheets "my target chase" column (Artefact 5.1) encodes multi-year observational learning about payer response-time patterns. This knowledge is not documented in athenahealth or shared systematically with other staff.  
**Confidence**: High  
**Rationale**: Artefact 5.1 explicitly shows payer-specific chase timing (Aetna fast, UHC 6–7 days, Wellpath denial pattern, Humana exactly 6 days). Footer note documents Wellpath colonoscopy workaround ("they want the prior visit note attached, never says so on the form").  
**Impact on design**: Agent can encode Dana's rules as payer-specific logic (if Dana can articulate them), reducing reliance on tribal knowledge.  
**Discovery question to resolve**: "Can you walk me through your PA chase timing for each major payer? Are there other payer-specific patterns beyond what's in your Google Sheets notes?"

---

### A06: Google Sheets is a Shadow System for PA Tracking
**Assumption**: Dana's PA chase list operates outside athenahealth because athenahealth's PA tracking module doesn't support the custom fields Dana needs ("my target chase," payer-specific notes).  
**Confidence**: High  
**Rationale**: Artefact 5.1 shows structured chase list in Google Sheets with columns not available in athenahealth. Industry pattern: EHR PA modules are built for compliance (what was submitted, when, to whom) but not for operational chase management (when to follow up based on payer behavior).  
**Impact on design**: Agent can replace Google Sheets with shared, auditable PA chase system integrated with athenahealth (or operating alongside it with bi-directional sync).  
**Discovery question to resolve**: "Have you tried using athenahealth's PA tracking module? What's missing that made you build the Google Sheets version?"

---

### A07: PA Status Not Checked at Patient Check-In
**Assumption**: Front-desk check-in workflow does not include a systematic PA status check. Staff assume that if a visit is on the schedule, PA must be cleared (or not required).  
**Confidence**: High  
**Rationale**: Artefact 5.2 documents patient arriving for MRI follow-up with PA still pending. Visit was aborted at exam-room check. Physician note: "Front desk did not flag this at check-in." Patient stated: "This is the second time this has happened to me."  
**Impact on design**: Agent can provide day-of-visit PA status alerts at check-in (pull from athenahealth PA module or payer portals).  
**Discovery question to resolve**: "What does your check-in workflow look like? Is there a step where staff are supposed to verify PA status, or is that step missing?"

---

## Pre-Visit Questionnaire & Triage Assumptions

### A08: Patient Portal Adoption is <70%
**Assumption**: Approximately 70% of patients complete pre-visit questionnaires via portal; 30%+ use paper forms at check-in.  
**Confidence**: Medium  
**Rationale**: Scenario mentions "phone + paper intake forms (for patients without portal accounts)" but doesn't state adoption rate. Industry benchmark for small primary care practices: 60–75% portal adoption (higher for younger patients, lower for elderly, Medicaid, and non-English-speaking populations).  
**Impact on design**: Agent must support dual workflows (portal-driven + paper/verbal intake). Cannot assume all patients will use portal.  
**Discovery question to resolve**: "What percentage of your patients complete the pre-visit questionnaire via the portal vs. paper at check-in?"

---

### A09: No Documented Escalation Threshold for Visit-Reason Triage
**Assumption**: Front-desk staff escalate ambiguous visit reasons to RN/physician based on informal judgment, not documented red-flag criteria.  
**Confidence**: High  
**Rationale**: Hard constraint #2 states "any contact with the stated visit reason must preserve a clear human escalation path." Scenario doesn't mention triage protocols. Front-desk staff are not clinically trained (Dana is RN but not doing intake directly).  
**Impact on design**: Agent can implement rule-based red-flag symptom list (chest pain, difficulty breathing, severe bleeding, etc.) with mandatory escalation, but cannot perform final triage decision.  
**Discovery question to resolve**: "Do you have documented triage rules or red-flag symptoms that always get escalated? How do front-desk staff decide when to pull in a clinician?"

---

### A10: Acute-Symptom Protocols Are Informal
**Assumption**: Practice has informal acute-symptom response (e.g., "chest pain → alert physician immediately") but protocols are not formalized in athenahealth or written SOPs.  
**Confidence**: Medium  
**Rationale**: No mention of acute-symptom protocols in scenario or artefacts. Small practices (6 physicians, 4 front-desk staff) often operate on shared informal knowledge rather than formalized triage protocols.  
**Impact on design**: Agent can surface and formalize these informal rules, making them consistent and auditable.  
**Discovery question to resolve**: "What happens when a patient reports chest pain, difficulty breathing, or other urgent symptoms at check-in? Is there a written protocol, or do staff just know to escalate immediately?"

---

## Medication Reconciliation Assumptions

### A11: DoseSpot Coverage Gaps for Certain Patient Populations
**Assumption**: DoseSpot pharmacy sync has gaps for: (1) small/independent pharmacies not in DoseSpot's network, (2) mail-order pharmacies (separate records from local), (3) medication assistance programs (free/discounted drugs not tracked as prescriptions), (4) patients who use multiple pharmacies inconsistently.  
**Confidence**: Medium  
**Rationale**: Scenario states med reconciliation is "especially complex for self-pay or Medicaid managed-care patients." Industry pattern: low-income patients use fragmented pharmacy sources (Walmart $4 generics, manufacturer assistance, free clinic samples). DoseSpot relies on pharmacy claims data; if no claim is filed, DoseSpot doesn't see it.  
**Impact on design**: Agent can prompt for common DoseSpot gaps (OTC meds, samples, mail-order, assistance programs) during patient interview, but cannot auto-populate these sources.  
**Discovery question to resolve**: "Where does DoseSpot's medication list miss things? Do you see gaps for patients on assistance programs, mail-order, or using multiple pharmacies?"

---

### A12: Front-Desk Staff Cannot Make Clinical Med-Change Decisions
**Assumption**: When a patient reports a medication change (stopped med, new med from specialist, dosage change), front-desk staff document the report and flag for physician review. Staff do not make clinical judgments about whether the change is safe, appropriate, or urgent.  
**Confidence**: High  
**Rationale**: Hard constraint #1: "No clinical judgment by the agent." Front-desk staff are not clinically trained. Medication reconciliation at intake is documentation, not clinical decision-making.  
**Impact on design**: Agent can structure patient interview, cross-reference against DoseSpot, and flag discrepancies for physician review. Cannot assess clinical significance of med changes.  
**Discovery question to resolve**: "When a patient says they stopped taking a medication or started a new one, what do front-desk staff do? Do they update the med list immediately, or just flag it for the physician?"

---

### A13: Allergy Alerts Fire at Prescribing Time, Not Intake
**Assumption**: Drug-allergy interaction alerts are physician-facing (fire when prescribing in athenahealth), not front-desk-facing at intake.  
**Confidence**: Medium  
**Rationale**: No mention of allergy decision-support at intake. Industry pattern: EHR allergy modules check drug-allergy interactions at prescribing time (when physician orders med), not at intake documentation time.  
**Impact on design**: Agent's role at intake is to ensure allergy list is complete and accurate; clinical decision-support is the physician's tool, not the agent's.  
**Discovery question to resolve**: "Does athenahealth alert front-desk staff to drug-allergy interactions during intake, or do those alerts only show up when the physician prescribes?"

---

## Process & System Assumptions

### A14: Payer Customer Service Phone Wait Times are 10–20 Minutes
**Assumption**: Manual insurance verification via phone (JtD 1.2a) includes 10–20 min hold time before reaching payer customer service, in addition to 5 min conversation/documentation time.  
**Confidence**: Medium  
**Rationale**: Scenario states "~5 min/case for the ~30% that fail auto-verify," but this likely refers to active work time, not total elapsed time. Industry pattern: commercial payer phone wait times are 10–30 min; Medicaid MCO wait times can be 30+ min.  
**Impact on design**: Manual verification is a significant time sink. Agent cannot eliminate phone wait times, but can reduce frequency by improving auto-verify success rate.  
**Discovery question to resolve**: "When you call a payer to verify insurance manually, how long does it typically take from dialing to getting the information you need?"

---

### A15: athenahealth PA Module API Accessibility is Unclear
**Assumption**: athenahealth has a PA tracking module, but it's unclear whether PA status, submission date, and notes are accessible via athenahealth's REST API or only via UI.  
**Confidence**: Low  
**Rationale**: athenahealth is described as "modern SaaS, REST APIs available," but scenario doesn't specify which workflows have API coverage. PA tracking is often a licensed add-on module with limited API surface.  
**Impact on design**: If PA data is API-accessible, agent can integrate directly with athenahealth for PA tracking. If not, agent may need to operate as a parallel system (like Dana's Google Sheets) with manual data entry.  
**Discovery question to resolve**: "Can you pull PA submission status and notes from athenahealth via an API, or is that data only accessible through the athenahealth UI?"

---

### A16: Physician Time to Review Pre-Visit Questionnaires
**Assumption**: Physicians review pre-visit questionnaires (visit reason, symptom onset, med changes, allergy updates) immediately before seeing the patient, not at a separate triage step.  
**Confidence**: Medium  
**Rationale**: Scenario doesn't describe physician workflow. Industry pattern for small practices: physicians review EHR chart (including intake notes) in the 1–2 minutes before entering exam room. No separate triage nurse role mentioned.  
**Impact on design**: Agent's intake documentation must be clear, concise, and structured so physicians can scan it quickly. Verbose free-text notes create cognitive load for physicians.  
**Discovery question to resolve**: "When and how do physicians review the intake information before seeing the patient?"

---

### A17: HIPAA and Malpractice Insurance Constraints on AI
**Assumption**: Westbridge's malpractice insurance and HIPAA compliance policies may impose constraints on AI usage (e.g., human-in-the-loop requirements, audit trail mandates, data residency).  
**Confidence**: Medium  
**Rationale**: Hard constraint #3: "HIPAA and state medical-records compliance is non-negotiable." No specifics given. Small practices often rely on Business Associate Agreements (BAAs) with EHR vendors; adding AI agents may require new BAAs or policy review.  
**Impact on design**: Agent architecture must include audit logging, data residency compliance (likely US-only), and BAA coverage from AI platform provider.  
**Discovery question to resolve**: "Have you checked with your malpractice insurance or HIPAA compliance advisor about using AI for patient intake? Are there specific constraints they've mentioned?"

---

### A18: Front-Desk Staff Turnover and Training Time
**Assumption**: Front-desk staff turnover is moderate (industry average ~30%/year for medical office admin roles); new staff take 3–6 months to reach full proficiency, including learning Dana's tribal knowledge about PA patterns.  
**Confidence**: Medium  
**Rationale**: Scenario doesn't mention turnover, but Dana's tribal knowledge (PA chase patterns, MCO verification workarounds) is not documented, suggesting new staff would face steep learning curve.  
**Impact on design**: Agent can reduce onboarding time by encoding tribal knowledge as agent rules, making institutional learning accessible to new staff immediately.  
**Discovery question to resolve**: "How long does it take a new front-desk hire to get up to speed on all the intake tasks, especially PA tracking and insurance verification edge cases?"

---

### A19: Visit Volume Distribution Across Two Locations
**Assumption**: The ~180 patients/day are distributed roughly evenly across both locations (~90/day each), with some cross-site staff rotation when one location is short-staffed.  
**Confidence**: Low  
**Rationale**: Scenario states "Two locations 12 miles apart" and "typically 2 [front-desk staff] at each site, with cross-site rotation when one location is short-staffed." No volume split given.  
**Impact on design**: If volume distribution is uneven (e.g., 70/30 split), staffing and agent deployment may need to account for location-specific load. If cross-site rotation is frequent, agent system must be accessible from both locations (cloud-based, not desktop-installed).  
**Discovery question to resolve**: "How do the 180 daily patients split across your two locations? Is one site busier than the other?"

---

### A20: Dana's Personal Career Stake in This Project
**Assumption**: Dana is personally invested in the AI project as a way to demonstrate operational leadership, reduce her own manual chase workload, and/or position herself for a broader role (multi-site operations, regional practice network).  
**Confidence**: Low  
**Rationale**: Scenario states Dana is RN-trained, 11 years at Westbridge, and that "the senior physician has asked her to 'look at this AI thing.'" Discovery elicitation prompt asks: "What's Dana's personal stake in this — what is she planning for beyond this project?"  
**Impact on design**: If Dana sees this as career-advancing, she'll be a strong internal champion. If she sees it as a threat (AI replacing her judgment), she may resist. Understanding her motivation shapes change management approach.  
**Discovery question to resolve**: "What does success on this AI project mean for you personally? Is this something you're excited about, or is it something you're being asked to do?"

---

### A21: Practice Insurance Verification Refresh Policy
**Assumption**: The practice has a 6-month verification refresh threshold based on industry standard, but this policy is not enforced automatically by athenahealth. Staff are expected to visually check "last verified" date, but this is inconsistently performed.  
**Confidence**: Medium  
**Rationale**: Artefact 5.3 shows billing error from 10-month stale verification. Front-desk note says ">6 months" but doesn't specify if 6 months is official policy or staff rule-of-thumb. Industry standard for commercial insurance is 6–12 months; Medicare/Medicaid is often 90 days.  
**Impact on design**: Agent needs to know correct refresh threshold (6 months? 90 days for Medicaid? Varies by payer?). If no official policy exists, agent design should help formalize one.  
**Discovery question to resolve**: "What is your official policy for how often to re-verify patient insurance? Does it vary by payer type (commercial vs. Medicare vs. Medicaid)?"

---

### A22: Volume Estimate for Self-Pay and Medicaid MCO Edge Cases
**Assumption**: Self-pay + Medicaid managed-care edge cases represent approximately 10–15% of daily intake volume (~20–30 cases/day out of 180 total).  
**Confidence**: Low  
**Rationale**: Scenario states these cases are "especially complex" but provides no volume data. Estimation based on: (1) US national average for uninsured (8–10%), (2) Medicaid enrollment in Mid-Atlantic states (12–18%), (3) subset requiring manual verification. This is speculative.  
**Impact on design**: If volume is <10/day, agent ROI for MCO lookup is lower. If volume is 40+/day, this is high-priority agent feature.  
**Discovery question to resolve**: "Of your 180 daily patients, approximately how many are self-pay or Medicaid managed-care? How much time does your team spend on these edge cases?"

---

## Summary: High-Priority Assumptions to Resolve

**Critical for design (resolve first in coach role-play)**:
1. A04: How is PA requirement lookup currently done? (determines agent data sources)
2. A05: Can Dana articulate her payer-specific chase timing rules? (determines if tribal knowledge is encodable)
3. A07: Why isn't PA status checked at check-in? (determines intervention point)
4. A09: Are there any documented triage protocols? (determines agent escalation logic)
5. A11: What are DoseSpot's specific coverage gaps? (determines agent interview prompts)

**Important for scoping (resolve in mid-week checkpoint)**:
6. A01: What causes the 30% manual verification rate? (system vs. patient issues)
7. A06: Why doesn't athenahealth's PA module meet Dana's needs? (determines build-vs-integrate)
8. A17: What are HIPAA/malpractice constraints on AI? (determines compliance requirements)
9. A18: How long does front-desk onboarding take? (determines ROI from knowledge encoding)

**Nice-to-have context (resolve if time permits)**:
10. A08: Portal adoption rate? (determines dual-workflow investment priority)
11. A19: Volume distribution across locations? (determines deployment complexity)
12. A20: Dana's personal stake? (determines change management approach)

---

## Economic & Cost Assumptions (Added from Candidate Prioritization)

### A23: Fully Loaded Hourly Cost for Front-Desk Staff
**Assumption**: Front-desk staff fully loaded hourly cost is $35/hr (salary + benefits + management overhead + facilities).  
**Confidence**: Medium  
**Rationale**: Medical office administrative staff in Mid-Atlantic US typically earn $28–32/hr base salary. Fully loaded cost (benefits, payroll taxes, overhead, facilities) adds 20–30% → $33–42/hr range. Using $35/hr as midpoint estimate.  
**Impact on design**: Determines baseline cost per case for ROI calculations. If actual cost is lower ($30/hr), agent ROI decreases. If higher ($40/hr), ROI increases.  
**Discovery question to resolve**: "What is your front-desk staff's fully loaded hourly cost (salary + benefits + overhead)? Can you share anonymized payroll data for TCO modeling?"

---

### A24: Fully Loaded Hourly Cost for Dana (Practice Manager)
**Assumption**: Dana's fully loaded hourly cost is $50/hr (RN-trained practice manager, 11 years tenure).  
**Confidence**: Medium  
**Rationale**: RN-trained practice managers in small primary care practices (Mid-Atlantic US) typically earn $65k–75k annual salary (base). Fully loaded cost (benefits, payroll taxes, overhead, facilities) adds 25–35% → $81k–101k fully loaded / 2,080 hrs/year = $39–49/hr. Using $50/hr as midpoint estimate accounting for 11-year tenure (higher end of range).  
**Impact on design**: Determines baseline cost for JtD 2.3 (PA chase), which Dana primarily owns. If actual cost is lower, agent ROI for JtD 2.3 decreases.  
**Discovery question to resolve**: "What is Dana's fully loaded hourly cost? (If sensitive, can provide range: $40–50/hr, $50–60/hr, etc.)"

---

### A25: Wave 1 Build Cost Estimate
**Assumption**: Wave 1 build cost is $530k–950k (midpoint $740k) for 3–4 months development (1 FDE + 1 platform engineer + 25% platform overhead + integrations + testing).  
**Confidence**: Low  
**Rationale**: Industry benchmarks for agentic system development: FDE fully loaded cost ~$150–200k/year (salary + benefits + overhead), platform engineer ~$120–150k/year, 25% platform overhead (infra, tooling, management), integration work (Availity, athenahealth, DoseSpot, payer portals) ~$50–100k, testing/validation ~$30–50k. 3–4 months → $450–800k development + $80–150k integration/testing = $530k–950k total.  
**Impact on design**: Determines economic gate for Wave 1. If build cost exceeds $950k, payback period lengthens beyond acceptable threshold (likely >18 months). If build cost is lower (e.g., $400k via reusable platform assets), payback shortens.  
**Discovery question to resolve**: "What is your budget range for Wave 1 agent development? What payback period is acceptable (12 months? 18 months? 24 months)?"

---

### A26: Time Saved per Case by Agent
**Assumption**: Agent saves 3–8 min per case (varies by JtD complexity) by reducing manual lookup time, decision time, or data entry time.  
**Confidence**: Low  
**Rationale**: Estimated based on cognitive load analysis. Examples: JtD 1.1 (insurance verification) saves ~3 min by automating stale-verification check + Availity retry logic. JtD 2.3 (PA chase) saves ~8 min by automating status check + payer-pattern lookup (Dana no longer checks Google Sheets + payer portal manually). JtD 4.2 (med reconciliation) saves ~4 min by structuring patient interview + DoseSpot cross-reference (reduces back-and-forth with patient). **These are estimates; require validation via time-motion study or pilot testing.**  
**Impact on design**: **Critical for ROI**. Time-saved drives annual saving calculation. If actual time saved is 50% lower (1.5–4 min), annual saving drops from $234k → $117k, extending payback from 3.2 years → 6.3 years (likely unacceptable). If time saved is 50% higher (4.5–12 min), payback shortens to 1.6 years (acceptable).  
**Discovery question to resolve**: "Can we conduct a time-motion study with your front-desk staff to measure actual time spent on each JtD? (Observe 20–30 cases per JtD; measure baseline time without agent.)"

---

## Summary: High-Priority Assumptions to Resolve
