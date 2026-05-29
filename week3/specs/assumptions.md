# Assumptions

> All assumptions go beyond what is explicitly stated in `scenario.md` and `discovery-session.md`.
> Each entry includes: assumed value, reasoning, and confidence level.

---

## A1 — Active coordinator work time per complete shift match: ~20 minutes

**Assumed value**: 20 minutes of active work per complete end-to-end match (request intake → candidate selection → submission).

**Reasoning**: $14M annual revenue back-solves to ~184 filled shifts/day (see A3, A4). With 8 coordinators and an 8-hour day, each handles ~23 matches/day → 8h × 60min / 23 ≈ 20 min/match net of admin overhead. This is consistent with a manual multi-step workflow (parse request, search candidates, check credentials, confirm availability, select best fit, submit). The 4.2-hour average *fill time* is elapsed calendar time including queue wait, nurse response latency, and hospital confirmation — not coordinator active work time.

**Confidence**: Medium. CEO deferred to head of operations for exact numbers. Direct timing study would validate or invalidate.

**Referenced in metrics**: M1, M2

---

## A2 — Candidate evaluations per match: ~5

**Assumed value**: A coordinator evaluates approximately 5 nurse candidates before selecting and submitting one.

**Reasoning**: 120 decisions/coordinator/day ÷ ~23 complete matches/day (A1) ≈ 5.2 evaluations per match. Each evaluation involves checking credentials, proximity, and availability for one candidate. This also explains why senior coordinators are faster — they pattern-match to the right candidates immediately, reducing evaluations to 1-2.

**Confidence**: Medium. Consistent with the math but not directly confirmed in discovery.

**Referenced in metrics**: M2

---

## A3 — MedFlex agency revenue per filled shift: ~$300

**Assumed value**: MedFlex earns approximately $300 net agency revenue per filled shift.

**Reasoning**: Travel nurse single-shift billing rate typically $100–200/hour × 12-hour shift = $1,200–$2,400 billed to hospital. Staffing agency margin: 15–25%. Mid-range: $1,800 × 17% ≈ $306. Cross-check: $14M annual revenue / 250 working days / ~184 fills/day ≈ $304/shift. Both methods converge at ~$300.

**Confidence**: Medium-High. Revenue figure is given ($14M); fills/day is inferred (see A4). Margin assumption is industry standard but unverified for MedFlex specifically.

**Referenced in metrics**: M3, M4, M5

---

## A4 — Current filled shifts per day: ~184

**Assumed value**: MedFlex fills approximately 184 shifts per day under current operations.

**Reasoning**: $14M annual revenue / $300 per shift (A3) / 250 working days = 186.7 ≈ 184 shifts/day net of ~1% variance. With a 12% no-show rate applied post-acceptance, the raw accepted placements are higher (~209/day), but only ~184 result in revenue-generating fills.

**Confidence**: Medium. Derived entirely from A3. If agency margin is higher (e.g., $500/shift), volume would be lower (~112/day). This is the most load-bearing derived figure in the model.

**Referenced in metrics**: M1, M2, M3, M4, M5

---

## A5 — Share of inbound requests currently lost to competitors due to slow fill time: ~30%

**Assumed value**: Approximately 30% of shift requests submitted to MedFlex are ultimately filled by a competing agency because MedFlex responds too slowly.

**Reasoning**: Marcus explicitly confirmed that hospitals submit requests to multiple agencies simultaneously and that "if we don't supply, then someone else will." The 4.2-hour average fill time vs. the <1-hour target implies significant competitive loss. A 30% loss rate is conservative (industry studies on competitive staffing suggest first-response wins in 40–60% of contested cases). No direct MedFlex data exists.

**Confidence**: Low. Highest-risk assumption in this document. Needs direct measurement (e.g., win/loss tracking by request). If the real loss rate is 10%, the revenue-at-stake calculation drops by two-thirds.

**Referenced in metrics**: M3

