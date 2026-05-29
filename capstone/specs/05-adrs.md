# Architecture Decision Records
## Greenfield Health Systems — AI Claims Processing Transformation

**Project:** Greenfield Health Systems — AI Claims Processing Transformation  
**Prepared by:** FDE Engagement Lead  
**Date:** 2026-05-20  
**Input:** `specs/03-delegation-matrix.md` (Delegation Qualification and Suitability Matrix)  
**Status:** Active — delegation decisions contingent on Phase 1 validation gates

---

## Table of Contents

1. [ADR-1: Claim Intake and Format Validation](#adr-1--claim-intake-and-format-validation)
2. [ADR-2: Member and Provider Eligibility Verification](#adr-2--member-and-provider-eligibility-verification)
3. [ADR-3: Coding and Compliance Validation](#adr-3--coding-and-compliance-validation)
4. [ADR-4: Clinical Content Triage](#adr-4--clinical-content-triage)
5. [ADR-5: Fast Path Administrative Adjudication](#adr-5--fast-path-administrative-adjudication)
6. [ADR-6: Clinical Pre-Screening and Summary Packaging](#adr-6--clinical-pre-screening-and-summary-packaging)
7. [ADR-7: Physician Clinical Review](#adr-7--physician-clinical-review)
8. [ADR-8: Payment Determination and EOB Generation](#adr-8--payment-determination-and-eob-generation)
9. [ADR-9: Denial Communication and Appeal Management](#adr-9--denial-communication-and-appeal-management)
10. [Assumptions Referenced](#assumptions-referenced)

---

### ADR-1 — Claim Intake and Format Validation

**Suitability:** 4H / 3M — no L dimensions

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| Input Structure | M | EDI 837P/I are structured and machine-parsable. Eight additional channels require varying extraction: FHIR R4 (structured JSON; member_id, member_name, prior_auth_required typically absent → HUMAN_REQUIRED in practice; member_dob/plan_id/billing fields deferred to ADR-2); portal JSON (structured; required fields typically high-confidence → AUTO_COMPLETE; plan_id/provider fields deferred downstream); CMS-1500 PDF/OCR and fax PDF (IDP OCR with confidence scoring); email (RFC 5322 headers + IDP body NLP; payer_id/plan_id deferred to ADR-2; confidence-based); fax-as-email (IDP body NLP; payer_id/plan_id deferred; confidence-based); exception notes (annotation routing — not claim submissions). Channels range from fully deterministic to confidence-scored — mixed [A14] |
| Decision Determinism | H | Format validation is rule-bound: required fields either present or not |
| Tool Coverage | M | EDI 837P/I parser available. Three additional components are Wave 1 build items: (1) IDP pipeline for CMS-1500 PDF/OCR, fax PDF, email, and fax-as-email extraction (~$35K); (2) FHIR R4 dedicated parser; (3) RFC 5322 header parser (low complexity). CMS write API still depends on IT discovery [A12] |
| Context Complexity | H | Stateless format checks require no institutional knowledge |
| Exception Rate | M | Format errors predictable but non-EDI volume creates variability [A7] |
| Latency Constraint | H | Batch acceptable — claims enter queue |
| Risk/Compliance | H | Format errors result in pend, not denial; low patient risk; reversible |

**Archetype:** Agent-led + Human Oversight

**Rationale:** EDI 837P and 837I claims can be fully agent-handled end-to-end through intake, deterministic parsing, and queue assignment. Non-EDI claims (~30% of daily volume [A7]) span eight distinct channels, each with a different extraction profile and HUMAN_REQUIRED rate. HUMAN_REQUIRED is set when any *required* field is absent or below confidence threshold (0.85); optional fields deferred to downstream ADRs do not trigger HUMAN_REQUIRED:

- **FHIR R4**: dedicated parser; confidence-based routing. Required fields member_id (reference URI), member_name, and prior_auth_required are typically absent → HUMAN_REQUIRED in practice. member_dob, billing_provider_tax_id, and plan_id are deferred to ADR-2 (optional at intake).
- **Portal JSON**: field mapping transformation; confidence-based routing. Required fields are typically present at high confidence after mapping → AUTO_COMPLETE achievable. plan_id is deferred to ADR-2; rendering vs billing NPI are deferred to ADR-2+.
- **CMS-1500 PDF and pre-OCR'd text**: IDP pipeline with OCR; HUMAN_REQUIRED when any required field confidence falls below 0.85 (0.80 effective threshold for pre-OCR'd text).
- **Email (.eml)**: RFC 5322 headers provide high-confidence NPI and Tax ID anchors; IDP body NLP for remaining fields; confidence-based routing. payer_id and plan_id are deferred to ADR-2 (optional); HUMAN_REQUIRED only if required fields fall below threshold.
- **Fax PDF**: IDP OCR; fax watermark artifacts reduce confidence on overlapping fields; HUMAN_REQUIRED when required field confidence falls below threshold.
- **Fax-as-email**: IDP body NLP (no header anchors); confidence-based routing; payer_id/plan_id deferred to ADR-2; HUMAN_REQUIRED only if required fields fall below threshold.
- **Exception notes**: not claim submissions — agent extracts claim_id if present and routes as an annotation (ANNOTATE_CLAIM) to the existing CMS claim record; no new NormalizedClaimRecord is created.

The human oversight function covers the exception queue for cases the agent cannot parse or complete.

**Trade-off:** Building the full IDP pipeline (CMS-1500 PDF, fax, email, fax-as-email, OCR-text), the FHIR R4 parser, and the RFC 5322 header parser in Phase 1 adds significant scope (~$35K Wave 1 IDP estimate) but eliminates BP-2 (the manual re-key bottleneck) across all non-EDI channels. Deferring these to Phase 2 preserves Phase 1 budget but leaves ~30% of daily volume on manual intake. With field deferral (plan_id, payer_id, and provider identity fields deferred to downstream ADRs that own them), all channels can achieve AUTO_COMPLETE when their extracted required fields pass confidence thresholds — including email, fax-as-email, and portal JSON that previously generated mandatory human review. Recommendation: fund the IDP pipeline and FHIR R4 parser in Phase 1 alongside shadow mode; the hidden cost of manual re-key [A14] makes this economically justified. Exception note annotation routing is low complexity and should be included in Wave 1 scope.

**Dependencies:** [A12] CMS API for queue write and annotation write (exception notes); [A14] IDP pipeline scope (Wave 1 build); [A7] non-EDI volume confirmation and channel distribution; FHIR R4 parser (Wave 1 build); RFC 5322 header parser (Wave 1, low complexity).

---

### ADR-2 — Member and Provider Eligibility Verification

**Suitability:** 3H / 2M / 1L — tool coverage is the binding constraint

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| Input Structure | M | Member and provider IDs are structured; benefit plan details may require multi-system reconciliation |
| Decision Determinism | H | Coverage rules are binary and documented: active on date of service, provider in-network |
| Tool Coverage | L | No unified eligibility API confirmed [A12]; multiple disconnected systems require manual cross-lookup today |
| Context Complexity | M | Retroactive enrollment changes, coordination of benefits, and renewal gaps add complexity |
| Exception Rate | M | Exceptions are frequent (retroactive changes, COB) but patterns are known and rule-resolvable |
| Latency Constraint | H | Batch acceptable |
| Risk/Compliance | H | Eligibility denials are reversible through correction; low patient safety risk at this stage |

**Archetype:** Agent-led + Human Oversight (conditional on [A12])

**Rationale:** The decision logic for eligibility is straightforward and rule-bound — high delegation suitability on 5 of 7 dimensions. The single binding constraint is tool coverage: if the agent cannot programmatically query the eligibility database, provider directory, and group contract system, it cannot replace the manual multi-window reconciliation that currently consumes processor time. Until [A12] is confirmed and system APIs are mapped, the fallback archetype is Human-led + Automation Support (agent formats the lookup query; human executes it and enters the result).

**Trade-off:** Delaying eligibility automation until a unified API is built may push the most common integration work into Phase 2 or Phase 3, reducing Fast Path throughput gains in Phase 1. If eligibility lookup remains manual, cycle time benefit on the Fast Path is partially offset. Prioritizing the eligibility API in the IT discovery sprint is the risk mitigation.

**Dependencies:** [A12] CMS and eligibility system APIs; IT discovery sprint (Week 1).

---

### ADR-3 — Coding and Compliance Validation

**Suitability:** 4H / 2M — strong candidate for delegation

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| Input Structure | H | ICD-10, CPT, HCPCS codes are structured; NCCI bundling rules are documented |
| Decision Determinism | H | Code validation is deterministic lookup; bundling rules are rule-bound |
| Tool Coverage | H | ICD-10/HCPCS reference databases and NCCI edits engines are commercially available as APIs |
| Context Complexity | M | Procedure-diagnosis plausibility (MT-3.4) requires clinical context; most tasks do not |
| Exception Rate | M | Coding anomalies are common but pattern-predictable |
| Latency Constraint | H | Batch acceptable |
| Risk/Compliance | M | Coding errors caught here result in correction requests, not final denials; reversible |

**Archetype:** Fully Agentic (with human exception queue for plausibility edge cases)

**Rationale:** Coding validation is the strongest Fully Agentic candidate in the workflow: all inputs are structured, rules are deterministic, tools are available, and exceptions are predictable. The agent applies NCCI bundling rules, validates code-set membership, and flags anomalies for correction — all tasks that current senior processors execute from memory using the same rule sets.

**Anti-pattern check:** ICD-10 and CPT validation (MT-3.1, MT-3.2) and NCCI bundling (MT-3.3) are deterministic lookups. These should be implemented as a rules engine or rules-API integration, not an LLM. The LLM agent's contribution is limited to MT-3.4 (procedure-diagnosis plausibility), where natural-language clinical context is required to assess whether the procedure is plausible given the stated diagnosis.

**Trade-off:** The risk of over-engineering: do not use an LLM to validate ICD-10 codes against a reference table. Use the reference table directly. The agent wraps the rules engine and applies LLM reasoning only where the rules are insufficient — plausibility edge cases estimated at 10–15% of coding tasks.

**Dependencies:** NCCI edits engine API access; ICD-10/HCPCS reference API subscription.

---

### ADR-4 — Clinical Content Triage

**Suitability:** 4L / 1M / 1H — lowest suitability score in the workflow

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| Input Structure | L | Claim content is unstructured; clinical indicators are embedded in diagnosis codes, procedure codes, and documentation |
| Decision Determinism | L | No formal criteria [A15]; routing driven by processor experience and informal heuristics today |
| Tool Coverage | L | No clinical criteria decision support tool exists; no documented policy to encode |
| Context Complexity | L | Contextual clinical interpretation required; tacit knowledge about what constitutes "clinical content" is currently undocumented |
| Exception Rate | L | Frequent errors: inconsistent routing is the primary driver of the 41% denial overturn rate |
| Latency Constraint | H | Batch acceptable |
| Risk/Compliance | L | Patient safety gate: a false negative routes a clinically complex claim to Fast Path without physician review [A6] |

**Archetype:** Agent-led + Human Oversight (TARGET — Phase 2 and later)  
**Current state: Human Only — delegation blocked until Phase 1 gate is passed**

**Rationale:** On raw suitability scores, ADR-4 would be assigned Human Only: three of the four most critical dimensions (decision determinism, context complexity, risk/compliance) are Low. The entire dual-path architecture — and the CFO's headcount reduction model — depends on overriding this default. The resolution is not to ignore the analysis but to honor it with a hard gate: delegation cannot proceed until Phase 1 shadow mode demonstrates a clinical flagging false-negative rate below 2% [A6].

The Phase 1 gate transforms this from a suitability problem into a validation problem. The agent is not deployed in clinical triage because the analysis says it is ready; it is deployed because Phase 1 produced labeled data, defined formal criteria [A15], and measured accuracy against a standard [A6]. This sequencing is the architecture's central safety design.

**Trade-off:** If Phase 1 cannot clear the 2% false-negative gate — because criteria remain ambiguous, training data is insufficient, or the clinical complexity distribution is wider than expected — the entire Fast Path architecture is blocked. The financial case (CFO's 13 FTE reduction) depends on this single task being delegatable. There is no fallback that preserves the financial model if ADR-4 cannot be delegated. The project's risk is concentrated here.

**Conditions for delegation:**
1. Formal clinical content criteria defined (with Dr. Webb) — must precede Phase 1
2. Phase 1 shadow mode produces ≥2,000 labeled examples across the clinical/admin boundary
3. False-negative rate < 2% sustained over 60 days of shadow evaluation [A6]
4. Ongoing: monthly random audit of Fast Path approvals reviewed by clinical staff

**Dependencies:** [A15] criteria definition (Week 1 blocker); [A6] Phase 1 gate; U8 (clinical content definition).

---

### ADR-5 — Fast Path Administrative Adjudication

**Suitability:** 4H / 2M — strong agent candidate

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| Input Structure | H | Validated, structured claim data post-coding and eligibility checks |
| Decision Determinism | H | Coverage rules and payment policies are documented and rule-bound |
| Tool Coverage | M | Rules engine assumed but not confirmed in machine-readable form [A18]; fee schedule API access assumed with CMS |
| Context Complexity | H | No institutional tacit knowledge required; pure rule application against documented coverage criteria |
| Exception Rate | M | Edge cases pend for additional information; patterns predictable |
| Latency Constraint | H | Batch acceptable |
| Risk/Compliance | M | Reversible via appeals; [A11] legal uncertainty on AI-generated denials is the primary risk dimension |

**Archetype:** Agent-led + Human Oversight  
Split by action type: **Approvals → Fully Agentic; Denials → Agent-led + Human Oversight** until [A11] is resolved

**Rationale:** The Fast Path is the primary throughput engine of the architecture: 65% of daily claims [A2] adjudicated end-to-end by the agent. For approvals, the risk/compliance dimension shifts to Medium — a correct approval that passes all eligibility, coding, and coverage rule checks carries minimal legal exposure. For denials, [A11] (legal permissibility of AI-generated denials without physician sign-off) remains unresolved and represents a jurisdiction-specific regulatory risk. Until legal counsel confirms AI denials are permissible in Greenfield's operating states, Fast Path denials should be queued for human sign-off.

**Trade-off:** Splitting denials to a human review queue reduces the administrative headcount savings — denied claims (~15–20% of Fast Path volume estimated) do not fully exit the human workflow. This is the conservative approach. If [A11] is confirmed, the full Fast Path volume can be agent-adjudicated, restoring the headcount model. The CFO should be aware that the 13 FTE reduction target is conditional on [A11] resolution.

**Dependencies:** [A18] coverage rules engine format; [A11] legal permissibility; [A12] CMS write API for adjudication records.

---

### ADR-6 — Clinical Pre-Screening and Summary Packaging

**Suitability:** 2H / 4M / 1L — moderate suitability; created by the architecture

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| Input Structure | L | Clinical documentation is unstructured (notes, imaging reports, prior auth records) |
| Decision Determinism | M | Extraction criteria can be defined with Dr. Webb's input; not judgment-dependent once criteria are set |
| Tool Coverage | M | CMS access available; dedicated clinical extraction pipeline must be built [A20] |
| Context Complexity | M | Relevance criteria are codifiable; clinical domain knowledge needed to define them initially |
| Exception Rate | M | Complex cases may have atypical documentation structures |
| Latency Constraint | H | Batch acceptable; feeds physician review queue asynchronously |
| Risk/Compliance | M | Physician provides oversight — summary quality affects decision quality; throughput monitoring is the quality gate [A5] |

**Archetype:** Agent-led + Human Oversight

**Rationale:** ADR-6 does not currently exist as a structured process. It is created by the agentic architecture. This is the highest-value new capability in the system: the pre-screened clinical summary package is what enables Dr. Webb's team to review 20 claims/hour (up from 5–8/hour today [A5]), generating the throughput gain that makes the Clinical Path viable. The physician's review of the summary is the human oversight mechanism — the physician corrects errors in the summary implicitly by making an independent clinical determination.

The agent's task in ADR-6 is extraction and packaging, not clinical judgment: identify which documentation is clinically relevant, extract it, attach applicable coverage policy references, and present it in a structured physician-ready format. With well-defined extraction criteria (a prerequisite shared with ADR-4), this is a tractable LLM task despite unstructured input.

**Trade-off:** Summary quality is not directly measurable by the agent — only the physician throughput metric measures it indirectly. If physicians must verify summary completeness before using it (adding time rather than saving it), the throughput gain disappears. The physician review portal must be designed to display summaries efficiently [A20], and the first 60 days of Clinical Path operation should include structured quality feedback from physicians to the summary generation team.

**Dependencies:** [A15] clinical content criteria (shared with ADR-4); [A5] physician throughput baseline; [A20] physician review portal capability.

---

### ADR-7 — Physician Clinical Review

**Suitability:** 3L / 2M / 1H — Human Only on suitability grounds; CMO mandate confirms

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| Input Structure | M | Structured summary from ADR-6 in target state |
| Decision Determinism | L | Medical necessity judgment requires clinical training, contextual reasoning, and professional accountability |
| Tool Coverage | M | Physician review portal and clinical policy database available |
| Context Complexity | L | Requires clinical expertise, patient context, and awareness of evolving clinical practice |
| Exception Rate | L | Clinical edge cases are frequent by definition; specialist consultation, additional information requests are normal |
| Latency Constraint | H | Batch acceptable within 6–7 day SLA target |
| Risk/Compliance | L | High patient care consequence; CMO non-negotiable; irreversible if clinical denial affects access to care |

**Archetype:** Human Only

**Rationale:** This archetype requires no trade-off analysis. Decision Determinism and Risk/Compliance are both Low — the two dimensions that most strongly contraindicate agent delegation. The CMO's non-negotiable position (from the stakeholder alignment memo) is fully consistent with the suitability analysis. Physician clinical review is not a target for agent delegation; it is the oversight layer that makes delegation of ADR-4 permissible.

The agent's role in this ADR is strictly support: ADR-6 produces the pre-screened summary that is the physician's primary input. The only lever for productivity improvement is summary quality, not autonomy expansion.

**Trade-off:** There is no trade-off to analyze on delegation. The relevant decision is scoping: ensuring ADR-6 quality is maintained, that the physician portal supports efficient review [A20], and that physician headcount (minimum 4 FTEs [A10]) is staffed before Clinical Path goes live.

**Dependencies:** [A5] throughput target; [A10] minimum physician headcount; [A20] portal UI capability; ADR-6 quality.

---

### ADR-8 — Payment Determination and EOB Generation

**Suitability:** 5H / 1M — highest suitability score in the workflow

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| Input Structure | H | Structured adjudication decision + structured fee schedule + structured member cost-sharing data |
| Decision Determinism | H | Fee schedule application and cost-sharing calculation are deterministic arithmetic |
| Tool Coverage | H | Fee schedule database, payment engine, and EOB generation system exist and are API-accessible (assumed [A12]) |
| Context Complexity | H | No institutional knowledge required; pure computation against documented schedules |
| Exception Rate | H | Coordination of benefits adds complexity but rules are defined; true exceptions are rare |
| Latency Constraint | H | Batch acceptable; not time-critical once adjudication decision is made |
| Risk/Compliance | M | Financial accuracy is important; errors are correctable through adjustment claims |

**Archetype:** Fully Agentic

**Rationale:** Payment determination is the most cleanly delegatable process in the workflow. All inputs are structured, all logic is deterministic, tools exist, and exceptions are rare and rule-governed. The agent's role is to receive the adjudication decision and trigger the existing payment engine — not to replicate payment calculation logic.

**Anti-pattern check:** This ADR is a strong anti-pattern candidate. The payment engine likely already computes fee schedule application, deductibles, and COB correctly. Building an LLM agent to perform arithmetic that a deterministic system already performs is engineering overhead with no benefit. The correct architecture is: agent orchestrates the payment workflow (passes adjudication output to payment engine, receives payment confirmation, triggers EOB generation) rather than performing payment calculation itself.

**Trade-off:** The only risk is integration scope. If the payment engine does not expose an API [A12], the agent cannot trigger it programmatically and a batch file-based integration becomes necessary. This is an IT discovery item, not a delegation question.

**Dependencies:** [A12] payment engine API; fee schedule database access.

---

### ADR-9 — Denial Communication and Appeal Management

**Suitability:** 3L / 3M — mixed; split archetype across sub-tasks

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| Input Structure | M | Claim data is structured; appeal documentation (letters, clinical notes) is unstructured |
| Decision Determinism | L | Appeal review requires clinical and policy judgment; denial outcomes are defensible only with accurate policy citation |
| Tool Coverage | M | CMS, denial templates, and appeals tracking system available; no automated policy-to-rationale mapping exists [A16] |
| Context Complexity | M | Initial denial letter is rule-based; complex appeals require case-by-case reasoning |
| Exception Rate | L | 41% overturn rate reflects frequent, significant edge cases |
| Latency Constraint | M | Regulatory appeal deadlines create urgency [A19]; not real-time but not batch-only |
| Risk/Compliance | L | Legally defensible documentation required; appeal deadline breaches carry regulatory consequences; denials affect patient access |

**Archetype:** Human-led + Agent Support (overall)  
Sub-task split:
- MT-9.1 Denial letter generation, MT-9.2 Appeal rights notice, MT-9.3 Appeal intake/logging → **Agent-led + Human Oversight**
- MT-9.4 Appeal re-review, MT-9.5 Escalation → **Human-led + Agent Support**

**Rationale:** This ADR has the widest internal variance of any workstream. The appeal logging and initial denial communication are structured, rule-bound, and suited for agent execution. The appeal re-review and escalation are judgment-dependent and legally consequential — they require the same kind of oversight the physician provides in ADR-7.

The highest-value agent contribution in this ADR is denial letter generation with accurate policy citation. The 41% overturn rate is driven primarily by indefensible denial language [A16] — not incorrect outcomes. An agent that automatically links the denial rationale to the specific policy provision violated would reduce the overturn rate materially. This is flagged as a Phase 3 target because it depends on the coverage rules engine [A18] being available to the agent.

**Trade-off:** AI-generated denial letters carry a new risk: if the agent systematically cites the wrong policy provision at scale, it creates a defensibility liability rather than resolving one. Phase 2 should keep human sign-off on AI-generated denial letters before they are issued. Phase 3 can move to autonomous generation only after a 90-day sample review confirms policy citation accuracy is above the human baseline.

**Dependencies:** [A16] denial letter format baseline; [A18] coverage rules engine access; [A19] appeal deadline tracking; [A11] AI denial permissibility.

---

## Assumptions Referenced

| ID | Description | Confidence | Relevant ADRs |
|----|-------------|:----------:|---------------|
| A2 | 35% clinical / 65% admin split | Low (50%) | ADR-4, ADR-5, ADR-6 routing volumes |
| A5 | Physician throughput 5–8/hr current; 20/hr with pre-screening | Low (45%) | ADR-6, ADR-7 |
| A6 | <2% clinical flagging false-negative achievable | Medium (60%) | ADR-4 delegation gate |
| A7 | 70% EDI / 30% non-EDI format split | Low (40%) | ADR-1 |
| A10 | Minimum 4 physicians for Clinical Path | Medium (60%) | ADR-7 staffing |
| A11 | AI Fast Path denials legally permissible | Low (45%) | ADR-5, ADR-9 |
| A12 | CMS has usable API for integration | Low (40%) | ADR-1, ADR-2, ADR-5, ADR-8 |
| A14 | ~80% of non-EDI claims require manual re-key | Low (40%) | ADR-1 |
| A15 | Clinical flagging criteria are informal/undocumented | Medium (60%) | ADR-4 (blocking), ADR-6 |
| A16 | Denial letters use manual template fill-in | Medium (55%) | ADR-9 |
| A17 | Processing queue not SLA-prioritized | Medium (55%) | ADR-1 queue design |
| **A18** | Coverage rules exist in machine-readable form | Low (45%) | ADR-5, ADR-9 |
| **A19** | Appeal regulatory deadlines are tracked | Low (40%) | ADR-9 |
| **A20** | Physician review portal supports structured summary display | Low (45%) | ADR-6, ADR-7 |

Full assumption definitions: `specs/assumptions.md`. Assumptions A18–A20 are defined in full there.
