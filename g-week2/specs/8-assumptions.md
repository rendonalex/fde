# Assumptions Log

## Document Purpose
This document captures all assumptions made during the cognitive load mapping analysis for Apex Distribution's Customer Operations transformation. Each assumption is explicitly marked with ID, confidence level, and rationale.

---

## Assumption Categories
- **VOL**: Volume and frequency assumptions
- **PROC**: Process and workflow assumptions  
- **SYS**: System capability and integration assumptions
- **ORG**: Organizational structure and capability assumptions
- **DATA**: Data availability and quality assumptions

---

## Assumptions Register

### A001 - Dispatch Adjustments Volume Distribution
- **Category**: VOL
- **Confidence**: Medium (60%)
- **Assumption**: Of the ~90 dispatch adjustments per day, approximately 40% are additional pickups, 30% are route diversions, 20% are driver swaps, and 10% are complex multi-event cases requiring multiple interventions.
- **Rationale**: Scenario provides total volume but not breakdown. This distribution is inferred from typical logistics operations patterns.
- **Impact**: Affects JtD decomposition and micro-task scoring for cognitive load and exception frequency.
- **Validation needed**: Interview dispatch coordinators; analyze 2-week sample of adjustment logs.

### A002 - Dispatcher Knowledge Distribution
- **Category**: ORG
- **Confidence**: Low (40%)
- **Assumption**: The 18-minute average handling time for dispatch adjustments implies significant tacit knowledge held by senior dispatchers. We assume 20% of dispatchers handle 60% of complex cases.
- **Rationale**: COO Sarah was promoted from dispatch team after 5 years, suggesting deep domain expertise exists but may be concentrated in senior staff.
- **Impact**: High dependency on individual expertise creates delegation risk and onboarding friction.
- **Validation needed**: Interview Sarah and senior dispatchers; map knowledge distribution.

### A003 - Driver App Data Completeness
- **Category**: SYS
- **Confidence**: Medium (50%)
- **Assumption**: Driver app provides GPS location, delivery status, and messaging, but does NOT provide real-time ETA calculations, route optimization suggestions, or exception classification.
- **Rationale**: Artefact 1 shows driver called dispatch rather than using app to resolve refused delivery. Artefact 3 shows agent had to "check with dispatch" for better ETA estimate.
- **Impact**: Agents will require integration with driver app API and potentially route optimization logic.
- **Validation needed**: Review driver app API documentation; interview drivers and dispatchers.

### A004 - Dispatch Console API Limitations
- **Category**: SYS
- **Confidence**: High (75%)
- **Assumption**: "Limited API surface" means read-only access to route/driver assignments, with no programmatic write access for adjustments. Route changes require manual operator input via Citrix desktop app.
- **Rationale**: Java desktop app via Citrix strongly suggests legacy architecture with minimal automation surface.
- **Impact**: Agent-led dispatch adjustments would require HITL approval and manual execution, limiting full autonomy.
- **Validation needed**: Technical discovery with IT team; API documentation review.

### A005 - Refused Delivery Decision Rules
- **Category**: PROC
- **Confidence**: Medium (60%)
- **Assumption**: Decision on refused delivery (return-to-depot, hold, re-attempt) depends on: customer tier (high-value vs. standard), reason for refusal (quality vs. administrative), delivery time remaining on route, and driver's proximity to depot.
- **Rationale**: Artefact 1 shows dispatcher discretion drives decisions. SOP mentions high-value escalation threshold (>£500) but damage section is incomplete.
- **Impact**: These decision rules would need to be made explicit through process mining and interviews before agent can be delegated this judgment.
- **Validation needed**: Shadow dispatchers on 20+ refused delivery cases; codify decision tree.

### A006 - Exception Handling Knowledge Gap
- **Category**: PROC  
- **Confidence**: High (80%)
- **Assumption**: The SOP (v2.3, October 2023) is significantly out of date. Section 4.3 (damaged consignments) is incomplete, and references to retired DispatchHub system indicate the document does not reflect current operations.
- **Rationale**: Explicit note in Artefact 4 states "DispatchHub was retired in October 2024" but SOP not updated. Damaged consignment section is marked "TBD."
- **Impact**: Cannot rely on documented process; must elicit lived process through observation and interviews.
- **Validation needed**: Compare SOP to actual workflows through shadowing and case walk-throughs.

### A007 - Billing System Integration Timeline
- **Category**: SYS
- **Confidence**: High (85%)
- **Assumption**: Aurum Billing batch exports have T-1 latency for most data, T-2 for reconciliation. This means dispute resolution workflows are working with data that is 24-48 hours stale. Real-time dispute validation against invoice state is not possible.
- **Rationale**: Explicitly stated in Artefact 5: "reconciliation file lags 24 hours behind invoice generation."
- **Impact**: Agent handling billing disputes must account for staleness; cannot guarantee real-time accuracy without manual verification.
- **Validation needed**: Confirm with IT team; assess feasibility of real-time API development.

### A008 - Sandra's Manual Override Authority
- **Category**: ORG
- **Confidence**: Medium (55%)
- **Assumption**: Sandra (appearing in Artefacts 1, 2, and dispute export) has informal authority to apply manual credits and goodwill adjustments outside standard approval workflows. The £170 credit in Artefact 2 has "no entry in the credits audit log."
- **Rationale**: Artefact 2 shows Sandra applied credit via "manual override" with no audit trail in expected system.
- **Impact**: Shadow processes exist that bypass controls. Agent delegation requires formalizing approval rules and audit requirements.
- **Validation needed**: Interview Sandra and finance team; review credit approval policies; audit recent credits.

### A009 - Customer Tier and Priority Rules
- **Category**: DATA
- **Confidence**: Low (40%)
- **Assumption**: Apex has implicit customer tier/priority system (Hayes & Sons appears 3x in sample exports, always handled by Sandra) but this is not formalized in accessible data.
- **Rationale**: Hayes & Sons has multiple invoices, disputes, and credits in small sample; always assigned to same agent. SOP mentions high-value threshold but not customer-based rules.
- **Impact**: If customer priority is tacit knowledge, agent will make suboptimal routing and escalation decisions.
- **Validation needed**: Analyze APEX_CUSTOMER_MASTER for tier/segment fields; interview Sandra about account management.

