# Agentic Solution Architecture — Westbridge Family Medicine Patient Intake

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Delegation Qualification: WS1 — Insurance Verification](#ws1--insurance-verification)
3. [Delegation Qualification: WS2 — Prior Authorization](#ws2--prior-authorization)
4. [Delegation Qualification: WS3 — Pre-visit Questionnaire & Triage](#ws3--pre-visit-questionnaire--triage)
5. [Delegation Qualification: WS4 — Medication Reconciliation & Allergy Review](#ws4--medication-reconciliation--allergy-review)
6. [Workstream Archetype Summary](#workstream-archetype-summary)

---

## Executive Summary

This document applies Phase 3 Delegation Qualification to the four patient-intake workstreams at Westbridge Family Medicine. For each workstream, every micro-task is scored across seven delegation suitability dimensions and assigned to one of five archetypes, from **Human Only** to **Fully Agentic**. Rationale and trade-off notes are provided for each assignment.

**Top-line findings:**

- **WS1 (Insurance Verification)** is the most automation-ready workstream. The standard path (data retrieval, eligibility query, EHR documentation) can operate **Agent-led with Human Oversight**. The exception path — manual patient or insurer contact — remains **Human Only**.

- **WS2 (Prior Authorization)** is the highest-value target but requires a prerequisite: codifying Dana's insurer-specific behavior patterns [A011] into a machine-readable knowledge base [A019] before the SLA planning and denial interpretation tasks become agent-supportable. Without that step, tasks 2.4–2.6 remain **Human Only**. The check-in gate (2.8) is immediately automatable and addresses the single most costly failure mode in the practice.

- **WS3 (Triage)** is sharply constrained by hard constraints HC1 (no clinical judgment) and HC2 (escalation path preserved). Collection and routing are agent-supportable; urgency classification and red-flag escalation are permanently **Human Only** under current constraints.

- **WS4 (Medication Reconciliation)** splits cleanly: data retrieval and structured comparison are **Fully Agentic**; OTC/specialist medication gap detection [A005] remains **Human-led + Agent Support** due to the known systematic data quality gap.

**Prerequisite before any agent is built:** HIPAA Business Associate Agreement (BAA) for any AI system processing PHI [A015]. All archetype assignments assume BAA is in place and all API write operations are covered by it [A020].

---

## Delegation Qualification: WS1 — Insurance Verification

### Scoring Key

**H** = High delegation suitability | **M** = Medium | **L** = Low

Dimension orientation (Phase 3):
- **Input Structure**: H = structured/machine-readable; L = unstructured/ambiguous
- **Decision Determinism**: H = rule-based, predictable; L = judgment-dependent
- **Tool Coverage**: H = full API available; L = manual only
- **Context Complexity**: H = state can be made explicit; L = requires institutional knowledge
- **Exception Rate**: H = rare, predictable; L = frequent, unpredictable
- **Latency Constraint**: H = batch/async acceptable; L = real-time/sub-second required
- **Risk/Compliance**: H = reversible, low consequence; L = irreversible, regulated, high-consequence

---

### Delegation Suitability Matrix — WS1

| ID | Micro-Task | Input Struct | Decision Determ | Tool Coverage | Context Complex | Exception Rate | Latency | Risk/Compliance | Archetype |
|----|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| 1.1 | Pull patient schedule from athenahealth | H | H | H | H | H | H | M | **Fully Agentic** (RPA-eligible) |
| 1.2 | Check verification date vs. staleness threshold [A004] | H | H | H | H | M | M | M | **Fully Agentic** (flag only; no write) |
| 1.3 | Run Availity eligibility query [A013] | H | H | H | H | M | M | M | **Fully Agentic** (API call, structured response) |
| 1.4 | Interpret eligibility result: active / lapsed / plan type / self-pay | M | M | H | M | M | M | L | **Agent-led + Human Oversight** |
| 1.5 | Identify self-pay and Medicaid managed-care edge cases [A001] | M | M | M | M | L | M | L | **Human-led + Agent Support** |
| 1.6 | Contact patient or insurer to resolve failed verification | L | L | M | L | L | L | M | **Human Only** |
| 1.7 | Update EHR with verification result and staleness flag [A020] | H | H | H | H | H | M | L | **Agent-led + Human Oversight** |

**Risk/Compliance note on 1.2, 1.3:** Both tasks carry high absolute compliance risk (billing errors if missed), but the agent's action is *flagging and querying*, not deciding. The write happens only at 1.7 after result confirmation. Risk L in these rows reflects the bounded, reversible nature of the agent's action.

---

### Workstream-Level Archetype: Agent-led + Human Oversight

**Rationale:** Tasks 1.1–1.4 form a deterministic pipeline with full API coverage (athenahealth + Availity [A013]). The agent executes the standard path end-to-end and writes only confirmed results to the EHR [A020]. Human intervention is reserved for the ~30% exception rate [A001] and all manual resolution.

**Trade-off analysis:**

| Trade-off | Notes |
|-----------|-------|
| Gain | Eliminates 3–4 min/patient of routine retrieval + query work; forces the staleness-refresh policy [A004] to be encoded as a rule, which is the fix that prevents billing errors like Artefact 5.3 |
| Risk | Agent writes to EHR (1.7) under PHI constraints; requires BAA [A015, A020] and audit-log enforcement |
| Anti-pattern check | Tasks 1.1–1.3 are deterministic lookups; a scheduled script or RPA job may be sufficient without full agent overhead. Recommend starting with RPA for these three tasks and reserving agent architecture for 1.4 (interpretation) and the exception-detection path |
| Dependency | Staleness threshold [A004] must be defined before coding rule 1.2; current policy gap is the blocker |

---

## Delegation Qualification: WS2 — Prior Authorization

### Delegation Suitability Matrix — WS2

| ID | Micro-Task | Input Struct | Decision Determ | Tool Coverage | Context Complex | Exception Rate | Latency | Risk/Compliance | Archetype |
|----|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| 2.1 | Identify procedures and referrals requiring PA | H | M | H | M | M | H | L | **Agent-led + Human Oversight** |
| 2.2 | Check PA status in athenahealth | H | H | H | H | H | H | M | **Fully Agentic** |
| 2.3 | Submit PA request via portal or fax [A017, A019, A021] | M | M | M | M | M | H | L | **Human-led + Agent Support** → upgrades to Agent-led once portal API confirmed [A021] |
| 2.4 | Apply insurer-specific SLA patterns to set chase date [A008, A011, A019] | L | L | L | L | L | H | L | **Human-led + Agent Support** (requires knowledge codification first; currently Human Only) |
| 2.5 | Chase pending PA via insurer phone or portal | L | L | L | L | L | L | M | **Human Only** |
| 2.6 | Interpret denial reason; identify required documentation [A011, A019] | L | L | M | L | L | L | L | **Human-led + Agent Support** (requires knowledge codification first; currently Human Only) |
| 2.7 | Resubmit PA with supplementary documentation | M | M | M | M | M | H | L | **Human-led + Agent Support** |
| 2.8 | Flag any pending PAs at day-of check-in [A012, A020] | H | H | H | H | M | L | M | **Agent-led + Human Oversight** |

---

### Workstream-Level Archetype: Human-led + Agent Support (with phased upgrade path)

**Rationale:** WS2 is split between two structurally different task types:
1. **Data-state tasks** (2.1, 2.2, 2.8): fully API-addressable, deterministic, high suitability — agent-led now.
2. **Tacit-knowledge tasks** (2.4, 2.5, 2.6): depend entirely on Dana's undocumented insurer behavior patterns [A008, A011]. These are **Human Only in current state** and upgrade to **Human-led + Agent Support** only after knowledge codification [A019].

Task 2.8 (check-in gate enforcement) is the single highest-impact automation target in the entire system — it directly prevents the failure mode documented in Artefact 5.2 (patient TJ, visit aborted at exam room). It requires only a PA-status query at check-in time and a deterministic flag; it should be built first, independently of the knowledge codification work.

**Trade-off analysis:**

| Trade-off | Notes |
|-----------|-------|
| Gain | 2.8 alone prevents same-day visit cancellations; 2.1 + 2.2 eliminate routine status-check labor (~2 min/case × 25 cases = ~50 min/day saved) |
| Prerequisite | Insurer pattern knowledge codification [A019] is required before 2.4 and 2.6 can receive agent support. This is a structured elicitation project, not a technical one — it must happen before the agent is built, not alongside it |
| Risk | 2.3 (PA submission) has non-trivial fax dependency [A017]; partial portal API coverage [A021] means fax workflow persists for some insurers — this is a hybrid path requiring human handling for non-portal insurers |
| Fragility | WS2 tacit knowledge is currently single-threaded through Dana [A008]. Codification also reduces operational fragility regardless of agent deployment |
| Anti-pattern check | Task 2.2 (PA status check) is a pure query — a scheduled script is sufficient; full agent overhead not justified for this task alone |

---

## Delegation Qualification: WS3 — Pre-visit Questionnaire & Triage

### Hard Constraints (from scenario)

- **HC1:** No clinical judgment by the agent.
- **HC2:** Any contact with the stated visit reason must preserve a clear human escalation path.

These constraints are binding on tasks 3.3–3.5 and cannot be overridden by technical capability.

---

### Delegation Suitability Matrix — WS3

| ID | Micro-Task | Input Struct | Decision Determ | Tool Coverage | Context Complex | Exception Rate | Latency | Risk/Compliance | Archetype |
|----|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| 3.1 | Route questionnaire: portal or paper [A006] | H | H | M | H | M | M | M | **Agent-led + Human Oversight** (portal patients); **Human Only** for paper-form patients [A006] |
| 3.2 | Chase incomplete/non-returned questionnaires | M | M | M | H | M | M | L | **Agent-led + Human Oversight** (automated reminders; human escalates after N attempts) |
| 3.3 | Parse visit reason from free-text response [A018] | M | M | M | M | M | L | M | **Human-led + Agent Support** |
| 3.4 | Classify visit urgency: routine / urgent / same-day [A009] | L | L | L | L | L | L | L | **Human Only** *(HC1: clinical judgment prohibited)* |
| 3.5 | Detect and escalate clinical red flags to RN/physician | L | L | L | L | M | L | L | **Human Only** *(HC1 + HC2: clinical judgment + mandatory escalation path)* |
| 3.6 | Document triage classification in athenahealth [A020] | H | H | H | H | H | M | L | **Agent-led + Human Oversight** |

---

### Workstream-Level Archetype: Human-led + Agent Support

**Rationale:** WS3 is constrained at its highest-cognitive-load steps by hard constraints HC1 and HC2. The agent's role is bounded to pre-processing and documentation:
- **Before human judgment:** collect (3.1), chase (3.2), and normalize free-text (3.3)
- **After human judgment:** document the human's classification (3.6)

The agent must not score, rank, or suggest urgency classifications — doing so would constitute indirect clinical judgment even if framed as "a recommendation." [A009]

For 3.3 (parse visit reason), the agent can extract structured data (symptom keywords, visit type indicators) and flag ambiguous responses for human review. This reduces cognitive load without substituting judgment.

**Trade-off analysis:**

| Trade-off | Notes |
|-----------|-------|
| Gain | Tasks 3.1 + 3.2 eliminate manual questionnaire routing and follow-up for ~144 portal patients/day [A006]; 3.6 auto-documents once human classification is complete |
| Constraint ceiling | HC1 and HC2 permanently cap delegation for 3.4 and 3.5 regardless of model capability improvement. Any future change to these constraints requires explicit sign-off from Dana and legal/malpractice review [A015] |
| Risk (3.3) | Agent NLP parsing of free-text visit reason carries mis-parse risk. Must surface uncertainty (e.g., confidence score < threshold) to human for review rather than silently defaulting. Requires clear human-review UI |
| Paper gap [A006] | ~20% of patients use paper intake; these bypass all agent routing. This creates a parallel manual path that must be explicitly managed, not left as an implicit exception |
| Anti-pattern check | 3.2 (questionnaire chasing) is a rule-based outreach workflow — a scripted reminder system (not an agent) is likely sufficient for the standard path |

---

## Delegation Qualification: WS4 — Medication Reconciliation & Allergy Review

### Delegation Suitability Matrix — WS4

| ID | Micro-Task | Input Struct | Decision Determ | Tool Coverage | Context Complex | Exception Rate | Latency | Risk/Compliance | Archetype |
|----|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| 4.1 | Pull pharmacy history from DoseSpot | H | H | H | H | H | H | M | **Fully Agentic** |
| 4.2 | Pull current medication list from athenahealth | H | H | H | H | H | H | M | **Fully Agentic** |
| 4.3 | Compare DoseSpot and athenahealth lists; identify deltas | M | M | H | M | M | H | L | **Agent-led + Human Oversight** |
| 4.4 | Review allergy record for new or changed flags | M | M | H | M | M | H | L | **Agent-led + Human Oversight** |
| 4.5 | Detect medications not in DoseSpot: OTC, specialist Rx [A005] | L | L | L | L | L | H | L | **Human-led + Agent Support** |
| 4.6 | Flag discrepancies and allergy changes for physician pre-chart review [A020] | M | M | H | M | M | H | L | **Agent-led + Human Oversight** |
| 4.7 | Document reconciliation status in athenahealth [A020] | H | H | H | H | H | M | L | **Agent-led + Human Oversight** |

**Risk/Compliance note on 4.3–4.7:** All tasks involve PHI and downstream clinical use by the physician. Risk/Compliance scores of L reflect the bounded nature of the agent's action (comparison, flagging, documentation) rather than clinical decision-making. Physician reviews all flags; agent does not resolve discrepancies.

---

### Workstream-Level Archetype: Agent-led + Human Oversight

**Rationale:** WS4 splits at task 4.5. Tasks 4.1–4.4, 4.6–4.7 form a deterministic comparison-and-flag pipeline with full API coverage between DoseSpot and athenahealth [A013]. These tasks are highly suitable for full agent execution with physician review of outputs.

Task 4.5 (OTC and specialist medication gap detection) sits outside this pipeline because DoseSpot's data coverage is structurally incomplete [A005]. There is no API for medications dispensed by a hospital system, given as samples, or purchased OTC. The agent can surface "DoseSpot shows X; check with patient for completeness" — but the actual gap-filling requires a patient conversation at check-in. This is **Human-led + Agent Support**, not a solvable data problem.

**Trade-off analysis:**

| Trade-off | Notes |
|-----------|-------|
| Gain | Eliminates ~3 min/patient of data retrieval + structured comparison work (4.1–4.4) across ~180 patients/day; ensures physician always receives a prepared discrepancy report, not a raw med list |
| Data quality ceiling [A005] | Automating the comparison step does not close the OTC/specialist gap. The agent should make this limitation visible in the output ("reconciliation complete against pharmacy records; OTC and specialist medications not included") rather than presenting output as a complete reconciliation |
| Risk | The agent produces the artifact the physician uses for clinical pre-charting. Output accuracy and completeness labeling are safety-critical. Requires validation against a real patient sample before production deployment |
| Anti-pattern check | Tasks 4.1 + 4.2 are pure data pulls — RPA or scheduled sync is sufficient; agent overhead not justified for retrieval alone |

---

## Workstream Archetype Summary

### Cross-Workstream Matrix

| Workstream | JtD Type | Dominant Archetype | Immediately Automatable | Requires Prerequisite | Permanently Human |
|-----------|----------|-------------------|------------------------|----------------------|-------------------|
| WS1 — Insurance Verification | Execution + Exception-Handling | Agent-led + Human Oversight | 1.1, 1.2, 1.3, 1.4, 1.7 | 1.2 (staleness policy [A004]); 1.7 (BAA [A020]) | 1.6 (patient/insurer contact) |
| WS2 — Prior Authorization | Decision-making + Synthesis + Exception-Handling | Human-led + Agent Support | 2.2, 2.8 | 2.3 (portal API [A021]); 2.4, 2.6 (knowledge codification [A019]) | 2.5 (phone chase) |
| WS3 — Questionnaire & Triage | Synthesis + Decision-making + Communication | Human-led + Agent Support | 3.1 (portal), 3.2, 3.6 | 3.3 (NLP parse review UI) | 3.4, 3.5 (HC1 + HC2) |
| WS4 — Medication Reconciliation | Execution + Synthesis + Exception-Handling | Agent-led + Human Oversight | 4.1, 4.2, 4.3, 4.4, 4.6, 4.7 | BAA [A020] | 4.5 (OTC gap detection [A005]) |

---

### Recommended Build Sequence

| Wave | Tasks | Rationale |
|------|-------|-----------|
| **Wave 1 — Immediate** | 2.8 (check-in PA gate), 2.2 (PA status check) | Addresses the highest-visible failure mode (Artefact 5.2); deterministic, no prerequisites beyond BAA |
| **Wave 2 — Near-term** | 1.1–1.4, 1.7 (insurance verification standard path), 4.1–4.4, 4.6, 4.7 (med reconciliation pipeline) | Full API coverage exists; prerequisites are BAA and staleness policy rule [A004, A020] |
| **Wave 3 — After prerequisites** | 2.3, 2.4, 2.6, 2.7 (PA submission and chase support), 3.1, 3.2, 3.3, 3.6 (questionnaire pipeline) | Requires knowledge codification [A019] and portal API confirmation [A021] for WS2; paper-form handling [A006] decision for WS3 |
| **Permanently out of scope** | 1.6, 2.5, 3.4, 3.5, 4.5 (partial) | Structural constraints: unstructured human communication, phone-only channels, hard constraints HC1/HC2, data quality ceiling [A005] |

---

*All assumption references [A001]–[A021] are documented in `specs/assumptions.md`.*
