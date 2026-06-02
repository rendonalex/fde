# Assumptions Register — Helix Therapeutics PV Triage System

**Document Version**: 1.0  
**Date**: 2026-06-01  
**Project**: Agentic Adverse Event Triage System

---

## Overview

This register captures all critical assumptions made beyond what is explicitly stated in the scenario. Each assumption includes: ID, statement, assumed value, confidence level, reasoning, and dependencies/references.

**Confidence Levels**:
- **High (80-95%)**: Strong industry data or logical inference from scenario facts
- **Medium (55-75%)**: Reasonable inference with some uncertainty
- **Low (30-50%)**: Significant uncertainty; requires early validation

---

## Critical Assumptions

### A1: Manual Case Processing Time Breakdown

**Assumption**: Of the 75-minute baseline per case, approximately:
- 35 min (47%) — data extraction and normalization from heterogeneous sources
- 15 min (20%) — seriousness classification per ICH E2A criteria
- 10 min (13%) — expectedness assessment against RSI
- 10 min (13%) — reportability determination logic
- 5 min (7%) — documentation and audit trail creation

**Confidence**: Medium (65%)

**Reasoning**: Dr. Iyer's quote emphasizes "boring synthesis" as the primary time sink — extraction, classification, and lookup work. Industry benchmarks from pharmacovigilance case processing studies (FDA guidances, CIOMS working groups) suggest that data harmonization from heterogeneous sources consumes 40-50% of intake time. Medical judgment (reportability decision) is typically faster once structured data is available.

**Why This Matters**: The 35-minute extraction component is the primary AI delegation target. If extraction is only 20% of total time, the 75→20 min target becomes unachievable through AI intake alone.

**Dependencies**: Directly impacts success metric calculations for time savings.

---

### A2: Distribution of AE Report Formats

**Assumption**: Of 6,000 annual AE reports (based on mock data available for prototype):
- 30% HCP report forms (text files, email with narrative text)
- 25% patient direct reports (web form JSON, phone transcripts VTT)
- 20% social media monitoring extracts (JSON with conversation threads)
- 15% clinical trial site reports (text with MedDRA codes)
- 10% literature alerts (published case reports, text format)

**Confidence**: Medium (60%)

**Reasoning**: The scenario's 8-case mock-data sample includes this format mix in text-based formats (no PDFs provided). Mock data has .txt (HCP reports, trial sites, literature), .json (webforms, social media), .vtt (phone transcripts), and .md (product RSI) formats. Modern pharmacovigilance intake increasingly includes digital and social media channels (~40-50% per industry reports), with traditional HCP reports declining but still significant. Literature and trial-site reports are smaller but required per regulatory obligations.

**Why This Matters**: Determines text parsing pipeline complexity and per-case token costs. Social media extracts require more sophisticated NLP (patient identifier challenges, non-medical language). Trial-site reports are easiest (already structured).

**Dependencies**: Impacts A5 (token economics) and A8 (text parsing build complexity).

---

### A3: Seriousness Classification Accuracy Requirement Context

**Assumption**: The 96% seriousness classification accuracy target allows for 4% error rate because:
- False negatives (serious AE classified as non-serious) are caught by medical safety officer review before submission
- False positives (non-serious classified as serious) result in unnecessary expedited reporting but do not create patient safety or regulatory risk
- 96% represents achievable LLM performance on structured ICH E2A criteria with CoT reasoning

**Confidence**: High (85%)

**Reasoning**: ICH E2A seriousness criteria are explicitly defined and codified (death, life-threatening, hospitalization, disability, congenital anomaly, other medically important). This is a classification task with clear rules, not ambiguous medical judgment. GPT-4 / Claude Opus-class models achieve >95% accuracy on similar rule-based classification with structured prompts. The scenario emphasizes that the medical safety officer signs off — so the system is providing a recommendation, not making the final decision.

**Why This Matters**: Justifies AI delegation of seriousness classification. If accuracy were required at 99.5%, full HITL verification would eliminate time savings.

**Dependencies**: Referenced in success metric for seriousness classification accuracy.

---

### A4: Expectedness Signal Precision — What "Unexpected" Means

