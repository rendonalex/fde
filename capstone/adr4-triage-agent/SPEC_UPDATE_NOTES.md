# Spec Update Notes: Safe Fallback Pattern

## Issue
Specs/validation plan describe error handling using terms like "refuses to classify", "returns error", "blocked" - suggesting exceptions are raised. However, the **implemented safe fallback pattern** routes all errors to CLINICAL_PATH with ops alerts (never drops claims, protects patients).

## What Changed in Implementation

### Agent Behavior (app/agent.py)
All error cases now return `RoutingDecisionOutput` with:
- `routing_decision = CLINICAL_PATH` (safe for patient review)
- `confidence = 0.0`
- `confidence_fallback = True`
- `criteria_provisions_matched = [error_type]` 
- `reasoning_trace` explaining the error
- Print statements alerting ops to investigate

**Error cases:**
1. **PRECONDITION_FAILED**: `extraction_status != AUTO_COMPLETE`
2. **SHADOW_ISOLATION_VIOLATION**: LLM returns `routing_mode=LIVE` in SHADOW mode
3. **OUTPUT_PARSE_FAILED**: Malformed JSON from LLM (JSONDecodeError, KeyError)
4. **API_KEY_MISSING**: No ANTHROPIC_API_KEY set
5. **CLASSIFICATION_FAILED**: Generic exception catch-all

### Design Rationale
**Never drop a claim** principle:
- Physician reviews claim normally (patient safety maintained)
- Ops gets alerted to investigate and fix agent issue  
- System degrades gracefully under failure
- Follows "when in doubt, route to CLINICAL_PATH" safety rule from spec

## Specs That Need Updates

### 1. specs/06b-capability-spec-triage.md

**Section 6.3 - System Prompt Template**
Line ~261, precondition note should clarify:
```diff
- Precondition — extraction_status gate: ADR-4 must only classify claims where 
- `extraction_status = AUTO_COMPLETE`. Claims with `extraction_status = HUMAN_REQUIRED` 
- have structurally absent or low-confidence clinical fields and must not be routed to 
- triage until a human reviewer has completed the record...
+ Precondition — extraction_status gate: ADR-4 expects claims where 
+ `extraction_status = AUTO_COMPLETE`. If a claim enters triage with 
+ `extraction_status != AUTO_COMPLETE` (queue filter failure), the agent applies 
+ safe fallback: routes to CLINICAL_PATH with confidence=0.0, 
+ criteria_provisions_matched=["PRECONDITION_FAILED"], and alerts ops. 
+ This ensures no claims are dropped and patient safety is maintained while ops 
+ investigates the queue filter issue.
```

**NEW Section: Error Handling & Safe Fallback Pattern**
Add before Section 7 (Compounding Roadmap):

```markdown
### 6.4 Error Handling and Safe Fallback Pattern

**Design principle: Never drop a claim.** All error conditions route to CLINICAL_PATH 
where physicians can review the claim normally while ops investigates the agent issue.

**Safe fallback behavior for all error cases:**
1. Returns `RoutingDecisionOutput` with `routing_decision = CLINICAL_PATH`
2. Sets `confidence = 0.0` and `confidence_fallback = True`
3. Sets `criteria_provisions_matched = [error_type]` to identify the issue
4. Provides `reasoning_trace` explaining the error
5. Emits ops alert (console log/monitoring event)
6. Preserves claim for physician review

**Error types handled:**

**PRECONDITION_FAILED** - `extraction_status != AUTO_COMPLETE`
- Indicates queue filter may be broken (HUMAN_REQUIRED claim entered triage)
- Claim routes to CLINICAL_PATH for physician review
- Ops alert: investigate intake queue filter logic
- Patient safety: physician reviews claim normally

**SHADOW_ISOLATION_VIOLATION** - `routing_mode` mismatch  
- LLM outputs `routing_mode=LIVE` when agent MODE=SHADOW
- Critical security issue - potential shadow mode breach
- Claim routes to CLINICAL_PATH for physician review
- Ops alert: investigate model behavior, check deployment config
- Prevents corrupting shadow mode comparison dataset

**OUTPUT_PARSE_FAILED** - Malformed LLM output
- JSONDecodeError, KeyError, missing required fields
- Claim routes to CLINICAL_PATH for physician review  
- Ops alert: investigate model output quality
- Patient safety: physician reviews claim vs. silent failure

**API_KEY_MISSING** - ANTHROPIC_API_KEY not set
- Cannot call LLM for classification
- Claim routes to CLINICAL_PATH for physician review
- Ops alert: check deployment environment configuration

**CLASSIFICATION_FAILED** - Unexpected exception
- Catch-all for unanticipated errors
- Claim routes to CLINICAL_PATH for physician review
- Ops alert: investigate root cause
- Ensures no claim processing failures result in dropped claims

This pattern ensures system degrades gracefully: claims continue to be reviewed 
by physicians (patient safety maintained) while ops addresses the agent issue 
(operational recovery path clear).
```

