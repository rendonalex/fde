# ADR-4 Build Summary

## What Was Built

A **complete, runnable implementation** of the ADR-4 Clinical Content Triage Agent per `specs/06b-capability-spec-triage.md`.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Shadow Log Store API (SQLite)                         │ │
│  │  - POST /api/v1/shadow-log                             │ │
│  │  - PUT /api/v1/shadow-log/{id}/processor-decision      │ │
│  │  - GET /api/v1/shadow-log/metrics  ([A6] gate)         │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Classification Endpoint                               │ │
│  │  - POST /api/v1/classify                               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌──────────────────────────┐
              │   Triage Agent (LLM)     │
              └──────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
    ┌──────────────────┐      ┌──────────────────┐
    │  System Prompt   │      │  Codebook Loader │
    │  (with codebook) │      │  (25 provisions) │
    └──────────────────┘      └──────────────────┘
              │
              ▼
    ┌──────────────────┐
    │  Claude Sonnet   │
    │  4.6 (Anthropic) │
    └──────────────────┘
              │
              ▼
    ┌──────────────────┐
    │  JSON Response   │
    │  + Reasoning     │
    └──────────────────┘
```

## Files Created

```
adr4-triage-agent/
├── app/
│   ├── __init__.py
│   ├── agent.py              # LLM-based triage agent (§6.3)
│   ├── codebook.py           # Codebook loader and validation
│   ├── database.py           # SQLite shadow log store (§8.2)
│   ├── main.py               # FastAPI app with shadow log API
│   └── models.py             # Pydantic data models (§9)
├── config/
│   └── criteria-codebook.json # 25 clinical provisions from Dr. Webb
├── tests/
│   ├── __init__.py
│   ├── test_agent.py         # Agent unit tests
│   ├── test_api.py           # API endpoint tests
│   └── test_scenarios.py     # Validation scenarios (§10)
├── data/
│   └── shadow_log.db         # SQLite database (created at runtime)
├── .env.example              # Environment variable template
├── .gitignore
├── BUILD_SUMMARY.md          # This file
├── Dockerfile                # Container image
├── docker-compose.yml        # Docker deployment
├── example_classify.py       # Example classification script
├── IMPLEMENTATION_NOTES.md   # Technical details
├── pytest.ini                # Test configuration
├── README.md                 # Main documentation
├── requirements.txt          # Python dependencies
└── run_tests.sh              # Test runner script
```

## Implementation Approach

### LLM-Based Classification (Jupyter Notebook Approach)

The agent sends the claim data to **Claude Sonnet 4.6** (Anthropic) with a **system prompt containing the clinical criteria codebook**. Claude:

1. **Reads the codebook** (25 provisions embedded in system prompt)
2. **Extracts clinical indicators** from claim (ICD-10, CPT, prior auth)
3. **Matches indicators** against codebook patterns
4. **Reasons about clinical appropriateness** (e.g., detects bronchitis + chemo mismatch)
5. **Computes confidence** based on match specificity and clinical coherence
6. **Applies fallback rule** (confidence < 0.70 → CLINICAL_PATH)
7. **Outputs structured JSON** with reasoning trace

**Why Claude?** Excellent at structured reasoning tasks, strong instruction following, native integration with Anthropic tools (Claude Code).

### Example LLM Reasoning

From your Jupyter notebook:

```
"Step 1 — Indicators present: ICD-10 code J20.9 (acute bronchitis), 
 CPT code 96413 (chemotherapy administration)...

 Step 2 — CPT 96413 matches CC-003 (Oncology)...

 Step 4 — Confidence 0.72: exact CPT match to CC-003, but ICD-10 
 diagnosis (J20.9) is acute bronchitis, which is inconsistent with 
 typical oncology chemotherapy indication. This mismatch lowers 
 confidence slightly..."
