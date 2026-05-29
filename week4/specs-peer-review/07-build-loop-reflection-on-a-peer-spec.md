# Reflection: Build Attempt vs. Peer Review — Spec 04a

## What the build attempt revealed

My 8 clarification questions surfaced **implementation-level blockers**: language/framework, persistence layer type, coordinator queue mechanism, credential CSV schema, fuzzy-match algorithm, LOCATION_INCOMPLETE detection logic, POSSIBLE_MISSED_CREDENTIAL heuristics, and which fields count as "required" for the −0.25 null deduction. These are the questions a builder hits *the moment they try to write the first line of code* — not theoretical concerns, but hard stops.

One gap the build exposed that the peer review missed entirely: **the Matching Agent has no outbound integration contract**. The spec defines contracts for ServiceNow, LLM, and coordinator queue — but Step 6 just says "Pass ShiftRequirement to Matching Agent" with zero interface definition. API call? Queue message? Function call? That's as undefined as the gaps the review did flag. The review catalogued the inputs and overlooked the primary output.

A second miss: **overnight shifts**. Example 2 shows start 20:00, end 04:00. There's no `shift_date_end` field and no rule for times that cross midnight. Silent data corruption risk.

A third miss: **language and runtime**. The review never asked. This is the first question any engineer asks before writing anything.

## What the peer review caught well

The review was strongest on **integration contract depth**: missing webhook payload schema, missing LLM API endpoint and auth header format, rate-limit queue mechanism, coordinator queue error handling. These are real production blockers I didn't surface because the build attempt stops before integration wiring. The review also caught `raw_text` sanitization (>10,000 chars handling, encoding), retry behavior (what actually changes on a second malformed-JSON attempt — the answer is: nothing, which means it's effectively a wasted call), and the missing cross-cutting concerns: timezone handling for shift times, concurrency, logging schema, data retention, and monitoring/alerting.

## False positives in the peer review

Three flags were overcalls:

1. **"Missing idempotency handling"** — The spec handles idempotency explicitly via `servicenow_ticket_id` deduplication enforced at both application and DB level. That *is* idempotency for a webhook receiver.

2. **"`parse_confidence_flags` not exhaustive"** — Every flag value is derivable from the spec: twelve distinct values across the processing steps and edge cases table. They're scattered, not missing. The right note is "consolidate into one enumeration" — not "open-ended."

3. **"Cache invalidation not specified"** — Assumption A2 explicitly documents this as an accepted tradeoff: stale codes until restart. Flagging it as a buildability gap ignores that the spec made a deliberate choice.

4. **"No acceptance criteria"** — The two worked examples with exact expected JSON output, plus the edge cases table, are functional acceptance criteria for an MVP spec. "No Gherkin" ≠ "no criteria."

## Net assessment

The peer review was broader but caught some non-issues. The build attempt was narrower but found the Matching Agent contract gap — a structural hole in the spec that the review didn't notice because it was cataloguing what was *present but incomplete*, not what was *absent entirely*. Both lenses are needed: the review catches depth gaps in documented integrations; the build attempt catches missing integrations the author forgot to document.
