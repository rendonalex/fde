# Assumptions Register
**Project:** Greenfield Health Systems — AI Claims Processing Transformation  
**Prepared by:** FDE Engagement Lead  
**Date:** 2026-04-09  
**Status:** Active — subject to revision as discovery data arrives

---

## How to Read This Register

Each assumption is labeled A1–A10. Throughout `01-problem-framing-and-success-metrics.md` and downstream specification documents, references appear as [A1], [A2], etc. When an assumption is validated or revised, update this file and propagate the change to all referencing documents.

Confidence levels:
- **High (>75%):** Well-supported by industry data or logical inference from stated facts
- **Medium (55–75%):** Reasonable but material uncertainty remains
- **Low (<55%):** Educated estimate; must be validated before Phase 2

---

## A1 — Claims Processor Fully Loaded Annual Cost

**Assumed value:** $65,000/year per admin claims processor (base salary ~$52,000 + 25% benefits and overhead)

**Why this value is reasonable:**  
The U.S. Bureau of Labor Statistics reports median annual wages for insurance claims and policy processing clerks at approximately $44,000–$56,000 (2024 data). Healthcare sector roles command a modest premium. A 25% benefits load (employer-side FICA, health insurance, retirement contribution, PTO accrual) is standard for U.S. employers. $65,000 fully loaded is a conservative midpoint.

**How it's used:** Financial ROI calculation in Metric 5; annual cost baseline for the 20-person admin team = $1.3M/year.

**Confidence:** Medium (65%)  
**Validation path:** Request HR salary bands for claims processor roles in Phase 1 discovery.

---

## A2 — Clinical vs. Administrative Claims Distribution

**Assumed value:** 35% of claims carry genuine clinical content (requiring physician review); 65% are administrative (eligible for Fast Path AI adjudication)

**Why this value is reasonable:**  
This is directly sourced from Dr. Marcus Webb's estimate in the stakeholder Slack exchange: *"Honestly? Maybe 30–35% of claims have genuine clinical content. The rest are billing and admin."* It is not independently validated. The CFO's earlier assumption (70% administrative) is more aggressive; Dr. Webb's estimate is more conservative. The 35% figure was accepted by the CFO as the basis for the revised financial model.

**How it's used:** The entire dual-path architecture depends on this split. It drives Fast Path volume, physician throughput requirements, and the headcount reduction model.

**Confidence:** Low (50%)  
**This is a hypothesis, not a fact.** Phase 1 shadow mode exists specifically to validate it. If actual clinical content is above 40%, the physician bottleneck reappears and the CFO's headcount model requires revision.

---

## A3 — Processor Productive Utilization Rate

**Assumed value:** 85% of an 8-hour workday = 408 productive minutes/day per processor

**Why this value is reasonable:**  
Standard knowledge-worker productivity research (SHRM, McKinsey) estimates 80–85% productive time for structured processing roles after accounting for breaks, brief meetings, system downtime, and administrative overhead. Claims processing is structured and repetitive, suggesting utilization at the higher end of this range.

**How it's used:** Daily processing capacity estimate = 45 processors × 408 min ÷ 35 min/claim = ~524 claims/day. This drives the capacity deficit calculation (1,300 manual claims/day required vs. ~524 capacity).

**Confidence:** Medium (65%)  
**Validation path:** Time-motion study or supervisor interviews during Phase 1 discovery.

---

## A4 — AI Token Cost per Claim

**Assumed value:** ~$0.05 per Fast Path claim (administrative checks); ~$0.10 per Clinical Path claim (pre-screening summary generation)

**Why this value is reasonable:**  
A single claim processed through Fast Path requires: (1) ingestion and parsing of claim data, (2) eligibility verification logic, (3) coding validation, and (4) structured output. Estimated token range: 2,000–5,000 input tokens + 300–800 output tokens. At Claude API pricing (~$3/M input, ~$15/M output), this yields approximately $0.01–0.02 for input and $0.005–0.012 for output ≈ $0.03–0.05 per Fast Path claim.

Clinical pre-screening requires reading more source material and generating a physician-ready summary. Estimated 2× token usage ≈ $0.06–0.12 per Clinical Path claim.

**How it's used:** Annual AI operating cost estimate = (1,667 × 365 × 65% × $0.05) + (1,667 × 365 × 35% × $0.10) ≈ $19,800 + $21,300 ≈ **~$41,000/year** in API costs. This is small relative to the $1.3M/year staff cost it partially replaces, making the economics favorable.

**Confidence:** Low–Medium (55%)  
Highly sensitive to actual claim document length, chosen model, and whether batching or caching reduces costs. Validate with a representative 100-claim sample in Phase 1.

---

## A5 — Physician Throughput Without Pre-Screening (Current State)

**Assumed value:** 5–8 claims/hour when reading full claim files from scratch

**Why this value is reasonable:**  
Dr. Webb states his team can review "~20 claims/hour if they're pre-screened by the agent" and contrasts this with "today's manual process where we read the whole file from scratch." A 2.5–4× throughput improvement from pre-screening is consistent with similar cognitive work where structured summaries replace unstructured document review. If pre-screening saves 70–75% of review time, the current rate implied is 20 ÷ 3.3 ≈ 6 claims/hour.

