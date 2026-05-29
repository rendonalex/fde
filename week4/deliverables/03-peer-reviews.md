
# Specification Validation Summary — Week 4 Peer Review

## Table of Contents

1. [Validation Summary - Planned Matching (Krzysztof Wilniewczyc)](#validation-summary---04a-capability-spec-planned-matching-krzysztof-wilniewczyc)
   - [ENTITY PRECISION Gaps](#entity-precision-gaps)
   - [INTEGRATION CONTRACTS Gaps](#integration-contracts-gaps)
   - [BUILDABILITY Gaps](#buildability-gaps)
   - [Status](#status)

2. [Validation Summary - Intake (Priya Gupta)](#validation-summary---04a-capability-spec-intake-priya-gupta)
   - [ENTITY PRECISION - Ambiguities](#entity-precision---ambiguities)
   - [INTEGRATION CONTRACTS - Missing Details](#integration-contracts---missing-details)
   - [BUILDABILITY - Implementation Gaps](#buildability---implementation-gaps)
   - [Missing Cross-Cutting Concerns](#missing-cross-cutting-concerns)
   - [Testability Gaps](#testability-gaps)

---

# Validation Summary - 04a-capability-spec-planned-matching-Krzysztof-Wilniewczyc

The specification `04a-capability-spec-planned-matching-Krzysztof-Wilniewczyc.md` does not pass production-grade validation for AI buildability. The following gaps prevent an AI coding agent from building without clarifying questions:

## ENTITY PRECISION Gaps

**Section 3: Shared Entities**
- Missing field types (string, int, datetime, enum values)
- Missing field constraints (max lengths, required vs optional, null handling)
- Missing timestamp format specifications (ISO 8601 not specified)
- Missing enum value definitions (LockState lists values but no casing/storage format)
- Missing foreign-key cascade behavior
- Missing index requirements for query performance

**Example**: `ShiftRequest.received_at` - no specification of timezone handling, format, or precision

## INTEGRATION CONTRACTS Gaps

**Section 7: Integration Contracts**
- Missing endpoint URLs/paths
- Missing authentication methods (API keys, OAuth, service accounts)
- Missing request/response JSON schemas
- Missing specific timeout values (only "retry with backoff" mentioned)
- Missing rate-limit budgets
- Missing HTTP methods (GET, POST, PUT)
- Missing error response codes and handling
- Missing pagination specifications for list operations
- Missing API versioning strategy

**Example**: "ServiceNow read API" - no specification of which endpoint, what query parameters, what the response structure looks like

## BUILDABILITY Gaps

**Numeric Parameters Left Undefined** (acknowledged in A11 but blocks building):
- Near-tie threshold (§5)
- Top-N shortlist size (§3)
- Location proximity bound (§4 step 2)
- Field-level confidence threshold (85% mentioned in step 1, but calculation method undefined)
- Agreement-between-signals metric calculation (§4 step 5)

**Template/Format Gaps**:
- `HospitalSubmission.reasoning_summary` format not specified
- SMS/email message templates not provided
- Citation format for reasoning not specified

**Timing Precision**:
- Decision 2 window "~90 min planned" - approximation not sufficient
- Trust ramp "weeks 5–7 behaviour" undefined
- Retry backoff algorithm not specified

**Missing Algorithms**:
- Two-stage extraction validation method (step 1)
- Rules-based eligibility filter logic (step 2)
- Contextual reasoning ranking algorithm (step 4)
- Confidence scoring calculation (step 5)

## Status

**Structurally complete** (all 10 sections present, entities named, validation hooks defined) but **not production-grade for AI building**. The specification correctly identifies these gaps in A11 and A12 as "deliberately deferred," but this deferral means an AI agent cannot compile working code without inventing these values.

**Recommendation**: Pin numeric parameters, define integration schemas, and specify entity field types before handoff to AI coding agent.


# Validation Summary - 04a-capability-spec-intake-Priya-Gupta

The specification `04a-capability-spec-intake-Priya-Gupta` did not pass production-grade validation. The following issues were identified:

## ENTITY PRECISION - Ambiguities

### ShiftRequirement Entity
- **`hospital_name_raw` validation**: "max 200 chars" but no handling for extraction failures
- **`location_address` partial state**: "may be null or partial" is ambiguous - how is "partial" determined programmatically?
- **`preferred_attributes` structure**: "array of strings" with "free-text preferences extracted verbatim" - no extraction rules defined
- **`parse_confidence_flags` enumeration**: Example values given but not exhaustive list - is this open-ended or fixed? Also, there is no clear description of how they are set

### Input Entity
- **`hospital_id` mapping logic**: "ServiceNow sender mapping" not defined - where/how is this mapping stored?
- **`raw_text` sanitization**: No specification for handling special characters, encoding, or malicious input; or what if it has lenght > 10,000 chars?

## INTEGRATION CONTRACTS - Missing Details

### ServiceNow Integration
- **Missing webhook payload schema**: No definition of the exact JSON structure ServiceNow sends
- **Missing error response format**: What does the agent return to ServiceNow on success/failure?
- **Missing endpoint specification**: What URL path does the agent expose for the webhook?
- **Incomplete polling fallback**: Query parameters defined but no response schema documented
- **Missing idempotency handling**: Beyond deduplication, how are retries handled at the HTTP level?

### LLM Extraction
- **Missing request schema**: Exact prompt structure and JSON schema for structured output not specified
- **Missing response schema**: Expected JSON structure from LLM not documented
- **Missing API endpoint**: Which specific API endpoint is called?
- **Missing authentication details**: How is the API key passed (header name, format)?
- **Rate limit handling incomplete**: "Queue inbound requests" mentioned but no queue mechanism specified

### Coordinator Review Queue
- **Missing write mechanism**: Is this a database write, message queue, or API call?
- **Missing connection details**: No database connection string, queue URL, or API endpoint specified
- **Missing error handling**: What happens if the write fails?

## BUILDABILITY - Implementation Gaps

### Step 1: Extract Fields via LLM
- **Prompt engineering**: No actual prompt template provided - AI cannot build without knowing what to send to LLM
- **Field extraction rules**: "Extract all ShiftRequirement fields" is not specific enough - which fields map to which parts of raw_text?
- **Retry logic on malformed JSON**: "retry once" but no specification of what changes between attempts

### Step 2: Normalize Credential Codes
- **Fuzzy matching algorithm**: "Fuzzy match" mentioned but no algorithm specified (Levenshtein distance? Threshold? Semantic similarity?)
- **Lookup table location**: "static CSV file" but no file path, format specification, or column headers defined
- **Cache invalidation**: "reads it at startup" but no mechanism for detecting updates or forcing reload

### Step 3: Normalize unit_type
- **Lookup table not provided**: References "a lookup table" but doesn't define it or provide examples beyond the enum values
- **Mapping rules**: How does "ICU unit" map to "ICU"? No fuzzy matching rules specified

### Step 4: Compute parse_confidence
- **Multiple null fields**: "−0.25 per field" but which fields count as "required" for this calculation? The entity shows conditional requirements based on status
- **"Partial or incomplete" detection**: `LOCATION_INCOMPLETE` flag requires undefined logic to detect partial addresses
- **"Credential-like language" detection**: `POSSIBLE_MISSED_CREDENTIAL` flag has no detection rules specified

## Missing Cross-Cutting Concerns

- **Logging specification**: "Every route decision is logged" but no log format, destination, or structured logging schema provided
- **Monitoring/alerting**: No specification for when/how to alert coordinators of system issues
- **Data retention**: No specification for how long ShiftRequirement records are kept
- **Timezone handling**: ISO 8601 timestamps specified as UTC but no handling for shift times in local hospital timezone
- **Concurrency**: No specification for handling multiple simultaneous requests

## Testability Gaps

- **No acceptance criteria**: Examples provided but no pass/fail criteria for each processing step
- **Confidence score validation**: No test cases showing exact score calculations with multiple flags
- **Edge case completeness**: Edge cases table provided but missing scenarios like: network failures mid-processing, database unavailability, partial LLM responses