**Falsifiable check** *[Rev. 2026-05-13 — CEO Pushback]*: Two-step check executable in the first two weeks of real ServiceNow data.

*Step 1 — Win rate calculation (Week 1):* Pull last 3 months of ServiceNow records. Compute win rate = total shifts filled ÷ total inbound shift requests logged. This is the direct measurement of A5.

*Step 2 — Speed correlation (Week 2, if historical data supports it):* For filled shifts in the same window, plot time-to-fill against queue depth by hour. If fill rate drops materially during high-queue periods, the competitive loss is speed-sensitive — validating A6's mechanism.

**Decision gate by end of week 2:**

| Win rate result | What it means for M3 | Action |
|---|---|---|
| Win rate ≤75% | A5 plausible; $1.5M target stands | Proceed with full engagement scope |
| Win rate 75–90% | A5 overstated; M3 likely $375K–$900K | Revise M3 before CFO review; proceed with adjusted ROI framing |
| Win rate >90% | A5 invalid; speed recovery is not the revenue story | Replace M3 with throughput-scaling metric; reframe to volume × $300 × growth path |

*Precondition:* Requires ServiceNow to log all inbound requests, including unfilled ones. If only filled shifts are logged, skip to Step 2 and add a "request not filled" log field from week 1 to generate forward-looking data.

---

## A6 — Reducing fill time to <1 hour recovers ~50% of currently lost requests

**Assumed value**: Cutting fill time from 4.2h to <1h would allow MedFlex to capture approximately 50% of the shift requests currently lost to competitors (A5).

**Reasoning**: First-response advantage in competitive staffing is significant but not absolute — hospitals have preferred agency relationships, nurse preferences, and price sensitivity. Achieving <1h response will not win every contested request, but it eliminates the primary disqualifier. Assuming roughly half of lost requests are speed-sensitive (vs. preference or price-sensitive), 50% recovery is reasonable.

**Confidence**: Low. Depends on competitive dynamics not disclosed. Named here to make the revenue case falsifiable.

**Referenced in metrics**: M3

---

## A7 — Fully-loaded coordinator cost: $55,000/year ($26.44/hour)

**Assumed value**: Each coordinator costs MedFlex approximately $55,000/year fully loaded (salary + benefits + overhead).

**Reasoning**: Healthcare staffing coordinator median base salary in the US: $42,000–$52,000 (BLS 2024). Adding 30–35% employer costs (payroll taxes, health benefits, 401k, overhead): $55,000–$70,000 fully loaded. Using the lower bound ($55,000) to be conservative. 8 coordinators = $440,000/year in coordination labor.

**Confidence**: Medium. Standard labor cost model; actual MedFlex salaries unknown.

**Referenced in metrics**: M2

---

## A8 — New coordinator ramp-to-productivity time: ~3 months

**Assumed value**: A new coordinator requires approximately 3 months before reaching full matching productivity.

**Reasoning**: Marcus explicitly stated training is "one of my biggest problems" and that "newcomers usually take longer" while experienced coordinators have internalized 10+ years of pattern recognition. Healthcare staffing matching involves multi-state credential rules, hospital preferences, and nurse relationship knowledge. Three months is a standard ramp for knowledge-worker roles with comparable complexity.

**Confidence**: Medium-High. Directly supported by discovery session language.

**Referenced in metrics**: M2

---

## A9 — Share of no-shows attributable to competitive poaching: ~60%

**Assumed value**: Approximately 60% of the 12% no-show rate is caused by nurses accepting competing agency offers after being notified by MedFlex (passive confirmation model + multi-agency dynamics).

**Reasoning**: Marcus stated that nurses sometimes don't show up because they attended a hospital submitted by another agency. The passive confirmation model (silence = acceptance, no explicit acknowledgment required) amplifies this: nurses may not feel committed. The remaining ~40% of no-shows are genuine scheduling conflicts, illness, or unreachable nurses.