### A010 - ETA Inquiry API Availability
- **Category**: SYS
- **Confidence**: Medium (60%)
- **Assumption**: Driver app exposes GPS location via API, but does NOT expose predictive ETA or route position (drop 3 of 8, etc.). ETA inquiries require human judgment based on GPS timestamp and knowledge of typical route timing.
- **Rationale**: Artefact 3 shows agent needed to "check with dispatch" and could only provide "best guess" ETA range, despite having GPS data.
- **Impact**: ETA inquiry automation requires building predictive ETA capability, not just API integration.
- **Validation needed**: Review driver app API; assess feasibility of ML-based ETA prediction.

### A011 - Exception Frequency Variability
- **Category**: VOL
- **Confidence**: Medium (50%)
- **Assumption**: The stated ~180 delivery exceptions per day is an average, with peaks during weather events, holiday seasons, or operational disruptions reaching 250-300/day.
- **Rationale**: Logistics operations typically show 30-40% volume variance. Scenario does not provide peak/trough data.
- **Impact**: Capacity planning for agent infrastructure must accommodate peak, not just average.
- **Validation needed**: Analyze 6-month historical exception volume; identify seasonal patterns.

### A012 - Cross-Work-Stream Dependency Frequency
- **Category**: PROC
- **Confidence**: High (70%)
- **Assumption**: Approximately 25% of cases span multiple work streams. Example: refused delivery (exception) triggers billing dispute (due to surcharge), which then requires dispatch adjustment (re-delivery).
- **Rationale**: Artefact 2 shows billing dispute that originated from damaged delivery (exception). Scenario explicitly states work streams "interlock and frequently cross-refer."
- **Impact**: Agent orchestration must handle cross-work-stream context and handoffs, not just isolated cases.
- **Validation needed**: Process mining on case management system; identify handoff patterns.

### A013 - Salesforce CRM Data Completeness
- **Category**: DATA
- **Confidence**: Medium (60%)
- **Assumption**: Salesforce CRM contains customer records and case history, but does NOT contain complete delivery event data, route details, or billing transaction details. These require lookups to driver app and Aurum exports.
- **Rationale**: Scenario describes CRM as customer-focused, with separate systems for dispatch and billing. Typical CRM does not deeply integrate operational logistics data.
- **Impact**: Agent workflows will require multi-system data retrieval and reconciliation.
- **Validation needed**: Review CRM data model; map data dependencies for each work stream.

### A014 - Driver Communication Preference
- **Category**: ORG
- **Confidence**: Medium (55%)
- **Assumption**: Drivers prefer voice communication over in-app messaging for complex or urgent issues, despite driver app having messaging capability.
- **Rationale**: Artefact 1 shows Mark called dispatch rather than using app messaging. He mentions "I tried Sandra but her line was busy."
- **Impact**: Agent-to-driver communication may require voice interface or SMS, not just app-based messaging.
- **Validation needed**: Survey drivers on communication preferences; analyze message vs. call volume.

### A015 - Aurum Schema Change Frequency
- **Category**: SYS
- **Confidence**: High (80%)
- **Assumption**: "Schema changes happen ~quarterly without prior notice" means Apex has no advance notification or migration planning process for Aurum export format changes. Past RPA failure was due to schema brittleness.
- **Rationale**: Explicitly stated in scenario and Artefact 5. COO's skepticism about automation is linked to 2024 RPA project that "broke whenever Aurum's schema changed."
- **Impact**: Any integration with Aurum exports must be schema-resilient with automated regression testing and alerting.
- **Validation needed**: Review past schema change incidents; implement schema validation monitoring.

### A016 - Driver Swap Volume Distribution
- **Category**: VOL
- **Confidence**: Medium (55%)
- **Assumption**: Of the ~90 dispatch adjustments per day, driver swaps represent 10-15% (10-15 cases/day). This is lower than additional pickups and route diversions because driver emergencies/breakdowns are less frequent than customer-initiated adjustments.
- **Rationale**: Driver swaps are triggered by illness, vehicle breakdown, shift limit breaches—events that are operationally infrequent compared to customer requests. Typical logistics operations see 10-15% of dispatch issues requiring driver reassignment.
- **Impact**: Affects prioritization—low volume makes driver swaps lower ROI for automation investment.
- **Validation needed**: Analyze 1-month dispatch adjustment log; categorize by adjustment type.

### A017 - Damage Liability Assessment Criteria
- **Category**: PROC
- **Confidence**: Low (35%)
- **Assumption**: Apex does not have formal, documented criteria for determining damage liability (transit vs. packaging fault). Assessment currently relies on visual inspection of photos, agent judgment, and supervisor discretion. Decision factors likely include: damage type (crushed, torn, leaking), packaging quality (standard wrap, reinforced), sender history (repeat damage patterns), and customer relationship sensitivity.
- **Rationale**: Artefact 2 shows Sandra applying £170 goodwill credit via manual override. SOP Section 4.3 on damaged consignments is marked "TBD." Micro-task DE-2.2 in cognitive load map scores damage liability as LOW decision determinism: "requires judgment: transit vs. packaging fault."
- **Impact**: Without formalized criteria, agent delegation of damage claims is limited to Human-led + Agent Support (recommendations only). Formalizing criteria would enable Agent-led + Oversight model.
- **Validation needed**: Interview Sandra and supervisor on liability assessment process; review 30-50 historical damage cases; codify decision tree.

### A018 - Labor Cost and FTE Calculation
- **Category**: ORG
- **Confidence**: Medium (60%)
- **Assumption**: Average Customer Operations agent salary is £35K/year fully loaded (base + benefits). Standard work year is 1,840 hours (230 days × 8 hours, accounting for holidays/sick leave). Therefore, 1 hour/day saved = 230 hours/year = 0.125 FTE equivalent = £4,375/year labor cost reduction.
- **Rationale**: UK logistics customer service salary benchmarks: £28K-40K base, £35K is mid-range. Fully loaded (benefits, NI, training) adds ~15-20% → £32-42K range, £35K is conservative midpoint.
- **Impact**: Used throughout business case calculations. Conservative estimate ensures ROI isn't overstated.
- **Validation needed**: Confirm with Sarah Whitmore (COO) or HR; adjust if actual salaries differ significantly.

### A019 - Route Diversion Decision Rules
- **Category**: PROC
- **Confidence**: Low (40%)
- **Assumption**: Decision on whether to approve route diversion depends on: (1) customer priority tier (high-value customers get priority), (2) delay impact magnitude (>30 min downstream delay requires escalation), (3) affected customer SLA tolerances (contractual windows vs. best-effort), (4) driver familiarity with alternate location (postal code history), (5) time remaining in delivery window (late-day diversions riskier). These rules are currently implicit, residing in dispatcher judgment.
- **Rationale**: Cognitive load map micro-task DA-2.2 notes "requires judgment on delay tolerance" and context complexity includes customer priority. Artefact 2 shows Hayes & Sons (appears 3x in exports) likely receives preferential treatment.
- **Impact**: Without formalized rules, route diversion remains Human-led + Agent Support. Formalization would improve agent recommendation accuracy.
- **Validation needed**: Shadow dispatch coordinators on 20+ diversion cases; interview Sarah (former dispatch lead) on decision criteria; codify into decision tree with thresholds.