**How it's used:** Establishing current physician throughput as a co-bottleneck baseline. Without pre-screening, even a small physician team cannot keep pace with 35% × 1,667 = 583 clinical claims/day.

**Confidence:** Low (45%)  
Not stated in the scenario. Inferred from Dr. Webb's comparative language. Validate through physician time-study in Phase 1.

---

## A6 — Achievable Clinical Flagging False-Negative Rate (Post-Phase 1 Tuning)

**Assumed value:** < 2% false-negative rate is achievable after Phase 1 tuning with labeled claims data and a well-defined clinical flagging criteria set

**Why this value is reasonable:**  
Modern LLMs applied to structured classification tasks (clinical vs. non-clinical claim routing) can achieve >98% accuracy when: (a) classification criteria are precisely defined, (b) the model is evaluated against a labeled dataset, and (c) the system is iteratively tuned based on misclassification analysis. The 2% gate is not assumed to be met out-of-box — it is the validation target Phase 1 is designed to achieve.

**How it's used:** Phase 1 go/no-go gate. If the false-negative rate cannot be driven below 2% within the Phase 1 window, the Fast Path architecture cannot safely launch.

**Confidence:** Medium (60%)  
The 2% target is achievable but not guaranteed. It depends critically on U8 (clear definition of "clinical content") being resolved before Phase 1 begins. Without clear criteria, the model has no stable signal to train toward.

---

## A7 — Claims Format Distribution (EDI 837 vs. Non-EDI)

**Assumed value:** ~70% EDI 837 (structured, machine-parsable); ~30% PDF or portal submissions (requiring extraction)

**Why this value is reasonable:**  
EDI 837 adoption has increased significantly over the past decade under HIPAA mandate, but smaller provider groups and specialty practices still submit via PDF or portal. A 70/30 split is consistent with mid-size payer operations. The exact distribution depends heavily on Greenfield's provider mix.

**How it's used:** Affects agent design complexity and processing cost. Higher non-EDI volume increases extraction errors and token costs. A 30% non-EDI rate is used as the conservative planning assumption for ingestion module scope.

**Confidence:** Low (40%)  
Validate against actual submission data in Phase 1 discovery. See Unknown U6.

---

## A8 — Payer Penalty Rate per Claim per Day Above SLA

**Assumed value:** $15/claim/day above the 7-day SLA threshold (range: $10–$25)

**Why this value is reasonable:**  
Healthcare payer-provider contracts routinely include liquidated damages provisions for processing delays, typically ranging from $5–$25 per claim per day depending on the payer and contract tier. $15 is a reasonable midpoint for planning purposes.

**Illustrative exposure at current state:** If 1,667 claims/day are running at 9+ days (2 days over SLA), daily penalty exposure ≈ 1,667 × $15 × 2 = **~$50,000/day**. Even at $5/claim/day, exposure is ~$16,700/day. This underscores why VP Operations is under pressure.

**How it's used:** Penalty avoidance is a material component of the financial case. A 7-day SLA restoration eliminates this exposure. The ROI calculation is significantly stronger if penalties are included.

**Confidence:** Low (40%)  
Must be confirmed against actual payer contracts. See Unknown U4.

---

## A9 — Phase 1 Shadow Mode Infrastructure and Development Cost

**Assumed value:** $80,000–$100,000 (20–25% of $400K budget) consumed in Phase 1

**Why this value is reasonable:**  
Phase 1 requires: (1) integration with the existing claims management system [U7], (2) shadow mode logging and comparison infrastructure, (3) agent development and initial tuning, and (4) 3 months of API operating costs. For a 3-month pilot with non-trivial integration work, $80–100K is a conservative lower bound if the claims system has a usable API. Legacy system integration could push this higher.

**How it's used:** Constrains the remaining budget for Phase 2 and Phase 3. If Phase 1 consumes $100K, the remaining $300K must cover full deployment, physician summary interface, and 3+ months of operations.

**Confidence:** Low (40%)  
Highly dependent on IT infrastructure complexity [U7]. Must be scoped in discovery before Phase 1 formally begins.

---

## A10 — Minimum Physician Headcount Required for Clinical Path at Steady State

**Assumed value:** 4 physicians (or equivalent APPs) minimum; 5–6 recommended with buffer

**Why this value is reasonable:**  
At steady state: 35% × 1,667 = 583 clinical claims/day. At Dr. Webb's confirmed throughput of 20 claims/hour with pre-screening × 8 hours = 160 claims/physician/day. Minimum headcount: 583 ÷ 160 = **3.65 → 4 physicians minimum.** A 25–30% buffer for volume variability and absences suggests 5–6 as a safe operational target.

This is the minimum to maintain the 7-day SLA on the Clinical Path. If current physician headcount is fewer than 4, the project requires either hiring or the SLA cannot be met — a constraint not addressed in the scenario.

**How it's used:** Validates that the CMO's physician review requirement is operationally feasible within the proposed architecture. Also establishes that clinical review staffing cannot be reduced without violating the SLA — confirming the CMO's non-negotiable position.