**Assumption**: "Expectedness signal precision ≥85%" means:
- Of all AEs flagged by AI as "unexpected" (not listed in product RSI), 85% are confirmed unexpected by medical safety officer review
- 15% false-positive rate is acceptable because flagging an expected AE as unexpected results in unnecessary expedited reporting but does not create compliance risk (over-reporting is safer than under-reporting)
- False negatives (unexpected AE flagged as expected) would be more serious but are mitigated by medical safety officer review

**Confidence**: High (80%)

**Reasoning**: FDA and EMA guidance emphasize that over-reporting serious unexpected AEs is preferred to under-reporting. The 15-day clock applies to serious-unexpected; if AI flags an expected event as unexpected, the worst outcome is unnecessary expedited reporting. The medical safety officer reviews all recommendations, providing a safety net for false negatives.

**Why This Matters**: Defines acceptable error modes. The system should err toward flagging unexpected when uncertain.

**Dependencies**: Referenced in success metric for expectedness signal precision.

---

### A5: Token Economics — Cost Per Case

**Assumption**: Per-case token cost for AI triage processing:
- Input tokens per case: ~8,000 tokens average (varies by format: 3K for structured trial reports, 15K for social media threads)
- Output tokens per case: ~2,000 tokens (structured extraction + classification reasoning + reportability recommendation)
- Total: ~10,000 tokens per case at Claude Opus 4 pricing ($15 per 1M input, $75 per 1M output) = ~$0.27 per case
- Annual token cost: 6,000 cases × $0.27 = ~$1,620

**Confidence**: Medium (70%)

**Reasoning**: The mock-data files vary significantly in length (phone transcripts are verbose, trial reports are structured). 8K input tokens reflects a weighted average across formats per A2 distribution. Output tokens include structured JSON extraction (ExtractionResult entity), CoT reasoning for seriousness classification, expectedness assessment, and reportability recommendation with citations — estimated at 1.5-2K tokens. Pricing is Claude Opus 4.7 pricing as of 2026.

**Why This Matters**: Token costs are <1% of total budget ($1,620 / $510K = 0.3%), so cost optimization is not the primary concern. Build cost and human oversight cost dominate.

**Dependencies**: Referenced in economics analysis and per-case cost modeling.

---

### A6: Medical Safety Officer Time Reduction

**Assumption**: If AI reduces per-case processing from 75 min → 20 min:
- Medical safety officer saves 55 min per case on intake synthesis
- That time is redirected to higher-value work: medical assessment quality, causality evaluation, complex case investigation
- Does NOT result in headcount reduction but enables throughput increase without new hires

**Confidence**: High (85%)

**Reasoning**: Dr. Iyer explicitly states: "I do not want AI to write my medical assessment. I want AI to do the boring synthesis so I can write the assessment." Theo Lonergan (Head of Drug Safety Ops) states: "We are hiring case processors. I'd rather not." The value is avoiding new hires as volume grows, not reducing existing headcount. This is consistent with pharmacovigilance operational models — regulatory workload is growing (new marketed products, expanded post-market surveillance), and throughput constraints are a bottleneck.

**Why This Matters**: The business case is NOT cost reduction through layoffs; it is capacity expansion without proportional hiring. This aligns incentives (safety physicians want better tools, not job threats).

**Dependencies**: Impacts ROI calculation and stakeholder alignment.

---

### A7: 15-Day Clock Compliance Failure — Root Cause

**Assumption**: Current 92% 15-day clock compliance means ~8% of serious-unexpected AEs miss the 15-day FDA deadline. Root causes:
- 50% due to delayed intake (report sits in queue before case processor starts)
- 30% due to slow extraction from complex text formats (HCP narratives, social media, literature)
- 20% due to back-and-forth with reporter for missing information

**Confidence**: Medium (60%)

**Reasoning**: Dr. Carmichael states: "The 15-day clock starts the moment any Helix employee or contractor receives the report, not when we open it." This indicates queue time is part of the problem. Theo Lonergan mentions backlog and capacity constraints. The scenario emphasizes heterogeneous formats and "messiness." The 92% baseline is below the 99.5% target, and Maeve's framing emphasizes career consequences of late SAE reporting — suggesting this is a high-stakes pain point.

**Why This Matters**: If queue time is 50% of the problem, AI intake acceleration alone won't fully solve compliance. May require operational process changes (auto-routing, prioritization logic) in addition to AI triage.

