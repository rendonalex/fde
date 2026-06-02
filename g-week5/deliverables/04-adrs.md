# Architecture Decision Records (ADRs)

**Document Version**: 2.0  
**Date**: 2026-06-01  
**Project**: Helix Therapeutics Agentic Adverse Event Triage System

---

## Table of Contents

### ADR-1: Intake, Extract, and Normalize AE Data
1. [Cognitive Work Summary](#cognitive-work-summary-adr-1)
2. [Delegation Suitability Scoring](#delegation-suitability-scoring-adr-1)
3. [Delegation Archetype Assignment](#delegation-archetype-assignment-adr-1)
4. [Trade-offs](#trade-offs-adr-1)

### ADR-2: Medical Triage — Seriousness, Expectedness, and Reportability
5. [Cognitive Work Summary](#cognitive-work-summary-adr-2)
6. [Delegation Suitability Scoring](#delegation-suitability-scoring-adr-2)
7. [Delegation Archetype Assignment](#delegation-archetype-assignment-adr-2)
8. [Trade-offs](#trade-offs-adr-2)

---

# ADR-1: Intake, Extract, and Normalize AE Data

## Cognitive Work Summary (ADR-1)

**Trigger**: AE report received via any channel (HCP text report, patient web form, phone transcript, social media monitoring extract, clinical trial site report, literature alert)

**Goal**: Receive report, classify format, route appropriately, extract all structured data elements per ICH E2D, normalize to standard nomenclature, and anchor 15-day clock timestamp

**Current Actor**: Case processing specialist  
**Current Time**: 40-45 min per case (intake 5-10 min + extraction 35 min = 53-60% of 75-min baseline per [A1])

**Proposed Actor**: Intake & Extraction Agent (ADR-1)  
**Proposed Time**: 5-10 min agent processing + 5 min HITL validation for ~12% of cases

## Delegation Suitability Scoring (ADR-1)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input Structure** | **Mixed (Medium)** | Structured inputs (JSON webforms, clinical trial site reports): High. Semi-structured (HCP text reports with field labels): Medium. Unstructured (patient narratives, phone transcripts, social media posts): Low. Per [A2], 30% HCP text, 25% patient (JSON + VTT), 20% social media (JSON), 15% trial sites (text), 10% literature (text). |
| **Decision Determinism** | **Mixed (Medium)** | Format classification: High (file extension, MIME type). Duplicate detection: High (hash comparison, fuzzy matching). Explicit field extraction (patient age, sex, drug name): High. Drug nomenclature normalization: High (RxNorm API). AE term MedDRA coding: High. Temporal relationship parsing: Low ("a few weeks ago" requires date estimation). AE narrative extraction: Medium (medical terminology translation). |
| **Tool Coverage** | **High** | Email parsing, web form API (JSON), phone transcript VTT parser, social media JSON parser all standard. Text parsing pipeline buildable with Claude Code + LLM per [A8]. RxNorm API, WHO Drug Dictionary API, MedDRA API available. PV case management system write API available [A16]. |
| **Context Complexity** | **Low** | No institutional knowledge required. Duplicate detection uses explicit data fields. Product-specific context (indication, dosing) available via product information API. |
| **Exception Rate** | **Medium** | Mis-routed complaints (~5%), insufficient minimum info (~10%), missing required fields (~20%), ambiguous temporal relationships (~30% of unstructured formats), concomitant med under-reporting (~40%). Predictable handling: exception queue, HITL validation, reporter follow-up. |
| **Latency Constraint** | **Low** | Batch processing acceptable. 1-2 hour intake latency acceptable (not sub-second). |
| **Risk/Compliance** | **High** | Incorrect patient demographics, suspect drug identification, or AE term extraction creates downstream classification errors and 15-day reporting risk. Incorrect timestamp anchoring creates compliance risk. Incomplete extraction triggers reporter follow-up delays. Per FDA 21 CFR 314.80, extraction errors that delay reportability determination create compliance risk. |

**Suitability Assessment**: **5/7 High or Medium, 1 Low (Latency), 1 High-Risk** — Fully Agentic with confidence-based HITL

## Delegation Archetype Assignment (ADR-1)

**Fully Agentic with Confidence-Based HITL**

**Rationale**: Format classification, duplicate detection, and scope routing are deterministic. Structured field extraction with per-field confidence scoring achieves high accuracy for most cases. Unstructured narrative extraction is less deterministic but achievable with LLM + prompt engineering. High compliance risk requires HITL validation when confidence is low. High volume (6,000 cases/year) justifies full automation with safety guardrail.

**Human Oversight Model**:
- **Confidence Threshold**: Any required field confidence < 0.85 → route to case processor HITL validation queue [A15]
- **Optional Field Threshold**: Optional field confidence < 0.70 → flag as "needs follow-up" but do not block processing
- **Exception Handling**: Mis-routed complaints → exception queue. Insufficient minimum info → reporter follow-up queue. Ambiguous duplicates (fuzzy match confidence 0.5-0.8) → manual review.
- **Audit**: Spot-check 5% of intake+extraction decisions weekly for quality assurance

**Expected HITL Rate**: ~12% of cases require HITL validation per [A2] format distribution and [A8] text parsing assumptions [A15]

## Trade-offs (ADR-1)

**Benefits**:
- Eliminates queue delay component of 15-day compliance failures (50% of failures per [A7])
- Eliminates 40-45 min per case intake+extraction time for 88% of cases (high-confidence auto-processing)
- Standardizes format classification, duplicate detection, nomenclature normalization
- Generates span-level citations for audit trail (compliance requirement per [A10])
- Enables parallel processing of multiple reports (removes sequential bottleneck)

**Risks**:
- False-negative confidence scores: low-quality extraction flagged as high-confidence → downstream classification errors → 15-day reporting risk
- False-positive duplicate detection: unique case flagged as duplicate → requires manual override
- Patient identifier de-identification errors in social media extracts → GDPR/HIPAA violation risk
- Temporal relationship estimation errors → causality assessment errors

**Mitigation**:
- Calibrate confidence thresholds on validation set with case processor labels before deployment
- Red-team patient identifier extraction on social media cases with privacy officer review
- Temporal relationship extraction: flag "estimated date" in audit trail when ambiguous + request follow-up
- Duplicate detection: confidence < 0.8 → flag for manual review
- Exception queue monitoring: alert if exception rate >15% over 24 hours
- Weekly feedback loop: case processors annotate HITL corrections → model refinement

**Anti-pattern Check**: This is **not** a static rules or RPA task. AE narrative extraction from unstructured text ("dizzy and vision went blurry" → structured fields "dizziness" + "blurred vision" with MedDRA codes) requires LLM reasoning, not regex alone. Agent is justified.

---

# ADR-2: Medical Triage — Seriousness, Expectedness, and Reportability

## Cognitive Work Summary (ADR-2)

**Trigger**: Structured AE data extraction complete (ADR-1 output: `AECasePackage` with `extraction_status == AUTO_COMPLETE`)

**Goal**: Classify seriousness per ICH E2A criteria, assess expectedness against product RSI, recommend reportability per FDA 21 CFR 314.80 and multi-jurisdictional rules, and generate defensible audit trail with CoT reasoning for FDA inspection

**Current Actor**: Medical safety officer  
**Current Time**: 30-35 min per case (seriousness 15 min + expectedness 10 min + reportability 10 min + audit trail 5 min = 40-47% of 75-min baseline per [A1])

**Proposed Actor**: Medical Triage Agent (ADR-2)  
**Proposed Time**: 10-15 min agent processing → outputs `TriageRecommendation` for MSO review

## Delegation Suitability Scoring (ADR-2)

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Input Structure** | **High** | Structured `AECasePackage` from ADR-1 with normalized patient demographics, drug names, MedDRA-coded AE terms, temporal relationships, concomitant meds. ICH E2A criteria are codified. Product RSI/CCSI are structured or semi-structured markdown per mock data. MedDRA hierarchy API queryable. |
| **Decision Determinism** | **Mixed (Medium)** | **Seriousness**: Explicit criteria (death, hospitalization, congenital anomaly) are High. Judgment-dependent criteria ("life-threatening," "other medically important") are Low to Medium. **Expectedness**: Exact term matching is High. Synonym/broader/narrower term relationships via MedDRA hierarchy are Medium (requires reasoning). **Reportability**: FDA 21 CFR 314.80 logic (serious + unexpected → 15-day) is High. Multi-jurisdictional variance (EMA, MHRA, PMDA) is Medium. Causality assessment influence is Low (judgment-dependent). |
| **Tool Coverage** | **High** | ICH E2A criteria codifiable in system prompt. Product RSI/CCSI readable from mock-data/product-information/ (Solivian_RSI.md, Tezarimab_RSI.md, Phaedora_RSI.md). MedDRA hierarchy API available or buildable. Reportability rules engine codifiable (FDA, EMA, MHRA, PMDA regulations). Audit trail store writable (span-level citations, CoT reasoning, timestamps). |
| **Context Complexity** | **Low to Medium** | Product-specific RSI variance (Solivian vs. Tezarimab vs. Phaedora safety profiles) is explicit in product information. No institutional knowledge required beyond what's documented. Causality assessment (if available from prior case review) is explicit data. |
| **Exception Rate** | **Medium** | "Other medically important" criterion requires medical judgment (~10% of cases per [A12]). Novel AE terms not in RSI (~15-20% per industry norms, flagged as "unexpected"). MedDRA hierarchy term specificity variance (rash vs. Stevens-Johnson syndrome) requires clinical interpretation (~20-30% of expectedness assessments per [A13]). Multi-jurisdictional reportability complexity (~25% of cases per [A14]). |
| **Latency Constraint** | **Low** | Batch processing acceptable. No real-time requirement. MSO reviews asynchronously. |
| **Risk/Compliance** | **High** | Incorrect seriousness classification creates 15-day reporting risk (serious-unexpected case missed). Incorrect expectedness assessment creates 15-day reporting risk (unexpected case flagged as expected). Incorrect reportability recommendation creates FDA compliance risk (late filing per 21 CFR 314.80). Per Dr. Mansour (external auditor): "Every reportability call needs to be defensible to an FDA inspector with the underlying evidence on demand" [A10]. |

**Suitability Assessment**: **5/7 High or Medium, 1 Low (Latency acceptable), 1 High-Risk** — Agent-led with MSO sign-off

## Delegation Archetype Assignment (ADR-2)

**Agent-led + MSO Sign-Off**

**Rationale**: ICH E2A criteria, MedDRA hierarchy matching, and FDA reportability rules are explicitly codifiable. Agent can apply rules systematically with CoT reasoning and span-level citations. However, judgment-dependent criteria ("other medically important," term specificity variance, causality influence) require medical interpretation. High compliance risk requires MSO final sign-off. Per CMO mandate (Dr. Carmichael): "We are not asking AI to make the reportability decision. That's our medical safety officer's call."

**Human Oversight Model**:
- **MSO Reviews All Recommendations**: Agent outputs `TriageRecommendation` (seriousness classification, expectedness signal, reportability recommendation, CoT reasoning, span-level citations). MSO reviews all 6,000 cases annually but accepts 88% as-is, revises 12% for edge cases per [A9].
- **Confidence Signaling**: Agent flags low-confidence cases (ambiguous seriousness, novel AE term, multi-jurisdictional complexity) for MSO deep review (estimated ~10-15% of cases).
- **Override Authority**: MSO can override any agent classification with clinical judgment. Override is logged in audit trail with MSO reasoning.
- **Audit**: Medical safety officer spot-checks 5% of agent recommendations monthly for systematic error patterns.

**Expected MSO Effort**: 15 min per case for review + sign-off (6,000 cases × 15 min = 1,500 hours annually, down from 7,500 hours baseline). Deep review cases (~10-15%) require 25-30 min MSO effort.

## Trade-offs (ADR-2)

**Benefits**:
- Eliminates 30-35 min per case medical synthesis work (seriousness classification, expectedness assessment, reportability recommendation, audit trail generation)
- Standardizes ICH E2A classification logic across all cases (reduces MSO-to-MSO variance)
- Automates MedDRA hierarchy term matching (reduces manual lookup time)
- Generates machine-readable audit trail with span-level citations and CoT reasoning for FDA inspection (0% automated today → 100% [A10])
- Enables MSO to focus 15 min per case on medical judgment and sign-off (high-value work) instead of 60 min on data extraction and classification lookup (low-value work)

**Risks**:
- Overconfidence on "other medically important" criterion: agent classifies ambiguous case as serious → over-reporting (safer than under-reporting per [A4])
- Underconfidence on "other medically important" criterion: agent classifies serious case as non-serious → 15-day reporting miss (critical compliance failure)
- MedDRA hierarchy term matching errors: agent flags expected AE as unexpected → over-reporting (safer) or flags unexpected AE as expected → 15-day reporting miss (critical)
- Multi-jurisdictional reportability errors: agent recommends FDA-only reporting, misses EMA/MHRA/PMDA requirement → global compliance failure
- Causality assessment influence: agent recommends "not reportable" based on "unrelated" causality, but FDA still requires expedited reporting → compliance failure

**Mitigation**:
- Conservative fallback: when ambiguous, always classify as serious + unexpected → over-report (per [A4] precision target 85-88%, allowing 12-15% false positives)
- Novel AE term guardrail: if AE term not found in RSI and not found in MedDRA hierarchy → flag as "unexpected" with confidence 0.0 → MSO deep review
- Multi-jurisdictional reportability: codify all global requirements (FDA, EMA, MHRA, PMDA) in system prompt → agent outputs reportability per jurisdiction
- Causality influence: agent includes causality assessment in reportability reasoning but always recommends expedited reporting for serious-unexpected regardless of causality (per FDA guidance)
- MSO spot-check: 5% monthly sample of agent recommendations → identify systematic error patterns → refine system prompt

**Anti-pattern Check**: This is **not** a simple lookup or rules engine. MedDRA hierarchy reasoning ("Is Stevens-Johnson syndrome a type of rash, or a distinct unexpected AE?") requires semantic understanding. Causality assessment reasoning ("Does 'unrelated' causality exempt from expedited reporting?") requires regulatory interpretation. Agent with CoT reasoning is justified.

---

**Document Owner**: FDE Engagement Lead  
**Architecture Decision**: Two-agent architecture (collapsed from 5 original delegation candidates) to reduce implementation complexity for prototype build within 8-hour exam scope.  
**Next Review**: After prototype build (validate time reduction [A6], HITL rate [A15], MSO acceptance rate [A9] with mock data test cases).