**Confidence:** Medium (60%)  
Arithmetic is solid given A2 (35% clinical split) and Dr. Webb's stated throughput. The key uncertainty is whether A2 holds — if clinical content is 50%, minimum physician headcount rises to 5.2 → 6.

---

---

## A11 — AI Fast Path Denials Are Legally Permissible Without Per-Claim Physician Sign-Off

**Assumed value:** AI-generated claim denials on the Fast Path are legally permissible in Greenfield's operating jurisdictions without requiring physician authorization on each denial

**Why this value is reasonable:**  
The dual-path architecture's entire throughput benefit depends on the Fast Path agent being able to deny administrative claims without physician sign-off. Most U.S. states permit automated adjudication of administrative (non-clinical) claims, but AI-specific insurance regulations are evolving rapidly in 2026. Some states have introduced or are considering requirements for physician oversight of AI-generated denials. This assumption is treated as true for planning purposes but is flagged as a legal discovery requirement [U5] that must be confirmed before the Fast Path specification is finalized.

**How it's used:** Determines whether the Fast Path can issue denials autonomously or must route potential denials to the Clinical Path queue for physician sign-off. If false, the Fast Path scope is limited to approvals only, reducing throughput gain and materially revising the CFO's headcount reduction model.

**Confidence:** Low (45%)  
State insurance AI regulations vary widely and are in active flux. Must be confirmed via legal review before Phase 2 specification is written. See Unknown U5.  
**Validation path:** Legal counsel review of applicable state insurance regulations by Day 30 of engagement.

---

## A12 — Claims Management System Has a Usable API for Phase 1 Shadow Integration

**Assumed value:** Greenfield's claims management system has a usable REST or HL7 FHIR API (or equivalent) that allows the agent to ingest claim data in near-real-time and write comparison logs for Phase 1 shadow mode without a full re-implementation

**Why this value is reasonable:**  
Shadow mode requires reading incoming claims and writing agent decisions back for comparison against processor decisions. Modern payer systems (updated Facets, TriZetto, or cloud-native alternatives) generally expose data APIs. However, a significant portion of mid-size payers run legacy systems on 2000s-era platforms with limited or proprietary interfaces. If the CMS has no modern API, integration becomes the dominant Phase 1 cost driver, consuming a disproportionate share of the $400K budget [A9] before a single claim is adjudicated.

**How it's used:** Determines Phase 1 architecture and integration cost estimate. If false, Phase 1 may require batch file-based shadow mode as a fallback, increasing complexity and reducing comparison data fidelity.

**Confidence:** Low (40%)  
Legacy healthcare CMS platforms are common and their API maturity varies widely. Must be assessed in the first IT discovery sprint. See Unknown U7.  
**Validation path:** IT discovery sprint in Week 1 of engagement — confirm CMS vendor, API availability, and integration scope before any development is committed.

---

## A13 — Admin Processors Remain Cooperative and Productive During Phase 1 Shadow Mode

**Assumed value:** The 20 admin claims processors whose roles are targeted for reduction will continue performing their current duties at normal capacity during the 3-month Phase 1 shadow period

**Why this value is reasonable:**  
Phase 1 comparison data depends on current processors making decisions the agent can be compared against. Staff facing potential elimination typically continue working through defined transition periods, particularly when: (a) no reductions have yet been announced, (b) the timeline is clear, and (c) HR communicates the process fairly. Risk increases if timeline is ambiguous, if informal attrition accelerates, or if processors reduce effort in anticipation of elimination. A clear HR policy — no reductions until Phase 1 gate is passed — is the primary mitigation.

**How it's used:** If processors reduce throughput or depart during Phase 1, the shadow comparison dataset degrades, potentially delaying the Phase 1 gate and threatening the 6-month headcount reduction timeline.

**Confidence:** Medium (65%)  
Most staff continue working through defined transition periods with proper communication. Risk is manageable with proactive HR engagement before Phase 1 begins.  
**Validation path:** HR communication plan deployed and supervisor check-ins established before Phase 1 launch.

---

## A14 — Non-EDI Claim Manual Re-keying Rate

**Assumed value:** ~80% of non-EDI submissions (PDF and portal claims) require manual re-keying of key claim fields by an admin processor before processing can begin; structured OCR or intelligent document extraction is not currently in place

**Why this value is reasonable:**  
Legacy payer operations commonly lack intelligent document processing for PDF claims. Portal submissions may carry semi-structured data but still require manual field mapping into the CMS. The 30% non-EDI volume [A7] combined with this assumption implies ~24% of total daily claim volume (400+ claims/day) involves manual re-entry as a hidden pre-processing step. This step is not separately logged in the 35-minute processing average, understating the true cost of non-EDI claims by an estimated 50–100%.

**How it's used:** Shapes the AI agent's ingestion module requirements (extraction pipeline for non-EDI formats), affects MT-1.2 cognitive load scoring, and explains a portion of cycle time not captured in the processing-time metric. See `cognitive-load-map.md`.