**Dependencies**: Impacts design of intake prioritization and queue management logic.

---

### A8: Text Parsing Pipeline Build Complexity and Cost

**Assumption**: Building a text parsing pipeline for heterogeneous formats (text, JSON, VTT):
- Requires LLM-based extraction for unstructured text (HCP narratives, patient phone transcripts, social media)
- Requires per-field confidence scoring for extraction validation
- Requires handling of table extraction (medication history, concomitant meds)
- Estimated build effort: 3-hour prototype window within 8-hour exam
- No external dependencies (all formats are text-based in mock data)

**Confidence**: Medium (60%)

**Reasoning**: The scenario states 8-hour build window with Claude Code as required tool, and provides mock data in text-based formats (no PDFs). Modern LLM-based document extraction (Claude 3.5 Sonnet, Claude Opus) can handle heterogeneous text formats (HCP narratives, JSON structured webforms, VTT phone transcripts) with per-field confidence scores. Build complexity is moderate for text parsing (not requiring OCR or image processing), achievable within 3-hour prototype build window.

**Why This Matters**: Text parsing is simpler and faster to build than PDF OCR pipeline, making prototype feasible within exam time constraints. Mock data format determines build scope.

**Dependencies**: Impacts Wave 1 deliverable scope and build timeline.

---

### A9: Reportability Recommendation Acceptance Rate — What It Measures

**Assumption**: "Reportability recommendation precision ≥88%" means:
- Of all reportability recommendations (15-day expedited, periodic only, non-reportable), the medical safety officer accepts 88% as-is without revision
- 12% are revised due to: edge cases (concomitant med causality, off-label use, literature case interpretation), global reportability variance (FDA vs PMDA vs EMA), or clinical judgment factors not captured in the AI logic
- Revision does not mean the AI recommendation was wrong — it may reflect legitimate medical judgment calls where reasonable people disagree

**Confidence**: Medium (70%)

**Reasoning**: Reportability determination involves both rule-based logic (seriousness + expectedness = 15-day expedited per FDA) and judgment calls (causality, global variance, product-specific factors). Carolina Núñez-Reyes warns: "What's reportable to FDA in 15 days is not the same as what's reportable to PMDA." The 88% target allows for 12% clinical override while still delivering value (reduced back-and-forth, structured reasoning provided to safety officer).

**Why This Matters**: Defines acceptable system performance. The AI is not expected to be perfect — it is expected to provide defensible recommendations that save time.

**Dependencies**: Referenced in success metric for reportability recommendation precision.

---

### A10: Audit Trail Requirement — What Greta and Dr. Mansour Need

**Assumption**: "100% per-case audit trail completeness" means:
- Every extraction must include span-level citations (which text in the source report supports each extracted field)
- Every classification decision must include reasoning (which ICH E2A criterion applies, why)
- Every reportability recommendation must include rule-based justification (seriousness + expectedness → 15-day expedited per FDA 21 CFR 314.80)
- Audit trail must be machine-generated and retrievable on-demand for FDA inspection

**Confidence**: High (85%)

**Reasoning**: Greta Schäffer (Chief Compliance Officer) states: "Every reportability call needs to be defensible to an FDA inspector with the underlying evidence on demand." Dr. Hadi Mansour (external auditor, former FDA reviewer) states: "AI in pharmacovigilance is acceptable when it accelerates human safety physicians and is transparent. It is not acceptable when it makes the medical assessment." The scenario emphasizes span-level citations and reasoning transparency. This is consistent with FDA guidance on AI in regulated industries — explainability and traceability are required.

**Why This Matters**: This is a hard requirement, not a nice-to-have. System must be designed with audit trail generation as a core capability from the start, not bolted on later.

**Dependencies**: Impacts entity model design (AECasePackage must include citations and reasoning fields) and validation plan.

### A11: Case Processor Triage Step — Queue Risk-Sorting

**Assumption**: Case processors spend ~5-10 minutes per day risk-sorting the intake queue (scanning subject lines, source channels, patient identifiers to identify potential serious-unexpected cases that must be opened immediately to anchor the 15-day clock). This triage step is not reflected in the SOP and contributes to queue delay.

**Confidence**: Low (45%)

