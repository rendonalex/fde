# Problem Framing and Success Metrics
## Helix Therapeutics — Agentic Adverse Event Triage System

**Document Version**: 1.0  
**Date**: 2026-06-01  
**Engagement Owner**: FDE Lead  
**Executive Sponsor**: Dr. Maeve Carmichael, Chief Medical Officer

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
   - [Current State](#current-state)
   - [Stakeholder Perspectives](#stakeholder-perspectives)
   - [The Actual Problem](#the-actual-problem)
   - [Constraints](#constraints)
3. [Success Metrics](#success-metrics)
4. [Critical Unknowns](#critical-unknowns)
5. [Assumptions Register Reference](#assumptions-register-reference)

---

## Executive Summary

Helix Therapeutics faces a pharmacovigilance capacity and compliance crisis driven by heterogeneous adverse event intake. With 6,000 annual AE reports across three marketed products, case processing specialists require 75 minutes per case for intake triage — primarily spent on "boring synthesis" (data extraction, classification, expectedness lookup) rather than medical judgment. This creates two acute problems:

1. **Regulatory compliance risk**: 8% of serious-unexpected AEs miss the 15-day FDA reporting deadline (92% current compliance vs 99.5% target), exposing Helix to enforcement action and Dr. Carmichael to career consequence.

2. **Operational capacity constraint**: Throughput bottleneck forces hiring of additional case processors rather than scaling medical safety officer capacity for higher-value medical assessment work.

The stated request is to "offload administrative load to an agentic workflow." The actual problem is to **decompose cognitive work** in AE triage such that:
- Routine synthesis work (extraction, classification per ICH E2A, expectedness lookup) is fully delegated to AI with HITL validation only when confidence is insufficient
- Medical safety officers spend saved time on medical judgment (causality, reportability edge cases, complex case investigation), not data entry
- Audit trail generation is automated and inspection-ready from day 1

**Target outcome**: Reduce per-case intake-to-triage-complete time from 75 min → ≤20 min, enabling Helix to handle growing AE volume without proportional hiring while reaching 99.5% 15-day clock compliance.

**Budget**: $510K for Wave 1 build + first-year run. Token economics are negligible (~$1,620/year per A5); value is in capacity expansion.

---

## Problem Statement

### Current State

Helix Therapeutics operates a pharmacovigilance program for three marketed products (Solivian, Tezarimab, Phaedora) with the following operational baseline:

| Metric | Value | Source |
|--------|-------|--------|
| Annual AE reports | 6,000 | Scenario |
| Case processing time per report | 75 minutes | Scenario (Dr. Carmichael) |
| Total annual case processing hours | 7,500 hours | Calculated: 6,000 × 75 min ÷ 60 |
| FTE equivalent (2,080 hrs/year) | 3.6 FTE | Calculated: 7,500 ÷ 2,080 |
| 15-day clock compliance (serious-unexpected AEs) | 92% | Scenario (Maeve's metrics table) |
| Audit trail completeness (machine-generated) | 0% | Scenario: "manual today" |
| AE report sources | Heterogeneous | HCP (PDF/fax/email), patient (web/phone), social media, trial sites, literature |

**Time breakdown per case** (A1 — see assumptions.md):
- **35 min (47%)** — Data extraction and normalization from heterogeneous formats
- **15 min (20%)** — Seriousness classification per ICH E2A criteria
- **10 min (13%)** — Expectedness assessment against product reference safety information (RSI)
- **10 min (13%)** — Reportability determination (15-day expedited vs periodic vs non-reportable)
- **5 min (7%)** — Documentation and audit trail creation

**The synthesis bottleneck**: 60 of 75 minutes (80%) is spent on rule-based cognitive work (extraction, classification, lookup) that does not require medical judgment. The remaining 15 minutes includes the reportability decision, which does require medical safety officer sign-off per stakeholder constraints.

### Stakeholder Perspectives

#### From the Reporter/Patient Perspective (Implicit)

Adverse event reporters (HCPs, patients, trial sites) file reports expecting:
- **Acknowledgment** — confirmation Helix received and will process the report
- **Timeliness** — serious AEs escalated to appropriate medical review without delay
- **Follow-up** — if additional information is needed, requests are prompt and clear

Current-state pain points (inferred from 75-min processing time and 8% compliance failures per A7):
- **Queue delays** — reports sit in intake queue before processing begins, burning 15-day clock time
- **Slow follow-up** — if information is missing, back-and-forth takes days
- **Lack of transparency** — reporters don't know processing status

**What they actually need**: Fast acknowledgment, prioritization of serious cases, and proactive information requests when needed.

#### From the Business/Regulatory Perspective

Dr. Maeve Carmichael (CMO, executive sponsor) states the problem explicitly:

> "Our case processing specialists average 75 minutes per case, and we have a backlog. The 15-day clock starts the moment any Helix employee or contractor receives the report, not when we open it."

This reveals three pain points:

1. **Compliance risk** — 8% of serious-unexpected AEs miss the FDA 15-day deadline (92% vs 99.5% target). FDA enforcement consequences include Warning Letters, Consent Decree (manufacturing restrictions), and reputational damage. For Dr. Carmichael personally, late SAE reporting is a career risk.

2. **Capacity constraint** — Theo Lonergan (Head of Drug Safety Ops): "We are hiring case processors. I'd rather not." Growing AE volume (new marketed products, expanded post-market surveillance, social media monitoring obligations) requires proportional hiring under the current model. This is operationally unsustainable and expensive.

3. **Misallocated cognitive work** — Dr. Anil Iyer (Senior Safety Physician, design partner): "I do not want AI to write my medical assessment. I want AI to do the boring synthesis so I can write the assessment." Medical safety officers are spending 60 of 75 minutes per case on data entry, extraction, and lookup work — not medical judgment. Their expertise is underutilized.

**What they actually need**: 
- Reach 99.5% 15-day compliance through faster intake and automatic prioritization
- Scale AE processing throughput without proportional hiring
- Redirect medical safety officer time from synthesis to medical judgment
- Produce inspection-ready audit trails automatically (per Greta Schäffer and Dr. Mansour requirements)

### The Actual Problem

**Stated request**: "Offload administrative load to an agentic workflow."

**Actual problem**: **Cognitive work decomposition for pharmacovigilance intake triage.**

The current process treats AE case processing as a monolithic 75-minute task performed by case specialists. In reality, it is a **composite cognitive job** with distinct work types:

| Work Type | Time | Cognitive Zone | Delegation Suitability |
|-----------|------|----------------|----------------------|
| Extract structured data from heterogeneous formats | 35 min | Routine (rule-based, low variance) | **Full delegation** — AI with HITL only when confidence < threshold |
| Classify seriousness per ICH E2A | 15 min | Routine (explicit criteria) | **Full delegation** — AI with medical officer review |
| Assess expectedness vs RSI | 10 min | Routine (lookup + matching) | **Full delegation** — AI with medical officer review |
| Determine reportability | 10 min | Judgment (regulatory interpretation + edge cases) | **AI assistance** — AI recommends, safety officer decides |
| Create audit trail | 5 min | Routine (documentation) | **Full delegation** — automated by system |

The actual problem is **not** "we need AI to do everything." It is: **"We need to delegate the 60 minutes of routine synthesis work (extraction, classification, expectedness, documentation) to AI so medical safety officers can focus the remaining 15 minutes on the medical judgment that requires their expertise."**

This is the difference between:
- **Automation** (replace humans) 
- **Augmentation** (redirect human effort from low-value to high-value cognitive work)

Dr. Iyer's requirement — "I do not want AI to write my medical assessment" — is the design constraint. The AI does synthesis; the human does medical judgment.

### Constraints

**Regulatory constraints** (non-negotiable):
- **15-day clock** — Serious-unexpected AEs must be reported to FDA within 15 calendar days from "day zero" (first receipt by any Helix employee/contractor), per 21 CFR 314.80(c)(1)
- **Audit trail** — Every reportability determination must be defensible to FDA inspectors with underlying evidence retrievable on demand (per Greta Schäffer and Dr. Hadi Mansour)
- **Medical safety officer sign-off** — AI does not make reportability decisions; it provides recommendations with reasoning; medical safety officer signs (per Dr. Carmichael scope guardrail)
- **No delegation of reporter communication** — AI does not communicate with reporters, patients, or regulators (per scope guardrail)
- **No black-box AI** — Dr. Mansour (external auditor, former FDA reviewer): "AI in pharmacovigilance is acceptable when it accelerates human safety physicians and is transparent. It is not acceptable when it makes the medical assessment."

**Architectural constraints**:
- **Patient PII handling** — Case identifiers, genetic data, and sensitive information require defensible data handling (encryption, access controls, audit logging). Architectural design decision required.
- **Heterogeneous input formats** — Must handle HCP reports (PDF/fax/email), patient reports (web form JSON, phone transcripts .vtt), social media monitoring (JSON with threads), trial site reports (MedDRA-coded), literature (text). No format standardization is feasible (sources are external).
- **Global reportability variance** — Carolina Núñez-Reyes warns: "What's reportable to FDA in 15 days is not the same as what's reportable to PMDA." System must handle jurisdiction-specific logic or defer global reportability to human judgment.

**Scope constraints** (per Dr. Carmichael):
- **In scope**: Marketed products only (Solivian, Tezarimab, Phaedora)
- **Out of scope**: Medical device complaints, clinical trial AEs for pipeline assets, quality complaints without AE component

**Budget and timeline constraints**:
- **Budget**: $510K for build + first-year run
- **Timeline**: 8-hour design-build-validate cycle (exam context); real-world Wave 1 would be 4-6 weeks
- **Tooling**: Claude Code is the required build tool
- **Curveball**: Scenario includes a design adaptation at 13:30 CET (exam format)

---

## Success Metrics

Success metrics are derived from Dr. Carmichael's framing (scenario metrics table) with quantified baselines, targets, measurement methods, and assumption dependencies.

### Metric 1: Per-Case Processing Time (Intake to Triage Complete)

**Description**: Elapsed time from AE report receipt to completed "AE case package" ready for medical safety officer sign-off.

**Current Baseline**: 75 minutes per case (scenario).

**Target**: ≤20 minutes per case (scenario).

**Measurement Method**:
- Start timestamp: `received_at` (report enters intake queue)
- End timestamp: `triage_complete_at` (AE case package generated with extraction, seriousness classification, expectedness signal, reportability recommendation, audit trail)
- Exclude time spent waiting in queue or waiting for medical safety officer review (measure processing time, not queue time)
- Calculate median and 95th percentile over 30-day rolling window

**Success Criteria**:
- Median processing time ≤20 min
- 95th percentile processing time ≤35 min (allows for complex cases)

**Dependencies**:
- **A1** — Assumes 60 min of the 75-min baseline is synthesis work (extraction + classification + expectedness + documentation) that can be delegated to AI
- **A8** — Assumes IDP pipeline is buildable within scope to handle non-structured formats

**Why This Matters**: This is the **leading indicator** of capacity expansion. If processing time drops from 75 min → 20 min, Helix can process 3.75× more cases with the same FTE capacity, avoiding new hires as AE volume grows.

**Risk if Target Missed**: If processing time is still 50 min, the capacity constraint remains and hiring is unavoidable.

---

### Metric 2: 15-Day Clock Compliance (SAE Reportability Decided + Filed Within 15 Calendar Days)

**Description**: Percentage of serious-unexpected AEs for which reportability determination is completed and FDA submission is filed within 15 calendar days from first receipt.

**Current Baseline**: 92% (scenario).

**Target**: 99.5% (scenario).

**Measurement Method**:
- Denominator: All AEs classified as serious-unexpected (requires 15-day expedited reporting per FDA 21 CFR 314.80)
- Numerator: Count of cases where `reportability_decision_final_at` timestamp ≤ `received_at` + 15 calendar days
- Calculate monthly compliance rate
- Track failures with root cause categorization (intake delay, extraction complexity, reporter follow-up, medical officer review delay)

**Success Criteria**:
- ≥99.5% compliance sustained over 90-day period
- Zero failures due to intake/extraction delays (failures may still occur due to reporter follow-up delays or complex causality assessments, which are out-of-scope for AI delegation)

**Dependencies**:
- **A7** — Assumes 50% of current compliance failures are due to intake queue delays and 30% due to extraction complexity from heterogeneous formats. If these are not the root causes, AI intake acceleration alone won't reach 99.5%.
- **A1** — Assumes 35 min of extraction time is the bottleneck; if extraction is faster but reportability decision takes longer, the 15-day clock still runs.

**Why This Matters**: This is the **lagging indicator** of regulatory compliance. Dr. Carmichael explicitly states that 15-day clock failures create "career consequence of late SAE reporting." This is a high-stakes metric.

**Risk if Target Missed**: FDA enforcement action (Warning Letter, Consent Decree), reputational damage, personal career risk for CMO.

---

### Metric 3: Seriousness Classification Accuracy vs Safety Physician Adjudication

**Description**: Agreement rate between AI seriousness classification and medical safety officer adjudication on a held-out validation sample.

**Current Baseline**: n/a (no AI baseline; manual process is assumed ~100% accurate as medical officers adjudicate directly).

**Target**: ≥96% (scenario).

**Measurement Method**:
- Sample: 100-case validation set spanning the heterogeneity of AE report formats and seriousness criteria (death, life-threatening, hospitalization, disability, congenital anomaly, other medically important)
- Ground truth: Medical safety officer adjudicates each case independently (blind to AI classification)
- Calculate: `accuracy = (count of cases where AI classification matches medical officer) / 100`
- Stratify by seriousness criterion to identify systematic errors (e.g., AI may perform well on death/hospitalization but poorly on "other medically important condition")

**Success Criteria**:
- ≥96% overall accuracy
- No systematic errors (e.g., <90% accuracy on any single ICH E2A criterion)
- False negative rate (serious classified as non-serious) ≤1% — patient safety priority

**Dependencies**:
- **A3** — Assumes ICH E2A seriousness criteria are sufficiently explicit and codified that LLM + chain-of-thought reasoning can achieve 96% accuracy. If criteria are more ambiguous than assumed, HITL verification is required, eliminating time savings.

**Why This Matters**: Seriousness classification is the gateway decision for 15-day reporting. A serious-unexpected AE requires expedited reporting; a non-serious AE does not. Errors in this classification create compliance risk (false negatives) or unnecessary expedited reporting burden (false positives).

**Risk if Target Missed**: If accuracy is 85%, the 15% error rate requires full HITL verification, eliminating the 15-minute time savings on classification.

---

### Metric 4: Expectedness Signal Precision (Cases Flagged Unexpected That Are Unexpected Per RSI)

**Description**: Precision of AI expectedness flagging — of all AEs flagged by AI as "unexpected" (not listed in product Reference Safety Information), what percentage are confirmed unexpected by medical safety officer review.

**Current Baseline**: n/a (no AI baseline).

**Target**: ≥85% (scenario).

**Measurement Method**:
- Numerator: Count of AEs flagged by AI as unexpected that are confirmed unexpected by medical safety officer review (true positives)
- Denominator: All AEs flagged by AI as unexpected (true positives + false positives)
- Calculate: `precision = TP / (TP + FP)`
- Measure over 90-day production period after Wave 1 deployment

**Success Criteria**:
- ≥85% precision sustained over 90 days
- False positive rate (expected flagged as unexpected) ≤15% — over-reporting is acceptable per A4

**Dependencies**:
- **A4** — Assumes 15% false-positive rate is acceptable because over-reporting is safer than under-reporting (FDA and EMA prefer over-reporting serious-unexpected AEs)
- **A2** — Performance may vary by AE source format; social media extracts with non-medical language may have lower precision than structured trial-site reports

**Why This Matters**: Expectedness is the second gate for 15-day expedited reporting (serious + unexpected = 15-day). False negatives (unexpected flagged as expected) are more serious than false positives (expected flagged as unexpected) — the system should err toward flagging unexpected when uncertain.

**Risk if Target Missed**: If precision is 60%, medical safety officers spend significant time correcting false-positive flags, eroding time savings.

---

### Metric 5: Reportability Recommendation Acceptance Rate (Recommendations Safety Officer Accepts As-Is)

**Description**: Percentage of AI reportability recommendations (15-day expedited, periodic only, non-reportable) that the medical safety officer accepts without revision.

**Current Baseline**: n/a (no AI baseline).

**Target**: ≥88% (scenario: "reportability recommendation precision").

**Measurement Method**:
- Numerator: Count of cases where medical safety officer accepts AI reportability recommendation without revision
- Denominator: All cases processed
- Calculate monthly acceptance rate
- Track rejection reasons (edge case complexity, global reportability variance, causality judgment, other)

**Success Criteria**:
- ≥88% acceptance rate sustained over 90 days
- Rejections primarily due to edge cases and clinical judgment (not systematic logic errors)

**Dependencies**:
- **A9** — Assumes 12% revision rate is acceptable because reportability involves judgment calls where reasonable experts may disagree (concomitant med causality, off-label use, global reportability variance)
- **A7** — If compliance failures are not primarily due to synthesis time, reportability recommendation quality becomes more critical

**Why This Matters**: This measures the practical value of AI recommendations. If medical safety officers revise 50% of recommendations, the system provides insufficient decision support.

**Risk if Target Missed**: If acceptance rate is 60%, medical safety officers spend time re-doing reportability determinations, eroding time savings.

---

### Metric 6: Per-Case Audit Trail Completeness (Machine-Generated for Inspector Retrieval)

**Description**: Percentage of processed cases with complete, machine-generated audit trails including span-level citations, classification reasoning, and reportability justification.

**Current Baseline**: 0% machine-generated (scenario: "manual today").

**Target**: 100% (scenario).

**Measurement Method**:
- Automated validation at `triage_complete_at` timestamp: Does the AE case package include:
  - Span-level citations for all extracted fields (which text in source report supports each field)
  - Chain-of-thought reasoning for seriousness classification (which ICH E2A criterion applies, why)
  - Rule-based justification for reportability recommendation (seriousness + expectedness → 15-day expedited per FDA 21 CFR 314.80)
- If any element is missing, flag as incomplete
- Calculate: `completeness = (count of complete audit trails) / (total cases processed)`

**Success Criteria**:
- 100% completeness sustained over production period
- Zero cases with missing or incomplete audit trails
- Audit trail retrievable on-demand in <10 seconds for FDA inspector request

**Dependencies**:
- **A10** — Assumes audit trail generation is a first-class system capability, not a post-processing step. If audit trail is bolted on later, it will be incomplete or unreliable.

**Why This Matters**: This is a **hard regulatory requirement** per Greta Schäffer (Chief Compliance Officer) and Dr. Hadi Mansour (external auditor, former FDA reviewer). Without complete audit trails, the system is non-compliant and cannot be deployed in production.

**Risk if Target Missed**: If completeness is 95%, FDA inspection readiness fails. Greta Schäffer's requirement is binary: 100% or the system is non-compliant.

---

## Critical Unknowns

The following unknowns require discovery work before detailed specification. Unknowns are prioritized by: (1) Must resolve before Wave 1 build begins, (2) Can be deferred to Wave 1 validation, (3) Can be deferred to post-deployment.

### Must Resolve Before Wave 1 Build (Week 1 Discovery)

#### U1: Actual Time Breakdown Per Case (Validates A1)

**Question**: Of the 75-minute baseline, how much time is actually spent on extraction vs classification vs expectedness vs reportability vs documentation?

**Why This Matters**: The entire economic case depends on the assumption that 60 of 75 minutes (80%) is synthesis work. If the actual breakdown is 40 min synthesis / 35 min medical judgment, the time savings target is unachievable.

**Discovery Method**: Time-motion study with case processing specialists — observe 20-30 cases across format mix, track time per activity type.

**Stakeholder**: Dr. Anil Iyer (Senior Safety Physician), case processing specialists.

**Risk if Wrong**: If synthesis is only 30 min of the 75 min, the target of ≤20 min total is unachievable, and the business case collapses.

---

#### U2: Root Cause of 15-Day Compliance Failures (Validates A7)

**Question**: Why do 8% of serious-unexpected AEs miss the 15-day clock? Is it intake queue delays, extraction complexity, reporter follow-up, medical officer review delays, or something else?

**Why This Matters**: If queue delays and extraction complexity are the root causes (per A7), AI intake triage solves the problem. If the root cause is medical officer review delays or complex causality assessments, AI intake acceleration alone won't reach 99.5% compliance.

**Discovery Method**: Root cause analysis with Theo Lonergan (Head of Drug Safety Ops) — pull data on last 50 compliance failures, categorize by failure mode, quantify contribution of each mode.

**Stakeholder**: Theo Lonergan, Dr. Maeve Carmichael.

**Risk if Wrong**: If compliance failures are due to medical officer capacity (not intake synthesis time), the AI triage system won't improve compliance, and the regulatory risk remains.

---

#### U3: Format Distribution and Complexity (Validates A2)

**Question**: What is the actual distribution of AE report formats in the intake queue? How much variation exists within each format category (e.g., are social media extracts consistently formatted JSON, or do they vary by monitoring vendor)?

**Why This Matters**: IDP build complexity depends on format heterogeneity. If 50% of reports are structured trial-site reports (MedDRA-coded), the IDP pipeline is simpler. If 50% are handwritten fax PDFs, the pipeline is more complex and expensive.

**Discovery Method**: Pull intake queue stats for past 90 days — count cases by source format, sample 5-10 cases per format to assess internal variation.

**Stakeholder**: Theo Lonergan (Head of Drug Safety Ops), case processing team.

**Risk if Wrong**: If social media extracts are 50% of volume (not 20% per A2), token costs and IDP complexity both increase.

---

#### U4: Product Reference Safety Information (RSI) Structure and Availability

**Question**: Are the Reference Safety Information profiles for Solivian, Tezarimab, and Phaedora available in machine-readable format (structured JSON, database)? Or are they unstructured text (PDF sections of the label)?

**Why This Matters**: Expectedness assessment requires comparing the reported AE term (MedDRA-coded or free text) against the product RSI. If RSI is structured, this is a lookup. If RSI is unstructured PDF text, this requires semantic matching and is less reliable.

**Discovery Method**: Request RSI documents from regulatory affairs (Carolina Núñez-Reyes). Assess structure and machine-readability. Identify if RSI is MedDRA-coded or free text.

**Stakeholder**: Carolina Núñez-Reyes (VP Regulatory Affairs).

**Risk if Wrong**: If RSI is unstructured text, expectedness signal precision may be <85%, requiring manual review and eroding time savings.

---

### Can Be Deferred to Wave 1 Build Validation

#### U5: Medical Safety Officer Review Workflow Integration

**Question**: How do medical safety officers currently receive completed case packages for sign-off? Email? Shared drive? Case management system? What is the integration point for the AI-generated AE case package?

**Why This Matters**: Determines the handoff mechanism from AI triage system to human review. If the current workflow is email-based, the system can generate email with structured attachment. If it's a case management system, API integration may be required.

**Discovery Method**: Workflow observation with Dr. Anil Iyer. Identify current handoff mechanism.

**Stakeholder**: Dr. Anil Iyer (Senior Safety Physician).

**Risk if Wrong**: If integration is complex (e.g., legacy case management system with no API), deployment timeline extends.

---

#### U6: Global Reportability Variance — FDA vs PMDA vs EMA

**Question**: Carolina Núñez-Reyes warns: "What's reportable to FDA in 15 days is not the same as what's reportable to PMDA." How significant are the jurisdiction-specific differences? Can the AI system delegate global reportability to human judgment, or is jurisdiction-specific logic required?

**Why This Matters**: Determines whether Wave 1 system handles only FDA reportability (simpler) or multi-jurisdiction reportability (more complex).

**Discovery Method**: Interview with Carolina Núñez-Reyes. Request examples of cases where FDA and PMDA reportability diverge.

**Stakeholder**: Carolina Núñez-Reyes (VP Regulatory Affairs).

**Risk if Wrong**: If multi-jurisdiction logic is required in Wave 1, build complexity increases. If deferred to Wave 2, early adopters may be limited to FDA-only cases.

---

#### U7: Historical Case Validation Set Availability

**Question**: Can Helix provide a validation set of 100-200 historical AE cases with ground-truth labels (seriousness, expectedness, reportability) adjudicated by medical safety officers?

**Why This Matters**: Required for validating AI seriousness classification accuracy (Metric 3), expectedness precision (Metric 4), and reportability acceptance rate (Metric 5).

**Discovery Method**: Request from Theo Lonergan or Dr. Iyer.

**Stakeholder**: Dr. Anil Iyer, Theo Lonergan.

**Risk if Wrong**: If validation set is unavailable, metrics cannot be measured pre-deployment, increasing production risk.

---

### Can Be Deferred to Post-Deployment

#### U8: Reporter Follow-Up Information Request Workflow

**Question**: When the AI system identifies missing information in an AE report (e.g., patient age not provided, concomitant medication list incomplete), how should the follow-up request be handled? Does the medical safety officer manually request follow-up, or can the system generate a draft request for officer approval?

**Why This Matters**: Determines whether the system only flags missing information (simpler) or generates follow-up requests (more value but more complex).

**Discovery Method**: Observe current follow-up workflow with case processing team.

**Stakeholder**: Dr. Anil Iyer, case processing specialists.

**Risk if Wrong**: If follow-up is fully manual, time savings are reduced. If the system generates follow-up requests without officer approval, it violates the "no reporter communication" scope guardrail.

---

#### U9: Token Cost Sensitivity to Report Complexity

**Question**: A5 assumes ~10,000 tokens per case on average. How much does this vary by report format and complexity? Are social media extracts with long conversation threads 3× more expensive than structured trial reports?

**Why This Matters**: Determines whether token costs are predictable (~$0.27/case) or highly variable ($0.10–$1.00/case). If variable, budget risk increases.

**Discovery Method**: Process the 8-case mock-data sample and measure actual token usage per case. Extrapolate to format distribution per A2.

**Stakeholder**: FDE (internal analysis).

**Risk if Wrong**: If token costs are 3× higher than assumed (~$5K/year instead of ~$1.6K/year), still negligible relative to $510K budget, but worth tracking.

---

#### U10: Incident-Management Integration for Audit Alerts

**Question**: When the AI system detects an anomalous case (e.g., novel AE term not in RSI, conflicting data in source report, extraction confidence across-the-board low), how should these incidents be escalated? Email alert to medical safety officer? Dashboard flag? Integration with existing incident-management system?

**Why This Matters**: Determines the monitoring and alerting architecture. If Helix has an existing incident-management system, integration may be required.

**Discovery Method**: Interview with Theo Lonergan and Greta Schäffer (Chief Compliance Officer).

**Stakeholder**: Theo Lonergan, Greta Schäffer.

**Risk if Wrong**: If incidents are not visible, the medical safety officer may miss high-risk cases. If alerts are too noisy, alert fatigue erodes trust in the system.

---

## Assumptions Register Reference

All assumptions referenced in this document are detailed in `specs/assumptions.md` with IDs A1–A10, including:
- Confidence levels (High 80-95%, Medium 55-75%, Low 30-50%)
- Reasoning and industry benchmark references
- Impact analysis if assumptions are wrong
- Validation plan (Week 1 discovery, Wave 1 build validation, post-deployment monitoring)

Key assumptions:
- **A1**: 75-min baseline breakdown (47% extraction, 20% classification, 13% expectedness, 13% reportability, 7% documentation)
- **A2**: Format distribution (30% HCP, 25% patient, 20% social media, 15% trial, 10% literature)
- **A3**: 96% seriousness classification accuracy achievable with LLM + CoT on ICH E2A criteria
- **A4**: 85% expectedness precision allows 15% false-positive rate (over-reporting safer than under-reporting)
- **A5**: Token cost ~$0.27 per case, ~$1,620 annually for 6K cases
- **A6**: Time savings enable throughput increase without new hires (not headcount reduction)
- **A7**: 15-day compliance failures: 50% queue delay, 30% extraction complexity, 20% reporter follow-up
- **A8**: IDP pipeline buildable within Wave 1 scope with Claude Code + LLM vision
- **A9**: 88% reportability recommendation acceptance allows 12% clinical override for edge cases
- **A10**: Audit trail requires span-level citations, CoT reasoning, and rule-based justification for FDA inspection

---

**Next Steps**:
1. **Week 1 Discovery Sprint** — Resolve U1, U2, U3, U4 (validates A1, A7, A2, and RSI structure)
2. **Architecture Decision Records** — Based on discovery findings, document ADRs for system decomposition, entity models, and delegation boundaries
3. **Capability Specifications** — Detailed specs for intake extraction (ADR-1), seriousness classification (ADR-2), expectedness assessment (ADR-3), reportability recommendation (ADR-4), and audit trail generation (ADR-5)

---

**Document Owner**: FDE Engagement Lead  
**Reviewers**: Dr. Maeve Carmichael (CMO), Dr. Anil Iyer (Senior Safety Physician), Theo Lonergan (Head of Drug Safety Ops)  
**Next Review**: After Week 1 Discovery Sprint