**Confidence:** Low (40%)  
**Validation path:** IT discovery sprint — confirm whether extraction tooling exists or must be built. See [A7] and [A12].

---

## A15 — Clinical Content Flagging Criteria Are Informal and Undocumented

**Assumed value:** No formal, written criteria currently exist for determining whether a claim contains "clinical content" requiring physician review; routing decisions are made by admin processors using experience-based heuristics and informal pattern recognition

**Why this value is reasonable:**  
Dr. Webb's estimate of 30–35% clinical volume was described as rough intuition during a Slack exchange, not derived from documented policy. The scenario flags this as Unknown U8 ("clinical content" not formally defined). The 41% denial appeal overturn rate is consistent with inconsistent upstream triage — some clinical claims reaching the Fast Path incorrectly. If formal criteria existed, their definition would not appear as a Day 1 next-step action in the stakeholder alignment memo.

**How it's used:** This is the single most consequential assumption for the agentic architecture. Without formal criteria, Phase 1 shadow mode cannot produce a stable training signal for the clinical flagging agent, and the <2% false-negative gate [A6] cannot be measured against a consistent standard. Criteria definition must be the first deliverable before any agent development begins.

**Confidence:** Medium (60%)  
**Validation path:** Structured interview with Dr. Webb and senior admin processors in Week 1 of engagement. See Unknown U8.

---

## A16 — Denial Letters Use Manual Template Fill-in

**Assumed value:** Denial letters are generated by copying from prior similar letters or manually filling in regulatory template fields; there is no automated generation of denial language from claim data; template adherence and rationale-to-policy matching is inconsistent across processors

**Why this value is reasonable:**  
The 41% denial appeal overturn rate is substantially above the typical industry range of 10–15%. Outcome accuracy alone cannot explain this rate — even correct denials are being overturned because the documentation is legally indefensible. Manual template fill-in with inconsistent policy citation is the most common operational driver of this pattern in payer operations.

**How it's used:** Shapes MT-9.1 scoring (denial letter generation) in the cognitive load map and the appeal management workstream in JtD-9. AI-generated denial language — pulling the specific policy provision violated and documenting the reasoning chain — could materially reduce the 41% overturn rate. Currently Out of Scope for MVP but flagged for Phase 3.

**Confidence:** Medium (55%)  
**Validation path:** Review sample denial letters and appeal overturn documentation in Phase 1 discovery.

---

## A17 — Processing Queue Is Not Prioritized by SLA Proximity

**Assumed value:** Claims are processed in informal first-in, first-out order; no systematic queue prioritization exists based on SLA age, payer penalty thresholds, or appeal deadlines; prioritization is driven by processor discretion and informal payer relationship conventions

**Why this value is reasonable:**  
VP Operations explicitly states claims are "sitting in queue for 9+ days," triggering payer penalties. If a formal SLA-based priority queue existed, claims nearest the 7-day breach threshold would be processed first, preventing penalties. Ongoing penalty exposure despite a known SLA implies either the queue management system does not track SLA proximity or does not act on it. Appeals re-entering the same queue as new claims (rather than a priority lane) is consistent with this assumption.

**How it's used:** Shapes queue management requirements for the AI agent. An SLA-aware priority queue — surfacing oldest or penalty-at-risk claims first — is a required capability for the Cycle Time SLA metric. Without it, AI adjudication speed gains are offset by queue management inefficiencies.

**Confidence:** Medium (55%)  
**Validation path:** Observe current queue management practice and CMS reporting capabilities in Phase 1 IT discovery.

---

## A18 — Coverage Rules Engine Exists in Machine-Readable Form

**Assumed value:** The coverage policies governing Fast Path adjudication (ADR-5) exist in a structured, machine-readable format (e.g., a rules engine, decision table, or structured policy database) — not solely as narrative PDF benefit documents — such that the agent can reliably apply coverage criteria without manual interpretation

**Why this value is reasonable:**  
ADR-5 Fast Path adjudication requires the agent to apply coverage rules deterministically. If those rules exist only as narrative benefit documents, the delegation archetype changes: the agent cannot reliably apply rules it can only read as prose, and "Fully Agentic" is not achievable. Many payers run structured rules engines (e.g., ClaimLogic, Edifecs, or proprietary policy tables). However, a meaningful proportion of coverage policy exists in hybrid form — partially structured, partially narrative — requiring manual encoding before agent use.

**How it's used:** Determines scope and feasibility of ADR-5 Fast Path adjudication and ADR-9 denial letter generation. If rules are not machine-readable, encoding them is a prerequisite Phase 1 work item that affects budget and timeline. See `specs/03-agentic-solution-architecture.md`.

**Confidence:** Low (45%)  
**Validation path:** Review coverage policy documentation format and rules engine existence in Phase 1 IT discovery sprint.

---

## A19 — Regulatory Appeal Response Deadlines Are Tracked

**Assumed value:** State-mandated appeal response deadlines (typically 30 days for first-level administrative appeals under applicable state insurance regulations) apply to Greenfield, and current tracking capability for those deadlines exists or can be readily implemented