**Confidence**: Low. No MedFlex data to support the split. This matters for solution design — competitive poaching is only partially addressable by automation (earlier confirmation requests, but nurses can still defect).

**Referenced in metrics**: M4

---

## A10 — Free-text ServiceNow records are parseable with >85% accuracy using LLM extraction

**Assumed value**: An LLM-based intake parser can extract structured shift requirements (specialty, date, location, credential requirements) from free-text hospital requests in ServiceNow with >85% field-level accuracy.

**Reasoning**: Hospital shift requests follow domain-specific patterns (e.g., "ICU RN needed Friday 7am–7pm, BLS/ACLS required, St. David's North Austin"). Modern LLMs with domain-specific prompting achieve >90% extraction accuracy on similarly structured free text in comparable healthcare intake workflows. The 85% threshold accounts for ambiguous or non-standard submissions. Sub-85% accuracy would require too much human correction to achieve speed gains.

**Confidence**: Medium-High on technical feasibility. Low on whether 85% is sufficient for downstream automation without human review on low-confidence parses.

**Referenced in metrics**: M1, M2

---

## A11-read — ServiceNow REST API available for agent read access

**Assumed value**: MedFlex's ServiceNow instance exposes a REST API that an external agent can use to read shift requests and read nurse profiles. IT/admin can configure read-only agent credentials by end of week 2.

**Reasoning**: ServiceNow is an enterprise platform where REST API access is a standard licensed capability. Read-only credentials carry lower privilege and typically have a shorter provisioning path than write credentials. JtD-1 (parser) and JtD-2 (candidate search) depend only on read access. The ServiceNow admin contact (not the Head of Operations) can provision this.

**Confidence**: Medium. Technically standard for ServiceNow; operationally depends on MedFlex IT capacity and licensing tier.

**Referenced in metrics**: M1, M2 (JtD-1, JtD-2)

---

## A11-write — ServiceNow REST API available for agent write access *[Rev. 2026-05-13 — CEO Pushback]*

**Assumed value**: MedFlex's ServiceNow instance permits write access via REST API for an external agent to record coordinator approval events (JtD-3) and submit candidate proposals to hospitals (JtD-4). This requires a distinct, higher-privilege credential set, separate from read access, that IT/admin can provision by end of week 3.

**Reasoning**: ServiceNow write API access requires higher-privilege credentials with different security review and change-management steps than read-only. JtD-3 (coordinator review interface — approval event) and JtD-4 (automated submission) both depend on write access. These two features share the same go/no-go gate: if write credentials are not provisioned by end of week 3, both Features 3 and 4 are blocked simultaneously — not sequentially. The write credential must be requested from the ServiceNow admin contact as a distinct, higher-privilege ask, separate from the read credential needed by JtD-1 and JtD-2.

**Confidence**: Medium. Write API is a standard ServiceNow capability; the risk is provisioning timeline and change-management approval, not technical availability.

**Referenced in metrics**: M1, M2, M3 (JtD-3, JtD-4)

---

## A12 — Hospital feedback on nurses (acceptance/rejection events) is partially captured in ServiceNow

**Assumed value**: MedFlex records at minimum candidate acceptance and rejection events per nurse per hospital in ServiceNow, enabling the AI ranker to weight hospital preference history in candidate scoring.

**Reasoning**: Marcus stated "we marked this in our systems" when asked about tracking nurse-hospital feedback. Rejection events are also reported as the source of the 7% mismatch statistic ("purely based on the data we get from the hospital"). At minimum, accepted/rejected outcomes per nurse-hospital pair are likely present. Whether these are structured fields or free-text notes is unknown.

**Confidence**: Medium-Low. Presence of some event data is confirmed; completeness, structure, and historical depth are unknown.

**Referenced in metrics**: M5

---

## A13 — Marcus will accept a human-in-the-loop MVP architecture and not push for full autonomy at launch

**Assumed value**: Marcus will approve a design where coordinators review and approve AI-ranked recommendations in MVP, rather than requiring the agent to submit to hospitals without human approval from day one.