**Reasoning**: The lived process narrative (from shadowing observations, inferred) indicates that intake is not FIFO but risk-sorted. AE reports arrive in bursts (clinical trial site reports batch on Fridays, social media monitoring sends daily digests, patient phone calls spike on Mondays). Case processors must prioritize serious-unexpected cases to avoid 15-day clock compliance failures. This is a **cognitive task** (pattern recognition, risk assessment) not documented in the SOP.

**Why This Matters**: If triage adds 5-10 min per day per case processor, and this step is not automated or eliminated by AI intake, then queue delay per [A7] persists. AI intake with automated seriousness/expectedness flagging could eliminate this triage step entirely.

**Dependencies**: Referenced in Cognitive Load Map lived process narrative. Impacts [A7] queue delay root cause analysis.

---

### A12: Medical Safety Officer Deep Review Frequency and Time

**Assumption**: Medical safety officer deep review (for ambiguous seriousness cases, especially "other medically important" criterion) occurs in ~10% of cases and adds ~15 minutes per flagged case beyond the baseline 75-minute per-case average.

**Confidence**: Medium (55%)

**Reasoning**: ICH E2A seriousness criteria are explicit for death, hospitalization, disability, congenital anomaly. "Other medically important" is judgment-dependent and requires clinical reasoning about whether medical intervention was required to prevent serious outcome. Dr. Iyer's statement ("I do not want AI to write my medical assessment. I want AI to do the boring synthesis so I can write the assessment") implies that medical judgment is a distinct, higher-value activity that cannot be rushed. 10% deep review rate is conservative based on industry norms for pharmacovigilance case complexity distributions.

**Why This Matters**: If deep review is required in 30% of cases (not 10%), then residual human effort after AI delegation is higher than baseline modeling suggests. Agent-led + Human Oversight design must account for realistic MSO review time.

**Dependencies**: Referenced in Cognitive Load Map breakpoints. Impacts success metric modeling for per-case time reduction.

---

### A13: Expectedness Determination Review Rate by Seriousness

**Assumption**: Medical safety officer reviews all serious-unexpected cases (~15-20% of total per industry norms) for expectedness determination. Serious-expected and non-serious cases (~80-85%) can be processed with lower oversight (agent recommendation accepted as-is or spot-checked).

**Confidence**: Medium (60%)

**Reasoning**: FDA 21 CFR 314.80 requires 15-day expedited reporting for serious-unexpected AEs. False negatives (unexpected AE flagged as expected) create compliance risk and patient safety risk. Therefore, medical safety officer has strong incentive to review all unexpected determinations. Serious-expected and non-serious cases have lower compliance consequence (periodic reporting vs. expedited reporting), so agent recommendations can be accepted with spot-check verification rather than 100% review.

**Why This Matters**: If all 6,000 cases require 100% MSO review for expectedness (not just serious-unexpected subset), then residual human effort is 6,000 × review time, not 1,200 × review time. This impacts success metric for per-case time reduction and MSO capacity expansion.

**Dependencies**: Referenced in Cognitive Load Map breakpoints. Impacts delegation archetype design (Agent-led + Human Oversight vs. Agent-led + Spot Check).

---

### A14: Multi-Jurisdictional Reportability Complexity Prevalence

**Assumption**: Multi-jurisdictional reportability complexity (FDA vs. EMA vs. PMDA vs. MHRA) adds cognitive load for ~25% of cases (products marketed in >2 jurisdictions). The remaining 75% are U.S.-only or FDA + EMA (aligned timelines).

**Confidence**: Medium (50%)

**Reasoning**: Helix Therapeutics has three marketed products (Solivian, Tezarimab, Phaedora). Carolina Núñez-Reyes (VP Regulatory Affairs) warns: "What's reportable to FDA in 15 days is not the same as what's reportable to PMDA." This implies that at least some cases require multi-jurisdictional assessment. However, the scenario does not state which products are marketed in which jurisdictions. Industry norms: large pharma products are typically marketed in U.S. + EU + Japan + UK (~4-5 major markets), but mid-sized pharma companies like Helix may have more limited geographic footprint. 25% multi-jurisdictional complexity is a conservative mid-point estimate.

**Why This Matters**: If 75% of cases require multi-jurisdictional assessment (not 25%), then reportability recommendation logic complexity increases significantly. Agent must handle global reportability variance for majority of cases, not just edge cases. This impacts IDP build scope, system prompt complexity, and token costs.

