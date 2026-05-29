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