**Reasoning**: Marcus deferred the human-in-the-loop decision entirely to FDE expertise ("I'm not an expert in this area — if you say you don't need human in the loop, then I would rely on you"). He also expressed the only two concerns as matching accuracy and coordinator trust/adoption — both of which the HITL design directly addresses. The two prior AI failures and his stated skepticism about accuracy make a full-autonomy launch commercially and operationally risky in a way he has implicitly acknowledged.

**Confidence**: Medium-High. Marcus explicitly delegated this decision and his concerns align with the HITL rationale.

**Referenced in metrics**: M2

---

## A14 — The nurse notification system supports programmatic triggering and response capture

**Assumed value**: The system that sends SMS/email notifications to nurses when a placement is confirmed can be triggered via API or ServiceNow workflow automation, and can capture nurse acknowledgment/decline responses (not just send one-way notifications).

**Reasoning**: Marcus confirmed that nurses are automatically notified via SMS/email when a shift placement is confirmed. The mechanism is either ServiceNow-native or an integrated notification service. However, whether response tracking (capturing explicit acknowledgment vs. no-response) is currently enabled or buildable within 8 weeks is explicitly unconfirmed (U4). The passive confirmation model (silence = acceptance) suggests response capture has not been implemented.

**Confidence**: Low. Trigger capability is plausible; response tracking is unconfirmed and likely requires new infrastructure.

**Referenced in metrics**: M4

---

## A15 — All 8 coordinators share a single ServiceNow instance with no per-coordinator data silos

**Assumed value**: All 8 coordinators work from the same ServiceNow instance and access the same nurse profile database — there are no regional, team-level, or per-coordinator data partitions that would require separate agent configurations or data reconciliation.

**Reasoning**: Discovery confirmed a centralized ServiceNow system ("there is a centralized system around ServiceNow — all requests go through"). The "8 different judgment patterns" observation refers to decision-making style, not data access segregation. No indication of per-coordinator specialization or regional data splits was given.

**Confidence**: High. Standard enterprise deployment pattern; would only fail if coordinators have undisclosed regional or specialty-based data partitions.

**Referenced in metrics**: M1, M2

---

## A16 — Coordinator active work time distribution across cognitive zones: ~35% parsing, ~55% search/evaluation, ~10% submission

**Assumed value**: Of the ~20 minutes of active coordinator work per match (A1), approximately 35% is consumed by intake parsing (JtD-1), 55% by candidate search and evaluation (JtD-2 + JtD-3), and 10% by submission and documentation (JtD-4).

**Reasoning**: Marcus described "matching availability and profile" as the biggest time-consuming step, which maps to JtD-2–3. The ~5 candidate evaluations (A2) at ~2 minutes each account for ~10 minutes / ~20 minutes = ~50% of active time. Parsing is explicitly the first cognitive step per discovery ("scan request"). Submission is near-clerical (format + click). The 35/55/10 split approximates this without a direct time study.

**Confidence**: Low. No time-study data exists. This matters for ROI-by-zone calculations — if parsing is less than 35%, the parser's standalone throughput impact is smaller than projected.

**Referenced in metrics**: M1, M2

---

## A17 — Nurse availability data staleness rate: ~15–20%

**Assumed value**: Approximately 15–20% of nurse availability records in ServiceNow are not current at any given time.

**Reasoning**: Marcus confirmed nurse availability is entirely self-managed ("up to them to update"). No automated prompts, no enforcement mechanism, no freshness timestamp is mentioned. The 12% no-show rate (partly from genuine scheduling conflicts per A9) and the implicit possibility of stale data in a self-managed system support a meaningful staleness estimate. 15–20% is conservative for a large pool without automated reminders. Stale availability directly causes false positives in MT-2.2 (availability filter), wasting search time and occasionally producing matched candidates who cannot actually attend.

**Confidence**: Low. No MedFlex data on record freshness. Key for understanding actual reliability of the availability filter and the value of automated staleness detection.