**Dependencies**: Referenced in Cognitive Load Map micro-task inventory (5.2 Apply multi-jurisdictional reportability rules). Impacts JtD-5 delegation suitability and reportability recommendation precision target.

---

### A15: HITL Validation Threshold for Data Extraction

**Assumption**: HITL validation threshold for data extraction: any required field confidence < 0.85 → case processor HITL validation queue. Expected HITL rate: ~12% of cases (30% unstructured formats per [A2] × 40% low-confidence rate).

**Confidence**: Medium (60%)

**Reasoning**: The 0.85 confidence threshold balances patient safety (high-stakes extraction errors create downstream classification errors → 15-day reporting risk) with operational efficiency (HITL rate too high → time savings erode). Industry benchmarks for IDP in regulated environments (healthcare, finance) typically use 0.80-0.90 thresholds for required fields. 0.85 is mid-point. The 40% low-confidence rate for unstructured formats is based on LLM document extraction performance on pharmacovigilance case narratives (patient phone transcripts, social media posts) in pilot studies.

**Why This Matters**: If HITL rate is 30% (not 12%), then residual human effort for ADR-2 increases significantly and time savings target (75 min → 20 min) becomes unachievable. If threshold is too low (0.70), false-negative risk (low-quality extraction flagged as high-confidence) increases → downstream errors → 15-day compliance risk.

**Dependencies**: Referenced in ADR-2 delegation suitability analysis. Impacts per-case time reduction modeling and HITL operational design.

**Validation owner**: Calibrate threshold on 200-case validation set with case processor labels in Week 1 discovery. Monitor HITL rate in Wave 1 shadow mode and adjust threshold if needed.

---

### A16: PV Case Management System API Availability

**Assumption**: PV case management system write API available for case record creation (ADR-1), structured data write (ADR-2), classification/expectedness/reportability writes (ADR-3, ADR-4, ADR-5). Product RSI/CCSI database queryable via API or structured data export. API SLA and authentication method to be confirmed in Week 1 IT discovery.

**Confidence**: Medium (55%)

**Reasoning**: The scenario states Helix has a PV case management system ("Every single [AE report] must be triaged for seriousness, expectedness, and reportability"). Modern PV systems (Veeva Vault Safety, Oracle Argus, ArisGlobal LifeSphere) have RESTful APIs for case data CRUD operations. However, the scenario does not explicitly state API availability. If API is not available, batch file integration (XML, CSV) is fallback but adds latency and complexity. Product RSI/CCSI must be queryable for expectedness assessment (ADR-4) — worst case, export to structured JSON or database for agent access.

**Why This Matters**: If PV system API is not available, entire architecture depends on batch file integration → adds latency (hours to days) → 15-day compliance target at risk. Product RSI/CCSI must be queryable for expectedness assessment (ADR-2) — mock data provides structured markdown files (Solivian_RSI.md, Tezarimab_RSI.md, Phaedora_RSI.md) which are sufficient for prototype.

**Dependencies**: Impacts all ADRs (ADR-1 through ADR-5) for data read/write operations. Blocking dependency for Wave 1 build.

**Validation owner**: Week 1 IT discovery sprint with PV IT team. Confirm API endpoints, authentication, SLA, and product RSI/CCSI data format. Go/No-Go decision point before Wave 1 build begins.

---

### A17: Fully Loaded Hourly Cost — Medical Safety Officer

**Assumption**: Medical safety officer fully loaded hourly cost = $85/hour
- Base salary: $120K/year (industry benchmark for mid-level pharma MSO)
- Benefits + overhead (40%): $48K
- Total fully loaded: $168K/year
- Working hours: 1,976 hours/year (52 weeks × 38 hours/week, accounting for PTO)
- Hourly rate: $168K / 1,976 hours = $85/hour

**Confidence**: High (75%)

**Reasoning**: Glassdoor and Salary.com data for Medical Safety Officer roles at mid-sized pharma companies (comparable to Helix: ~1,200 employees, $680M revenue) show base salary range $100K-$140K. $120K is mid-range. 40% overhead multiplier is standard for fully loaded cost (benefits, payroll taxes, management, facilities, opportunity cost).