```

Claude provides **clinical reasoning**, not just pattern matching.

## Key Features Implemented

### Core Agent (app/agent.py)

✅ **System prompt with embedded codebook** (§6.3)  
✅ **6-step classification procedure** defined in prompt  
✅ **Claude-based reasoning** via Anthropic API  
✅ **Structured JSON output** validated by Pydantic  
✅ **Chain-of-thought reasoning traces**  
✅ **Confidence scoring** by LLM (context-aware)  
✅ **Confidence fallback** (< 0.70 → CLINICAL_PATH)  
✅ **NOVEL_CASE guardrail** (unmatched codes → CLINICAL_PATH)  
✅ **Shadow vs. Live mode** switching  
✅ **Precondition validation** (extraction_status = AUTO_COMPLETE)  
✅ **Shadow mode isolation** enforcement  

### Shadow Log Store (app/main.py, app/database.py)

✅ **POST /api/v1/shadow-log** — write agent classification (§8.2)  
✅ **PUT /api/v1/shadow-log/{id}/processor-decision** — update with processor decision  
✅ **GET /api/v1/shadow-log/metrics** — query false-negative rate for [A6] gate  
✅ **GET /api/v1/shadow-log** — list/filter entries  
✅ **SQLite backing store** (no external dependencies)  
✅ **Agreement calculation** (AGREE/DISAGREE)  
✅ **False-negative detection** (agent=FAST_PATH, processor=CLINICAL_PATH)  

### Data Models (app/models.py)

✅ **NormalizedClaimRecord** (input from ADR-1)  
✅ **RoutingDecisionOutput** (agent classification output)  
✅ **RoutingDecisionRecord** (shadow log entry with state machine)  
✅ **CriteriaCodebookEntry** (provision definition)  
✅ **ShadowLogMetrics** ([A6] gate validation response)  
✅ **Enums** (RoutingDecision, RoutingMode, ExtractionStatus, etc.)  

### Codebook (config/criteria-codebook.json)

✅ **25 clinical provisions** from Dr. Webb  
✅ **6 clinical categories** (Diagnostic Imaging, Specialist Auth, Medical Necessity, etc.)  
✅ **ICD-10/CPT trigger patterns** (prefix matching)  
✅ **Prior auth triggers**  
✅ **Effective date / approval metadata**  

### Tests (tests/)

✅ **Unit tests** (test_agent.py): Codebook loading, pattern matching, classification logic  
✅ **API tests** (test_api.py): Shadow log CRUD, metrics calculation, error handling  
✅ **Validation scenarios** (test_scenarios.py): Happy paths, edge cases, failure modes from spec §10  

### Deployment

✅ **Dockerfile** for container image  
✅ **docker-compose.yml** for easy deployment  
✅ **Environment variables** for configuration  
✅ **Health check endpoint**  
✅ **OpenAPI/Swagger docs** at `/docs`  

## Guard Rails Implemented

Per spec §11 (Governance):

1. **Shadow Mode Isolation** (§11.3)
   - MODE declared in system prompt first line
   - Agent validates `routing_mode` matches agent `MODE`
   - Raises `SHADOW_ISOLATION_VIOLATION` if mismatch

2. **Precondition Validation**
   - Rejects claims with `extraction_status != AUTO_COMPLETE`
   - Returns to ADR-1 intake queue if violated

3. **Confidence Fallback** (§6.3)
   - If confidence < 0.70 → override to CLINICAL_PATH
   - Conservative default: err on side of physician review

4. **NOVEL_CASE Guardrail**
   - Unmatched codes → CLINICAL_PATH, confidence=0.0
   - Flag for Dr. Webb adjudication

5. **[A6] Gate Logic** (§11.4)
   - Query: `GET /api/v1/shadow-log/metrics`
   - Conditions: false_negative_rate < 2%, labeled_entries >= 2000
   - Blocks Wave 2 activation until passed

## Testing

**Run all tests:**
```bash
cd adr4-triage-agent
pip install -r requirements.txt
pytest tests/ -v
```

**Run example classification** (requires `OPENAI_API_KEY`):
```bash
export OPENAI_API_KEY="sk-..."
python3 example_classify.py
```

## Deployment

**Local development:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export ADR4_MODE="SHADOW"
uvicorn app.main:app --reload --port 8000
```

**Docker:**
```bash
docker-compose up
```

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Usage Example

