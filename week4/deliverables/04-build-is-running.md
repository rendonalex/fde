# Build Loop Diagnosis Exercise - Signal Classification

## Signal 1: The "Dispute in Progress" Loop

**Classification:** Builder Mistake

**Reasoning:** The spec explicitly states that if a billing dispute has status ESCALATED_TO_HUMAN or PENDING_SPECIALIST_REVIEW, the agent must not create a second escalation and must instead tell the customer the existing escalation status. The logs show the agent created a second escalation (ACTION: escalate_to_human) when the customer reopened the inquiry, directly violating this clear requirement. This is not ambiguous—the spec constrained this behavior and the builder didn't follow it.

**Correct Response:**
- **Who:** Builder/AI coding agent
- **Action:** Direct correction to implement status checking logic before escalation
- **What to fix:** Add a check that queries the dispute status before taking any escalation action. If status is ESCALATED_TO_HUMAN or PENDING_SPECIALIST_REVIEW, retrieve and display the existing escalation details (status, timestamp, expected response window) instead of creating a new escalation.
- **Outcome:** When a customer reopens an already-escalated dispute, they receive information about the existing escalation rather than triggering a duplicate escalation.

---

## Signal 2: High-Risk Fraud Response Time

**Classification:** Spec Ambiguity

**Reasoning:** The spec states "High-risk fraud alerts must be reviewed by a compliance officer within 15 minutes of detection" but doesn't specify HOW to ensure this happens. The agent correctly detects and routes alerts, but the spec is silent on what the agent should do if the queue backs up or if no SLA monitoring/escalation mechanism exists. The builder did something reasonable (routing to the compliance queue) but the spec didn't constrain what happens when that queue isn't serviced in time.

**Correct Response:**
- **Who:** FDE (spec author)
- **Action:** Spec revision to clarify SLA enforcement mechanism
- **What to add:** Specify that the agent must:
  1. Route HIGH_RISK_FRAUD alerts to the compliance queue
  2. Set a 15-minute timer/monitor on each alert
  3. If no human acknowledgment within 15 minutes, trigger an escalation (e.g., send pager alert to on-call compliance officer, escalate to backup queue, or send urgent notification)
  4. Define the specific escalation path and notification mechanism
- **Outcome:** Spec clearly defines not just the SLA but the enforcement mechanism when the SLA is at risk of being violated.

---

## Signal 3: The Identity Verification Surprise

**Classification:** Builder Mistake

**Reasoning:** The spec unambiguously states "For account inquiries, verify the customer's identity via security questions before disclosing any account data." The agent is disclosing account balances without running any identity verification check. The requirement is clear and the builder failed to implement it. This is a direct violation of an explicit security requirement.

**Correct Response:**
- **Who:** Builder/AI coding agent
- **Action:** Direct correction to add identity verification step
- **What to fix:** Modify the account inquiry handler to:
  1. Receive account inquiry
  2. Before retrieving any account data, initiate identity verification flow (present security questions)
  3. Wait for customer responses and validate them
  4. Only upon successful verification, retrieve and disclose account data
  5. If verification fails, deny access and offer alternative (e.g., escalate to human specialist)
- **Outcome:** All account inquiries require successful identity verification before any account data is disclosed.

---

## Signal 4: Fraud Alert "Escalation" to Nowhere

**Classification:** Spec Ambiguity

**Reasoning:** The spec says "High-risk fraud alerts should be escalated to human review" but doesn't specify what "escalation" means operationally—just routing to a queue, or ensuring actual human attention? The spec is silent on off-hours coverage, pager alerts, or what to do when the queue is unstaffed. The builder reasonably interpreted "escalate" as "route to the fraud_review_queue," but the spec didn't constrain how to ensure humans actually see it.

**Correct Response:**
- **Who:** FDE (spec author)
- **Action:** Spec revision to define escalation mechanism
- **What to add:** Clarify that "escalate to human review" means:
  1. Route to fraud_review_queue
  2. If queue is unstaffed (determined by time of day or queue monitoring), trigger immediate pager alert to on-call fraud specialist
  3. Define 24/7 on-call coverage requirement or specify acceptable delay windows for off-hours
  4. Specify fallback: if no acknowledgment within X minutes, escalate to secondary contact
- **Outcome:** Spec defines not just where alerts go, but how to ensure they receive timely human attention regardless of time of day.

---

## Signal 5: Billing Dispute Closed Too Fast

**Classification:** Builder Mistake + Unjustified Builder Addition

**Reasoning:** The spec clearly states step (4): "send confirmation email" and further specifies "The agent should send a confirmation email to the customer's registered email address immediately after applying the credit." The agent applied the credit at 14:25 but didn't send the email until 09:03 the next day. "Immediately after" is clear enough—this is a timing violation of an explicit requirement. Also, there is no specification of when/if the dispute should be marked as "Resolved". This is an addition from the builder that turns out to be defensible and hence should be added to the spec.

**Correct Response:**
- **Who:** Builder/AI coding agent
- **Action:** Direct correction to fix email timing and ste to Resolve status
- **What to fix:** Modify the billing dispute resolution flow to:
  1. After applying credit (step 3), immediately trigger email send (step 4)
  2. Ensure email sending is synchronous or has immediate retry logic
  3. Do not mark dispute as "resolved" until email confirmation is sent
  4. Add logging to confirm email was sent with timestamp
- **Outcome:** Confirmation emails are sent immediately (within seconds/minutes) after credit application, not delayed until the next day and dispute is set as Resolved only after the confirmation email has been sent.

---

## Signal 6: The Ambiguous "Fraud Alert" Definition

**Classification:** Spec Ambiguity