**Why This Matters**: Baseline cost determines ROI calculation. If actual hourly cost is lower ($65/hour), annual baseline cost reduces to $455K and annual savings reduce to $311K, but payback period is still <3 months.

**Dependencies**: Impacts TCO assessment and ROI calculations for both ADRs.

---

### A18: Build Cost Estimates — ADR-1 and ADR-2

**Assumption**: Build cost breakdown:
- **ADR-1**: $50K total (FDE 2 weeks $20K + text parsing $15K + integration $10K + testing $5K)
- **ADR-2**: $30K total (FDE 1.5 weeks $15K + system prompt $8K + RSI integration $3K + testing $4K)
- **Combined**: $80K

**Confidence**: Medium (65%)

**Reasoning**: FDE hourly rate $150-200/hour × 40 hours/week = $6K-8K/week → $10K/week is high-end estimate including overhead. Text parsing pipeline build ($15K) reflects 1 week of core development + 1 week of prompt engineering and testing. Integration build ($10K ADR-1, $3K ADR-2) reflects API discovery and connector development. Testing ($5K + $4K) reflects validation on 8 mock cases + stakeholder review cycles.

**Why This Matters**: Build cost determines payback period and Year 1 ROI. If actual build cost is $120K (50% higher), payback period extends to 3.2 months and Year 1 ROI drops to 366%, but still passes economic gate (>0%, <18 months).

**Dependencies**: Impacts ROI calculations and Wave 1 self-financing justification.

---

### A19: Historical Validation Set Availability

**Assumption**: Helix can provide 100-200 historical AE cases with ground-truth labels:
- Seriousness classification (serious/non-serious with ICH E2A criterion)
- Expectedness determination (expected/unexpected per product RSI)
- Reportability decision (15-day expedited / periodic / non-reportable)
- Medical safety officer adjudication recorded

This validation set is required to measure:
- Metric 3: Seriousness classification accuracy ≥96%
- Metric 4: Expectedness signal precision ≥85%
- Metric 5: Reportability recommendation acceptance ≥88%

**Confidence**: Medium (60%)

**Reasoning**: Most pharmaceutical companies maintain case archives with adjudication history for quality assurance and regulatory inspection readiness. However, the availability of structured labels (vs. free-text case files) is uncertain. The 8-case mock data sample provides format examples but not ground-truth labels for accuracy measurement.

**Why This Matters**: Without a labeled validation set, pre-deployment accuracy metrics cannot be measured directly. Alternatives include:
- Extended shadow mode (process cases in parallel with human workflow, compare outputs) — adds 60-90 days to timeline
- Manual labeling by MSO team (time-intensive, ~30 min per case to adjudicate + document reasoning)
- Reduced confidence in go-live decision (deploy based on mock data testing only, measure accuracy post-deployment)

**Validation owner**: Request from Dr. Iyer or Theo Lonergan in Week 1 discovery. If unavailable, plan extended shadow mode or MSO labeling sprint.

**Dependencies**: Impacts validation plan timeline and deployment confidence. Referenced in validation plan exit criteria.

---

## Summary Table

