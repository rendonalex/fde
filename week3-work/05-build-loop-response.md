# W3D3 Build-Loop Exercise — Signal Analysis - Cascade Public Libraries

## Signal 1 — 72-hour notification window implementation

**Classification:** Spec gap

**Rationale:** R3 specifies "72 hours to claim the hold" but the Assumptions section explicitly flags that "the definition of '72 hours' in R3 as calendar hours vs business hours (libraries closed Sundays) is not specified" and assumes calendar hours pending FDE review.

**Response:**
The implementation correctly interprets the 72-hour window as calendar matching the assumption that I documented but my specification does not say either from when specifically the 72 hours start counting (although you correctly used the notified_at time which could be a timestamp of notification), and whether the library opening hours are to be taken into account. However, I should have resolved this ambiguity in the spec itself rather than leaving it in Assumptions. After confirming with the business that library operating hours should not be taken into account when calculating the 72 hour window, I can update R3 to explicitly state: "A notified patron has 72 calendar hours (not business hours) to claim the hold from the moment it is notified, measured from the notification timestamp regardless of library operating hours." This removes the ambiguity for future builds.

---

## Signal 2 — Accessibility priority weight implementation

**Classification:** Builder misread

**Rationale:** R4 explicitly states "Accessibility-priority patrons jump to queue position 1" (a positional jump, not a weight), but the builder implemented a 0.25 weight multiplier instead of the specified position-1 jump behavior.

**Response:**
R4 specifies that accessibility-priority patrons "jump to queue position 1", not that they receive a weight multiplier. The implementation in `accessibility_priority.py` uses `ACCESSIBILITY = 0.25` weight, which contradicts the spec's explicit jump to queue position 1 behavior. 
To the Builder: Please revise `compute_effective_position()` to implement the position jump: when `patron.has_accessibility_modifier` is true, return position 1 (or the next available position if another accessibility-priority patron is already in the list, per R4's FIFO rule between them). The weight-based approach should only apply to Academic-tier patrons per R5.

---

## Signal 3 — Auto-checkout return reminder

**Classification:** Unjustified implementation choice

**Rationale:** Unjustified implementation choice: R7 specifies auto-checkout behavior (automatic loan creation and notification) but does not mention scheduling return reminders; the builder added `schedule_reminder()` functionality that appears nowhere in the requirements.

**Response:**
To the Builder: the spec does not ask for the reminder functionality, and R7 only covers the auto-checkout and notification flow. Remove the `schedule_reminder()` call and related logic.

---

## Signal 4 — OverDrive refresh test fixture

**Classification:** Test/environment issue

**Rationale:** The test passes when CI clock is set to 2025 but fails in 2026 because the fixture's `expected_advances` field encodes queue state from Q4 2025, making the test brittle and time-dependent rather than testing the logic specified in R8.

**Response:**
The implementation of `on_overdrive_catalog_refresh()` correctly advances the queue by the number of added copies per R8. The test failure is due to the fixture being bound to 2025 queue state rather than testing the refresh logic itself. To the Builder: refactor the test to mock the queue state explicitly in the test setup rather than relying on dated fixture data. The test should verify that N copies added results in N queue advances, independent of calendar date.

---

## Signal 5 — Duplicate hold rejection for same title

**Classification:** Builder misread

**Rationale:** R11 explicitly states "if a patron places holds on the ebook and audiobook editions of the same title, the system treats them as two separate holds," but the builder's code rejects any hold where `patron_has_active_hold_on_title(patron, title_id)` returns true, ignoring format distinction.
NOTE: This same snippet could also be a Spec gap because there is no rule for the Accessibility-priority patrons. R9 provides the rule for Standard patrons and Academic-tier patrons but says nothing about Accessibility-priority patrons. The builder assumed they get the same limits as a Standard patron.

**Response:**
To the Builder: R11 specifies that ebook and audiobook editions of the same title should be treated as separate holds, both counting toward the active-hold limit. Your implementation in `place_hold.py` rejects duplicate holds based on `title_id` alone, which would incorrectly prevent a patron from holding both the ebook and audiobook of the same title. Revise the duplicate check to: `patron_has_active_hold_on_title(patron, title_id, format_type)` so that holds are only considered duplicates when both title_id **AND** format_type match. The current logic contradicts R11's format-distinct requirement.

---

## Signal 6 — Paused hold notification

**Classification:** Unjustified implementation choice

**Rationale:** R6 specifies that "paused holds retain queue position but are skipped over when the title becomes available; the next eligible patron is notified instead," but does not specify sending an email notification to patrons whose paused holds are skipped.

**Response:**
To the Builder: the logic correctly skips paused holds per R6, but the spec does not ask for the email notification you have added when a paused hold is skipped. Remove the `send_email()` call in the paused-hold branch.

---

## Signal 7 — SMS-only notification channel

**Classification:** Spec gap

**Rationale:** R12 states "email by default" and "patrons who registered a mobile number can opt-in to SMS notifications," but the Assumptions section explicitly flags that "the business has not yet decided whether SMS-opted patrons should receive both email and SMS, or only SMS." The implementation chooses SMS-only for opted-in patrons, which is one valid interpretation of R12, but the spec does not specifically say if SMS-opted patrons should also receive an email.

**Response:**
 After confirming with business, I can update R12 to specify: "Patrons who opt-in to SMS receive SMS notifications only (email is suppressed for SMS-opted patrons to avoid duplicate notifications). Patrons without SMS opt-in receive email."

---

## Signal 8 — Academic + Accessibility-priority intersection

**Classification:** Legitimate clarification request

**Rationale:** The Assumptions section explicitly states "Academic + Accessibility-priority intersection is not specified" and flags it as "pending FDE confirmation," and the builder correctly identifies that the interaction between R4 (position-1 jump) and R5 (0.5x weight) creates ambiguous edge cases.

**Response:**
After confirming with the business that the intended behavior is option (a) R4 wins completely, I can add a clarification to R4 to specify: "For patrons with both Academic and Accessibility-priority status, the accessibility position-1 jump takes precedence; the academic weight does not apply. The Academic weight only applies when comparing Academic vs Standard patrons, not when accessibility priority has already placed someone at position 1". To the Builder: implement option (a) so that we can merge.

---

## Reflection

The hardest diagnostic move for me was distinguishing between **spec gap** and **legitimate clarification request** (Signals 1, 7, and 8). All three involved ambiguities that were documented in the Assumptions section, but Signal 8 was a clarification request because the builder explicitly asked for direction before merging, while Signals 1 and 7 were spec gaps because the builder made reasonable assumptions. Is the key distinction whether the builder is asking or assuming?. If I ran this exercise again, I would then focus more carefully on the builder's perspective in the signal: is this a question or a decision made based on reasonable assumptions? That would change whether I respond with acknowledgment or spec revision.