**Referenced in metrics**: M1, M4

---

## A18 — Senior coordinator pattern recognition is concentrated in Zone 3 (candidate pre-selection), not parsing or submission

**Assumed value**: The speed advantage of senior coordinators (10+ years) is primarily located in MT-3.2 (tacit knowledge application) — specifically, the ability to skip MT-2.1 through MT-2.5 by going directly to 1–3 known candidates, reducing effective evaluations from ~5 (A2) to ~1–2.

**Reasoning**: Marcus explicitly stated experienced coordinators "know how to act better in specific cases" and named the specialization of hospitals and nurses as the domain of their pattern recognition. Discovery confirmed they work faster than newcomers, and this advantage is undocumented. The inference is that the speed differential is in candidate pre-selection, not in parsing speed (both senior and junior coordinators read the same free-text requests) or submission speed (both use the same ServiceNow interface). The AI Candidate Ranker is a direct attempt to replicate this Zone 3 advantage systemically.

**Confidence**: Medium. Supported by discovery language but never confirmed with a direct time breakdown per coordinator tier.

**Referenced in metrics**: M2

---

## A19 — Historical shift outcome records in ServiceNow are sufficient to cold-start the AI candidate ranker

**Assumed value**: At least 3–6 months of coordinator selection records with outcomes (hospital accepted / rejected per candidate submission) are accessible in ServiceNow — estimated at 8,000–16,000 labeled examples at current volume (A4: ~184 fills/day × 90–180 working days).

**Reasoning**: At $14M revenue and ~184 fills/day (A4), MedFlex generates substantial historical volume. Even if only 50% of outcome records are structured enough to serve as labeled training examples (consistent with the "raw format" characterization in discovery), the corpus is sufficient to cold-start a supervised ranking model. The critical unknown is whether coordinator selection records link the specific candidate selected to the submission outcome — A12 confirms hospital acceptance/rejection events exist, but whether the full selection + outcome tuple is available per match is unconfirmed. If data is insufficient, the MVP ranker uses a rule-based scoring approach (T4) while accumulating labeled data from live coordinator review decisions.

**Confidence**: Low-Medium. A12 confirms outcome data exists; completeness and tuple structure are unknown. Key dependency for the Phase 2 ML ranker upgrade.

**Referenced in metrics**: M2, M5

---

## A20 — The same nurse can be submitted to multiple MedFlex requests simultaneously with no internal reservation lock

**Assumed value**: When multiple coordinators process concurrent requests, the same nurse can be independently selected and submitted to different hospitals in the same session. There is no internal reservation mechanism or nurse-lock in ServiceNow that prevents duplicate submissions before hospital acceptance.

**Reasoning**: Marcus explicitly confirmed MedFlex submits the same nurse to multiple hospitals and deconflicts post-acceptance: "we submit a couple of nurses to different hospitals, and then as soon as someone is confirmed, then we remove it from other hospital submission." While described in the context of cross-agency competition, the same dynamic applies internally — 8 coordinators processing the queue concurrently can independently select the same qualified nurse for different shift requests. This creates internal race conditions (A9 is primarily framed as cross-agency; A20 captures the internal version) that manifest as MT-5.4-style conflicts or as wasted submissions after a nurse is already committed.

**Confidence**: Medium. Internal race condition is inferred from the confirmed cross-agency model; not directly confirmed for intra-MedFlex submissions.

**Referenced in metrics**: M4

---

## A21 — FDE engagement delivery cost: ~$15,000/week all-in

**Assumed value**: The 8-week engagement build cost is approximately $15,000 per week all-in (FDE team time + platform overhead + tooling), totaling ~$120,000 for the full engagement.

**Reasoning**: Standard small-team FDE delivery model for a specialized AI sprint (2 FDE engineers + engagement management overhead). Used as the basis for per-JtD build cost estimates in TCO calculations: JtD-1 ~$30K (2 weeks), JtD-2 ~$45K (3 weeks), JtD-3 ~$60K (4 weeks), JtD-4 ~$15K (1 week), JtD-5a ~$15K (1 week). Overlapping parallel builds keep total within the 8-week budget. MedFlex-specific contract terms are unknown.