### A020 - Route Diversion Exception Frequency
- **Category**: VOL
- **Confidence**: Medium (50%)
- **Assumption**: ~40% of route diversions have complicating factors that prevent standard processing: driver unreachable (phone/app), customer refuses alternate timing, diversion creates cascading delays requiring multiple customer notifications, or diversion conflicts with driver shift limits.
- **Rationale**: Route diversions are inherently higher-risk than standard pickups (affect committed deliveries vs. adding new ones). Typical logistics operations see 30-50% of mid-route changes having downstream complications. Conservative midpoint used.
- **Impact**: High exception rate drives delegation archetype to Human-led + Agent Support (agent recommends, human handles edge cases).
- **Validation needed**: Analyze diversion case logs; measure escalation rate and complication frequency.

### A021 - Driver Swap Handling Time
- **Category**: VOL
- **Confidence**: Medium (60%)
- **Assumption**: Driver swaps take 25-30 minutes average handling time, higher than the stated 18-minute average for dispatch adjustments overall, because they require: identifying available drivers (may need to call multiple), negotiating handoff logistics (location, timing), coordinating both drivers simultaneously, supervisor approval for overtime, and customer notifications for affected deliveries.
- **Rationale**: Driver swaps are the most complex dispatch adjustment type (cognitive load map scores DA-3 as "decision-making 70%"). Micro-task DA-3.4 notes "multi-turn negotiation" and driver resistance. Real-world logistics operations see driver reassignments taking 20-40 minutes.
- **Impact**: Higher handling time increases potential ROI for automation, but low suitability scores override volume consideration.
- **Validation needed**: Time-study dispatch coordinators on 10-15 driver swap cases; measure actual duration.

### A022 - Refused Delivery Volume Distribution
- **Category**: VOL
- **Confidence**: Medium (55%)
- **Assumption**: Of the ~180 delivery exceptions per day, refused deliveries represent 30% (~54 cases/day). This is a significant category alongside damaged consignments, missed windows, and unattended addresses.
- **Rationale**: Artefact 1 (driver voicemail about refused delivery) and Artefact 2 (billing dispute originating from damaged/refused delivery) suggest refused deliveries are common. Typical logistics operations see 25-35% of exceptions being refusals. Midpoint estimate used.
- **Impact**: Volume drives refused deliveries as high-priority automation target, but delegation archetype (Human-led + Agent Support) limits full autonomy.
- **Validation needed**: Analyze exception case logs by category; measure refused delivery frequency and sub-type distribution (damage, incorrect consignment, administrative).

### A023 - Damaged Consignment Volume Distribution
- **Category**: VOL
- **Confidence**: Medium (55%)
- **Assumption**: Damaged consignments represent ~20% of delivery exceptions (~36 cases/day). Lower than refused deliveries but still significant.
- **Rationale**: Artefact 2 centers on damaged delivery dispute. Damage reports require photo documentation and liability assessment (higher handling time than simple inquiries). Typical logistics sees 15-25% of exceptions involving damage claims.
- **Impact**: Volume justifies automation investment, but LOW decision determinism (liability judgment) limits delegation.
- **Validation needed**: Analyze exception logs; measure damage report frequency and liability patterns (transit vs. packaging).

### A024 - Missed Window Investigation Volume
- **Category**: VOL
- **Confidence**: High (70%)
- **Assumption**: Of the ~400 ETA inquiries per day (stated in scenario), ~35% require investigation beyond simple lookup (~140 cases/day). These are cases where delivery status is ambiguous (GPS stale, driver unreachable) or customer is escalating due to missed committed window.
- **Rationale**: Artefact 3 shows ETA inquiry requiring dispatch consultation ("checking with dispatch"). Simple lookups (delivery completed, clear in-transit) are <4 min (stated in scenario). Cases requiring investigation drive the ~8 min handling time estimated in cognitive load map.
- **Impact**: Missed window investigation is highest-volume fully agentic candidate. 140 cases/day × 8 min = 1,120 min/day = primary Phase 1 pilot target.
- **Validation needed**: Analyze ETA inquiry case logs; measure % requiring dispatch consultation or GPS investigation vs. simple status lookups.

### A025 - Unattended Address Volume Distribution
- **Category**: VOL
- **Confidence**: Medium (60%)
- **Assumption**: Unattended addresses represent ~25% of delivery exceptions (~45 cases/day). Common in both B2B (business closed outside hours) and residential (no answer) deliveries.
- **Rationale**: Typical logistics operations see 20-30% of exceptions being "recipient unavailable." Apex serves both B2B and DTC (stated in scenario: "B2B and DTC parcels"), increasing likelihood of unattended addresses across mixed delivery windows.
- **Impact**: Volume supports unattended address as Phase 1 expansion candidate (Agent-led + Oversight).
- **Validation needed**: Analyze exception logs; measure unattended address frequency and resolution patterns (safe place, re-delivery, depot pickup).

### A026 - Unattended Delivery Policy Conflict Frequency
- **Category**: VOL
- **Confidence**: Medium (55%)
- **Assumption**: ~5% of unattended address cases have policy conflicts requiring escalation (e.g., customer demands unattended delivery but consignment requires signature, or safe place authority conflicts with high-value item policy).
- **Rationale**: Policy conflicts are predictable but infrequent in well-controlled systems. Most customers with safe place authority have appropriate consignment values; signature-required items are flagged upfront. 5% accounts for edge cases and customer disputes.
- **Impact**: Low exception rate supports Agent-led + Oversight archetype (agent handles 95%, escalates 5%).
- **Validation needed**: Analyze unattended address resolution logs; measure escalation frequency and policy conflict types.