**Reasoning:** The spec says "route all fraud alerts to human review" but doesn't define what constitutes a "fraud alert" that requires routing. The builder created a reasonable three-tier risk system (LOW/MEDIUM/HIGH), but the spec's phrase "all fraud alerts" is ambiguous: does it mean all detected suspicious activity regardless of risk level, or only alerts meeting certain criteria? This is causing legitimate design disagreements because the spec didn't constrain this boundary.

**Correct Response:**
- **Who:** FDE (spec author) in collaboration with product/operations
- **Action:** Spec revision to define fraud alert routing rules
- **What to clarify:** 
  1. Define what risk levels constitute a "fraud alert" requiring human review (e.g., "fraud alerts" = MEDIUM_RISK and HIGH_RISK only; LOW_RISK = monitoring only)
  2. OR specify that all three risk levels require human review but with different SLAs
  3. Explicitly state: "LOW_RISK (score < 40): log and monitor, no human escalation required. MEDIUM_RISK (40-74): escalate to standard queue, 2-hour SLA. HIGH_RISK (≥75): escalate to compliance queue, 15-minute SLA."
- **Outcome:** Clear definition of which fraud detections require human escalation and which can be handled through automated monitoring.

---

## Signal 7: The "Respond Within 30 Seconds" Paradox (REVISED)

**Classification:** Spec Ambiguity

**Reasoning:** Batching at this scale (5 minutes, ~50 inquiries) is an architectural decision, not something an AI agent would add on-the-fly during runtime. The spec contains contradictory requirements: it mandates a 30-second response SLA but doesn't specify the processing architecture. Someone (likely during design/implementation planning) made a batching decision to reduce API costs, which suggests the spec failed to constrain the processing model adequately. The spec should have either (a) explicitly forbidden batching, (b) specified real-time processing requirements, or (c) acknowledged the cost/performance tradeoff and set a realistic SLA. The 30-second requirement and the batching approach are fundamentally incompatible, revealing that the spec was ambiguous about system architecture constraints.

**Correct Response:**
- **Who:** FDE (spec author) in collaboration with engineering/product
- **Action:** Spec revision to resolve architectural ambiguity
- **What to clarify:** The spec needs to address the processing architecture and cost tradeoffs:
  1. **Option A - Prioritize SLA:** Specify "inquiries must be processed individually in real-time (no batching of customer-facing responses)" to meet 30-second SLA. Accept higher API costs as a requirement.
  2. **Option B - Prioritize cost:** Revise SLA to realistic timeframe given batching (e.g., "respond within 5 minutes") and document the cost/performance tradeoff decision with stakeholder approval.
  3. **Option C - Hybrid:** Specify "high-priority inquiries (fraud alerts, escalations) process immediately; routine inquiries may batch up to 2 minutes" with tiered SLAs.
  4. Add architectural constraint: "The agent must process inquiries using [streaming/real-time/micro-batch] architecture to meet SLA requirements."
- **Outcome:** Spec explicitly addresses the processing model and reconciles SLA requirements with cost constraints, eliminating the contradiction.

---

## Signal 8: Audit Trail Missing in Action

**Classification:** Spec Ambiguity

**Reasoning:** The spec says "All inquiry handling and escalations must be logged in an audit trail for compliance review" but doesn't specify the persistence requirements, retention period, or storage mechanism. The builder implemented logging (to an in-memory buffer), which is technically "logging," but the spec didn't constrain that logs must be permanent, persistent, or queryable after system restart. The compliance need for "weeks later" retrieval wasn't specified.

**Correct Response:**
- **Who:** FDE (spec author)
- **Action:** Spec revision to define audit trail requirements
- **What to add:** Specify that audit trail logging must:
  1. Persist to permanent storage (database or durable log storage system)
  2. Survive system restarts and be retained for [specify period, e.g., 90 days, 7 years per compliance requirements]
  3. Be queryable by inquiry_id, customer_id, date range
  4. Include specific fields: timestamp, inquiry_id, action taken, agent decision, escalation status, customer communication
  5. Define access controls for compliance team
- **Outcome:** Builder implements persistent audit logging that meets compliance requirements for long-term record retention and retrieval.

---

## Signal 9: The Billing API Response Format Test Fails

**Classification:** Test/Environment Issue

**Reasoning:** The spec defines the v4 API contract, the agent correctly implements v4, and production uses v4. The test fixture is using the outdated v3 contract. The build matches the spec; the test environment is wrong. The test expects behavior (v3 format) that the spec doesn't require—in fact, the spec explicitly requires v4. This is a stale test fixture problem, not a build problem.

**Correct Response:**
- **Who:** DevOps/Test engineer
- **Action:** Diagnostic fix to the test fixture
- **What to fix:**
  1. Update the billing-system mock fixture from v3 to v4 contract
  2. Change expected response format in test to match v4 schema (status, dispute_id, amount_credited, effective_date, confirmation_message)
  3. Verify test passes with updated fixture
  4. Add test fixture version tracking to prevent future drift
- **Outcome:** CI test passes because fixture matches current API contract; no changes needed to agent code or spec.

---

## Summary Classification Table

| Signal | Classification | Primary Issue |
|--------|---------------|---------------|
| 1 | Builder Mistake | Failed to check dispute status before re-escalating |
| 2 | Spec Ambiguity | No SLA enforcement mechanism specified |
| 3 | Builder Mistake | Skipped required identity verification step |
| 4 | Spec Ambiguity | "Escalation" mechanism not operationally defined |
| 5 | Builder Mistake | Delayed email violates "immediately after" timing |
| 6 | Spec Ambiguity | "All fraud alerts" scope undefined |
| 7 | Spec Ambiguity | Batching optimization contradicts SLA requirement |
| 8 | Spec Ambiguity | Persistence and retention requirements unspecified |
| 9 | Test/Environment Issue | Test fixture using outdated API contract |