**Confidence**: Low-Medium. Reasonable for a small specialized AI delivery engagement; actual FDE contract terms and team composition are unconfirmed.

**Referenced in metrics**: TCO calculations in `specs/volume-×-value-analysis.md`

---

## A22 — Claude Sonnet API cost model per matching case

**Assumed value**: Claude Sonnet (claude-sonnet-4-6) pricing: $3.00/M input tokens, $15.00/M output tokens. Per-case token estimates: JtD-1 parsing ~1,500 input / 400 output tokens ($0.011/case); JtD-2 search ~500 input / 200 output tokens ($0.005/case); JtD-3 ranking ~2,000 input / 600 output tokens ($0.015/case).

**Reasoning**: Based on published Anthropic pricing as of May 2026 for Sonnet models. Per-case token estimates derived from domain analysis: JtD-1 requires system prompt (~1,300 tokens) + shift request (~200 tokens) + context + structured JSON output; JtD-2 orchestrates structured ServiceNow API tool calls with minimal LLM text; JtD-3 requires multi-candidate comparison with explanation generation. Actual token usage will vary with prompt engineering, caching, and context window size.

**Confidence**: Medium on pricing (published rates); Medium-Low on per-case token estimates (validated through mock testing, not live runs).

**Referenced in metrics**: TCO calculations in `specs/volume-×-value-analysis.md`

---

## A23 — ServiceNow REST API rate limit: ≥60 requests/minute per MedFlex instance

**Assumed value**: MedFlex's ServiceNow enterprise instance supports at least 60 API requests per minute without throttling, sufficient for the combined JtD-1 queue poll + JtD-2 profile fetch + JtD-3 preference history read workload at 184 shifts/day.

**Reasoning**: Standard ServiceNow enterprise tiers support 60–300 requests/minute depending on instance size and licensing. At 184 fills/day across an 8-hour active window, peak throughput is ~0.64 requests/second for queue polls, well under even the conservative 60 req/min floor. The assumption becomes binding only if MedFlex runs a constrained developer-tier instance or if multi-agent polling creates burst spikes. Circuit breaker logic (20% error rate in 5-minute window) provides a safety valve if this assumption fails.

**Confidence**: Low. MedFlex IT must confirm instance tier and API rate limit configuration before agent integration is finalized.

**Referenced in metrics**: Integration contracts in `specs/04a-capability-spec-match-selection.md`, `specs/04b-capability-spec-shift-intake-parsing.md`

---

## A24 — ServiceNow table and field naming convention for MedFlex instance

**Assumed value**: Shift requests are stored in table `u_shift_request`; nurse profiles in `sys_user` with custom fields prefixed `u_`; hospital preference history in `u_nurse_hospital_outcome` with fields `u_nurse_id`, `u_hospital_id`, `u_outcome` (ACCEPTED/REJECTED), and `u_placement_date`.

**Reasoning**: ServiceNow custom tables use the `u_` prefix convention by platform standard. The table names and field names used throughout the capability specs are informed estimates based on standard ServiceNow healthcare staffing implementations. Actual table names depend on how MedFlex's ServiceNow admin originally configured the instance — these may differ significantly. All integration contracts in 04a and 04b must be validated against MedFlex's actual ServiceNow schema before development begins.

**Confidence**: Low. Requires MedFlex IT or ServiceNow admin confirmation. Invalidating this assumption would require updating all endpoint paths and field mapping logic in both specs before any integration code is written.

**Referenced in metrics**: Integration contracts in `specs/04a-capability-spec-match-selection.md`, `specs/04b-capability-spec-shift-intake-parsing.md`

---

## A25 — Rule-based ranker scoring weights (Wave 1 MVP)