### A027 - Agent Infrastructure Cost Estimate
- **Category**: ORG
- **Confidence**: Medium (50%)
- **Assumption**: Agent infrastructure operational cost is £30-40K/year for Phase 1 (Fully Agentic + Agent-led archetypes, ~221 cases/day). Includes: model inference (Claude API or self-hosted), API call costs (CRM, driver app, SMS/email), compute/storage, monitoring/logging, and operational overhead (1 person 20% FTE for supervision and tuning).
- **Rationale**: Estimated costs: Model inference (140 cases × 2K tokens avg × £0.015/1K tokens × 365 days) = £15K/year. API calls + SMS/email (221 cases × £0.05/case × 365 days) = £4K/year. Monitoring + ops overhead = £10-15K/year. Total: £29-34K, rounded to £30-40K for contingency.
- **Impact**: Infrastructure cost must be subtracted from labor savings to calculate net ROI. Phase 1 net benefit: £109K savings - £35K infrastructure = £74K/year conservative estimate.
- **Validation needed**: Obtain Claude API pricing, SMS gateway costs, CRM API rate limits; refine estimate based on actual token usage in pilot.

### A028 - Platform Compounding Marginal Cost Reduction
- **Category**: ORG
- **Confidence**: Medium (60%)
- **Assumption**: Agents built on top of Wave 1 platform assets (CRM API, GPS API, NLP, notification automation) have 40-50% lower marginal build cost compared to standalone implementation. Example: DE-1 standalone would cost £45K; inheriting Wave 1 assets reduces to £25K.
- **Rationale**: Platform reusability is a core ATX thesis (compounding concept in atx-concepts.md). CRM and GPS integrations built in Wave 1 eliminate 8-12 weeks of Wave 2 integration effort. NLP classification engine is reusable across multiple exception types.
- **Impact**: Makes Wave 2-3 economically viable despite lower per-case ROI. Platform value exceeds sum of individual agents.
- **Validation needed**: Track actual Wave 2 build costs vs. estimates; measure integration reuse %.

### A029 - Multi-Wave Cumulative ROI
- **Category**: ORG
- **Confidence**: Low (45%)
- **Assumption**: 3-year cumulative ROI across all waves (if deployed) is 35% (£67.5K net benefit / £192K total build cost). This assumes Wave 1 deploys fully (£83K/year), Wave 2 prep costs £45K, Wave 3 deploys with marginal economics (£7K/year for 1.5 years).
- **Rationale**: Calculated from detailed TCO analysis in Phase 4. Conservative estimate assumes no volume growth, no token cost reduction, no HITL rate improvement beyond formalized rules.
- **Impact**: Modest ROI suggests alternative strategy (pivot to other work streams after Wave 1) may be superior.
- **Validation needed**: Re-calculate after Wave 1 pilot with actual token costs, HITL rates, and volume patterns.

### A030 - Token Cost Caching Opportunity
- **Category**: SYS
- **Confidence**: High (75%)
- **Assumption**: DE-3 (Missed Window Investigation) can leverage prompt caching for route plan and historical timing data, reducing input tokens by 40-50% (from 1,500 to 800-900 per case). Route plans and timing patterns are stable within a day and reused across 140 cases.
- **Rationale**: Claude API supports prompt caching for repeated context (anthropic.com documentation). Route plan (400 tokens) and historical timing (400 tokens) are identical across all ETA inquiries on same route within same day.
- **Impact**: Reduces DE-3 token cost from £0.045/case to £0.025/case, improving annual savings from £53K to £60K. Caching implementation adds £2K to build cost but payback in <2 months.
- **Validation needed**: Implement caching in DE-3 pilot; measure actual token reduction.

### A031 - Infrastructure Cost Allocation by Wave
- **Category**: ORG
- **Confidence**: Medium (55%)
- **Assumption**: Infrastructure cost allocated by wave: Wave 1 (£25K/year for supervision 0.3 FTE + monitoring + platform overhead), Wave 2 preparation (£10K investment for rule formalization and model training), Wave 3 (+£10K/year operational for expanded supervision 0.5 FTE total).
- **Rationale**: Supervision FTE scales with number of agents and escalation volume. Wave 1 (3 agents, low exception rate) requires part-time supervision. Wave 3 (6 agents, higher exception rate) requires half-time supervision.
- **Impact**: Per-JtD infrastructure allocation affects individual ROI calculations (DE-3 gets £10K allocation, DA-1 gets £7K, etc.).
- **Validation needed**: Measure actual supervision time in Wave 1 pilot; adjust allocation for Wave 2-3.

### A032 - Per-JtD Infrastructure Allocation Method
- **Category**: ORG
- **Confidence**: Medium (50%)
- **Assumption**: Wave 1 infrastructure cost (£25K) allocated to JtDs proportionally by volume × HITL rate. DE-3 (140 cases × 10% HITL) gets highest allocation (£10K), DE-4 (45 cases × 20% HITL) gets £8K, DA-1 (36 cases × 25% HITL) gets £7K. Rationale: Higher volume or higher HITL rate drives more supervision overhead.
- **Rationale**: Allocation method ensures each JtD's TCO reflects its actual infrastructure burden. DE-3 has lowest HITL but highest volume → requires most monitoring/logging capacity.
- **Impact**: Affects per-JtD ROI calculations. Alternative: allocate evenly (£8.3K each) for simpler accounting.
- **Validation needed**: Track actual supervision time per JtD in pilot; refine allocation method.

### A033 - Wave 1 DA-1 Inclusion Decision
- **Category**: ORG
- **Confidence**: Medium (60%)
- **Assumption**: Including DA-1 in Wave 1 extends blended payback from 7 months (DE-3 + DE-4 only) to 9 months (all three), due to DA-1's negative Year 1 ROI (-32%) from dispatch console API constraint. Decision point: Is 9-month payback acceptable, or is 7-month payback critical for stakeholder buy-in?
- **Rationale**: DA-1 has 18-month standalone payback due to API constraint limiting automation to 70%. However, it builds route calculation assets useful for Wave 3 (DA-2). Trade-off: Faster Wave 1 payback vs. more complete platform.
- **Impact**: Recommendation is to proceed with DA-1 unless fast payback is critical, since 9 months is still self-financing within Year 1.
- **Validation needed**: Stakeholder preference on payback timeline; technical discovery on dispatch console API workaround viability.

### A034 - Agent Support Cognitive Load Reduction %
- **Category**: ORG
- **Confidence**: Medium (55%)
- **Assumption**: "Human-led + Agent Support" archetype reduces handling time by 50-60% through data gathering, synthesis, and recommendation generation, but human retains 100% of decision authority. Example: DE-1 baseline 12 min/case → 5 min/case with agent support (55% reduction).
- **Rationale**: Cognitive load map shows 50-60% of handling time is data retrieval (CRM lookup, GPS query, history review) and communication drafting, which agents excel at. Remaining 40-50% is judgment/decision, which stays human-owned.
- **Impact**: Drives TCO calculations for DE-1, DE-2, DA-2. Higher reduction % improves economics.
- **Validation needed**: Time-study pilot with agent support; measure actual handling time reduction.