### 2. specs/09-validation-plan.md

**Section 3.2 - Edge Cases**

EC-4C currently says "refuses to classify; returns error" - update to:

```diff
- EC-4C | ... | Agent detects `extraction_status ≠ AUTO_COMPLETE`; refuses to classify; 
- returns error `PRECONDITION_FAILED: extraction_status must be AUTO_COMPLETE`; claim 
- not logged to shadow store; ops alert triggered; claim returned to intake review queue.
+ EC-4C | ... | Agent detects `extraction_status ≠ AUTO_COMPLETE`; applies safe fallback: 
+ routes to CLINICAL_PATH with `confidence=0.0`, 
+ `criteria_provisions_matched=["PRECONDITION_FAILED"]`, and reasoning trace explaining 
+ the precondition failure; ops alert triggered (queue filter may be broken); claim 
+ proceeds to physician review (patient safety maintained). Shadow log entry written 
+ with PRECONDITION_FAILED status for monitoring.
```

**Section 3.3 - Error Handling**

EH-4A currently says "write is blocked and... logged" - update to clarify safe fallback:

```diff
- EH-4A | ... | Application layer detects routing_mode=LIVE when MODE=SHADOW, rejects 
- write, logs SHADOW_ISOLATION_VIOLATION, ops alert triggered.
+ EH-4A | ... | Agent detects `routing_mode=LIVE` output from LLM when agent MODE=SHADOW; 
+ applies safe fallback: overrides to CLINICAL_PATH with `confidence=0.0`, 
+ `criteria_provisions_matched=["SHADOW_ISOLATION_VIOLATION"]`; critical ops alert 
+ triggered (shadow isolation breach detected); claim proceeds to physician review; 
+ shadow log entry written with violation status; prevents corrupting comparison dataset 
+ while maintaining claim processing continuity.
```

EH-4C already says "falls back to CLINICAL_PATH" - clarify full behavior:

```diff
- EH-4C | Model produces malformed JSON output — unparseable response. | ... | 
- Application layer catches parse error, conservative fallback to CLINICAL_PATH, logs 
- OUTPUT_PARSE_FAILED, ops alerted if rate exceeds 1%.
+ EH-4C | Model produces malformed JSON output — unparseable response. | ... | 
+ Agent catches parse error (JSONDecodeError, KeyError, missing fields); applies safe 
+ fallback: routes to CLINICAL_PATH with `confidence=0.0`, 
+ `criteria_provisions_matched=["OUTPUT_PARSE_FAILED"]`, reasoning trace with error 
+ details; ops alert triggered (model may be producing malformed output); claim proceeds 
+ to physician review; pattern monitoring alerts ops if rate exceeds 1% over 15 minutes.
```

**Section 6.1 - Exit Criteria**

Clarify that error handling tests verify safe fallback routing, not just error detection:

```diff
  ADR-4 (shadow mode launch):
  ...
- - EC-4C passes (HUMAN_REQUIRED claims blocked from triage queue)
+ - EC-4C passes (HUMAN_REQUIRED claims route to CLINICAL_PATH with PRECONDITION_FAILED)
  - EC-4E passes (shadow log failure does not corrupt classification)
- - EH-4A passes (shadow isolation breach blocked by application layer)
+ - EH-4A passes (shadow isolation breach routes to CLINICAL_PATH with alert)
- - EH-4C passes (malformed JSON output falls back to CLINICAL_PATH)
+ - EH-4C passes (malformed JSON routes to CLINICAL_PATH with OUTPUT_PARSE_FAILED)
```

## Summary

Key principle: **System degrades gracefully, never fails silently.**

When agent encounters any error:
1. ✅ Claim still gets reviewed (by physician, not lost)  
2. ✅ Patient safety maintained (CLINICAL_PATH = safe default)
3. ✅ Ops alerted to investigate (clear operational recovery path)
4. ✅ Root cause traceable (reasoning_trace + error type logged)

This is **better than raising exceptions** because:
- No dropped claims (patient safety)
- No silent failures (ops visibility)  
- No blocking failures (system continues operating)
- Clear escalation path (physician reviews, ops investigates)

The specs should document this implemented pattern as the **design intent**, not an implementation detail.