**Assumed value**: The composite_score formula weights are: credential_match = 0.40, availability_confidence = 0.30, proximity_score = 0.20, hospital_preference_weight = 0.10. Weights sum to 1.00. These are configurable parameters stored outside model code, not hardcoded constants.

**Reasoning**: Credential compliance is non-negotiable (disqualifies candidates outright if failed, then highest ranking weight among eligible candidates). Availability confidence is second because a credentialed but unavailable nurse produces a no-show (A9). Proximity reduces travel cost and latency risk. Hospital preference is weighted lowest because data is sparse at launch (A12: partial coverage). The 40/30/20/10 split reflects the relative cost of getting each dimension wrong: a credential mismatch produces a regulatory incident; an availability mismatch produces a no-show; a proximity mismatch wastes cost; a preference mismatch produces mild hospital friction. Weights should be reviewed with coordinators before launch and recalibrated after Wave 1 data accumulates (A19 labeled feedback store).

**Confidence**: Low. Initial weights derived from first-principles reasoning, not coordinator validation or historical data. Senior coordinator review before Wave 1 launch is required to validate or adjust. Key dependency for the Phase 2 ML ranker upgrade where weights become learned parameters.

**Referenced in metrics**: `specs/04a-capability-spec-match-selection.md` (Activity Catalog MT-3.2, Context Engineering)

---

## A26 — Geocoding provider: Google Maps API with ZIP-level caching

**Assumed value**: Proximity scoring (MT-3.1c) uses the Google Maps Geocoding API to convert nurse ZIP codes to latitude/longitude coordinates. Haversine formula calculates distance to shift location. Geocoded lat/lng is cached per ZIP code for 24 hours to minimize API calls. API key stored in env var `GOOGLE_MAPS_API_KEY`.

**Reasoning**: Google Maps Geocoding is the industry-standard geocoding provider with >99% uptime and coverage for all US ZIP codes. ZIP-level caching (not address-level) is appropriate because nurse location precision is ZIP code only (nurse profiles store ZIP, not street address). At 184 fills/day with ~5 candidates each (~920 proximity calculations/day), and with ZIP-level caching reducing repeat calls, actual API calls are well within Google Maps free tier limits (40,000/month). Proximity score falls back to neutral 0.50 if geocoding API is unavailable — shortlist generation is never blocked.

**Confidence**: Medium. Geocoding at ZIP level is technically straightforward; the assumption is that MedFlex can obtain a GOOGLE_MAPS_API_KEY and that nurse profile ZIP codes are populated in ServiceNow. If ZIP codes are missing from nurse profiles, the proximity component defaults to 0.50 for all candidates (neutral fallback, not an error).

**Referenced in**: `specs/04a-capability-spec-match-selection.md` (§7.4 Google Maps Integration Contract, MT-3.1c, §8 Scoring Algorithm proximity_score breakpoints)

---

## A27 — Coordinator review UI is tech-stack-agnostic; API contract defines the interface

**Assumed value**: The coordinator review interface (Feature 3, BP4) is defined entirely by its API contract: `POST /internal/api/v1/coordinator-review`. The frontend tech stack (React, Vue, ServiceNow portal widget, or other) is not constrained by this spec. The spec defines what the interface must send and receive; the implementation team chooses the rendering layer.

**Reasoning**: The FDE engagement delivers the backend pipeline (parser, ranker, submission agent) and the API contract for the coordinator review step. The coordinator UI implementation may be done by MedFlex's internal IT team, a separate contractor, or as a ServiceNow portal extension — none of these choices affect the backend pipeline behavior. Constraining the tech stack in the spec would introduce unnecessary dependencies on MedFlex internal IT decisions. The API contract (HTTP 409 on duplicate, HTTP 422 on missing low_confidence_acknowledged, JWT auth, review_duration_seconds computed server-side) is the stable interface; the UI is a consumer of that contract.