**Classify a claim:**
```bash
curl -X POST http://localhost:8000/api/v1/classify \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "test-001",
    "source_claim_ref": "PDF-2026-0441",
    "intake_channel": "CMS1500_PDF",
    "extraction_status": "AUTO_COMPLETE",
    "member_id": "M-4421908",
    "icd10_codes": ["C50.911"],
    "cpt_codes": ["96413"],
    "prior_auth_required": true,
    "prior_auth_number": "PA-001",
    "payer_id": "BX-0042",
    "place_of_service": "22",
    "billed_amount": 4200.00
  }'
```

**Response:**
```json
{
  "claim_id": "test-001",
  "source_claim_ref": "PDF-2026-0441",
  "routing_decision": "CLINICAL_PATH",
  "confidence": 0.95,
  "confidence_fallback": false,
  "clinical_indicators_detected": [
    "ICD-10: C50.911",
    "CPT: 96413",
    "Prior Auth: Required"
  ],
  "criteria_provisions_matched": ["CC-003", "CC-001"],
  "reasoning_trace": "Step 1 — Indicators present: ICD-10 code C50.911 (malignant neoplasm, breast), CPT code 96413 (chemotherapy IV infusion), prior_auth_required = true...",
  "routing_mode": "SHADOW"
}
```

## Cost Estimate

**Per classification:**
- System prompt: ~2,500 tokens (codebook + instructions)
- Claim data: ~200 tokens
- Response: ~300 tokens
- **Total: ~3,000 tokens per claim**

**At scale (1,667 claims/day per spec):**
- **Claude Sonnet 4.6**: ~$25-75/day = **$750-2,250/month** (recommended)
- **Claude Opus 4.7**: ~$125-375/day = **$3,750-11,250/month** (higher accuracy)

## Next Steps (Wave 1 → Wave 2)

1. **Deploy to Wave 1 Shadow Mode**
   - Set `ADR4_MODE=SHADOW`
   - Collect 2,000+ labeled examples
   - Measure false-negative rate

2. **[A6] Gate Validation**
   - Query `/api/v1/shadow-log/metrics`
   - Verify: `false_negative_rate < 0.02`, `labeled_entries >= 2000`
   - 60-day window, Dr. Webb sign-off

3. **Activate Wave 2 Live Mode**
   - Set `ADR4_MODE=LIVE`
   - Enable CMS routing writes
   - Monthly physician audits (5% sample)

## Spec Compliance

✅ **§6.3 Context Engineering Design** — System prompt with codebook, 6-step procedure, few-shot examples  
✅ **§8.2 Shadow Evaluation Log Store** — POST/PUT/GET endpoints, false-negative calculation  
✅ **§9 Entity Data Models** — All models implemented with Pydantic  
✅ **§10 Validation Scenarios** — Happy paths, edge cases, failure modes tested  
✅ **§11 Governance** — Shadow mode isolation, audit trail, [A6] gate logic  

## Technical Decisions

1. **Python + FastAPI** — Fast API development, good for ML/AI workflows
2. **SQLite** — No external DB dependencies, easy testing
3. **Pydantic** — Strong typing, automatic validation
4. **Anthropic Claude API** — LLM inference (Claude Sonnet 4.6 or Opus 4.7)
5. **Docker** — Container deployment, reproducible environments

**Why Claude Sonnet 4.6?**
- Excellent at structured reasoning and instruction following
- Strong JSON output quality
- Cost-effective for production scale (~$0.015-0.045 per claim)
- Native Anthropic integration (using Claude Code with Claude API)

## Documentation

- **README.md** — Quick start, features, API usage
- **IMPLEMENTATION_NOTES.md** — Technical details, LLM approach, cost estimates
- **BUILD_SUMMARY.md** — This file (what was built and why)
- **API Docs** — Auto-generated at `/docs` (OpenAPI/Swagger)

---

**Built by:** Claude Code (Anthropic)  
**Date:** 2026-05-27  
**Spec:** `specs/06b-capability-spec-triage.md`  
**Status:** ✅ Complete and ready for Wave 1 deployment