### A035 - Wave 3 HITL Rate Reduction from Rule Formalization
- **Category**: PROC
- **Confidence**: Low (40%)
- **Assumption**: Formalizing decision rules (A005, A017, A019) reduces HITL rates from 50-60% (current state with tacit rules) to 30-40% (with codified rules) for DE-1, DE-2, DA-2. This reduction improves economics from negative to marginally positive (£4-7K net savings).
- **Rationale**: Current high HITL is driven by agents escalating edge cases because decision rules are implicit. Formalized rules enable agent to handle standard cases confidently, escalating only true exceptions.
- **Impact**: HITL reduction is critical for Wave 3 viability. If reduction doesn't materialize, Wave 3 should be deferred/cancelled.
- **Validation needed**: Mock test with formalized rules; measure expected HITL reduction before committing to Wave 3 build.

### A036 - Wave 2 Strategy Pivot Rationale
- **Category**: ORG
- **Confidence**: High (75%)
- **Assumption**: Original Wave 2 deployment plan (DE-1, DE-2, DA-2) revised to "Wave 2 Preparation Phase" because all three candidates have negative net economics in current state (agent costs exceed savings due to high HITL rates 50-60%). Deploying agents with negative economics would undermine ROI case and stakeholder confidence.
- **Rationale**: TCO analysis shows DE-1 (-£5K), DE-2 (-£3K), DA-2 (-£2K) annual net impact. Better strategy: Use Wave 1 savings to prepare (formalize rules, train models), then deploy Wave 3 only if economics validate.
- **Impact**: Major strategy shift from original 3-wave deployment to 2-wave deployment + 1-wave preparation. More conservative but economically sound.
- **Validation needed**: None; this is analytical conclusion from TCO assessment.

### A037 - Wave 1 Exclusion of DA-1 Alternative Scenario
- **Category**: ORG
- **Confidence**: Medium (60%)
- **Assumption**: If DA-1 excluded from Wave 1 (due to dispatch console API blocker or preference for fast payback), Wave 1 becomes DE-3 + DE-4 only: £69K annual saving, £45K build cost, 7-month payback (vs. 9-month with DA-1). Trade-off: Faster payback but smaller absolute savings and missing route calculation asset for Wave 3.
- **Rationale**: Calculated from TCO removing DA-1. 7-month payback is more attractive for risk-averse stakeholders. Route calculation asset can be built later if needed.
- **Impact**: Decision point for Wave 1 scope planning.
- **Validation needed**: Stakeholder preference; technical discovery on DA-1 API workaround viability.

### A038 - Wave 2 Preparation Funding Source
- **Category**: ORG
- **Confidence**: High (70%)
- **Assumption**: Wave 2 preparation (£40-50K for decision rule formalization, image recognition training, API wrapper, NLP model training) is funded by Wave 1 Year 2 savings (£83K full-year saves, minus £40-50K prep cost = £33-43K surplus). This maintains self-financing model without requiring new budget.
- **Rationale**: Self-financing is critical sequencing criterion (atx-scoring.md). Wave 1 must generate enough savings to fund Wave 2 preparation.
- **Impact**: Validates Wave 2 preparation is economically viable from Wave 1 ROI.
- **Validation needed**: None; this is cash flow projection from Wave 1 ROI.

### A039 - Wave 3 Marginal Economics Strategic Value
- **Category**: ORG
- **Confidence**: Low (45%)
- **Assumption**: Wave 3 marginal net saving (£7K/year combined across DE-1, DE-2, DA-2) is strategically valuable despite low absolute ROI because: (1) 40-60% cognitive load reduction frees senior staff (Sandra, dispatchers) for higher-value work, (2) platform learning enables multi-agent workflows (Wave 4+), (3) demonstrates agent capability on complex judgment tasks for stakeholder confidence.
- **Rationale**: Not all value is captured in direct labor cost savings. Cognitive load reduction on high-complexity tasks has strategic value (upskills workforce, reduces burnout, enables growth without headcount).
- **Impact**: Justifies Wave 3 even with marginal economics, if strategic value is prioritized. Alternative view: £7K is too marginal, pivot to other work streams with higher ROI.
- **Validation needed**: Stakeholder input on strategic value vs. absolute ROI prioritization.

### A040 - Alternative Wave 3 Pivot to Other Work Streams
- **Category**: ORG
- **Confidence**: Medium (50%)
- **Assumption**: Instead of deploying DE-1/DE-2/DA-2 (marginal £7K/year), pivot to expanding Wave 1 platform to other work streams: ETA inquiries (full 400/day automation, not just 140 investigation cases) and billing disputes (60/day). Estimated additional savings: £120K/year over 2 years, with £80K build cost leveraging Wave 1 platform. 3-year ROI: 237% vs. 35% if Wave 3 deployed as planned.
- **Rationale**: Platform value is in reusability across work streams, not in completing original 7 JtDs. ETA inquiries and billing disputes likely have better economics than DE-1/DE-2/DA-2 because higher volume, lower complexity.
- **Impact**: Strategic recommendation: Deploy Wave 1, assess at Month 12, pivot to high-ROI work streams if Wave 3 economics remain weak.
- **Validation needed**: Preliminary economics on ETA inquiries and billing disputes work streams; confirm higher ROI than Wave 3.

### A041 - Platform Reusability Strategic Principle
- **Category**: ORG
- **Confidence**: High (80%)
- **Assumption**: Platform value is maximized by reusing assets (CRM API, GPS API, NLP, ETA engine) across multiple high-ROI work streams, not by completing all original candidate JtDs. If DE-1/DE-2/DA-2 have marginal economics, better strategy is to pivot platform to ETA inquiries (400/day full automation) and billing disputes (60/day) where volume and determinism drive higher ROI.
- **Rationale**: Core ATX compounding thesis (atx-concepts.md): platform assets should amplify future agents. Completing low-ROI agents for completeness' sake is anti-pattern. Prioritize highest-ROI applications of platform.
- **Impact**: Strategic recommendation for sequencing: Deploy Wave 1 → assess Wave 3 viability → pivot to other work streams if better ROI available.
- **Validation needed**: None; this is strategic principle from ATX framework.