**Confidence**: High. The API-contract-as-interface pattern is standard and does not depend on any MedFlex-specific assumption. Risk materializes only if MedFlex's IT environment has a hard constraint on API consumption (e.g., ServiceNow-only tooling) — in that case, the internal API becomes a ServiceNow scripted REST API, but the contract fields remain identical.

**Referenced in**: `specs/04a-capability-spec-match-selection.md` (§7.5 Internal Coordinator Review API, §5 Autonomy Matrix BP4 boundary)

---

## A28 — Ranker labeled feedback stored in ServiceNow `u_ranker_feedback`

**Assumed value**: Every coordinator review decision (approve, edit, or escalate) is logged to a ServiceNow custom table `u_ranker_feedback` with the following fields: `u_feedback_id` (UUID, idempotency key), `u_shift_request_id`, `u_shortlist_json` (immutable snapshot of the ranked shortlist presented to coordinator), `u_selected_nurse_id`, `u_coordinator_edited` (boolean: true if coordinator changed the top-ranked selection), `u_submission_outcome` (enum: ACCEPTED / REJECTED / PENDING — updated by JtD-5a when hospital responds), `u_review_timestamp` (ISO 8601 UTC).

**Reasoning**: The Phase 2 ML ranker upgrade (T4) requires a labeled training corpus of coordinator decisions and submission outcomes — this is the A19 data dependency. `u_ranker_feedback` is the accumulation mechanism. Storing it in ServiceNow (rather than a separate database) keeps all engagement data in MedFlex's existing system of record, avoids a new data store dependency, and makes the feedback data accessible to MedFlex's IT team without additional infrastructure. The `u_shortlist_json` immutable snapshot is essential — the training signal is which candidate the coordinator chose *from the shortlist that was shown*, not which candidate was theoretically best. Without the snapshot, the training corpus cannot be reconstructed accurately after ranker versions change.

**Confidence**: Medium. ServiceNow custom table creation is a standard admin operation (A24 table naming convention applies). The risk is that `u_submission_outcome` must be updated by JtD-5a when hospital response arrives — this creates a cross-JtD write dependency that must be maintained in the integration layer. If JtD-5a is not built (Feature 5 deferred), `u_submission_outcome` stays PENDING for all records; the feedback corpus is still useful for coordinator edit-rate analysis but cannot support full outcome-based ranker training until JtD-5a ships.

**Referenced in**: `specs/04a-capability-spec-match-selection.md` (§7.3 RankerFeedback Write Contract, MT-3.6, §9 Compounding Roadmap Wave 2, §3.6 RankerFeedback entity data model)

---

## A29 — A ServiceNow non-production (staging) instance with representative data exists for pre-launch validation

**Assumed value**: MedFlex has or can provision a ServiceNow sandbox or non-production instance that (a) runs the same schema as production (`u_shift_request`, `u_parsed_shift_requirement`, and related tables per A24), (b) is pre-loaded with anonymized historical shift request records suitable for the 200-record A10 validation corpus, and (c) allows test writes without affecting production nurse profiles or live shift queue.

**Reasoning**: The validation plan (`specs/07-validation-plan.md`) requires running all 15 tests — including dead-letter queue tests, advisory lock race condition tests, and the 200-record corpus accuracy run — before touching the production instance. Without a staging environment, pre-launch testing either risks corrupting production data (unacceptable) or cannot be done at all (blocks the A10 accuracy check that gates launch). Most enterprise ServiceNow instances have at least a sub-production environment; this assumption is that MedFlex's does too and that a ServiceNow admin can provision test data.

**Confidence**: Medium. Marcus is the sole point of contact; MedFlex's ServiceNow admin and IT setup are unknown. If no staging environment exists, the mitigation is to create one: ServiceNow supports cloning a sub-production instance from production (standard admin operation). Worst case: build and test against a developer sandbox with synthetic data, then validate the A10 corpus run against production in a controlled batch during off-hours before go-live.

**Referenced in**: `specs/07-validation-plan.md` (§2 Scope, HP-05 test steps, EC-01 test notes)