**Why this value is reasonable:**  
ADR-9 appeal management depends on knowing which open appeals have binding regulatory deadlines. VP Operations' observation that claims sit in queue without SLA-based prioritization [A17] suggests deadline tracking may be informal. An appeal deadline breach is a regulatory compliance violation independent of the AI project — but the agent queue prioritization design must account for it. If deadlines are not currently tracked, this is a compliance risk that the project surfaces rather than creates.

**How it's used:** Shapes ADR-9 queue design — appeals with active regulatory deadlines must be prioritized ahead of new claims. If tracking capability does not exist, it must be built as part of the agent's appeal management workflow. See `specs/03-agentic-solution-architecture.md`.

**Confidence:** Low (40%)  
**Validation path:** Legal/compliance review in Phase 1 discovery; confirm applicable state insurance appeal timelines.

---

## A20 — Physician Review Portal Can Display Structured Pre-screened Summaries

**Assumed value:** The physician review portal used by Dr. Webb's team can be configured or extended to display structured pre-screened clinical summary packages generated by the ADR-6 agent — rather than requiring physicians to navigate the full claim file

**Why this value is reasonable:**  
Dr. Webb's throughput improvement from 5–8 to 20 claims/hour [A5] depends on physicians receiving and reading the pre-screened summary efficiently, not on the summary existing in isolation. If the physician review portal cannot display structured summaries — or forces physicians to toggle between the summary and the underlying file — the productivity gain is partially or fully negated. Portal UI capability is an IT constraint that must be assessed before ADR-6 development scope is finalized.

**How it's used:** Determines whether ADR-6 summary delivery requires portal modification (in-scope) or can be embedded in the existing interface (out-of-scope). If the portal requires a new UI component, this is a Phase 2 development item that must be scoped and budgeted against [A9]. See `specs/03-agentic-solution-architecture.md`.

**Confidence:** Low (45%)  
**Validation path:** IT discovery sprint — physician portal vendor assessment and UI modification feasibility review.

---

## A21 — Time Allocation Across ADRs (% of 35-Minute Processing Average)

**Assumed value:** The 35-minute average claim processing time is allocated across ADRs as follows: ADR-1 Intake 9%, ADR-2 Eligibility 23%, ADR-3 Coding 17%, ADR-4 Triage 9%, ADR-5 Fast Path Adjudication 19% (65% of claims), ADR-8 Payment 9%, ADR-9 Denial letters 7%, overhead/residual 7%.

**Why this value is reasonable:**  
Eligibility verification (multi-system manual lookup) is the known largest time sink per claim — consistent with processor accounts of "opening three windows" to reconcile coverage data. Coding validation and Fast Path adjudication each require rule application against reference databases. Intake and payment are largely system-facilitated steps. The allocation is calibrated to sum to 35 minutes across the blended Fast Path (65%) and Clinical Path (35%) populations. No time-motion study data exists; this is a model input requiring Phase 1 validation.

**How it's used:** Allocates the $1.3M/year admin labor cost baseline across individual ADRs for TCO calculations in `specs/volume-×-value-analysis.md`.

**Confidence:** Low (40%)  
**Validation path:** Time-motion study or supervisor time log analysis in Phase 1 discovery. Adjust allocations before finalizing Wave 2 ROI projections.

---

## A22 — Denial Rate Across All Claims (~20%)

**Assumed value:** Approximately 20% of all claims across both Fast Path and Clinical Path result in a denial at first adjudication (before appeals).

**Why this value is reasonable:**  
The scenario reports a 41% denial appeal overturn rate, which implies a meaningful volume of claims are denied. U.S. payer denial rates typically range from 15–25% before appeals, with the higher end more common in payers with manual adjudication processes. A 20% denial rate applied to 1,667 claims/day yields ~333 denials/day — the volume basis for ADR-9 scoring. The actual rate will depend on the clinical/admin split [A2] and the accuracy of the AI flagging system [A6].

**How it's used:** Drives ADR-9 volume score (333 denials/day → Score 4) and HITL cost estimates for physician sign-off on AI-generated denial letters. See `specs/volume-×-value-analysis.md`.

**Confidence:** Low (40%)  
**Validation path:** Review adjudication outcome data in Phase 1 discovery — actual denial rate by path type and reason code.

---

## A23 — Physician Fully Loaded Annual Cost (~$250,000)

**Assumed value:** A physician or advanced practice provider in a clinical review role carries a fully loaded annual cost of approximately $250,000 (base salary ~$180,000–$200,000 + benefits, malpractice coverage, and overhead at ~25–35%).

**Why this value is reasonable:**  
Physician salary for clinical review roles (non-procedural, administrative) typically ranges $180K–$220K base for MD/DO and $120K–$150K for NPs/PAs. Fully loaded cost adds employer benefits, malpractice insurance, and administrative overhead. $250K is a conservative midpoint for a physician reviewer role. This assumption is used only for the avoided-hiring value calculation for ADR-6 — it does not affect the admin staff headcount model, which uses [A1].

**How it's used:** Estimates the value of ADR-6's physician capacity multiplier: if the same 4 physicians handle 2.7× more claims with pre-screening [A5], the project avoids hiring ~6 additional reviewers at $250K = ~$1.5M/year in avoided cost. This is additive value not included in the base ROI case.