| ID | Assumption | Confidence | Impact if Wrong |
|----|-----------|-----------|-----------------|
| A1 | 75-min baseline breakdown (47% extraction, 20% classification, 13% expectedness, 13% reportability, 7% documentation) | Medium (65%) | Time savings target unachievable if extraction is not the primary bottleneck |
| A2 | Format distribution (30% HCP, 25% patient, 20% social media, 15% trial, 10% literature) | Medium (60%) | IDP complexity and token costs shift if social media volume is higher |
| A3 | 96% seriousness classification accuracy is achievable with LLM + CoT on ICH E2A criteria | High (85%) | If unachievable, HITL verification required, eliminating time savings |
| A4 | 85% expectedness precision allows 15% false-positive rate (over-reporting is safer than under-reporting) | High (80%) | If false-negatives are unacceptable, confidence thresholds must tighten |
| A5 | Token cost ~$0.27 per case, ~$1,620 annually for 6K cases | Medium (70%) | Cost remains negligible even if 2x higher; not a design constraint |
| A6 | Time savings enable throughput increase without new hires (not headcount reduction) | High (85%) | If stakeholders expect layoffs, change management fails |
| A7 | 15-day compliance failures: 50% queue delay, 30% extraction complexity, 20% reporter follow-up | Medium (60%) | If queue time is not the bottleneck, AI intake alone won't reach 99.5% |
| A8 | IDP pipeline buildable within Wave 1 scope with Claude Code + LLM vision capabilities | Medium (60%) | If vendor procurement required, budget and timeline break |
| A9 | 88% reportability recommendation acceptance allows 12% clinical override for edge cases | Medium (70%) | If acceptance rate is 50%, system provides insufficient value |
| A10 | Audit trail requires span-level citations, CoT reasoning, and rule-based justification for FDA inspection | High (85%) | If not built from day 1, system is non-compliant and cannot be deployed |
| A11 | Case processor triage step (risk-sorting intake queue) adds 5-10 min/day, contributes to queue delay per [A7] | Low (45%) | If triage is not a bottleneck, AI intake won't reduce queue delay as expected |
| A12 | Medical safety officer deep review occurs in ~10% of cases, adds ~15 min per flagged case | Medium (55%) | If deep review required in 30%+ of cases, residual human effort is higher than modeled |
| A13 | MSO reviews all serious-unexpected cases (~15-20%) for expectedness; spot-checks remaining 80-85% | Medium (60%) | If 100% MSO review required for all cases, time savings target breaks |
| A14 | Multi-jurisdictional reportability complexity applies to ~25% of cases (>2 jurisdictions) | Medium (50%) | If 75% require multi-jurisdictional assessment, recommendation logic complexity increases significantly |
| A15 | HITL validation threshold 0.85 for required fields; expected HITL rate ~12% of cases | Medium (60%) | If HITL rate is 30%, time savings target unachievable |
| A16 | PV case management system API available; product RSI/CCSI queryable | Medium (55%) | If API unavailable, batch integration adds latency → 15-day compliance at risk |
| A17 | Fully loaded MSO hourly cost $85/hour ($120K base + 40% overhead) | High (75%) | If actual cost is $65/hour, ROI remains positive but annual savings reduce by ~30% |
| A18 | Build cost: ADR-1 $50K, ADR-2 $30K (FDE time, development, integration, testing) | Medium (65%) | If actual cost is $120K (+50%), payback extends to 3.2 months but still passes economic gate |
| A19 | Historical validation set available: 100-200 labeled cases with ground-truth MSO adjudication | Medium (60%) | If unavailable, pre-deployment metric validation requires manual labeling or extended shadow mode |

---

## Validation Plan

**Week 1 Discovery (Must Resolve Before Build)**:
- **A1**: Interview case processors — time-motion study of actual 75-min breakdown
- **A2**: Pull intake queue stats for past 90 days — confirm format distribution
- **A7**: Root cause analysis of 15-day compliance failures with Theo Lonergan
- **A8**: Validate IDP build feasibility with Claude Code + sample non-EDI files
- **A11**: Shadow case processors for 1-2 days — quantify triage step time and cognitive load
- **A12**: Interview Dr. Iyer — confirm deep review frequency and time per ambiguous case
- **A13**: Pull PV case management system stats — confirm serious-unexpected case rate and MSO review patterns
- **A14**: Interview Carolina Núñez-Reyes — confirm product geographic footprint and multi-jurisdictional case prevalence
- **A15**: Calibrate HITL confidence threshold (0.85) on 200-case validation set with case processor labels
- **A16**: Week 1 IT discovery sprint with PV IT team — confirm API endpoints, authentication, SLA, product RSI/CCSI data format (Go/No-Go decision point)
- **A19**: Request historical validation set (100-200 labeled cases) from Dr. Iyer or Theo Lonergan

**Wave 1 Build Validation**:
- **A3**: Test seriousness classification on 50-case validation set with safety physician labels
- **A4**: Test expectedness flagging on 50-case validation set with RSI cross-reference
- **A9**: Pilot with Dr. Iyer on 20 cases — measure acceptance rate
- **A15**: Monitor HITL rate in Wave 1 shadow mode and adjust threshold if needed

**Post-Deployment Monitoring**:
- **A5**: Track actual token costs per case in production for 30 days
- **A6**: Survey safety officers after 60 days — confirm time savings enable higher-value work
- **A10**: Conduct mock FDA inspection audit trail retrieval test

---

**Document Owner**: FDE Engagement Lead  
**Next Review**: After Week 1 Discovery Sprint