### A042 - ETA Accuracy Target
- **Category**: ORG
- **Confidence**: Medium (60%)
- **Assumption**: Agent ETA accuracy target is 95% of calculations within ±30 minutes of actual delivery time. This is measurable by comparing agent-provided ETA to actual delivery timestamp logged in driver app.
- **Rationale**: ±30 min tolerance balances precision (tighter than current 4-hour windows) with achievability (accounts for traffic variability, driver pace differences). Industry standard for logistics ETA prediction is 80-90%; 95% is aspirational but achievable with GPS + historical timing + traffic data.
- **Impact**: Drives ETA calculation engine design (confidence scoring, fallback logic). If accuracy falls below 90%, requires algorithm refinement or traffic API integration.
- **Validation needed**: Pilot measurement over 2-4 weeks; adjust target based on actual performance.

### A043 - Customer Satisfaction Target
- **Category**: ORG
- **Confidence**: Medium (55%)
- **Assumption**: Customer satisfaction target for ETA inquiries is 90%+ satisfaction score on post-delivery survey question "Was ETA information helpful?" This is measurable via SMS/email survey sent after delivery completion.
- **Rationale**: Current satisfaction unknown (no baseline survey). 90% is ambitious but achievable if agent provides accurate, timely ETAs with empathetic tone. Comparison: Industry benchmarks for automated customer service satisfaction range 70-85%; 90% reflects high-quality agent experience.
- **Impact**: KPI for agent success. If satisfaction <85% in pilot, requires communication template refinement or escalation threshold adjustment.
- **Validation needed**: Implement post-delivery survey in pilot; measure actual satisfaction scores.

### A044 - ETA Confidence Threshold
- **Category**: PROC
- **Confidence**: Medium (60%)
- **Assumption**: Agent escalates ETA inquiries to human if confidence score <70% on ETA calculation. Confidence scoring factors: GPS freshness (>30 min stale → low confidence), route timing data availability (new route with <20 historical samples → medium confidence), traffic anomalies (if traffic API shows unusual congestion → medium confidence).
- **Rationale**: 70% threshold balances autonomous coverage (agent handles high-confidence cases) vs. accuracy (escalates ambiguous cases to prevent wrong ETAs). Similar to ML model deployment thresholds (70-80% confidence for autonomous action is standard practice).
- **Impact**: Affects HITL rate (lower threshold → higher escalation rate → lower coverage). Pilot tuning required to optimize threshold (may adjust to 60% or 80% based on accuracy/coverage trade-off).
- **Validation needed**: Pilot testing with varied thresholds; measure accuracy vs. escalation rate trade-off.

### A045 - GPS Staleness Threshold
- **Category**: PROC
- **Confidence**: Medium (65%)
- **Assumption**: Agent escalates if GPS last update >30 minutes ago, as stale GPS prevents accurate ETA calculation. Rationale: Typical delivery routes have 10-20 min per stop; 30 min gap suggests driver app offline, poor signal, or driver on break (no delivery progress). Agent cannot reliably estimate remaining time without fresh GPS.
- **Rationale**: Based on typical logistics operations (GPS updates every 30-60 seconds during active delivery, or on delivery event). 30 min threshold is conservative (reduces unnecessary escalations) while preventing inaccurate ETAs.
- **Impact**: Affects escalation rate (~10% cases estimated to have stale GPS). Threshold tunable based on pilot data (may adjust to 45 min if driver app updates infrequently but driver is active).
- **Validation needed**: Analyze driver app GPS update frequency; measure false positive escalations (GPS appears stale but driver is active between stops).

### A046 - Order Number Provision Rate
- **Category**: VOL
- **Confidence**: Medium (55%)
- **Assumption**: 80% of customers provide order number explicitly in ETA inquiry message ("Where is order AX-771-3344?"). Remaining 20% require agent to extract from customer authentication (lookup recent orders for authenticated customer in CRM) or request clarification.
- **Rationale**: Artefact 3 shows customer provided order number in SMS inquiry. Typical customer behavior: order confirmation email/SMS includes order number, customers reference it in follow-up inquiries.
- **Impact**: Affects agent NLP task complexity (order extraction). If provision rate <50%, increases ambiguous cases requiring human escalation.
- **Validation needed**: Analyze sample of ETA inquiry messages (email, SMS, phone transcripts) to measure actual order number provision rate.

### A047 - Human Approval Time (Agent-led + Oversight)
- **Category**: ORG
- **Confidence**: Medium (60%)
- **Assumption**: Human approval for "Agent Proposes, Human Approves" cases takes average 30 seconds per case (review agent recommendation in dashboard, click "Approve" or "Override"). Approval mechanism: web dashboard shows pending cases, one-click approval workflow.
- **Rationale**: Simple approve/override decision with agent-provided context (ETA calculation, reasoning) should take <1 minute. 30 seconds is conservative estimate assuming human reviews 2-3 data points before approving.
- **Impact**: Affects HITL cost calculation (approval time × hourly cost). If actual approval time >2 min, increases HITL cost and reduces agent ROI.
- **Validation needed**: Time-study human approvals in pilot; optimize dashboard UI for fast review if approval time >1 min.

### A048 - Customer Inquiry History Threshold
- **Category**: PROC
- **Confidence**: Medium (55%)
- **Assumption**: Agent retrieves customer inquiry history (prior ETA inquiries from CRM case records) if customer has >1 inquiry in past 30 days. This signals potential escalation pattern (repeat delays, dissatisfied customer). If ≥3 inquiries in 30 days → escalate to supervisor for proactive outreach.
- **Rationale**: Repeat inquiries indicate delivery reliability issues or customer dissatisfaction. Threshold of 3 inquiries balances sensitivity (catches escalation patterns) vs. specificity (avoids false positives for customers with multiple legitimate orders).
- **Impact**: Improves customer relationship management (proactive escalation before formal complaint). Requires CRM field to track inquiry count or query case history on demand.
- **Validation needed**: Analyze CRM case data to measure frequency of repeat inquiries; validate 3-inquiry threshold is meaningful signal.

### A049 - Salesforce API Base URL
- **Category**: SYS
- **Confidence**: Low (40%)
- **Assumption**: Apex Distribution's Salesforce instance base URL is `https://apex-distribution.salesforce.com/services/data/v60.0/`. API version is v60.0 (latest as of 2026). Actual URL and version must be confirmed with Apex IT team.
- **Rationale**: Standard Salesforce URL pattern for custom domains. API version v60.0 is current in 2026 (Salesforce releases 3 versions/year).
- **Impact**: URL and version required for API client configuration. If incorrect, API calls fail during integration testing.
- **Validation needed**: Confirm with Apex IT team in Week 1 discovery; update API client configuration.