**Confidence:** Low (40%)  
**Validation path:** Request physician role salary bands from HR in Phase 1 discovery. Confirm whether current clinical review staff are MDs, DOs, or APPs — compensation varies materially by credential.

---

## A24 — Triage Agent Conservative Routing Fallback Threshold

**Assumed value:** When the clinical content triage agent's classification confidence falls below a defined threshold (initial default: 0.80; to be calibrated during Phase 1 shadow mode), the claim is routed to Clinical Path regardless of the marginal classification — accepting a false-positive cost to eliminate false-negative patient safety risk.

**Why this value is reasonable:**  
The cost asymmetry between false negatives (clinical claim routed to Fast Path without physician review — patient care failure) and false positives (administrative claim routed to Clinical Path — unnecessary physician time) is categorical, not marginal. A conservative confidence fallback enforces this asymmetry structurally: near-boundary claims default to the safe path. The 0.80 default is a starting calibration point; Phase 1 shadow data will determine whether a higher or lower threshold better balances false-negative rate and Clinical Path volume. The threshold is a versioned parameter in the agent system prompt.

**How it's used:** Governs the ADR-4 routing decision rule for low-confidence classifications. Affects Clinical Path volume and physician workload [A10]. If the fallback rate is high, it signals that criteria codebook coverage [A15] needs expansion before live deployment.

**Confidence:** Low–Medium (55%)  
**Validation path:** Phase 1 shadow mode calibration — analyze confidence score distribution across agent classifications and false-negative cases to determine optimal threshold before Wave 2 live deployment.

---

## A25 — Shadow Mode Ground-Truth Adjudication Process

**Assumed value:** During Phase 1 shadow mode, claims where the agent's routing classification disagrees with the current processor's routing decision are submitted to Dr. Webb's team for definitive labeling — establishing an authoritative ground-truth dataset used to measure the false-negative rate [A6].

**Why this value is reasonable:**  
Processor routing decisions are themselves informal and subject to the heuristic variance documented in [A15] — using raw processor decisions as the sole ground-truth baseline risks measuring agent accuracy against a noisy standard. Cases where the agent and processor disagree are precisely the clinically ambiguous boundary cases where processor error is most likely. Dr. Webb adjudication on disagreements produces a higher-quality labeled dataset, resolves the ambiguity at the clinical boundary, and is consistent with the stakeholder alignment memo's requirement that clinical criteria are co-defined with the CMO. The volume of disagreements will determine Dr. Webb team capacity requirements; if disagreements exceed ~10% of daily claim volume, a structured adjudication workflow (not ad-hoc review) is required.

**How it's used:** Determines the ground-truth labeling methodology for Phase 1 evaluation, which directly determines the denominator and false-negative rate calculation used to measure the [A6] gate. Also drives the criteria codebook refinement process — disagreements that Dr. Webb labels as clinical (but the agent classified as administrative) are the primary input to codebook expansion.

**Confidence:** Low (40%)  
**Validation path:** Confirm Dr. Webb team availability and adjudication capacity in Week 1 planning. Design adjudication workflow before Phase 1 shadow mode begins.

---

---

## A26 — ADR-4 Triage Agent Token Cost Per Claim

**Assumed value:** ~$0.03/claim for all 600,000 claims/year (blended: base token cost + policy RAG on ~20% of claims)

**Why this value is reasonable:**  
ADR-4 processes a compact normalized claim record (~300 tokens of claim fields) alongside the criteria codebook (~1,000 tokens) in the system prompt. With chain-of-thought output required for auditability (~1,000 tokens of reasoning trace + JSON), total token consumption is approximately 2,300 tokens/claim. At Claude Sonnet pricing ($3/M input, $15/M output), base token cost ≈ $0.022/claim. Policy RAG is triggered for ~20% of claims at $0.02–0.04/call, adding ~$0.006/claim on a volume-weighted basis. Rounded total: $0.028–$0.030/claim.

**How it's used:** ADR-4 token economics model in `specs/08-economics.md` (§3.3). Annual token cost = 600,000 × $0.030 = $18,000, representing 36% of total ADR-4 agent cost.

**Confidence:** Low–Medium (55%)  
**Validation path:** Measure actual token consumption on a 100-claim calibration sample during Phase 1 shadow mode. Adjust model tier or prompt length if cost exceeds $0.05/claim.

---

## A27 — Annual System Maintenance and Operations Cost

**Assumed value:** 15% of total build cost per year (range: 10–20%)

**Why this value is reasonable:**  
Healthcare AI systems with regulatory compliance requirements (HIPAA, clinical oversight [A11]) require ongoing maintenance including: model re-evaluation on new releases, prompt and codebook updates [A15], integration maintenance as CMS evolves [A12], monitoring and alerting, and compliance audit support. 15% annual maintenance is standard for production AI systems in regulated industries — lower than traditional enterprise software (20–25%) because the platform layer (CMS API, audit logging) requires minimal ongoing change once stable.

