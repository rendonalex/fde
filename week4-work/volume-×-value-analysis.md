# Volume × Value Analysis — Westbridge Family Medicine Patient Intake

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Step 1: Suitability Gating](#step-1-suitability-gating)
3. [Step 2: Volume × Value Scoring](#step-2-volume--value-scoring)
4. [Step 3: Total Cost of Ownership Assessment](#step-3-total-cost-of-ownership-assessment)
5. [Step 4: Feasibility Scoring Matrix](#step-4-feasibility-scoring-matrix)
6. [Step 5: Strategic Sequencing Validation](#step-5-strategic-sequencing-validation)
7. [Prioritised Candidate Shortlist](#prioritised-candidate-shortlist)
8. [Implementation Sequencing Logic](#implementation-sequencing-logic)

---

## Executive Summary

This document applies Phase 4 Candidate Prioritisation to the four Westbridge patient-intake workstreams following Phase 3 Delegation Qualification. Each workstream is scored for suitability, volume-value position, economics, and feasibility, then sequenced into an implementation roadmap.

**Top-line findings:**

- **WS4 (Medication Reconciliation)** is the highest-ROI Wave 1 anchor: 4.6-month payback, ~$92K/year saving, full API coverage, no prerequisites beyond a HIPAA BAA [A015, A020]. The integrations it builds (athenahealth read/write, DoseSpot) compound value across all subsequent waves.
- **WS2 (Prior Authorization)** has the highest per-case non-determinism and the most visible failure mode. Tasks 2.2 and 2.8 are immediately deployable and eliminate the check-in blind spot documented in Artefact 5.2. Full WS2 automation is Wave 3 and gates on insurer knowledge codification [A019].
- **WS1 (Insurance Verification)** is RPA-eligible on the standard path — low non-determinism, high volume, strong economics ($56K/year, 5.9-month payback). Placed in Wave 2 where it reuses the athenahealth integration from WS4 and adds Availity as a second shared platform asset.
- **WS3 (Questionnaire & Triage)** has the highest raw value score (16) but the tightest constraint ceiling: HC1 and HC2 permanently cap agent scope to collection, routing, and documentation. Placed in Wave 3 after the paper-path decision [A006] is made and a HITL-compliant review UI is designed.

**Pre-condition before Wave 1 builds begin:** HIPAA BAA executed with athenahealth and DoseSpot [A015, A020]. Knowledge codification project with Dana [A019] must begin in parallel with Wave 1 technical work to avoid Wave 3 delays.

---

## Step 1: Suitability Gating

Pass criteria: at least Medium suitability on Input Structure, Decision Determinism, and Tool Coverage; no hard compliance blocks.

| Workstream | Input Structure | Decision Determinism | Tool Coverage | Compliance Risk | Gate Result |
|-----------|:-:|:-:|:-:|:-:|:---|
| WS1 — Insurance Verification | H | H (standard path); L (exception) | H [A013] | M (PHI; BAA required [A020]) | **Pass** — exception path stays Human Only |
| WS2 — Prior Authorization | M | L (2.4, 2.6 tacit); H (2.2, 2.8) | M (portal/fax hybrid [A017, A021]) | M (PHI; BAA required) | **Conditional** — data-state tasks (2.2, 2.8) pass immediately; tacit-knowledge tasks (2.4, 2.6) blocked until A019 |
| WS3 — Pre-visit Questionnaire & Triage | M | L (3.4, 3.5 triage); H (routing, doc) | M (paper path gap [A006]) | H (HC1/HC2 clinical boundary [A009]) | **Conditional** — collection and documentation tasks pass; 3.4 and 3.5 are permanently Human Only |
| WS4 — Medication Reconciliation | H (structured lists); L (OTC gap [A005]) | H (comparison); L (gap detection) | H [A013] | M (PHI; physician reviews all flags) | **Pass** — OTC gap detection (4.5) stays Human-led + Agent Support |

**Anti-pattern flag (from Phase 3):** Tasks 1.1–1.3 (WS1 retrieval), 2.2 (WS2 PA status check), 4.1–4.2 (WS4 data pulls), and 3.2 (questionnaire chase reminders) are deterministic lookups — scripted pipelines or RPA are sufficient. Agents are warranted for interpretation, synthesis, and exception-routing steps only.

---

## Step 2: Volume × Value Scoring

### Score Table

| Workstream | Volume Score (1–5) | Non-Determinism Score (1–5) | Agentic Value Score | Interpretation |
|-----------|:-:|:-:|:-:|:---|
| WS1 — Insurance Verification | **4** (180/day) | **2** (mostly deterministic — API lookups + rule application) | **8** | Consider agentic; anti-pattern risk on standard path — RPA-eligible |
| WS2 — Prior Authorization | **3** (25/day) | **4** (insurer SLA patterns, denial interpretation, contextual chase timing [A008, A011]) | **12** | Strong agentic candidate for reasoning-intensive tasks; lower volume limits position |
| WS3 — Pre-visit Questionnaire & Triage | **4** (180/day) | **4** (clinical synthesis, urgency judgment, free-text parsing [A009, A018]) | **16** | Primary agentic target by raw score; effective agent scope constrained to collection and documentation by HC1/HC2 |
| WS4 — Medication Reconciliation | **4** (180/day) | **3** (comparison is rule-based; synthesis and exception handling require reasoning [A005]) | **12** | Strong agentic candidate; best economics in portfolio |

Score ≥ 15 → Strong agentic candidate. Score 8–14 → Consider agentic, validate TCO. Score < 8 → Rule-based automation.

### Volume × Value Quadrant

| | **Low Non-Determinism** | **High Non-Determinism** |
|---|---|---|
| **High Volume** | **WS1** Insurance Verification (8)<br/>180/day, mostly deterministic<br/>RPA-eligible | **WS3** Questionnaire & Triage (16) ⭐<br/>180/day, high reasoning<br/>HC1/HC2 scope constraint<br/><br/>**WS4** Medication Reconciliation (12)<br/>180/day, mixed logic<br/>Best economics in portfolio |
| **Low Volume** | *(No candidates)* | **WS2** Prior Authorization (12)<br/>25/day, high reasoning<br/>Insurer patterns, knowledge codification |

**Quadrant notes:**

- **WS3** lands top-right (Primary Agentic Target) on the raw JtD score — the full triage task demands high reasoning. HC1/HC2 cap what the agent may actually do; the quadrant position reflects cognitive demand, not agent authority.
- **WS4** lands at the top-centre, straddling the boundary between RPA and Agentic — correctly reflecting a workstream where retrieval steps are RPA-eligible and comparison/flagging warrants agent reasoning.
- **WS1** lands top-left (RPA/Rules) — confirms that the standard path should be a scripted pipeline; agent overhead is justified only for the interpretation step (1.4) and exception routing.
- **WS2** lands right-centre at the volume midpoint — lower volume constrains position, but the per-case reasoning intensity makes it the most cognitively valuable target per case in the portfolio.

---

## Step 3: Total Cost of Ownership Assessment

**Shared assumptions:** Fully loaded front-desk staff hourly cost = $40/hour [A022]; 250 operating days/year [A023]; token pricing — Claude Sonnet 4.6 (~$3/M input, ~$15/M output).

---

### WS1 — Insurance Verification

| Item | Value |
|------|-------|
| Agent scope | Tasks 1.1–1.4, 1.7 (schedule pull, staleness check, eligibility query, interpretation, EHR write) |
| Time saved per case | ~2 min/case (across all 180/day; human retains ~1 min review for standard path) |
| Annual cases (agent scope) | 45,000 [A023] |
| **Annual baseline cost (agent scope)** | 45,000 × (2/60) × $40 = **$60,000** |
| Token cost per case | ~600 input + 200 output → $0.005 |
| Tool call cost per case | ~2 API calls → $0.010 |
| HITL rate / cost | 10% × 1 min × $40/60 = $0.067 |
| **Agent cost per case** | **~$0.08** |
| **Annual agent cost** | 45,000 × $0.08 = **$3,600** |
| **Annual saving** | **$56,400** |
| Build cost (est.) | $27,500 (athenahealth + Availity integration + staleness rule; ~70 dev-hours) |
| **Payback period** | **5.9 months** |
| Year 1 ROI | 105% |
| 3-year ROI | 515% |

Tasks 1.1–1.3 are RPA-eligible; full agent architecture not justified for retrieval alone. Recommended: scripted pipeline for 1.1–1.3; lightweight agent for 1.4 (interpretation) and exception-routing path.

---

### WS2 — Prior Authorization (Wave 1 scope: tasks 2.2 and 2.8)

| Item | Value |
|------|-------|
| Agent scope (Wave 1) | Task 2.2 (PA status check) + Task 2.8 (check-in gate alert) |
| Time saved per case (Wave 1) | ~4 min/case (PA status lookup + automated check-in alert) |
| Annual PA cases | 6,250 [A023] |
| **Annual baseline cost (agent scope)** | 6,250 × (4/60) × $40 = **$16,667** |
| Avoided-miss value | ~12 visit cancellations/year × $250 avg cost = $3,000 [A010, A024] |
| Token cost per case | ~400 input + 100 output → $0.003 |
| Tool call cost per case | ~$0.005 |
| HITL rate / cost | 20% × 2 min × $40/60 = $0.27 |
| **Agent cost per case** | **~$0.28** |
| **Annual agent cost** | 6,250 × $0.28 = **$1,750** |
| **Annual saving (Wave 1)** | ($16,667 + $3,000) − $1,750 = **$17,917** |
| Build cost (est.) | $20,000 standalone; **~$12,000 if built after WS4** (shared athenahealth integration) |
| **Payback period** | 13.4 mo standalone / **8 months with shared integration** |
| Year 1 ROI | ~50% (with shared integration) |
| Full scope (Wave 3, after A019) | ~$37,500 baseline; ~$28,000+ additional annual saving; incremental build ~$30,000 |

Task 2.2 (PA status query) is a deterministic lookup — a scheduled script is sufficient. Task 2.8 (check-in gate) is the primary value driver; it is the automation target that directly prevents the failure documented in Artefact 5.2.

---

### WS3 — Pre-visit Questionnaire & Triage (agent scope: tasks 3.1, 3.2, 3.3, 3.6 — portal patients only)

| Item | Value |
|------|-------|
| Agent scope | Tasks 3.1 (routing), 3.2 (chase reminders), 3.3 (NLP visit-reason parse), 3.6 (documentation) |
| Applicable patients | ~80% portal × 180/day ≈ 144 portal patients/day [A006] |
| Time saved per case | ~2 min/case (routing automation + reminders + parse + doc) |
| Annual cases (agent scope) | 36,000 [A023] |
| **Annual baseline cost (agent scope)** | 36,000 × (2/60) × $40 = **$48,000** |
| Token cost per case | ~800 input + 300 output → $0.009 |
| Tool call cost per case | ~$0.008 |
| HITL rate / cost | 25% × 2 min × $40/60 = $0.33 |
| **Agent cost per case** | **~$0.35** |
| **Annual agent cost** | 36,000 × $0.35 = **$12,600** |
| **Annual saving** | **$35,400** |
| Build cost (est.) | $35,000 (questionnaire routing + NLP parse model + reminder system + doc automation) |
| **Payback period** | **11.9 months** |
| Year 1 ROI | ~1% (marginal) |
| 3-year ROI | 203% |

Year 1 ROI is marginal; 3-year economics are strong. WS3 is excluded from Wave 1–2 due to prerequisite decisions (paper-path handling [A006]) and the compliance boundary (HC1/HC2 require a robust human-review UI before any deployment).

---

### WS4 — Medication Reconciliation (agent scope: tasks 4.1–4.4, 4.6, 4.7)

| Item | Value |
|------|-------|
| Agent scope | Tasks 4.1–4.4, 4.6, 4.7 (full pipeline except OTC gap detection) |
| Time saved per case | ~4 min/case (of 6 min total; ~2 min remains for human review of 4.5 and physician exceptions) |
| Annual cases | 45,000 [A023] |
| **Annual baseline cost (agent scope)** | 45,000 × (4/60) × $40 = **$120,000** |
| Token cost per case | ~1,200 input + 400 output → $0.0096 |
| Tool call cost per case | ~3 API calls → $0.015 |
| HITL rate / cost | 30% × 3 min × $40/60 = $0.60 |
| **Agent cost per case** | **~$0.62** |
| **Annual agent cost** | 45,000 × $0.62 = **$27,900** |
| **Annual saving** | **$92,100** |
| Build cost (est.) | $35,000 (DoseSpot + athenahealth read/write + comparison + flagging pipeline) |
| **Payback period** | **4.6 months** |
| Year 1 ROI | 163% |
| 3-year ROI | 690% |

WS4 has the strongest economics in the portfolio. The athenahealth and DoseSpot integrations built here are foundational platform assets reused by WS1 (athenahealth) and WS2 (athenahealth). This is the primary reason WS4 anchors Wave 1.

---

## Step 4: Feasibility Scoring Matrix

Scale: 1 = lowest feasibility / 5 = highest.

| Factor | WS1 | WS2 | WS3 | WS4 |
|--------|:---:|:---:|:---:|:---:|
| **Data availability** | 4 — APIs confirmed [A013]; staleness policy [A004] must be defined first | 3 — PA status queryable; insurer patterns unstructured [A019] | 3 — portal data ready; paper path [A006] unresolved; free-text NLP needs validation | 4 — DoseSpot + athenahealth APIs confirmed [A013]; OTC gap is known and bounded [A005] |
| **System integration feasibility** | 5 — athenahealth + Availity both REST, standard [A013] | 3 — athenahealth confirmed; fax/portal hybrid [A017, A021] is partial | 3 — athenahealth API for doc; questionnaire routing feasible; paper path is manual | 5 — DoseSpot + athenahealth both REST API-native, already integrated [A013] |
| **Compliance risk** | 3 — PHI in EHR write [A020]; read-heavy scope; BAA required | 3 — PHI; BAA required; Wave 1 tasks are read-only | 2 — HC1/HC2 create permanent compliance boundary; NLP mis-classification is clinical liability [A009] | 3 — PHI; physician reviews all flags; agent action bounded to comparison and flagging |
| **Context stability** | 4 — insurance rules and Availity format change slowly | 3 — insurer SLAs change; knowledge base [A019] requires ongoing maintenance | 3 — visit-reason vocabulary stable; clinical edge cases evolve; paper path static | 4 — medication list schema stable; drug database updates handled by DoseSpot |
| **Organisational readiness** | 4 — Dana's team motivated by billing errors [A004]; problem documented in Artefact 5.3 | 5 — physician documented the miss; exec attention high; Dana's ownership strong | 3 — HC1/HC2 constrain agent scope; paper-path requires policy decision; HITL design needs sign-off | 4 — known pain point; no clinical judgment risk in comparison and flagging steps |
| **TCO viability** | 5 — $56K/year; 5.9-month payback; 105% Year 1 ROI | 3 — Wave 1: 8-month payback (shared integration); full scope ROI dependent on A019 timeline | 4 — 11.9-month payback; marginal Year 1; strong 3-year economics | 5 — $92K/year; 4.6-month payback; 163% Year 1 ROI; best economics in portfolio |
| **Total (/30)** | **25** | **20** | **18** | **25** |

WS4 and WS1 tie at 25/30 — both technically ready and economically strong. WS4 anchors Wave 1 due to higher absolute saving and foundational integration value. WS1 follows in Wave 2, inheriting the athenahealth integration at marginal incremental cost. WS2 scores 20 — limited by the knowledge prerequisite [A019] and portal API uncertainty [A021]. WS3 scores 18 — the compliance boundary is the binding constraint, not the economics.

---

## Step 5: Strategic Sequencing Validation

| Sequencing Criterion | WS4 (Wave 1) | WS2 partial (Wave 1) | WS1 (Wave 2) | WS2 full + WS3 (Wave 3) |
|---------------------|:---:|:---:|:---:|:---|
| Self-financing ROI | ✓ 163% Year 1 | ✓ ~50% with shared integration | ✓ 105% Year 1 | Funded by Wave 1+2 combined earning |
| Integration reusability | ✓ athenahealth + DoseSpot → reused by all waves | ✓ reuses WS4's athenahealth client | ✓ adds Availity → reused by WS3 | Inherits all prior integrations |
| Low compliance risk | ✓ bounded agent; physician reviews all flags | ✓ read-only Wave 1 scope | ✓ rule-based standard path | Conditional — WS3 requires HITL design sign-off |
| Data readiness | ✓ APIs confirmed; need BAA + staleness rule [A004] | ✓ PA status queryable now | ✓ APIs confirmed; need staleness policy [A004] | Gated — WS2 needs A019; WS3 needs paper-path decision [A006] |
| Organisational readiness | ✓ known pain; motivated team | ✓ highest exec visibility | ✓ problem documented; billing impact clear | Moderate — WS2 needs knowledge elicitation; WS3 needs policy decisions |
| Strategic visibility | ✓ daily impact; physician receives prepared discrepancy report | ✓ eliminates visible failure (Artefact 5.2) | ✓ prevents billing errors (Artefact 5.3) | ✓ completes the intake automation picture |

**Validation summary:** Wave 1 passes all 6 criteria. Wave 2 inherits Wave 1 integration assets, reducing marginal build cost from ~$27,500 to ~$15,000. Wave 3 prerequisites (A019 knowledge codification, paper-path decision) must be initiated in Month 0 — these are non-technical tracks with their own lead times that cannot be compressed by technical effort.

---

## Prioritised Candidate Shortlist

| Rank | Workstream | Value Score | Feasibility | Wave | Annual Saving | Payback | Key Dependency |
|:----:|-----------|:-----------:|:-----------:|:----:|:------------:|:-------:|:---------------|
| 1 | **WS4 — Medication Reconciliation** | 12 | 25/30 | **Wave 1** | $92,100 | 4.6 mo | BAA executed [A015, A020] |
| 2 | **WS2 — Prior Authorization (2.2, 2.8 only)** | 12 | 20/30 | **Wave 1** | $17,917 | 8 mo | BAA; uses WS4 athenahealth integration |
| 3 | **WS1 — Insurance Verification** | 8 | 25/30 | **Wave 2** | $56,400 | 5.9 mo | Staleness policy [A004]; Availity integration |
| 4 | **WS3 — Questionnaire & Triage** | 16 | 18/30 | **Wave 3** | $35,400 | 11.9 mo | Paper-path decision [A006]; NLP validation; HC1/HC2 HITL design [A015] |
| 5 | **WS2 — Prior Authorization (full scope)** | 12 | 20/30 | **Wave 3** | +$28,000 incremental | ~21 mo | Insurer knowledge codification [A019]; portal API confirmation [A021] |

**Composite ranking notes:**

- WS4 and WS1 tie on feasibility (25/30); WS4 ranks first due to higher absolute saving ($92K vs $56K) and its role as foundational integration provider for all subsequent waves.
- WS3 scores highest on value (16) but ranks fourth: HC1/HC2 cap effective agent scope, lowering feasibility to 18/30. The raw score overstates automatable value.
- WS2 appears twice: as a Wave 1 partial deployment (immediate ROI from data-state tasks) and a Wave 3 full deployment (after A019 prerequisite is met).

---

## Implementation Sequencing Logic

### Wave 1 — Self-Funding Foundation (Months 0–6)

**Build:** WS4 medication reconciliation pipeline + WS2 check-in gate (tasks 2.2, 2.8)

**Foundational integrations built:**
- athenahealth REST client (read + write, under BAA [A020]) → shared asset for all subsequent waves
- DoseSpot REST client → shared asset for WS4 only; client patterns reusable elsewhere
- PA status query module (reuses athenahealth client) → reused in Wave 2 WS1 verification flow

**Economics:**
- WS4: +$92,100/year from approximately Month 7 onward
- WS2 (2.2, 2.8): +$17,917/year; eliminates visit-cancellation failure mode
- Combined Wave 1 annual saving: ~$110,000
- Combined build cost: ~$47,000 (WS4 $35K + WS2 incremental $12K using shared integration)
- Portfolio payback: ~5.1 months

**Governance prerequisite:** BAA must be executed before any Wave 1 build begins. Initiate BAA negotiation with athenahealth and DoseSpot as Month 0 action.

**Parallel non-technical work (begin Month 0):** Insurer knowledge codification project with Dana [A019] — structured elicitation of 8–12 insurer SLA and denial patterns. This is a facilitated interview process, not a technical dependency; it must start now to be ready for Wave 3 build.

---

### Wave 2 — Compounding (Months 6–12)

**Build:** WS1 insurance verification standard path (tasks 1.1–1.4, 1.7)

**Reuses:** athenahealth integration (from Wave 1)
**Adds:** Availity REST integration — new shared asset for Wave 3 WS3 portal questionnaire routing

**Prerequisites:**
- Staleness refresh policy defined and encoded as a rule [A004] — policy decision must be made by Dana before build, not during
- Availity API credentials and BAA (if Availity requires separate agreement for write-adjacent operations)

**Economics:**
- +$56,400/year incremental
- Marginal build cost: ~$15,000 (Availity integration only; athenahealth already built in Wave 1)
- Wave 1 + Wave 2 combined annual saving: ~$166,400

---

### Wave 3 — AI-Native Operations (Months 12–18)

**Build:** WS2 full scope expansion (tasks 2.3, 2.4, 2.6, 2.7) + WS3 questionnaire pipeline (tasks 3.1–3.3, 3.6)

**Reuses:** athenahealth (Wave 1), Availity (Wave 2)
**Adds:** Dana's insurer knowledge base (structured from A019 elicitation), NLP parse model for free-text visit reason, paper-form exception workflow (if policy resolved [A006])

**Prerequisites — all must be complete before Wave 3 build begins:**
- A019 knowledge codification complete: 8–12 insurer patterns structured, validated with Dana, and stored in a machine-readable knowledge base
- Paper-path handling decision resolved [A006] — either explicitly out-of-scope or a parallel manual workflow defined and documented
- HC1/HC2 HITL design reviewed and signed off by Dana and malpractice counsel [A015] — agent must not surface urgency suggestions even as soft recommendations
- Availity portal API coverage confirmed for top 3 insurers by volume [A021]

**Economics:**
- WS2 expansion: +$28,000/year incremental (after prerequisites met)
- WS3: +$35,400/year
- Full portfolio annual saving after Wave 3: ~$229,800/year
- Wave 3 build cost: ~$65,000 (knowledge base $15K + WS2 expansion $20K + WS3 pipeline $30K)

---

### Permanently Out of Scope

| Task | Reason |
|------|--------|
| 1.6 — Contact patient or insurer to resolve failed verification | Unstructured human communication; no machine interface |
| 2.5 — Chase pending PA via insurer phone | Phone-only; no API; real-time judgment required |
| 3.4 — Classify visit urgency: routine / urgent / same-day | HC1: clinical judgment prohibited [A009] |
| 3.5 — Detect and escalate clinical red flags | HC1 + HC2: clinical judgment + mandatory human escalation path |
| 4.5 — Detect OTC / specialist medication gaps | Data quality ceiling: DoseSpot is structurally incomplete [A005]; no API covers this gap |

---

*All assumption references [A001]–[A024] are documented in `specs/assumptions.md`.*