### A050 - Customer Inquiry History Count Field
- **Category**: DATA
- **Confidence**: Medium (50%)
- **Assumption**: CRM does not have `inquiry_history_count` custom field on Contact object. If needed (for repeat inquiry detection [A048]), requires custom field creation in Salesforce and nightly batch job to update count from Case history.
- **Rationale**: Standard Salesforce Contact object does not include inquiry count. Custom field is simple to create but requires data backfill and ongoing maintenance.
- **Impact**: If field missing, agent queries Case history on demand (higher API cost: +1 API call per inquiry with repeat customers ~20% → +28 calls/day → negligible impact). Custom field optimizes performance but not critical.
- **Validation needed**: Check Salesforce schema with IT team; decide if custom field worth build effort or use on-demand query.

### A051 - Agent Actions JSON Field
- **Category**: DATA
- **Confidence**: Medium (55%)
- **Assumption**: CRM Case object requires custom field `Agent_Actions__c` (long text/JSON type) to store agent decision reasoning, data sources queried, ETA calculation details, confidence scores for audit trail. Standard Case object has `Description` field but insufficient structured storage for detailed audit data.
- **Rationale**: Audit trail requirement for governance [governance element of enterprise agents]. JSON field allows structured logging ({"data_sources": ["crm", "gps"], "eta_calculation": {...}, "confidence": 0.85}) that is queryable and exportable for compliance reviews.
- **Impact**: Custom field required for production deployment. Without this, agent logs to external audit DB (increases complexity). Custom field is simpler and keeps audit data in CRM alongside case records.
- **Validation needed**: Confirm with IT team; create custom field in Week 2 of build sprint.

### A052 - Salesforce API Rate Limits
- **Category**: SYS
- **Confidence**: High (75%)
- **Assumption**: Apex Distribution has Salesforce Enterprise Edition with 100,000 API calls per 24 hours rate limit (standard Enterprise tier). Agent usage is 420 calls/day (140 cases × 3 calls: order, contact, case creation) = 0.4% of limit → no risk of rate limit breach.
- **Rationale**: Salesforce Enterprise Edition standard rate limit (documented in Salesforce API limits). Agent volume is modest relative to limit.
- **Impact**: Confirms API rate limit is not a constraint for pilot or production. If Apex has lower tier (Professional Edition: 15,000 calls/day), would need rate limit management (caching, request throttling).
- **Validation needed**: Confirm Salesforce edition with IT team; verify actual rate limit allocation.

### A053 - Driver App API Base URL and Version
- **Category**: SYS
- **Confidence**: Low (30%)
- **Assumption**: Driver app backend exposes REST API at `https://driver-app.apex-distribution.com/api/v1/` with endpoints for GPS location, delivery status, route sequence. API authentication is via API key. **This is speculative**; actual API availability, URL, and auth method must be validated with IT team in Week 1 discovery.
- **Rationale**: Modern mobile apps typically have REST API backend for data sync. Assumed standard REST patterns (versioned API, API key auth). However, driver app is in-house build (not off-the-shelf) → API may not exist or may be undocumented.
- **Impact**: **Critical blocker validation** [A003]. If API does not exist, requires API wrapper build (+2-3 weeks) or direct DB query (if permissions granted). Pilot cannot proceed without GPS/delivery status access.
- **Validation needed**: **Week 1 priority** — IT discovery to confirm API availability, obtain API documentation, test endpoints.

### A054 - Historical Timing Data Completeness
- **Category**: DATA
- **Confidence**: Medium (50%)
- **Assumption**: Driver app logs delivery events with sufficient completeness (timestamps for arrival, departure, delivery) to enable historical timing pattern aggregation. Requires 6-12 months of clean logs for statistical validity (min 20 samples per route × time bucket). If logs are incomplete (<50% of deliveries have timestamps), historical timing DB will be sparse → ETA accuracy degraded.
- **Rationale**: ETA calculation engine relies on historical avg stop duration. Without clean logs, agent falls back to default timing assumptions (15 min/stop [A055]) → less accurate ETAs.
- **Impact**: **Medium risk** for ETA accuracy. If logs incomplete, pilot ETA accuracy may be 85-90% (vs. 95% target [A042]) until 3-6 months of post-pilot data collected.
- **Validation needed**: **Week 1 discovery** — Query driver app DB for sample month of logs; assess timestamp completeness and data quality.

### A055 - Default Timing Assumption Fallback
- **Category**: PROC
- **Confidence**: Medium (60%)
- **Assumption**: If historical timing data is unavailable or sparse for a route, agent uses default assumption of 15 minutes per stop (generic avg across all Apex routes). This is a fallback for cold start scenarios (new routes, sparse data). Default assumption is less accurate than route-specific historical timing but prevents agent from being unable to calculate ETA.
- **Rationale**: 15 min/stop is conservative estimate based on typical logistics operations (5 min drive between stops + 5 min delivery + 5 min buffer). Actual stop duration varies (residential vs. commercial, parcel count), but 15 min is reasonable approximation.
- **Impact**: Affects ETA accuracy for new/sparse routes (~5% of cases). Agent flags ETA as "low confidence" when using default assumption → may escalate if confidence <70% [A044].
- **Validation needed**: Validate 15 min assumption against Apex's actual avg (analyze historical logs for all-route average).

### A056 - SLA Committed Window Fields in CRM
- **Category**: DATA
- **Confidence**: Medium (50%)
- **Assumption**: Salesforce Order object does not have fields for committed delivery window start/end timestamps. SLA terms are in customer contracts (not digitized in CRM). Agent requires these fields for SLA breach detection. Options: (1) Create custom fields and migrate SLA data from contracts/dispatch console, (2) Use default SLA windows by customer tier (high-priority = 2-hour window, standard = 4-hour window).
- **Rationale**: Standard Salesforce Order object has delivery date field but not time-specific windows. Apex's SLA terms likely in contracts; CRM integration may be incomplete.
- **Impact**: **Medium risk** for SLA breach detection accuracy. Wave 1 pilot can use default windows by tier [A009]; Wave 2 prep should formalize SLA data in CRM.
- **Validation needed**: Check Salesforce schema with IT; assess feasibility of SLA data migration vs. using tier-based defaults.