**How it's used:** ROI calculations in `specs/08-economics.md`: ADR-1 annual maintenance = $8,250 (15% of $55K build); ADR-4 annual maintenance = $5,250 (15% of $35K build); portfolio annual maintenance = $60,000 (15% of $400K total build).

**Confidence:** Low–Medium (55%)  
**Validation path:** Confirm with EPAM delivery team at project kickoff. Adjust if physician portal integration [A20] or compliance requirements drive higher change frequency.

---

## A28 — Wave 1 Build Cost Allocation (ADR-1 and ADR-4)

**Assumed value:** ADR-1: $55,000; ADR-4 (shadow mode + evaluation infrastructure): $35,000; shared Wave 1 infrastructure: $10,000. Total Wave 1: $100,000 (within A9 range of $80K–$110K).

**Why this value is reasonable:**  
ADR-1 build cost is driven by: CMS API integration [A12] ($15K), EDI parser and IDP pipeline development [A14] ($25K), and testing across 8+ claim format channels ($5K). ADR-4 shadow mode build cost is driven by: criteria codebook co-development with Dr. Webb [A15] ($7K), classification model and prompt engineering ($15K), and shadow evaluation log store + adjudication queue infrastructure [A25] ($10K). Shared infrastructure (audit log, common schema, SLA queue module [A17]) is allocated equally across Wave 1 agents. Total $100K is consistent with [A9] estimate and leaves $300K for Wave 2 and Wave 3 development.

**How it's used:** Business case models in `specs/08-economics.md` §2.4 and §3.4; payback period calculations for individual agents and portfolio.

**Confidence:** Low (40%)  
**Validation path:** Confirm with EPAM team during Phase 1 scoping. CMS API complexity [A12] is the single largest cost uncertainty — legacy CMS integration could increase ADR-1 build cost by $20K–$40K.

---

## A29 — Portal API Rate Limit (ADR-1 Ingestion)

**Assumed value:** Provider portal APIs enforce a rate limit of approximately 100 requests/minute; ADR-1 applies exponential backoff on HTTP 429 responses and preserves the original claim submission timestamp as `received_at` regardless of ingestion delay.

**Why this value is reasonable:**  
Major healthcare portal APIs (payer portals, clearinghouse APIs) routinely enforce per-minute rate limits to protect backend systems from burst traffic. End-of-day batch submissions from large provider groups are the most likely burst pattern. 100 requests/minute is a conservative estimate for mid-size payer APIs; actual limits vary by vendor. Preserving `received_at` from the original submission (not the time of normalization) is required to ensure SLA timers are not artificially extended by rate-limit-induced processing delays.

**How it's used:** ADR-1 error handling design (EC-1E in `specs/09-validation-plan.md`); SLA timer anchoring logic in the NormalizedClaimRecord schema.

**Confidence:** Low (40%)  
**Validation path:** Confirm portal vendor rate limit specifications in Week 1 IT discovery sprint. Implement token-bucket rate control in ADR-1 ingestion layer if confirmed limit is below expected peak submission rate.

---

## A30 — IDP Pipeline Failure Alert Threshold

**Assumed value:** If ≥5% of IDP extraction attempts fail (return empty or errored results) over any 15-minute window, an ops alert is triggered; individual extraction failures below this threshold are handled silently via HITL routing.

**Why this value is reasonable:**  
Individual IDP failures on low-quality scans are expected and handled by routing the claim to HITL review (normal operating condition). A sustained failure rate above 5% over 15 minutes signals a systemic IDP service degradation rather than individual document quality issues — this requires ops intervention. The 5% threshold is a starting calibration point; the actual baseline IDP failure rate must be measured during Phase 1 shadow mode to set an appropriate alert sensitivity.

**How it's used:** ADR-1 error handling (EH-1B in `specs/09-validation-plan.md`); IDP monitoring configuration for Wave 1 ops.

**Confidence:** Low–Medium (55%)  
**Validation path:** Measure actual IDP failure rate against a representative 200-document sample during Phase 1 calibration. Adjust threshold before ops dashboard is finalized.

---

## A31 — NOVEL_CASE Rate Alert Threshold (ADR-4)

**Assumed value:** If ADR-4 classifies ≥50% of incoming claims as NOVEL_CASE over any 5-minute window, an ops alert is triggered — indicating that the criteria codebook is missing, empty, or misconfigured rather than reflecting genuine claim novelty.

**Why this value is reasonable:**  
Under normal operations, NOVEL_CASE classifications should represent genuinely novel CPT/ICD-10 codes absent from the codebook — expected to be a small fraction of daily volume (<5%). A sudden rate of ≥50% NOVEL_CASE is not consistent with real-world claim mix variability; it is consistent with an empty codebook, a misconfigured system prompt, or a failed codebook deployment [A15]. A 5-minute window is short enough to catch an empty-codebook startup error before large volumes of claims are misclassified, while being long enough to avoid spurious alerts on momentary sampling noise.

**How it's used:** ADR-4 ops monitoring (EC-4B in `specs/09-validation-plan.md`); codebook deployment validation gate before ADR-4 starts processing production claims.

