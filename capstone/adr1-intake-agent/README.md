# ADR-1 Claim Intake and Format Validation Agent

AI-powered claim intake agent for Greenfield Health Systems, built per specification `specs/06a-capability-spec-intake.md`.

## Architecture

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **AI Model**: Claude Sonnet 4.6
- **Database**: SQLite (mocked integrations)
- **Agent Type**: Agent-led + Human Oversight

## Components

1. **Data Models** (`src/models/`)
   - `NormalizedClaimRecord` - canonical claim schema
   - `ExceptionQueueEntry` - HITL routing
   - `AuditLogEntry` - audit trail
   - Enums for all status values

2. **System Prompt** (`src/prompts/system_prompt.py`)
   - Versioned prompt template (1.1.0-demo)
   - Confidence adjustment rules
   - Required field validation logic
   - Few-shot examples

3. **Mock Integrations** (`src/mocks/`)
   - `MockCMSAPI` - Claims Management System
   - `EDI837Parser` - EDI 837P/I parser
   - `MockIDPPipeline` - IDP extraction

4. **Core Agent** (`src/services/agent.py`)
   - Claude API integration
   - Extraction processing
   - Confidence validation

5. **FastAPI Service** (`src/api/app.py`)
   - `/api/v1/claims/submit` - submit claim
   - `/api/v1/claims/{claim_id}` - get claim
   - `/api/v1/stats` - processing stats

## Setup

1. **Install dependencies**:
   ```bash
   cd adr1-intake-agent
   pip install -e .
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

3. **Create data directory**:
   ```bash
   mkdir -p data
   ```

## Usage

### Start API Server
```bash
python cli.py serve
```

Visit http://localhost:8000/docs for interactive API documentation.

### Process a Claim (CLI)
```bash
python cli.py process examples/example1_clean_pdf.json
```

### Run Tests
```bash
python cli.py test
```

## Example Request

```json
{
  "extraction_result": {
    "source_format": "PDF",
    "source_claim_ref": "PDF-2026-0441",
    "intake_channel": "CMS1500_PDF",
    "extracted_fields": {
      "member_id": {"value": "M-4421908", "confidence": 0.97},
      "member_name_last": {"value": "Thompson", "confidence": 0.96},
      "member_name_first": {"value": "Alice", "confidence": 0.96},
      "date_of_service_start": {"value": "2026-04-11", "confidence": 0.97},
      "date_of_service_end": {"value": "2026-04-11", "confidence": 0.97},
      "claim_type": {"value": "PROFESSIONAL", "confidence": 0.99},
      "icd10_codes": {"value": ["Z00.00"], "confidence": 0.92},
      "cpt_codes": {"value": ["99213"], "confidence": 0.94},
      "payer_name": {"value": "Blue Cross PPO", "confidence": 0.95},
      "prior_auth_required": {"value": false, "confidence": 0.97}
    }
  }
}
```

## Key Features

✓ **Confidence Boosting**: LLM validates and adjusts preprocessor confidence scores  
✓ **Code Validation**: ICD-10 decimal check, CPT 5-digit validation  
✓ **Identity Fallback**: member_id-only routing when names are low-confidence  
✓ **Duplicate Detection**: Prevents duplicate CMS writes  
✓ **SLA-Aware Queueing**: PRIORITY/STANDARD tiers  
✓ **Audit Trail**: All processing events logged  

## Guardrails

- Required field confidence < 0.85 → HUMAN_REQUIRED (0.80 for OCR text)
- Malformed ICD-10 (no decimal) or CPT (not 5 digits) → HUMAN_REQUIRED
- CMS API failure → local buffer + retry with idempotency key
- Duplicate claim → PENDING_DUPLICATE status

## Validation Scenarios

Implements all 12 edge cases from spec Section 10:
- Happy path EDI 837
- PDF low confidence extraction
- Duplicate detection
- Identity fallback rule
- OCR confidence boosting
- And more...

## Production Readiness

### Still Needed for Production:
- [ ] Real EDI 837 parser integration
- [ ] Real IDP pipeline (AWS Textract, Google Document AI)
- [ ] Real CMS API integration (confirm [A12])
- [ ] PostgreSQL instead of SQLite
- [ ] Redis for claim buffering
- [ ] Prometheus metrics
- [ ] Distributed tracing
- [ ] HIPAA-compliant audit log storage

### Already Implemented:
- ✓ Complete data models per spec
- ✓ System prompt with versioning
- ✓ Claude API integration
- ✓ Confidence validation logic
- ✓ Exception routing
- ✓ Duplicate detection
- ✓ SLA queueing
- ✓ FastAPI service
- ✓ Test scaffolding

## Wave 1 Integration

ADR-1 is the foundation for all Wave 2+ agents:
- **ADR-4** (Clinical Triage) reads `NormalizedClaimRecord`
- **ADR-2** (Eligibility) resolves optional intake fields
- **ADR-5** (Fast Path) consumes validated claims
- All agents share CMS API, audit log, queue module

## References

- Full spec: `specs/06a-capability-spec-intake.md`
- Assumptions: `specs/assumptions.md` ([A12], [A14], [A17], [A21])
- CLAUDE.md: `specs/CLAUDE.md`
- Entity models: spec Section 9
- System prompt: spec Section 6
- Validation scenarios: spec Section 10

## License

Proprietary - Greenfield Health Systems AI Claims Processing Transformation