### A057 - Hard-Coded High-Priority Accounts Fallback
- **Category**: PROC
- **Confidence**: Medium (55%)
- **Assumption**: If customer priority tier field [A009] is unavailable in CRM, agent uses hard-coded list of known high-priority accounts (Hayes & Sons, Northstar Foods, Travis & Mason Ltd, etc.) based on scenario artefacts. This is a temporary workaround for Wave 1 pilot; formalized priority system required for Wave 2.
- **Rationale**: Scenario artefacts show Hayes & Sons appears 3× in samples, always handled by Sandra → clearly high-priority. Hard-coding known accounts is pragmatic short-term solution while priority system is formalized [A009 validation in Wave 2 prep].
- **Impact**: **Low risk** for pilot (covers 80%+ of high-priority accounts). Incomplete for production (new high-priority customers not on list → treated as standard). Formalization required for Wave 2.
- **Validation needed**: Compile list of high-priority accounts from Sandra interview; validate coverage against top 20% revenue customers.

### A058 - Twilio SMS Pricing UK
- **Category**: ORG
- **Confidence**: High (75%)
- **Assumption**: Twilio SMS pricing for UK recipients is approximately £0.04 per SMS (standard UK mobile rate). Volume: 140 SMS/day × £0.04 = £5.60/day = £2,044/year. This is included in agent cost model (£0.05 per case API cost covers SMS + email + other APIs).
- **Rationale**: Twilio UK pricing publicly documented (https://www.twilio.com/en-us/pricing). Rate varies slightly by carrier but £0.04 is typical for UK mobile.
- **Impact**: Confirms SMS cost is within budget. If actual rate >£0.06/SMS, increases agent cost per case from £0.57 to £0.60 (marginal impact on ROI).
- **Validation needed**: Confirm Twilio pricing with actual Twilio account tier; negotiate volume discount if applicable.

### A059 - Customer Phone Number Completeness
- **Category**: DATA
- **Confidence**: Medium (55%)
- **Assumption**: Approximately 20% of customers in CRM do not have valid phone numbers on file (missing or incorrect). Agent cannot send SMS to these customers → falls back to email or escalates to human for phone call follow-up. Data quality issue requiring CRM cleanup initiative.
- **Rationale**: Typical B2B/B2C CRM data quality: phone numbers are less reliably maintained than email addresses. 20% missing rate is conservative estimate based on industry norms.
- **Impact**: Affects notification channel distribution (80% SMS, 20% email/escalation). **Low risk** — email is viable fallback. CRM cleanup post-pilot improves phone completeness.
- **Validation needed**: Query CRM for % of Contact records with populated phone number field; assess actual missing rate.

### A060 - SendGrid Email Pricing
- **Category**: ORG
- **Confidence**: High (80%)
- **Assumption**: SendGrid email pricing is approximately £0.001 per email (first 100,000 emails/month free on standard tier). Volume: 140 emails/day = 32,200 emails/year = £32/year (negligible cost). This is included in agent cost model (£0.05 per case API cost).
- **Rationale**: SendGrid pricing publicly documented (https://sendgrid.com/pricing). Free tier covers pilot volume; paid tier is £0.001/email.
- **Impact**: Confirms email cost is negligible (<1% of total agent cost). No budget risk.
- **Validation needed**: Confirm SendGrid account tier with IT; ensure free tier limit (100K emails/month) is not exceeded by other Apex systems.

### A061 - Customer Email Bounce Rate
- **Category**: DATA
- **Confidence**: Medium (60%)
- **Assumption**: Approximately 10% of customer email addresses in CRM are invalid (bounce, spam filter, incorrect). Agent logs bounce and escalates to human for phone follow-up. Data quality issue requiring CRM cleanup.
- **Rationale**: Typical email bounce rate for B2B CRM data is 5-15%. 10% is mid-range estimate. Includes hard bounces (invalid address) and soft bounces (mailbox full, spam filter).
- **Impact**: Affects email notification success rate (90% delivered). **Low risk** — agent handles bounce gracefully (logs error, escalates). CRM cleanup post-pilot improves email quality.
- **Validation needed**: Pilot email bounce rate measurement over 2-4 weeks; initiate CRM data cleanup for bounced emails.

### A062 - Google Maps Traffic API Pricing
- **Category**: ORG
- **Confidence**: High (75%)
- **Assumption**: Google Maps Distance Matrix API (with traffic) pricing is approximately £0.005 per request. Volume: 140 requests/day = £0.70/day = £256/year. This is optional Wave 1 cost (traffic API may not be included in pilot).
- **Rationale**: Google Maps API pricing publicly documented (https://mapsplatform.google.com/pricing). Distance Matrix with traffic is £0.005/request.
- **Impact**: Confirms traffic API cost is marginal (£256/year = 0.5% of agent annual cost). Inclusion decision based on ETA accuracy need (if historical timing alone achieves 95% accuracy [A042], traffic API is optional).
- **Validation needed**: Pilot without traffic API initially; measure ETA accuracy; add traffic API in Month 2-3 if accuracy <90%.

---

## Assumption Summary by Confidence Level

### High Confidence (70-85%): 13 assumptions
- A004, A006, A007, A012, A015, A024, A030, A036, A038, A041, A052, A058, A060, A062

### Medium Confidence (50-70%): 32 assumptions  
- A001, A003, A005, A008, A009, A010, A011, A013, A014, A016, A018, A020, A021, A022, A023, A025, A026, A027, A028, A031, A032, A033, A034, A037, A040, A042, A043, A044, A045, A046, A047, A048, A050, A051, A054, A055, A056, A057, A059, A061

### Low Confidence (30-45%): 7 assumptions
- A002, A017, A019, A029, A035, A039, A049, A053

**Total Assumptions**: 62 (updated after Agent Mapping for DE-3)

---

## Validation Priority

### Critical Path (must validate before agent design)
1. A004 - Dispatch console API capabilities
2. A007 - Billing system integration timeline  
3. A015 - Aurum schema stability
4. A005 - Refused delivery decision rules

### High Priority (validate during discovery phase)
1. A003 - Driver app data completeness
2. A006 - SOP vs. lived process gap
3. A008 - Sandra's manual override authority
4. A012 - Cross-work-stream dependencies

### Medium Priority (validate during pilot)
1. A001, A011 - Volume distributions and peaks
2. A009 - Customer tier system
3. A013 - CRM data completeness
4. A014 - Driver communication preferences

### Low Priority (validate during scale)
1. A002 - Dispatcher knowledge distribution

---

## Document Control
- **Created**: 2026-05-06
- **Last Updated**: 2026-05-06 (Agent Mapping update: added A042-A062)
- **Owner**: AI FDE Team
- **Review Cadence**: Update after each discovery interview; full review before build sprint kickoff
