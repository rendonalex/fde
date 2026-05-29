# Agentic Solution Architecture
## Delegation Qualification — Greenfield Health Systems AI Claims Processing

**Project:** Greenfield Health Systems — AI Claims Processing Transformation  
**Prepared by:** FDE Engagement Lead  
**Date:** 2026-05-20  
**Input:** `specs/cognitive-load-map.md` (Phase 2 output)  
**Status:** Active — delegation decisions contingent on Phase 1 validation gates

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Delegation Qualification Framework](#2-delegation-qualification-framework)
3. [Delegation Suitability Matrix](#3-delegation-suitability-matrix)
4. [Assumptions Referenced](#4-assumptions-referenced)

**Architecture Decision Records** (per-ADR suitability analysis, trade-offs, and dependencies): [`specs/05-adrs.md`](05-adrs.md)

---

## 1. Executive Summary

Six of nine architecture decisions support agentic delegation in some form. Two warrant full delegation (**ADR-3**, **ADR-8**); three are strong candidates for agent-led execution with human oversight (**ADR-1**, **ADR-2**, **ADR-5**); one is a new high-value agent capability (**ADR-6**); one is human-only by CMO mandate (**ADR-7**); and one requires agent support with human judgment retained (**ADR-9**).

The single most consequential delegation decision is **ADR-4 (Clinical Content Triage)**. On raw suitability scores, this task would be rated Human Only — the input is unstructured, the criteria are undocumented [A15], and a misclassification carries patient safety consequences [A6]. Yet the entire dual-path financial case depends on delegating it. The resolution is not to skip the analysis but to honor it: delegation of ADR-4 is conditional on passing the Phase 1 false-negative gate, and the current state is Human Only until that gate is cleared.

Two anti-pattern checks modify the apparent scope: **ADR-3** coding validation is primarily a rules lookup, not an LLM problem — the recommendation is a rules engine for deterministic checks with an agent for plausibility edge cases only. **ADR-8** payment calculation is arithmetic — the agent should trigger the existing payment engine, not replicate it.

The binding dependencies across the full architecture are [A12] (CMS API availability), [A15] (clinical criteria definition), [A11] (legal permissibility of AI denials), and [A18] (coverage rules engine format). All four must be resolved before Phase 2 specifications are finalized.

---

## 2. Delegation Qualification Framework

Phase 3 of the ATX Assessment evaluates each JtD (referred to here as an Architecture Decision Record, ADR) against seven suitability dimensions. **H = high delegation suitability; L = low delegation suitability.**

| Dimension | H — favors agent | L — favors human |
|-----------|-----------------|-----------------|
| **Input Structure** | Structured, machine-readable | Unstructured, ambiguous, requires interpretation |
| **Decision Determinism** | Clear rules, predictable outputs | Judgment-dependent, contextual |
| **Tool Coverage** | APIs available or buildable | Systems inaccessible, black-box, or manual |
| **Context Complexity** | State can be made explicit | Requires institutional knowledge or relationships |
| **Exception Rate** | Rare, predictable exceptions | Frequent, unpredictable edge cases |
| **Latency Constraint** | Batch or async acceptable | Real-time, sub-second required |
| **Risk/Compliance** | Reversible, low consequence | Irreversible, regulated, high-consequence |

Archetype thresholds (from Phase 3 guidance):
- **Human Only**: ≥3 dimensions at L, especially Risk/Compliance and Decision Determinism
- **Human-led + Automation Support**: deterministic sub-tasks automated; judgment stays human
- **Human-led + Agent Support**: agent synthesizes and recommends; human decides
- **Agent-led + Human Oversight**: agent acts; human reviews or approves high-stakes outputs
- **Fully Agentic**: all dimensions M or H; volume justifies full delegation

**Anti-pattern check**: If a task can be solved with static rules, RPA, or a simple script — do not build an agent. Agents are for non-determinism, not for engineering overhead.

---

## 3. Delegation Suitability Matrix

Scoring: **H** = high suitability for delegation · **M** = medium · **L** = low  
Archetype column reflects planned target state; conditions noted where current state differs.

| ADR | Description | Input Struct | Decision Determ | Tool Coverage | Context Complexity | Exception Rate | Latency | Risk / Compliance | **Archetype** |
|-----|-------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---------|
| ADR-1 | Claim Intake & Format Validation | M | H | M | H | M | H | H | **Agent-led + Human Oversight** ¶ |
| ADR-2 | Eligibility Verification | M | H | L | M | M | H | H | **Agent-led + Human Oversight** † |
| ADR-3 | Coding & Compliance Validation | H | H | H | M | M | H | M | **Fully Agentic** ‡ |
| ADR-4 | Clinical Content Triage | L | L | L | L | L | H | L | **Agent-led + Human Oversight** § |
| ADR-5 | Fast Path Adjudication | H | H | M | H | M | H | M | **Agent-led + Human Oversight** |
| ADR-6 | Clinical Pre-Screening & Summary | L | M | M | M | M | H | M | **Agent-led + Human Oversight** |
| ADR-7 | Physician Clinical Review | M | L | M | L | L | H | L | **Human Only** |
| ADR-8 | Payment & EOB Generation | H | H | H | H | H | H | M | **Fully Agentic** ‡ |
| ADR-9 | Denial Communication & Appeals | M | L | M | M | L | M | L | **Human-led + Agent Support** |

**Notes:**  
¶ Input Structure spans 10 distinct intake channels: EDI 837P/I (deterministic — fully agentic within ADR-1), FHIR R4 (dedicated parser; confidence-based routing — required fields member_id, member_name, and prior_auth_required typically absent → HUMAN_REQUIRED in practice; member_dob, plan_id, billing_provider_tax_id deferred to ADR-2), portal JSON (field mapping required; confidence-based routing — required fields typically high-confidence → AUTO_COMPLETE achievable; plan_id deferred to ADR-2), CMS-1500 PDF and pre-OCR'd text (IDP pipeline; confidence-scored extraction), email (IDP NLP; confidence-based routing — payer_id/plan_id deferred to ADR-2; HUMAN_REQUIRED only if required fields fall below 0.85 threshold), fax PDF (IDP OCR; moderate confidence; high HUMAN_REQUIRED rate), fax-as-email (IDP NLP; confidence-based routing — payer_id/plan_id/provider fields deferred to ADR-2 and ADR-2+; HUMAN_REQUIRED only if required fields below threshold), exception notes (annotation routing only — not new claim submissions). See `specs/06a-capability-spec-intake.md` §8 for channel-specific parser contracts.  
† Conditional on [A12] API availability. If no unified eligibility API exists, drops to Human-led + Automation Support for system-lookup steps.  
‡ Anti-pattern applies: prefer rules engine (ADR-3) and existing payment engine integration (ADR-8) over LLM agent for deterministic sub-tasks.  
§ Current state = **Human Only** until Phase 1 [A6] false-negative gate (<2%) is passed. Target state = Agent-led + Human Oversight conditional on gate clearance.

---

## 4. Assumptions Referenced

Assumptions referenced in this document (Executive Summary and Suitability Matrix). Full per-ADR assumption dependencies are in [`specs/05-adrs.md`](05-adrs.md). Full assumption definitions are in [`specs/assumptions.md`](assumptions.md).

| ID | Description | Confidence | Relevant Section |
|----|-------------|:----------:|-----------------|
| A6 | <2% clinical flagging false-negative achievable | Medium (60%) | §1 Executive Summary — ADR-4 gate condition |
| A11 | AI Fast Path denials legally permissible | Low (45%) | §1 Executive Summary; §3 Matrix note |
| A12 | CMS has usable API for integration | Low (40%) | §1 Executive Summary; §3 Matrix note |
| A15 | Clinical flagging criteria are informal/undocumented | Medium (60%) | §1 Executive Summary — ADR-4 blocking dependency |
| **A18** | Coverage rules exist in machine-readable form | Low (45%) | §1 Executive Summary — binding dependency |
