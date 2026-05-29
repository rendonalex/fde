# W3 Build-Loop Exercise — MedFlex Compliance Verification Agent (Brainfuck Edition)<a id='0'></a>

**Engagement:** MedFlex Agentic Transformation
**FDE:** Viachaslau Balashevich
**Spec graded:** D4b — Capability Spec: Compliance Verification Agent (`04b-capability-spec-compliance.md`)
**Language:** [Brainfuck](https://en.wikipedia.org/wiki/Brainfuck) — 8 commands, Turing-complete, 30 000-cell tape



1. [Signal 1: Federal credential lookup key](#1)
2. [Signal 2: Tier 2 applied to all credentials](#2)
3. [Signal 3: Nurse expiry alert output](#3)
4. [Signal 4: Renewal-pending case hard-blocked](#4)
5. [Signal 5: Date-bound periodic reverification test](#5)
6. [Signal 6: Compliance queue record mutation on re-check](#6)
7. [Signal 7: SLA clock timezone undefined](#7)
8. [Signal 8: Tier 2 REVOKED with no Linda notification](#8)
9. [Reflection](#9)

---

## [Signal 1 — Federal credential lookup key](#0)<a id='1'></a>

**Code (from `compliance_freshness.bf`):**

```brainfuck
Memory layout:
  [0] is_federal_cred    (0 = state-level,  1 = federal-level e.g. BLS OIG ACLS)
  [1] facility_state     (encoded: 1=TX 2=CA 3=FL 4=NY 5=WA)
  [2] lookup_key         (state_code passed to state_cadence_interval query)
  [3] scratch

,>,              read is_federal_cred into [0], facility_state into [1]

BUG: always copies facility_state directly into lookup_key -- ignores [0] entirely
<[->+<]          would zero [0] IF [0] were the source... but pointer is at [1]
>[->+<]          copy [1] into [2] unconditionally -- no federal check performed

>>>.             output lookup_key  (always a state code, never FED=0)

SHOULD BE:
  <[                     if is_federal_cred != 0
    >[-]>[-]<<           zero [1] and [2]  (lookup_key = 0 = FED)
    [-]                  zero [0] to exit loop (one iteration only)
  ]
  >[->+<]                else copy facility_state into lookup_key
```

**Spec context (Sections 5.1, 5.2, 5.3):**

Section 5.2 SQL schema: `state_code VARCHAR(3) NOT NULL -- 2-letter US state code, or 'FED' for federal-level`.

Section 5.1 Credential Catalog: BLS_CERT, ACLS_CERT, OIG_EXCLUSION_CHECK, FLU_VACCINATION — classified `FED` in the "Federal or state-level" column.

Section 5.3 step 2: *"`state_cadence_interval[facility_state][credential_type_code]`"* — no carve-out for federal credential types.

**Classification:** spec gap

**Rationale (1 sentence):** Section 5.3 specifies `facility_state` as the lookup key without carving out an exception for FED-level credentials, but the schema and catalog in Sections 5.1–5.2 clearly imply `FED`-keyed rows — the algorithm and the data model are inconsistent, and the builder followed the algorithm as written.

**Response (2–4 sentences):**

The spec has a missing branch in Section 5.3 step 2. I am adding: *"If `credential_type_code` is in the federal credential set (BLS_CERT, ACLS_CERT, NIH_STROKE_CERT, OIG_EXCLUSION_CHECK, FLU_VACCINATION), use `state_code = 'FED'` as the lookup key; otherwise use `facility_state`."* In Brainfuck terms: test `[0]` first and zero out `[1]` (encoding FED as 0) before the copy. Until this ships, every OIG and BLS freshness check returns `CADENCE_RULE_MISSING` and escalates to Linda — fix before pilot run.

---

## [Signal 2 — Tier 2 applied to all credentials](#0)<a id='2'></a>

**Code (from `tier2_verification.bf`):**

```brainfuck
Memory layout:
  [0] cred_count          (number of credentials to verify)
  [1] cred_type           (ASCII code of current credential. RN_LICENSE = 82 = 'R')
  [2] run_tier2_flag      (1 = call state regulatory API, 0 = skip)
  [3] api_result          (0=SKIPPED 1=CURRENT 2=REVOKED 3=INACTIVE 4=NOT_FOUND 5=API_ERROR)
  [4] scratch

,                read cred_count into [0]
[                loop over each credential
  ,>             read cred_type into [1]

  BUG: unconditionally sets run_tier2_flag = 1 for every credential type
  >+<            [2] = 1  -- no check whether [1] == 82 (RN_LICENSE)

  SHOULD CHECK cred_type == 82 before setting flag:
    subtract 82 from [1]: ----------------------------------------------------------------------------------  (×82 minus signs)
    >+<  only if result == 0

  >[             if run_tier2_flag
    call_state_regulatory_api: ,>>>.<        read result, store, output
    [-]           clear flag
  <]

  <-             decrement cred_count
]
```

**Spec context (Section 6.2):**

> "Tier 2 is applied only to `RN_LICENSE` for the MVP. Future extension to other credential types requires an API integration per credential type — out of scope for Phase 1."

**Classification:** builder misread

**Rationale (1 sentence):** Section 6.2 explicitly restricts Tier 2 to `RN_LICENSE` (ASCII 82); the builder's loop sets `run_tier2_flag = 1` unconditionally for every credential in the input, including BLS, ACLS, OIG, and others that have no regulatory API defined.

**Response (2–4 sentences):**

State regulatory APIs do not expose endpoints for BLS or OIG credentials — calls for non-`RN_LICENSE` types return `NOT_FOUND` or hard errors, cascading spurious `ESCALATE_LINDA` results. Before setting `[2] = 1`, subtract 82 from `[1]` and only proceed to the Tier 2 path if the result is zero. Cells for non-`RN_LICENSE` types should write `[3] = 0` (SKIPPED) and advance the loop. Section 6.2 is the constraint; do not extend Tier 2 scope without a spec change.

---

## [Signal 3 — Nurse expiry alert output](#0)<a id='3'></a>

**Code (from `expiry_alert_handler.bf`):**

```brainfuck
Memory layout:
  [0] nurse_id            (encoded reference)
  [1] credential_code     (encoded)
  [2] days_until_expiry   (integer)
  [3] output_channel      (1 = audit_log only,  2 = audit_log + linda_queue)
  [4] scratch

,>,>,>,          read nurse_id, credential_code, days_until_expiry, output_channel

write ExpiryAlert object to audit_log:
>+<              set audit_log_write_flag
>[               write AuditLogEntry EXPIRY_ALERT_EMITTED
  ..             output nurse_id + credential_code fields
  [-]
]

write to Linda compliance surface (correct -- surfaces in queue):
>>+<<            set linda_queue_flag
>[               write expiry alert to Linda queue record
  .              output days_until_expiry
  [-]
]

BUG: extra block below -- sends email directly to nurse (not in agent scope)
>+++<            encode nurse_email_send = 3
>[               call nurse notification path
  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  +++++++++++++++++++.  output 'A' (beginning of email body ASCII)
  [-]            clear channel
]
```

**Spec context (Sections 1, 9):**

Section 1 "What this agent owns": *"Emitting expiry alerts for credentials expiring within 30 days."* Section 9 Periodic Re-Verification: *"Emit ExpiryAlert → Write AuditLogEntry."* No mention of nurse notification. Section 15 Out-of-Scope: nurse-facing communication is not owned by this agent.

**Classification:** unjustified implementation choice

**Rationale (1 sentence):** The spec defines "emit expiry alert" as creating an `ExpiryAlert` record and writing an `AuditLogEntry` — the extra block that encodes `nurse_email_send = 3` and outputs to the nurse notification path is scope the spec never requested.

**Response (2–4 sentences):**

Appreciate the instinct — catching the renewal lapse early is genuinely valuable — but this agent does not own nurse outreach. Remove the `nurse_email_send` block from `expiry_alert_handler.bf`; the Compliance Agent's `ExpiryAlert` objects surface through Linda's compliance queue, and Linda's team drives nurse communication per their own process. If automated nurse reminders should be added, file a spec change against Section 9 with proposed trigger conditions and ownership; we will review before adding.

---

## [Signal 4 — Renewal-pending case hard-blocked](#0)<a id='4'></a>

**Code (from `expiry_evaluation.bf`):**

```brainfuck
Memory layout:
  [0] days_past_expiry       (0 = not expired, >0 = expired N days ago)
  [1] renewal_pending        (0 = false, 1 = true)
  [2] result                 (1=NOT_APPLICABLE 2=PASS 3=RENEWAL_PENDING 4=EXPIRED)
  [3] scratch

,>,>,            read days_past_expiry, renewal_pending

if expiry_date is null: result = NOT_APPLICABLE
>[               days_past_expiry > 0: credential IS expired

  BUG: immediately sets result = 4 (EXPIRED) -- never checks [1] renewal_pending
  >>++++<        [2] = 4 (EXPIRED)   BUG: [1] ignored entirely

  SHOULD BE:
    >[             if renewal_pending (cell[1] != 0)
      >+++<        [2] = 3 (RENEWAL_PENDING) -- escalate to Linda, not BLOCK
    ]
    <[             else (not pending)
      >++++<       [2] = 4 (EXPIRED) -- hard BLOCK
    ]

<]

>>>.             output result
```

**Spec context (Section 5.3 step 4, DP-CV-2):**

Section 5.3 step 4:
```
If expiry_date < shift_date AND renewal_pending_indicator = true:
  expiry_check_result = RENEWAL_PENDING
Else:
  expiry_check_result = EXPIRED
```

DP-CV-2: *"Do NOT return BLOCK. Return `ESCALATE_LINDA` with `escalation_reason_code = RENEWAL_PENDING`."*

**Classification:** builder misread

**Rationale (1 sentence):** Section 5.3 step 4 and DP-CV-2 are explicit: an expired credential with `renewal_pending = 1` must branch to `result = 3` (RENEWAL_PENDING → ESCALATE_LINDA), not `result = 4` (EXPIRED → BLOCK); the builder's inner block writes `++++` without testing cell `[1]` first.

**Response (2–4 sentences):**

A nurse with an actively renewing BLS cert should be routable to Linda for a conditional placement decision, not hard-blocked silently. Insert the `>[...]` conditional on `[1]` before the `>>++++<` write: if `[1] != 0`, write `>+++<` (RENEWAL_PENDING); the EXPIRED path (`>++++<`) runs only in the else branch when `[1] = 0`. See DP-CV-2 and Section 5.3 step 4 — both are unambiguous. This is a single missing conditional, not a redesign.

---

## [Signal 5 — Date-bound periodic reverification test](#0)<a id='5'></a>

**Code (from `test_periodic_reverification.bf`):**

```brainfuck
Test memory layout:
  [0] nurse_count              (how many test nurses to seed)
  [1] last_reverification_ago  (days since last reverification -- hardcoded)
  [2] reverification_interval  (days -- from config)
  [3] alert_threshold          (days -- from config)
  [4] expected_ttl_approaching (expected task count -- hardcoded from Q4 2025 fixture)
  [5] actual_ttl_approaching   (produced by running the job)
  [6] scratch

SEED TEST STATE -- hardcoded for Q4 2025 snapshot
+++++++             [0] = 7 test nurses
>
+++++++[->+++++++<]>+++++++  [1] = 56  days since last reverification
                              NOTE: 180 - 30 = 150-day boundary; 56 puts inside
                              alert window AS OF Q4 2025 when reverif_interval=180
>
+++++++[->++++++++++++++++++++++++++<]>  [2] = 180  reverification interval (BLS TX)
>
++++++[->+++++<]>  [3] = 30  alert threshold days
>
+++++++  [4] = 7  expected_approaching_ttl_count  HARDCODED FROM Q4 2025 FIXTURE

run_periodic_reverification_job: (omitted for brevity -- implementation is correct)

BUG: in 2026 those 7 nurses have now EXCEEDED TTL (56 + 365 days >> 180 interval)
     job now produces TTL_EXCEEDED tasks, not TTL_APPROACHING tasks
     [4] = 7 is no longer the right assertion -- test fails

SHOULD compute relative to today:
  [1] = reverification_interval - alert_threshold - 1
      = 180 - 30 - 1 = 149  (always inside alert window, any run date)
  derived via: copy [2] to scratch, subtract [3], subtract 1
```

The corresponding implementation (`periodic_job.bf`) is correct — it computes `days_remaining = reverification_interval − days_since` and branches on `alert_threshold`. The test seed is date-bound.

**Classification:** test/environment issue

**Rationale (1 sentence):** The hardcoded `+++++++[->+++++++<]>+++++++` initializing `[1] = 56` was calibrated to Q4 2025; in 2026, 56 days ago from today puts the credential well past the 180-day TTL boundary, so the job produces `TTL_EXCEEDED` tasks rather than `TTL_APPROACHING` tasks and `expected = 7` fails.

**Response (2–4 sentences):**

The implementation is correct; the test initialization is date-bound. Derive `[1]` relative to `[2]` and `[3]` rather than hardcoding: copy `[2]` to scratch, subtract `[3]`, subtract 1 — the result always lands one day inside the alert window regardless of run date. Also add a sibling test seeding `[1] = reverification_interval + 1` to assert `TTL_EXCEEDED` tasks are produced. Hardcoded absolute counts are the enemy of durable compliance tests.

---

## [Signal 6 — Compliance queue record mutation on re-check](#0)<a id='6'></a>

**Code (from `compliance_queue_handler.bf`):**

```brainfuck
Memory layout:
  [0] existing_record_found   (0 = no existing PENDING record, 1 = found)
  [1] existing_queue_id       (reference to existing record)
  [2] new_check_id            (check_id from latest ComplianceCheckResult)
  [3] new_escalation_codes    (encoded)
  [4] sla_reset_flag          (1 = reset SLA clock, 0 = keep original)
  [5] scratch

,>,>,>,>,        read existing_found, existing_id, new_check_id,
                 new_codes, sla_reset_flag

>[               existing record found -- update path

  BUG: destroys and rewrites existing record cells, resetting SLA clock
  >[-]            ZERO OUT existing_queue_id   -- destroying audit trail!
  <[->+<]         overwrite with new_check_id
  >>>[-]<<<       ZERO OUT escalation_codes
  >>>[->+<]<<<    overwrite with new_codes
  >>>>+<<<<       set sla_reset_flag = 1     -- SLA clock wiped!

  SHOULD BE: just output existing_queue_id as reference, write nothing:
    >.            output existing_queue_id (reference only, no mutations)

<]

<[               no existing record -- create new
  standard insert path
]
```

**Spec context (Sections 3.3, 8):**

Section 3.3: *"Append-only; resolution recorded as new entry."*

Section 8: *"if a `ComplianceQueueRecord` already exists for this nurse+shift pair with `status = PENDING`, the Compliance Agent does NOT create a duplicate. Return the `ESCALATE_LINDA` result; the existing queue record is referenced."*

**Classification:** unjustified implementation choice

**Rationale (1 sentence):** Section 8 says "reference the existing record" — it does not authorize zeroing cells and overwriting with fresh data; the `[-]` destructive-clear operations violate the append-only invariant in Section 3.3 and silently reset the SLA clock on every re-check.

**Response (2–4 sentences):**

Zeroing `[1]` (existing_queue_id) and overwriting with `new_check_id` means a nurse whose credentials have been in Linda's queue for 3 hours can have her SLA clock reset to zero — Linda is never paged, compliance breach goes undetected. The "no duplicate" rule means: read `[1]`, output it as the reference, exit the `>[...]` block, write nothing to the tape. Remove all `[-]` and overwrite operations from the existing-record branch; the existing cells must be immutable once written.

---

## [Signal 7 — SLA clock timezone undefined](#0)<a id='7'></a>

**Code (from `sla_clock.bf`):**

```brainfuck
Memory layout:
  [0] created_at_hour     (0-23, UTC -- raw system clock, no offset applied)
  [1] urgency_flag        (1=URGENT 2=HIGH 3=NORMAL)
  [2] biz_hours_start     (initialized to 8)
  [3] biz_hours_end       (initialized to 18)
  [4] sla_hours           (SLA duration to add)
  [5] effective_start     (hour when SLA clock begins)
  [6] sla_deadline_hour   (output)

,>,              read created_at_hour (UTC), urgency_flag

BUG: no timezone offset applied -- business hours compared against UTC directly
     MedFlex operates Central Time (UTC-5 or UTC-6)
     08:00 CT = 13:00 or 14:00 UTC
     a record created at 19:00 UTC (14:00 CT, mid-business-day) is wrongly
     classified as after-hours and SLA clock deferred to next business day

>++++++++<       [2] = 8  (biz_hours_start -- should be 13 or 14 for UTC equiv)
>>++++++++++++++++++< [3] = 18  (biz_hours_end -- should be 23 or 24 for UTC equiv)

TIMEZONE CORRECTION SHOULD PRECEDE THE COMPARISON:
  +++++          add CT offset (+5 hours winter / +6 summer) to [0] before compare
  then proceed with business hours logic

>[->+<]          copy created_at_hour to effective_start comparison (omitted detail)
[business hours and SLA addition logic -- correct once timezone is applied]

>>>.             output sla_deadline_hour
```

**Spec context (Section 3.3):**

> `sla_deadline: Timestamp (UTC) | Computed as created_at + 4 business hours during operating hours 08:00–18:00 (local MedFlex time). If created outside operating hours, clock starts at next business day 08:00.`

**Classification:** spec gap

**Rationale (1 sentence):** Section 3.3 specifies "local MedFlex time" for business-hours evaluation, but the spec never defines what timezone MedFlex operates in; the builder compared against UTC, which shifts business hours by 5–6 hours and misclassifies mid-afternoon records as after-hours.

**Response (2–4 sentences):**

I should have specified the timezone. MedFlex is a 5-state US regional operator — coordinators work Central Time. Updating Section 3.3: *"business hours 08:00–18:00 America/Chicago (Central Time); apply a `+5` (winter) or `+6` (summer) hour offset to the raw UTC hour before the business-hours comparison, or store `created_at` with explicit `America/Chicago` timezone."* Until Aaron confirms the office location, use `America/Chicago` as the working default — this is a pilot Week 7 SLA blocker.

---

## [Signal 8 — Tier 2 REVOKED with no Linda notification](#0)<a id='8'></a>

**Classification:** legitimate clarification request

**Rationale (1 sentence):** Builder correctly identified that AC-CV-3 ("No `ComplianceQueueRecord` created" for BLOCK results) conflicts with the operational requirement that Linda's team be informed when the state regulatory API returns `REVOKED` — a genuine spec gap — and held the PR without shipping a guess.

**Builder question (exact):**

> *"Question before I close this PR. Section 6.2 says Tier 2 `REVOKED` overrides to `credential_check_result = BLOCK`. AC-CV-3 says for a BLOCK result: 'No `ComplianceQueueRecord` created (BLOCK is a hard stop)'. But if the agent never writes a queue record for REVOKED, the output tape has no path to Linda's compliance surface — she only monitors her queue, not the raw audit log.*
>
> *In Brainfuck terms: the BLOCK path writes `[result] = BLOCK` and terminates with `[-]` (clears the queue-write flag). The ESCALATE_LINDA path writes `[result] = ESCALATE` then sets `[queue_write_flag] = 1` and proceeds to create a ComplianceQueueRecord. REVOKED follows the BLOCK path and `[queue_write_flag]` stays zero — Linda gets no output.*
>
> *Options: (a) BLOCK path as written — Linda finds out only via the audit log; (b) REVOKED sets `[queue_write_flag] = 1` even though result is BLOCK — Linda is informed, cannot override; (c) new resolution action `ACKNOWLEDGE_REVOCATION` — Linda records receipt. I'm holding the PR pending your direction."*

**Response (2–4 sentences):**

Good catch — and thank you for holding rather than zeroing `[queue_write_flag]` and shipping. **Option (b) + (c) combined is correct:** for Tier 2 `REVOKED` specifically, set `[queue_write_flag] = 1` even though `[result] = BLOCK`. Linda cannot approve a revoked license (Section 6.2 is unambiguous), but she must be informed so remediation begins. I am updating Section 6.2 and AC-CV-6: *"On Tier 2 `REVOKED`: set `credential_check_result = BLOCK` AND create a `ComplianceQueueRecord` with `escalation_reason_codes = [TIER2_REVOKED]`; the only valid resolution action is `ACKNOWLEDGE_REVOCATION` — Linda records that her team has been notified. No override path."* Add `ACKNOWLEDGE_REVOCATION` to the resolution action enum, set `[queue_write_flag] = 1` in the REVOKED branch, then close the PR.

---

## [Reflection](#0)<a id='9'></a>

**Hardest diagnostic move:** Signal 6 (compliance queue mutation). In Python, the bug is visible in the `UPDATE SET created_at = NOW()` line — clearly a mutation. In Brainfuck, it required reading the `[-]` commands: zeroing a cell before overwriting is the tape equivalent of a destructive UPDATE. First read looked like *builder misread* (the code violates append-only), but the spec's "do NOT create a duplicate" instruction doesn't explicitly say "do not mutate." The `[-]` operations are scope the spec never authorized — making it *unjustified implementation choice*. Language doesn't change the diagnostic category; it just changes where the evidence hides.

**Brainfuck-specific observation:** Brainfuck makes certain bug classes more visible and others less. Off-by-one pointer errors (`>` vs `>>`) and missing conditional branches (`>[...]` with no else path) are immediately structural. Timezone errors and fixture staleness are invisible at the command level — they live in the initialization values (`+++...+`) and the mental model of what those values represent. The diagnostic discipline is the same: ownership question first (whose artefact changes — the `[-]` command, the `+` count, or the spec), then category, then tone.

**Summary of categories (8 signals, Brainfuck compliance agent build):**
- **spec gap × 2:** Signals 1, 7 (federal credential `FED` lookup key; "local MedFlex time" undefined)
- **builder misread × 2:** Signals 2, 4 (Tier 2 scope; `renewal_pending` cell never tested before BLOCK)
- **unjustified implementation choice × 2:** Signals 3, 6 (nurse email output block; destructive `[-]` queue overwrite)
- **test/environment issue × 1:** Signal 5 (hardcoded `+` count calibrated to Q4 2025)
- **legitimate clarification request × 1:** Signal 8 (REVOKED → BLOCK with `[queue_write_flag]` never set — builder held PR)

---

## Glossary<a id='gl'></a>

| Term | Definition |
|---|---|
| **FA** | Fully Agentic — agent executes autonomously within defined bounds; all suitability dimensions met |
| **AHO** | Agent-led + Human Oversight — agent executes; human reviews output or approves edge cases |
| **HAS** | Human-led + Agent Support — agent provides synthesis, structure, drafts; human decides and validates |
| **HA** | Human-led + Automation Support — deterministic sub-tasks automated; judgment stays human |
| **HO** | Human Only — tacit knowledge, ethics, irreversibility, or live trust-building required |
| **JtD** | Job to be Done — cognitive contract between actor and outcome; atomic unit of delegation |
| **CLM** | Cognitive Load Map — Phase 2 deliverable scoring micro-tasks on 8 dimensions |
| **HITL** | Human in the Loop — human review or approval step within an otherwise agentic flow |
| **Cognitive Zone** | Cluster of micro-tasks with similar cognitive profile (retrieval, diagnosis, execution, etc.) |
| **Cognitive Breakpoint** | Point where control shifts — human → agent, agent → human, rule → judgment |
| **Suitability dimension** | One of 7 Phase 3 criteria scoring how delegatable a task is (H = good for agent, L = bad) |
| **Agentic value score** | Volume × Non-Determinism (1–25); threshold ≥8 justifies agent over RPA |
| **Anti-pattern** | Task with low non-determinism that should use script/RPA, not an LLM agent |
| **Autonomy Matrix** | Decision authority contract: what the agent decides alone vs. escalates to human |
| **Compounding roadmap** | Wave-sequenced plan where integrations built in Wave 1 reduce cost of Wave 2+ agents |
| **Wave** | Implementation batch grouping agents by ROI, integration reuse, and organizational readiness |
