# ADR-4 Clinical Content Triage Agent

Full implementation of the Clinical Content Triage Agent per `specs/06b-capability-spec-triage.md`.

## Architecture

```
adr4-triage-agent/
├── app/
│   ├── main.py                 # FastAPI application (shadow log API)
│   ├── agent.py                # Core triage agent (classification logic)
│   ├── models.py               # Pydantic data models
│   ├── database.py             # SQLite database setup
│   └── codebook.py             # Criteria codebook loader
├── tests/
│   ├── test_agent.py           # Agent classification tests
│   ├── test_api.py             # API endpoint tests
│   └── test_scenarios.py       # Validation scenarios from spec §10
├── config/
│   └── criteria-codebook.json  # Clinical criteria codebook
├── data/
│   └── shadow_log.db           # SQLite database (created at runtime)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Features Implemented

### Core Agent (agent.py)

**LLM-Based Classification** (per spec §6.3):
- ✅ Uses **Claude Sonnet 4.6** for classification (Anthropic API)
- ✅ Sends claim + codebook to Claude via system prompt (Jupyter notebook approach)
- ✅ Claude performs 6-step reasoning procedure
- ✅ Clinical reasoning with context (e.g., detects code mismatches like bronchitis + chemo)
- ✅ Nuanced confidence scoring based on clinical appropriateness
- ✅ Chain-of-thought reasoning traces from Claude
- ✅ Structured JSON output validated by Pydantic
- ✅ Confidence fallback (< 0.70 → CLINICAL_PATH)
- ✅ NOVEL_CASE guardrail (unmatched codes → CLINICAL_PATH, confidence=0.0)
- ✅ Shadow vs. Live mode switching
- ✅ Precondition validation (`extraction_status = AUTO_COMPLETE`)
- ✅ Shadow mode isolation enforcement
- ✅ Requires: `ANTHROPIC_API_KEY` environment variable

### Shadow Log Store API (main.py)
- ✅ `POST /api/v1/shadow-log` — write agent classification
- ✅ `PUT /api/v1/shadow-log/{shadow_log_id}/processor-decision` — update with processor decision
- ✅ `GET /api/v1/shadow-log/metrics` — query false-negative rate for [A6] gate
- ✅ `GET /api/v1/shadow-log` — list shadow log entries
- ✅ SQLite backing store (no external dependencies)

### Guard Rails
- ✅ Shadow mode isolation (MODE=SHADOW enforced)
- ✅ Codebook version mismatch detection
- ✅ Precondition validation (`extraction_status = AUTO_COMPLETE`)
- ✅ Conservative fallback on low confidence
- ✅ Novel case detection

### Data Models
- ✅ `NormalizedClaimRecord` (input schema)
- ✅ `RoutingDecisionRecord` (shadow log entry)
- ✅ `CriteriaCodebookEntry` (codebook provision)
- ✅ State machines per spec §9.1

### Validation
- ✅ Happy path scenarios (§10.1, §10.2)
- ✅ Edge cases EC-1 through EC-7 (§10.3)
- ✅ Failure modes FM-1 through FM-3 (§10.4)

## Quick Start

### 1. Install Dependencies

```bash
cd adr4-triage-agent
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Anthropic API key for Claude LLM calls
export ANTHROPIC_API_KEY="your-api-key-here"

# Optional: set mode (default: SHADOW)
export ADR4_MODE="SHADOW"

# Optional: set confidence threshold (default: 0.70)
export ADR4_CONFIDENCE_THRESHOLD="0.70"
```

### 3. Run the Shadow Log API

```bash
uvicorn app.main:app --reload --port 8000
```

API will be available at `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`

### 4. Test the Agent

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agent.py -v

# Run validation scenarios
pytest tests/test_scenarios.py -v
```

### 5. Classify a Claim

```bash
# Example: classify a routine office visit claim
curl -X POST http://localhost:8000/api/v1/classify \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "a3f1e2d4-0c8b-4e6a-9f7d-1b2c3d4e5f60",
    "source_claim_ref": "PDF-2026-0441",
    "intake_channel": "CMS1500_PDF",
    "extraction_status": "AUTO_COMPLETE",
    "member_id": "M-4421908",
    "icd10_codes": ["Z00.00"],
    "cpt_codes": ["99213"],
    "prior_auth_required": false,
    "prior_auth_number": null,
    "payer_id": "BX-0042",
    "place_of_service": "11",
    "billed_amount": 185.00
  }'
```

Expected output:
```json
{
  "claim_id": "a3f1e2d4-0c8b-4e6a-9f7d-1b2c3d4e5f60",
  "source_claim_ref": "PDF-2026-0441",
  "routing_decision": "FAST_PATH",
  "confidence": 0.96,
  "confidence_fallback": false,
  "clinical_indicators_detected": ["ICD-10: Z00.00", "CPT: 99213"],
  "criteria_provisions_matched": [],
  "reasoning_trace": "Step 1 — ICD-10 scan: Z00.00...",
  "routing_mode": "SHADOW"
}
```

