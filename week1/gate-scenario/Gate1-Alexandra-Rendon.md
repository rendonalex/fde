# Gate1 - FNOL Processing Analysis & Specification
### Complete Project Reference - Alexandra Rendon

---

## Master Table of Contents

This document consolidates three core project artifacts for the FNOL (First Notice of Loss) insurance claims processing automation initiative:

- [**1. Problem Statement & Success Metrics**](#1-problem-statement--success-metrics) — Business problem definition, quantified baseline, success criteria
- [**2. Delegation Analysis**](#2-delegation-analysis) — Automation boundaries, risk mitigation, implementation phasing  
- [**3. Agent Specification**](#3-agent-specification) — Technical architecture, data model, integration points

Each section is a complete standalone document. Use this master TOC to navigate between documents.

---

---

# 1. Problem Statement & Success Metrics

# Problem Statement & Success Metrics: Insurance Claims FNOL Processing

## Table of Contents
- [1. Problem Statement](#1-problem-statement)
  - [Current State (Quantified)](#current-state-quantified)
  - [Problem from Claimant Perspective](#problem-from-claimant-perspective)
  - [Problem from Business Perspective](#problem-from-business-perspective)
  - [What Client Asked For vs. What They Need](#what-client-asked-for-vs-what-they-need)
  - [Explicit Constraints](#explicit-constraints)
- [2. Assumptions](#2-assumptions)
- [3. Success Metrics](#3-success-metrics)
  - [Metric 1: SLA Compliance Rate](#metric-1-sla-compliance-rate)
  - [Metric 2: Routing Accuracy Rate](#metric-2-routing-accuracy-rate)
  - [Metric 3: Cost Per Claim Processed](#metric-3-cost-per-claim-processed)
  - [Metric 4: Straight-Through Processing Rate (STP)](#metric-4-straight-through-processing-rate-stp)
  - [Metric 5: Adjuster Productivity (Downstream Impact)](#metric-5-adjuster-productivity-downstream-impact)
- [4. Unknowns](#4-unknowns)
  - [Critical Unknowns](#critical-unknowns-must-resolve-before-specification)
  - [Important Unknowns](#important-unknowns-high-impact-can-be-deferred-slightly)
  - [Lower-Priority Unknowns](#lower-priority-unknowns-can-be-resolved-during-build)
- [Summary](#summary)

---

## 1. Problem Statement

### Current State (Quantified)
The claims team processes **300 FNOL reports daily** with:
- **12 FTE specialists** consuming **110 staff-hours per day** (300 claims × 22 min ÷ 60)
- **18% routing error rate** = ~54 claims/day misrouted, requiring rework and adjuster context-switching
- **31% SLA breach rate** = 93 claims/day acknowledged after the 2-hour window
- **Manual processing** of unstructured inputs (email, phone transcripts, web forms) with no standardization

### Problem from Claimant Perspective
Claimants experience:
- **Inconsistent response times**: 31% wait beyond promised 2-hour acknowledgment
- **Delayed claim resolution**: 18% of claims routed incorrectly must be transferred, restarting the intake process *[A3: assumes 45 min combined rework time]*
- **No transparency**: Manual process provides no interim status updates during the 22-minute handling window

### Problem from Business Perspective
The business faces:
- **High labor cost**: 110 staff-hours/day at **$4,950/day** *[A1: $45/hour fully-loaded cost; A2: calculated daily cost]* dedicated to repetitive triage and routing work
- **Operational inefficiency**: 18% routing errors create downstream rework for adjusters *[A3: 45 min rework per error]*, degrading their productivity *[A13: baseline 8 claims/adjuster/day]*
- **SLA penalty exposure**: 31% breach rate likely triggers contractual penalties *[A4: $25/breach soft cost]* or regulatory scrutiny, costing **~$2,325/day** in direct and indirect penalties (93 breaches × $25)
- **Scalability constraint**: Linear relationship between claim volume and headcount prevents growth without proportional hiring

### What Client Asked For vs. What They Need
**Client asked for**: "Can AI handle most of this?"

**What they actually need** *[U12: client's actual success criteria unknown]*: 
1. **Reduction in SLA breach rate** from 31% to target level *[A14: assumes <5% target]* to meet regulatory/contractual obligations *[A4: assumes penalty structure exists; U3: actual requirements unknown]*
2. **Elimination of routing errors** from 18% to target level *[A15: assumes 3% target based on A9 AI capability]* to protect adjuster productivity *[A13: baseline productivity]*
3. **Cost structure transformation** from linear (headcount scales with volume) to sublinear (technology + oversight), reducing cost-per-claim from **$16.50** *[A2: current cost]* to target level *[A16: assumes ~$1.55 based on 90% reduction]*
4. **Preservation of judgment** for high-value/ambiguous cases *[A5: 15% of volume; U1: definition unknown]* while automating deterministic triage *[A17: assumes 85% automation target]*

The real problem is not "can AI do this?" but rather: **"How do we redesign the FNOL intake process to meet client-defined success criteria *[U12: unknown]* while balancing cost reduction, quality improvement, and risk mitigation?"**

### Explicit Constraints
- **Human oversight mandatory** for high-value or ambiguous claims *[A5: assumed 15% threshold; U1: definition unknown]*
- **System integration required**: Modern CRM (APIs), legacy policy admin (SOAP), document management system *[A12: integration effort estimates; U5: technical details unknown]*
- **No existing AI infrastructure**: Must build from zero (MLOps, monitoring, human-in-the-loop tooling) *[A11: 6-month timeline assumption]*
- **Regulatory environment**: Insurance claims processing subject to state/federal oversight *[U3: specific requirements unknown]*
- **Data availability**: No information provided on historical claim data quality, volume, or labeling *[U2: critical unknown]*

---

## 2. Assumptions

**A1: Average fully-loaded cost per specialist = $45/hour**
- *Reasoning*: Mid-size insurance company, back-office role requiring domain expertise. Industry benchmark for claims specialists is $55-65K salary + 35% benefits/overhead = ~$38-44/hour. Using $45 as midpoint.
- *Used in*: Problem Statement (labor cost), A2, Metric 3, Metric 5

**A2: Current daily labor cost = $4,950 (110 hours × $45)**
- *Reasoning*: Direct calculation from scenario data (300 claims × 22 min = 110 hours) and A1.
- *Used in*: Problem Statement (business cost), Metric 3 baseline

**A3: Routing error cost = 45 minutes of combined rework time**
- *Reasoning*: Misrouted claim requires: (1) original adjuster to recognize error (5 min), (2) re-route and document (5 min), (3) new adjuster to re-intake and context-switch (20 min), (4) specialist to update systems (15 min). Conservative estimate given context-switching penalties.
- *Used in*: Problem Statement (claimant impact, business inefficiency), Metric 5, U6

**A4: SLA breach cost = $25 per occurrence (soft cost)**
- *Reasoning*: No explicit penalty stated, but industry standard for consumer insurance includes regulatory reporting thresholds at 20% breach rate and reputational harm. Using $25 as blended average of direct penalties, customer service recovery costs, and churn risk.
- *Used in*: Problem Statement (penalty exposure), U3

**A5: High-value/ambiguous claim threshold = 15% of total volume**
- *Reasoning*: Client insists on human oversight for these cases. Typical distribution in property/casualty insurance: 70% straightforward (clear coverage, low value), 15% require judgment (coverage ambiguity, fraud indicators), 15% high-value (>$50K, bodily injury). Assuming 15% need human review.
- *Used in*: Problem Statement (solution requirements), Metric 3, Metric 4, Summary, U1

**A6: Task breakdown of 22-minute handling time:**
- Data extraction from unstructured text: 6 min
- Policy lookup and coverage validation: 8 min
- Severity triage and routing decision: 5 min
- System updates and claimant acknowledgment: 3 min
- *Reasoning*: Based on typical claims intake workflows. Policy validation is most time-consuming due to legacy system interaction. Data extraction from unstructured sources (email parsing, transcript review) is second-highest.
- *Used in*: A8 calculation

**A7: AI processing cost = $0.15 per claim**
- *Reasoning*: 
  - Document parsing (OCR/NLP): ~2,000 tokens input = $0.002 (GPT-4 Turbo pricing)
  - Classification/triage: ~500 tokens = $0.0005
  - Policy validation API calls: 2 calls × $0.01 = $0.02
  - Routing logic + acknowledgment generation: ~1,000 tokens = $0.01
  - Infrastructure (compute, storage, monitoring): $0.12 amortized per claim
  - **Total: ~$0.15/claim**
- *Used in*: Problem Statement (target cost), Metric 3

**A8: Human-in-the-loop review time for escalated claims = 12 minutes**
- *Reasoning*: AI handles data extraction and policy lookup (14 min saved from A6), but human still performs severity triage, routing decision, and validation. Reduces from 22 min to 12 min.
- *Used in*: Problem Statement (target cost), Metric 3

**A9: AI routing error rate = 3% (after training and validation)**
- *Reasoning*: Industry benchmarks for supervised classification tasks with domain-specific training data show 95-98% accuracy. Using conservative 97% (3% error rate) assuming 6-month tuning period.
- *Used in*: Problem Statement (target error rate), Metric 2, Metric 5, A15

**A10: AI can fully automate 85% of claims (inverse of A5)**
- *Reasoning*: If 15% require human oversight, 85% are candidates for full automation (straight-through processing).
- *Used in*: Problem Statement (automation target), Metric 3, Metric 4, Summary, A17

**A11: Implementation timeline = 6 months to production**
- *Reasoning*: No AI infrastructure exists. Requires: data pipeline build (2 mo), model training/validation (2 mo), integration with 3 systems (2 mo), parallel run (overlaps final month). Aggressive but achievable with dedicated FDE + engineering team.
- *Used in*: Problem Statement (constraints), Summary (ROI calculation)

**A12: System integration effort distribution:**
- CRM (modern API): 20 hours engineering
- Policy admin (SOAP): 60 hours engineering (legacy complexity)
- Document management: 30 hours engineering
- *Reasoning*: SOAP integration with legacy systems typically 3x more complex than REST APIs. Document management systems vary widely; assuming mid-complexity.
- *Used in*: Problem Statement (constraints), U5

**A13: Current adjuster productivity = 8 claims/adjuster/day**
- *Reasoning*: If 18% of claims are misrouted, adjusters lose ~45 min per error (A3). With typical caseload, this represents 10-15% productivity loss. Assuming 8 claims/day baseline, eliminating routing errors should recover 1.5-2 claims/day capacity.
- *Used in*: Problem Statement (business impact), Metric 5, U8

**A14: Target SLA compliance rate = 96% (≤4% breach rate)**
- *Reasoning*: Industry benchmark for high-performing claims operations; represents 87% reduction in breach rate from current 31%; likely threshold for avoiding regulatory scrutiny based on insurance industry standards. 4% allows for edge cases (system downtime, truly ambiguous claims) while meeting likely regulatory thresholds.
- *Risk if wrong*: Client may only need 85% (over-engineering solution) or may need 99% (under-scoped solution). Client may prioritize cost reduction over SLA improvement.
- *Used in*: Metric 1 target, Problem Statement

**A15: Target routing accuracy = 97% (3% error rate)**
- *Reasoning*: Aligned with A9 (AI capability assumption of 3% error rate); represents 83% error reduction from current 18%; balances automation benefits with realistic ML performance given training data constraints.
- *Risk if wrong*: Client may accept 90% accuracy if cost savings are high enough, or may require 99%+ for high-stakes claims. May need to segment by claim type (higher accuracy for high-value claims).
- *Used in*: Metric 2 target, Problem Statement

**A16: Target cost reduction = 91% (from $16.50 to $1.55/claim)**
- *Reasoning*: Necessary to achieve ROI payback within 12 months given estimated $500K implementation cost (A11); achievable with 85% automation rate (A10) and assumed cost structure (A7, A8). Represents aggressive but realistic target for AI automation of repetitive tasks.
- *Risk if wrong*: Client may be satisfied with 50-60% reduction if risk is lower, or may need 95% to justify organizational change and potential headcount reduction. Budget constraints unknown (U12).
- *Used in*: Metric 3 target, Problem Statement, Summary ROI calculation

**A17: Target straight-through processing rate = 85%**
- *Reasoning*: Inverse of A5 (15% human oversight requirement); represents theoretical maximum automation given client's constraint on human oversight for high-value/ambiguous claims. Assumes definition of "high-value/ambiguous" can be operationalized.
- *Risk if wrong*: Client may want to start at 50% and scale gradually (phased approach), or may push for 95% despite risks. Actual threshold depends on U1 (definition of oversight criteria).
- *Used in*: Metric 4 target, Problem Statement

**A18: Target adjuster productivity increase = 25% (from 8 to 10 claims/day)**
- *Reasoning*: Conservative estimate based on eliminating 83% of routing errors (from 18% to 3% via A9, A15); justifies investment by showing downstream value beyond direct cost savings. Calculation: 18% error rate × 20 min adjuster rework time (A3) = ~29 min/day lost; recovering this = ~0.6 claims/day. Additional quality improvements (better intake data) add ~0.9 claims/day = 1.5 total, rounded to 2 for 25% increase.
- *Risk if wrong*: Client may not care about adjuster productivity if adjusters are underutilized (U8), or may need 50% increase to justify adjuster headcount reduction. Productivity gains may not materialize if downstream bottlenecks exist.
- *Used in*: Metric 5 target, Problem Statement

---

## 3. Success Metrics

### Metric 1: SLA Compliance Rate
**Description**: Percentage of FNOL reports acknowledged within 2 hours of receipt

**Current Baseline**: 69% (100% - 31% breach rate from scenario)

**Target**: 96% (≤4% breach rate) *[A14]*

**Measurement Method**: 
- Timestamp delta between claim receipt (CRM log) and acknowledgment sent (outbound email/SMS log)
- Measured daily, reported weekly
- Segmented by: claim channel (email/phone/web), time of day, claim complexity

**Dependencies**: None for baseline (directly from scenario data)

**Assumption References**: 
- *[A14: 96% target is assumed based on industry benchmarks; client's actual requirement unknown per U12]*
- *[A4: informs business case for improvement]*
- *[U3: actual SLA penalties and regulatory requirements unknown]*
- *[U12: client's acceptable improvement level unknown]*

**Rationale**: 96% target *[A14]* represents 87% reduction in breach rate (from 31% to 4%). Allows for edge cases (system downtime, truly ambiguous claims requiring extended research) while meeting likely regulatory thresholds *[U3: actual requirements unknown]*. **However, client may have different priorities** *[U12]* **– they may accept 85% if cost savings are prioritized, or require 99% for regulatory reasons.**

---

### Metric 2: Routing Accuracy Rate
**Description**: Percentage of claims routed to correct adjuster on first attempt (no re-routing required)

**Current Baseline**: 82% (100% - 18% error rate from scenario)

**Target**: 97% *[A15]*

**Measurement Method**:
- Track re-routing events in CRM workflow logs
- Adjuster survey (weekly): "Did you receive any claims this week that should have gone to a different adjuster?"
- Root cause tagging for each routing error (model misclassification, data quality issue, edge case)

**Dependencies**: *[A9: assumes AI achieves 3% error rate after training]*

**Assumption References**: 
- *[A15: 97% target is assumed based on A9 AI capability; client's acceptable error rate unknown per U12]*
- *[A9: 3% AI error rate target based on industry ML benchmarks]*
- *[A3: quantifies impact of errors]*
- *[U2: data quality affects achievability]*
- *[U6: error type breakdown unknown]*
- *[U12: client's risk tolerance for routing errors unknown]*

**Rationale**: 97% accuracy *[A15]* represents 83% reduction in routing errors (from 18% to 3%). This is conservative for ML classification tasks but accounts for real-world data quality issues and edge cases not seen in training data. **However, client's actual tolerance for errors is unknown** *[U12]* **– they may accept 90% if cost-benefit favors it, or require 99%+ for high-value claims.**

---

### Metric 3: Cost Per Claim Processed
**Description**: Fully-loaded cost (labor + technology) to process one FNOL from receipt to acknowledgment

**Current Baseline**: $16.50 per claim
- Calculation: $4,950 daily labor cost *[A2]* ÷ 300 claims = $16.50

**Target**: $1.55 per claim (91% reduction) *[A16]*

**Measurement Method**:
- **Labor cost**: (# claims escalated to human × 12 min *[A8]* × $45/hour *[A1]* ÷ 60) ÷ total claims
- **Technology cost**: (AI processing cost per claim *[A7]* × total claims) + (monthly infrastructure cost ÷ 30 ÷ 300)
- Measured monthly, trended over 12 months post-launch

**Target Breakdown** *[A16]*:
- 85% of claims (255/day) fully automated *[A10, A17]*: 255 × $0.15 *[A7]* = $38.25/day
- 15% of claims (45/day) human review *[A5]*: 45 × 12 min *[A8]* × $45/hour *[A1]* ÷ 60 = $405/day
- Infrastructure (monitoring, MLOps, support): ~$450/month = $15/day *[embedded in A7]*
- **Total: $458.25/day ÷ 300 = $1.53/claim** (rounded to $1.55)

**Dependencies**: *[A1, A2, A5, A7, A8, A10, A16, A17]*

**Assumption References**: 
- *[A1: $45/hour labor cost]*
- *[A2: current baseline cost]*
- *[A5: 15% require human review]*
- *[A7: $0.15 AI processing cost]*
- *[A8: 12 min human review time]*
- *[A10: 85% automation rate]*
- *[A16: 91% cost reduction target is assumed; client's ROI requirement unknown per U12]*
- *[A17: 85% STP target]*
- *[U1: definition of human oversight affects A5 percentage]*
- *[U12: client's acceptable cost reduction and budget constraints unknown]*

**Rationale**: This is a *lagging indicator* of operational efficiency. 91% cost reduction *[A16]* is aggressive but achievable if automation rate reaches 85% *[A10, A17]*. Includes full technology stack cost, not just inference. **However, client's actual ROI requirements are unknown** *[U12]* **– they may be satisfied with 50-60% reduction, or may need 95% to justify headcount changes. Budget constraints and payback period requirements are undefined.**

---

### Metric 4: Straight-Through Processing Rate (STP)
**Description**: Percentage of claims processed end-to-end without human intervention

**Current Baseline**: 0% (all claims manually processed)

**Target**: 85% within 6 months of launch *[A17, A11]*

**Measurement Method**:
- Count claims where no human review event logged in workflow system
- Exclude claims flagged for human review by AI confidence thresholds
- Segmented by claim type, channel, and complexity *[U4: distribution unknown]*

**Dependencies**: *[A5: 15% require human oversight; A10: 85% automation target; A17: target STP rate]*

**Assumption References**: 
- *[A5: 15% threshold for human oversight]*
- *[A10: inverse calculation for automation potential]*
- *[A11: 6-month timeline to reach target]*
- *[A17: 85% STP target is assumed based on A5; client's desired automation level unknown per U12]*
- *[U1: definition of "high-value/ambiguous" affects achievability]*
- *[U4: claim distribution affects which 85% can be automated]*
- *[U12: client may prefer phased rollout starting at 50% STP]*

**Rationale**: This is a *leading indicator* of automation maturity. 85% STP rate *[A17]* is the theoretical maximum given *[A5: 15% must have human oversight]*. Tracks progress toward full automation potential. **However, client's risk appetite and rollout strategy are unknown** *[U12]* **– they may want to start at 30-50% STP and scale gradually, or may push for 95% despite risks. The 85% target assumes U1 can be resolved to clearly define automation boundaries.**

---

### Metric 5: Adjuster Productivity (Downstream Impact)
**Description**: Average number of claims fully resolved per adjuster per day

**Current Baseline**: 8 claims/adjuster/day *[A13]*

**Target**: 10 claims/adjuster/day (25% increase) *[A18]*

**Measurement Method**:
- Track claim closure events per adjuster in CRM
- Measure time-to-first-action after claim assignment (should decrease as routing errors drop from 18% to 3% *[A9, A15]*)
- Adjuster survey: "How much time do you spend per week on misrouted claims or intake errors?"

**Dependencies**: *[A13: baseline productivity; A3: rework time per error; A9: AI routing accuracy; A18: target productivity increase]*

**Assumption References**: 
- *[A13: 8 claims/day baseline is assumed]*
- *[A3: 45 min rework per routing error]*
- *[A9: 3% AI error rate vs. 18% current]*
- *[A15: 97% routing accuracy target]*
- *[A18: 25% productivity increase target is assumed; client's expectations unknown per U12]*
- *[U8: adjuster capacity and utilization unknown]*
- *[U12: client may not prioritize adjuster productivity if other constraints exist]*

**Rationale**: This is a *lagging indicator* measuring downstream business impact. Reducing routing errors from 18% to 3% *[A9, A15]* should materially improve adjuster efficiency by eliminating context-switching and rework *[A3: 45 min per error]*. 25% productivity gain *[A18]* is conservative given the 83% reduction in errors received.

**Calculation**: Current state: adjusters receive ~18% misrouted claims, each costing 20 min of their time *[A3: 45 min total, ~20 min adjuster portion]*. With 8 claims/day baseline *[A13]*, that's ~1.44 misrouted claims/day × 20 min = 29 min lost. Recovering this time = ~0.6 additional claims/day. With improved intake quality (better data from AI), estimate additional 0.9 claims/day capacity = 1.5 total increase, rounded to 2 for 25% improvement target.

**However, client's interest in adjuster productivity is unknown** *[U12]* **– if adjusters are already underutilized** *[U8]*, **this metric may not be valued. Client may prefer to focus solely on FNOL cost reduction rather than downstream impacts.**

---

## 4. Unknowns

### Critical Unknowns (Must Resolve Before Specification)

**U1: What defines "high-value or ambiguous" claims requiring human oversight?**
- Is it dollar threshold (e.g., >$50K)?
- Specific claim types (bodily injury, liability, fraud indicators)?
- Coverage ambiguity (policy exclusions, lapsed coverage)?
- Claimant characteristics (litigious history, VIP status)?
- **Risk if wrong**: Over-automate and miss cases requiring judgment (regulatory/legal exposure), or under-automate and fail to hit cost targets *[Metric 3, Metric 4]*.
- **Assumption affected**: *[A5: 15% threshold is placeholder; actual definition will change this percentage significantly]*
- **Metric impact**: 
  - *[Metric 3: changes labor cost calculation – if 30% need review instead of 15%, cost target of $1.55 becomes $2.85]*
  - *[Metric 4: changes STP target – if 30% need review, max STP is 70% not 85%]*
  - *[A17: target STP rate depends entirely on this definition]*
- **Discovery questions**: 
  - "What percentage of claims currently get escalated to senior adjusters or managers?"
  - "What are the top 5 reasons a claim requires extra scrutiny today?"
  - "Have you had regulatory issues or lawsuits related to claims handling in the past 3 years?"
  - "Can you provide examples of claims that should never be fully automated?"

---

**U2: What is the quality and availability of historical claims data?**
- How many historical FNOL reports exist with ground-truth labels (correct routing, severity, coverage determination)?
- Are phone transcripts already transcribed, or do they need ASR?
- What percentage of historical data has PII/PHI requiring redaction?
- What is the error rate in historical routing decisions (ground truth may be noisy)?
- Are claim outcomes tracked (to validate that routing was actually correct)?
- **Risk if wrong**: Insufficient training data = poor model performance, high error rates *[A9: 3% target unachievable]*, failed deployment.
- **Assumption affected**: 
  - *[A9: 3% error rate assumes adequate, clean training data with 10K+ labeled examples]*
  - *[A11: 6-month timeline assumes data is accessible within 4 weeks]*
- **Metric impact**: 
  - *[Metric 2: routing accuracy directly depends on training data quality – poor data may only achieve 85-90% accuracy]*
  - *[Metric 4: STP rate unachievable without good model performance]*
  - *[A15: 97% accuracy target may be unrealistic if data quality is poor]*
- **Discovery questions**:
  - "Can we access 10,000+ historical FNOL reports with final adjuster assignments and outcomes?"
  - "What formats are phone transcripts stored in? Are they human-transcribed or ASR?"
  - "What data governance approvals are needed to use historical claims for ML training?"
  - "How do you know if a historical routing decision was correct? Do you track re-routes?"

---

**U3: What are the actual SLA penalties or regulatory consequences of breaches?**
- Are there contractual penalties with customers (e.g., premium refunds)?
- State insurance department reporting thresholds?
- Impact on loss ratio or combined ratio (actuarial metrics)?
- Customer churn rate correlated with SLA breaches?
- **Risk if wrong**: Overestimate urgency and over-invest, or underestimate and fail to address root business problem.
- **Assumption affected**: 
  - *[A4: $25/breach is placeholder; actual penalties may be $0 or $500+]*
  - *[A14: 96% SLA target may be too aggressive or too lenient]*
- **Metric impact**: 
  - *[Metric 1: SLA compliance target of 96% may be unnecessary if no penalties exist, or insufficient if regulatory threshold is 98%]*
- **Discovery questions**:
  - "What happens when you breach the 2-hour SLA? Are there financial penalties?"
  - "Has the state insurance department flagged your SLA performance?"
  - "What percentage of customer complaints relate to slow claims response?"
  - "Do you track customer retention by SLA performance?"

---

**U4: What is the current distribution of claim types, channels, and complexity?**
- What % arrive via email vs. phone vs. web form?
- What % are auto vs. property vs. liability claims?
- What is the distribution of claim values ($0-5K, $5-25K, $25-100K, >$100K)?
- Which claim types have highest routing error rates today?
- **Risk if wrong**: Build solution optimized for wrong claim types, miss automation opportunities, or over-automate risky segments.
- **Assumption affected**: 
  - *[A5: 15% threshold may be wrong if claim distribution is heavily skewed – e.g., if 40% are high-value liability claims]*
  - *[A6: task breakdown may vary significantly by channel – phone transcripts take longer than web forms]*
- **Metric impact**: 
  - *[Metric 4: STP rate target may need segmentation by claim type – e.g., 95% for auto, 60% for liability]*
  - *[Metric 1: SLA performance may vary by channel – email may be easier to process in 2 hours than phone]*
- **Discovery questions**:
  - "Can you provide a breakdown of last month's 300 daily claims by type and channel?"
  - "What percentage of claims are under $10K? Under $50K?"
  - "Which claim types have the highest routing error rates?"
  - "Do different claim types have different SLA requirements?"

---

**U5: What is the technical architecture and data model of the three systems?**
- CRM: Which vendor? What claim fields are exposed via API? Rate limits?
- Policy admin system: What SOAP operations are available? Is policy coverage data real-time or batch-updated? Latency?
- Document management: Can it accept programmatic uploads? What metadata fields exist? Storage limits?
- Are there authentication/authorization requirements (OAuth, SAML, etc.)?
- **Risk if wrong**: Discover integration blockers mid-project, causing delays or requiring expensive workarounds.
- **Assumption affected**: 
  - *[A12: integration effort estimates may be 2-5x off]*
  - *[A11: 6-month timeline assumes integrations are feasible; could extend to 12 months if legacy system has undocumented limitations]*
- **Metric impact**: 
  - *[Metric 1: SLA compliance depends on real-time policy lookups – if legacy system has 30-second latency, may be impossible to meet 2-hour SLA at scale]*
  - *[All metrics depend on successful integration – project fails if systems cannot be integrated]*
- **Discovery questions**:
  - "Can we get API documentation and sandbox access for all three systems?"
  - "What is the latency of policy lookups in the legacy system? Can it handle 300 requests/day?"
  - "Are there rate limits or throttling on any of the APIs?"
  - "Who owns each system, and what is the approval process for integration work?"

---

**U12: What improvement levels would justify the investment in the client's view?**
- What ROI threshold or payback period does leadership require?
- Are they optimizing for cost reduction, customer satisfaction, regulatory compliance, or scalability?
- What is their risk tolerance for automation errors?
- What is the budget for this initiative?
- Are there organizational constraints (e.g., no-layoff policy, union agreements)?
- What would make this project a "success" vs. "failure" in 12 months?
- **Risk if wrong**: Build a solution that achieves 90% cost reduction but client only needed 50% (over-engineering), or vice versa (under-delivery). Misalign on priorities (optimize for cost when client cares about compliance).
- **Assumption affected**: 
  - *[A14: SLA target of 96% may be unnecessary or insufficient]*
  - *[A15: Routing accuracy target of 97% may be too aggressive or too lenient]*
  - *[A16: Cost reduction target of 91% may not align with client's ROI requirements]*
  - *[A17: STP target of 85% may be too aggressive for risk-averse client]*
  - *[A18: Adjuster productivity may not be a priority at all]*
- **Metric impact**: 
  - *[ALL METRICS: Targets are assumptions, not requirements. Client may have completely different priorities.]*
  - *[Metric 3: Client may be satisfied with 50% cost reduction if it reduces risk]*
  - *[Metric 1: Client may need 99% SLA compliance for regulatory reasons, making 96% target inadequate]*
  - *[Metric 5: Client may not care about adjuster productivity if they're planning to expand the team anyway]*
- **Discovery questions**:
  - "What would make this project a success in your view? Cost savings? Faster response times? Fewer errors?"
  - "What's your budget for this initiative, and what ROI do you need to justify it?"
  - "If we could reduce costs by 60% but SLA compliance only improved to 85%, would that be acceptable?"
  - "Are there any non-negotiable requirements? (e.g., 'must achieve 95% SLA compliance for regulatory reasons')"
  - "What happens to the 12 specialists if we automate 85% of the work? Redeployment? Retraining? Reduction?"
  - "On a scale of 1-10, how risk-averse is leadership regarding AI making routing decisions?"

---

### Important Unknowns (High Impact, Can Be Deferred Slightly)

**U6: What is the current error rate breakdown by error type?**
- Of the 18% routing errors, how many are due to: misclassified claim type, incorrect adjuster specialization, wrong geographic assignment, data entry errors?
- **Assumption affected**: 
  - *[A3: 45 min rework time may vary by error type – wrong adjuster specialization may take 60 min, wrong geography may take 15 min]*
  - *[A9: AI may excel at some error types (claim type classification) but not others (nuanced specialization matching)]*
- **Metric impact**: 
  - *[Metric 2: routing accuracy improvement may be uneven across error types – may achieve 99% on claim type but only 90% on specialization]*
- **Discovery**: Error log analysis or specialist interviews.
- **Discovery questions**:
  - "Can you categorize last month's routing errors by root cause?"
  - "Which types of routing errors are most costly or time-consuming to fix?"

---

**U7: What is the staff's technical proficiency and change readiness?**
- Will the 12 specialists be redeployed, reduced, or retrained as AI reviewers?
- What is leadership's appetite for workforce restructuring?
- Have there been previous automation initiatives? How did they go?
- What is the union situation (if applicable)?
- **Assumption affected**: 
  - *[A8: 12 min human review time assumes specialists can adapt to new workflow – may be 20 min if they struggle with new tools]*
  - *[A1: labor cost may change if roles are restructured or if specialists are replaced with lower-cost reviewers]*
- **Metric impact**: 
  - *[Metric 3: cost savings may be lower if staff cannot be redeployed – may only achieve 60% reduction instead of 91%]*
  - *[Metric 4: STP rate may be lower if staff resist automation and flag more claims for review than necessary]*
- **Discovery**: HR discussion, change management assessment.
- **Discovery questions**:
  - "What is the plan for the 12 specialists if we automate 85% of their work?"
  - "Have you done workforce automation projects before? What lessons did you learn?"
  - "How do the specialists feel about AI? Have they been consulted?"

---

**U8: What is the current adjuster utilization and capacity?**
- Are adjusters at full capacity, or is there slack to absorb higher-quality claim flow?
- What is the adjuster-to-claim ratio?
- Are adjusters complaining about workload, or is there capacity?
- **Assumption affected**: 
  - *[A13: 8 claims/day baseline may be wrong – could be 5 or 12]*
  - *[A18: productivity gains may not materialize if adjusters are already underutilized – can't increase from 8 to 10 if they're only doing 6 today]*
- **Metric impact**: 
  - *[Metric 5: 25% productivity increase may not be realized if adjusters don't have additional capacity to absorb more claims]*
  - *[May need to remove Metric 5 entirely if adjuster productivity is not a constraint]*
- **Discovery**: Adjuster time-tracking data, manager interviews.
- **Discovery questions**:
  - "Are adjusters at full capacity today, or is there slack?"
  - "What is the average caseload per adjuster?"
  - "Do adjusters complain about being overwhelmed, or do they have capacity for more work?"

---

### Lower-Priority Unknowns (Can Be Resolved During Build)

**U9: What is the variance in handling time across the 12 specialists?**
- Is 22 min an average with high variance (some at 10 min, others at 40 min), or is it consistent?
- Are there "super-specialists" who handle complex claims faster?
- **Assumption affected**: 
  - *[A6: task breakdown may vary by specialist skill level]*
  - *[A2: daily cost calculation assumes uniform productivity]*
- **Metric impact**: 
  - *[Metric 3: cost baseline may be understated if high performers are retained and low performers exit]*
- **Discovery**: Time-tracking analysis, specialist interviews.

---

**U10: What compliance or audit requirements exist for AI decision-making?**
- Do you need explainability for every routing decision?
- Are there model governance or fairness requirements?
- Do state regulators have AI-specific requirements for insurance claims?
- **Assumption affected**: 
  - *[A7: AI processing cost may increase if explainability tools required (e.g., LIME, SHAP) – could be $0.25/claim instead of $0.15]*
  - *[A11: timeline may extend if compliance reviews needed – could be 9 months instead of 6]*
- **Metric impact**: 
  - *[Metric 3: cost target may be higher – $2.00/claim instead of $1.55]*
  - *[Metric 4: STP rate may be lower if explainability requires human review – 70% instead of 85%]*
- **Discovery**: Legal/compliance review, regulatory research.

---

**U11: What is the customer communication preference?**
- Do claimants prefer email, SMS, or phone acknowledgment?
- Are there accessibility requirements (e.g., Spanish language, TTY)?
- **Assumption affected**: 
  - *[A7: AI processing cost varies slightly by channel – SMS is cheaper than email with attachments]*
- **Metric impact**: 
  - *[Metric 1: SLA measurement method may need to account for multi-channel acknowledgments]*
- **Discovery**: Customer survey or CRM data analysis.

---

## Summary

**The core problem is not "Can AI do this?" but rather "How do we re-engineer FNOL intake to meet client-defined success criteria** *[U12: unknown]* **while balancing cost reduction, quality improvement, and risk mitigation?"**

**Based on assumed targets** *[A14-A18]*, success would mean:
- SLA compliance: 96% vs. 69% *[Metric 1, A14]*
- Cost-per-claim: $1.55 vs. $16.50 (91% reduction) *[Metric 3, A16]*
- Routing accuracy: 97% vs. 82% *[Metric 2, A15]*
- Straight-through processing: 85% vs. 0% *[Metric 4, A17]*
- Adjuster productivity: 10 vs. 8 claims/day (25% increase) *[Metric 5, A18]*

**However, these targets are assumptions, not requirements.** *[U12]* **The client may have completely different priorities, budget constraints, or risk tolerances.**

Success depends on:
1. **Resolving U12 FIRST** (client's actual success criteria) before committing to any specific targets
2. Resolving **U1-U5** (critical unknowns) in discovery before specification
3. Achieving assumed **85% straight-through processing** *[A17]* for deterministic claims (depends on U1)
4. Reducing **routing errors to 3%** *[A9, A15]* through ML classification (depends on U2)
5. Building **human-in-the-loop tooling** for assumed 15% of claims requiring judgment *[A5]* (depends on U1)

**Business case (if assumptions hold)**:

**Annual Savings Calculation** *[A1, A2, A7, A8, A10, A16]*:
- Current annual cost: $4,950/day × 250 business days = **$1,237,500**
- Target annual cost: $458.25/day × 250 business days = **$114,563**
- **Gross annual savings: $1,122,937**
- Less: AI infrastructure and operations: ~$200,000/year *[A7: embedded assumption]*
- **Net annual savings: ~$923,000**

**ROI Calculation** *[A11]*:
- Implementation cost estimate: $500K (6 months *[A11]* × blended team cost of ~$85K/month for FDE + 2 engineers + PM)
- **Payback period: 6.5 months** ($500K ÷ $923K × 12)

**BUT: Client's actual ROI requirements are unknown** *[U12]*. **They may need 12-month payback, or 36-month. They may have a $200K budget, or $2M. They may prioritize risk reduction over cost savings.**

**Key risks to business case**:
- *[U12]*: **Client's actual success criteria differ from assumed targets** – e.g., they only need 50% cost reduction, making aggressive automation unnecessary
- *[U2]*: Insufficient training data makes *[A9: 3% error rate]* unachievable, requiring more human review than *[A5: 15%]*, increasing costs to $3-4/claim instead of $1.55
- *[U1]*: Actual high-value threshold is 30% not 15%, cutting automation rate *[A10]* in half and doubling labor costs to $3.10/claim
- *[U5]*: Legacy system integration takes 12 months not 6 *[A11]*, delaying ROI and increasing implementation cost to $1M
- *[U7]*: Staff resistance or inability to adapt to new workflow *[A8: 12 min review time]* increases labor costs by 50%
- *[U3]*: SLA penalties are actually $0, making *[A14: 96% target]* over-engineering

**Confidence level in success metrics (assuming targets are correct per U12)**:
- *[Metric 1: SLA Compliance]* - **High confidence** (AI processing is deterministic and fast; main risk is system downtime from U5)
- *[Metric 2: Routing Accuracy]* - **Medium confidence** (depends heavily on *[U2: data quality]* and *[U4: claim distribution]*)
- *[Metric 3: Cost Per Claim]* - **Medium confidence** (depends on *[A5/U1: human oversight threshold]* and *[U7: staff adaptability]*)
- *[Metric 4: STP Rate]* - **Medium confidence** (directly tied to *[U1: definition of automation boundary]*)
- *[Metric 5: Adjuster Productivity]* - **Low confidence** (depends on *[U8: adjuster capacity]* and downstream factors outside FNOL scope)

**CRITICAL NEXT STEP: Discovery session with client to resolve U12 before proceeding with any technical specification or architecture design.**

---

---

# 2. Delegation Analysis

# Delegation Analysis - Insurance Claims FNOL Processing

## Table of Contents
- [Executive Summary](#executive-summary-fnol-processing-delegation-analysis)
  - [Overview](#overview)
  - [Delegation Distribution Summary](#delegation-distribution-summary)
  - [Key Findings](#key-findings)
    - [1. High-Volume, Low-Risk Tasks Fully Automated](#1-high-volume-low-risk-tasks-are-fully-automated-73-of-work)
    - [2. Judgment-Intensive Tasks Hybrid Approach](#2-judgment-intensive-tasks-use-hybrid-approach-18-of-work)
    - [3. Non-Standard Cases Remain Human-Led](#3-non-standard-cases-remain-human-led-7-of-work)
    - [4. Quality Assurance Automated](#4-quality-assurance-is-automated-monitoring-2-of-work)
  - [Critical Dependencies & Sensitivities](#critical-dependencies--sensitivities)
  - [Cost & Time Comparison](#cost--time-comparison)
  - [Boundary Decision Framework](#boundary-decision-framework)
  - [Implementation Phasing](#implementation-phasing-recommendation)
  - [Next Steps](#next-steps)
  - [Conclusion](#conclusion)
- [Detailed Delegation Analysis](#detailed-delegation-analysis-fnol-processing-automation)
  - [1. Delegation Analysis by Work Component](#1-delegation-analysis-by-work-component)
  - [2. Key Assumptions](#2-key-assumptions)
  - [3. Component Details](#component-details)
  - [4. Boundary Justification & Challenges](#4-boundary-justification--challenges)
  - [5. Sensitivity Analysis](#5-sensitivity-analysis)

---

# Executive Summary: FNOL Processing Delegation Analysis

## Overview

This analysis determines which components of the First Notice of Loss (FNOL) intake process should be automated, which require human oversight, and which must remain human-led. The current manual process consumes **110 staff-hours per day** *[scenario: 300 claims × 22 min]* with an **18% routing error rate** and **31% SLA breach rate**. 

The proposed delegation model reduces human workload to **10.9 hours per day (90% reduction)** while improving quality and compliance, assuming baseline assumptions hold.

---

## Delegation Distribution Summary

| Delegation Category | % of Work (by time) | % of Claims | Daily Human Time | Key Components |
|---------------------|---------------------|-------------|------------------|----------------|
| **Fully Agentic** | 73% | 85% | 0.9 min/claim | Data validation, policy lookup, acknowledgment, system updates |
| **Agent-Led with Human Oversight** | 18% | 15% | 9.4 min/claim | Data extraction, coverage determination, severity triage, routing (for high-value/ambiguous claims) |
| **Human-Led with Agent Support** | 7% | 8% | 15 min/claim | Exception handling |
| **Human Only** | 2% | 0% | 0.15 min/claim | Quality assurance oversight |

**Weighted Average**: **2.18 minutes human time per claim** (vs. 22 minutes current = **90% reduction**)

**Total Daily Human Workload**: **10.9 hours** (vs. 110 hours current)

---

## Key Findings

### 1. High-Volume, Low-Risk Tasks Are Fully Automated (73% of work)

**Components**:
- **Data Validation** (1 min/claim): Rule-based checks on extracted data (policy number format, date ranges, required fields). Zero ambiguity, zero risk. *[A25: 2 sec AI processing time]*
- **Policy Lookup** (8 min/claim): Automated SOAP API calls to legacy system. Deterministic retrieval, no judgment required. *[A26: 10 sec AI processing time; U5: assumes acceptable system latency]*
- **Claimant Acknowledgment** (2 min/claim): Template-based message generation with variable substitution. Error cost is minimal (5 min customer service call *[A35]*). *[A36: 5 sec AI processing time]*
- **System Updates** (1 min/claim): Automated CRM/document management API calls. Deterministic data entry. *[A37: 8 sec AI processing time]*

**Rationale**: These tasks have **very high codifiability** (deterministic rules or simple API calls), **low error cost** (<$50 per error), and **high volume** (combined 3,600 min/day = 60 hours). Automation ROI is immediate and risk-free.

**Total AI processing time for fully agentic components**: **63 seconds per claim** (vs. 22 minutes manual)

---

### 2. Judgment-Intensive Tasks Use Hybrid Approach (18% of work)

**The 85/15 Split**: **85% of claims** *[A10]* are straightforward and can be fully automated. **15% of claims** *[A5]* are high-value or ambiguous and require human oversight. This split is the **primary cost driver**.

**Components with hybrid delegation**:

#### Data Extraction (6 min/claim manual → 15 sec AI *[A23]*)
- **Fully Agentic for 85%**: AI extracts structured fields from unstructured text (email, phone transcript, web form) using NLP.
- **Agent-Led for 15%**: Human validates extraction for high-value claims (>$100K *[A21]*) or when AI confidence <90% *[A24]* on critical fields (policy number, claimant name).
- **Risk**: Extraction errors cost 8 min rework *[A22]*. For high-value claims, downstream coverage errors cost $2,000 avg *[A27]*.

#### Coverage Determination (2 min/claim manual → 8 sec AI *[A28]*)
- **Fully Agentic for 85%**: Rule-based logic for straightforward cases (claim type matches coverage, loss date in policy period, no exclusions).
- **Agent-Led for 15%**: Human reviews ambiguous cases (complex exclusions, policy language interpretation, fraud indicators ≥3 *[A29]*).
- **Risk**: Coverage errors cost $2,000 avg *[A27]* (wrongly denied claim → lawsuit; wrongly approved claim → fraudulent payout). Human oversight for 15% of claims reduces expected error cost from $60/claim to $52.50/claim, **saving $600K/year**.

#### Severity/Complexity Triage (5 min/claim manual → 10 sec AI *[A30]* + 2 min human review for 15% *[A31]*)
- **Agent-Led for all claims**: AI triages all 300 claims, flags 15% for human review based on claim value (>$100K *[A21]*), fraud indicators *[A29]*, AI confidence (<85% *[A20]*), or policy ambiguity.
- **Human reviews only flagged claims**: 2 min per flagged claim *[A31]* (vs. 5 min full manual triage). Human validates AI's triage decision and makes final oversight determination.
- **Risk**: This is the **gatekeeper** for downstream automation. Over-triage (flag too many) defeats automation purpose. Under-triage (miss high-risk claims) exposes company to regulatory/legal risk.

#### Adjuster Routing (3 min/claim manual *[A19]* → 3 sec AI *[A33]*)
- **Fully Agentic for 85%**: ML model assigns claims to adjusters based on claim type, geography, specialization, and workload balancing.
- **Agent-Led for 15%**: Human approves routing for high-value/ambiguous claims to ensure senior adjuster assignment.
- **Risk**: Routing errors cost 45 min rework *[A3]*. AI at 3% error rate *[A9]* is **83% improvement** over 18% human baseline (scenario). Current error cost: 18% × 45 min × 300 claims = **40.5 hours/day lost to rework**. Future error cost: 3% × 45 min × 300 claims = **6.8 hours/day** (saves 33.7 hours/day).

---

### 3. Non-Standard Cases Remain Human-Led (7% of work)

**Exception Handling** (8% of claims *[A38]*, 15 min per exception):
- **Human-Led with Agent Support**: AI provides context and suggested actions, but human investigates and resolves.
- **Examples**: Missing policy data, claimant cannot be reached, coverage dispute, system downtime, fraud investigation.
- **Rationale**: Exceptions are **by definition non-standard** (cannot be codified). Low volume (24 claims/day) makes automation investment unjustified. Requires problem-solving, judgment, empathy.

---

### 4. Quality Assurance Is Automated Monitoring (2% of work)

**QA** (45 min/day aggregate *[A39]*):
- **Agent-Led with Human Oversight**: AI monitors 100% of claims in real-time (routing accuracy, SLA compliance, data quality, AI confidence distribution). Human reviews daily dashboard and investigates anomalies.
- **Rationale**: Automated monitoring scales to 300 claims/day at negligible cost *[A40: 2 sec per claim]*. Human judgment needed for trend analysis and corrective action decisions.

---

## Critical Dependencies & Sensitivities

### Dependency 1: Definition of "High-Value/Ambiguous" Claims (U1)

**Current assumption**: 15% of claims *[A5]* require human oversight, defined as claim value >$100K *[A21]* OR fraud indicators ≥3 *[A29]* OR AI confidence <85% *[A20]*.

**Sensitivity**:
- **If threshold is $50K instead of $100K**: Human oversight increases to **25%** → cost per claim increases from **$1.55 to $2.50** *[A16, Metric 3]* → daily human time increases from **10.9 hours to 18 hours**.
- **If threshold is $250K instead of $100K**: Human oversight decreases to **8%** → cost per claim decreases from **$1.55 to $1.05** → daily human time decreases from **10.9 hours to 6.5 hours**.

**Impact**: **U1 is the single most important unknown**. A 2x change in threshold changes automation rate from 75% to 85% to 92%, and cost per claim by 60%.

**Action Required**: **Must resolve U1 in discovery (week 1)** before finalizing delegation boundaries.

---

### Dependency 2: Historical Data Quality (U2)

**Current assumption**: Historical claims data *[U2]* is sufficient to train ML models for routing and coverage determination, achieving 3% error rate *[A9]*.

**Sensitivity**:
- **If data quality is poor** (insufficient labeled examples, noisy labels): Must use rule-based systems with 10% error rate *[A32]* → human oversight increases to **30%** → cost per claim increases from **$1.55 to $3.20**.
- **If data quality is excellent** (20K+ clean labeled examples): ML achieves 2% error rate → human oversight decreases to **10%** → cost per claim decreases from **$1.55 to $1.20**.

**Impact**: Poor data quality doesn't kill the project (rule-based systems still improve on 18% human baseline), but reduces ROI from 91% cost reduction *[A16]* to ~80% cost reduction.

**Action Required**: **Assess data quality in weeks 1-2** (data discovery sprint) to adjust targets.

---

### Dependency 3: Client's Risk Tolerance (U12)

**Current assumption**: Client accepts 3% error rate *[A9]* on routing and coverage determination, with human oversight for 15% of claims *[A5]*.

**Sensitivity**:
- **If client is risk-averse** (requires 99%+ accuracy): Human oversight increases to **40-50%** → cost per claim increases from **$1.55 to $5-6** → daily human time increases from **10.9 hours to 35-40 hours** → ROI payback extends from **6.5 months to 18-24 months**.
- **If client is risk-tolerant** (accepts 5-8% error rate): Human oversight decreases to **5-8%** → cost per claim decreases from **$1.55 to $0.80-1.00** → daily human time decreases from **10.9 hours to 4-5 hours** → ROI payback shortens from **6.5 months to 3-4 months**.

**Impact**: **U12 determines the optimal automation/oversight balance**. Risk-averse client → 50% automation. Risk-tolerant client → 95% automation.

**Action Required**: **Resolve U12 in discovery (week 1)** through executive interviews to understand ROI requirements, budget constraints, and risk appetite.

---

### Dependency 4: Legacy System Performance (U5)

**Current assumption**: Legacy policy admin system has acceptable latency (10 sec per lookup *[A26]*) and availability (99%+).

**Sensitivity**:
- **If latency is 60+ sec**: Cannot meet 2-hour SLA without parallel processing (lookup 10 claims simultaneously) → requires infrastructure investment (connection pooling, rate limit management).
- **If availability is 95%** (36 min downtime/day): 7.5 claims/day cannot be processed during downtime → SLA breach rate increases from 4% target *[A14, Metric 1]* to 6.5% (still improvement from 31% baseline).

**Impact**: **U5 affects implementation feasibility, not delegation decisions**. Even with poor legacy system performance, automation is still beneficial (AI handles other components while human performs manual policy lookup during outages).

**Action Required**: **Assess U5 in weeks 2-3** (technical discovery with IT team) to plan infrastructure (parallel processing, caching, fallback workflows).

---

## Cost & Time Comparison

| Metric | Current State | Future State (Baseline Assumptions) | Improvement |
|--------|---------------|-------------------------------------|-------------|
| **Daily Human Time** | 110 hours | 10.9 hours | **90% reduction** |
| **Cost per Claim** | $16.50 *[A2]* | $1.55 *[A16, Metric 3]* | **91% reduction** |
| **Routing Error Rate** | 18% (scenario) | 3% *[A9, A15, Metric 2]* | **83% reduction** |
| **SLA Compliance** | 69% (scenario) | 96% *[A14, Metric 1]* | **87% reduction in breaches** |
| **Processing Time per Claim** | 22 min manual | 63 sec AI + 2.18 min human avg | **90% reduction** |

**Annual Cost Savings** (if baseline assumptions hold):
- Current: $4,950/day × 250 days = **$1,237,500/year** *[A2]*
- Future: $458/day × 250 days = **$114,563/year**
- **Net Savings: ~$923,000/year** (after $200K AI infrastructure cost *[A7]*)
- **ROI Payback: 6.5 months** (assuming $500K implementation cost *[A11]*)

---

## Risk Mitigation: The 85/15 Split Protects Against High-Stakes Errors

**Why not 100% automation?**

The 15% human oversight *[A5]* is **insurance against high-cost errors**:

1. **Coverage determination errors** cost $2,000 avg *[A27]*. Full automation (3% error rate *[A9]*) would cost $18K/day in errors. Human oversight for 15% of claims reduces error cost to $15.6K/day, **saving $2.4K/day = $600K/year**.

2. **Routing errors** cost 45 min rework *[A3]*. AI at 3% error rate *[A9]* saves 33.7 hours/day vs. 18% human baseline, **worth $1,517/day = $379K/year** *[A1: $45/hour labor cost]*.

3. **Regulatory/legal exposure** *[U3: actual penalties unknown]* from coverage errors is potentially catastrophic (lawsuits, regulatory sanctions, reputational harm). Human oversight for ambiguous cases provides **defensibility** ("we had a human review this decision").

4. **The 85/15 split is optimized for ROI**: 
   - 100% automation → saves $1.1M/year but exposes $600K/year in error costs = **net $500K/year**.
   - 85% automation + 15% oversight → saves $923K/year with minimal error exposure = **net $900K/year**.
   - **The 15% human oversight costs $177K/year but prevents $600K/year in errors** (3.4x ROI on oversight).

---

## Boundary Decision Framework

**Every delegation decision is based on quantified risk vs. benefit, not arbitrary judgment**:

| Component | Codifiability | Error Cost | Volume (min/day) | Delegation Decision | Rationale |
|-----------|---------------|-----------|------------------|---------------------|-----------|
| Data Validation | Very High | Very Low (<$10) | 300 | **Fully Agentic** | Deterministic rules, zero risk |
| Policy Lookup | Very High | Low ($0) | 2,400 | **Fully Agentic** | API call, no judgment |
| Acknowledgment | Very High | Very Low ($5 *[A35]*) | 600 | **Fully Agentic** | Template generation, minimal risk |
| System Updates | Very High | Low ($0) | 300 | **Fully Agentic** | API calls, deterministic |
| Data Extraction | Medium-High | Medium ($8 min rework *[A22]*) | 1,800 | **Hybrid** (85/15) | High volume justifies automation; high-value claims need validation |
| Coverage Determination | Medium | High ($2,000 *[A27]*) | 600 | **Hybrid** (85/15) | Error cost justifies oversight for ambiguous cases |
| Severity Triage | Medium | High (gatekeeper) | 1,500 | **Hybrid** (85/15) | Critical decision point, requires judgment for edge cases |
| Adjuster Routing | Medium-High | Medium ($34 *[A3, A1]*) | 900 | **Hybrid** (85/15) | High volume + high error cost justifies automation with oversight |
| Exception Handling | Low | High (varies) | 225-450 | **Human-Led** | Non-standard, low volume, requires judgment |
| Quality Assurance | Medium-High | Medium | 45 min/day | **Agent-Led** | Automated monitoring + human trend analysis |

---

## Implementation Phasing Recommendation

**Phase 1 (Months 1-2): Low-Risk, High-ROI Components**
- Data Validation (Fully Agentic) *[A25]*
- Claimant Acknowledgment (Fully Agentic) *[A36]*
- System Updates (Fully Agentic) *[A37]*
- **Impact**: 10% time savings (3 min per claim), zero risk, builds confidence

**Phase 2 (Months 3-4): High-Volume Components**
- Policy Lookup (Fully Agentic) *[A26]* – requires U5 resolution (legacy system integration)
- Data Extraction (Hybrid 85/15) *[A23, A24]* – requires U2 resolution (data quality assessment)
- **Impact**: 50% time savings (14 min per claim), moderate risk, high ROI

**Phase 3 (Months 5-6): Judgment-Intensive Components**
- Coverage Determination (Hybrid 85/15) *[A28, A27]* – requires U1 resolution (high-value definition)
- Severity Triage (Hybrid 85/15) *[A30, A31]* – requires U12 resolution (risk tolerance)
- Adjuster Routing (Hybrid 85/15) *[A33, A9]* – requires U2 resolution (training data quality)
- Quality Assurance (Agent-Led) *[A39, A40]*
- **Impact**: 90% time savings (full 22 min → 2.18 min), highest risk, requires careful tuning

**Exception Handling** (Human-Led *[A38]*) remains unchanged throughout all phases.

---

## Next Steps

### Week 1: Critical Discovery
1. **Resolve U1** (high-value/ambiguous definition): Interview claims managers, review historical escalation patterns, define objective criteria (claim value threshold, fraud indicators, policy complexity flags).
2. **Resolve U12** (risk tolerance): Executive interviews to understand ROI requirements, budget constraints, error tolerance, regulatory concerns.
3. **Assess U2** (data quality): Audit historical claims data (volume, labeling, completeness, diversity).

### Week 2-3: Technical Discovery
4. **Assess U5** (legacy system integration): API documentation review, latency testing, availability analysis, integration complexity estimation.
5. **Validate assumptions A20, A21, A24** (confidence thresholds, value thresholds): Workshop with specialists to calibrate thresholds.

### Week 4-6: Prototype & Pilot
6. **Prototype Phase 1 components** (validation, acknowledgment, system updates): Validate time estimates *[A25, A36, A37]*.
7. **Pilot with 10% of claims** (30/day) for 2 weeks: Measure actual automation rate, error rate, human review time, SLA compliance.
8. **Adjust delegation boundaries** based on pilot results before full rollout.

---

## Conclusion

The proposed delegation model achieves **90% reduction in human workload** (110 hours → 10.9 hours/day) while **improving quality** (routing errors from 18% → 3%, SLA compliance from 69% → 96%) through a **risk-calibrated hybrid approach**:

- **73% of work is fully automated** (high-codifiability, low-risk tasks)
- **18% uses AI with human oversight** (judgment-intensive tasks for 15% of claims *[A5]*)
- **7% remains human-led** (exceptions and edge cases)

**The 85/15 split** *[A10, A5]* **is the key design decision**: it balances aggressive automation (85% of claims) with prudent risk management (15% human oversight), optimizing for both cost reduction ($923K/year savings) and error prevention ($600K/year in avoided error costs).

**Success depends on resolving three critical unknowns** *[U1, U2, U12]* **in discovery (weeks 1-2)** to validate or adjust the 85/15 split and associated cost/quality targets.# Delegation Analysis

---
---

# Detailed Delegation Analysis: FNOL Processing Automation

## 1. Delegation Analysis by Work Component

---

### Component 1: Claim Intake - Data Extraction

**Current State**: Specialist manually reads unstructured text from email body, phone transcript, or web form. Extracts key fields: claimant name, policy number, date of loss, loss description, contact info. Takes 6 minutes per claim *[A6]*. No standardization across channels.

**Delegation Decision**: **Fully Agentic** (for 85% of claims *[A10]*); **Agent-Led with Human Oversight** (for 15% flagged as high-value/ambiguous *[A5]*)

**Rationale**:
- **Codifiability**: HIGH. Named entity recognition (NER) and information extraction are well-established NLP tasks. Can extract structured fields from unstructured text with 90-95% accuracy for standard formats. Edge cases: handwritten notes, heavily redacted documents, non-English text.
- **Risk Profile**: LOW-MEDIUM. Extraction errors propagate downstream but are usually caught in validation step. Incorrect policy number → lookup failure (caught immediately). Incorrect loss date → potential coverage issue (caught in coverage determination). Cost of error: 5-10 min rework *[A22: new assumption below]*.
- **Data Availability**: DEPENDENT on *[U2]*. Need historical FNOL reports with ground-truth extracted fields. If unavailable, can use few-shot learning with GPT-4 (50-100 examples) but accuracy drops to 85-90%.
- **Human Expertise Required**: LOW. Extraction is mechanical pattern-matching. No domain judgment needed except for ambiguous handwriting or context-dependent abbreviations.
- **Volume/Economics**: 300 claims/day × 6 min = 1,800 min/day (30 hours). Highest time consumer in intake process. High ROI for automation.

**Assumption/Unknown References**: *[A5, A6, A10, U2, U4]*

**New Assumptions**:
- **A22**: Data extraction error rework time = 8 minutes
  - *Reasoning*: Specialist must re-read original document, correct extracted fields, validate against policy system. Less than full 22-min intake (only re-doing extraction, not full workflow). Conservative estimate.
  - *Used in*: Risk calculation for this component
  - *Risk if wrong*: If rework takes 15+ min, may justify human oversight for more claims.

- **A23**: AI data extraction time = 15 seconds per claim
  - *Reasoning*: LLM inference (2,000 tokens input, 200 tokens output) = ~3-5 sec. OCR for scanned documents = ~5-10 sec. Total ~15 sec conservative estimate.
  - *Used in*: Time calculations, SLA compliance (Metric 1)

**Boundary Conditions**:
- IF document is handwritten or low-quality scan → **Agent-Led with Human Oversight** (AI extracts, human validates before proceeding)
- IF AI confidence on any critical field (policy number, claimant name) <90% *[A24: new assumption]* → **Agent-Led with Human Oversight**
- IF claim flagged as high-value/ambiguous *[A5, U1]* → **Agent-Led with Human Oversight** (human validates extraction before workflow continues)

**New Assumptions for Boundary Conditions**:
- **A24**: AI confidence threshold for critical field extraction = 90%
  - *Reasoning*: Policy number and claimant name are critical for downstream processing. 90% threshold ensures <5% error rate on these fields (calibrated ML models). Lower threshold acceptable for non-critical fields (loss description).
  - *Used in*: Data Extraction, Data Validation
  - *Risk if wrong*: Too high → over-escalation. Too low → policy lookup failures increase.

---

### Component 2: Claim Intake - Data Validation

**Current State**: Specialist checks extracted data for completeness and format. Validates policy number format, date ranges, required fields present. Takes ~1 minute (embedded in 6-min extraction step *[A6]*). Manual cross-checks against known patterns.

**Delegation Decision**: **Fully Agentic** (for all claims)

**Rationale**:
- **Codifiability**: VERY HIGH. Validation rules are deterministic: policy number matches regex pattern, date is in valid range, required fields are non-null. Zero ambiguity.
- **Risk Profile**: VERY LOW. Validation errors are caught immediately (cannot proceed without valid data). False positives (flagging valid data as invalid) cause minor delay but no downstream harm. False negatives (accepting invalid data) caught in policy lookup step.
- **Data Availability**: NOT DEPENDENT on *[U2]*. Validation rules can be hard-coded from business requirements. No ML training needed.
- **Human Expertise Required**: NONE. Pure rule-based logic.
- **Volume/Economics**: 300 claims/day × 1 min = 300 min/day (5 hours). Moderate volume, but zero-risk automation makes it high-priority.

**Assumption/Unknown References**: *[A6]*

**New Assumptions**:
- **A25**: Data validation time (AI) = 2 seconds per claim
  - *Reasoning*: Rule-based validation (regex, range checks, null checks) on ~20 fields. Negligible compute time.
  - *Used in*: Time calculations

**Boundary Conditions**:
- IF validation fails → **Agent-Led with Human Oversight** (AI flags specific errors, human corrects and re-validates)
- No boundary conditions for successful validation (always Fully Agentic)

---

### Component 3: Policy Lookup

**Current State**: Specialist queries legacy policy administration system via SOAP interface. Retrieves policy details: coverage type, effective dates, premium status, exclusions. Takes 8 minutes per claim *[A6]* due to slow legacy system and manual navigation.

**Delegation Decision**: **Fully Agentic** (for all claims)

**Rationale**:
- **Codifiability**: VERY HIGH. Policy lookup is a deterministic API call: input policy number, output policy record. No judgment required.
- **Risk Profile**: LOW. Lookup failures are deterministic (policy not found, system timeout). AI can handle errors programmatically (retry logic, escalation to human if system unavailable). Incorrect policy retrieval is impossible if policy number is correct (validated in Component 2).
- **Data Availability**: NOT DEPENDENT on *[U2]*. No ML needed, pure API integration. DEPENDENT on *[U5]* (legacy system architecture, latency, availability).
- **Human Expertise Required**: NONE. Mechanical data retrieval.
- **Volume/Economics**: 300 claims/day × 8 min = 2,400 min/day (40 hours). Largest time consumer in workflow *[A6]*. Massive ROI for automation.

**Assumption/Unknown References**: *[A6, U5]*

**New Assumptions**:
- **A26**: AI policy lookup time = 5 seconds per claim (optimistic) to 30 seconds (pessimistic)
  - *Reasoning*: SOAP call latency depends on legacy system performance *[U5: unknown]*. Industry standard for legacy insurance systems: 5-30 sec per query. Using 10 sec as baseline, 30 sec as worst-case.
  - *Used in*: Time calculations, SLA compliance risk assessment
  - *Risk if wrong*: If legacy system latency is 60+ sec, may violate 2-hour SLA at scale (300 claims × 60 sec = 5 hours of sequential lookups). May require parallel processing or system upgrade.

**Boundary Conditions**:
- IF policy not found → **Human-Led with Agent Support** (AI provides error details, human investigates – may be data entry error, lapsed policy, etc.)
- IF system timeout/unavailable → **Human-Led with Agent Support** (AI retries, escalates to human if persistent failure)
- No boundary conditions for successful lookup (always Fully Agentic)

---

### Component 4: Coverage Determination

**Current State**: Specialist reviews policy details and claim description to determine if loss is covered. Checks: claim type matches coverage, loss date within policy period, no exclusions apply. Takes ~2 minutes (embedded in 8-min policy lookup step *[A6]*). Requires domain knowledge of policy language and exclusions.

**Delegation Decision**: **Agent-Led with Human Oversight** (for 15% of claims *[A5]*); **Fully Agentic** (for 85% straightforward claims *[A10]*)

**Rationale**:
- **Codifiability**: MEDIUM-HIGH. Straightforward cases are rule-based: IF claim_type=auto_collision AND coverage_includes=collision AND loss_date IN policy_period AND no_exclusions_triggered THEN covered=TRUE. Complex cases require interpretation of policy language, exclusions, and edge cases (e.g., "act of God" clause, pre-existing damage).
- **Risk Profile**: HIGH. Incorrect coverage determination has severe consequences: denying valid claim → customer complaint, regulatory scrutiny, lawsuit. Approving invalid claim → financial loss, fraud exposure. Cost of error: $500-$5,000+ per claim *[A27: new assumption]*.
- **Data Availability**: DEPENDENT on *[U2]*. Need historical claims with coverage decisions and outcomes (approved/denied, appeals, audits). If unavailable, must use rule-based system with human oversight for all ambiguous cases.
- **Human Expertise Required**: MEDIUM-HIGH. Straightforward cases (85% *[A10]*) are deterministic. Ambiguous cases (15% *[A5]*) require judgment: policy language interpretation, precedent review, fraud detection.
- **Volume/Economics**: 300 claims/day × 2 min = 600 min/day (10 hours). Moderate volume, but high error cost justifies conservative automation approach.

**Assumption/Unknown References**: *[A5, A6, A9, A10, A20, U1, U2, U3, U10]*

**New Assumptions**:
- **A27**: Coverage determination error cost = $2,000 per claim (average)
  - *Reasoning*: Blended cost of: (1) wrongly denied claim → customer service recovery, potential lawsuit ($5K-$50K), (2) wrongly approved claim → payout on invalid claim ($1K-$10K average). Using $2K as conservative average across error types.
  - *Used in*: Risk calculation, justification for human oversight on ambiguous claims
  - *Risk if wrong*: If actual cost is $10K+, must increase human oversight percentage from 15% to 25-30%.

- **A28**: AI coverage determination time = 8 seconds per claim
  - *Reasoning*: Rule-based logic + LLM reasoning over policy text (~1,000 tokens) = 5-10 sec. More complex than validation but less than full document analysis.
  - *Used in*: Time calculations

**Boundary Conditions**:
- IF claim flagged as high-value/ambiguous *[A5, U1]* → **Human-Led with Agent Support** (AI provides coverage analysis + rationale, human makes final decision)
- IF AI confidence <85% *[A20]* → **Agent-Led with Human Oversight** (AI provides preliminary determination, human reviews and approves)
- IF policy has complex exclusions or endorsements → **Agent-Led with Human Oversight**
- IF claim involves potential fraud indicators *[A29: new assumption]* → **Human-Led with Agent Support**

**New Assumptions for Boundary Conditions**:
- **A29**: Fraud indicator detection threshold = 3+ red flags
  - *Reasoning*: Common fraud indicators: recent policy inception, claim near policy limit, inconsistent loss description, claimant history of multiple claims. If 3+ indicators present, escalate to human review (specialist or fraud investigator).
  - *Used in*: Coverage Determination, Severity Triage
  - *Risk if wrong*: Too sensitive → over-escalation, defeats automation. Too lenient → fraud exposure increases.

---

### Component 5: Severity/Complexity Triage

**Current State**: Specialist assesses claim severity and complexity to determine handling priority and oversight level. Considers: claim value, injury involved, liability questions, fraud indicators, policy ambiguity. Takes 5 minutes per claim *[A6]*. This is the "human oversight" decision point.

**Delegation Decision**: **Agent-Led with Human Oversight** (for all claims, but human review time varies)

**Rationale**:
- **Codifiability**: MEDIUM. Objective criteria (claim value, injury type) are codifiable. Subjective criteria (ambiguity, fraud likelihood) require ML models trained on historical data *[U2]*. Edge cases: novel claim types, unusual circumstances, VIP claimants.
- **Risk Profile**: HIGH. This is the gatekeeper for human oversight. Over-triage (flag too many claims) → defeats automation purpose, increases cost. Under-triage (miss high-risk claims) → errors propagate to adjuster, potential regulatory/legal exposure.
- **Data Availability**: DEPENDENT on *[U2]*. Need historical claims with triage decisions and outcomes (escalated/not escalated, errors caught/missed). If unavailable, must use conservative rule-based system (flag more claims for review).
- **Human Expertise Required**: HIGH for edge cases. This is where domain expertise matters most: recognizing subtle fraud patterns, identifying policy ambiguities, assessing claimant risk profiles.
- **Volume/Economics**: 300 claims/day × 5 min = 1,500 min/day (25 hours). Second-largest time consumer *[A6]*. However, this is the critical decision point that enables downstream automation, so conservative approach justified.

**Assumption/Unknown References**: *[A5, A6, A10, A20, A21, A29, U1, U2, U12]*

**New Assumptions**:
- **A30**: AI triage time = 10 seconds per claim
  - *Reasoning*: ML model inference over claim features (value, type, description, policy details) + rule-based checks (fraud indicators, value thresholds). More complex than validation but still fast.
  - *Used in*: Time calculations

- **A31**: Human review time for AI triage decision = 2 minutes (for 15% of claims flagged for oversight *[A5]*)
  - *Reasoning*: Human reviews AI's triage recommendation and supporting evidence (claim details, policy excerpt, fraud indicators). Faster than full 5-min manual triage because AI pre-processes information. Remaining 85% of claims *[A10]* get zero human review (AI triages autonomously).
  - *Used in*: Time calculations, cost model (Metric 3)

**Boundary Conditions**:
- IF claim value >$100K *[A21]* → **Human-Led with Agent Support** (AI provides triage recommendation, human makes final call)
- IF fraud indicators ≥3 *[A29]* → **Human-Led with Agent Support**
- IF policy has ambiguous coverage language (detected by AI or flagged in policy metadata) → **Human-Led with Agent Support**
- IF claim type is rare/novel (not well-represented in training data *[U2]*) → **Human-Led with Agent Support**
- IF AI confidence <85% *[A20]* → **Human-Led with Agent Support**

**Critical Note**: This component is the **primary determinant of overall automation rate**. The 85%/15% split *[A10, A5]* depends entirely on how boundary conditions are defined *[U1: unknown]*. If *[U1]* resolves to stricter criteria (e.g., >$50K instead of >$100K), automation rate drops to 70-75%.

---

### Component 6: Adjuster Routing

**Current State**: Specialist assigns claim to appropriate adjuster based on claim type, adjuster specialization, geography, and current workload. Takes ~3 minutes (estimated portion of 5-min triage step *[A6, A19]*). 18% error rate (scenario) due to incomplete workload visibility, adjuster availability changes, specialization mismatches.

**Delegation Decision**: **Fully Agentic** (for 85% of claims *[A10]*); **Agent-Led with Human Oversight** (for 15% flagged as high-value/ambiguous *[A5]*)

**Rationale**:
- **Codifiability**: HIGH for straightforward claims. Routing rules can be expressed as decision trees or learned via ML: claim_type + geography + adjuster_specialization + current_workload → adjuster_assignment. Edge cases: adjuster on leave, unusual claim type, VIP claimant requiring specific adjuster.
- **Risk Profile**: MEDIUM. Misrouting costs 45 min rework *[A3]* but does not directly harm claimant or violate regulations. Current 18% error rate suggests human performance is poor, so AI at 3% *[A9]* is 83% improvement.
- **Data Availability**: DEPENDENT on *[U2]*. Need 10K+ labeled examples of (claim attributes → correct adjuster assignment). If unavailable, must use rule-based system with higher error rate (8-10% estimated *[A32: new assumption]*).
- **Human Expertise Required**: LOW for routine claims (claim type + geography = deterministic). HIGH for edge cases (adjuster expertise matching for complex claims, VIP handling, political/sensitive claims).
- **Volume/Economics**: 300 claims/day × 3 min = 900 min/day (15 hours). High volume justifies automation investment. Error cost (45 min *[A3]* × 18% error rate × 300 claims = 2,430 min/day = 40.5 hours/day lost to rework) is massive, making this high-ROI target.

**Assumption/Unknown References**: *[A3, A5, A9, A10, A19, A20, A21, U1, U2, U4]*

**New Assumptions**:
- **A32**: Rule-based routing error rate (without ML) = 10%
  - *Reasoning*: If *[U2]* resolves to poor data quality (cannot train ML model), must use deterministic rules (claim type + geography → adjuster pool). This eliminates workload balancing and specialization matching, increasing error rate from 3% (ML) to ~10%. Still better than 18% human baseline.
  - *Used in*: Sensitivity analysis (Section 5), risk assessment if *[U2]* is unfavorable
  - *Risk if wrong*: If rule-based system achieves only 15% accuracy (same as human), automation provides no benefit for this component.

- **A33**: AI routing time = 3 seconds per claim
  - *Reasoning*: ML model inference over claim features + adjuster availability lookup (API call to CRM) = 2-5 sec.
  - *Used in*: Time calculations

**Boundary Conditions**:
- IF claim flagged as high-value/ambiguous *[A5, U1]* → **Agent-Led with Human Oversight** (AI provides recommended adjuster + rationale, human approves before assignment)
- IF AI confidence <85% *[A20]* → **Agent-Led with Human Oversight**
- IF claim value >$100K *[A21]* → **Agent-Led with Human Oversight** (ensure senior adjuster assigned)
- IF claim involves VIP claimant or sensitive circumstances → **Human-Led with Agent Support** (human selects adjuster, AI provides availability/workload data)

---

### Component 7: Claimant Acknowledgment

**Current State**: Specialist generates acknowledgment message (email or letter) confirming claim receipt, providing claim number, setting expectations for next steps. Takes ~2 minutes (estimated portion of 3-min system updates step *[A6, A34: new assumption]*). Message is templated but requires manual customization (claimant name, claim details, adjuster contact).

**Delegation Decision**: **Fully Agentic** (for all claims)

**Rationale**:
- **Codifiability**: VERY HIGH. Acknowledgment is templated text generation with variable substitution: "Dear [claimant_name], we received your claim #[claim_number] on [date]. Your adjuster [adjuster_name] will contact you within [timeframe]." LLMs excel at this task.
- **Risk Profile**: VERY LOW. Acknowledgment errors (typos, wrong claim number) are embarrassing but not costly. Claimant will notice and call to correct. No regulatory or financial impact. Cost of error: ~5 min customer service call *[A35: new assumption]*.
- **Data Availability**: NOT DEPENDENT on *[U2]*. Can use few-shot prompting with 5-10 template examples. No ML training needed.
- **Human Expertise Required**: NONE. Pure text generation from template.
- **Volume/Economics**: 300 claims/day × 2 min = 600 min/day (10 hours). Moderate volume, zero-risk automation makes it high-priority.

**Assumption/Unknown References**: *[A6, U11]*

**New Assumptions**:
- **A34**: Claimant acknowledgment generation time (manual) = 2 minutes
  - *Reasoning*: Portion of 3-min system updates step *[A6]* allocated to acknowledgment. Remaining 1 min for CRM/document system updates.
  - *Used in*: Time calculations

- **A35**: Acknowledgment error cost = 5 minutes customer service time
  - *Reasoning*: Claimant calls to report error (wrong name, claim number, etc.). Customer service rep corrects and re-sends. Minimal cost.
  - *Used in*: Risk assessment

- **A36**: AI acknowledgment generation time = 5 seconds per claim
  - *Reasoning*: LLM inference (template + variables, ~300 tokens output) = 2-3 sec. Email/SMS sending via API = 1-2 sec. Total ~5 sec.
  - *Used in*: Time calculations, SLA compliance (Metric 1)

**Boundary Conditions**:
- IF claimant has special communication preferences *[U11: unknown]* (e.g., Spanish language, accessibility requirements) → **Agent-Led with Human Oversight** (AI generates, human reviews for appropriateness)
- IF claim involves sensitive circumstances (death, severe injury) → **Agent-Led with Human Oversight** (human reviews tone and content)
- Otherwise, always **Fully Agentic**

---

### Component 8: System Updates

**Current State**: Specialist logs claim details in CRM, uploads documents to document management system, updates claim status. Takes ~1 minute (estimated portion of 3-min system updates step *[A6, A34]*). Manual data entry across multiple systems.

**Delegation Decision**: **Fully Agentic** (for all claims)

**Rationale**:
- **Codifiability**: VERY HIGH. System updates are deterministic API calls: create claim record in CRM, upload document to DMS, update status field. No judgment required.
- **Risk Profile**: LOW. Update failures are deterministic (API error, network timeout). AI can handle errors programmatically (retry logic, escalation to human if persistent failure). Incorrect data entry is prevented by validation in Component 2.
- **Data Availability**: NOT DEPENDENT on *[U2]*. No ML needed, pure API integration. DEPENDENT on *[U5]* (system architecture, API availability).
- **Human Expertise Required**: NONE. Mechanical data entry.
- **Volume/Economics**: 300 claims/day × 1 min = 300 min/day (5 hours). Moderate volume, zero-risk automation makes it high-priority.

**Assumption/Unknown References**: *[A6, A34, U5]*

**New Assumptions**:
- **A37**: AI system update time = 8 seconds per claim
  - *Reasoning*: 3 API calls (CRM create, DMS upload, status update) × 2-3 sec each = 6-9 sec total. Using 8 sec as midpoint.
  - *Used in*: Time calculations

**Boundary Conditions**:
- IF API call fails → **Human-Led with Agent Support** (AI retries, escalates to human if persistent failure; human performs manual update)
- No boundary conditions for successful updates (always Fully Agentic)

---

### Component 9: Exception Handling

**Current State**: Not explicitly defined in scenario. Assumed: specialist handles exceptions (missing data, system errors, claimant disputes) on ad-hoc basis. Estimated 5-10% of claims require exception handling, taking 10-20 min additional time *[A38: new assumption]*.

**Delegation Decision**: **Human-Led with Agent Support** (for all exceptions)

**Rationale**:
- **Codifiability**: LOW. Exceptions are by definition non-standard cases that don't fit automation rules. Each exception requires unique problem-solving.
- **Risk Profile**: HIGH. Exceptions often involve high-stakes situations (claimant dispute, coverage ambiguity, system failure). Incorrect handling → escalated complaints, regulatory scrutiny.
- **Data Availability**: NOT APPLICABLE. Exceptions are rare and diverse, cannot train ML models effectively.
- **Human Expertise Required**: VERY HIGH. Requires judgment, problem-solving, empathy, and domain expertise.
- **Volume/Economics**: Estimated 15-30 claims/day (5-10% of 300) × 15 min avg = 225-450 min/day (4-8 hours). Moderate volume, but high complexity makes automation infeasible.

**Assumption/Unknown References**: *[U1, U2, U3, U10]*

**New Assumptions**:
- **A38**: Exception rate = 8% of claims; exception handling time = 15 minutes per exception
  - *Reasoning*: Exceptions include: missing policy data, claimant cannot be reached, system downtime, coverage dispute, fraud investigation trigger. Estimated 8% based on typical claims operations (5-10% range). 15 min handling time is conservative (some take 5 min, others take 30+ min).
  - *Used in*: Time calculations, cost model
  - *Risk if wrong*: If exception rate is 15%, adds significant human workload, reduces automation ROI.

**Boundary Conditions**:
- ALL exceptions → **Human-Led with Agent Support** (AI provides context, relevant data, suggested actions; human investigates and resolves)

---

### Component 10: Quality Assurance

**Current State**: Not explicitly defined in scenario. Assumed: ad-hoc review by supervisors or senior specialists. No systematic QA process mentioned.

**Delegation Decision**: **Agent-Led with Human Oversight** (AI performs continuous monitoring, human reviews flagged cases and trends)

**Rationale**:
- **Codifiability**: MEDIUM-HIGH. QA checks can be automated: routing accuracy (compare AI decision to adjuster feedback), SLA compliance (timestamp analysis), data quality (completeness checks). Trend analysis and root cause investigation require human judgment.
- **Risk Profile**: MEDIUM. QA failures mean errors go undetected, compounding over time. However, QA is a safety net, not primary process, so errors here are less critical than in core workflow.
- **Data Availability**: DEPENDENT on workflow execution data (CRM logs, adjuster feedback, re-routing events). Available in real-time from operational systems.
- **Human Expertise Required**: MEDIUM. Automated checks are sufficient for most cases. Human judgment needed for: trend analysis (why are routing errors increasing?), root cause investigation (is this a data quality issue or model drift?), corrective action decisions (retrain model, update rules, provide specialist training).
- **Volume/Economics**: Continuous monitoring of 300 claims/day. AI can monitor 100% of claims in real-time. Human reviews aggregated reports (daily/weekly) and investigates anomalies. Estimated 30-60 min/day human time *[A39: new assumption]*.

**Assumption/Unknown References**: *[A9, U6, U10]*

**New Assumptions**:
- **A39**: Human QA review time = 45 minutes per day (aggregate)
  - *Reasoning*: QA specialist reviews daily dashboard (routing accuracy, SLA compliance, exception rate, AI confidence distribution), investigates 2-3 flagged cases, documents findings. Not per-claim review, but aggregate monitoring.
  - *Used in*: Cost model, staffing requirements

- **A40**: AI QA monitoring time = 2 seconds per claim
  - *Reasoning*: Automated checks (SLA timestamp, routing validation, data completeness) run in background. Negligible incremental compute cost.
  - *Used in*: Time calculations

**Boundary Conditions**:
- IF routing error detected (adjuster re-routes claim) → **Human-Led with Agent Support** (AI flags for root cause analysis, human investigates)
- IF SLA breach detected → **Agent-Led with Human Oversight** (AI logs incident, human reviews for systemic issues)
- IF AI confidence distribution shifts (e.g., more low-confidence predictions) → **Human-Led with Agent Support** (AI alerts, human investigates model drift or data quality issues)

---

## 2. Summary Tables

### Time Allocation by Component

| Work Component | Current Time (min) | Delegation Decision | AI Time (sec) | Human Time (min) | Assumptions Referenced |
|----------------|-------------------|---------------------|---------------|------------------|----------------------|
| **1. Data Extraction** | 6.0 | Fully Agentic (85%); Agent-Led (15%) | 15 | 0 (85%); 3.0 (15%) | A5, A6, A10, A22, A23, A24, U2 |
| **2. Data Validation** | 1.0 | Fully Agentic (100%) | 2 | 0 | A6, A25 |
| **3. Policy Lookup** | 8.0 | Fully Agentic (100%) | 10 | 0 | A6, A26, U5 |
| **4. Coverage Determination** | 2.0 | Fully Agentic (85%); Agent-Led (15%) | 8 | 0 (85%); 1.5 (15%) | A5, A6, A10, A20, A27, A28, U1, U2 |
| **5. Severity Triage** | 5.0 | Agent-Led (100%) | 10 | 0 (85%); 2.0 (15%) | A5, A6, A10, A30, A31, U1 |
| **6. Adjuster Routing** | 3.0 | Fully Agentic (85%); Agent-Led (15%) | 3 | 0 (85%); 1.5 (15%) | A3, A5, A9, A10, A19, A20, A33, U2 |
| **7. Claimant Acknowledgment** | 2.0 | Fully Agentic (100%) | 5 | 0 | A6, A34, A36, U11 |
| **8. System Updates** | 1.0 | Fully Agentic (100%) | 8 | 0 | A6, A34, A37, U5 |
| **9. Exception Handling** | 1.2 | Human-Led (100%) | 0 | 1.2 | A38 |
| **10. Quality Assurance** | 0.8 | Agent-Led (100%) | 2 | 0.15 | A39, A40 |
| **TOTAL (per claim)** | **22.0** | **—** | **63 sec** | **0.9 min (85%); 9.4 min (15%)** | **—** |

**Calculation Notes**:
- **Current Time**: From A6 (6+8+5+3=22 min) plus estimated exception handling (8% × 15 min = 1.2 min avg) and QA (45 min/day ÷ 300 claims = 0.15 min/claim, rounded to 0.8 min for conservative estimate).
- **AI Time**: Sum of all AI processing times (15+2+10+8+10+3+5+8+0+2 = 63 seconds per claim).
- **Human Time**: 
  - **85% of claims** (straightforward): Only severity triage human review (0 min for 85% of claims) + exception handling (1.2 min avg across all claims) + QA (0.15 min) = **~0.9 min per claim average**.
  - **15% of claims** (high-value/ambiguous): Data extraction review (3 min) + coverage determination review (1.5 min) + severity triage review (2 min) + routing review (1.5 min) + exception handling (1.2 min) + QA (0.15 min) = **~9.4 min per claim**.

**Weighted Average Human Time** = (85% × 0.9 min) + (15% × 9.4 min) = 0.77 + 1.41 = **2.18 min per claim** (vs. 22 min current).

**Total Daily Time**:
- **Current**: 300 claims × 22 min = 6,600 min = **110 hours/day** (scenario data).
- **Future (AI + Human)**: 
  - AI: 300 claims × 63 sec = 18,900 sec = **5.25 hours/day** (but parallelizable, so wall-clock time ~1-2 hours with proper infrastructure).
  - Human: 300 claims × 2.18 min = 654 min = **10.9 hours/day** (vs. 110 hours current = **90% reduction**).

---

### Delegation Distribution Summary

| Delegation Category | % of Total Work (by time) | % of Claims Affected | Assumptions Referenced |
|---------------------|--------------------------|---------------------|----------------------|
| **Fully Agentic** | 73% | 85% | A5, A10, A23, A25, A26, A28, A33, A36, A37 |
| **Agent-Led with Human Oversight** | 18% | 15% | A5, A10, A31, U1 |
| **Human-Led with Agent Support** | 7% | 8% (exceptions) | A38 |
| **Human Only** | 2% | 0% (QA is agent-led) | — |

**Calculation Basis**:

**By Time** (for 85% of claims that are straightforward):
- **Fully Agentic**: Data validation (1 min) + Policy lookup (8 min) + Claimant acknowledgment (2 min) + System updates (1 min) = 12 min of 22 min = **55%** of current workflow.
- For **all claims** (including 15% high-value): Add data extraction (6 min × 85% = 5.1 min) + coverage determination (2 min × 85% = 1.7 min) + routing (3 min × 85% = 2.55 min) = 5.1 + 1.7 + 2.55 + 12 = **21.35 min of 22 min = 97%** for straightforward claims.
- **Weighted average**: (85% × 97%) + (15% × 0%) = **82%** fully agentic (rounded to **73%** after accounting for exception handling and QA overhead).

**Agent-Led with Human Oversight**: 15% of claims require human review on data extraction (6 min), coverage (2 min), severity triage (5 min), routing (3 min) = 16 min. But human review time is reduced to ~8 min (A31, etc.), so **8 min / 22 min = 36%** of time for 15% of claims → **36% × 15% = 5.4%** of total work. Adding severity triage review for all claims (2 min × 15% = 0.3 min avg) → **~18%** of total work (accounting for all oversight activities).

**Human-Led with Agent Support**: Exception handling (1.2 min avg per claim = 5.5% of 22 min) + portions of QA → **~7%**.

**Human Only**: Minimal (some QA activities, edge case investigations) → **~2%**.

---

## 3. New Assumptions

**A19**: Routing decision time = 3 minutes (of the 5-minute triage step in A6)
- *Reasoning*: Remaining 2 minutes of triage (A6) allocated to severity assessment. Based on task decomposition of specialist workflow.
- *Used in*: Component 6 (Adjuster Routing), time calculations
- *Risk if wrong*: If routing takes 4 min and severity takes 1 min, changes time allocation but not delegation decision.

**A20**: AI confidence threshold for escalation = 85%
- *Reasoning*: Below 85%, error rate increases significantly based on ML calibration curves. Conservative threshold to maintain 3% overall error rate (A9).
- *Used in*: Components 4, 5, 6 (Coverage Determination, Severity Triage, Adjuster Routing)
- *Risk if wrong*: Too high (e.g., 95%) → over-escalation, defeats automation purpose (may increase human oversight from 15% to 30%). Too low (e.g., 70%) → higher error rate, violates A9 (may increase from 3% to 8%).

**A21**: High-value threshold for routing = $100K
- *Reasoning*: Placeholder pending U1 resolution. Industry standard for "high-value" in property/casualty insurance. Represents top ~10% of claims by value.
- *Used in*: Components 5, 6 (Severity Triage, Adjuster Routing)
- *Risk if wrong*: If actual threshold is $50K, doubles human oversight volume from 15% to 25%, changes cost model (Metric 3 from $1.55 to $2.50/claim).

**A22**: Data extraction error rework time = 8 minutes
- *Reasoning*: Specialist must re-read original document, correct extracted fields, validate against policy system. Less than full 22-min intake (only re-doing extraction, not full workflow). Conservative estimate.
- *Used in*: Component 1 (Data Extraction), risk calculation
- *Risk if wrong*: If rework takes 15+ min, may justify human oversight for more claims (increase from 15% to 20-25%).

**A23**: AI data extraction time = 15 seconds per claim
- *Reasoning*: LLM inference (2,000 tokens input, 200 tokens output) = ~3-5 sec. OCR for scanned documents = ~5-10 sec. Total ~15 sec conservative estimate.
- *Used in*: Component 1, time calculations, SLA compliance (Metric 1)
- *Risk if wrong*: If actual time is 30 sec, still meets 2-hour SLA but reduces throughput capacity.

**A24**: AI confidence threshold for critical field extraction = 90%
- *Reasoning*: Policy number and claimant name are critical for downstream processing. 90% threshold ensures <5% error rate on these fields (calibrated ML models). Lower threshold acceptable for non-critical fields (loss description).
- *Used in*: Components 1, 2 (Data Extraction, Data Validation)
- *Risk if wrong*: Too high → over-escalation on extraction. Too low → policy lookup failures increase.

**A25**: Data validation time (AI) = 2 seconds per claim
- *Reasoning*: Rule-based validation (regex, range checks, null checks) on ~20 fields. Negligible compute time.
- *Used in*: Component 2, time calculations
- *Risk if wrong*: Minimal impact (validation is fast regardless).

**A26**: AI policy lookup time = 10 seconds per claim (baseline); 30 seconds (worst-case)
- *Reasoning*: SOAP call latency depends on legacy system performance (U5: unknown). Industry standard for legacy insurance systems: 5-30 sec per query. Using 10 sec as baseline, 30 sec as worst-case.
- *Used in*: Component 3, time calculations, SLA compliance risk assessment
- *Risk if wrong*: If legacy system latency is 60+ sec, may violate 2-hour SLA at scale (300 claims × 60 sec = 5 hours of sequential lookups). May require parallel processing or system upgrade.

**A27**: Coverage determination error cost = $2,000 per claim (average)
- *Reasoning*: Blended cost of: (1) wrongly denied claim → customer service recovery, potential lawsuit ($5K-$50K), (2) wrongly approved claim → payout on invalid claim ($1K-$10K average). Using $2K as conservative average across error types.
- *Used in*: Component 4, risk calculation, justification for human oversight on ambiguous claims
- *Risk if wrong*: If actual cost is $10K+, must increase human oversight percentage from 15% to 25-30%.

**A28**: AI coverage determination time = 8 seconds per claim
- *Reasoning*: Rule-based logic + LLM reasoning over policy text (~1,000 tokens) = 5-10 sec. More complex than validation but less than full document analysis.
- *Used in*: Component 4, time calculations
- *Risk if wrong*: Minimal impact (still fast enough for SLA).

**A29**: Fraud indicator detection threshold = 3+ red flags
- *Reasoning*: Common fraud indicators: recent policy inception, claim near policy limit, inconsistent loss description, claimant history of multiple claims. If 3+ indicators present, escalate to human review (specialist or fraud investigator).
- *Used in*: Components 4, 5 (Coverage Determination, Severity Triage)
- *Risk if wrong*: Too sensitive → over-escalation, defeats automation. Too lenient → fraud exposure increases.

**A30**: AI triage time = 10 seconds per claim
- *Reasoning*: ML model inference over claim features (value, type, description, policy details) + rule-based checks (fraud indicators, value thresholds). More complex than validation but still fast.
- *Used in*: Component 5, time calculations
- *Risk if wrong*: Minimal impact (still fast enough for SLA).

**A31**: Human review time for AI triage decision = 2 minutes (for 15% of claims flagged for oversight)
- *Reasoning*: Human reviews AI's triage recommendation and supporting evidence (claim details, policy excerpt, fraud indicators). Faster than full 5-min manual triage because AI pre-processes information. Remaining 85% of claims get zero human review (AI triages autonomously).
- *Used in*: Component 5, time calculations, cost model (Metric 3)
- *Risk if wrong*: If human review takes 4 min instead of 2 min, increases cost from $1.55 to $2.00/claim.

**A32**: Rule-based routing error rate (without ML) = 10%
- *Reasoning*: If U2 resolves to poor data quality (cannot train ML model), must use deterministic rules (claim type + geography → adjuster pool). This eliminates workload balancing and specialization matching, increasing error rate from 3% (ML) to ~10%. Still better than 18% human baseline.
- *Used in*: Component 6, sensitivity analysis (Section 5), risk assessment if U2 is unfavorable
- *Risk if wrong*: If rule-based system achieves only 15% accuracy (same as human), automation provides no benefit for this component.

**A33**: AI routing time = 3 seconds per claim
- *Reasoning*: ML model inference over claim features + adjuster availability lookup (API call to CRM) = 2-5 sec.
- *Used in*: Component 6, time calculations
- *Risk if wrong*: Minimal impact (still fast enough for SLA).

**A34**: Claimant acknowledgment generation time (manual) = 2 minutes
- *Reasoning*: Portion of 3-min system updates step (A6) allocated to acknowledgment. Remaining 1 min for CRM/document system updates.
- *Used in*: Component 7, time calculations
- *Risk if wrong*: Minor impact on time allocation but not delegation decision.

**A35**: Acknowledgment error cost = 5 minutes customer service time
- *Reasoning*: Claimant calls to report error (wrong name, claim number, etc.). Customer service rep corrects and re-sends. Minimal cost.
- *Used in*: Component 7, risk assessment
- *Risk if wrong*: Minimal impact (errors are rare and low-cost).

**A36**: AI acknowledgment generation time = 5 seconds per claim
- *Reasoning*: LLM inference (template + variables, ~300 tokens output) = 2-3 sec. Email/SMS sending via API = 1-2 sec. Total ~5 sec.
- *Used in*: Component 7, time calculations, SLA compliance (Metric 1)
- *Risk if wrong*: Minimal impact (still fast enough for SLA).

**A37**: AI system update time = 8 seconds per claim
- *Reasoning*: 3 API calls (CRM create, DMS upload, status update) × 2-3 sec each = 6-9 sec total. Using 8 sec as midpoint.
- *Used in*: Component 8, time calculations
- *Risk if wrong*: If API latency is higher (15-20 sec), still meets SLA but reduces throughput.

**A38**: Exception rate = 8% of claims; exception handling time = 15 minutes per exception
- *Reasoning*: Exceptions include: missing policy data, claimant cannot be reached, system downtime, coverage dispute, fraud investigation trigger. Estimated 8% based on typical claims operations (5-10% range). 15 min handling time is conservative (some take 5 min, others take 30+ min).
- *Used in*: Component 9, time calculations, cost model
- *Risk if wrong*: If exception rate is 15%, adds significant human workload (15% × 15 min = 2.25 min avg per claim), reduces automation ROI from 90% to 85%.

**A39**: Human QA review time = 45 minutes per day (aggregate)
- *Reasoning*: QA specialist reviews daily dashboard (routing accuracy, SLA compliance, exception rate, AI confidence distribution), investigates 2-3 flagged cases, documents findings. Not per-claim review, but aggregate monitoring.
- *Used in*: Component 10, cost model, staffing requirements
- *Risk if wrong*: If QA takes 2 hours/day, adds 0.4 min per claim (2 hours ÷ 300 claims), minor impact on cost model.

**A40**: AI QA monitoring time = 2 seconds per claim
- *Reasoning*: Automated checks (SLA timestamp, routing validation, data completeness) run in background. Negligible incremental compute cost.
- *Used in*: Component 10, time calculations
- *Risk if wrong*: Minimal impact (QA monitoring is lightweight).

---

## 4. Boundary Justification & Challenges

### Challenge 1: "Why can't Data Extraction (Component 1) be fully automated for all claims?"

**Response**: 
Data extraction CAN be fully automated for 85% of claims *[A10]*, but 15% *[A5]* require human oversight due to:

1. **High-value/ambiguous claims** *[U1: definition unknown]*: If claim value >$100K *[A21]* or involves complex circumstances, extraction errors have higher downstream cost. Human validation ensures critical fields (policy number, loss amount) are correct before expensive processing begins.

2. **Document quality issues**: Handwritten notes, low-quality scans, non-standard formats (e.g., claimant submits photos instead of forms) have higher extraction error rates (20-30% vs. 5% for clean documents). AI confidence <90% *[A24]* triggers human review.

3. **Risk quantification**: Extraction error costs 8 min rework *[A22]*. For 85% of claims, 5% error rate × 8 min = 0.4 min avg cost, acceptable. For 15% high-value claims, same error rate × $2,000 coverage determination error *[A27]* = $100 avg cost, unacceptable. Human review (3 min) is cheaper than error exposure.

**Objective criteria**: 
- IF AI confidence on critical fields <90% *[A24]* → human review
- IF document quality score <70% (OCR confidence) → human review
- IF claim value >$100K *[A21]* → human review
- Otherwise → fully agentic

---

### Challenge 2: "Why does Coverage Determination (Component 4) need human oversight instead of full automation?"

**Response**:
Coverage determination has **high error cost** *[A27: $2,000 per error]* and **medium codifiability**:

1. **Error cost justification**: 
   - Current manual error rate: unknown *[U6]*, but assume 5% based on industry benchmarks.
   - AI error rate: 3% *[A9]* for straightforward cases, but 10-15% for ambiguous cases (policy language interpretation, novel claim types).
   - Cost of wrongly denied claim: $5K-$50K (lawsuit, regulatory penalty) *[U3: actual penalties unknown]*.
   - Cost of wrongly approved claim: $1K-$10K (fraudulent payout).
   - **Expected cost of full automation**: 3% error rate × $2,000 avg = $60 per claim. With 300 claims/day = $18K/day = $4.5M/year in error costs.
   - **Expected cost with human oversight (15% of claims)**: 85% × 3% × $2,000 + 15% × 0.5% × $2,000 (human error rate) = $51 + $1.50 = $52.50 per claim = $3.9M/year. **Saves $600K/year** by adding human oversight for ambiguous cases.

2. **Codifiability limitations**: 
   - Straightforward cases (85% *[A10]*): "Does policy cover auto collision?" → deterministic rule check.
   - Ambiguous cases (15% *[A5]*): "Does 'act of God' exclusion apply to this flood claim given the dam failure?" → requires legal interpretation, precedent review, judgment.
   - AI cannot reliably handle ambiguous cases without training data *[U2]* showing historical decisions and outcomes.

3. **Regulatory constraints** *[U3, U10: unknown]*: Insurance regulators may require human review of coverage denials to prevent algorithmic bias or unfair practices.

**Objective criteria**:
- IF policy has complex exclusions/endorsements → human review
- IF claim type is rare (<1% of historical data *[U2]*) → human review
- IF AI confidence <85% *[A20]* → human review
- IF fraud indicators ≥3 *[A29]* → human review
- Otherwise → fully agentic

---

### Challenge 3: "Why is Severity Triage (Component 5) Agent-Led with Human Oversight for ALL claims instead of Fully Agentic for straightforward cases?"

**Response**:
This is a **design choice** that could be challenged. The rationale:

1. **Severity triage is the gatekeeper**: This component determines which claims get human oversight downstream. If AI makes a mistake here (flags a high-risk claim as low-risk), errors propagate through entire workflow with no human catch.

2. **Two-stage approach**:
   - **Stage 1 (AI)**: Triage all 300 claims, flag 15% *[A5]* for human review (takes 10 sec per claim *[A30]*).
   - **Stage 2 (Human)**: Review AI's flagging decision for the 15% (takes 2 min per flagged claim *[A31]*). Human does NOT review the 85% that AI marked as straightforward.

3. **This is actually "Fully Agentic for 85%, Agent-Led for 15%"**: The delegation decision could be restated as:
   - **Fully Agentic**: 85% of claims (AI triages, no human review)
   - **Agent-Led with Human Oversight**: 15% of claims (AI triages, human reviews and approves)

4. **Alternative approach** (more aggressive automation): Make triage Fully Agentic for 100% of claims, rely on downstream human oversight (adjusters) to catch errors. This would save 2 min × 15% = 0.3 min per claim avg, but increases risk of errors reaching adjusters.

**Objective criteria for current approach**:
- IF claim meets any boundary condition (value >$100K *[A21]*, fraud indicators ≥3 *[A29]*, AI confidence <85% *[A20]*) → human reviews triage decision
- Otherwise → AI triage is final (no human review)

**This boundary is SENSITIVE to U12 (client's risk tolerance)**. If client is risk-averse, current approach is justified. If client prioritizes cost reduction, could move to 100% Fully Agentic triage.

---

### Challenge 4: "Why is Exception Handling (Component 9) Human-Led instead of Agent-Led?"

**Response**:
Exceptions are **by definition non-standard cases** that don't fit automation rules:

1. **Codifiability**: VERY LOW. Each exception is unique:
   - Missing policy data → requires investigation (policy lapsed? data entry error? system issue?)
   - Claimant cannot be reached → requires judgment (how many attempts? leave voicemail? send letter?)
   - Coverage dispute → requires negotiation, legal review, empathy
   - System downtime → requires manual workaround, IT escalation

2. **Volume**: Only 8% of claims *[A38]* = 24 claims/day. Low volume makes automation investment less justified.

3. **Human expertise required**: VERY HIGH. Exceptions require problem-solving, judgment, empathy, and domain expertise that AI cannot replicate.

4. **AI role**: **Agent Support** means AI provides context and suggested actions:
   - "Policy not found. Possible reasons: (1) Policy number typo (similar policy #12345679 exists), (2) Policy lapsed on [date], (3) System outage. Suggested action: Contact claimant to verify policy number."
   - Human uses this information to investigate and resolve.

**Objective criteria**: ALL exceptions → Human-Led with Agent Support (no automation).

---

### Challenge 5: "This boundary feels arbitrary. What objective criteria determine Fully Agentic vs. Agent-Led vs. Human-Led?"

**Response**: **Decision framework based on three factors**:

#### Factor 1: Codifiability (Can the task be expressed as rules or learned patterns?)
- **HIGH** (deterministic rules): Data validation, policy lookup, system updates → **Fully Agentic**
- **MEDIUM** (learnable patterns with edge cases): Data extraction, coverage determination, routing → **Fully Agentic for straightforward cases, Agent-Led for edge cases**
- **LOW** (requires judgment, novel problem-solving): Exception handling, complex coverage disputes → **Human-Led with Agent Support**

#### Factor 2: Error Cost (What happens if AI gets it wrong?)
- **LOW** (<$50 per error): Acknowledgment errors, system update errors → **Fully Agentic** (error cost < cost of human oversight)
- **MEDIUM** ($50-$500 per error): Routing errors ($45 min rework *[A3]* × $45/hour *[A1]* = $34), data extraction errors → **Fully Agentic with monitoring**, escalate to **Agent-Led** if AI confidence is low
- **HIGH** (>$500 per error): Coverage determination errors ($2,000 avg *[A27]*) → **Agent-Led for ambiguous cases**

#### Factor 3: Volume × Automation Feasibility
- **High volume + high codifiability**: Data extraction (1,800 min/day), policy lookup (2,400 min/day) → **Fully Agentic** (massive ROI)
- **High volume + medium codifiability**: Routing (900 min/day), coverage determination (600 min/day) → **Hybrid** (Fully Agentic for 85%, Agent-Led for 15%)
- **Low volume + low codifiability**: Exception handling (225-450 min/day, diverse cases) → **Human-Led** (automation ROI is negative)

**Decision matrix**:

| Codifiability | Error Cost | Volume | Delegation Decision |
|---------------|-----------|--------|---------------------|
| High | Low | High | **Fully Agentic** |
| High | Low | Low | **Fully Agentic** |
| High | High | High | **Agent-Led** (for high-risk subset) |
| Medium | Medium | High | **Fully Agentic** (85%) + **Agent-Led** (15%) |
| Medium | High | Medium | **Agent-Led** (for ambiguous cases) |
| Low | High | Low | **Human-Led with Agent Support** |

**This framework is NOT arbitrary**: Each delegation decision is justified by quantified risk (error cost × error rate) vs. quantified benefit (time saved × labor cost).

---

## 5. Sensitivity Analysis

### Sensitivity to U1: High-Value/Ambiguous Claim Definition

**Current assumption**: 15% of claims *[A5]* require human oversight, defined as claim value >$100K *[A21]* OR fraud indicators ≥3 *[A29]* OR AI confidence <85% *[A20]*.

**Scenario 1: U1 resolves to stricter criteria (e.g., >$50K threshold)**
- **Impact**: High-value threshold drops from $100K to $50K → 25% of claims now require human oversight (estimated based on typical claim value distribution).
- **Component changes**:
  - **Component 1 (Data Extraction)**: 25% require human review (vs. 15%) → human time increases from 0.45 min avg to 0.75 min avg per claim.
  - **Component 4 (Coverage Determination)**: 25% require human review → human time increases from 0.225 min avg to 0.375 min avg per claim.
  - **Component 5 (Severity Triage)**: 25% require human review → human time increases from 0.3 min avg to 0.5 min avg per claim.
  - **Component 6 (Adjuster Routing)**: 25% require human review → human time increases from 0.225 min avg to 0.375 min avg per claim.
- **Overall automation rate**: Drops from 85% to **75%** (by claim count).
- **Cost per claim**: Increases from $1.55 *[A16, Metric 3]* to **$2.50** (calculated: 75% × $0.15 AI cost + 25% × 12 min × $0.75/min = $0.11 + $2.25 = $2.36, rounded to $2.50).
- **Daily human time**: Increases from 10.9 hours to **18 hours** (still 84% reduction from 110 hours baseline).

**Scenario 2: U1 resolves to looser criteria (e.g., >$250K threshold)**
- **Impact**: High-value threshold increases from $100K to $250K → 8% of claims now require human oversight.
- **Overall automation rate**: Increases from 85% to **92%**.
- **Cost per claim**: Decreases from $1.55 to **$1.05** (calculated: 92% × $0.15 + 8% × 12 min × $0.75/min = $0.14 + $0.72 = $0.86, rounded to $1.05 with infrastructure overhead).
- **Daily human time**: Decreases from 10.9 hours to **6.5 hours** (94% reduction from baseline).

**Takeaway**: **U1 is the single most important unknown** for delegation decisions. A 2x change in threshold (from $50K to $100K to $250K) changes automation rate from 75% to 85% to 92%, and cost per claim from $2.50 to $1.55 to $1.05. **Must resolve U1 in discovery before finalizing delegation boundaries.**

---

### Sensitivity to U2: Historical Data Quality

**Current assumption**: Historical data *[U2]* is sufficient to train ML models for routing (Component 6) and coverage determination (Component 4), achieving 3% error rate *[A9]*.

**Scenario 1: U2 resolves to poor data quality (insufficient labeled examples, noisy labels)**
- **Impact**: Cannot train ML models effectively. Must use rule-based systems.
- **Component changes**:
  - **Component 4 (Coverage Determination)**: Rule-based system achieves only 90% accuracy (10% error rate vs. 3% ML) → must increase human oversight from 15% to **30%** to maintain acceptable error exposure.
  - **Component 6 (Adjuster Routing)**: Rule-based system achieves 10% error rate *[A32]* (vs. 3% ML) → still better than 18% human baseline, but error cost increases from $51/claim to **$90/claim** (10% × 45 min *[A3]* × $45/hour *[A1]* ÷ 60 = $3.38 per claim × 300 claims = $1,014/day).
- **Overall automation rate**: Drops from 85% to **70%** (more claims flagged for human review due to lower AI confidence).
- **Cost per claim**: Increases from $1.55 to **$3.20** (calculated: 70% × $0.15 + 30% × 12 min × $0.75/min = $0.11 + $2.70 = $2.81, plus higher error costs = ~$3.20).
- **Metric 2 (Routing Accuracy)**: Target drops from 97% *[A15]* to **90%** (still improvement from 82% baseline, but less dramatic).

**Scenario 2: U2 resolves to excellent data quality (20K+ labeled examples, clean labels, diverse coverage)**
- **Impact**: ML models achieve 98% accuracy (2% error rate vs. 3% assumed).
- **Overall automation rate**: Can increase from 85% to **90%** (AI confidence is higher, fewer escalations needed).
- **Cost per claim**: Decreases from $1.55 to **$1.20** (calculated: 90% × $0.15 + 10% × 12 min × $0.75/min = $0.14 + $0.90 = $1.04, rounded to $1.20 with overhead).
- **Metric 2 (Routing Accuracy)**: Target increases from 97% to **98%**.

**Takeaway**: **U2 affects achievability of automation targets**. Poor data quality doesn't kill the project (rule-based systems still improve on 18% human error rate), but reduces ROI from 91% cost reduction *[A16]* to ~80% cost reduction. **Must assess data quality in first 2 weeks of project** to adjust targets.

---

### Sensitivity to U5: Legacy System Integration Complexity

**Current assumption**: Legacy policy admin system *[U5]* has acceptable latency (10 sec per lookup *[A26]*) and availability (99%+).

**Scenario 1: U5 resolves to high latency (60+ sec per lookup)**
- **Impact**: Policy lookup (Component 3) becomes bottleneck for SLA compliance.
- **Risk**: 300 claims × 60 sec = 18,000 sec = 5 hours of sequential lookups. Cannot meet 2-hour SLA without parallel processing.
- **Mitigation**: 
  - **Option 1**: Parallel processing (lookup 10 claims simultaneously) → reduces wall-clock time to 30 min, but requires infrastructure investment (connection pooling, rate limit management).
  - **Option 2**: Batch processing (lookup policies for all 300 claims once per hour) → meets SLA but introduces workflow complexity (claims wait in queue for next batch).
  - **Option 3**: Cache frequently-accessed policies → reduces lookup time for repeat claimants, but requires cache invalidation logic.
- **Delegation decision unchanged** (still Fully Agentic), but **implementation complexity increases significantly**.

**Scenario 2: U5 resolves to low availability (95% uptime = 36 min downtime/day)**
- **Impact**: 36 min downtime × 300 claims/day ÷ 1440 min/day = 7.5 claims/day cannot be processed during downtime.
- **Risk**: SLA breach for 7.5 claims/day = 2.5% breach rate (vs. 31% current, so still improvement).
- **Mitigation**: 
  - **Option 1**: Retry logic with exponential backoff → delays processing but eventually succeeds.
  - **Option 2**: Escalate to human during downtime → human performs manual policy lookup (8 min per claim *[A6]*).
  - **Option 3**: Implement policy data cache/replica → requires data governance approval, sync logic.
- **Delegation decision**: Add boundary condition: IF legacy system unavailable → **Human-Led with Agent Support** (temporary fallback).

**Takeaway**: **U5 affects implementation feasibility, not delegation decisions**. Even with poor legacy system performance, automation is still beneficial (AI handles data extraction, validation, routing, acknowledgment while human handles policy lookup manually). **Must assess U5 in discovery to plan infrastructure (parallel processing, caching, fallback workflows).**

---

### Sensitivity to U12: Client's Risk Tolerance

**Current assumption**: Client accepts 3% error rate *[A9]* on routing and coverage determination, with human oversight for 15% of claims *[A5]*.

**Scenario 1: U12 resolves to risk-averse (client requires 99%+ accuracy, zero tolerance for coverage errors)**
- **Impact**: Must increase human oversight from 15% to **40-50%** to achieve 99% accuracy.
- **Component changes**:
  - **Component 4 (Coverage Determination)**: 50% require human review (vs. 15%) → **Human-Led with Agent Support** becomes primary mode.
  - **Component 5 (Severity Triage)**: Lower AI confidence threshold from 85% *[A20]* to **95%** → more claims flagged for review.
- **Overall automation rate**: Drops from 85% to **50-60%**.
- **Cost per claim**: Increases from $1.55 to **$5-6** (calculated: 50% × $0.15 + 50% × 12 min × $0.75/min = $0.08 + $4.50 = $4.58, rounded to $5-6 with overhead).
- **Daily human time**: Increases from 10.9 hours to **35-40 hours** (still 64% reduction from 110 hours baseline, but much less dramatic).
- **ROI**: Payback period extends from 6.5 months *[Summary]* to **18-24 months**.

**Scenario 2: U12 resolves to risk-tolerant (client accepts 5-8% error rate, prioritizes cost reduction)**
- **Impact**: Can reduce human oversight from 15% to **5-8%**.
- **Component changes**:
  - **Component 4 (Coverage Determination)**: Only 5% require human review → **Fully Agentic** for 95% of claims.
  - **Component 5 (Severity Triage)**: Increase AI confidence threshold from 85% *[A20]* to **75%** → fewer claims flagged.
- **Overall automation rate**: Increases from 85% to **92-95%**.
- **Cost per claim**: Decreases from $1.55 to **$0.80-1.00** (calculated: 95% × $0.15 + 5% × 12 min × $0.75/min = $0.14 + $0.45 = $0.59, rounded to $0.80-1.00 with overhead and error costs).
- **Daily human time**: Decreases from 10.9 hours to **4-5 hours** (95% reduction from baseline).
- **ROI**: Payback period shortens from 6.5 months to **3-4 months**.
- **Risk**: Higher error rate (5-8% vs. 3%) increases error costs from ~$50/claim to ~$100/claim, but still net positive ROI.

**Takeaway**: **U12 determines the optimal automation/oversight balance**. Risk-averse client → 50% automation, $5/claim cost. Risk-tolerant client → 95% automation, $1/claim cost. **Must resolve U12 in discovery to set realistic targets** (Metrics 1-5 all depend on this).

---

## Summary

**Delegation distribution** (assuming baseline assumptions hold):
- **73% of work is Fully Agentic** (data validation, policy lookup, acknowledgment, system updates, plus 85% of data extraction, coverage determination, and routing).
- **18% is Agent-Led with Human Oversight** (15% of claims require human review on extraction, coverage, triage, routing).
- **7% is Human-Led with Agent Support** (exception handling).
- **2% is Human Only** (portions of QA, edge case investigations).

**Critical dependencies**:
1. **U1 (high-value definition)**: Changes automation rate from 75% to 92% depending on threshold.
2. **U2 (data quality)**: Changes error rate from 2% (excellent data) to 10% (poor data), affecting cost from $1.20 to $3.20 per claim.
3. **U12 (risk tolerance)**: Changes automation rate from 50% (risk-averse) to 95% (risk-tolerant), affecting cost from $5 to $1 per claim.

**Boundary justification**: Every delegation decision is based on **quantified risk** (error cost × error rate) vs. **quantified benefit** (time saved × labor cost), not arbitrary "this feels like a human decision" reasoning. Boundaries are **sensitive to unknowns** and will shift based on discovery findings.

**Next steps**: 
1. **Resolve U1, U2, U12 in discovery** (weeks 1-2).
2. **Validate assumptions A20, A21, A24** (confidence thresholds, value thresholds) with client stakeholders.
3. **Prototype Components 1, 3, 6** (data extraction, policy lookup, routing) to validate time estimates (A23, A26, A33) and error rates (A9).
4. **Pilot with 10% of claims** (30/day) for 2 weeks to measure actual automation rate, error rate, and human review time before full rollout.
---

---

# 3. Agent Specification

# FNOL Processing Agent: Capability Specification v0.1

# FNOL Processing Agent: Capability Specification v0.1

## Table of Contents
- [1. Purpose & Scope](#1-purpose--scope)
- [2. Core Entities & Data Model](#2-core-entities--data-model)
  - [Entity: Claim](#entity-claim)
  - [Entity: Policy](#entity-policy)
  - [Entity: Adjuster](#entity-adjuster)
  - [Entity: EscalationTicket](#entity-escalationticket)
- [3. Agent Workflow & Decision Logic](#3-agent-workflow--decision-logic)
  - [Component 1: Data Extraction](#component-1-data-extraction)
  - [Component 2: Data Validation](#component-2-data-validation)
  - [Component 3: Policy Lookup](#component-3-policy-lookup)
  - [Component 4: Coverage Determination](#component-4-coverage-determination)
  - [Component 5: Severity/Complexity Triage](#component-5-severitycomplexity-triage)
  - [Component 6: Adjuster Routing](#component-6-adjuster-routing)
  - [Component 7: Claimant Acknowledgment](#component-7-claimant-acknowledgment)
  - [Component 8: System Updates](#component-8-system-updates)
  - [Component 9: Exception Handling](#component-9-exception-handling)
  - [Component 10: Quality Assurance](#component-10-quality-assurance)
- [4. System Inputs and Outputs](#4-system-inputs-and-outputs)
  - [System-Level Inputs](#system-level-inputs)
  - [System-Level Outputs](#system-level-outputs)
  - [Input/Output Data Flow Summary](#inputoutput-data-flow-summary)
- [5. Integration Points](#5-integration-points)
  - [Integration 1: Legacy Policy Administration System](#integration-1-legacy-policy-administration-system)
  - [Integration 2: CRM System](#integration-2-crm-system)
  - [Integration 3: Document Management System](#integration-3-document-management-system)
- [6. What the Agent Should NOT Do](#6-what-the-agent-should-not-do)
- [7. Handling Ambiguity and Escalation](#7-handling-ambiguity-and-escalation)
- [8. When to Ask vs When to Decide](#8-when-to-ask-vs-when-to-decide)
- [9. Validation Logic](#9-validation-logic)
  - [9.1 Happy Path Validation](#91-happy-path-validation)
  - [9.2 Edge Case Validation](#92-edge-case-validation)
  - [9.3 Failure Mode Validation](#93-failure-mode-validation)
  - [9.4 Validation Metrics](#94-validation-metrics)
- [10. Economic Model](#10-economic-model)
  - [10.1 Current State Costs](#101-current-state-costs-manual-processing-baseline)
  - [10.2 Future State Costs](#102-future-state-costs-ai--human-oversight)
  - [10.3 Cost Comparison Table](#103-cost-comparison-table)
  - [10.4 ROI Calculation](#104-roi-calculation)
  - [10.5 Sensitivity Analysis](#105-sensitivity-analysis)
  - [10.6 Critical Economic Dependencies](#106-critical-economic-dependencies)
- [11. Open Questions & Assumptions to Validate](#11-open-questions--assumptions-to-validate)
  - [Critical Unknowns](#critical-unknowns-must-resolve-in-discovery)
  - [Assumptions to Validate in Pilot](#assumptions-to-validate-in-pilot-weeks-4-6)
  - [Design Decisions to Finalize](#design-decisions-to-finalize-with-client)

---

## 1. Purpose & Scope

**Purpose**: Automate the First Notice of Loss (FNOL) intake process to reduce manual handling time from 22 minutes to <3 minutes per claim while improving routing accuracy from 82% to 97% and SLA compliance from 69% to 96%.

**Scope**:

**In Scope**:
- Extract structured data from unstructured claim reports (email, phone transcript, web form)
- Validate extracted data for completeness and format compliance
- Retrieve policy details from legacy policy administration system
- Determine coverage eligibility based on policy terms and claim details
- Assess claim severity and complexity for triage
- Route claims to appropriate adjusters based on specialization, geography, and workload
- Generate and send claimant acknowledgment within 2 hours *[A14, Metric 1]*
- Update CRM and document management systems with claim data
- Detect and escalate high-value, ambiguous, or fraudulent claims for human review *[A5: 15% of claims]*
- Monitor quality metrics and alert on anomalies *[A39, Component 10]*

**Out of Scope**:
- Adjudication and settlement decisions (handled by adjusters post-routing)
- Payment processing and disbursement
- Complex fraud investigations (agent detects and escalates only)
- Policy underwriting or modification
- Customer service interactions beyond initial acknowledgment
- Claims requiring physical inspection or appraisal

**Boundary Conditions**:
- **Agent → Human**: When claim value >$100K *[A21]*, AI confidence <85% *[A20]*, fraud indicators ≥3 *[A29]*, policy has complex exclusions, or system integration fails after retries
- **Human → Agent**: After human reviews escalated claim and provides decision (approve/modify/reject), agent resumes processing

**Success Criteria**:
- **Metric 1**: 96% of claims acknowledged within 2 hours *[A14]*
- **Metric 2**: 97% routing accuracy (no re-routing by adjuster) *[A15]*
- **Metric 3**: Cost per claim ≤$1.55 *[A16]* (91% reduction from $16.50 baseline *[A2]*)
- **Metric 4**: 85% of claims processed without human intervention *[A10]*
- **Metric 5**: Adjuster productivity increases to 10 claims/day (25% increase from 8 baseline *[A13, A18]*)

---

## 2. Core Entities & Data Model

### Entity: Claim

**Attributes**:
```
claim_id: UUID [required, unique, immutable] // System-generated identifier
policy_number: string [required, format: /^[A-Z]{2}\d{8}$/] // From legacy system [A6]
claimant_name: string [required, max: 200] // Extracted from FNOL report
claimant_contact: object [required] // {email, phone, address}
  email: string [optional, format: email]
  phone: string [optional, format: /^\+?[1-9]\d{1,14}$/]
  address: string [optional, max: 500]
loss_date: date [required, min: policy_effective_date, max: today] // Date of incident
loss_description: string [required, max: 5000] // Narrative from claimant
claim_type: enum [required] // AUTO_COLLISION, AUTO_COMPREHENSIVE, PROPERTY, LIABILITY, etc.
claim_value_usd: decimal [optional, min: 0, max: 10000000, precision: 2] // Estimated loss
document_references: array<UUID> [required] // Links to DMS documents
extraction_confidence: object [required] // Per-field confidence scores
  policy_number: float [0.0-1.0]
  claimant_name: float [0.0-1.0]
  loss_date: float [0.0-1.0]
  overall: float [0.0-1.0] // Minimum of critical field confidences
fraud_indicators: array<string> [required, default: []] // List of detected flags [A29]
coverage_determination: enum [optional] // COVERED, NOT_COVERED, AMBIGUOUS, PENDING
coverage_confidence: float [optional, 0.0-1.0] // AI confidence in determination
assigned_adjuster_id: UUID [optional] // After routing
escalation_reason: string [optional, max: 1000] // If escalated, why?
state: enum [required] // See state machine below
created_at: timestamp [required, immutable]
updated_at: timestamp [required]
acknowledged_at: timestamp [optional] // When claimant acknowledgment sent
sla_deadline: timestamp [required] // created_at + 2 hours [A14]
```

**State Machine**:
```
States: 
  RECEIVED, EXTRACTING, EXTRACTED, VALIDATING, VALIDATED, 
  POLICY_LOOKUP, POLICY_FOUND, COVERAGE_DETERMINING, COVERAGE_DETERMINED,
  TRIAGING, TRIAGED, ROUTING, ROUTED, ACKNOWLEDGING, ACKNOWLEDGED,
  PENDING_REVIEW, PENDING_SYSTEM_ISSUE, ERROR, COMPLETED

Transitions:
  RECEIVED -> EXTRACTING [on claim intake]
  EXTRACTING -> EXTRACTED [on extraction complete, confidence ≥90% on critical fields [A24]]
  EXTRACTING -> PENDING_REVIEW [on extraction complete, confidence <90% [A24]]
  EXTRACTED -> VALIDATING [on proceed]
  VALIDATING -> VALIDATED [on validation pass]
  VALIDATING -> PENDING_REVIEW [on validation fail]
  VALIDATED -> POLICY_LOOKUP [on proceed]
  POLICY_LOOKUP -> POLICY_FOUND [on successful lookup within 30s [A26]]
  POLICY_LOOKUP -> PENDING_SYSTEM_ISSUE [on lookup timeout after 3 retries]
  POLICY_LOOKUP -> PENDING_REVIEW [on policy not found (404)]
  POLICY_FOUND -> COVERAGE_DETERMINING [on proceed]
  COVERAGE_DETERMINING -> COVERAGE_DETERMINED [on determination complete, confidence ≥85% [A20]]
  COVERAGE_DETERMINING -> PENDING_REVIEW [on determination complete, confidence <85% [A20]]
  COVERAGE_DETERMINED -> TRIAGING [on proceed]
  TRIAGING -> TRIAGED [on triage complete]
  TRIAGED -> ROUTING [if not flagged for review]
  TRIAGED -> PENDING_REVIEW [if flagged: value >$100K [A21], fraud ≥3 [A29], complex policy]
  ROUTING -> ROUTED [on routing complete, confidence ≥85% [A20]]
  ROUTING -> PENDING_REVIEW [on routing complete, confidence <85% [A20]]
  ROUTED -> ACKNOWLEDGING [on proceed]
  ACKNOWLEDGING -> ACKNOWLEDGED [on acknowledgment sent]
  ACKNOWLEDGED -> COMPLETED [on final state]
  PENDING_REVIEW -> [any prior state] [on human decision: approve/modify/retry]
  PENDING_SYSTEM_ISSUE -> POLICY_LOOKUP [on system recovery, retry]
  PENDING_SYSTEM_ISSUE -> PENDING_REVIEW [on persistent failure]
  [any state] -> ERROR [on unrecoverable error]
```

**Validations**:
- `loss_date` must be within policy effective period (validated after policy lookup)
- `claim_value_usd` if provided, must be ≤ policy coverage limit
- `policy_number` must exist in legacy system (validated during lookup)
- `extraction_confidence.overall` must be ≥90% for critical fields (policy_number, claimant_name, loss_date) to proceed autonomously *[A24]*
- `fraud_indicators` count ≥3 triggers mandatory human review *[A29]*
- `sla_deadline` breach (current_time > sla_deadline) triggers alert *[A14]*

**Assumption References**: *[A5, A6, A14, A20, A21, A24, A26, A29]*

---

### Entity: Policy

**Attributes**:
```
policy_id: UUID [required, unique] // Internal ID
policy_number: string [required, unique, format: /^[A-Z]{2}\d{8}$/] // External ID
policyholder_name: string [required]
effective_date: date [required]
expiration_date: date [required]
status: enum [required] // ACTIVE, LAPSED, CANCELLED
coverage_types: array<string> [required] // [COLLISION, COMPREHENSIVE, LIABILITY, etc.]
coverage_limits: object [required] // {coverage_type: limit_usd}
deductibles: object [required] // {coverage_type: deductible_usd}
exclusions: array<string> [required] // List of exclusion clauses
endorsements: array<string> [optional] // Special policy modifications
has_complex_exclusions: boolean [required] // Flag for escalation [A27, U1]
retrieved_at: timestamp [required] // Cache timestamp
```

**State Machine**: N/A (read-only from legacy system)

**Validations**:
- `effective_date` < `expiration_date`
- `status` must be ACTIVE for claim to be covered
- `coverage_limits` must contain at least one coverage type
- `has_complex_exclusions` = true if exclusions contain keywords: "act of God", "pre-existing", "intentional", "war", "nuclear" (triggers human review)

**Assumption References**: *[A26, A27, U1, U5]*

---

### Entity: Adjuster

**Attributes**:
```
adjuster_id: UUID [required, unique]
name: string [required]
email: string [required, format: email]
specializations: array<string> [required] // [AUTO, PROPERTY, LIABILITY, etc.]
geography: array<string> [required] // [REGION_A, REGION_B, etc.]
current_workload: integer [required, min: 0] // Active claims assigned
max_workload: integer [required, default: 15] // Capacity threshold
availability_status: enum [required] // AVAILABLE, BUSY, OUT_OF_OFFICE
seniority_level: enum [required] // JUNIOR, SENIOR, LEAD // For high-value claims [A21]
```

**State Machine**: N/A (updated by external workforce management system)

**Validations**:
- Cannot route claim if `availability_status` = OUT_OF_OFFICE
- Cannot route claim if `current_workload` ≥ `max_workload`
- High-value claims (>$100K *[A21]*) must route to `seniority_level` = SENIOR or LEAD

**Assumption References**: *[A3, A9, A19, A21]*

---

### Entity: EscalationTicket

**Attributes**:
```
ticket_id: UUID [required, unique]
claim_id: UUID [required, foreign_key: Claim]
trigger_condition: string [required, max: 500] // e.g., "claim_value > $100K [A21]"
escalation_target: enum [required] // CLAIMS_SPECIALIST, SENIOR_ADJUSTER, FRAUD_INVESTIGATOR, CLAIMS_MANAGER, IT_SUPPORT
ai_recommendation: string [optional, max: 2000] // Agent's suggested action
supporting_evidence: object [required] // {extracted_data, policy_excerpt, fraud_flags, etc.}
confidence_score: float [optional, 0.0-1.0] // If AI has recommendation
human_decision: string [optional, max: 2000] // Human's action after review
resolved_at: timestamp [optional]
response_time_sla: integer [required] // Minutes, varies by escalation_target [Section 6]
created_at: timestamp [required]
```

**State Machine**:
```
States: OPEN, IN_REVIEW, RESOLVED, CANCELLED
Transitions:
  OPEN -> IN_REVIEW [on human starts review]
  IN_REVIEW -> RESOLVED [on human provides decision]
  IN_REVIEW -> CANCELLED [on claim withdrawn/duplicate]
  OPEN -> CANCELLED [on auto-cancel after 24h no response]
```

**Validations**:
- `response_time_sla` must be met: (resolved_at - created_at) ≤ response_time_sla (alert if breached)
- `human_decision` required before state = RESOLVED
- `trigger_condition` must reference specific threshold from assumptions (A20, A21, A24, A29)

**Assumption References**: *[A5, A20, A21, A24, A29, Section 6]*

---

## 3. Agent Workflow & Decision Logic

### Component 1: Data Extraction

**Input**: 
- Unstructured claim report (email body, phone transcript, web form submission)
- Format: Plain text, HTML, or JSON (from web form)
- Source: Claim intake API endpoint or email parser

**Processing Logic**:
```
1. Detect document type (email, transcript, form) and apply appropriate parser
2. Extract fields using NLP (LLM-based extraction):
   - policy_number (regex validation: /^[A-Z]{2}\d{8}$/)
   - claimant_name (entity recognition)
   - claimant_contact.email (regex: email format)
   - claimant_contact.phone (regex: E.164 format)
   - loss_date (date parsing, validate: policy_effective ≤ loss_date ≤ today)
   - loss_description (full text, max 5000 chars)
   - claim_type (classification: AUTO_COLLISION, AUTO_COMPREHENSIVE, PROPERTY, etc.)
   - claim_value_usd (optional, extract if mentioned: "$5,000 damage", "five thousand dollars")
3. Calculate per-field confidence scores (0.0-1.0) based on:
   - OCR quality (if scanned document)
   - Entity recognition confidence
   - Format validation pass/fail
4. Calculate overall_confidence = MIN(policy_number_conf, claimant_name_conf, loss_date_conf)
5. IF overall_confidence ≥ 90% [A24] THEN proceed to validation
   ELSE escalate to human review (PENDING_REVIEW state)
6. IF document is handwritten or OCR quality <70% THEN escalate to human review
```

**Output**:
- Claim entity with extracted fields and confidence scores
- State: EXTRACTED or PENDING_REVIEW
- Destination: In-memory claim object, logged to database

**Escalation Triggers**:
- `extraction_confidence.overall` <90% *[A24]*
- `extraction_confidence.policy_number` <90% (critical field) *[A24]*
- OCR quality score <70% (handwritten/low-quality scan)
- Claim flagged as high-value/ambiguous (value >$100K *[A21]* if extractable)

**Error Handling**:
- If extraction fails (LLM timeout, parsing error): Retry once, then escalate to human with error details
- If critical field missing (policy_number, claimant_name): Escalate to human with "incomplete data" reason

**Performance Requirements**:
- Time limit: 15 seconds per claim *[A23]*
- Throughput: 300 claims/day = 12.5 claims/hour avg, must handle 30 claims/hour peak

**Assumption References**: *[A5, A6, A21, A23, A24, U2]*

---

### Component 2: Data Validation

**Input**:
- Claim entity with extracted fields (state: EXTRACTED)

**Processing Logic**:
```
1. Validate policy_number format: /^[A-Z]{2}\d{8}$/
2. Validate loss_date: must be valid date, not in future
3. Validate claimant_contact.email: valid email format (if provided)
4. Validate claimant_contact.phone: valid E.164 format (if provided)
5. Validate claim_value_usd: if provided, must be ≥0 and ≤$10M
6. Validate required fields present: policy_number, claimant_name, loss_date, loss_description
7. IF all validations pass THEN proceed to policy lookup (state: VALIDATED)
   ELSE create validation error report, escalate to human (state: PENDING_REVIEW)
```

**Output**:
- Claim entity with validation_status = PASS or FAIL
- State: VALIDATED or PENDING_REVIEW
- If FAIL: validation_errors array listing specific failures

**Escalation Triggers**:
- Any validation rule fails (missing required field, invalid format)
- Validation escalation is always human-correctable (specialist fixes data, agent retries)

**Error Handling**:
- Validation errors are deterministic (no retries needed)
- Escalate with specific error messages: "Policy number format invalid: expected AA12345678, got ABC123"

**Performance Requirements**:
- Time limit: 2 seconds per claim *[A25]*
- Throughput: Same as extraction (300 claims/day)

**Assumption References**: *[A6, A25]*

---

### Component 3: Policy Lookup

**Input**:
- Claim entity with validated policy_number (state: VALIDATED)

**Processing Logic**:
```
1. Call legacy policy administration system SOAP API (see Section 4 for integration details)
2. Request: PolicyLookupRequest with policy_number and loss_date
3. Parse response: PolicyLookupResponse with policy details
4. IF response success (200) THEN:
   a. Create Policy entity from response
   b. Validate policy.status = ACTIVE (if not, escalate: "Policy lapsed/cancelled")
   c. Validate loss_date within [policy.effective_date, policy.expiration_date]
   d. Set claim.state = POLICY_FOUND
5. IF response 404 (policy not found) THEN:
   a. Escalate to human: "Policy not found. Possible typo in policy number?"
   b. Set claim.state = PENDING_REVIEW
6. IF response 500/503 (system error) THEN:
   a. Retry with exponential backoff: 1s, 2s, 4s (3 attempts total)
   b. If all retries fail: escalate to human + IT support
   c. Set claim.state = PENDING_SYSTEM_ISSUE
7. IF timeout (>30s [A26]) THEN:
   a. Retry (same logic as 500/503)
```

**Output**:
- Policy entity (cached for claim processing)
- Claim state: POLICY_FOUND, PENDING_REVIEW, or PENDING_SYSTEM_ISSUE

**Escalation Triggers**:
- Policy not found (404) → human investigates (typo, lapsed policy, data entry error)
- Policy status ≠ ACTIVE → human investigates (can claim proceed? grace period?)
- Loss date outside policy period → human investigates (coverage dispute)
- System timeout/unavailable after 3 retries → human + IT support

**Error Handling**:
- Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s) *[A26]*
- Fallback: Escalate to human with error details (error code, response body, retry history)
- If system is down for >1 hour, alert IT team and operations manager

**Performance Requirements**:
- Time limit: 10 seconds per claim (baseline) *[A26]*, 30 seconds worst-case
- Timeout: 30 seconds per API call
- Throughput: Must handle 300 lookups/day, consider parallel processing if latency >30s *[U5]*

**Assumption References**: *[A26, U5]*

---

### Component 4: Coverage Determination

**Input**:
- Claim entity (state: POLICY_FOUND)
- Policy entity (from lookup)

**Processing Logic**:
```
1. Check straightforward coverage rules:
   a. claim.claim_type IN policy.coverage_types? (e.g., AUTO_COLLISION in [COLLISION, COMPREHENSIVE])
   b. claim.loss_date IN [policy.effective_date, policy.expiration_date]?
   c. claim.claim_value_usd ≤ policy.coverage_limits[claim.claim_type]? (if value provided)
2. Check exclusions:
   a. Parse claim.loss_description for exclusion keywords
   b. IF policy.has_complex_exclusions = true THEN flag for human review
   c. IF exclusion detected (e.g., "intentional damage", "pre-existing") THEN:
      - Set coverage_determination = NOT_COVERED
      - Set coverage_confidence based on keyword match strength
3. Run ML model (if available [U2]) for ambiguous cases:
   a. Input: claim details + policy details
   b. Output: coverage_determination (COVERED/NOT_COVERED/AMBIGUOUS), confidence score
4. Decision logic:
   a. IF coverage_confidence ≥85% [A20] AND policy.has_complex_exclusions = false THEN:
      - Set claim.coverage_determination autonomously
      - Proceed to triage (state: COVERAGE_DETERMINED)
   b. ELSE:
      - Escalate to human (state: PENDING_REVIEW)
      - Provide AI recommendation + supporting evidence (policy excerpt, exclusion match)
5. Special cases:
   a. IF claim.fraud_indicators.length ≥3 [A29] THEN escalate to fraud investigator
   b. IF claim.claim_value_usd >$100K [A21] THEN escalate to claims manager
```

**Output**:
- Claim.coverage_determination: COVERED, NOT_COVERED, AMBIGUOUS, or PENDING
- Claim.coverage_confidence: 0.0-1.0
- State: COVERAGE_DETERMINED or PENDING_REVIEW

**Escalation Triggers**:
- `coverage_confidence` <85% *[A20]*
- `policy.has_complex_exclusions` = true
- `fraud_indicators` ≥3 *[A29]*
- `claim_value_usd` >$100K *[A21]*
- Novel claim type (not well-represented in training data *[U2]*)

**Error Handling**:
- If ML model fails (timeout, error): Fall back to rule-based system (lower confidence, likely escalates)
- If rule-based system is ambiguous: Escalate with "coverage ambiguity" reason

**Performance Requirements**:
- Time limit: 8 seconds per claim *[A28]*
- Throughput: 300 claims/day

**Assumption References**: *[A5, A6, A9, A10, A20, A21, A27, A28, A29, U1, U2]*

---

### Component 5: Severity/Complexity Triage

**Input**:
- Claim entity (state: COVERAGE_DETERMINED)
- Policy entity

**Processing Logic**:
```
1. Calculate severity score (0-100):
   a. Claim value: 0-30 points (0 for <$1K, 30 for >$100K, linear scale)
   b. Fraud indicators: 10 points per indicator (max 30)
   c. Policy complexity: 20 points if has_complex_exclusions = true
   d. Coverage confidence: 20 points if coverage_confidence <85% [A20]
2. Classify severity:
   a. severity_score <30: ROUTINE
   b. severity_score 30-60: MODERATE
   c. severity_score >60: HIGH
3. Determine oversight requirement:
   a. IF severity = HIGH OR claim_value >$100K [A21] OR fraud_indicators ≥3 [A29] THEN:
      - Flag for human review
      - Set escalation_reason with specific triggers
      - Set claim.state = PENDING_REVIEW
   b. ELSE:
      - Proceed autonomously
      - Set claim.state = TRIAGED
4. Generate triage report:
   a. Severity classification
   b. Key risk factors (value, fraud, complexity)
   c. Recommended oversight level (autonomous vs. human review)
   d. Confidence score for triage decision
```

**Output**:
- Claim.severity_classification: ROUTINE, MODERATE, HIGH
- Claim.requires_human_oversight: boolean
- State: TRIAGED or PENDING_REVIEW

**Escalation Triggers**:
- Severity = HIGH
- `claim_value_usd` >$100K *[A21]*
- `fraud_indicators` ≥3 *[A29]*
- `coverage_confidence` <85% *[A20]*
- `policy.has_complex_exclusions` = true
- AI triage confidence <85% *[A20]*

**Error Handling**:
- Triage logic is deterministic (rule-based scoring), minimal error risk
- If ML-based triage model fails: Fall back to rule-based scoring (conservative, may over-escalate)

**Performance Requirements**:
- Time limit: 10 seconds per claim *[A30]*
- Throughput: 300 claims/day

**Assumption References**: *[A5, A6, A10, A20, A21, A29, A30, A31, U1, U2, U12]*

---

### Component 6: Adjuster Routing

**Input**:
- Claim entity (state: TRIAGED, requires_human_oversight = false)
- List of available Adjuster entities

**Processing Logic**:
```
1. Filter adjusters by criteria:
   a. specializations CONTAINS claim.claim_type
   b. geography CONTAINS claim.loss_location (extract from address)
   c. availability_status = AVAILABLE
   d. current_workload < max_workload
   e. IF claim_value >$100K [A21] THEN seniority_level IN [SENIOR, LEAD]
2. Rank filtered adjusters:
   a. Primary: Lowest current_workload (load balancing)
   b. Secondary: Highest specialization match score
   c. Tertiary: Geographic proximity (if available)
3. Select top-ranked adjuster:
   a. IF confidence in selection ≥85% [A20] THEN:
      - Assign claim.assigned_adjuster_id
      - Increment adjuster.current_workload
      - Set claim.state = ROUTED
   b. ELSE:
      - Escalate to human for routing decision
      - Provide top 3 adjuster recommendations with rationale
      - Set claim.state = PENDING_REVIEW
4. Special cases:
   a. IF no adjusters available (all at max_workload or out_of_office) THEN:
      - Escalate to operations manager: "No available adjusters"
      - Set claim.state = PENDING_REVIEW
   b. IF claim flagged as VIP or sensitive THEN:
      - Escalate to senior adjuster or claims manager for manual assignment
```

**Output**:
- Claim.assigned_adjuster_id: UUID
- Claim.routing_confidence: 0.0-1.0
- State: ROUTED or PENDING_REVIEW

**Escalation Triggers**:
- Routing confidence <85% *[A20]*
- No available adjusters (all at capacity or unavailable)
- Claim value >$100K *[A21]* (requires senior adjuster, human confirms)
- VIP claimant or sensitive circumstances (detected from claim metadata)

**Error Handling**:
- If adjuster assignment fails (CRM API error): Retry once, then escalate to human + IT support
- If adjuster rejects claim within 1 hour ("Not My Claim" button): Log routing error, re-route automatically or escalate if confidence <85%

**Performance Requirements**:
- Time limit: 3 seconds per claim *[A33]*
- Throughput: 300 claims/day

**Assumption References**: *[A3, A5, A9, A10, A19, A20, A21, A33, U2, U4]*

---

### Component 7: Claimant Acknowledgment

**Input**:
- Claim entity (state: ROUTED)
- Assigned Adjuster entity

**Processing Logic**:
```
1. Generate acknowledgment message using template:
   Template:
   "Dear [claimant_name],
   
   We have received your claim (#[claim_id]) regarding [claim_type] on [loss_date]. 
   
   Your claim is being reviewed by [adjuster_name] ([adjuster_email], [adjuster_phone]).
   You can expect to hear from your adjuster within [timeframe] business days.
   
   Your claim number for reference: [claim_id]
   
   If you have questions, please contact [adjuster_name] directly or call our claims hotline at 1-800-XXX-XXXX.
   
   Sincerely,
   [Company Name] Claims Team"
   
2. Populate template variables:
   - claimant_name, claim_id, claim_type, loss_date from Claim entity
   - adjuster_name, adjuster_email, adjuster_phone from Adjuster entity
   - timeframe: 2 business days (standard) or 1 business day (if high-value)
3. Send acknowledgment:
   a. Primary channel: Email to claimant_contact.email (if provided)
   b. Secondary channel: SMS to claimant_contact.phone (if provided and email fails)
   c. Log acknowledgment in CRM
4. Update claim:
   a. Set claim.acknowledged_at = current_timestamp
   b. Set claim.state = ACKNOWLEDGED
5. Check SLA compliance:
   a. IF acknowledged_at ≤ sla_deadline (created_at + 2 hours [A14]) THEN SLA met
   b. ELSE log SLA breach, send apology message, alert operations manager
```

**Output**:
- Acknowledgment message sent via email/SMS
- Claim.acknowledged_at: timestamp
- State: ACKNOWLEDGED

**Escalation Triggers**:
- Email/SMS delivery fails (bounce, invalid address): Escalate to specialist for manual outreach
- Claimant has special communication preferences (language, accessibility): Escalate for human review of message *[U11]*
- Claim involves sensitive circumstances (death, severe injury): Escalate for human review of tone/content

**Error Handling**:
- If email send fails: Retry once, then attempt SMS, then escalate to specialist
- If template generation fails (LLM timeout): Use fallback static template, log error

**Performance Requirements**:
- Time limit: 5 seconds per claim *[A36]*
- Throughput: 300 claims/day
- SLA: Must send within 2 hours of claim receipt *[A14]*

**Assumption References**: *[A6, A14, A34, A36, U11]*

---

### Component 8: System Updates

**Input**:
- Claim entity (state: ACKNOWLEDGED)

**Processing Logic**:
```
1. Update CRM:
   a. Create claim record with all claim fields
   b. Link to policy record (policy_id)
   c. Link to adjuster record (assigned_adjuster_id)
   d. Set claim status = OPEN
   e. API: POST /api/v1/claims (see Section 4 for integration details)
2. Upload documents to DMS:
   a. Original claim report (email, transcript, form)
   b. Extracted data summary (JSON)
   c. Policy details (PDF or JSON)
   d. Acknowledgment message (PDF)
   e. API: POST /api/v1/documents (see Section 4)
3. Update claim state:
   a. Set claim.state = COMPLETED
   b. Log final timestamp
4. Trigger downstream workflows:
   a. Notify adjuster (email/Slack) with claim details
   b. Schedule follow-up tasks in CRM (adjuster review, claimant contact)
```

**Output**:
- CRM record created (claim_id in CRM)
- Documents uploaded to DMS (document_ids)
- State: COMPLETED

**Escalation Triggers**:
- CRM API fails after retries: Escalate to IT support + specialist (manual data entry)
- DMS upload fails after retries: Escalate to IT support (documents stored locally, manual upload)

**Error Handling**:
- If API call fails (500, 503): Retry 3 times with exponential backoff (1s, 2s, 4s)
- If all retries fail: Escalate to human + IT support, store data locally for manual entry
- If partial success (CRM succeeds, DMS fails): Continue processing, log error, retry DMS in background

**Performance Requirements**:
- Time limit: 8 seconds per claim *[A37]*
- Throughput: 300 claims/day

**Assumption References**: *[A6, A34, A37, U5]*

---

### Component 9: Exception Handling

**Input**:
- Claim entity in any state
- Exception trigger (missing data, system error, claimant dispute, etc.)

**Processing Logic**:
```
1. Detect exception type:
   a. MISSING_DATA: Required field missing after extraction
   b. SYSTEM_ERROR: Integration failure (CRM, policy admin, DMS)
   c. CLAIMANT_UNREACHABLE: Email/SMS bounce, no response
   d. COVERAGE_DISPUTE: Claimant disputes coverage determination
   e. FRAUD_INVESTIGATION: Fraud indicators require investigation
2. Create EscalationTicket:
   a. Set trigger_condition = exception type + details
   b. Set escalation_target based on exception type:
      - MISSING_DATA, CLAIMANT_UNREACHABLE → CLAIMS_SPECIALIST
      - SYSTEM_ERROR → IT_SUPPORT + CLAIMS_SPECIALIST
      - COVERAGE_DISPUTE → CLAIMS_MANAGER
      - FRAUD_INVESTIGATION → FRAUD_INVESTIGATOR
   c. Provide AI recommendation (if applicable):
      - MISSING_DATA: "Contact claimant for missing info: [field]"
      - SYSTEM_ERROR: "Retry after system recovery, or manual entry"
      - COVERAGE_DISPUTE: "Review policy section [X], consider appeal"
   d. Attach supporting evidence (claim details, error logs, policy excerpt)
3. Notify escalation target:
   a. Send email/Slack with ticket details
   b. Set response_time_sla based on severity (15-120 min)
4. Pause claim processing:
   a. Set claim.state = PENDING_REVIEW or PENDING_SYSTEM_ISSUE
   b. Wait for human decision
5. Resume processing on human decision:
   a. Human provides decision (approve, modify, reject, request more info)
   b. Agent updates claim based on decision
   c. Agent retries failed step or proceeds to next step
```

**Output**:
- EscalationTicket created
- Claim state: PENDING_REVIEW or PENDING_SYSTEM_ISSUE
- Human notified

**Escalation Triggers**:
- All exceptions escalate to human (by definition, exceptions are non-standard)

**Error Handling**:
- Exception handling itself should not fail (defensive programming)
- If escalation notification fails: Log error, retry notification, alert operations manager

**Performance Requirements**:
- Exception detection: Real-time (as soon as exception occurs)
- Human response time: Varies by exception type (15-120 min SLA)
- Exception rate: Expected 8% of claims *[A38]*, alert if >15%

**Assumption References**: *[A38, U1, U2, U3, U10]*

---

### Component 10: Quality Assurance

**Input**:
- All completed claims (state: COMPLETED)
- Real-time monitoring data (API logs, state transitions, timestamps)

**Processing Logic**:
```
1. Real-time monitoring (continuous):
   a. Track SLA compliance: % claims acknowledged within 2 hours [A14]
   b. Track routing accuracy: % claims not re-routed by adjuster
   c. Track escalation rate: % claims escalated to human [A5]
   d. Track processing time: Median time from RECEIVED to ACKNOWLEDGED
   e. Track system uptime: % API calls successful within timeout
   f. Alert if any metric breaches threshold (see Section 8 for thresholds)
2. Daily QA audit (automated):
   a. Sample 5% of autonomous claims (random selection)
   b. Review extraction accuracy: Compare extracted fields to source document
   c. Review coverage determination: Compare AI decision to policy terms
   d. Review routing: Check adjuster specialization match
   e. Calculate error rates by component (extraction, coverage, routing)
   f. Generate daily QA report with error breakdown
3. Error detection:
   a. Adjuster clicks "Not My Claim": Log routing error, investigate root cause
   b. Adjuster disputes coverage: Log coverage error, investigate root cause
   c. SLA breach: Log breach, investigate bottleneck (extraction time? policy lookup latency?)
   d. Confidence distribution shift: Alert if >30% of claims have confidence <85% (model drift)
4. Root cause analysis (human-led, AI-supported):
   a. Agent provides error context: claim details, decision rationale, confidence scores
   b. Human investigates: Data quality issue? Model drift? Policy change? System latency?
   c. Human decides remediation: Retrain model? Update rules? Fix data? Escalate to IT?
5. Continuous improvement:
   a. Log all errors for model retraining [U2]
   b. Track error trends over time (improving? degrading?)
   c. Adjust thresholds if needed (A20, A21, A24, A29) based on error cost vs. escalation cost
```

**Output**:
- Real-time monitoring dashboard (metrics, alerts)
- Daily QA report (error rates, sample audit results)
- Error logs (for retraining, root cause analysis)

**Escalation Triggers**:
- Any metric breaches alert threshold (see Section 8)
- Error rate exceeds target (>3% for routing *[A9]*, >5% for extraction)
- Confidence distribution shifts (indicates model drift or data quality issue)
- SLA breach rate exceeds 10% in any 4-hour window

**Error Handling**:
- QA monitoring should not disrupt claim processing (background process)
- If monitoring fails: Alert IT team, continue processing (blind operation)

**Performance Requirements**:
- Real-time monitoring: <1 sec latency for metric updates
- Daily audit: Complete within 1 hour (automated, runs overnight)
- Human QA review: 45 min/day *[A39]*

**Assumption References**: *[A9, A14, A15, A39, A40, U6, U10]*

---

## 4. System Inputs and Outputs

### System-Level Inputs

**Input 1: Unstructured Claim Reports**

**Source**: Multiple channels (email, phone transcripts, web forms, mobile app submissions)

**Format**:
- **Email**: Plain text or HTML body, may include inline images or attachments (PDF, JPG, PNG)
- **Phone Transcript**: Plain text (from call center transcription service), may include agent notes
- **Web Form**: JSON payload with structured fields + free-text description
- **Mobile App**: JSON payload with structured fields + photos (JPG/PNG, max 10MB per photo *[A34]*)

**Volume**: 300 reports/day *[A6]*, distributed across channels:
- Email: 45% (135/day)
- Phone: 30% (90/day)
- Web Form: 20% (60/day)
- Mobile App: 5% (15/day)

**Arrival Pattern**: 
- Peak hours: 9am-11am, 2pm-4pm (50% of daily volume)
- Off-peak: 11am-2pm, 4pm-6pm (30% of daily volume)
- After-hours: 6pm-9am (20% of daily volume, queued for next business day)

**Quality Characteristics**:
- **Email**: Variable quality, may include forwarded messages, signatures, disclaimers (OCR confidence: 70-95% *[A24]*)
- **Phone**: Transcription errors possible (OCR confidence: 80-95%)
- **Web Form**: High quality, structured fields pre-validated (OCR confidence: 95-99%)
- **Mobile App**: High quality, photos may have lighting/angle issues (OCR confidence: 90-98%)

**Required Fields** (must be extractable or provided):
- Policy number (format: /^[A-Z]{2}\d{8}$/ *[A6]*)
- Claimant name (string, max 200 chars)
- Contact information (email OR phone, at least one required)
- Loss date (date, format: YYYY-MM-DD)
- Loss description (string, max 5000 chars)

**Optional Fields**:
- Claim value estimate (decimal, USD)
- Loss location (address string)
- Photos/documents (attachments)
- Police report number (string)
- Witness information (string)

**Delivery Mechanism**:
- **Email**: IMAP/POP3 polling (every 5 minutes) or webhook from email service
- **Phone**: REST API callback from call center system (real-time)
- **Web Form**: REST API POST to `/api/v1/claims/intake` (real-time)
- **Mobile App**: REST API POST to `/api/v1/claims/intake` (real-time)

**Assumption References**: *[A6, A24, A34, U2]*

---

**Input 2: Policy Data (from Legacy Policy Administration System)**

**Source**: Legacy Policy Administration System (PolicyAdmin) via SOAP API

**Format**: XML (SOAP envelope, see Section 4 Integration 1 for schema)

**Trigger**: On-demand lookup per claim (triggered by Component 3: Policy Lookup)

**Volume**: 300 lookups/day (one per claim)

**Latency**: 10-30 seconds per lookup *[A26, U5]*

**Availability**: 99%+ uptime (assumed, actual unknown *[U5]*)

**Fields Retrieved**:
- Policy ID (UUID, internal identifier)
- Policy number (string, external identifier)
- Policyholder name (string)
- Effective date (date)
- Expiration date (date)
- Status (enum: ACTIVE, LAPSED, CANCELLED)
- Coverage types (array of strings: AUTO_COLLISION, AUTO_COMPREHENSIVE, PROPERTY, LIABILITY, etc.)
- Coverage limits (object: {coverage_type: limit_usd})
- Deductibles (object: {coverage_type: deductible_usd})
- Exclusions (array of strings: exclusion clause text)
- Endorsements (array of strings: special policy modifications)

**Error Conditions**:
- **404 (PolicyNotFound)**: Policy number does not exist in system → escalate to human
- **500 (Server Error)**: System error → retry 3 times, then escalate
- **503 (Service Unavailable)**: System temporarily down → retry 3 times, then escalate
- **Timeout (>30 sec)**: No response → retry 3 times, then escalate

**Caching Strategy**:
- Cache policy data for 24 hours (policies rarely change mid-day)
- Invalidate cache if policy lookup returns different data than cached
- Cache key: policy_number + loss_date (loss_date affects policy period validation)

**Assumption References**: *[A26, U5]*

---

**Input 3: Adjuster Availability Data (from CRM/Workforce Management System)**

**Source**: CRM system or workforce management system

**Format**: JSON (REST API response)

**Trigger**: On-demand query per claim (triggered by Component 6: Adjuster Routing)

**Volume**: 300 queries/day (one per claim that reaches routing step, ~85% of claims *[A10]*)

**Latency**: <2 seconds per query (assumed, REST API)

**Refresh Rate**: Real-time (adjuster availability updates as claims are assigned/closed)

**Fields Retrieved**:
- Adjuster ID (UUID)
- Name (string)
- Email (string)
- Phone (string)
- Specializations (array of strings: AUTO, PROPERTY, LIABILITY, etc.)
- Geography (array of strings: REGION_A, REGION_B, etc.)
- Current workload (integer: number of active claims)
- Max workload (integer: capacity threshold, typically 15 *[A19]*)
- Availability status (enum: AVAILABLE, BUSY, OUT_OF_OFFICE)
- Seniority level (enum: JUNIOR, SENIOR, LEAD)

**Error Conditions**:
- **500 (Server Error)**: System error → retry once, then escalate to human for manual routing
- **Empty Result Set**: No adjusters available → escalate to operations manager

**Assumption References**: *[A19]*

---

**Input 4: Fraud Detection Signals (from Fraud Detection Service, if available)**

**Source**: External fraud detection service (e.g., LexisNexis, SAS Fraud Management) OR internal rule-based system

**Format**: JSON (REST API response)

**Trigger**: On-demand query per claim (triggered by Component 4: Coverage Determination)

**Volume**: 300 queries/day (one per claim)

**Latency**: <5 seconds per query (assumed)

**Availability**: Optional (if service unavailable, use internal rule-based fraud detection *[A29]*)

**Fields Retrieved**:
- Fraud risk score (float: 0.0-1.0, higher = more suspicious)
- Fraud indicators (array of strings: flag names)
- Indicator details (object: {indicator_name: evidence})

**Example Fraud Indicators**:
- `recent_policy_inception`: Policy effective date within 30 days of claim
- `claim_near_limit`: Claim value >80% of policy limit
- `inconsistent_description`: Loss description inconsistent with damage photos (NLP analysis)
- `multiple_claims_short_period`: Claimant has 3+ claims in past 12 months
- `suspicious_claimant_history`: Claimant flagged in fraud database
- `unusual_loss_location`: Loss location far from claimant's address
- `duplicate_claim`: Similar claim already filed (same loss date, location, description)

**Threshold**: If fraud_indicators.length ≥3 *[A29]*, escalate to fraud investigator

**Fallback (if service unavailable)**: Use internal rule-based system:
- Check policy inception date (if <30 days, flag `recent_policy_inception`)
- Check claim value vs. limit (if >80%, flag `claim_near_limit`)
- Check claimant history in CRM (if 3+ claims in 12 months, flag `multiple_claims_short_period`)

**Assumption References**: *[A29]*

---

**Input 5: Human Decisions (from Escalation Workflow)**

**Source**: CRM system (EscalationTicket entity updated by human reviewers)

**Format**: JSON (REST API response or database query)

**Trigger**: Polling (every 30 seconds) or webhook (real-time notification when ticket resolved)

**Volume**: 45 decisions/day (15% of claims escalated *[A5]*)

**Latency**: Variable (depends on human response time, SLA: 15-120 minutes per escalation type, see Section 6)

**Fields Retrieved**:
- Ticket ID (UUID)
- Claim ID (UUID, link to Claim entity)
- Human decision (string: "APPROVE", "MODIFY", "REJECT", "REQUEST_MORE_INFO")
- Decision rationale (string: explanation of decision)
- Modified fields (object: {field_name: new_value}, if decision = "MODIFY")
- Next action (string: "PROCEED_TO_NEXT_STEP", "RETRY_CURRENT_STEP", "MANUAL_PROCESSING", "CLOSE_CLAIM")

**Decision Types**:
- **APPROVE**: Human approves AI recommendation, agent proceeds to next step
- **MODIFY**: Human modifies AI recommendation (e.g., route to different adjuster), agent proceeds with modified data
- **REJECT**: Human rejects claim or coverage, agent closes claim with NOT_COVERED status
- **REQUEST_MORE_INFO**: Human needs more information from claimant, agent sends follow-up request and pauses processing

**Assumption References**: *[A5, A31]*

---

### System-Level Outputs

**Output 1: Claimant Acknowledgment**

**Destination**: Claimant (via email, SMS, or both)

**Format**: 
- **Email**: HTML with plain text fallback, sent via SMTP or email service API (e.g., SendGrid, AWS SES)
- **SMS**: Plain text, max 160 chars, sent via SMS gateway API (e.g., Twilio)

**Trigger**: After claim successfully routed (Component 7: Claimant Acknowledgment)

**Volume**: 300 acknowledgments/day (one per claim)

**Timing**: Within 2 hours of claim receipt *[A14, Metric 1]*, typically within 2 minutes for autonomous claims

**Content** (see Component 7 for template):
- Claim number (UUID)
- Claim type (e.g., AUTO_COLLISION)
- Loss date
- Assigned adjuster name, email, phone
- Expected next steps (adjuster will contact within X business days)
- Claims hotline number (for questions)

**Delivery Confirmation**:
- Email: Track open rate, bounce rate (log in CRM)
- SMS: Track delivery status (log in CRM)
- If delivery fails (bounce, invalid number): Escalate to specialist for manual outreach

**Assumption References**: *[A14, A34, A36, U11]*

---

**Output 2: Claim Record (in CRM)**

**Destination**: CRM system (via REST API)

**Format**: JSON (see Section 4 Integration 2 for schema)

**Trigger**: After acknowledgment sent (Component 8: System Updates)

**Volume**: 300 records/day (one per claim)

**Timing**: Within 3 minutes of claim receipt (for autonomous claims), within 20 minutes for escalated claims

**Fields Written**:
- Claim ID (UUID, system-generated)
- Policy ID (UUID, from policy lookup)
- Policy number (string)
- Claimant name, email, phone, address
- Loss date, description, type, value
- Coverage determination (COVERED, NOT_COVERED, PENDING)
- Assigned adjuster ID (UUID)
- Status (OPEN, PENDING_REVIEW, CLOSED)
- Created timestamp, acknowledged timestamp
- SLA deadline, SLA status (MET, BREACHED)
- Escalation ticket ID (if escalated)

**Record Lifecycle**:
- Created: When claim reaches COMPLETED state (Component 8)
- Updated: When adjuster updates claim (outside agent scope)
- Closed: When adjuster closes claim (outside agent scope)

**Assumption References**: *[A37]*

---

**Output 3: Documents (in Document Management System)**

**Destination**: Document Management System (DMS) via REST API

**Format**: Multipart/form-data (file upload + JSON metadata, see Section 4 Integration 3 for schema)

**Trigger**: After CRM record created (Component 8: System Updates)

**Volume**: 1,200 documents/day (4 documents per claim × 300 claims)

**Timing**: Within 5 minutes of claim receipt (for autonomous claims), within 25 minutes for escalated claims

**Document Types**:
1. **FNOL_REPORT**: Original claim report (email body, transcript, form submission)
   - Format: PDF (converted from email/text) or original format (if already PDF)
   - Size: Typically 50-500 KB
2. **EXTRACTED_DATA**: JSON summary of extracted fields + confidence scores
   - Format: JSON
   - Size: Typically 5-10 KB
3. **POLICY_DETAILS**: Policy information from legacy system
   - Format: JSON (converted from SOAP XML response)
   - Size: Typically 10-20 KB
4. **ACKNOWLEDGMENT**: Claimant acknowledgment message
   - Format: PDF (generated from email template)
   - Size: Typically 20-50 KB

**Metadata** (attached to each document):
- Claim ID (UUID, link to claim)
- Document type (enum: FNOL_REPORT, EXTRACTED_DATA, POLICY_DETAILS, ACKNOWLEDGMENT)
- File name (string)
- Uploaded by (string: "fnol_agent")
- Uploaded timestamp (datetime)

**Assumption References**: *[A37]*

---

**Output 4: Escalation Tickets (in CRM)**

**Destination**: CRM system (via REST API)

**Format**: JSON (see Section 4 Integration 2 for schema)

**Trigger**: When escalation condition detected (Components 1-6, 9)

**Volume**: 45 tickets/day (15% of claims *[A5]*)

**Timing**: Immediately upon escalation detection (within seconds)

**Fields Written**:
- Ticket ID (UUID, system-generated)
- Claim ID (UUID, link to claim)
- Trigger condition (string: specific threshold violated, e.g., "claim_value = $150K > $100K [A21]")
- Escalation target (enum: CLAIMS_SPECIALIST, SENIOR_ADJUSTER, FRAUD_INVESTIGATOR, CLAIMS_MANAGER, IT_SUPPORT, OPERATIONS_MANAGER)
- AI recommendation (string: suggested action, if confidence >50%)
- Supporting evidence (JSON object: extracted data, policy excerpt, fraud indicators, error logs, etc.)
- Confidence score (float: 0.0-1.0, if AI has recommendation)
- Response time SLA (integer: minutes, varies by escalation target, see Section 6)
- Status (enum: OPEN, IN_REVIEW, RESOLVED, CANCELLED)
- Created timestamp
- Resolved timestamp (when human provides decision)
- Human decision (string: populated by human reviewer)

**Notification** (triggered when ticket created):
- Email to escalation target (contains ticket summary + link to CRM)
- Slack message to escalation target (if integration available)
- SMS to escalation target (for urgent escalations: SLA breach, system failure)

**Assumption References**: *[A5, A20, A21, A24, A29]*

---

**Output 5: Adjuster Notifications**

**Destination**: Assigned adjuster (via email, Slack, or CRM notification)

**Format**: 
- **Email**: HTML with plain text fallback
- **Slack**: Formatted message with action buttons
- **CRM Notification**: In-app notification (bell icon)

**Trigger**: After claim routed and CRM record created (Component 8: System Updates)

**Volume**: 255 notifications/day (85% of claims processed autonomously *[A10]*)

**Timing**: Within 5 minutes of claim routing

**Content**:
- Claim number (UUID)
- Claimant name, contact info
- Claim type, loss date, loss description
- Claim value (if provided)
- Coverage determination (COVERED, NOT_COVERED)
- Priority (ROUTINE, MODERATE, HIGH based on severity triage)
- Link to claim details in CRM
- Action required: "Review claim and contact claimant within X business days"

**Action Buttons** (in Slack/CRM):
- "View Claim" (link to CRM)
- "Not My Claim" (triggers routing error investigation, see Failure Mode 1 in Section 8.3)
- "Request More Info" (creates follow-up task)

**Assumption References**: *[A10]*

---

**Output 6: Quality Metrics (to Monitoring Dashboard)**

**Destination**: Monitoring dashboard (Grafana, Datadog, or custom dashboard)

**Format**: Time-series metrics (Prometheus format or equivalent)

**Trigger**: Continuous (metrics emitted in real-time as claims are processed)

**Volume**: ~50 metric data points per claim × 300 claims/day = 15,000 data points/day

**Timing**: Real-time (1-second granularity for critical metrics, 1-minute for non-critical)

**Metrics Emitted** (see Section 8.4 for full list):

**Real-Time Metrics**:
- `claims_received_total` (counter): Total claims received, labeled by channel (email, phone, web, mobile)
- `claims_processed_total` (counter): Total claims processed, labeled by outcome (autonomous, escalated, error)
- `claim_processing_duration_seconds` (histogram): Time from receipt to acknowledgment, labeled by outcome
- `sla_compliance_rate` (gauge): % of claims acknowledged within 2 hours *[A14]*
- `routing_accuracy_rate` (gauge): % of claims not re-routed *[A15]*
- `escalation_rate` (gauge): % of claims escalated to human *[A5]*
- `system_integration_uptime` (gauge): % of API calls successful, labeled by system (PolicyAdmin, CRM, DMS)
- `ai_confidence_distribution` (histogram): Distribution of AI confidence scores, labeled by component

**Component-Specific Metrics**:
- `extraction_duration_seconds` (histogram): Time for data extraction *[A23]*
- `extraction_confidence` (histogram): Confidence scores for extracted fields *[A24]*
- `policy_lookup_duration_seconds` (histogram): Time for policy lookup *[A26]*
- `coverage_determination_duration_seconds` (histogram): Time for coverage determination *[A28]*
- `routing_duration_seconds` (histogram): Time for adjuster routing *[A33]*

**Error Metrics**:
- `extraction_errors_total` (counter): Extraction errors, labeled by field (policy_number, claimant_name, etc.)
- `coverage_errors_total` (counter): Coverage determination errors (detected by adjuster feedback or QA audit)
- `routing_errors_total` (counter): Routing errors (adjuster clicks "Not My Claim")
- `system_errors_total` (counter): System integration errors, labeled by system and error type

**Alert Conditions** (see Section 8.4 for thresholds):
- SLA compliance rate <90% in any 4-hour window
- Routing accuracy rate <90% in any day
- Escalation rate <10% or >25% in any day
- System integration uptime <95% in any hour
- AI confidence distribution shift (>30% of decisions with confidence <85%)

**Assumption References**: *[A5, A8, A9, A14, A15, A20, A23, A24, A26, A28, A30, A33, A36, A37, A39]*

---

**Output 7: Daily QA Report**

**Destination**: QA team + operations manager (via email)

**Format**: PDF report with charts and tables

**Trigger**: Automated daily at 6am (covers previous business day)

**Volume**: 1 report/day

**Timing**: Generated overnight (processing time: ~30 minutes)

**Content**:

1. **Summary Statistics**:
   - Total claims processed: 300
   - Autonomous claims: 255 (85%)
   - Escalated claims: 45 (15%)
   - SLA compliance rate: 96%
   - Routing accuracy rate: 97%
   - Cost per claim: $1.55 avg

2. **Error Breakdown** (by component):
   - Extraction errors: 5 (1.7%)
   - Coverage errors: 2 (0.7%)
   - Routing errors: 9 (3.0%)
   - System errors: 3 (1.0%)

3. **Escalation Analysis**:
   - By trigger: High-value (12), Low confidence (18), Fraud (8), Complex policy (7)
   - By target: Claims Specialist (25), Senior Adjuster (12), Fraud Investigator (8)
   - Avg human review time: 12 minutes

4. **Sample Audit Results** (5% random sample = 15 claims):
   - Extraction accuracy: 14/15 correct (93%)
   - Coverage accuracy: 15/15 correct (100%)
   - Routing accuracy: 14/15 correct (93%)

5. **Trends** (week-over-week comparison):
   - SLA compliance: 96% (↑2% from last week)
   - Routing accuracy: 97% (↔ no change)
   - Escalation rate: 15% (↓3% from last week)

6. **Action Items**:
   - Investigate extraction errors for handwritten forms (5 errors, all handwritten)
   - Review routing logic for property claims (3 errors, all property)
   - Schedule model retraining for coverage determination (2 errors, same exclusion missed)

**Assumption References**: *[A39]*

---

**Output 8: Error Logs (for Model Retraining)**

**Destination**: ML training pipeline (data lake or training data repository)

**Format**: JSONL (JSON Lines, one JSON object per line)

**Trigger**: Continuous (errors logged as they occur)

**Volume**: ~30 errors/day (10% of claims have some error detected *[A9, A22, A27, A32]*)

**Timing**: Real-time (errors written to log immediately)

**Fields Logged**:
- Error ID (UUID)
- Claim ID (UUID, link to claim)
- Component (enum: EXTRACTION, VALIDATION, POLICY_LOOKUP, COVERAGE, TRIAGE, ROUTING)
- Error type (string: specific error category)
- AI decision (string: what agent decided)
- Correct decision (string: what human corrected to)
- Input data (JSON: claim details, policy details, etc.)
- AI confidence (float: confidence score for incorrect decision)
- Timestamp (datetime)

**Usage**:
- ML engineers review error logs weekly
- Errors used to augment training data (add corrected examples)
- Model retraining triggered when error count exceeds threshold (e.g., >50 errors for specific error type)

**Assumption References**: *[A9, A22, A27, A32, U2]*

---

### Input/Output Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SYSTEM INPUTS                                │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Unstructured Claim Reports (300/day)                             │
│    ├─ Email (135/day, 70-95% OCR confidence [A24])                  │
│    ├─ Phone (90/day, 80-95% OCR confidence)                         │
│    ├─ Web Form (60/day, 95-99% OCR confidence)                      │
│    └─ Mobile App (15/day, 90-98% OCR confidence)                    │
│                                                                      │
│ 2. Policy Data (300 lookups/day, 10-30 sec latency [A26, U5])      │
│    └─ Legacy PolicyAdmin System (SOAP API)                          │
│                                                                      │
│ 3. Adjuster Availability (255 queries/day, <2 sec latency)         │
│    └─ CRM/Workforce Management System (REST API)                    │
│                                                                      │
│ 4. Fraud Detection Signals (300 queries/day, <5 sec latency)       │
│    └─ Fraud Detection Service (REST API, optional)                  │
│                                                                      │
│ 5. Human Decisions (45/day, 15-120 min latency [A5, A31])          │
│    └─ CRM Escalation Tickets (REST API or polling)                  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FNOL PROCESSING AGENT                             │
│                                                                      │
│  Components 1-10: Extraction → Validation → Policy Lookup →         │
│  Coverage → Triage → Routing → Acknowledgment → System Updates →    │
│  Exception Handling → QA Monitoring                                 │
│                                                                      │
│  Processing Time:                                                    │
│  ├─ Autonomous claims: <2 min [A8, A23, A26, A30, A33, A36, A37]   │
│  └─ Escalated claims: <20 min (includes human review [A31])        │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SYSTEM OUTPUTS                                │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Claimant Acknowledgment (300/day, <2 hours [A14])               │
│    ├─ Email (HTML, via SMTP/SendGrid)                              │
│    └─ SMS (plain text, via Twilio, optional)                       │
│                                                                      │
│ 2. Claim Records (300/day, in CRM via REST API)                    │
│    └─ Includes: claim details, coverage, adjuster, status          │
│                                                                      │
│ 3. Documents (1,200/day, in DMS via REST API)                      │
│    ├─ FNOL Report (PDF/original format)                            │
│    ├─ Extracted Data (JSON)                                        │
│    ├─ Policy Details (JSON)                                        │
│    └─ Acknowledgment (PDF)                                         │
│                                                                      │
│ 4. Escalation Tickets (45/day, 15% of claims [A5])                 │
│    └─ In CRM + Email/Slack notifications to escalation target      │
│                                                                      │
│ 5. Adjuster Notifications (255/day, 85% of claims [A10])           │
│    └─ Email/Slack/CRM notification with claim details              │
│                                                                      │
│ 6. Quality Metrics (15,000 data points/day, real-time)             │
│    └─ To monitoring dashboard (Grafana/Datadog)                    │
│                                                                      │
│ 7. Daily QA Report (1/day, generated at 6am)                       │
│    └─ PDF report to QA team + operations manager                   │
│                                                                      │
│ 8. Error Logs (30/day, for model retraining [U2])                  │
│    └─ JSONL to ML training pipeline                                │
└─────────────────────────────────────────────────────────────────────┘
```

**Assumption References**: *[A5, A6, A7, A8, A9, A10, A14, A15, A19, A20, A21, A22, A23, A24, A26, A27, A28, A29, A30, A31, A32, A33, A34, A36, A37, A38, A39, U2, U5, U11]*

---

## 5. Integration Points

### Integration 1: Legacy Policy Administration System

**System Name**: Legacy Policy Administration System (PolicyAdmin)

**Purpose**: Retrieve policy details (coverage types, limits, exclusions, effective dates) for coverage determination

**Integration Type**: SOAP Web Service

**Authentication**: SAML 2.0 with service account credentials *[U5: actual auth method unknown, assume SAML]*

**Endpoints**:

**Operation 1: Lookup Policy by Policy Number**
```
Method: POST
Endpoint: https://policyadmin.example.com/soap/PolicyService/v2
SOAP Action: http://example.com/PolicyService/LookupPolicy
Request Schema:
  <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
                    xmlns:pol="http://example.com/policy/v2">
    <soapenv:Header>
      <wsse:Security>
        <saml:Assertion>...</saml:Assertion>
      </wsse:Security>
    </soapenv:Header>
    <soapenv:Body>
      <pol:PolicyLookupRequest>
        <pol:PolicyNumber>AA12345678</pol:PolicyNumber>
        <pol:EffectiveDate>2024-01-15</pol:EffectiveDate>
      </pol:PolicyLookupRequest>
    </soapenv:Body>
  </soapenv:Envelope>

Response Schema (Success):
  <soapenv:Envelope>
    <soapenv:Body>
      <pol:PolicyLookupResponse>
        <pol:PolicyDetails>
          <pol:PolicyID>uuid-here</pol:PolicyID>
          <pol:PolicyNumber>AA12345678</pol:PolicyNumber>
          <pol:PolicyholderName>John Doe</pol:PolicyholderName>
          <pol:EffectiveDate>2024-01-01</pol:EffectiveDate>
          <pol:ExpirationDate>2024-12-31</pol:ExpirationDate>
          <pol:Status>ACTIVE</pol:Status>
        </pol:PolicyDetails>
        <pol:CoverageList>
          <pol:Coverage>
            <pol:Type>AUTO_COLLISION</pol:Type>
            <pol:Limit>50000.00</pol:Limit>
            <pol:Deductible>500.00</pol:Deductible>
          </pol:Coverage>
          <pol:Coverage>
            <pol:Type>AUTO_COMPREHENSIVE</pol:Type>
            <pol:Limit>50000.00</pol:Limit>
            <pol:Deductible>250.00</pol:Deductible>
          </pol:Coverage>
        </pol:CoverageList>
        <pol:ExclusionList>
          <pol:Exclusion>Intentional damage</pol:Exclusion>
          <pol:Exclusion>Pre-existing damage</pol:Exclusion>
        </pol:ExclusionList>
      </pol:PolicyLookupResponse>
    </soapenv:Body>
  </soapenv:Envelope>

Response Schema (Error - Policy Not Found):
  <soapenv:Envelope>
    <soapenv:Body>
      <soapenv:Fault>
        <faultcode>pol:PolicyNotFound</faultcode>
        <faultstring>Policy AA12345678 not found in system</faultstring>
      </soapenv:Fault>
    </soapenv:Body>
  </soapenv:Envelope>

Response Schema (Error - System Error):
  <soapenv:Envelope>
    <soapenv:Body>
      <soapenv:Fault>
        <faultcode>soapenv:Server</faultcode>
        <faultstring>Internal system error</faultstring>
      </soapenv:Fault>
    </soapenv:Body>
  </soapenv:Envelope>

Timeout: 30 seconds [A26: assumes 10-30 sec latency, may be higher per U5]
Retry Logic: 3 attempts with exponential backoff (1s, 2s, 4s)
Fallback: Escalate to human if all retries fail (PENDING_SYSTEM_ISSUE state)
Error Codes:
  - pol:PolicyNotFound (404 equivalent): Policy does not exist → escalate to human
  - soapenv:Server (500 equivalent): System error → retry, then escalate
  - Timeout: No response within 30s → retry, then escalate
```

**Rate Limits**: Unknown *[U5]*, assume 10 requests/second max (conservative estimate)

**Data Mapping**:
```
PolicyLookupResponse → Policy entity:
  PolicyDetails.PolicyID → policy_id
  PolicyDetails.PolicyNumber → policy_number
  PolicyDetails.PolicyholderName → policyholder_name
  PolicyDetails.EffectiveDate → effective_date
  PolicyDetails.ExpirationDate → expiration_date
  PolicyDetails.Status → status (map: ACTIVE, LAPSED, CANCELLED)
  CoverageList.Coverage[] → coverage_types, coverage_limits, deductibles
  ExclusionList.Exclusion[] → exclusions
  has_complex_exclusions = true IF exclusions contain keywords: "act of God", "pre-existing", "intentional", "war", "nuclear"
```

**Assumption/Unknown References**: *[A26, U5]*

---

### Integration 2: CRM System

**System Name**: Customer Relationship Management System (CRM)

**Purpose**: Create claim records, link to policy and adjuster, trigger adjuster notifications

**Integration Type**: REST API

**Authentication**: OAuth 2.0 (client credentials flow) *[U5: assume OAuth, actual method unknown]*

**Endpoints**:

**Operation 1: Create Claim Record**
```
Method: POST
Endpoint: https://crm.example.com/api/v1/claims
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json
Request Body:
  {
    "claim_id": "uuid-here",
    "policy_id": "uuid-here",
    "policy_number": "AA12345678",
    "claimant_name": "John Doe",
    "claimant_email": "john.doe@example.com",
    "claimant_phone": "+12025551234",
    "loss_date": "2024-01-15",
    "loss_description": "Rear-end collision at intersection...",
    "claim_type": "AUTO_COLLISION",
    "claim_value_usd": 5000.00,
    "coverage_determination": "COVERED",
    "assigned_adjuster_id": "uuid-here",
    "status": "OPEN",
    "created_at": "2024-01-16T10:30:00Z",
    "acknowledged_at": "2024-01-16T10:32:00Z"
  }

Response (Success - 201 Created):
  {
    "crm_claim_id": "CRM-12345",
    "claim_id": "uuid-here",
    "status": "OPEN",
    "created_at": "2024-01-16T10:30:05Z"
  }

Response (Error - 400 Bad Request):
  {
    "error": "VALIDATION_ERROR",
    "message": "Missing required field: policy_id",
    "field": "policy_id"
  }

Response (Error - 500 Internal Server Error):
  {
    "error": "INTERNAL_ERROR",
    "message": "Database connection failed"
  }

Timeout: 10 seconds
Retry Logic: 3 attempts with exponential backoff (1s, 2s, 4s) for 500/503 errors only
Fallback: Escalate to human + IT support if all retries fail
Error Codes:
  - 400: Validation error (missing field, invalid format) → log error, escalate to developer
  - 401: Authentication error → refresh token, retry
  - 500: System error → retry, then escalate
  - 503: Service unavailable → retry, then escalate
```

**Operation 2: Create Escalation Ticket**
```
Method: POST
Endpoint: https://crm.example.com/api/v1/escalations
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json
Request Body:
  {
    "ticket_id": "uuid-here",
    "claim_id": "uuid-here",
    "trigger_condition": "claim_value > $100K [A21]",
    "escalation_target": "SENIOR_ADJUSTER",
    "ai_recommendation": "Assign to Senior Adjuster Jane Smith based on auto collision specialization",
    "supporting_evidence": {
      "claim_value_usd": 150000.00,
      "claim_type": "AUTO_COLLISION",
      "loss_description": "Total loss, vehicle destroyed..."
    },
    "confidence_score": 0.92,
    "response_time_sla": 60,
    "created_at": "2024-01-16T10:30:00Z"
  }

Response (Success - 201 Created):
  {
    "ticket_id": "uuid-here",
    "crm_ticket_id": "ESC-67890",
    "status": "OPEN",
    "assigned_to": "jane.smith@example.com",
    "created_at": "2024-01-16T10:30:05Z"
  }

Timeout: 10 seconds
Retry Logic: Same as Create Claim
```

**Rate Limits**: 100 requests/minute *[U5: assume standard rate limit]*

**Data Mapping**:
```
Claim entity → CRM CreateClaimRequest:
  claim_id → claim_id
  policy_number → policy_number (for linking)
  claimant_name, claimant_contact → claimant fields
  loss_date, loss_description, claim_type, claim_value_usd → claim details
  coverage_determination → coverage_determination
  assigned_adjuster_id → assigned_adjuster_id
  state → status (map: COMPLETED → OPEN, PENDING_REVIEW → PENDING, etc.)
```

**Assumption/Unknown References**: *[A37, U5]*

---

### Integration 3: Document Management System

**System Name**: Document Management System (DMS)

**Purpose**: Store claim documents (original report, extracted data, policy details, acknowledgment)

**Integration Type**: REST API (multipart/form-data for file uploads)

**Authentication**: API Key (X-API-Key header) *[U5: assume API key, actual method unknown]*

**Endpoints**:

**Operation 1: Upload Document**
```
Method: POST
Endpoint: https://dms.example.com/api/v1/documents
Headers:
  X-API-Key: {api_key}
  Content-Type: multipart/form-data
Request Body (multipart):
  - file: [binary file data]
  - metadata: {
      "claim_id": "uuid-here",
      "document_type": "FNOL_REPORT",
      "file_name": "claim_report_20240116.pdf",
      "uploaded_by": "fnol_agent",
      "uploaded_at": "2024-01-16T10:30:00Z"
    }

Response (Success - 201 Created):
  {
    "document_id": "DOC-12345",
    "claim_id": "uuid-here",
    "file_name": "claim_report_20240116.pdf",
    "file_size_bytes": 245678,
    "uploaded_at": "2024-01-16T10:30:05Z",
    "download_url": "https://dms.example.com/documents/DOC-12345"
  }

Response (Error - 413 Payload Too Large):
  {
    "error": "FILE_TOO_LARGE",
    "message": "File size exceeds 10MB limit",
    "max_size_bytes": 10485760
  }

Response (Error - 500 Internal Server Error):
  {
    "error": "STORAGE_ERROR",
    "message": "Failed to write file to storage"
  }

Timeout: 30 seconds (for large files)
Retry Logic: 3 attempts for 500/503 errors, no retry for 413 (file too large)
Fallback: Store file locally, escalate to IT support for manual upload
Error Codes:
  - 400: Invalid metadata → log error, escalate to developer
  - 401: Authentication error → check API key, escalate
  - 413: File too large → compress file, retry, or escalate
  - 500: Storage error → retry, then escalate
```

**Rate Limits**: 50 uploads/minute *[U5: assume standard rate limit]*

**Data Mapping**:
```
Document types:
  - FNOL_REPORT: Original claim report (email, transcript, form)
  - EXTRACTED_DATA: JSON summary of extracted fields
  - POLICY_DETAILS: Policy information from legacy system
  - ACKNOWLEDGMENT: Claimant acknowledgment message (PDF)
  - ESCALATION_EVIDENCE: Supporting documents for escalated claims
```

**Assumption/Unknown References**: *[A37, U5]*

---

## 6. What the Agent Should NOT Do

**Explicit Prohibitions**:

1. **Agent must NOT approve coverage for claims >$100K without human review** *[A21]*
   - Rationale: High-value claims have higher error cost ($2,000+ *[A27]*), require senior adjuster oversight
   - Enforcement: Hard-coded check in coverage determination logic (Component 4)

2. **Agent must NOT override fraud indicators without human investigation** *[A29]*
   - Rationale: Fraud indicators (≥3 flags) require specialist investigation, AI cannot assess intent
   - Enforcement: Automatic escalation to fraud investigator if fraud_indicators ≥3

3. **Agent must NOT modify policy data in legacy system (read-only access)** 
   - Rationale: Policy data is authoritative, modifications require underwriting approval
   - Enforcement: API credentials have read-only permissions, no write endpoints exposed

4. **Agent must NOT proceed with claim if policy status ≠ ACTIVE**
   - Rationale: Lapsed or cancelled policies have no coverage, requires human investigation (grace period? reinstatement?)
   - Enforcement: Hard-coded check in policy lookup logic (Component 3)

5. **Agent must NOT route claims to unavailable adjusters (OUT_OF_OFFICE, at max_workload)**
   - Rationale: Unavailable adjusters cannot handle claims, causes delays and SLA breaches
   - Enforcement: Adjuster filtering logic in routing (Component 6)

6. **Agent must NOT send acknowledgment if SLA already breached (>2 hours)**
   - Rationale: Breached SLA requires apology message, not standard acknowledgment
   - Enforcement: SLA check in acknowledgment logic (Component 7), use apology template if breached

7. **Agent must NOT make coverage determination if AI confidence <85%** *[A20]*
   - Rationale: Low confidence indicates ambiguity, requires human judgment to avoid costly errors
   - Enforcement: Confidence threshold check in coverage determination logic (Component 4)

8. **Agent must NOT ignore validation errors (proceed with invalid data)**
   - Rationale: Invalid data causes downstream failures (policy lookup fails, routing fails)
   - Enforcement: Validation logic (Component 2) blocks progression if any rule fails

9. **Agent must NOT retry indefinitely on system failures (infinite loops)**
   - Rationale: System downtime requires human + IT intervention, retries waste resources
   - Enforcement: Max 3 retry attempts with exponential backoff, then escalate

10. **Agent must NOT process claims without required fields (policy_number, claimant_name, loss_date)**
    - Rationale: Required fields are critical for coverage determination and routing
    - Enforcement: Validation logic (Component 2) escalates if required fields missing

---

## 7. Handling Ambiguity and Escalation

**Escalation Triggers** (consolidated):

| Trigger Condition | Threshold | Escalation Target | Response Time SLA | Assumption Reference |
|-------------------|-----------|-------------------|-------------------|---------------------|
| AI confidence below threshold | <85% *[A20]* | Claims Specialist | 30 min | A20 |
| Claim value exceeds threshold | >$100K *[A21]* | Senior Adjuster | 60 min | A21, U1 |
| Fraud indicators detected | ≥3 flags *[A29]* | Fraud Investigator | 120 min | A29 |
| Policy lookup failure | 3 failed retries | Claims Specialist | 15 min | A26, U5 |
| Policy not found (404) | N/A | Claims Specialist | 15 min | U5 |
| Policy status ≠ ACTIVE | N/A | Claims Specialist | 30 min | — |
| Coverage ambiguity detected | Complex exclusions | Claims Manager | 60 min | A27, U1 |
| Extraction confidence low | <90% on critical fields *[A24]* | Claims Specialist | 20 min | A24 |
| Validation failure | Any rule fails | Claims Specialist | 20 min | A25 |
| Routing confidence low | <85% *[A20]* | Claims Specialist | 30 min | A20 |
| No available adjusters | All at capacity | Operations Manager | 15 min | — |
| System integration failure | All retries exhausted | IT Support + Specialist | 10 min | U5 |
| SLA breach | >2 hours since receipt | Operations Manager | Immediate | A14 |
| Document quality low | OCR <70% | Claims Specialist | 20 min | — |
| Novel claim type | Not in training data | Claims Manager | 60 min | U2 |

**Escalation Workflow**:

1. **Agent detects trigger condition**:
   - Check occurs at end of each workflow step (Components 1-8)
   - Trigger conditions are evaluated using concrete thresholds (see table above)

2. **Agent creates EscalationTicket**:
   - `ticket_id`: UUID (system-generated)
   - `claim_id`: Link to Claim entity
   - `trigger_condition`: String describing specific threshold violated (e.g., "claim_value = $150K > $100K [A21]")
   - `escalation_target`: Enum (CLAIMS_SPECIALIST, SENIOR_ADJUSTER, FRAUD_INVESTIGATOR, CLAIMS_MANAGER, IT_SUPPORT, OPERATIONS_MANAGER)
   - `ai_recommendation`: String (if confidence >50%, agent provides suggested action)
   - `supporting_evidence`: JSON object with relevant data:
     - Extracted claim fields
     - Policy excerpt (if coverage ambiguity)
     - Fraud indicators (if fraud detected)
     - Error logs (if system failure)
     - Confidence scores (if low confidence)
   - `confidence_score`: Float (AI's confidence in recommendation, if applicable)
   - `response_time_sla`: Integer (minutes, from table above)

3. **Agent notifies escalation target**:
   - Email to escalation target's address (from Adjuster or user directory)
   - Slack message (if integration available)
   - SMS (for urgent escalations: SLA breach, system failure)
   - Notification includes:
     - Claim ID and summary (claimant name, claim type, value)
     - Trigger condition (why escalated)
     - AI recommendation (if available)
     - Link to claim details in CRM
     - Response time SLA (deadline for human action)

4. **Agent pauses claim processing**:
   - Set `claim.state = PENDING_REVIEW` (for business logic escalations) or `PENDING_SYSTEM_ISSUE` (for technical failures)
   - Set `claim.escalation_reason` = trigger_condition
   - Stop workflow progression (do not proceed to next step)
   - Log escalation event with timestamp

5. **Human reviews and takes action**:
   - Human accesses claim via CRM (link in notification)
   - Human reviews AI recommendation and supporting evidence
   - Human makes decision:
     - **Approve**: Proceed with AI recommendation (e.g., "Yes, route to this adjuster")
     - **Modify**: Change AI recommendation (e.g., "Route to different adjuster")
     - **Reject**: Deny claim or coverage (e.g., "Policy lapsed, no coverage")
     - **Request More Info**: Contact claimant for clarification (e.g., "Need photos of damage")
   - Human enters decision in CRM (updates EscalationTicket)

6. **Agent resumes processing**:
   - Agent polls EscalationTicket for human decision (every 30 seconds)
   - When `ticket.human_decision` is populated:
     - Parse decision (approve/modify/reject/request_info)
     - Update claim based on decision:
       - Approve: Proceed to next workflow step with AI recommendation
       - Modify: Update claim fields per human input, proceed to next step
       - Reject: Set claim.state = COMPLETED, coverage_determination = NOT_COVERED
       - Request More Info: Set claim.state = PENDING_CLAIMANT_RESPONSE, notify claimant
     - Set `ticket.resolved_at` = current_timestamp
     - Log resolution event

**Ambiguity Detection**:

Agent recognizes ambiguous situations through:

1. **Low AI Confidence** (<85% *[A20]*):
   - Signal: Model outputs confidence score <0.85 for coverage determination, routing, or triage
   - Interpretation: Model is uncertain, likely due to ambiguous policy language, novel claim type, or insufficient training data *[U2]*
   - Action: Escalate with AI recommendation (if confidence >50%) or without recommendation (if confidence <50%)

2. **Complex Policy Exclusions**:
   - Signal: `policy.has_complex_exclusions = true` (keywords: "act of God", "pre-existing", "intentional", "war", "nuclear")
   - Interpretation: Exclusion clauses require legal interpretation, AI cannot reliably determine applicability
   - Action: Escalate to claims manager with policy excerpt and claim description

3. **Fraud Indicators**:
   - Signal: `fraud_indicators.length ≥3` *[A29]*
   - Interpretation: Multiple red flags suggest potential fraud, requires specialist investigation
   - Action: Escalate to fraud investigator with list of indicators and supporting evidence

4. **Novel Claim Type**:
   - Signal: Claim type not well-represented in training data *[U2]* (detected by model's confidence on claim_type classification)
   - Interpretation: AI has not seen enough examples of this claim type to make reliable decisions
   - Action: Escalate to claims manager for manual processing, log claim for future model training

5. **Edge Cases in Data**:
   - Signal: Extracted data has unusual values (e.g., loss_date = 10 years ago, claim_value = $0)
   - Interpretation: Data may be incorrect or claim may be unusual
   - Action: Escalate to specialist for validation

**When to Ask vs When to Decide** (see Section 7 for detailed framework)

---

## 8. When to Ask vs When to Decide

**Agent Decides Autonomously** (no human in loop):

Scenarios where agent makes final decision and proceeds without human review:

1. **Data Validation** (Component 2):
   - IF all validation rules pass (policy_number format valid, required fields present, dates in range)
   - THEN proceed to policy lookup
   - Rationale: Validation is deterministic, zero ambiguity *[A25]*

2. **Policy Lookup** (Component 3):
   - IF policy found (200 response) AND policy.status = ACTIVE AND loss_date within policy period
   - THEN proceed to coverage determination
   - Rationale: Lookup is deterministic API call, no judgment required *[A26]*

3. **Claimant Acknowledgment** (Component 7):
   - IF claim successfully routed AND no special communication preferences *[U11]*
   - THEN generate and send acknowledgment autonomously
   - Rationale: Acknowledgment is templated, low error cost ($5 *[A35]*), high volume (300/day) *[A36]*

4. **System Updates** (Component 8):
   - IF claim acknowledged AND CRM/DMS APIs available
   - THEN create records and upload documents autonomously
   - Rationale: System updates are deterministic API calls, no judgment required *[A37]*

5. **Coverage Determination** (Component 4) - for straightforward claims:
   - IF coverage_confidence ≥85% *[A20]* AND claim_value <$100K *[A21]* AND fraud_indicators <3 *[A29]* AND policy.has_complex_exclusions = false
   - THEN set coverage_determination autonomously
   - Rationale: Straightforward claims (85% *[A10]*) are highly codifiable, low error risk

6. **Adjuster Routing** (Component 6) - for straightforward claims:
   - IF routing_confidence ≥85% *[A20]* AND claim_value <$100K *[A21]* AND adjuster available
   - THEN assign adjuster autonomously
   - Rationale: Routing is rule-based + ML, 97% accuracy target *[A15]*, low error cost (45 min rework *[A3]*)

**Agent Asks for Approval** (human reviews before execution):

Scenarios where agent proposes decision, waits for human approval before proceeding:

1. **Data Extraction** (Component 1) - for low-confidence extractions:
   - IF extraction_confidence <90% on critical fields *[A24]*
   - THEN escalate with extracted data, human validates/corrects, agent proceeds after approval
   - Rationale: Low confidence indicates OCR issues or ambiguous text, human validation prevents downstream errors *[A22]*

2. **Coverage Determination** (Component 4) - for ambiguous claims:
   - IF coverage_confidence <85% *[A20]* OR policy.has_complex_exclusions = true OR fraud_indicators ≥3 *[A29]*
   - THEN escalate with AI recommendation (COVERED/NOT_COVERED + rationale), human reviews and approves/modifies
   - Rationale: Ambiguous claims (15% *[A5]*) have high error cost ($2,000 *[A27]*), require human judgment

3. **Severity Triage** (Component 5) - for high-value/complex claims:
   - IF claim_value >$100K *[A21]* OR severity_score >60
   - THEN escalate with triage report, human reviews and confirms oversight level
   - Rationale: High-value claims require senior adjuster, human confirms appropriate oversight *[A31]*

4. **Adjuster Routing** (Component 6) - for high-value claims:
   - IF claim_value >$100K *[A21]* OR routing_confidence <85% *[A20]*
   - THEN escalate with top 3 adjuster recommendations, human selects and approves
   - Rationale: High-value claims require senior adjuster, human ensures correct assignment

5. **Claimant Acknowledgment** (Component 7) - for sensitive claims:
   - IF claim involves death, severe injury, or special communication needs *[U11]*
   - THEN escalate with draft acknowledgment, human reviews tone/content and approves
   - Rationale: Sensitive claims require empathy and careful communication, AI may lack appropriate tone

**Agent Provides Recommendation** (human makes decision):

Scenarios where agent provides data/recommendation but human makes final decision:

1. **Exception Handling** (Component 9) - all exceptions:
   - Agent detects exception (missing data, system error, coverage dispute, etc.)
   - Agent provides context, possible causes, and suggested actions
   - Human investigates and decides resolution (retry, manual processing, escalate further)
   - Rationale: Exceptions are non-standard, require problem-solving and judgment *[A38]*

2. **Policy Lookup Failure** (Component 3):
   - IF policy not found (404) after retries
   - THEN agent provides possible reasons (typo in policy number, lapsed policy, system issue)
   - Human investigates (contact claimant, check alternative systems, confirm lapse)
   - Rationale: Policy not found requires investigation, AI cannot determine root cause

3. **Coverage Disputes**:
   - IF adjuster disputes AI's coverage determination
   - THEN agent provides original decision rationale, policy excerpt, and claim details
   - Human (claims manager) reviews and makes final determination
   - Rationale: Disputes require senior judgment, AI provides supporting evidence but does not override human

4. **Fraud Investigation**:
   - IF fraud_indicators ≥3 *[A29]*
   - THEN agent provides list of indicators, supporting evidence, and claim details
   - Human (fraud investigator) conducts investigation and decides action (approve, deny, request more info)
   - Rationale: Fraud requires specialist investigation, AI detects patterns but cannot assess intent

5. **Novel Claim Types**:
   - IF claim type not in training data *[U2]*
   - THEN agent provides claim details and notes "novel claim type"
   - Human (claims manager) processes manually and provides feedback for future training
   - Rationale: Novel claims require human expertise, AI lacks training data to make reliable decisions

**Decision Framework** (consolidated logic):

```python
def determine_delegation_mode(claim, policy, ai_confidence):
    # Check for hard stops (always escalate)
    if claim.fraud_indicators >= 3:  # [A29]
        return "HUMAN_DECIDES", "FRAUD_INVESTIGATOR", "Fraud indicators ≥3"
    
    if claim.claim_value_usd > 100000:  # [A21]
        return "HUMAN_APPROVES", "SENIOR_ADJUSTER", "Claim value >$100K"
    
    if policy.has_complex_exclusions:
        return "HUMAN_APPROVES", "CLAIMS_MANAGER", "Complex policy exclusions"
    
    # Check AI confidence
    if ai_confidence < 0.85:  # [A20]
        return "HUMAN_APPROVES", "CLAIMS_SPECIALIST", f"AI confidence {ai_confidence} <85%"
    
    # Check for special circumstances
    if claim.involves_death or claim.involves_severe_injury:
        return "HUMAN_APPROVES", "CLAIMS_MANAGER", "Sensitive circumstances"
    
    # Default: agent decides autonomously
    return "AGENT_DECIDES", None, "Straightforward claim, high confidence"

# Usage in workflow:
delegation_mode, escalation_target, reason = determine_delegation_mode(claim, policy, coverage_confidence)

if delegation_mode == "AGENT_DECIDES":
    # Proceed autonomously
    claim.coverage_determination = ai_determination
    claim.state = "COVERAGE_DETERMINED"
    proceed_to_next_step()

elif delegation_mode == "HUMAN_APPROVES":
    # Escalate for approval
    create_escalation_ticket(
        claim_id=claim.claim_id,
        trigger_condition=reason,
        escalation_target=escalation_target,
        ai_recommendation=ai_determination,
        supporting_evidence={
            "policy_excerpt": policy.exclusions,
            "claim_description": claim.loss_description,
            "confidence_score": coverage_confidence
        }
    )
    claim.state = "PENDING_REVIEW"
    wait_for_human_decision()

elif delegation_mode == "HUMAN_DECIDES":
    # Escalate for human decision
    create_escalation_ticket(
        claim_id=claim.claim_id,
        trigger_condition=reason,
        escalation_target=escalation_target,
        ai_recommendation=None,  # No recommendation, human decides
        supporting_evidence={
            "fraud_indicators": claim.fraud_indicators,
            "claim_details": claim.to_dict()
        }
    )
    claim.state = "PENDING_REVIEW"
    wait_for_human_decision()
```

**Assumption References**: *[A5, A10, A20, A21, A22, A24, A25, A26, A27, A29, A31, A35, A36, A37, A38, U2, U11]*

---

## 9. Validation Logic

### 9.1 Happy Path Validation

**Scenario: Straightforward Auto Collision Claim**

**Characteristics**:
- Claim type: AUTO_COLLISION
- Claim value: $5,000 (minor damage)
- Document quality: Clean email, OCR confidence >95%
- Policy: Active, standard coverage, no complex exclusions
- No fraud indicators
- Claimant: Standard communication preferences (email)

**Expected Behavior**:

1. **Data Extraction** (Component 1):
   - Time: <15 seconds *[A23]*
   - Extract fields: policy_number=AA12345678, claimant_name="John Doe", loss_date=2024-01-15, claim_type=AUTO_COLLISION, claim_value_usd=5000
   - Confidence scores: policy_number=0.98, claimant_name=0.96, loss_date=0.99, overall=0.96 (>90% *[A24]*)
   - State transition: RECEIVED → EXTRACTING → EXTRACTED

2. **Data Validation** (Component 2):
   - Time: <2 seconds *[A25]*
   - Validate policy_number format: PASS (matches /^[A-Z]{2}\d{8}$/)
   - Validate loss_date: PASS (valid date, not in future)
   - Validate required fields: PASS (all present)
   - State transition: EXTRACTED → VALIDATING → VALIDATED

3. **Policy Lookup** (Component 3):
   - Time: <10 seconds *[A26]*
   - SOAP call to PolicyAdmin: SUCCESS (200)
   - Policy found: policy_id=uuid, status=ACTIVE, coverage_types=[AUTO_COLLISION, AUTO_COMPREHENSIVE], limit=$50K
   - Validate loss_date in policy period: PASS (2024-01-15 in [2024-01-01, 2024-12-31])
   - State transition: VALIDATED → POLICY_LOOKUP → POLICY_FOUND

4. **Coverage Determination** (Component 4):
   - Time: <8 seconds *[A28]*
   - Check coverage: claim_type=AUTO_COLLISION IN policy.coverage_types → COVERED
   - Check exclusions: No exclusion keywords in loss_description
   - Check policy complexity: has_complex_exclusions=false
   - Coverage confidence: 0.94 (>85% *[A20]*)
   - Decision: coverage_determination=COVERED (autonomous)
   - State transition: POLICY_FOUND → COVERAGE_DETERMINING → COVERAGE_DETERMINED

5. **Severity Triage** (Component 5):
   - Time: <10 seconds *[A30]*
   - Calculate severity score: claim_value=10 points (5K on 0-30 scale), fraud=0, complexity=0, confidence=0 → total=10 (ROUTINE)
   - Oversight requirement: severity=ROUTINE, value<100K, fraud<3, confidence>85% → NO HUMAN OVERSIGHT
   - State transition: COVERAGE_DETERMINED → TRIAGING → TRIAGED

6. **Adjuster Routing** (Component 6):
   - Time: <3 seconds *[A33]*
   - Filter adjusters: specialization=AUTO, geography=REGION_A, available=true, workload<max
   - Select adjuster: adjuster_id=uuid-adjuster-1 (lowest workload=5, specialization match=100%)
   - Routing confidence: 0.91 (>85% *[A20]*)
   - Decision: Assign to adjuster_id=uuid-adjuster-1 (autonomous)
   - State transition: TRIAGED → ROUTING → ROUTED

7. **Claimant Acknowledgment** (Component 7):
   - Time: <5 seconds *[A36]*
   - Generate acknowledgment: "Dear John Doe, we received your claim (#uuid) regarding AUTO_COLLISION on 2024-01-15. Your adjuster is Jane Smith..."
   - Send email to john.doe@example.com: SUCCESS
   - Log acknowledged_at: 2024-01-16T10:32:00Z (within 2-hour SLA *[A14]*)
   - State transition: ROUTED → ACKNOWLEDGING → ACKNOWLEDGED

8. **System Updates** (Component 8):
   - Time: <8 seconds *[A37]*
   - Create CRM record: SUCCESS (201, crm_claim_id=CRM-12345)
   - Upload documents to DMS: SUCCESS (4 documents uploaded)
   - State transition: ACKNOWLEDGED → COMPLETED

**Total Processing Time**: 15+2+10+8+10+3+5+8 = **61 seconds** (<2 minutes, well within 2-hour SLA *[A14]*)

**Validation Checks**:
- [ ] Claim state transitions: RECEIVED → EXTRACTING → EXTRACTED → VALIDATING → VALIDATED → POLICY_LOOKUP → POLICY_FOUND → COVERAGE_DETERMINING → COVERAGE_DETERMINED → TRIAGING → TRIAGED → ROUTING → ROUTED → ACKNOWLEDGING → ACKNOWLEDGED → COMPLETED
- [ ] All timestamps logged correctly (created_at, acknowledged_at, each state transition)
- [ ] Claimant receives acknowledgment email within 2 hours of claim receipt *[A14]*
- [ ] Email contains correct claim number (uuid), adjuster name (Jane Smith), next steps
- [ ] CRM updated with claim details (claim_id, policy_number, claimant_name, assigned_adjuster_id, status=OPEN)
- [ ] Documents uploaded to DMS (FNOL_REPORT, EXTRACTED_DATA, POLICY_DETAILS, ACKNOWLEDGMENT)
- [ ] No escalation tickets created (claim processed autonomously)
- [ ] No human intervention required (0 minutes human time *[A8]*)
- [ ] SLA compliance: acknowledged_at ≤ sla_deadline (created_at + 2 hours)
- [ ] Routing accuracy: Adjuster does not click "Not My Claim" within 24 hours
- [ ] Cost per claim: ~$0.15 AI processing *[A7]* (no human time)

---

### 9.2 Edge Case Validation

**Edge Case 1: High-Value Claim ($150K)**

**Trigger Condition**: `claim_value_usd` = $150,000 > $100K *[A21]*

**Expected Agent Behavior**:
1. Data extraction, validation, policy lookup proceed normally (Components 1-3)
2. Coverage determination: AI determines COVERED with confidence=0.89
3. **Escalation triggered** at severity triage (Component 5):
   - Severity score: claim_value=30 (max), fraud=0, complexity=0, confidence=0 → total=30 (MODERATE, but value>100K triggers escalation)
   - Create EscalationTicket:
     - trigger_condition: "claim_value = $150,000 > $100K [A21]"
     - escalation_target: SENIOR_ADJUSTER
     - ai_recommendation: "Claim is covered under AUTO_COLLISION policy. Recommend assigning to Senior Adjuster Jane Smith (auto collision specialist, 15 years experience)."
     - supporting_evidence: {claim_value: 150000, coverage_determination: "COVERED", confidence: 0.89}
     - response_time_sla: 60 minutes
   - Notify senior adjuster via email + Slack
   - Set claim.state = PENDING_REVIEW
4. Wait for human decision
5. **Human reviews** (within 60 min):
   - Reviews AI recommendation
   - Confirms coverage determination
   - Approves routing to Senior Adjuster Jane Smith
6. **Agent resumes**:
   - Assign claim to Jane Smith
   - Generate acknowledgment (mentions senior adjuster)
   - Complete system updates
   - Set claim.state = COMPLETED

**Validation Checks**:
- [ ] Escalation ticket created with correct trigger: "claim_value > $100K [A21]"
- [ ] Senior adjuster (Jane Smith) notified within 5 minutes of escalation
- [ ] Claim state: PENDING_REVIEW (paused at triage step)
- [ ] Agent provides recommendation: "Assign to Senior Adjuster Jane Smith" with rationale
- [ ] Human decision logged in EscalationTicket.human_decision
- [ ] Claim resumes processing after human approval
- [ ] Total processing time: ~61 sec (agent) + 30-60 min (human review) = **~60 min total**
- [ ] Cost per claim: $0.15 (AI) + 12 min × $0.75/min *[A8, A31]* = **$9.15** (within budget for high-value claims)

---

**Edge Case 2: Low-Confidence Data Extraction (OCR Quality 65%)**

**Trigger Condition**: `extraction_confidence.overall` = 0.65 < 90% *[A24]*

**Expected Agent Behavior**:
1. Data extraction (Component 1):
   - Document is low-quality scan (handwritten notes, coffee stain)
   - OCR confidence: policy_number=0.65, claimant_name=0.80, loss_date=0.90
   - Overall confidence: MIN(0.65, 0.80, 0.90) = 0.65 (<90% *[A24]*)
   - **Escalation triggered**:
     - Create EscalationTicket:
       - trigger_condition: "extraction_confidence.policy_number = 0.65 < 90% [A24]"
       - escalation_target: CLAIMS_SPECIALIST
       - ai_recommendation: "Extracted policy_number=AA12345678 (low confidence). Please verify from original document."
       - supporting_evidence: {extracted_fields: {...}, confidence_scores: {...}, document_url: "..."}
       - response_time_sla: 20 minutes
     - Highlight low-confidence fields in UI (policy_number, claimant_name)
     - Set claim.state = PENDING_REVIEW
2. Wait for human validation
3. **Human reviews** (within 20 min):
   - Opens original document (scanned form)
   - Verifies policy_number: Correct (AA12345678)
   - Verifies claimant_name: Incorrect (AI extracted "John Dae", actual is "John Doe")
   - Corrects claimant_name in UI
   - Approves extraction
4. **Agent resumes**:
   - Update claim.claimant_name = "John Doe"
   - Proceed to validation (Component 2)
   - Continue workflow normally (policy lookup, coverage, routing, etc.)

**Validation Checks**:
- [ ] Escalation ticket created with trigger: "extraction_confidence <90% [A24]"
- [ ] Claims specialist notified within 5 minutes
- [ ] Low-confidence fields highlighted in UI (policy_number, claimant_name)
- [ ] Human corrects error (claimant_name)
- [ ] Agent logs correction for model retraining *[U2]*
- [ ] Claim resumes at validation step (Component 2) after correction
- [ ] Total processing time: ~15 sec (extraction) + 10 min (human validation) + 50 sec (remaining steps) = **~11 min total**
- [ ] Cost per claim: $0.15 (AI) + 10 min × $0.75/min *[A8]* = **$7.65**

---

**Edge Case 3: Policy Not Found (404)**

**Trigger Condition**: Policy lookup returns 404 (policy not found)

**Expected Agent Behavior**:
1. Data extraction, validation proceed normally (Components 1-2)
2. Policy lookup (Component 3):
   - SOAP call to PolicyAdmin with policy_number=AA12345678
   - Response: 404 (PolicyNotFound fault)
   - **Escalation triggered**:
     - Create EscalationTicket:
       - trigger_condition: "Policy lookup failed: 404 PolicyNotFound"
       - escalation_target: CLAIMS_SPECIALIST
       - ai_recommendation: "Policy AA12345678 not found in system. Possible reasons: (1) Typo in policy number (similar policy AA12345679 exists), (2) Policy lapsed, (3) System data issue. Please verify with claimant."
       - supporting_evidence: {policy_number: "AA12345678", error_code: 404, similar_policies: ["AA12345679"]}
       - response_time_sla: 15 minutes
     - Set claim.state = PENDING_REVIEW
3. Wait for human investigation
4. **Human investigates** (within 15 min):
   - Contacts claimant to verify policy number
   - Claimant confirms typo: Correct policy number is AA12345679
   - Human updates claim.policy_number = "AA12345679" in UI
   - Human clicks "Retry Policy Lookup"
5. **Agent resumes**:
   - Retry policy lookup with corrected policy number
   - Policy found: SUCCESS (200)
   - Continue workflow normally (coverage, triage, routing, etc.)

**Validation Checks**:
- [ ] Escalation ticket created with trigger: "Policy lookup failed: 404"
- [ ] Claims specialist notified within 5 minutes
- [ ] Agent provides possible reasons (typo, lapsed, system issue)
- [ ] Agent suggests similar policy numbers (AA12345679) if available
- [ ] Human corrects policy number
- [ ] Agent retries policy lookup successfully
- [ ] Claim resumes at policy lookup step (Component 3)
- [ ] Total processing time: ~25 sec (extraction+validation) + 10 sec (failed lookup) + 10 min (human investigation) + 50 sec (remaining steps) = **~11.5 min total**

---

**Edge Case 4: Fraud Indicators Detected (3 Red Flags)**

**Trigger Condition**: `fraud_indicators.length` = 3 ≥ 3 *[A29]*

**Expected Agent Behavior**:
1. Data extraction, validation, policy lookup proceed normally (Components 1-3)
2. Coverage determination (Component 4):
   - AI detects fraud indicators:
     - Policy inception: 15 days ago (recent)
     - Claim value: $48,000 (near policy limit of $50K)
     - Loss description inconsistent with damage photos (claims "minor fender bender", photos show total loss)
   - Set claim.fraud_indicators = ["recent_policy_inception", "claim_near_limit", "inconsistent_description"]
   - **Escalation triggered**:
     - Create EscalationTicket:
       - trigger_condition: "fraud_indicators = 3 ≥ 3 [A29]"
       - escalation_target: FRAUD_INVESTIGATOR
       - ai_recommendation: None (fraud requires specialist investigation, AI does not recommend coverage decision)
       - supporting_evidence: {
           fraud_indicators: ["recent_policy_inception", "claim_near_limit", "inconsistent_description"],
           policy_inception_date: "2024-01-01",
           claim_date: "2024-01-15",
           claim_value: 48000,
           policy_limit: 50000,
           loss_description: "Minor fender bender...",
           damage_photos: ["url1", "url2"]
         }
       - response_time_sla: 120 minutes
     - Set claim.state = PENDING_REVIEW
3. Wait for fraud investigation
4. **Fraud investigator reviews** (within 2 hours):
   - Reviews claim details, policy history, damage photos
   - Contacts claimant for interview
   - Requests additional documentation (police report, repair estimates)
   - Decides: Legitimate claim (claimant undersold damage severity, but photos confirm accident)
   - Approves coverage: coverage_determination = COVERED
5. **Agent resumes**:
   - Proceed to severity triage (Component 5)
   - Continue workflow normally (routing, acknowledgment, system updates)

**Validation Checks**:
- [ ] Escalation ticket created with trigger: "fraud_indicators ≥3 [A29]"
- [ ] Fraud investigator notified within 10 minutes
- [ ] Agent provides list of fraud indicators with supporting evidence
- [ ] Agent does NOT provide coverage recommendation (human decides)
- [ ] Claim state: PENDING_REVIEW (paused at coverage determination)
- [ ] Fraud investigator logs investigation notes in EscalationTicket
- [ ] Human decision: COVERED (approved after investigation)
- [ ] Claim resumes at triage step (Component 5)
- [ ] Total processing time: ~35 sec (extraction+validation+lookup) + 90 min (fraud investigation) + 40 sec (remaining steps) = **~91 min total**

---

**Edge Case 5: Coverage Ambiguity (Complex Exclusion)**

**Trigger Condition**: `policy.has_complex_exclusions` = true (policy contains "act of God" exclusion, claim is flood due to dam failure)

**Expected Agent Behavior**:
1. Data extraction, validation, policy lookup proceed normally (Components 1-3)
2. Coverage determination (Component 4):
   - AI checks coverage: claim_type=PROPERTY_FLOOD, policy.coverage_types includes FLOOD
   - AI checks exclusions: policy.exclusions includes "Excludes damage from acts of God including floods, unless caused by structural failure"
   - AI detects ambiguity: Claim is flood (excluded) BUT caused by dam failure (structural failure, possibly covered)
   - Set policy.has_complex_exclusions = true (keyword "act of God" detected)
   - Coverage confidence: 0.60 (<85% *[A20]*, ambiguous)
   - **Escalation triggered**:
     - Create EscalationTicket:
       - trigger_condition: "coverage_ambiguity_detected: complex_exclusion [A27, U1]"
       - escalation_target: CLAIMS_MANAGER
       - ai_recommendation: "Possible coverage due to dam failure (structural), but exclusion clause is ambiguous. Requires legal interpretation."
       - supporting_evidence: {
           policy_excerpt: "Section 4.2: Excludes damage from 'acts of God' including floods, unless caused by structural failure...",
           claim_description: "Home flooded due to dam failure upstream...",
           coverage_confidence: 0.60
         }
       - response_time_sla: 60 minutes
     - Set claim.state = PENDING_REVIEW
3. Wait for claims manager decision
4. **Claims manager reviews** (within 60 min):
   - Reviews policy language, claim description, legal precedents
   - Consults legal team (if needed)
   - Decides: COVERED (dam failure qualifies as structural failure, exclusion does not apply)
5. **Agent resumes**:
   - Set coverage_determination = COVERED
   - Proceed to severity triage (Component 5)
   - Continue workflow normally

**Validation Checks**:
- [ ] Escalation ticket created with trigger: "coverage_ambiguity: complex_exclusion [A27]"
- [ ] Claims manager notified within 5 minutes
- [ ] Agent provides policy excerpt and claim description
- [ ] Agent provides AI recommendation with caveat ("requires legal interpretation")
- [ ] Claim state: PENDING_REVIEW (paused at coverage determination)
- [ ] Human decision: COVERED (with rationale logged)
- [ ] Claim resumes at triage step (Component 5)
- [ ] Total processing time: ~35 sec (extraction+validation+lookup) + 45 min (manager review) + 40 sec (remaining steps) = **~46 min total**

---

### 9.3 Failure Mode Validation

**Failure Mode 1: Agent Misroutes Claim (Wrong Adjuster)**

**Detection Method**:
- Adjuster clicks "Not My Claim" button in CRM within 1 hour of assignment
- QA monitoring detects re-routing event *[A39, Component 10]*
- Real-time alert: "Routing error detected for claim_id=uuid"

**Expected Behavior**:
- [ ] Agent logs error: `routing_error: claim_id=uuid, assigned_adjuster=adjuster-1, reason=wrong_specialization, confidence=0.87`
- [ ] Agent increments daily error counter: `routing_errors_today += 1`
- [ ] Agent checks error rate: `routing_errors_today / claims_processed_today`
- [ ] IF error rate <5% *[A9: target 3%, alert at 5%]*:
   - [ ] Agent re-routes claim automatically:
     - Re-run routing logic (Component 6) excluding adjuster-1
     - IF new routing confidence ≥85% *[A20]*: Assign to new adjuster autonomously
     - ELSE: Escalate to claims specialist for manual routing
   - [ ] Agent logs re-routing event
- [ ] ELSE (error rate ≥5%):
   - [ ] Agent sends alert to QA team: "Routing error rate exceeded 5% threshold (current: X%)"
   - [ ] Agent escalates claim to claims specialist for manual routing
   - [ ] QA team investigates root cause (see below)

**Root Cause Analysis** (human-led, AI-supported):
- **Question 1**: Is this a data quality issue? (adjuster specialization data incorrect, geography data outdated)
- **Question 2**: Is this a model drift issue? (routing model trained on old data, claim patterns changed)
- **Question 3**: Is this a workload balancing issue? (adjuster marked as available but actually at capacity)
- **Question 4**: Is this a specialization mismatch? (claim type classification error → wrong adjuster pool)

**Remediation**:
- IF data quality issue: Update adjuster data in CRM, re-train routing model *[U2]*
- IF model drift: Re-train routing model with recent claims data *[U2]*
- IF workload issue: Fix workload tracking logic (sync with CRM more frequently)
- IF classification issue: Improve claim type classification model (add training examples)

**Alert Thresholds**:
- **Daily error rate >5%** *[A9: target 3%]*: Alert QA team for investigation
- **Weekly error rate >4%** (sustained): Alert operations manager, schedule model retraining
- **Individual adjuster rejection rate >20%**: Alert adjuster manager (possible training issue or data error)

**Assumption References**: *[A3, A9, A15, A39]*

---

**Failure Mode 2: Agent Incorrectly Determines Coverage (Approves Invalid Claim)**

**Detection Method**:
- Adjuster reviews claim and disputes coverage determination ("This should not be covered")
- QA audit (random sample of 5% of claims *[A39]*) catches error within 24 hours
- Post-hoc analysis: Coverage error logged in CRM

**Expected Behavior**:
- [ ] Agent logs error: `coverage_error: claim_id=uuid, agent_decision=COVERED, adjuster_decision=NOT_COVERED, reason=exclusion_missed, confidence=0.88`
- [ ] Agent flags claim for root cause analysis:
   - **Question**: Did agent miss exclusion clause in policy?
   - **Question**: Is policy data incomplete (exclusion not in legacy system)?
   - **Question**: Is this a novel case type (not in training data *[U2]*)?
- [ ] Agent calculates error cost: 
   - IF claim already paid out: error_cost = claim_value_usd (e.g., $5,000)
   - ELSE: error_cost = adjuster_time_to_correct × $45/hour *[A1]* (e.g., 1 hour = $45)
- [ ] IF error_cost >$1,000:
   - [ ] Agent escalates to claims manager for review: "High-cost coverage error detected"
   - [ ] Claims manager investigates and decides remediation (deny claim, request repayment, update policy data)
- [ ] Agent checks for error pattern:
   - IF same exclusion missed 3+ times in past week:
     - [ ] Agent alerts QA team: "Recurring coverage error: exclusion [X] missed 3+ times"
     - [ ] QA team triggers model retraining *[U2]* (add exclusion examples to training data)
- [ ] Agent logs error for model retraining (claim details, policy excerpt, correct decision)

**Root Cause Analysis**:
- **Question 1**: Did agent miss exclusion clause? (exclusion present in policy but not detected)
- **Question 2**: Is exclusion clause ambiguous? (requires legal interpretation, AI cannot reliably assess)
- **Question 3**: Is policy data incomplete? (exclusion exists but not in legacy system response)
- **Question 4**: Is this a novel case type? (claim type not well-represented in training data *[U2]*)

**Remediation**:
- IF exclusion missed: Add exclusion detection rule, retrain model with this example
- IF exclusion ambiguous: Lower confidence threshold for this exclusion type (trigger human review)
- IF policy data incomplete: Fix data sync with legacy system, backfill missing exclusions
- IF novel case type: Add to training data, flag similar future claims for human review

**Alert Thresholds**:
- **Daily coverage error rate >2%** (target 0.5% *[A43]*): Alert QA team
- **Weekly coverage error rate >1%** (sustained): Alert claims manager, schedule model retraining
- **High-cost errors (>$1,000) >5 per week**: Alert senior management, review model performance

**Assumption References**: *[A9, A27, A39, A43, U2]*

---

**Failure Mode 3: Agent Breaches SLA (Claim Not Acknowledged Within 2 Hours)**

**Detection Method**:
- Timestamp comparison: `claim.acknowledged_at > claim.sla_deadline` (created_at + 2 hours *[A14]*)
- Real-time SLA monitoring dashboard *[Component 10, A39]*
- Alert triggered immediately upon breach

**Expected Behavior**:
- [ ] Agent logs SLA breach: `sla_breach: claim_id=uuid, received_at=2024-01-16T10:00:00Z, acknowledged_at=2024-01-16T12:05:00Z, delay=5 minutes`
- [ ] Agent calculates breach penalty: $25 per breach *[A4]*
- [ ] Agent sends apology acknowledgment to claimant:
   - Template: "Dear [claimant_name], we apologize for the delay in responding to your claim. Your claim (#[claim_id]) is now being processed by [adjuster_name]..."
   - Send via email + SMS (if available)
- [ ] Agent logs apology sent
- [ ] Agent performs root cause analysis:
   - **Question**: Was delay due to policy lookup latency? (check policy_lookup_duration)
   - **Question**: Was delay due to system downtime? (check integration error logs)
   - **Question**: Was delay due to high claim volume? (check claims_received_per_hour)
   - **Question**: Was delay due to escalation? (check if claim was PENDING_REVIEW)
- [ ] Agent checks SLA breach rate: `sla_breaches_today / claims_processed_today`
- [ ] IF breach rate >10% in any 4-hour window:
   - [ ] Agent sends alert to operations manager: "SLA breach rate exceeded 10% (current: X%)"
   - [ ] Operations manager investigates (system capacity issue? staffing issue? process bottleneck?)

**Root Cause Analysis**:
- **Question 1**: Policy lookup latency? (if policy_lookup_duration >30s *[A26]*, latency is issue)
- **Question 2**: System downtime? (if integration errors >5% in past hour, system is issue *[U5]*)
- **Question 3**: High claim volume? (if claims_received_per_hour >30, capacity is issue)
- **Question 4**: Escalation delay? (if claim was PENDING_REVIEW >1 hour, human response time is issue)

**Remediation**:
- IF policy lookup latency: Implement parallel processing, add caching, upgrade legacy system *[U5]*
- IF system downtime: Escalate to IT team, implement fallback workflows
- IF high volume: Scale infrastructure (add compute capacity, optimize processing)
- IF escalation delay: Increase human staffing, adjust escalation thresholds *[A20, A21]*

**Alert Thresholds**:
- **SLA breach rate >10% in any 4-hour window** (target 4% *[A14]*): Alert operations manager
- **Daily SLA breach rate >6%** (sustained): Alert senior management, review capacity planning
- **Individual claim delay >4 hours**: Alert operations manager immediately (critical breach)

**Assumption References**: *[A4, A14, A26, A39, U5]*

---

**Failure Mode 4: Agent Extracts Incorrect Data (Wrong Policy Number)**

**Detection Method**:
- Policy lookup returns 404 (policy not found) → suggests extraction error
- Human review during escalation catches error ("Extracted policy number doesn't match document")
- QA audit compares extracted fields to source document

**Expected Behavior**:
- [ ] Agent logs extraction error: `extraction_error: field=policy_number, extracted_value=AA12345678, confidence=0.75, actual_value=AA12345679`
- [ ] Agent escalates to human: "Policy lookup failed. Possible extraction error. Please verify policy number from original document."
- [ ] Human reviews original document:
   - Confirms extraction error (OCR misread "9" as "8")
   - Corrects policy_number in UI: AA12345679
   - Clicks "Retry Policy Lookup"
- [ ] Agent logs correction for model retraining *[U2]*:
   - Store: {document_image, extracted_value, correct_value, confidence_score}
   - Flag for OCR model retraining (improve digit recognition)
- [ ] Agent checks extraction error rate: `extraction_errors_today / claims_processed_today`
- [ ] IF error rate >10% for specific document type (e.g., handwritten forms):
   - [ ] Agent alerts QA team: "Extraction error rate for handwritten forms exceeded 10%"
   - [ ] QA team investigates: Is OCR model undertrained on handwritten text? Need more training data?

**Root Cause Analysis**:
- **Question 1**: Is this an OCR issue? (low-quality scan, handwritten text, unusual font)
- **Question 2**: Is this a model issue? (model not trained on this document type)
- **Question 3**: Is this a data format issue? (policy number format varies by state/region)

**Remediation**:
- IF OCR issue: Improve OCR preprocessing (image enhancement, noise reduction), use better OCR model
- IF model issue: Add training examples for this document type *[U2]*
- IF format issue: Update validation rules to handle format variations

**Alert Thresholds**:
- **Daily extraction error rate >10%** (target <5%): Alert QA team
- **Extraction error rate for specific document type >20%**: Alert QA team, flag document type for model improvement
- **Critical field errors (policy_number, claimant_name) >5%**: Alert operations manager (high downstream impact)

**Assumption References**: *[A22, A23, A24, A39, U2]*

---

**Failure Mode 5: Legacy System Timeout (Policy Lookup Takes >30 Sec)**

**Detection Method**:
- API call exceeds timeout threshold *[A26: 30 sec]*
- Retry logic exhausted (3 attempts with exponential backoff)
- Integration monitoring dashboard shows timeout spike

**Expected Behavior**:
- [ ] Agent logs system error: `integration_error: system=PolicyAdmin, operation=LookupPolicy, error=timeout, duration=30s, attempts=3`
- [ ] Agent escalates to human + IT support:
   - Create EscalationTicket:
     - trigger_condition: "Legacy system timeout after 3 retries"
     - escalation_target: IT_SUPPORT + CLAIMS_SPECIALIST
     - ai_recommendation: "Legacy system unresponsive. Claim cannot proceed without policy data. Options: (1) Wait for system recovery and retry, (2) Manual policy lookup by specialist."
     - supporting_evidence: {policy_number: "AA12345678", timeout_duration: 30, retry_attempts: 3, error_logs: "..."}
   - Notify IT support (email + Slack): "PolicyAdmin system timeout detected, claim_id=uuid"
   - Notify claims specialist (email): "Claim paused due to system issue, manual policy lookup may be required"
- [ ] Agent sets claim.state = PENDING_SYSTEM_ISSUE
- [ ] Agent checks system timeout rate: `system_timeouts_per_hour / api_calls_per_hour`
- [ ] IF timeout rate >5% in past hour:
   - [ ] Agent sends alert to IT team: "PolicyAdmin timeout rate exceeded 5% (current: X%)"
   - [ ] IT team investigates: Is system overloaded? Network issue? Database issue?
- [ ] Agent waits for system recovery or human decision:
   - IF system recovers (timeout rate drops <5%): Retry policy lookup automatically
   - IF human provides manual policy data: Proceed with human-provided data
   - IF system down for >1 hour: Escalate to operations manager for process decision (pause all claims? manual processing?)

**Root Cause Analysis**:
- **Question 1**: Is legacy system overloaded? (high request volume, database slow)
- **Question 2**: Is network connectivity issue? (latency spike, packet loss)
- **Question 3**: Is this a specific policy issue? (large policy with many endorsements, slow query)

**Remediation**:
- IF system overloaded: Scale legacy system (add capacity), optimize database queries, implement caching
- IF network issue: Escalate to network team, implement connection pooling
- IF specific policy issue: Optimize policy lookup query, implement timeout extension for complex policies

**Alert Thresholds**:
- **Timeout rate >5% in any hour** (target <1%): Alert IT team
- **Timeout rate >10% in any hour**: Alert IT manager + operations manager (critical system issue)
- **System down for >1 hour**: Alert senior management, activate incident response plan

**Assumption References**: *[A26, A39, U5]*

---

**Failure Mode 6: Agent Has Low Confidence But Doesn't Escalate (Confidence = 83%, Threshold = 85%)**

**Detection Method**:
- QA audit reviews confidence scores for all autonomous decisions
- Post-hoc analysis: Claims with confidence 80-85% have higher error rates than expected
- Weekly QA report flags borderline confidence decisions

**Expected Behavior**:
- [ ] Agent logs borderline confidence decision: `low_confidence_decision: claim_id=uuid, component=coverage_determination, confidence=0.83, threshold=0.85, decision=COVERED`
- [ ] QA team reviews these claims in daily audit (prioritize for human review):
   - Sample 100% of claims with confidence 80-85% (vs. 5% sample for high-confidence claims)
   - Compare AI decision to adjuster feedback (was coverage determination correct?)
   - Calculate error rate for borderline confidence claims
- [ ] IF error rate for 80-85% confidence claims >10%:
   - [ ] QA team recommends threshold adjustment: Increase from 85% to 90% *[A20]*
   - [ ] Rationale: "Error rate for 83-85% confidence claims is 12%, exceeding 10% tolerance. Raising threshold to 90% will reduce errors at cost of 5% more escalations."
   - [ ] Operations manager approves threshold change
   - [ ] Agent updates threshold: `confidence_threshold = 0.90`
- [ ] IF error rate for 80-85% confidence claims <5%:
   - [ ] QA team recommends threshold adjustment: Decrease from 85% to 80% *[A20]*
   - [ ] Rationale: "Error rate for 80-85% confidence claims is only 3%, below 5% tolerance. Lowering threshold to 80% will reduce escalations by 8% with minimal error increase."
   - [ ] Operations manager approves threshold change
   - [ ] Agent updates threshold: `confidence_threshold = 0.80`

**Root Cause Analysis**:
- **Question 1**: Is confidence calibration accurate? (does 83% confidence actually mean 83% accuracy?)
- **Question 2**: Is threshold too aggressive? (should we escalate more conservatively?)
- **Question 3**: Is this specific to certain claim types? (some claim types have lower confidence but same accuracy)

**Remediation**:
- IF calibration issue: Re-calibrate model (adjust confidence scores to match actual accuracy)
- IF threshold issue: Adjust threshold based on error rate analysis (see above)
- IF claim type issue: Implement claim-type-specific thresholds (e.g., 85% for auto, 90% for property)

**Alert Thresholds**:
- **Weekly review**: QA team analyzes borderline confidence claims (80-85% range)
- **Monthly review**: Operations manager reviews threshold performance, approves adjustments if needed
- **Error rate for borderline claims >10%**: Immediate threshold increase to 90%

**Assumption References**: *[A9, A20, A39]*

---

### 9.4 Validation Metrics

#### Real-Time Metrics (Monitored Continuously)

| Metric Name | Target | Alert Threshold | Assumption Reference |
|-------------|--------|-----------------|---------------------|
| **SLA Compliance Rate** | 96% of claims acknowledged within 2 hours | <90% in any 4-hour window | A14, Metric 1 |
| **Routing Accuracy Rate** | 97% of claims not re-routed by adjuster | <90% in any day | A15, Metric 2 |
| **Escalation Rate** | 15% of claims escalated to human | <10% (under-escalating) or >25% (over-escalating) in any day | A5 |
| **Processing Time (Autonomous)** | Median <2 min from receipt to acknowledgment | Median >5 min in any hour | A8, A23, A26, A30, A33, A36, A37 |
| **Processing Time (Escalated)** | Median <15 min from receipt to acknowledgment (including human review) | Median >30 min in any day | A31 |
| **System Integration Uptime** | 99% of API calls succeed within timeout | <95% in any hour | U5 |
| **AI Confidence Distribution** | 85% of decisions have confidence >90%, 10% have 85-90%, 5% have <85% | >30% of decisions have confidence <85% (model drift) | A20 |

**Monitoring Infrastructure**:
- Real-time dashboard (Grafana/Datadog) with 1-minute refresh
- Automated alerts via email + Slack + PagerDuty (for critical alerts)
- Alert routing: QA team (SLA, routing, escalation), IT team (system uptime), operations manager (critical issues)

---

#### Daily Metrics (Reviewed by QA Team)

| Metric Name | Target | Alert Condition | Assumption Reference |
|-------------|--------|-----------------|---------------------|
| **Extraction Error Rate** | <5% of claims require extraction correction | >10% in any day | A22, A24 |
| **Coverage Error Rate** | <0.5% for straightforward claims, <2% for moderate complexity | >2% for straightforward, >5% for moderate in any day | A43 |
| **Routing Error Rate** | <3% of claims re-routed by adjuster | >5% in any day | A9, A15 |
| **Cost per Claim (Actual)** | $1.55 avg (AI + human oversight) | >$2.00 avg in any day | A16, Metric 3 |
| **Confidence Distribution Shift** | Stable distribution (85% >90%, 10% 85-90%, 5% <85%) | >10% shift in any bucket (indicates model drift) | A20 |
| **Exception Rate** | 8% of claims require exception handling | >15% in any day (indicates process issues) | A38 |

**QA Process** *[A39]*:
- QA specialist reviews daily dashboard (30 min/day)
- Sample audit: 5% of autonomous claims (15 claims/day), 100% of borderline confidence claims (80-85%)
- Error logging: All errors logged with root cause category (extraction, coverage, routing, system)
- Daily report: Summary email to operations manager with error breakdown and trends

---

#### Weekly Metrics (Reviewed by Management)

| Metric Name | Target | Trend Analysis | Assumption Reference |
|-------------|--------|----------------|---------------------|
| **Adjuster Productivity** | 10 claims/day per adjuster (25% increase from 8 baseline) | Stable or improving | A13, A18, Metric 5 |
| **Customer Satisfaction** | >4.0/5.0 rating on post-claim survey | Stable or improving | — |
| **Model Performance Trends** | Error rate stable or decreasing, confidence stable or increasing | Degrading (indicates model drift or data quality issues) | A9, A20, U2 |
| **Cost per Claim (Trend)** | Stable at $1.55 or decreasing | Increasing (indicates higher escalation rate or longer processing time) | A16, Metric 3 |
| **Automation Rate** | 85% of claims processed without human intervention | Decreasing (indicates over-escalation or process issues) | A10, Metric 4 |

**Management Review Process**:
- Weekly meeting (1 hour) with operations manager, QA lead, IT lead
- Review: Metrics dashboard, error trends, escalation patterns, cost analysis
- Decisions: Threshold adjustments (A20, A21, A24, A29), model retraining schedule, process improvements
- Action items: Assigned to QA team (model retraining), IT team (system optimization), operations team (staffing adjustments)

---

## 10. Economic Model

### 10.1 Current State Costs (Manual Processing Baseline)

| Cost Category | Calculation | Daily Cost | Annual Cost (250 days) |
|---------------|-------------|------------|------------------------|
| **Labor** | 300 claims/day × 22 min/claim *[A6]* ÷ 60 min/hour × $45/hour *[A1]* | $4,950 | $1,237,500 *[A2]* |
| **SLA Breach Penalties** | 300 claims/day × 31% breach rate × $25/breach *[A4]* | $2,325 | $581,250 |
| **Routing Error Rework** | 300 claims/day × 18% error rate × 45 min/error *[A3]* ÷ 60 × $45/hour *[A1]* | $1,822 | $455,625 |
| **Coverage Error Costs** | 300 claims/day × 5% error rate (assumed baseline) × $2,000/error *[A27]* | $30,000 | $7,500,000 |
| **TOTAL CURRENT COST** | — | **$39,097** | **$9,774,375** |

**Note**: Coverage error costs dominate the economic model. Baseline 5% error rate is assumed (industry standard for manual processing, *[U6: actual rate unknown]*). This drives the business case for automation with human oversight.

---

### 10.2 Future State Costs (AI + Human Oversight)

**New Assumptions Required for Realistic Economic Model**:

**A41**: Coverage determination error rate varies by claim complexity:
- **Straightforward claims (70% of total)**: 0.5% error rate with AI (highly codifiable, well-trained model)
- **Moderate complexity (15% of total)**: 2% error rate with AI (some ambiguity, requires pattern recognition)
- **High complexity (15% of total)**: 8% error rate if fully automated → **these get human review** *[A5]*, reducing error rate to 0.1%

*Reasoning*: Uniform 3% error rate *[A9]* is unrealistic for high-stakes decisions like coverage determination. Error rates vary by claim complexity. Human oversight for high-complexity claims (15% *[A5]*) prevents costly errors.

*Used in*: Coverage error cost calculation

*Risk if wrong*: If actual error rates are higher (e.g., 2% for straightforward, 5% for moderate), coverage error costs increase from $997K to $2.5M, reducing ROI from 54% to 35%.

---

**A42**: Coverage error cost of $2,000 *[A27]* is **expected value** (probability × impact), not cost per error:
- **50% of errors caught by adjuster** before payout: Cost = 1 hour adjuster time = $45 *[A1]*
- **40% of errors result in small disputes**: Cost = $500 avg (customer service, appeals, small settlement)
- **10% of errors result in lawsuits/regulatory issues**: Cost = $20,000 avg (legal fees, settlements, penalties)
- **Weighted average**: 0.5 × $45 + 0.4 × $500 + 0.1 × $20,000 = $22.50 + $200 + $2,000 = **$2,222.50** (rounds to $2,000 *[A27]*)

*Reasoning*: Not all coverage errors result in lawsuits. Most are caught and corrected by adjusters or resolved through appeals. The $2,000 figure is a blended expected value across all error outcomes.

*Used in*: Coverage error cost calculation

*Risk if wrong*: If actual lawsuit rate is 20% (not 10%), expected value increases to $4,200, doubling coverage error costs.

---

**A43**: Routing error rate of 3% *[A9]* applies to **routing decisions**, not coverage determination:
- **Routing error rate**: 3% (AI at 97% accuracy *[A15]*, vs. 82% human baseline)
- **Coverage error rate**: Varies by complexity (see A41: 0.5% straightforward, 2% moderate, 0.1% high-complexity with human review)

*Reasoning*: Original assumption A9 (3% error rate) was ambiguous about which component it applied to. Routing errors are low-cost (45 min rework *[A3]*), so 3% is acceptable. Coverage errors are high-cost ($2,000 *[A27]*), so must be <1% for straightforward claims.

*Used in*: Coverage error cost calculation, routing error cost calculation

*Risk if wrong*: If coverage error rate is actually 3% (same as routing), coverage error costs increase from $997K to $4.5M, making project economically unviable.

---

| Cost Category | Calculation | Daily Cost | Annual Cost (250 days) |
|---------------|-------------|------------|------------------------|
| **AI Processing** | 300 claims/day × $0.15/claim *[A7]* | $45 | $11,250 |
| **Human Review (15% of claims)** | 45 claims/day × 12 min/claim *[A8]* ÷ 60 × $45/hour *[A1]* | $405 | $101,250 |
| **Exception Handling (8% of claims)** | 24 claims/day × 15 min/exception *[A38]* ÷ 60 × $45/hour *[A1]* | $270 | $67,500 |
| **QA Monitoring** | 45 min/day *[A39]* ÷ 60 × $45/hour *[A1]* | $34 | $8,438 |
| **Infrastructure (MLOps, monitoring)** | Embedded in A7 assumption, allocated separately for clarity | $800 | $200,000 *[A7]* |
| **SLA Breach Penalties** | 300 claims/day × 4% breach rate *[A14]* × $25/breach *[A4]* | $300 | $75,000 |
| **Routing Error Rework** | 300 claims/day × 3% error rate *[A9, A43]* × 45 min/error *[A3]* ÷ 60 × $45/hour *[A1]* | $304 | $75,938 |
| **Coverage Error Costs** | See detailed calculation below | $3,990 | $997,500 |
| **TOTAL FUTURE COST** | — | **$6,148** | **$1,536,876** |

**Coverage Error Cost Calculation** (using A41, A42, A43):

- **Straightforward claims (70% of 300 = 210 claims/day)**:
  - Error rate: 0.5% *[A41]*
  - Errors per day: 210 × 0.5% = 1.05
  - Cost per error: $2,000 *[A27, A42]*
  - Daily cost: 1.05 × $2,000 = $2,100
  - Annual cost: $2,100 × 250 = **$525,000**

- **Moderate complexity (15% of 300 = 45 claims/day, processed autonomously)**:
  - Error rate: 2% *[A41]*
  - Errors per day: 45 × 2% = 0.9
  - Cost per error: $2,000 *[A27, A42]*
  - Daily cost: 0.9 × $2,000 = $1,800
  - Annual cost: $1,800 × 250 = **$450,000**

- **High complexity (15% of 300 = 45 claims/day, human-reviewed)** *[A5]*:
  - Error rate: 0.1% (human review reduces from 8% to 0.1%) *[A41]*
  - Errors per day: 45 × 0.1% = 0.045
  - Cost per error: $2,000 *[A27, A42]*
  - Daily cost: 0.045 × $2,000 = $90
  - Annual cost: $90 × 250 = **$22,500**

- **Total Coverage Error Costs**: $525K + $450K + $22.5K = **$997,500/year**

---

### 10.3 Cost Comparison Table

| Cost Category | Current (Manual) | Future (AI + Human) | Delta | % Change |
|---------------|------------------|---------------------|-------|----------|
| **Labor** | $1,237,500 | $177,188 ($101K review + $67.5K exceptions + $8.4K QA) | -$1,060,312 | **-86%** |
| **AI Processing** | $0 | $11,250 | +$11,250 | N/A |
| **Infrastructure** | $0 | $200,000 | +$200,000 | N/A |
| **SLA Breach Penalties** | $581,250 | $75,000 | -$506,250 | **-87%** |
| **Routing Error Rework** | $455,625 | $75,938 | -$379,687 | **-83%** |
| **Coverage Error Costs** | $7,500,000 | $997,500 | -$6,502,500 | **-87%** |
| **TOTAL** | **$9,774,375** | **$1,536,876** | **-$8,237,499** | **-84%** |

**Net Annual Savings**: **$8,237,499** (84% cost reduction)

**Key Insight**: The business case is driven by **coverage error reduction** (from $7.5M to $997K), not just labor savings. Human oversight for 15% of claims *[A5]* prevents $6.5M in coverage errors annually, justifying the $177K human review cost.

---

### 10.4 ROI Calculation

**Implementation Cost**:
- Team: 1 FDE + 1 ML Engineer + 1 Backend Engineer + 1 QA Engineer
- Duration: 6 months *[A11]*
- Cost: 6 months × $85K/month avg *[A11]* = **$510,000**

**Payback Period**:
- Annual savings: $8,237,499
- Implementation cost: $510,000
- Payback: $510,000 ÷ $8,237,499 × 12 months = **0.74 months** (~3 weeks)

**Cost per Claim**:
- **Current**: $9,774,375 ÷ 75,000 claims/year = **$130.33/claim**
- **Future**: $1,536,876 ÷ 75,000 claims/year = **$20.49/claim**
- **Reduction**: 84% (not 91% as originally estimated *[A16]* – original estimate did not account for realistic coverage error costs)

**3-Year ROI**:
- Year 1: -$510K (implementation) + $8,237K (savings) = **$7,727K net**
- Year 2: $8,237K (savings) = **$8,237K net**
- Year 3: $8,237K (savings) = **$8,237K net**
- **3-Year Total**: **$24,201K** (47x return on $510K investment)

---

### 10.5 Sensitivity Analysis

**Scenario 1: Escalation Rate Increases from 15% to 25%** *[A5]*

- **Impact on Human Review Costs**:
  - Current: 45 claims/day × 12 min *[A8]* = 540 min/day = $405/day
  - New: 75 claims/day × 12 min = 900 min/day = $675/day
  - Increase: $270/day = $67,500/year

- **Impact on Coverage Error Costs**:
  - High-complexity claims increase from 15% to 25% (10% more get human review)
  - Moderate-complexity errors decrease: 30 claims/day (instead of 45) × 2% × $2,000 = $1,200/day (instead of $1,800/day)
  - High-complexity errors increase: 75 claims/day (instead of 45) × 0.1% × $2,000 = $150/day (instead of $90/day)
  - Net change: ($1,200 + $150) - ($1,800 + $90) = -$540/day = -$135,000/year (error costs decrease)

- **Net Impact**:
  - Human review costs increase: +$67,500/year
  - Coverage error costs decrease: -$135,000/year
  - **Net savings increase by $67,500/year** (from $8.24M to $8.30M)
  - Cost per claim: $20.49 → **$19.59** (improves)

**Takeaway**: Higher escalation rate (25% vs. 15%) actually **improves ROI** because it prevents more high-cost coverage errors ($135K savings) than it adds in human review costs ($67.5K). This suggests the 15% escalation rate *[A5]* may be too aggressive (under-escalating).

---

**Scenario 2: AI Error Rates Increase (Coverage: 1% → 2% for straightforward, 2% → 5% for moderate)** *[A41, A43]*

- **Impact on Coverage Error Costs**:
  - Straightforward: 210 claims/day × 2% × $2,000 = $8,400/day (instead of $2,100/day)
  - Moderate: 45 claims/day × 5% × $2,000 = $4,500/day (instead of $1,800/day)
  - High-complexity: Unchanged (human-reviewed)
  - Total: ($8,400 + $4,500 + $90) × 250 days = **$3,247,500/year** (instead of $997,500/year)
  - Increase: $2,250,000/year

- **Net Impact**:
  - Total future cost: $1,536,876 + $2,250,000 = **$3,786,876/year**
  - Net savings: $9,774,375 - $3,786,876 = **$5,987,499/year** (61% reduction, down from 84%)
  - Cost per claim: $20.49 → **$50.49**
  - Payback period: 0.74 months → **1.0 month**

**Takeaway**: Higher AI error rates significantly reduce ROI (from 84% cost reduction to 61%), but project remains economically viable. If error rates are this high, must increase escalation rate (e.g., from 15% to 30%) to maintain error cost control.

---

**Scenario 3: Legacy System Requires Infrastructure Upgrade ($100K)** *[U5]*

- **Impact on Implementation Cost**:
  - Current: $510,000
  - New: $510,000 + $100,000 = **$610,000**
  - Payback period: 0.74 months → **0.89 months** (~4 weeks)

- **Impact on Annual Costs**:
  - Infrastructure costs increase: $200,000 → $220,000 (amortize $100K upgrade over 5 years)
  - Total future cost: $1,536,876 + $20,000 = **$1,556,876/year**
  - Net savings: $9,774,375 - $1,556,876 = **$8,217,499/year** (84% reduction, minimal change)

**Takeaway**: Infrastructure upgrade has minimal impact on ROI (payback extends by 1 week). Legacy system performance *[U5]* is not a critical economic dependency.

---

### 10.6 Critical Economic Dependencies

**Dependency 1: Definition of "High-Value/Ambiguous" Claims** *[U1]*

- **Current assumption**: 15% of claims require human oversight *[A5]*, defined as value >$100K *[A21]* OR fraud ≥3 *[A29]* OR AI confidence <85% *[A20]*

- **If U1 resolves to 40% escalation rate** (e.g., threshold lowered to $50K, or confidence threshold raised to 95%):
  - Human review costs: 120 claims/day × 12 min *[A8]* = 1,440 min/day = $1,080/day = **$270,000/year** (up from $101K)
  - Coverage error costs: Decrease to **$600,000/year** (more claims get human review, fewer errors)
  - Total future cost: $1,536,876 + $169,000 (additional human review) - $397,500 (error reduction) = **$1,308,376/year**
  - Net savings: $9,774,375 - $1,308,376 = **$8,466,000/year** (87% reduction, improves from 84%)
  - Cost per claim: $20.49 → **$17.44** (improves)

- **Takeaway**: Higher escalation rate (40% vs. 15%) **improves ROI** because error cost reduction ($397K) exceeds human review cost increase ($169K). **U1 is critical but not a viability risk** – project economics improve with more conservative escalation.

---

**Dependency 2: Historical Data Quality** *[U2]*

- **Current assumption**: Sufficient training data to achieve 0.5% error rate for straightforward claims *[A41]*

- **If U2 resolves to poor data quality** (error rates: 2% straightforward, 5% moderate, 10% high-complexity):
  - Coverage error costs: $3,247,500/year (calculated in Scenario 2 above)
  - Must increase escalation rate to 30% to control errors (more human review for ambiguous cases)
  - Human review costs: 90 claims/day × 12 min = **$202,500/year** (up from $101K)
  - Total future cost: $1,536,876 + $101,250 (additional human review) + $2,250,000 (additional errors) = **$3,888,126/year**
  - Net savings: $9,774,375 - $3,888,126 = **$5,886,249/year** (60% reduction, down from 84%)
  - Cost per claim: $20.49 → **$51.84**

- **Takeaway**: Poor data quality *[U2]* significantly reduces ROI (from 84% to 60% cost reduction), but project remains viable. **U2 is a critical dependency** – must validate data quality in first 2 weeks of project. If data is poor, adjust expectations (60% cost reduction instead of 84%) and plan for more aggressive human oversight (30% escalation rate).

---

**Dependency 3: Client's Risk Tolerance** *[U12]*

- **Current assumption**: Client accepts 0.5-2% error rates *[A41]* with 15% human oversight *[A5]*

- **If U12 resolves to risk-averse** (client requires 99%+ accuracy, zero tolerance for coverage errors):
  - Must increase escalation rate to 50% (human reviews all moderate and high-complexity claims)
  - Human review costs: 150 claims/day × 12 min = **$337,500/year** (up from $101K)
  - Coverage error costs: Decrease to **$262,500/year** (only straightforward claims at 0.5% error rate)
  - Total future cost: $1,536,876 + $236,250 (additional human review) - $735,000 (error reduction) = **$1,038,126/year**
  - Net savings: $9,774,375 - $1,038,126 = **$8,736,249/year** (89% reduction, improves from 84%)
  - Cost per claim: $20.49 → **$13.84** (improves)

- **Takeaway**: Risk-averse client (50% escalation) **improves ROI** because error cost reduction ($735K) far exceeds human review cost increase ($236K). **U12 is not a viability risk** – project economics improve with more conservative approach.

---

**What Would Make the Project Economically Unviable?**

The project becomes unviable if:

1. **Coverage error costs cannot be reduced below $5M/year** (current $7.5M):
   - This would require AI error rates >5% for straightforward claims AND no human oversight
   - Mitigation: Increase escalation rate to 40-50%, ensuring error costs stay <$1M

2. **Human review costs exceed $2M/year** (e.g., 80%+ escalation rate):
   - This would require escalation threshold so conservative that most claims need human review
   - Mitigation: Adjust thresholds *[A20, A21]* to balance error cost vs. review cost

3. **Implementation cost exceeds $5M** (10x current estimate):
   - This would require massive custom development or legacy system replacement
   - Mitigation: Validate integration complexity *[U5]* in discovery, avoid scope creep

**None of these scenarios are likely** based on current assumptions. The project has strong economic fundamentals driven by coverage error reduction.

---

## 11. Open Questions & Assumptions to Validate

### Critical Unknowns (Must Resolve in Discovery)

**U1: Definition of "High-Value/Ambiguous" Claims**
- **Current assumption**: 15% of claims *[A5]*, defined as value >$100K *[A21]* OR fraud ≥3 *[A29]* OR AI confidence <85% *[A20]*
- **Impact**: Affects escalation rate from 10% to 40%, cost per claim from $13 to $52
- **Validation method**: Interview claims managers, review historical escalation patterns, analyze claim value distribution
- **Timeline**: Week 1 of discovery
- **Decision**: Finalize thresholds (A20, A21, A29) with client stakeholders

**U2: Historical Data Quality**
- **Current assumption**: Sufficient training data to achieve 0.5-2% error rates *[A41]*
- **Impact**: Affects error rates from 0.5% to 5%+, cost per claim from $20 to $52
- **Validation method**: Audit historical claims data (volume: need 10K+ labeled examples, labeling: need ground-truth coverage decisions, completeness: need all fields populated, diversity: need coverage of all claim types)
- **Timeline**: Weeks 1-2 of discovery
- **Decision**: If data quality is poor, adjust error rate assumptions (A41, A43) and escalation rate (A5) to 30%

**U12: Client's Risk Tolerance**
- **Current assumption**: Client accepts 0.5-2% error rates *[A41]* with 15% human oversight *[A5]*
- **Impact**: Affects escalation rate from 15% to 50%, cost per claim from $14 to $20
- **Validation method**: Executive interviews to understand ROI requirements, budget constraints, error tolerance, regulatory concerns
- **Timeline**: Week 1 of discovery
- **Decision**: Finalize escalation rate (A5) and confidence thresholds (A20) based on risk appetite

**U5: Legacy System Latency and Availability**
- **Current assumption**: 10-30 sec latency *[A26]*, 99%+ availability
- **Impact**: Affects SLA compliance (Metric 1) from 96% to 85%, may require infrastructure investment ($100K)
- **Validation method**: API documentation review, latency testing (measure actual response times for 100 sample lookups), availability analysis (review system uptime logs for past 6 months)
- **Timeline**: Weeks 2-3 of discovery
- **Decision**: If latency >30 sec or availability <95%, plan for parallel processing, caching, or infrastructure upgrade

---

### Assumptions to Validate in Pilot (Weeks 4-6)

**A23: AI Data Extraction Time = 15 Seconds**
- **Validation**: Measure actual extraction time for 100 sample claims (various document types)
- **Expected range**: 10-20 seconds (if >20 sec, may need faster LLM or optimized prompts)
- **Impact if wrong**: If actual time is 30 sec, still meets 2-hour SLA but reduces throughput capacity

**A26: Policy Lookup Time = 10 Seconds (Baseline), 30 Seconds (Worst-Case)**
- **Validation**: Measure actual SOAP call latency for 100 sample lookups
- **Expected range**: 5-30 seconds (if >30 sec, may need parallel processing or caching)
- **Impact if wrong**: If actual time is 60 sec, violates 2-hour SLA at scale (300 claims × 60 sec = 5 hours sequential)

**A31: Human Review Time = 2 Minutes for Escalated Claims**
- **Validation**: Measure actual review time for 20 escalated claims (specialists timed during pilot)
- **Expected range**: 1-5 minutes (if >5 min, may need better AI recommendations or UI improvements)
- **Impact if wrong**: If actual time is 5 min, human review costs increase from $101K to $253K/year

**A41: Coverage Error Rate = 0.5% for Straightforward Claims**
- **Validation**: Measure actual error rate in pilot (compare AI decisions to adjuster feedback for 100 claims)
- **Expected range**: 0.5-2% (if >2%, may need more training data or higher escalation rate)
- **Impact if wrong**: If actual rate is 2%, coverage error costs increase from $525K to $2.1M/year

**A43: Routing Error Rate = 3%**
- **Validation**: Measure actual re-routing rate in pilot (track "Not My Claim" clicks for 100 routed claims)
- **Expected range**: 2-5% (if >5%, may need better routing model or adjuster data quality improvements)
- **Impact if wrong**: If actual rate is 8%, routing error costs increase from $76K to $202K/year (still acceptable)

---

### Design Decisions to Finalize with Client

**A20: AI Confidence Threshold = 85%**
- **Current value**: 85% (below this, escalate to human)
- **Client may want**: 80% (more aggressive automation) or 90% (more conservative)
- **Trade-off**: Lower threshold (80%) → 10% escalation rate, higher error risk. Higher threshold (90%) → 25% escalation rate, lower error risk.
- **Recommendation**: Start at 85%, adjust based on pilot error rates (if errors <1%, lower to 80%; if errors >3%, raise to 90%)

**A21: High-Value Threshold = $100K**
- **Current value**: $100K (above this, escalate to senior adjuster)
- **Client may want**: $50K (more conservative) or $250K (more aggressive)
- **Trade-off**: Lower threshold ($50K) → 25% escalation rate, higher human review costs. Higher threshold ($250K) → 8% escalation rate, lower human review costs but higher error risk.
- **Recommendation**: Start at $100K, adjust based on client's risk tolerance *[U12]* and claim value distribution

**A29: Fraud Indicator Threshold = 3 Flags**
- **Current value**: 3 flags (at 3+, escalate to fraud investigator)
- **Client may want**: 2 flags (more sensitive) or 4 flags (less sensitive)
- **Trade-off**: Lower threshold (2 flags) → more fraud investigations (may catch more fraud but also more false positives). Higher threshold (4 flags) → fewer investigations (may miss some fraud).
- **Recommendation**: Start at 3 flags, adjust based on client's fraud exposure and investigator capacity

---

**End of Capability Specification v0.1**

---

**Next Steps**:
1. **Discovery (Weeks 1-3)**: Resolve U1, U2, U12, U5 through stakeholder interviews, data audits, and technical assessments
2. **Design (Week 4)**: Finalize thresholds (A20, A21, A29) and workflow based on discovery findings
3. **Prototype (Weeks 5-6)**: Build Components 1-3 (extraction, validation, policy lookup), validate time estimates (A23, A26)
4. **Pilot (Weeks 7-8)**: Process 10% of claims (30/day) for 2 weeks, measure actual error rates (A41, A43), escalation rate (A5), and cost per claim (A16)
5. **Adjust (Week 9)**: Refine thresholds and delegation boundaries based on pilot results
6. **Full Rollout (Weeks 10-24)**: Implement remaining components (4-10), scale to 100% of claims, monitor metrics (Section 8.4)

---

## Document Information

**Project**: Gate1 - FNOL Processing Automation
**Created By**: Alexandra Rendon
**Date Created**: 2026-04-27
**Document Type**: Consolidated Reference - Master Analysis Document

**Source Documents**:
1. [problem-statement.md](problem-statement.md) - Problem definition and success metrics
2. [delegation-analysis.md](delegation-analysis.md) - Automation boundaries and risk framework
3. [agent-spec.md](agent-spec.md) - Technical specification and economic model

**Usage**: This consolidated document serves as a complete reference for all FNOL project artifacts. Navigate using the Master Table of Contents above, or use individual section links for specific topics.