**Confidence:** Low–Medium (55%)  
**Validation path:** Calibrate threshold against observed NOVEL_CASE rate during Phase 1 shadow mode. If legitimate NOVEL_CASE rate in shadow data exceeds 10%, lower the alert threshold to 30% to maintain sensitivity.

---

## Assumption Summary Table

| ID | Description | Value | Confidence | Must Validate By |
|----|-------------|-------|------------|-----------------|
| A1 | Processor fully loaded annual cost | $65,000/year | Medium (65%) | Phase 1 discovery |
| A2 | Clinical vs. admin claims split | 35% clinical / 65% admin | Low (50%) | **End of Phase 1** |
| A3 | Processor productive utilization | 85% of 8-hour day | Medium (65%) | Phase 1 discovery |
| A4 | AI token cost per claim | $0.05 Fast Path / $0.10 Clinical | Low–Medium (55%) | Phase 1 pilot |
| A5 | Physician throughput without pre-screening | 5–8 claims/hour | Low (45%) | Phase 1 discovery |
| A6 | Clinical flagging false-negative rate (achievable) | <2% post-tuning | Medium (60%) | **Phase 1 gate** |
| A7 | Claims format distribution | 70% EDI / 30% non-EDI | Low (40%) | Phase 1 discovery |
| A8 | Payer penalty rate | $15/claim/day (range $10–25) | Low (40%) | Phase 1 discovery |
| A9 | Phase 1 infrastructure cost | $80K–$100K | Low (40%) | Pre-Phase 1 scoping |
| A10 | Min. physician headcount for Clinical Path | 4 minimum, 5–6 recommended | Medium (60%) | Phase 1 discovery |
| A11 | AI Fast Path denials legally permissible without physician sign-off | Assumed permissible pending legal review | Low (45%) | **Day 30 of engagement** |
| A12 | CMS has a usable API for Phase 1 shadow integration | Assumed present pending IT assessment | Low (40%) | **Week 2 IT discovery sprint** |
| A13 | Admin processor cooperation through Phase 1 shadow mode | Assumed; depends on HR communication | Medium (65%) | Before Phase 1 launch |
| A14 | Non-EDI claim manual re-keying rate | ~80% of PDF/portal claims require manual re-key | Low (40%) | IT discovery sprint |
| A15 | Clinical flagging criteria documentation status | Informal/undocumented — no formal criteria exist | Medium (60%) | **Week 1 — before agent development** |
| A16 | Denial letter generation method | Manual template fill-in; inconsistent policy matching | Medium (55%) | Phase 1 discovery |
| A17 | Processing queue prioritization approach | Informal; not SLA-aware | Medium (55%) | IT discovery sprint |
| A18 | Coverage rules engine in machine-readable form | Assumed present; format unconfirmed | Low (45%) | Phase 1 IT discovery sprint |
| A19 | Regulatory appeal response deadlines tracked | Assumed; tracking capability unconfirmed | Low (40%) | Phase 1 legal/compliance review |
| A20 | Physician portal supports structured summary display | Assumed configurable; UI capability unconfirmed | Low (45%) | Phase 1 IT discovery sprint |
| A21 | Time allocation across ADRs (% of 35 min/claim) | Estimated distribution; no time-motion data | Low (40%) | Phase 1 time-motion study |
| A22 | Denial rate across all claims | ~20%; industry range 15–25% | Low (40%) | Phase 1 adjudication outcome review |
| A23 | Physician fully loaded annual cost | ~$250K/year (MD/DO or APP) | Low (40%) | Phase 1 HR salary band review |
| A24 | Triage agent confidence fallback threshold | 0.80 default; claims below threshold route to Clinical Path | Low–Medium (55%) | Phase 1 shadow mode calibration |
| A25 | Shadow mode ground-truth adjudication | Agent-vs-processor disagreements labeled by Dr. Webb's team | Low (40%) | **Week 1 — before Phase 1 begins** |
| A26 | ADR-4 triage agent token cost per claim | ~$0.03/claim (Sonnet, CoT + 20% RAG trigger rate) | Low–Medium (55%) | Phase 1 calibration sample |
| A27 | Annual system maintenance cost | 15% of total build cost per year | Low–Medium (55%) | Project kickoff with EPAM delivery team |
| A28 | Wave 1 build cost allocation | ADR-1: $55K; ADR-4: $35K; shared: $10K; total: $100K | Low (40%) | Phase 1 scoping with EPAM team |
| A29 | Portal API rate limit | 100 requests/minute assumed; claim submission timestamp preserved as `received_at` | Low (40%) | Week 1 IT discovery — confirm portal vendor rate limit specs |
| A30 | IDP pipeline failure alert threshold | ≥5% IDP extraction failures over any 15-minute window triggers an ops alert | Low–Medium (55%) | Phase 1 — calibrate threshold against observed IDP baseline failure rate |
| A31 | NOVEL_CASE alert threshold (ADR-4) | NOVEL_CASE rate ≥50% over any 5-minute window triggers an ops alert (indicates empty or missing codebook) | Low–Medium (55%) | Phase 1 pre-launch — confirm with ops team before shadow mode begins |
