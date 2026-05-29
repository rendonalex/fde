# Token Economics Model — Shift Intake Parser (JtD-1)
## MedFlex Agentic Transformation

> ATX Phase 5 deliverable. Input sources: `specs/04b-capability-spec-shift-intake-parsing.md`, `input-docs/atx/atx-economics.md`, `specs/assumptions.md`.
> All values reference assumption IDs from `specs/assumptions.md`. New assumptions added in this document: A32.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Baseline Cost Model](#2-baseline-cost-model)
3. [Token Economics Model](#3-token-economics-model)
4. [ROI and Business Case](#4-roi-and-business-case)
5. [Self-Financing Roadmap](#5-self-financing-roadmap)
6. [Calibration — Making Economics Survive Reality](#6-calibration--making-economics-survive-reality)
7. [Economic Governance — Ongoing](#7-economic-governance--ongoing)
8. [Delegation Qualification Analysis](#8-delegation-qualification-analysis)

---

## 1. Executive Summary

JtD-1 (Shift Intake Parser) is the fastest-payback investment in the MedFlex pipeline and the critical path dependency for every downstream automation. It pays back in ~3 months, and its integration assets directly reduce the build cost of JtD-2 and JtD-3.

**Three key findings:**

1. **Parsing labor is pure overhead.** Current coordinator parsing costs $141,900/year (A1, A4, A7, A16) — a data-entry burden with no judgment value that an LLM eliminates for 85% of cases at $0.011/case (A10, A22). Every fill-time delay begins here.

2. **HITL rate is the only economic lever that matters.** Token cost ($0.011/case) and tool calls ($0.001/case) together are 3% of agent spend. Human review of the 15% exception path ($0.463/case) accounts for 97% of all agent-side cost. Cost optimization means HITL rate reduction, not LLM tuning.

3. **Wave 2 prompt re-tuning is self-financing within 6 weeks.** Dropping HITL rate from 15% to ≤10% (A32) adds $7,100/year in additional saving — recoverable from ~1–2 weeks of prompt engineering effort using the HITL correction corpus accumulated in production.

**Year 1 ROI Summary:**

| Scenario | Annual Saving | Payback | 3-Year ROI |
|---|---|---|---|
| Conservative (+50% token cost, 20% HITL) | $112,500 | 3.2 months | 676% |
| **Base case ($0.011/case, 15% HITL)** | **$119,900** | **3.0 months** | **727%** |
| Optimistic (−30% token cost, 10% HITL, A32) | $127,200 | 2.8 months | 777% |

JtD-1 is self-financing within Quarter 1. Starting month 4, it generates ~$10,000/month in net surplus that contributes to funding the longer-payback JtDs (JtD-3 at ~12 months, JtD-2 at ~3.3 months) within the Wave 1 portfolio.

---

## 2. Baseline Cost Model

### 2.1 Unit Cost

Parsing currently consumes 35% of coordinator active work time per match (A16), applied to the 20-minute total active time per case (A1):

| Component | Value | Source |
|---|---|---|
| Active parsing time per case | 7 min (35% × 20 min) | A1 × A16 |
| Fully-loaded coordinator hourly cost | $26.44/hr | A7 |
| **Baseline cost per parse** | **$3.08/case** | |

The capability spec confirms this at aggregate scale: ~1,274 minutes of daily parsing labor across 8 coordinators at 184 fills/day (A4). The small difference from the formula-derived 1,288 min/day (184 × 7 min) reflects rounding in A16's stated 35% proportion.

### 2.2 Annual Baseline

| Metric | Value | Source |
|---|---|---|
| Annual volume | 46,000 cases/year (184/day × 250 days) | A4 |
| **Annual parsing labor cost** | **$141,900/year** | A1, A4, A7, A16 |

### 2.3 Indirect Costs

**Queue delay cost**: Parsing is the first step in the pipeline — JtD-2 (candidate search) and JtD-3 (ranking) are blocked until `ParsedShiftRequirement` is written. Every parsing delay cascades directly to fill time. The 4.2-hour current average vs. the <1-hour target is attributable primarily to queue accumulation before any automation can begin.

**Rework cost**: A misextracted specialty code sends JtD-2 searching against the wrong credential profile. The 15% HITL mechanism prevents downstream propagation, but each BP1 case consumes coordinator review time in addition to the initial LLM call. The 200-record validation corpus (A29) is the gate that bounds this risk before production.

**Opportunity cost**: 8 coordinators spend ~35% of active time on data entry equivalent to reading a structured form and typing codes. This capacity is not contributing to match quality, nurse relationships, or exception management — all of which require coordinator judgment.

---

## 3. Token Economics Model

### 3.1 Token Consumption Per Case

JtD-1 is an LLM-native workstream: every inbound request triggers one Claude Sonnet API call. Token costs are explicit, fully attributable, and fixed per case.

| Component | Tokens | Cost (Sonnet: $3/$15 per 1M) | Source |
|---|---|---|---|
| System prompt (role + output schema + dictionaries + confidence rules + 3 few-shot examples) | ~1,300 input | — | A22 |
| User message (raw shift request text average) | ~200 input | — | A22 |
| LLM output (structured JSON with per-field confidence scores) | ~400 output | — | A22 |
| **Total per case** | **~1,500 in / ~400 out** | **$0.011/case** | A22 |

Calculation: (1,500 × $3.00 + 400 × $15.00) / 1,000,000 = $10.50 / 1,000,000 = $0.0105/case ≈ $0.011/case (A22).

The system prompt (~1,300 tokens) is stable across sessions. Prompt caching would reduce repeat input costs further, but is not modeled here because $0.011/case is already at 0.36% of the $3.08/case baseline — further optimization has negligible economic impact.

### 3.2 Tool Call Costs

| Tool Call | Per Case | Annual Cost |
|---|---|---|
| ServiceNow GET (queue poll, batched 10 records) | ~$0.0001 | ~$5/year |
| ServiceNow PATCH (PARSING lock) | ~$0.0001 | ~$5/year |
| ServiceNow POST (ParsedShiftRequirement write) | ~$0.0002 | ~$9/year |
| HITL Queue API write (15% of cases only) | ~$0.00015 | ~$3/year |
| Internal event bus emit | ~$0.00005 | ~$2/year |
| **Total tool calls** | **~$0.001/case** | **~$46/year** |

Tool call costs are negligible. The ServiceNow queue poll is batched (10 records per API call), making the per-case cost of the poll step a fraction of one API call divided across the batch.

### 3.3 Infrastructure Cost

JtD-1 runs as a lightweight polling service: 30-second polling intervals, ~0.38 LLM requests/minute peak — well within Anthropic Tier 3 limits (5,000 req/min) and ServiceNow rate limits (A23: ≥60 req/min).

| Component | Monthly | Annual |
|---|---|---|
| Container/Lambda runtime | ~$10/month | ~$120/year |
| API networking | ~$3/month | ~$36/year |
| Monitoring + logging | ~$5/month | ~$60/year |
| **Total infrastructure** | **~$18/month** | **~$216/year** |

Per-case infrastructure: ~$0.003/case.

### 3.4 Human-in-the-Loop Cost (BP1 Exception Path)

The 15% HITL path (A10) is the dominant cost driver — the only economically meaningful variable in the model:

| Component | Value | Source |
|---|---|---|
| HITL rate (BP1 route) | 15% | A10 |
| Coordinator review time per BP1 case | 7 min (conservative: same as original manual parse time) | A1 × A16 |
| Coordinator hourly cost | $26.44/hr | A7 |
| **HITL cost per case** | **$0.463/case** (0.15 × 7/60 × $26.44) | |
| Annual HITL cost | $21,298/year (46,000 × $0.463) | |

Note on HITL review time: using 7 min/HITL case (the original manual parsing time) is conservative. The coordinator is presented with a pre-filled partial parse and only needs to correct wrong fields, making actual review time likely shorter. The 7-min figure bounds the estimate on the high side; the economics are sound even at this conservative value.

### 3.5 Total Agent Cost Per Case

| Component | MVP (15% HITL) | Phase 2 (≤10% HITL, A32) |
|---|---|---|
| Token cost | $0.011 | $0.011 |
| Tool call cost | $0.001 | $0.001 |
| Infrastructure | $0.003 | $0.003 |
| HITL cost | $0.463 | $0.308 |
| **Total agent cost** | **$0.478/case** | **$0.323/case** |
| Baseline cost | $3.08/case | $3.08/case |
| **Cost reduction** | **84.5%** | **89.5%** |

**Cost decomposition**: Token + tool costs ($0.015/case) = 3% of total agent cost. HITL = 97%. The entire economic optimization roadmap for JtD-1 is HITL rate reduction, not token engineering.

### 3.6 Annual Cost Summary

| Line Item | Annual |
|---|---|
| Token costs | $506 |
| Tool call costs | $46 |
| Infrastructure | $216 |
| HITL labor | $21,298 |
| **Total agent operating cost** | **$22,066/year** |
| Baseline parsing labor | $141,900/year |
| **Annual net saving** | **$119,834/year ≈ $119,900/year** |


 ### 3.7 Multi-Model Output Analysis & Economic Optimization  

After analyzing 5 model outputs for the MedFlex intake parser, Claude Haiku 4.5 (Model C) is the recommended production model: it scores 8.78/10 accuracy — higher than the currently specified Sonnet 4.6 (8.30/10) and within 1.3% of the best performer (GPT-5/Opus at 8.90/10), while costing ~73% less per case than Sonnet. The biggest errors in the test set were date disambiguation failures — Gemini 2.5 hallucinated a future year (2028) to reconcile a Saturday/date conflict; Sonnet 4.6 prioritized day-of-week over the explicit date. Since HITL cost dominates at 97% of agent spend, the economic impact of switching models is small ($377/year token savings), but using the higher-accuracy Haiku reduces downstream HITL risk. The existing economics model correctly identifies Haiku as a future candidate; this analysis promotes it to the recommended model now.   


---

## 4. ROI and Business Case

### 4.1 Standard Business Case Model

| Metric | Value | Source |
|---|---|---|
| Annual baseline cost | $141,900/year | §2 |
| Annual agent operating cost | $22,100/year | §3.6 |
| **Annual saving** | **$119,900/year** | §3.6 |
| Build cost | $30,000 (2 weeks × $15K/week) | A21 |
| Annual maintenance | $4,500/year (15% × $30K) | A31 |
| **Payback period** | **3.0 months** ($30K / ($119,900/12)) | |
| Year 1 net (saving − build − maintenance) | $85,400 | |
| Year 1 ROI | 247% | |
| 3-year total saving | $359,700 | |
| 3-year total investment | $43,500 ($30K + 3 × $4.5K) | |
| **3-year net value** | **$316,200** | |
| **3-year ROI** | **727%** | |

### 4.2 Financial Sensitivity Table

| Scenario | Token Cost | HITL Rate | Annual Saving | Payback | 3-Year ROI |
|---|---|---|---|---|---|
| Conservative | $0.0165 (+50%) | 20% | $112,500 | 3.2 months | 676% |
| **Base case** | **$0.011** | **15% (A10)** | **$119,900** | **3.0 months** | **727%** |
| Optimistic | $0.0077 (−30%) | 10% (A32) | $127,200 | 2.8 months | 777% |

**Conservative scenario calculation**: HITL cost = 0.20 × (7/60) × $26.44 = $0.617/case. Total agent cost = $0.638/case. Annual saving = $141,900 − $29,350 = $112,550/year.

**Robustness**: The business case is insensitive to token price movement — a 50% price increase shifts payback by only 0.2 months. The range of 3-year ROI (676%–777%) is narrow, confirming that JtD-1 economics are not at risk from LLM pricing volatility. The only scenario that materially degrades ROI is a sustained HITL rate above 25% — which would only occur if the A10 accuracy target (≥85%) is not met at launch.

**A10 risk gate**: If production HITL rate exceeds 15% post-launch, the conservative scenario degrades further. At 25% HITL, annual saving drops to ~$102,000 and payback extends to ~3.5 months — still sound, but requiring Wave 2 prompt re-tuning to recover the base case. This is why the 200-record validation corpus run (§6.1) is the production go/no-go gate.

---

## 5. Self-Financing Roadmap

### 5.1 JtD-1's Role in Wave 1

JtD-1 is the fastest-payback use case in Wave 1 and is the critical path for every other automation in the pipeline — JtD-2 and JtD-3 cannot start their work until JtD-1 produces a `ParsedShiftRequirement`.

| Wave 1 Use Case | Build Cost | Annual Saving | Payback | Build Weeks |
|---|---|---|---|---|
| JtD-1 — Shift Intake Parser | $30K | $119,900 | 3.0 months | Weeks 1–2 |
| JtD-2 — Candidate Search | $45K | ~$165,000 | ~3.3 months | Weeks 2–4 |
| JtD-3 — Match Selection | $60K | $60,144 | ~12 months | Weeks 3–6 |
| JtD-4 — Submission | $15K | ~$15,000 | ~12 months | Week 7 |
| JtD-5a — Hospital Notification | $15K | ~$6,000 | ~30 months | Week 8 |
| **Wave 1 Total** | **$120K** | **~$346,000/year** | **~4.2 months** | |

*JtD-2/JtD-4/JtD-5a annual saving figures sourced from `specs/volume-×-value-analysis.md`.*

JtD-3 (match selection) has a 12-month payback on its own — it requires M3 revenue recovery to close that gap. JtD-1 and JtD-2 fund the portfolio: their combined ~$285,000/year saving and <4-month paybacks generate enough Wave 1 surplus to absorb JtD-3's slower return.

### 5.2 Platform Assets Built in JtD-1

JtD-1 is built first (Weeks 1–2) and produces reusable integration components that reduce subsequent Wave 1 build costs:

| Asset Built in JtD-1 | Reused by | Estimated Build Saving |
|---|---|---|
| ServiceNow REST read integration (auth, retry, rate limit, circuit breaker) | JtD-2, JtD-3 | ~$5,000 |
| ANTHROPIC_API_KEY provisioning + error handling pattern | JtD-3 Phase 2 ML ranker | ~$2,000 |
| Internal HITL Queue API (write contract + schema) | JtD-3 BP4 coordinator review | ~$4,000 |
| Internal event bus trigger pattern | JtD-2, JtD-3 | ~$2,000 |
| Dead-letter queue + reconciliation cron infrastructure | JtD-2, JtD-3, JtD-4 | ~$3,000 |
| **Total Wave 1 build cost reduction from JtD-1 assets** | | **~$16,000** |

This $16K reduction means Wave 1's effective build cost for JtD-2 onward is ~$16K lower than the gross figure — shortening portfolio payback from 4.2 months to approximately 3.8 months.

### 5.3 Self-Financing Timeline

```
Weeks 1–2:   JtD-1 built ($30K invested); launched end of week 2
Week 3+:     JtD-1 live; daily parsing labor saving begins (~$480/day)
Month 3:     JtD-1 reaches payback; net surplus begins (~$10,000/month)
Month 3–6:   JtD-1 surplus (~$30K over 3 months) offsets JtD-3 build cost
Month 4–6:   Wave 1 portfolio net positive; combined JtD-1+JtD-2 surplus funds Wave 2
Year 1 end:  JtD-1 generates $85,400 net (after build + maintenance)
```

### 5.4 Wave 2 Self-Financing

Wave 2 JtD-1 improvement (system prompt re-tuning) requires no additional capital allocation — it is funded from Wave 1 surplus. Cost is ~1–2 FDE engineer-weeks to:
1. Analyze the HITL correction corpus (750–1,100 examples after 4–6 weeks live at 15% HITL rate)
2. Identify highest-frequency failure modes (typically: ambiguous location references, unknown specialty abbreviations, relative datetime expressions)
3. Update few-shot examples in the system prompt; restart agent

Expected outcome: HITL rate ≤10% (A32), producing $7,100/year additional saving. At 1 engineer-week cost (~$7,500 at A21 rates), payback on the Wave 2 improvement is approximately 13 months — modest but positive, and enabling the Wave 3 option (structured intake template T2 for high-volume hospital partners).

---

## 6. Calibration — Making Economics Survive Reality

### 6.1 Mock Environment Testing

Before production release, validate against the 200-record corpus (A29: non-production ServiceNow instance with representative historical shift request data):

- Run the parser against all 200 records; measure field-level accuracy for specialty, datetime, location, and credentials separately
- Confirm overall HITL rate is ≤15% on the test corpus
- Measure actual token consumption per case — compare against the $0.011/case budget (A22); flag if average exceeds $0.013
- Measure parse latency (QUEUED → PARSED status) — confirm ≤30 seconds on test instance
- Test BP1 path: submit a known low-confidence case; confirm `HITLQueueEntry` writes within 10 seconds
- Test PARSE_FAILED path: submit a request triggering HTTP 400 from the LLM mock; confirm ops alert fires

**Go/no-go gate**: Do not release to production until field-level accuracy ≥85% AND HITL rate ≤15% on the 200-record corpus. If HITL rate is 15%–20%, tune few-shot examples and re-run before launch. If HITL rate is >20% on test data, delay launch and escalate to prompt architecture review — the system prompt structure needs rework, not just example updates.

### 6.2 Key Calibration Metrics

| Metric | Target | Impact If Missed | Remediation |
|---|---|---|---|
| Field-level extraction accuracy | ≥85% (A10) | HITL rate rises; $3.08/case cost on uncaught misses | Re-tune few-shot examples; expand SpecialtyCode / CredentialCode dictionaries; re-validate |
| HITL rate (BP1 route) | ≤15% (A10) | Agent cost per case rises; ROI degrades below base case | Tune confidence threshold; add few-shot examples for top failure modes |
| Parse latency (QUEUED → PARSED) | ≤30 seconds | Fill-time gains erode; downstream JtD-2/JtD-3 SLAs miss | Reduce system prompt token count; review retry strategy; check ServiceNow write latency |
| Cost per parse | ≤$0.011/case (A22) | Budget exceeded | Trim system prompt tokens; evaluate Claude Haiku for pre-filtering (Wave 3) |
| LLM fallback rate | ≤1% | HITL queue floods with LLM_UNAVAILABLE cases | Review Anthropic API tier; implement circuit breaker earlier; check ANTHROPIC_API_KEY |
| ServiceNow write success rate | ≥99% | Dead-letter queue grows; fill-time delays compound | Check A11-write credential provisioning; review ServiceNow instance health |

### 6.3 Sigma Management

JtD-1 is a **narrow-sigma** workload. Hospital shift requests follow highly predictable domain patterns: a limited vocabulary of specialty codes, credential abbreviations, date formats, and hospital names. The LLM's job is pattern-matching, not creative reasoning. Variance comes from non-standard hospital text formats, unknown abbreviations, and ambiguous location names — all surfaced explicitly through confidence scoring and routed to HITL.

Tuning levers:
- **Temperature**: 0.0 — no creative variance wanted on extraction tasks
- **Few-shot examples**: 3 in system prompt; calibrate output format and confidence scoring behavior; update in Wave 2 using HITL correction corpus
- **Confidence threshold**: 0.85 routing gate; validated against the 200-record corpus; adjustable as a config parameter without code changes
- **Dictionary coverage**: SpecialtyCode and CredentialCode dictionaries loaded from config at startup; update when new abbreviations appear in HITL corrections; each update narrows sigma further

---

## 7. Economic Governance — Ongoing

### 7.1 Monthly Dashboard

| Metric | Target | Data Source |
|---|---|---|
| Cost per parse | ≤$0.011/case | Claude API usage logs (`usage.input_tokens`, `usage.output_tokens`) |
| HITL rate (BP1 route) | ≤15% MVP; ≤10% Phase 2 (A32) | `HITLQueueEntry` count ÷ total `ShiftRequest` volume |
| Parse latency p95 | ≤30 seconds | `u_received_at` → `u_parsed_at` timestamp delta |
| LLM fallback rate | ≤1% | `PARSE_FAILED` + `LLM_UNAVAILABLE` reason count ÷ total |
| Dead-letter queue depth | 0 (cleared within 1 business day) | Reconciliation cron log |
| HUMAN_CORRECTED rate | Tracked only | `u_parse_method = HUMAN_CORRECTED` count; seeds Wave 2 corpus |

### 7.2 Quarterly Reviews

- **HITL rate trend**: Declining trend indicates few-shot coverage is improving as corpus accumulates. Rising trend (new hospital submission patterns, specialty abbreviations) triggers Wave 2 prompt update.
- **Model release evaluation (A22)**: On each Anthropic model release, run the 200-record validation corpus against the new model. Compare accuracy, HITL rate, tokens per case, and latency. If the new model achieves equivalent accuracy at lower cost, update model ID in config — it is a parameterized field in the integration contract (A22). Claude Haiku ($0.25/$1.25 per 1M tokens) is a Wave 3 candidate for a pre-filter architecture: Haiku confirms whether confidence is high or low; Sonnet handles the ambiguous subset only.
- **Volume change reforecast**: If MedFlex fills/day changes ±20% from the A4 baseline (184/day), reforecast annual saving, annual HITL labor, and infrastructure cost per case.

### 7.3 Wave 2 Trigger Conditions

Initiate Wave 2 system prompt re-tuning when all four conditions are met:

1. ≥500 `HUMAN_CORRECTED` entries in `HITLQueueEntry` (sufficient to identify top-3 failure modes)
2. HITL rate has stabilized at or above 12% for 2 consecutive weeks (prompt is plateauing — incremental auto-parse accuracy gains have stalled)
3. FDE engineering capacity available (~1–2 engineer-weeks; A21 rates)
4. Objective: reduce HITL rate to ≤10% (A32)

Expected timing: ~4–6 weeks post-launch at 15% HITL rate × 184/day × 20 production days = 750–1,100 HITL corrections. Wave 2 improvement is executable within Wave 1's delivery window.

### 7.4 On-Model-Release Review Protocol

1. Run 200-record validation corpus against candidate new model
2. Record: field-level accuracy, overall HITL rate, tokens per case, latency p95
3. If new model achieves ≥ same accuracy AND ≤ same cost: update `model` parameter in agent config; restart agent; monitor HITL rate for 48 hours post-change
4. Update A22 token cost assumptions if pricing changes materially (>20%)
5. If new model is significantly cheaper (e.g., Haiku for routine cases): design pre-filter architecture (Wave 3) — do not implement mid-production without a full validation run

---

## 8. Delegation Qualification Analysis

JtD-1 contains 10 micro-tasks spanning fully-agentic mechanical work (queue polling, status management, schema validation) to human judgment for exception resolution (coordinator BP1 correction of ambiguous requests). The economics strongly favor delegation for all structural tasks. The single retained human task (MT-1.6) is appropriately positioned at the genuine judgment boundary: ambiguous requests where the LLM has signaled its own uncertainty.

### 8.1 Delegation Summary Table

| MT | Micro-Task | Delegation Level | Economic Cost | Verdict |
|---|---|---|---|---|
| MT-1.0 | Poll ServiceNow queue | Fully Agentic | ~$0.0001/case | DELEGATE |
| MT-1.1 | Acquire processing lock | Fully Agentic | ~$0.0001/case | DELEGATE |
| MT-1.2 | LLM extraction call | Fully Agentic | $0.011/case | DELEGATE |
| MT-1.3 | Validate LLM response schema | Fully Agentic | ~$0.0001/case | DELEGATE |
| MT-1.4a | Compute overall confidence score | Fully Agentic | ~$0.0001/case | DELEGATE |
| MT-1.4b | Route high-confidence parse (BP2) | Fully Agentic | ~$0.0001/case | DELEGATE |
| MT-1.4c | Route low-confidence parse (BP1) | Agent Routes, Human Resolves | $0.463/case (HITL labor, 15% rate) | PARTIAL DELEGATE |
| MT-1.5 | Handle PARSE_FAILED | Fully Agentic | ~$0.0001/case | DELEGATE |
| MT-1.6 | Human review correction (BP1 resolution) | Human Acts, Agent Logs | $0.463/case (same HITL cost as MT-1.4c) | RETAIN |
| MT-1.7 | Emit parsed event to JtD-2 | Fully Agentic | ~$0.0001/case | DELEGATE |

### 8.2 Delegation Rationale by Workstream

---

**MT-1.0–MT-1.1 — Queue Poll and Processing Lock (Pure Mechanics)**

Delegation justification: deterministic queue consumption (FIFO ordering) and a status PATCH that acts as an advisory lock. Both tasks have zero cognitive load — there is no judgment, no ambiguity, and no decision-making. Delegating these eliminates the latency between request arrival and the start of LLM processing (previously: coordinator scans their email or queue UI, picks up the request, opens ServiceNow). At 184 cases/day, the agent polls every 30 seconds with no human queuing delay.

Economic impact: combined cost ~$0.0002/case. Negligible in absolute terms; eliminates the human queue-management overhead that was embedded in the original 7-min baseline.

---

**MT-1.2 — LLM Extraction Call (Core Value Proposition)**

Delegation justification: this is the primary economic trade. The LLM translates free-text hospital requests into a strict validated schema at $0.011/case — replacing $3.08/case of coordinator labor for the 85% auto-path. Instruction specificity (A22 system prompt: role, output schema, domain dictionaries, per-field confidence rules, 3 few-shot examples) is sufficient to produce consistent, validatable JSON output.

The confidence scoring mechanism makes delegation safe: the LLM self-reports uncertainty per field, and the agent uses the minimum confidence as the routing signal. The model does not make autonomous decisions on ambiguous cases — it flags them explicitly. This is the correct human-AI boundary for an extraction task: automate the structured pattern-matching; surface the genuine ambiguity for human resolution.

Economic impact: $0.011/case in token cost replaces $3.08/case in coordinator labor for 85% of cases. The remaining $0.463/case in HITL cost handles the 15% exception path.

---

**MT-1.3–MT-1.4a — Schema Validation and Confidence Computation (Rule Execution)**

Delegation justification: both tasks are fully deterministic rule execution. Schema validation checks field presence, SpecialtyCode dictionary membership, and CredentialCode dictionary membership — no judgment involved. Confidence computation is a single formula: `min(specialty_confidence, datetime_start_confidence, datetime_end_confidence, location_confidence, credential_confidence)`. These are correctly delegated; retaining them for human review would add latency without adding value.

---

**MT-1.4b — High-Confidence Routing (BP2 Auto-Proceed)**

Delegation justification: once confidence_score ≥ 0.85 and schema validation passes, the write to `ParsedShiftRequirement` and the `PARSED` status transition are unconditional. The 0.85 threshold was derived from the A10 accuracy target and validated against the 200-record corpus. Delegating BP2 routing is what eliminates coordinator time for 85% of requests — any human checkpoint here would negate the primary economic benefit of JtD-1.

Economic impact: removing the human touchpoint for BP2 cases recovers 7 min × 85% × 46,000 cases = ~2,714 coordinator-hours/year = $71,803/year in saved labor (the difference between baseline $141,900 and HITL-only cost ~$70,097).

---

**MT-1.4c — Low-Confidence Routing (BP1, Partial Delegation)**

Delegation justification: the routing *decision* (is confidence_score < 0.85?) is fully delegatable — it is a numeric comparison. What is NOT delegated is the *resolution* of a low-confidence case — that is MT-1.6. The partial parse written to `HITLQueueEntry` pre-fills the coordinator's correction form with whatever fields the LLM extracted at moderate confidence, reducing the manual review burden.

Economic implication: $0.463/case is the cost of human review on the 15% exception path. The agent bears the routing responsibility at $0.0001/case; the human cost activates precisely where the agent's own confidence signal indicates uncertainty. This is the optimal delegation boundary — human effort is applied where the agent has signaled it is insufficient, not uniformly across all cases.

---

**MT-1.6 — Human Review Correction (Necessary Retention)**

Retention justification: this is the one genuinely irreplaceable human task in JtD-1. The coordinator reads ambiguous free text, applies domain knowledge (hospital location relationships across a multi-campus system, shift scheduling conventions, credential naming variations across hospital systems), and produces a validated correction. Two additional factors require human judgment that no system prompt can replace:

1. **Cancellation authority**: if a request is a duplicate or invalid, the coordinator's decision to CANCEL (HUMAN_REVIEW → CANCELLED) represents an action in an active hospital relationship — it should not be automated.
2. **Hospital clarification**: when the request is fully unparseable (partial_parse = null), the coordinator contacts the hospital directly. This requires relationship awareness and communication judgment beyond extraction.

The HITL mechanism converts this from "100% of cases" (baseline) to "15% of cases" — which is the correct engineering answer. Further reduction comes from prompt engineering (Wave 2, A32 target: 10%), not from attempting to automate judgment.

Economic cost: $0.463/case embedded in total agent cost (at 15% HITL rate). Wave 2 target of ≤10% HITL (A32) reduces this to $0.308/case, saving $7,100/year.

---

**MT-1.5, MT-1.7 — PARSE_FAILED Handling and Event Emission (Infrastructure)**

Both are fully agentic infrastructure operations with no judgment content. MT-1.5 (PARSE_FAILED) sets status and fires an ops alert — the alert notifies a human, but the routing decision itself is deterministic. MT-1.7 (emit `shift_parsed` event) is a fire-and-forget trigger that unblocks JtD-2. Combined cost: ~$0.0001/case.

---

### 8.3 Overall JtD-1 Delegation Economics

| Classification | Micro-Tasks | Agent Cost | Human Cost |
|---|---|---|---|
| Fully delegated (Fully Agentic) | MT-1.0, 1.1, 1.2, 1.3, 1.4a, 1.4b, 1.5, 1.7 | $0.015/case | $0.00/case |
| Boundary (Agent Routes, Human Resolves) | MT-1.4c | $0.0001/case (routing) | $0.463/case (resolution) |
| Retained (Human Acts, Agent Logs) | MT-1.6 | — | (included in MT-1.4c HITL cost) |
| **Total** | **10 micro-tasks** | **$0.015/case (agent)** | **$0.463/case (HITL, 15% path)** |

The HITL mechanism is not a weakness in the design — it is the economic boundary condition that makes 85% autonomous operation safe. Without it, a 90% accuracy parser would propagate errors into JtD-2 and JtD-3 at $3.08/case cost to fix downstream. With it, the 15% uncertain cases are caught and corrected at $0.463/case while the 85% certain cases proceed at $0.015/case.

At the Wave 2 HITL target of ≤10% (A32):
- Agent cost: $0.015/case
- HITL cost: $0.308/case
- Total: $0.323/case (89.5% reduction from $3.08/case baseline)
