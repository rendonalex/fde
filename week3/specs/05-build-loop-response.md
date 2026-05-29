# Approach:

When I built and ran the tests, all 29 tests passed (see output from claude build in Deliverable #9). This created a significant challenge: with no test failures to investigate, I had no clear starting point for the build diagnosis. The program materials did not specify how to proceed in this scenario, particularly in the context of a build-loop diagnosis. How can I identify "builder misread" issues when all tests pass? Under exam time constraints, manually parsing the entire codebase against the specification to find discrepancies is impractical.

My solution was to ask Claude to analyze the BUILD spec for ambiguities, which produced a comprehensive report identifying spec and design gaps. This approach proved effective for uncovering issues that weren't caught by the test suite, but it raises questions about the intended diagnostic workflow. While this investigative process is valuable and would be highly relevant in real-world scenarios, it requires significantly more time than was available in exam conditions. The workflow of test failure → code investigation → spec verification is intellectually engaging and mirrors actual debugging practices, but the all-tests-passing scenario requires a different methodology that would benefit from explicit guidance.

# Prompt to identify ambiguities in the specs

I want you to write a detailed BUILD SPEC (not implementation code) for the “shift-intake-parsing” capability described in the `specs/04b-capability-spec-shift-intake-parsing.md` file.

A build spec should include:
1. Feature overview and purpose
2. Detailed logic flow with decision points
3. API contracts (request/response formats)
4. Data models and state transitions
5. Edge cases and error handling
6. Acceptance criteria and test scenarios
7. Dependencies and integration points

Use ONLY the information in specs/04b-capability-spec-shift-intake-parsing.md to write this spec.

CRITICAL INSTRUCTION: If you encounter ANY ambiguity or missing information in specs/04b-capability-spec-shift-intake-parsing.md that prevents you from writing a complete, unambiguous build spec, STOP immediately and list all the ambiguities you found. Do NOT make assumptions or invent details.

Your goal is to identify gaps in specs/04b-capability-spec-shift-intake-parsing.md, not to fill them in yourself.


# Build Spec Analysis — Shift Intake Parsing (JtD-1)

> Source spec: `specs/04b-capability-spec-shift-intake-parsing.md`
> Purpose: Identify ambiguities and gaps that prevent writing a complete, unambiguous build spec.

---

## Summary

| Category | Count |
|---|---|
| Direct contradictions (two statements that cannot both be true) | 3 (items 1, 3, 12) |
| Missing integration contracts (referenced but never specified) | 4 (items 4, 5, 6, 7) |
| Missing env var / configuration definitions | 2 (items 7, 8) |
| Ambiguous behavior requiring a judgment call | 6 (items 2, 9, 10, 11, 13, 14) |
| Lifecycle ownership gaps | 2 (items 4, 15) |

**Recommendation**: Resolve items 1, 2, 3, 4, 5, and 6 before writing a build spec — these directly determine observable system behavior. Items 7–15 can be resolved with short answers; items 1–6 require design decisions.

---

## Ambiguity 1 — HTTP 409 on `PARSING` PATCH: Direct Contradiction (§7.2)

The same section gives mutually exclusive instructions:

- **Error table**: `HTTP 409: status already set to target value → treat as success (idempotent); do not retry`
- **Critical note**: `PATCH to PARSING is the advisory lock mechanism. If this write fails, the agent must NOT proceed to call the LLM — it must skip the record`
- **Idempotency note**: `a second PATCH of the same sys_id to PARSING returns HTTP 409 — treated as success. The agent does not double-process the same record.`

These cannot all be true simultaneously. If Agent A holds the lock and Agent B tries to PATCH to PARSING:
- Agent B gets HTTP 409
- Error table says: treat as success → proceed to LLM call
- Critical note says: do NOT proceed → skip

**Question**: When Agent B receives HTTP 409 on the PARSING PATCH, does it proceed to the LLM call or skip the record? The spec says both.

---

## Ambiguity 2 — Confidence Score Formula: Field Count Mismatch (§4 vs §8.4)

**§4 MT-1.4a**:
```
confidence_score = min(specialty_confidence, datetime_confidence, location_confidence, credential_confidence)
```
→ 4 terms, singular `datetime_confidence`

**§8.4**:
```
confidence_score = min(specialty_confidence, datetime_start_confidence, datetime_end_confidence, location_confidence, credential_confidence)
```
→ 5 terms, split datetime fields

**Question**: Is the formula a 4-field min or a 5-field min? Which section is authoritative?

---

## Ambiguity 3 — `location_confidence` for Ambiguous Match: Three Conflicting Values

| Section | Scenario | Value |
|---|---|---|
| §8.3 | `"St. David's"` matches multiple entries | `0.30` |
| §8.4 scoring rules | partial name match with ambiguity between two or more hospitals | `0.50` |
| §8.5 Example 2 | `"St. David's Saturday morning"` — ambiguous | `0.50` |
| §8.5 Example 3 | `"St. David's"` — ambiguous | `0.30` |

Examples 2 and 3 have materially identical ambiguity scenarios ("St. David's" without North/South) but produce different values. §8.3 (the rule) and §8.4 (the scoring table) directly contradict.

**Question**: For an ambiguous partial hospital name match, what value does the builder use — 0.30 or 0.50?

---

## Ambiguity 4 — Reconciliation Cron: Referenced Three Times, Never Defined

Referenced at:
- §7.3: `The dead-letter queue reconciliation cron will re-attempt the write and trigger JtD-2 once confirmed`
- §7.5: `ops must detect via reconciliation cron (HUMAN_REVIEW records with no matching HITLQueueEntry after >5 minutes)`
- §10.3 Failure Mode 2: `reconciliation cron retries the POST every 5 minutes`

Missing from §4 (Activity Catalog), §5 (Autonomy Matrix), §6 (System Inventory), and §7 (Integration Contracts).

**Questions with no answers in the spec**:
- Is the reconciliation cron a separate process or part of the main agent loop?
- What is its exact schedule? (§10.3 says "every 5 minutes" — is that the only task interval?)
- Does one cron handle both DLQ retries AND stale-PARSING detection, or are these separate?
- What is the stale-PARSING threshold? (§7.5 says ">5 minutes" — this is the only hint)
- When the cron re-attempts a DLQ write and succeeds, does it then also emit the `shift_parsed` event?
- Does the cron PATCH the `ShiftRequest` status as part of its retry flow?

---

## Ambiguity 5 — Event Bus: "Or" Is Ambiguous, Interface Undefined

**§4 MT-1.7**: `emit shift_parsed event to trigger JtD-2 candidate search` via `Internal event bus or ServiceNow workflow trigger`

**§6**: `Internal Event Bus: Write (emit shift_parsed event); Internal service auth; Shared platform component (built with JtD-2 integration)`

No integration contract for the event bus exists in §7. There is no endpoint, no event schema, no authentication spec, no payload definition, no error handling.

**Questions**:
- Is it an event bus OR a ServiceNow workflow trigger? How does the builder choose?
- What is the `shift_parsed` event schema?
- What endpoint does it post to?
- What authentication mechanism?
- What error handling applies?

---

## Ambiguity 6 — Dead-Letter Queue: Mentioned Four Times, Schema Never Defined

Referenced at §7.3, §7.5, §10.3 Failure Mode 2. Never defined in §3 (Data Models), §4, §6, or §7.

**Questions with no answers**:
- What is stored in the DLQ entry? (the full LLM extraction result? the failed POST body? the `u_shift_request_id` reference?)
- Is this an in-process data structure, a database table, or a separate service?
- What is the DLQ entry schema?
- When the reconciliation cron re-attempts a DLQ write, does it re-call the LLM or use the stored extraction result?

---

## Ambiguity 7 — Ops Alert Channel: "Configured at Deployment" With No Interface

**§6**: `Ops Alert Channel: Write; Configured at deployment; Week 1 infrastructure setup`

Referenced at §4 MT-1.5, §5 Category 2 (two triggers), §7.1 (ServiceNow unreachable), §10.3 (DLQ > 10 items).

**Questions**:
- What is the interface? (HTTP webhook, Slack API, email, PagerDuty?)
- What is the alert payload format?
- Is this a single env var pointing to a webhook URL, or a more complex integration?
- Without this defined, the builder must invent an alert mechanism from scratch.

---

## Ambiguity 8 — HITL Queue API Base URL: Not Specified

**§7.5**: Endpoint is `POST /internal/api/v1/hitl-queue` but the base host and port are never stated.

The spec names `SYSTEM_SERVICE_TOKEN` as the auth credential but does not name the env var for the base URL (e.g., `HITL_SERVICE_BASE_URL`).

**Question**: What env var holds the HITL service base URL? What is the default host/port for local development?

---

## Ambiguity 9 — UTC Offset: Internally Consistent But Factually Incorrect for Half the Year

**§8.1 Important Rules**: `Assume US Central Time (UTC-5) if no timezone specified`

US Central Standard Time (CST) = UTC-6. US Central Daylight Time (CDT) = UTC-5.

The spec is internally consistent (all examples follow UTC-5) but UTC-5 is only correct ~7 months of the year (March–November). From November–March, Central Time is UTC-6.

**Question**: Should the agent always use UTC-5 (follow spec literally), or should it apply the seasonally-correct offset for the parse date?

---

## Ambiguity 10 — `UNKNOWN_SPECIALTY` Failure Reason: In Enum, Never Assigned by Routing Logic

**§3.3**: `HITLQueueEntry.u_failure_reason` enum includes `UNKNOWN_SPECIALTY`

**§6 Data Dependencies**: `If [SpecialtyCode dict unavailable]: routes to HUMAN_REVIEW with UNKNOWN_SPECIALTY`

But §3.1 transition rules, §4, §5, and the edge cases never reference `UNKNOWN_SPECIALTY` in routing logic. Edge Case 6 (LLM returns `UNKNOWN` specialty code) routes to BP1 with `failure_reason = LOW_CONFIDENCE`.

**Questions**:
- Is `UNKNOWN_SPECIALTY` only emitted when the SpecialtyCode dictionary itself is unavailable at runtime?
- What does "dictionary unavailable" mean operationally? (file missing? parse error at startup?)
- If the dictionary is unavailable, should the agent halt, alert ops, and refuse to process — or process with `UNKNOWN_SPECIALTY` routed to HITL?
- This scenario is entirely absent from §4 and §10 (no failure mode covers it).

---

## Ambiguity 11 — `u_partial_parse` Content: Pre- or Post-Validation Values

**§3.3**: `u_partial_parse: the partial extraction the LLM produced before confidence threshold failure`

The phrase "before confidence threshold failure" suggests raw LLM output (pre-validation).

But the validator modifies confidence values:
- `DATETIME_IN_PAST` → sets `datetime_start_confidence = 0.00`
- Unknown specialty → caps `specialty_confidence` at 0.50
- Invalid credential → caps `credential_confidence` at 0.70

**Question**: Does `u_partial_parse` reflect (a) the literal JSON the LLM returned before any agent-side validation, or (b) the post-validation field values that drove the routing decision?

---

## Ambiguity 12 — Consecutive LLM Failure Counter Scope: Two Contradictory Definitions

**§5 Category 2**: `Alert on consecutive LLM failures: ≥ 10 consecutive LLM unavailability events`

**§7.4 Fallback**: `After 10 consecutive LLM failures (any error type): alert ops`

§5 scopes to "unavailability events" (529, timeout, 5xx).
§7.4 scopes to "any error type" (includes 400, 401, 422, 429).

**Question**: Does a 401 (invalid API key — which separately triggers an immediate halt per §7.4) also increment the consecutive failure counter? Does a 429 (rate limit — which separately triggers a retry-after wait) increment it?

---

## Ambiguity 13 — HTTP 409 on `ParsedShiftRequirement` Write: Retrieval Method Undefined

**§7.3 Error responses**: `HTTP 409: use the existing record's u_parsed_requirement_id for downstream event emission`

The 409 response body format is not defined. The agent needs `u_parsed_requirement_id` from the existing record to emit `shift_parsed`, but:
- The spec does not define whether the 409 response body contains the existing record's data
- No GET endpoint or query pattern is specified for retrieving the existing record
- The endpoint for querying `u_parsed_shift_requirement` by `u_shift_request_id` is never defined in §7

**Question**: After receiving HTTP 409 on the POST to `u_parsed_shift_requirement`, what exact API call does the agent make to retrieve the `u_parsed_requirement_id`?

---

## Ambiguity 14 — LLM Timeout Retry Count: "Retry Once" vs "529 Path = 3 Retries"

**§7.4 Timeout**: `If LLM does not respond within 30 seconds: count as one failure; retry once on 529 handling path`

**§7.4 HTTP 529**: `retry up to 3 times with exponential backoff (4s, 8s, 16s)`

"Retry once on 529 handling path" — does "once" mean one retry total (2 total attempts), or does it mean follow the full 529 policy (up to 3 retries = 4 total attempts)?

**Question**: For a timeout, is the retry budget 1 retry (2 total attempts) or 3 retries (4 total attempts)?

---

## Ambiguity 15 — `u_parsed_at` on BP1 Completion: Ownership Unclear

**§3.1 Transition rules**: `HUMAN_REVIEW → PARSED: coordinator reviews and submits corrected parse; sets u_reviewed_by, u_parsed_at`

**§3.2**: `u_parsed_at: set by agent when status transitions to PARSED`

These contradict. §3.1 says "coordinator sets" (implying the HITL service does it on behalf of the coordinator). §3.2 says "set by agent."

For the BP2 (auto-parse) path, the agent sets `u_parsed_at` before the PATCH. For the BP1 (human review) path, the human completes in the HITL UI — but the HITL service's PATCH request body to ServiceNow is never defined in §7.

**Question**: On BP1 completion, who generates and sends `u_parsed_at` — the HITL Queue service as part of the coordinator's submission, or the main parsing agent in response to a callback?