## Using Docker

```bash
# Build image
docker build -t adr4-triage-agent .

# Run with docker-compose
docker-compose up

# Access API at http://localhost:8000
```

## [A6] Gate Validation

Query false-negative rate for Wave 2 activation:

```bash
curl http://localhost:8000/api/v1/shadow-log/metrics
```

Expected response:
```json
{
  "total_entries": 2154,
  "labeled_entries": 2154,
  "disagreement_entries": 38,
  "false_negative_count": 21,
  "false_negative_rate": 0.0097,
  "gate_status": "PASS",
  "gate_threshold": 0.02,
  "min_labeled_entries": 2000,
  "wave_2_ready": true
}
```

Wave 2 activation conditions:
- ✅ `false_negative_rate < 0.02`
- ✅ `labeled_entries >= 2000`
- ✅ 60-day window elapsed

## Testing

The test suite covers:

1. **Unit tests** (`test_agent.py`):
   - Clinical indicator extraction
   - Codebook matching
   - Confidence scoring
   - Fallback logic
   - Novel case detection

2. **API tests** (`test_api.py`):
   - Shadow log write endpoint
   - Processor decision update
   - Metrics query
   - Error handling

3. **Validation scenarios** (`test_scenarios.py`):
   - Happy paths (§10.1, §10.2)
   - Edge cases EC-1 through EC-7
   - Failure modes FM-1 through FM-3

Run tests:
```bash
pytest tests/ -v --cov=app --cov-report=html
```

Coverage report: `htmlcov/index.html`

## Configuration

### Codebook Management

Edit `config/criteria-codebook.json` to update clinical criteria. Agent will detect version mismatches and halt.

Codebook versioning:
- `codebook_version`: Semver string
- `effective_date`: YYYY-MM-DD
- `approved_by`: Dr. Webb user ID
- `approved_at`: ISO 8601 timestamp

### Mode Switching

**Shadow mode** (Wave 1):
```bash
export ADR4_MODE="SHADOW"
```

**Live mode** (Wave 2, after [A6] gate passes):
```bash
export ADR4_MODE="LIVE"
```

**CRITICAL**: Mode switching requires redeployment. Never modify mode at runtime.

### Confidence Threshold

Adjust fallback threshold (default: 0.70):
```bash
export ADR4_CONFIDENCE_THRESHOLD="0.75"
```

## Integration Points

### CMS API (not implemented in this build)
- Read: `GET /api/v1/claims/{claim_id}`
- Write: `PUT /api/v1/claims/{claim_id}/routing` (LIVE mode only)

### Adjudication Queue (not implemented in this build)
- Submit: `POST /api/v1/adjudication-items`
- Label: `PUT /api/v1/adjudication-items/{id}`

### Policy Vector Store (not active in current build)
- Query: `POST /api/v1/vector-store/query`

## Compliance

### HIPAA
- Reasoning traces contain PHI and are stored only in shadow log database
- Database access restricted to evaluation pipeline and Dr. Webb's team
- Audit trail for all routing decisions

### Shadow Mode Isolation
- MODE declaration is first line of system prompt
- Application validates `routing_mode == "SHADOW"` before any CMS write
- Pre-deployment integration test verifies claim status unchanged

### Live Mode Activation Gate
Gate conditions (all required):
- ✅ False-negative rate < 2% over ≥60 days
- ✅ ≥2,000 labeled entries in shadow log
- ✅ Criteria codebook approved by Dr. Webb
- ✅ CMS shadow write confirmed isolated
- ✅ Three-stakeholder sign-off (CFO, CMO, VP Ops)

## Maintenance

### Updating the Codebook

1. Dr. Webb approves new provisions
2. Update `config/criteria-codebook.json` with new `codebook_version`
3. Redeploy agent with new prompt version
4. Verify codebook version match at startup

### Monitoring

Key metrics:
- `false_negative_rate` (target: < 2%)
- `confidence_fallback_rate` (% below threshold)
- `novel_case_rate` (codebook coverage indicator)
- Shadow log write failures
- Classification latency (target: < 2 min/claim)

Ops alerts:
- `SHADOW_ISOLATION_VIOLATION` — MODE=SHADOW but routing_mode=LIVE output
- `CODEBOOK_VERSION_MISMATCH` — system prompt vs. deployed codebook
- `NOVEL_CASE_RATE_SPIKE` — >50% over 5-min window (empty codebook)
- `SHADOW_LOG_WRITE_FAILED` — buffering to local storage

## License

Internal use only. Greenfield Health Systems AI Claims Processing Transformation.

## Support

FDE Engagement Lead  
Wave 1 Delivery Team
