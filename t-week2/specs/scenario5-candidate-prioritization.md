# Candidate Prioritization: Small-Clinic Patient Intake
## Scenario 5 — Westbridge Family Medicine

**Practice**: Westbridge Family Medicine (6-physician, 2 locations, ~180 patients/day)  
**Function**: 4-person front-desk intake team  
**Analysis**: Volume × Value prioritization for 13 Jobs to be Done

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Scoring Methodology](#scoring-methodology)
3. [JtD Scoring Results](#jtd-scoring-results)
4. [Volume × Value Quadrant Analysis](#volume--value-quadrant-analysis)
5. [Feasibility Assessment](#feasibility-assessment)
6. [Implementation Waves](#implementation-waves)
7. [Economic Validation Requirements](#economic-validation-requirements)

---

## Executive Summary

### Prioritization Overview

Of 13 Jobs to be Done evaluated, **4 JtDs qualify as strong agentic candidates** (Value score ≥ 15), representing the intersection of high volume and high non-deterministic reasoning. Two RPA candidates (JtD 3.1, 4.1) are excluded from agent development due to deterministic nature.

### Top Priority Candidates (Value Score ≥ 15)

| Rank | JtD | Description | Volume | Non-Det | Value | Archetype | Wave |
|------|-----|-------------|--------|---------|-------|-----------|------|
| 1 | 4.2 | Reconcile medication changes with patient | 180/day | 4 | **20** | Human-led + Agent Support | Wave 1 |
| 2 | 3.2 | Triage visit reason (routine/urgent/same-day) | 180/day | 4 | **20** | Human-led + Agent Support | Wave 2 |
| 3 | 1.1 | Verify active insurance eligibility | 180/day | 3 | **15** | Agent-led + Human Oversight | Wave 1 |
| 4 | 1.2 | Resolve manual insurance verification cases | 54/day | 4 | **16** | Human-led + Agent Support | Wave 2 |

### Strategic Recommendation: Three-Wave Implementation

**Wave 1 (Foundation — Months 1-6)**:
- **JtD 1.1**: Insurance verification (high volume, proven failure mode [A02])
- **JtD 2.3**: PA chase (encodes Dana's tribal knowledge [A05, A06]; eliminates shadow system risk)
- **JtD 4.2**: Medication reconciliation (high volume, patient safety impact)

**Rationale**: Wave 1 prioritizes documented failure modes (billing errors [A02], aborted visits [A07], DoseSpot gaps [A11]) with clear ROI. Builds foundational integrations: Availity API, athenahealth EHR, DoseSpot, payer portals.

**Wave 2 (Compounding — Months 7-12)**:
- **JtD 3.2**: Visit-reason triage (high volume, patient safety; requires clinical red-flag protocols formalized first)
- **JtD 1.2**: Manual insurance verification (inherits Wave 1 Availity integration; adds payer-pattern recognition)
- **JtD 2.2**: PA submission (inherits Wave 1 payer portal integrations; adds Dana's workaround encoding)

**Rationale**: Wave 2 inherits Wave 1 integrations (lower marginal build cost). Tackles higher complexity (clinical triage, payer-specific workarounds). Requires Wave 1 governance and testing infrastructure.

**Wave 3 (Optimization — Months 13+)**:
- **JtD 4.3**: Allergy review (extends Wave 1 med reconciliation; marginal value-add)
- **JtD 1.3**: Self-pay/MCO edge cases (low volume [A22]; high complexity; niche value)
- **JtD 2.1**: PA requirement lookup (extends Wave 1 PA chase; lower priority than chase itself)

**Rationale**: Wave 3 addresses remaining gaps with lower ROI. Consider as continuous improvement after Wave 1-2 stabilize.

### Key Gating Factors

**Before Wave 1**:
1. Dana must articulate payer-specific PA chase rules [Discovery Q1] — If not encodable, JtD 2.3 drops to Wave 2
2. Clinical staff must define visit-reason red-flag criteria [Discovery Q4] — Required for JtD 3.2 (currently Wave 2)
3. HIPAA/malpractice insurance approval for AI in patient intake [Discovery Q12] — Blocks entire program if denied

**Before Wave 2**:
1. Wave 1 agent performance validated (accuracy, HITL rate, TCO)
2. Front-desk staff trained on agent handoffs (documentation vs. judgment boundary [A12])
3. Governance infrastructure operational (audit trails, escalation protocols, error recovery)

### Expected Cumulative Impact

**Wave 1 targets**:
- Prevent 3rd+ occurrence of stale verification billing errors [A02]
- Prevent PA-related visit cancellations [A07: "second time this has happened"]
- Close DoseSpot gaps for 180 patients/day [A11]
- Encode Dana's tribal knowledge (reduce bus factor risk [A05, A06])

**Wave 1-2 combined**:
- Address 730+ daily JtD executions (80% of intake cognitive load)
- Reduce manual insurance verification rate from 30% → 15–20% [A01]
- Formalize clinical triage protocols [A10]
- Eliminate Google Sheets shadow system [A06]

---

## Scoring Methodology

### Volume Score (1-5): Execution Frequency

Based on ATX scoring framework (`atx-scoring.md`):

| Score | Frequency Range | Description |
|-------|-----------------|-------------|
| 5 | 100+ per day | Very frequent: hundreds+ per day or continuous stream |
| 4 | 50–99 per day | Frequent: 50–200 per day |
| 3 | 10–49 per day | Regular: 10–50 per day, or high volume per week |
| 2 | 3–9 per day | Moderate: several per day or high volume per month |
| 1 | <3 per day | Infrequent: weekly or monthly |

### Non-Determinism Score (1-5): Reasoning Beyond Rules

Based on ATX scoring framework (`atx-scoring.md`):

| Score | Reasoning Level | Description |
|-------|-----------------|-------------|
| 5 | High reasoning | Requires synthesis of multiple data sources, policy interpretation, contextual judgment |
| 4 | Significant reasoning | Follows patterns but requires contextual adaptation and exception handling |
| 3 | Mixed | Core path is rule-based but exceptions and edge cases require reasoning |
| 2 | Mostly deterministic | Small reasoning component around structured rules |
| 1 | Fully deterministic | Pure rules/logic, no reasoning required (RPA candidate) |

### Value Score (1-25): Agentic Value

**Formula**: `Value = Volume Score × Non-Determinism Score`

**Interpretation**:
- **Score ≥ 15**: Strong agentic candidate (primary targets)
- **Score 8–14**: Consider agentic, validate with TCO
- **Score < 8**: Use rule-based automation or don't automate

### Exclusions from Agent Development

**RPA candidates** (Non-Determinism = 1):
- **JtD 3.1**: Collect pre-visit questionnaire (portal path is deterministic patient self-service; paper path is manual data entry)
- **JtD 4.1**: Pull medication list from DoseSpot (API call already automated; no reasoning required)

---

## JtD Scoring Results

### Summary Table

| JtD ID | Description | Volume/Day | Vol Score | Non-Det Score | Value Score | Archetype | Priority |
|--------|-------------|------------|-----------|---------------|-------------|-----------|----------|
| **4.2** | Reconcile medication changes | 180 | 5 | 4 | **20** | Human-led + Agent Support | **High** |
| **3.2** | Triage visit reason | 180 | 5 | 4 | **20** | Human-led + Agent Support | **High** |
| **1.2** | Manual insurance verification | 54 | 4 | 4 | **16** | Human-led + Agent Support | **High** |
| **1.1** | Verify insurance eligibility (auto) | 180 | 5 | 3 | **15** | Agent-led + Human Oversight | **High** |
| **2.3** | Chase pending PA approvals | 25 | 3 | 4 | **12** | Agent-led + Human Oversight | **Medium** |
| **2.2** | Submit PA request to payer | 25 | 3 | 4 | **12** | Human-led + Agent Support | **Medium** ⬆ |
| **4.3** | Review and update allergy flags | 180 | 5 | 2 | **10** | Human-led + Agent Support | **Medium** |
| **1.3** | Self-pay/Medicaid MCO edge cases | 25 | 3 | 3 | **9** | Human-led + Agent Support | **Medium** |
| **2.1** | Identify PA requirement | 25 | 3 | 2 | **6** | Agent-led + Human Oversight | **Low** |
| **3.1** | Collect pre-visit questionnaire | 180 | 5 | 1 | **5** | RPA (excluded) | **N/A** |
| **4.1** | Pull med list from DoseSpot | 180 | 5 | 1 | **5** | RPA (excluded) | **N/A** |

### Detailed Scoring Rationale

#### High-Value Candidates (Score ≥ 15)

---

**JtD 4.2: Reconcile medication changes with patient**
- **Volume/day**: 180
- **Volume score**: 5 (Very frequent: 180/day = continuous stream)
- **Non-Determinism score**: 4 (Significant reasoning)
  - **Rationale**: Agent must cross-reference patient verbal report (unstructured) vs. DoseSpot sync (structured), detect discrepancies ("patient says stopped, but refilled 7 days ago"), and flag clinically ambiguous cases. Patterns exist (med stopped, new med added, dosage change) but require contextual adaptation per patient. Exception handling: patients forget med names, confuse dosage vs. med change, report changes inconsistently [A12]. Agent structures interview but cannot assess clinical significance (physician review required).
- **Value score**: 5 × 4 = **20**
- **Archetype**: Human-led + Agent Support
- **Prioritization rationale**: Highest volume + high reasoning. Documented DoseSpot gaps [A11]. Patient safety impact (prescribing error risk). Agent can close gaps immediately without waiting for DoseSpot integration improvements.

---

**JtD 3.2: Triage visit reason (routine vs. urgent vs. same-day)**
- **Volume/day**: 180
- **Volume score**: 5 (Very frequent: 180/day)
- **Non-Determinism score**: 4 (Significant reasoning)
  - **Rationale**: Agent must parse unstructured symptom descriptions ("some chest discomfort," "feeling dizzy") and detect red-flag patterns requiring escalation. Patterns exist (chest pain → urgent, med refill → routine) but symptoms are under-reported or over-reported by patients, requiring contextual interpretation. NLP required for semantic matching ("discomfort," "pressure," "tightness" all map to "chest pain"). Hard constraint: agent cannot make final triage decision [Hard Constraint #2]; must escalate to RN/physician. High reasoning because symptom language varies widely and clinical judgment is ultimately required.
- **Value score**: 5 × 4 = **20**
- **Archetype**: Human-led + Agent Support
- **Gating requirement**: Red-flag criteria must be documented or formalized with clinical staff before deployment [A09, A10: Discovery Q4]. If protocols don't exist, JtD 3.2 moves to Wave 2 (after protocols created in Wave 1 planning).
- **Prioritization rationale**: Highest volume + high reasoning. Patient safety impact (under-triage = delayed care). Currently no documented protocols [A10] — agent can formalize informal rules, making them consistent and auditable.

---

**JtD 1.2: Resolve manual insurance verification cases**
- **Volume/day**: 54 (30% of 180 total)
- **Volume score**: 4 (Frequent: 50–99/day)
- **Non-Determinism score**: 4 (Significant reasoning)
  - **Rationale**: Agent provides pattern recognition and decision-support for unstructured phone-based verification. Reasoning required: "Accept patient's verbal report vs. call payer?" "Defer visit or bill as self-pay?" "Which payers have reliable portals vs. must call?" [A03]. Exception handling: payer systems down, ambiguous payer responses ("coverage pending"), patient doesn't have card. Agent cannot execute phone calls or make final judgment calls ("defer visit?"), but can provide contextual recommendations based on prior cases and payer patterns (extension of Dana's PA chase logic [A05] to eligibility).
- **Value score**: 4 × 4 = **16**
- **Archetype**: Human-led + Agent Support
- **Prioritization rationale**: High volume + high reasoning. Inherits Wave 1 Availity integration (retry logic, stale detection). Adds payer-specific pattern recognition. Reduces 10–20 min wait times (agent can't eliminate payer hold times, but can reduce decision time via checklist).

---

**JtD 1.1: Verify active insurance eligibility (automated path)**
- **Volume/day**: 180
- **Volume score**: 5 (Very frequent: 180/day)
- **Non-Determinism score**: 3 (Mixed: rule-based core with reasoning edge cases)
  - **Rationale**: Core path is deterministic (Availity API call: binary success/failure). Reasoning required for: (1) stale verification detection (>6 months old → trigger re-verify) [A02], (2) MCO plan fuzzy matching (patient card name vs. Availity database mismatch) [A03], (3) retry logic for transient API failures [A01]. Agent applies rules ("last verified >6 months = stale") but also contextual reasoning ("patient has chronic condition + stable commercial insurance → 6-month window acceptable" vs. "Medicaid MCO → verify every visit due to eligibility churn"). Score is 3 (not 4) because majority of cases (70%) are straightforward API calls with binary response.
- **Value score**: 5 × 3 = **15**
- **Archetype**: Agent-led + Human Oversight
- **Prioritization rationale**: High volume. Documented failure mode [A02: "third time" billing error]. Agent can prevent recurring failures immediately. Builds Availity integration reusable for JtD 1.2 (manual verification) in Wave 2.

---

#### Medium-Value Candidates (Score 8–14)

---

**JtD 2.3: Chase pending PA approvals**
- **Volume/day**: 25 (all PAs require monitoring; ~15/day require active chase)
- **Volume score**: 3 (Regular: 10–50/day)
- **Non-Determinism score**: 4 (Significant reasoning)
  - **Rationale**: Agent encodes Dana's payer-specific chase timing rules [A05, A06]. Rules exist and are articulable ("UHC is always 6 days, not 5"; "Wellpath always denies colonoscopy first time, chase on day 7"), but require contextual application per payer + procedure combination. Exception handling: payer response times vary (holidays, system load), portal status sometimes stale, escalation decision requires judgment ("reschedule visit or keep trying?"). High reasoning because Dana's rules are pattern-based, not deterministic ("Aetna is fast *this month* (unusual)" — temporal context matters).
- **Value score**: 3 × 4 = **12**
- **Archetype**: Agent-led + Human Oversight
- **Gating requirement**: Dana must articulate payer-specific rules explicitly [Discovery Q1]. If rules are pure intuition (not encodable), JtD 2.3 becomes Human-led + Agent Support (agent reminds, doesn't execute).
- **Prioritization rationale**: **Strategic value exceeds numeric score**. Encodes tribal knowledge (bus factor risk [A05, A06]). Prevents documented failure mode [A07: aborted visits]. Eliminates shadow system [A06: Google Sheets]. Placed in **Wave 1** despite Value score 12 because: (1) tribal knowledge capture is one-time opportunity (if Dana leaves, knowledge is lost), (2) PA failures have high patient dissatisfaction + revenue impact, (3) shadow system creates audit/compliance gaps.

---

**JtD 4.3: Review and update allergy flags**
- **Volume/day**: 180
- **Volume score**: 5 (Very frequent: 180/day)
- **Non-Determinism score**: 2 (Mostly deterministic with small reasoning component)
  - **Rationale**: Core path is deterministic (ask patient: "Any new allergies?" → document response). Reasoning required for: (1) distinguishing allergy vs. side effect vs. intolerance (agent documents symptom; physician decides), (2) severity assessment (agent flags for physician). Low reasoning because agent's role is structured data collection + escalation, not clinical decision. Exception handling: patient unsure ("I felt nauseous — is that allergy?"), doesn't remember which med caused reaction. Agent prompts for detail but cannot make final determination [A13].
- **Value score**: 5 × 2 = **10**
- **Archetype**: Human-led + Agent Support
- **Prioritization rationale**: High volume but low reasoning. Extends JtD 4.2 (med reconciliation) from Wave 1. Marginal value-add (allergy decision-support fires at prescribing time [A13], not intake). Place in Wave 3 as continuous improvement.

---

**JtD 2.2: Submit PA request to payer**
- **Volume/day**: 25
- **Volume score**: 3 (Regular: 10–50/day)
- **Non-Determinism score**: 4 (Significant reasoning) - **UPGRADED from 3**
  - **Rationale**: Core path is semi-deterministic (copy CPT, ICD codes, demographics into payer portal fields). Reasoning required for: (1) selecting which clinical documentation to attach (payer-specific requirements), (2) applying Dana's workarounds [Discovery Q2 confirms **7-8 payer-specific workarounds**, not just 1: Wellpath colonoscopy, Aetna specialty referrals, Humana imaging narrative, BCBS cardiac EKG/stress test, Medicaid DME visit notes, plus 3 more]. Low tool coverage (20+ payer portals, no API) means agent-led execution would require brittle RPA. Agent provides checklist + documentation retrieval. **Score upgraded to 4 because workaround reasoning is now substantial (7-8 patterns, not 1).**
- **Value score**: 3 × 4 = **12** - **UPGRADED from 9**
- **Archetype**: Human-led + Agent Support
- **Prioritization rationale**: Medium value. Inherits Wave 1 payer portal patterns (from JtD 2.3 PA chase). Encodes Dana's workarounds [A05]. Place in Wave 2 after PA chase (JtD 2.3) validates payer integration approach.

---

**JtD 1.3: Handle self-pay and Medicaid MCO edge cases**
- **Volume/day**: 25 (estimated; 10–15% of 180) [A22]
- **Volume score**: 3 (Regular: 10–50/day)
- **Non-Determinism score**: 3 (Mixed: MCO lookup is rule-based, payment negotiation requires judgment)
  - **Rationale**: MCO plan lookup can be rule-based (fuzzy match patient card name to state portal database), but plan identification is ambiguous due to frequent eligibility churn [A03]. Self-pay payment arrangement negotiation requires judgment (assess patient financial situation, offer payment plan, flag for financial counseling). Agent can assist with MCO lookup and self-pay workflow checklist, but cannot negotiate payment terms. Score is 3 (not 4) because MCO lookup is primary task; self-pay negotiation is smaller subset.
- **Value score**: 3 × 3 = **9**
- **Archetype**: Human-led + Agent Support
- **Prioritization rationale**: Medium value. Low volume (estimated 25/day [A22]; requires validation via Discovery Q22). High complexity (state-specific MCO rules, patient financial negotiation). Place in Wave 3 as niche use case after higher-volume JtDs stabilize.

---

#### Low-Value Candidates (Score < 8)

---

**JtD 2.1: Identify PA requirement for scheduled procedure/imaging/referral**
- **Volume/day**: 25
- **Volume score**: 3 (Regular: 10–50/day)
- **Non-Determinism score**: 2 (Mostly deterministic: rule-based lookup with human override for stale rules)
  - **Rationale**: Core task is deterministic rule lookup: "CPT code + payer ID → PA required (yes/no)." Reasoning required only when athenahealth rules are stale [A04] (agent flags: "Rule last updated 9 months ago; recommend manual confirmation"). Responsibility clarification (practice vs. specialist) requires judgment, but this is edge case, not core workflow. Low reasoning because majority of lookups are straightforward database queries. Exception handling: ambiguous diagnostic/screening distinction (requires clinical judgment, escalate).
- **Value score**: 3 × 2 = **6**
- **Archetype**: Agent-led + Human Oversight
- **Prioritization rationale**: Low value (numeric score < 8). PA requirement lookup is less urgent than PA chase (JtD 2.3), which prevents aborted visits [A07]. Lookup can be manual until Wave 3 without major impact. Agent value is primarily flagging stale rules [A04], which is nice-to-have, not critical.

---

#### RPA Candidates (Excluded from Agent Development)

---

**JtD 3.1: Collect pre-visit questionnaire (portal or paper)**
- **Volume/day**: 180 (126 portal + 54 paper)
- **Volume score**: 5
- **Non-Determinism score**: 1 (Fully deterministic)
  - **Rationale**: Portal path (70%) is patient self-service (deterministic: patient enters data, system saves). Paper path (30%) is manual data entry (front-desk types handwritten form into athenahealth). No reasoning required; pure data entry. Agent value is minimal (portal adoption prompts, data validation).
- **Value score**: 5 × 1 = **5**
- **Recommendation**: **Not an agent candidate.** Increase portal adoption (70% → 85%) via patient communication (SMS reminders, pre-visit emails) and UX improvements. Paper path will always require human data entry (no OCR mentioned; handwriting reading requires human).

---

**JtD 4.1: Pull current medication list from DoseSpot/pharmacy**
- **Volume/day**: 180
- **Volume score**: 5
- **Non-Determinism score**: 1 (Fully deterministic)
  - **Rationale**: DoseSpot API call is already automated (patient ID → API → med list). No reasoning required. Agent value is gap-filling interview script [A11] (prompt for OTC, supplements, mail-order), but this is structured data collection (Human-led + Automation Support), not agentic reasoning.
- **Value score**: 5 × 1 = **5**
- **Recommendation**: **Not an agent candidate.** Core task is already automated. Agent can provide interview script for DoseSpot gaps [A11], but this is low priority; focus on JtD 4.2 (medication reconciliation), which requires reasoning.

---

## Volume × Value Quadrant Analysis

### Quadrant Visualization

**Volume × Non-Determinism Matrix** (Value Score = Volume Score × Non-Determinism Score)

**QUADRANT 1: PRIMARY AGENTIC TARGETS** (High Volume + High Non-Determinism) ⭐
- JtD 4.2 (Value=20)
- JtD 3.2 (Value=20)
- JtD 1.2 (Value=16)
- JtD 1.1 (Value=15)

**QUADRANT 2: RPA / RULES-BASED** (High Volume + Low Non-Determinism)
- JtD 3.1 (Value=5)
- JtD 4.1 (Value=5)
- JtD 4.3 (Value=10)

**QUADRANT 3: NOT AUTOMATING** (Low Volume + Low Non-Determinism)
- No candidates

**QUADRANT 4: SELECT USE CASES** (Low Volume + High Non-Determinism)
- JtD 2.3 (Value=12)
- JtD 1.3 (Value=9)
- JtD 2.2 (Value=9)
- JtD 2.1 (Value=6)

### Quadrant Interpretation

#### Quadrant 1: PRIMARY AGENTIC TARGETS (Top Right — High Volume + High Non-Determinism)

**JtDs**: 4.2 (Value 20), 3.2 (Value 20), 1.2 (Value 16), 1.1 (Value 15)

**Characteristics**:
- 180/day (4.2, 3.2, 1.1) or 54/day (1.2) volume
- Requires significant contextual reasoning, pattern recognition, exception handling
- Cannot be solved with deterministic rules or simple scripts
- High cognitive load on front-desk staff (structured interview, cross-referencing, NLP)

**Strategic priority**: These are the core agentic opportunities. Agent value comes from reasoning over unstructured inputs (patient verbal reports, symptom descriptions, DoseSpot discrepancies) and adapting to context (patient history, payer patterns, clinical red flags).

**Implementation approach**:
- **Wave 1**: JtD 1.1 (insurance verification), JtD 4.2 (med reconciliation) — foundational integrations (Availity, DoseSpot, athenahealth)
- **Wave 2**: JtD 3.2 (triage — requires red-flag protocols formalized first), JtD 1.2 (manual verification — inherits Wave 1 Availity integration)

---

#### Quadrant 2: RPA / RULES-BASED (Top Left — High Volume + Low Non-Determinism)

**JtDs**: 3.1 (portal intake), 4.1 (DoseSpot API), 4.3 (allergy review — borderline)

**Characteristics**:
- 180/day volume
- Deterministic or mostly deterministic (API calls, data entry, structured checklists)
- No significant reasoning required; can be solved with rules, scripts, or existing automation

**Strategic priority**: **Exclude JtD 3.1 and 4.1 from agent development** (already automated or not automatable). JtD 4.3 (allergy review) is borderline (score 10) — include in Wave 3 as low-priority extension of JtD 4.2 (med reconciliation).

**Implementation approach**:
- **JtD 3.1**: Increase portal adoption (patient communication, UX) — not an agent problem
- **JtD 4.1**: Already automated via DoseSpot API — not an agent problem
- **JtD 4.3**: Wave 3 as marginal extension of Wave 1 med reconciliation

---

#### Quadrant 3: NOT WORTH AUTOMATING (Bottom Left — Low Volume + Low Non-Determinism)

**JtDs**: 2.1 (PA requirement lookup — Value 6)

**Characteristics**:
- 25/day volume (low)
- Mostly deterministic (rule-based PA requirement database lookup)
- Low cognitive load (quick database query)

**Strategic priority**: Low. PA requirement lookup is less urgent than PA chase (JtD 2.3). Manual lookup is acceptable until Wave 3.

**Implementation approach**: **Wave 3** as nice-to-have. Primary value is flagging stale athenahealth rules [A04]. Agent can be simple lookup wrapper + staleness alert (low investment).

---

#### Quadrant 4: SELECT AGENTIC USE CASES (Bottom Right — Low Volume + High Non-Determinism)

**JtDs**: 2.3 (PA chase — Value 12), 2.2 (PA submission — Value 9), 1.3 (self-pay/MCO — Value 9)

**Characteristics**:
- 25/day volume (low)
- High reasoning required (payer-specific patterns, tribal knowledge, contextual judgment)
- High impact per case (PA failures → visit cancellations [A07]; self-pay errors → billing compliance risk)

**Strategic priority**: **JtD 2.3 (PA chase) elevated to Wave 1 despite low volume** due to strategic value:
1. Encodes Dana's tribal knowledge (one-time capture opportunity [A05, A06])
2. Prevents documented failure mode (aborted visits [A07])
3. Eliminates shadow system risk (Google Sheets [A06])
4. High patient dissatisfaction + revenue impact when PA fails

**JtD 2.2 (PA submission)** and **JtD 1.3 (self-pay/MCO)**: Wave 2-3. Medium value, lower urgency than Wave 1 priorities.

**Implementation approach**:
- **JtD 2.3**: Wave 1 (strategic value overrides numeric score)
- **JtD 2.2**: Wave 2 (inherits payer portal patterns from JtD 2.3)
- **JtD 1.3**: Wave 3 (niche use case; low volume [A22]; validate volume assumption first)

---

## Feasibility Assessment

### Feasibility Scoring Framework

Score each prioritized candidate (Value ≥ 8) on 6 factors (1-5 scale, 5 = most favorable):

| Factor | Weight | Description |
|--------|--------|-------------|
| Data availability | High | Is required data accessible and clean? |
| System integration feasibility | High | APIs, connectors, or reasonable build effort |
| Compliance risk | Medium | Red flags for HIPAA, malpractice, sector regulation |
| Context stability | Medium | Does the domain change frequently? |
| Organizational readiness | Medium | Change management, HITL tolerance, leadership buy-in |
| TCO viability | High | Preliminary sense-check: does economics likely close? |

### Feasibility Scores by JtD

| JtD | Data Avail | System Integ | Compliance | Context Stable | Org Ready | TCO Viable | Total | Risk Level |
|-----|------------|--------------|------------|----------------|-----------|------------|-------|------------|
| **1.1** | 5 | 5 | 4 | 4 | 4 | 5 | 27/30 | **Low** |
| **2.3** | 4 | 3 | 4 | 3 | 3 | 4 | 21/30 | **Medium** |
| **4.2** | 4 | 4 | 3 | 4 | 3 | 4 | 22/30 | **Medium** |
| **3.2** | 3 | 4 | 2 | 3 | 2 | 4 | 18/30 | **High** |
| **1.2** | 3 | 2 | 4 | 3 | 3 | 3 | 18/30 | **High** |
| **4.3** | 4 | 4 | 3 | 4 | 3 | 3 | 21/30 | **Medium** |
| **2.2** | 3 | 2 | 4 | 3 | 3 | 3 | 18/30 | **High** |
| **1.3** | 2 | 2 | 4 | 2 | 3 | 2 | 15/30 | **High** |
| **2.1** | 3 | 3 | 4 | 2 | 3 | 3 | 18/30 | **Medium** |

### Detailed Feasibility Analysis

#### JtD 1.1: Verify active insurance eligibility — Feasibility: HIGH (27/30)

| Factor | Score | Rationale |
|--------|-------|-----------|
| **Data availability** | 5 | Structured: patient ID, payer ID, DOS → Availity API. athenahealth has verification history (last verified date). [A02: Known data gap — stale verifications not flagged automatically.] |
| **System integration** | 5 | Availity REST API available. athenahealth integration exists. Stale-verification trigger requires athenahealth API read (last verified date field) — feasible [A15: athenahealth REST APIs available]. |
| **Compliance risk** | 4 | HIPAA applies (patient data access). Malpractice risk is low (incorrect verification is reversible; can re-verify, refile claim). Requires BAA with agent platform [A17]. |
| **Context stability** | 4 | Payer rules stable (insurance plan structures don't change frequently). Availity API stable. Stale-verification threshold (6 months) is practice policy [A21], not external regulation (low churn). |
| **Org readiness** | 4 | Documented failure mode [A02: "third time"] creates urgency. Dana + senior physician bought in (physician initiated AI project). Front-desk will accept agent (reduces manual verification workload). |
| **TCO viability** | 5 | High volume (180/day = 45,000/year). Low token cost (structured input: patient ID + payer ID; short output: active/inactive + escalation flag). HITL rate: 30% (manual verification fallback) already baked into current workflow. Strong ROI expected. |

**Gating risks**: None. Proceed to Wave 1.

---

#### JtD 2.3: Chase pending PA approvals — Feasibility: MEDIUM (21/30)

| Factor | Score | Rationale |
|--------|-------|-----------|
| **Data availability** | 4 | Structured: PA submission date, payer ID, visit date → athenahealth PA module. **Gating dependency**: Dana's payer-specific chase timing rules [A05, A06] must be encodable [Discovery Q1]. If rules are pure intuition, data availability drops to 2 (not encodable). |
| **System integration** | 3 | Payer portals (no standard API; 20+ different). athenahealth PA module integration unclear [A15: API accessibility unknown]. Google Sheets replacement requires athenahealth PA write access or agent-managed system. Medium effort. |
| **Compliance risk** | 4 | HIPAA applies. Malpractice risk is low (PA chase is administrative, not clinical). Requires BAA [A17]. |
| **Context stability** | 3 | Payer behavior patterns change (Dana notes: "Aetna is fast *this month* (unusual)" [A05]). Agent rules may need periodic updates (quarterly) as payer response times shift. Medium stability. |
| **Org readiness** | 3 | Dana is key stakeholder. If she sees agent as codifying her expertise (career-advancing [A20]), buy-in is high. If she sees it as replacement threat, resistance risk. Requires careful change management. |
| **TCO viability** | 4 | Medium volume (25/day = 6,250/year). High impact per case (aborted visit = $200–500 revenue loss + patient dissatisfaction). Token cost moderate (payer-pattern reasoning requires multi-turn logic). HITL: Dana reviews escalations (5–10/day). ROI likely positive but requires validation. |

**Gating risks**:
1. **Discovery Q1**: Can Dana articulate payer-specific rules? If no → agent becomes reminder system (Human-led), not autonomous chase executor (Agent-led).
2. **athenahealth PA API**: If PA data not API-accessible [A15], agent operates as parallel system (higher build cost + manual data sync).

**Mitigation**: Validate both dependencies before Wave 1 kickoff. If Q1 fails, defer to Wave 2 (Human-led + Agent Support archetype).

---

#### JtD 4.2: Reconcile medication changes with patient — Feasibility: MEDIUM (22/30)

| Factor | Score | Rationale |
|--------|-------|-----------|
| **Data availability** | 4 | Semi-structured: DoseSpot API (structured med list) + patient verbal report (unstructured). Agent must cross-reference. DoseSpot gaps [A11] are known; agent can prompt for them. Data is accessible but incomplete. |
| **System integration** | 4 | DoseSpot API integrated with athenahealth. athenahealth med list API (read/write) likely accessible [A15]. Agent writes med changes + flags for physician review. Feasible integration. |
| **Compliance risk** | 3 | **HIPAA applies. Malpractice risk is MEDIUM** (incorrect med list → prescribing error risk). Agent must NOT assess clinical significance [A12: Hard Constraint #1]. Requires clear physician review workflow (agent documents; physician confirms). BAA required [A17]. |
| **Context stability** | 4 | Medication reconciliation workflow is stable (standard medical practice). DoseSpot gaps are stable (small pharmacies, assistance programs don't change frequently [A11]). High stability. |
| **Org readiness** | 3 | Front-desk staff must understand documentation vs. clinical assessment boundary [A12: Discovery Q9]. Training required. Physicians must buy into agent-documented med changes (trust agent prompts). Medium readiness; requires education. |
| **TCO viability** | 4 | High volume (180/day = 45,000/year). Token cost moderate (interview + cross-reference logic). HITL: physician reviews all flagged changes (built into visit workflow; no added time). ROI likely positive (closes DoseSpot gaps [A11]; reduces prescribing error risk). |

**Gating risks**:
1. **Front-desk training** [A12]: Staff must understand they document med changes (not assess clinical significance). Agent reinforces this boundary via UI prompts.
2. **Physician trust**: Physicians must accept agent-documented changes as reliable input (not dismiss as "AI error"). Requires pilot testing + accuracy validation.

**Mitigation**: Pilot with 2–3 physicians in Wave 1. Validate accuracy (agent-documented changes match physician post-visit assessment) before full rollout.

---

#### JtD 3.2: Triage visit reason — Feasibility: HIGH RISK (18/30)

| Factor | Score | Rationale |
|--------|-------|-----------|
| **Data availability** | 3 | Unstructured: patient symptom descriptions (free-text). athenahealth visit reason field. **Gating dependency**: Red-flag criteria must be documented [A09, A10: Discovery Q4]. If protocols don't exist, data is unusable (no ground truth for agent training). Medium availability. |
| **System integration** | 4 | athenahealth visit reason field (API read). Escalation via phone/pager/athenahealth messaging to RN/physician. Feasible integration. |
| **Compliance risk** | 2 | **HIPAA + MALPRACTICE RISK IS HIGH**. Under-triage = delayed care for urgent condition (patient safety risk; malpractice exposure). Over-triage = physician alert fatigue (physicians may ignore agent escalations if false-positive rate is high). Agent must NOT make final triage decision [Hard Constraint #2]; RN/physician decides. Requires careful escalation threshold tuning (bias toward over-escalation for safety). BAA required [A17]. |
| **Context stability** | 3 | Clinical triage protocols are stable (chest pain, difficulty breathing, severe bleeding are always urgent). But symptom language varies (patients under-report or use ambiguous terms). Medium stability. |
| **Org readiness** | 2 | **LOW READINESS**. Front-desk staff currently have no formal triage protocols [A10]. Clinical staff (RN/physician) must define red-flag criteria before agent deployment [Discovery Q4]. Physicians may resist agent escalations if false-positive rate is high (alert fatigue). Requires clinical staff buy-in + protocol formalization work. |
| **TCO viability** | 4 | High volume (180/day = 45,000/year). Token cost moderate (NLP for symptom parsing). HITL: RN/physician reviews all agent-flagged cases (adds 2–5 min per escalation; currently happens informally, so marginal added time is low). ROI likely positive (prevents under-triage; formalizes protocols). |

**Gating risks**:
1. **Discovery Q4**: Do red-flag protocols exist? If no → must create them with clinical staff before agent deployment. This is 1–3 month project (clinical review, policy writing, physician approval).
2. **Malpractice insurance approval** [Discovery Q12]: AI triage may require malpractice carrier review. If carrier requires human review of all agent outputs (not just escalations), agent value drops (becomes checklist, not autonomous flagging).

**Mitigation**: **Move JtD 3.2 to Wave 2**. Use Wave 1 planning phase (Months 1-3) to formalize red-flag protocols with clinical staff. Deploy agent in Wave 2 (Months 7-12) after protocols exist + Wave 1 governance infrastructure validates agent reliability.

---

#### JtD 1.2: Resolve manual insurance verification — Feasibility: HIGH RISK (18/30)

| Factor | Score | Rationale |
|--------|-------|-----------|
| **Data availability** | 3 | Unstructured: phone conversation with payer, patient-provided card (photos, verbal). Agent relies on front-desk staff to relay payer responses (not direct API). Medium availability. |
| **System integration** | 2 | **LOW INTEGRATION FEASIBILITY**. Payer phone calls have no API. Payer portals (20+ different, no standard API). Agent cannot automate phone calls (voice AI out of scope). Agent provides decision-support checklist + pattern recognition, but front-desk executes. Low integration opportunity. |
| **Compliance risk** | 4 | HIPAA applies. Malpractice risk is low (billing error is reversible). Requires BAA [A17]. |
| **Context stability** | 3 | Payer portal reliability varies (some portals are down frequently; staff must call instead). Medium stability. |
| **Org readiness** | 3 | Front-desk staff will accept agent (reduces decision time; provides pattern recognition [A05 extension to eligibility]). Medium readiness. |
| **TCO viability** | 3 | Medium volume (54/day = 13,500/year). **Low token cost savings** (agent doesn't eliminate 10–20 min payer hold time [A14]; only reduces decision time by ~2 min). ROI is marginal. May not pass economic gate. Requires TCO validation. |

**Gating risks**:
1. **Low tool coverage**: Agent cannot automate phone calls. Value is checklist + pattern recognition only (not execution).
2. **TCO viability unclear**: Agent reduces decision time (~2 min/case) but doesn't eliminate hold time (~15 min/case). Annual saving may not justify build cost.

**Mitigation**: **Move JtD 1.2 to Wave 2**. Validate TCO after Wave 1 (JtD 1.1 insurance verification) deployment. If JtD 1.1 reduces manual fallback rate from 30% → 20% (via stale detection + retry logic), JtD 1.2 volume drops from 54/day → 36/day, further reducing ROI. May cancel JtD 1.2 if ROI doesn't close.

---

## Implementation Waves

### Wave 1: Foundation (Months 1-6) — Self-Funding Core

**Objective**: Prevent documented failure modes. Build foundational integrations. Establish governance infrastructure. Achieve payback ≤ 12 months.

#### Wave 1 Candidates

| JtD | Description | Value | Volume | Feasibility | Priority Rationale |
|-----|-------------|-------|--------|-------------|-------------------|
| **1.1** | Verify insurance eligibility | 15 | 180/day | HIGH (27/30) | Prevents billing errors [A02: "third time"]. Builds Availity + athenahealth integrations reusable in Wave 2. |
| **2.3** | Chase pending PA approvals | 12 | 25/day | MEDIUM (21/30) | Encodes Dana's tribal knowledge [A05, A06]. Prevents aborted visits [A07]. Eliminates shadow system [A06]. Strategic value overrides numeric score. |
| **4.2** | Reconcile medication changes | 20 | 180/day | MEDIUM (22/30) | Closes DoseSpot gaps [A11]. Patient safety impact. Builds athenahealth + DoseSpot integrations. |

**Total Wave 1 volume**: 385 JtD executions/day (97,000/year)

**Foundational integrations built in Wave 1** (reusable in Wave 2-3):
1. **Availity API** (insurance eligibility) — reused in JtD 1.2 (manual verification)
2. **athenahealth EHR API** (patient data, med list, PA tracking) — reused in all Wave 2-3 JtDs
3. **DoseSpot API** (pharmacy sync) — reused in JtD 4.3 (allergy review)
4. **Payer portal patterns** (PA chase) — reused in JtD 2.2 (PA submission)
5. **Agent platform infrastructure** (audit trails, HITL routing, error recovery) — reused in all waves

**Governance infrastructure established in Wave 1**:
- HIPAA BAA with agent platform provider [A17]
- Audit trail system (all agent actions logged; human reviewer traceable)
- HITL escalation protocols (front-desk → Dana → RN/physician)
- Error recovery workflows (agent error → human override → log for retraining)
- Testing harness (mock patient cases; accuracy validation before production)

**Wave 1 gating dependencies (must resolve before kickoff)**:
1. **Discovery Q1**: Dana articulates payer-specific PA chase rules [A05] — If no → JtD 2.3 deferred to Wave 2
2. **Discovery Q12**: HIPAA/malpractice insurance approval — If denied → entire program blocked
3. **Discovery Q7**: Understand Availity 30% failure root cause [A01] — Informs JtD 1.1 design (retry logic vs. patient communication)

**Expected Wave 1 outcomes**:
- Zero stale verification billing errors (baseline: 3+ in last quarter [A02])
- Zero PA-related visit cancellations (baseline: 2+ documented [A07])
- DoseSpot gaps closed for 45,000 med reconciliations/year [A11]
- Dana's tribal knowledge encoded (bus factor risk eliminated [A05, A06])
- Google Sheets PA tracker replaced with shared agent system [A06]
- Governance + testing infrastructure operational for Wave 2

**Wave 1 payback target**: ≤ 12 months

---

### Wave 2: Compounding (Months 7-12) — Inherited Assets

**Objective**: Leverage Wave 1 integrations (lower marginal build cost). Tackle higher complexity (clinical triage, payer workarounds). Expand coverage to 80% of intake cognitive load.

#### Wave 2 Candidates

| JtD | Description | Value | Volume | Feasibility | Inherited Assets (from Wave 1) |
|-----|-------------|-------|--------|-------------|-------------------------------|
| **3.2** | Triage visit reason | 20 | 180/day | HIGH RISK (18/30) | Agent platform, audit trails, HITL protocols. **Requires**: Red-flag protocols formalized in Wave 1 planning phase [Discovery Q4]. |
| **1.2** | Manual insurance verification | 16 | 54/day | HIGH RISK (18/30) | Availity API (retry logic, stale detection from JtD 1.1). athenahealth integration. Payer-pattern recognition extends JtD 2.3 logic. |
| **2.2** | Submit PA request to payer | 9 | 25/day | HIGH RISK (18/30) | Payer portal patterns (from JtD 2.3). athenahealth clinical notes API. Dana's workaround checklist encoded [A05]. |

**Total Wave 2 volume**: 259 JtD executions/day (65,000/year)  
**Cumulative coverage (Wave 1 + 2)**: 644 JtD executions/day (162,000/year) — 80% of intake cognitive load

**New integrations built in Wave 2**:
- **Red-flag triage protocols** (formalized with clinical staff) — JtD 3.2
- **Payer-pattern database** (manual verification decision-support) — JtD 1.2

**Wave 2 gating dependencies**:
1. **Wave 1 performance validated**: Agent accuracy ≥ 95%, HITL rate matches expectations, TCO closes, no governance violations
2. **Discovery Q4**: Red-flag protocols formalized (clinical staff collaboration; 1–3 months in Wave 1 planning phase)
3. **JtD 1.2 TCO validation**: Manual verification volume post-Wave 1 (if JtD 1.1 reduces 30% → 20%, JtD 1.2 ROI drops; may cancel)

**Expected Wave 2 outcomes**:
- Visit-reason under-triage eliminated (red-flag protocols formalized [A10])
- Manual insurance verification decision time reduced by 50% (payer-pattern checklist)
- PA submission workarounds encoded [A05] (Wellpath, Aetna, etc. — all staff can apply)
- 80% of intake cognitive load covered by agent assistance (644 JtD executions/day)

---

### Wave 3: Optimization (Months 13+) — Continuous Improvement

**Objective**: Address remaining gaps. Low ROI use cases. Marginal extensions of Wave 1-2 agents.

#### Wave 3 Candidates

| JtD | Description | Value | Volume | Feasibility | Rationale |
|-----|-------------|-------|--------|-------------|-----------|
| **4.3** | Review and update allergy flags | 10 | 180/day | MEDIUM (21/30) | Extends Wave 1 med reconciliation (JtD 4.2). Marginal value-add (allergy decision-support fires at prescribing, not intake [A13]). |
| **1.3** | Self-pay/MCO edge cases | 9 | 25/day | HIGH RISK (15/30) | Niche use case. Low volume [A22]. Requires state-specific MCO knowledge. Defer until Wave 1-2 stabilize. |
| **2.1** | Identify PA requirement | 6 | 25/day | MEDIUM (18/30) | Low priority (lookup less urgent than chase [JtD 2.3]). Primary value: flag stale athenahealth rules [A04]. Simple lookup wrapper. |

**Total Wave 3 volume**: 230 JtD executions/day (58,000/year)  
**Cumulative coverage (Wave 1-3)**: 874 JtD executions/day (220,000/year) — 97% of intake cognitive load

**Wave 3 is optional continuous improvement** after Wave 1-2 demonstrate ROI and stabilize operationally. May cancel Wave 3 if ROI doesn't justify further investment.

---

## Economic Validation Requirements

### Preliminary TCO Assumptions (Requires Validation)

**Human baseline cost**:
- Fully loaded hourly cost: $35/hr (front-desk staff salary + benefits + overhead) [**Assumption A23**: Fully loaded cost for medical office admin in Mid-Atlantic US, typical range $30–40/hr]
- Dana's hourly cost: $50/hr (RN-trained, 11 years tenure) [**Assumption A24**: Practice manager with RN background, typical range $45–55/hr]

**Agent cost model (per case)**:
- **Token cost**: $0.02–0.05/case (Claude Sonnet 4 input + output tokens; varies by JtD complexity)
  - Simple tasks (JtD 1.1 eligibility check): ~500 input + 200 output tokens = $0.02
  - Complex tasks (JtD 4.2 med reconciliation): ~1,500 input + 800 output tokens = $0.05
- **Infrastructure cost**: $0.01/case (amortized platform overhead: compute, storage, networking)
- **HITL cost**: Varies by JtD (% cases requiring human review × review time × hourly cost)

**Build cost estimate (Wave 1)**:
- Development: 3–4 months × $150k–200k fully loaded FDE cost = $450k–800k [**Assumption A25**: One FDE + one platform engineer + 25% platform overhead]
- Integration: Availity API, athenahealth API, DoseSpot API, payer portals — $50k–100k (vendor setup, connector development)
- Testing: Mock patient cases, accuracy validation, physician review — $30k–50k
- **Total Wave 1 build cost**: $530k–950k (midpoint: $740k)

### Economic Gate Criteria

**Wave 1 must achieve**:
- **Payback period**: ≤ 12 months
- **Year 1 ROI**: > 0% (Wave 1 saving covers Wave 1 build cost within 12 months)
- **Accuracy**: ≥ 95% (agent output matches human judgment in mock testing)
- **HITL rate**: ≤ expected rate per JtD (agent doesn't create more work than it saves)

### Required Economic Validations (Before Wave 1 Kickoff)

1. **Validate fully loaded hourly cost** (front-desk staff + Dana) — Get actual salary + benefits data from Westbridge finance
2. **Validate volume estimates** [A22: Self-pay/MCO volume is estimated; needs confirmation via Discovery Q22]
3. **Mock test token consumption** (run agent on 50 sample cases per JtD; measure actual tokens used)
4. **Validate HITL rates** (run agent on 100 sample cases per JtD; measure % requiring human review)
5. **Calculate Wave 1 annual saving (REVISED with Discovery findings)**:
   ```
   TIME SAVINGS (per-case efficiency):
   JtD 1.1: 180 cases/day × 3 min saved × 260 days/year × $35/hr / 60 min/hr = $81,900/year
   JtD 2.3: 25 cases/day × 8 min saved × 260 days/year × $50/hr / 60 min/hr = $43,333/year
   JtD 4.2: 180 cases/day × 4 min saved × 260 days/year × $35/hr / 60 min/hr = $109,200/year
   Subtotal time savings: $234,433/year
   
   ONBOARDING TIME REDUCTION [Discovery Q15 - NEW]:
   Current onboarding: 3-4 months (16 weeks) for tribal knowledge
   Agent-enabled onboarding: 6-8 weeks (50% reduction via encoded knowledge)
   Turnover rate: 30%/year (industry standard medical office admin) = 1.2 new hires/year for 4-person team
   Onboarding cost savings: 1.2 hires × 8 weeks saved × $35/hr × 40 hrs/week = $13,440/year
   
   PATIENT EXPERIENCE VALUE [Discovery Q20 - NEW]:
   Senior physician priority: prevent patient-facing failures (visit cancellations + billing errors)
   Prevented PA cancellations: ~8-10/year × ($200 visit revenue + $5k patient lifetime value × 10% churn risk) = $20,000/year
   Prevented billing errors: ~12-15/year × ($150 refund admin + $2k reputation cost × 20% risk) = $8,000/year
   Subtotal patient experience: $28,000/year
   
   WAVE 1 TOTAL ANNUAL SAVING: $234k + $13k + $28k = $275,867/year
   ```
   [**Assumption A26**: Time saved per case is estimated (requires validation via time-motion study or pilot)]

6. **Calculate Wave 1 payback (REVISED)**: Build cost $740k / Annual saving $276k = **2.7 years payback** (was 3.2 years; still exceeds 12-month target)

**Result**: **Preliminary TCO does not pass economic gate** (2.7 years payback > 12-month target), but **improved from 3.2 years**.

**Required actions before Wave 1**:
1. **Validate time-saved assumptions** [A26]: Run time-motion study on front-desk staff to confirm 3–8 min saved per case. If actual time saved is 50% higher (4.5-12 min), payback drops to ~1.8 years.
2. **Validate onboarding reduction** [Q15]: Confirm new staff can reach proficiency in 6-8 weeks (vs. 16 weeks) with agent-encoded tribal knowledge. Track onboarding metrics in pilot.
3. **Quantify patient churn prevention** [Q20]: Track patient retention after PA cancellations and billing errors. If churn rate is higher than 10% assumption, patient experience value increases.
4. **Consider phased Wave 1**: Deploy JtD 1.1 + 2.3 only (5-month build, $400k cost, $125k/year saving, 3.2 year payback) → validate → expand to JtD 4.2 if economics improve

**Critical Blockers Identified** [Discovery Q12, Q13]:
1. **HIPAA/malpractice approval NOT obtained** — Must validate before Wave 1 kickoff (2-4 weeks)
2. **BAA execution requires 2-3 months** — Start BAA process NOW in parallel with Wave 1 design

**Note**: These are revised calculations incorporating Discovery findings [Q15, Q20]. **Do not proceed to Wave 1 until economic gate is validated with actual data AND compliance blockers are resolved.**

---

**Document cross-references**:
- **Cognitive Load Map**: `scenario5-cognitive-load-map.md` — JtD decomposition, process topology
- **Delegation Qualification**: `scenario5-delegation-qualification.md` — Delegation archetype assignments, feasibility scoring
- **Assumptions**: `scenario5-assumptions.md` — All assumption IDs (A01–A26)
- **Discovery Questions**: `scenario5-discovery-questions.md` — Coach elicitation priorities (Q1, Q4, Q7, Q12 are Wave 1 gates)
