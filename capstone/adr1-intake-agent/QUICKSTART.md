# Quick Start Guide

Get ADR-1 running in 5 minutes.

## Prerequisites

- Python 3.11+
- Anthropic API key ([get one here](https://console.anthropic.com/))

## Installation

```bash
cd adr1-intake-agent

# Install dependencies
pip install -e .

# Or if you don't have pip install working:
pip install fastapi uvicorn pydantic anthropic python-dotenv sqlalchemy aiosqlite httpx

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Test It

### Option 1: CLI (fastest)

```bash
# Process example claim
python cli.py process examples/example1_clean_pdf.json
```

Expected output:
```
Processing claim: PDF-2026-0441
Channel: CMS1500_PDF

✓ extraction_status: AUTO_COMPLETE
✓ SLA Queue: STANDARD
✓ Claim ID: <uuid>
✓ Status: QUEUED
```

### Option 2: API Server

```bash
# Start server
python cli.py serve

# In another terminal, submit claim
curl -X POST http://localhost:8000/api/v1/claims/submit \
  -H "Content-Type: application/json" \
  -d @examples/example1_clean_pdf.json

# Check stats
curl http://localhost:8000/api/v1/stats
```

Visit http://localhost:8000/docs for interactive API documentation.

## Example Scenarios

### Clean PDF (AUTO_COMPLETE)
```bash
python cli.py process examples/example1_clean_pdf.json
```
All fields above confidence threshold → queued automatically.

### Low Confidence (HUMAN_REQUIRED)
```bash
python cli.py process examples/example4_low_confidence.json
```
member_id at 0.61 (below 0.85) → human review required.

## What Happens

1. **Extraction result** enters system (from EDI parser or IDP pipeline)
2. **Claude Sonnet 4.6** validates fields and adjusts confidence scores
3. **Agent logic** determines AUTO_COMPLETE or HUMAN_REQUIRED
4. **CMS API** (mocked) writes claim if validated
5. **Response** includes claim_id, extraction_status, low_confidence_fields

## Key Confidence Rules

- **Standard threshold**: 0.85 for most channels
- **OCR threshold**: 0.80 for CMS1500_OCR_TEXT
- **EDI**: No threshold (deterministic parsing)
- **Code validation**: ICD-10 must have decimal, CPT must be 5 digits
- **Identity fallback**: Names can be low if member_id is strong

## Architecture Decisions

**Tech Stack** (my choices per your instructions):
- Python 3.11 + FastAPI (best for AI agents)
- Claude Sonnet 4.6 (cost/capability balance)
- SQLite (simple, persistent mock storage)
- Pydantic (type-safe models)

**What's Mocked**:
- CMS API (in-memory store)
- IDP pipeline (simulated confidence scores)
- EDI parser (simplified)

**What's Real**:
- Claude API integration
- System prompt (full spec Section 6)
- Data models (full spec Section 9)
- Validation logic
- Confidence rules
- Exception routing
- SLA queueing

## Project Structure

```
adr1-intake-agent/
├── src/
│   ├── models/          # Pydantic entities
│   ├── prompts/         # System prompt (versioned)
│   ├── services/        # Agent, validator, queue
│   ├── mocks/           # CMS, IDP, EDI mocks
│   └── api/             # FastAPI app
├── tests/               # Validation scenarios
├── examples/            # Test claims
├── cli.py               # CLI tool
└── README.md            # Full documentation
```

## Next Steps

1. **Try other examples**: Create JSON files for edge cases
2. **Test duplicate detection**: Submit same claim twice
3. **Explore API docs**: http://localhost:8000/docs
4. **Read full spec**: `specs/06a-capability-spec-intake.md`
5. **Run tests**: `python cli.py test`

## Troubleshooting

**No ANTHROPIC_API_KEY**:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

**Import errors**:
```bash
pip install -e .
```

**Can't start server**:
Check port 8000 isn't already in use.

## Production Gaps

This is a **working prototype** per spec. For production, you still need:
- Real EDI 837 parser (Stedi, Centauri)
- Real IDP pipeline (AWS Textract, Google Document AI)
- Real CMS API integration (validate [A12])
- PostgreSQL (not SQLite)
- Redis (for buffering)
- HIPAA-compliant logging
- Monitoring & alerts

But the **core agent logic is production-ready**:
- ✓ Full system prompt
- ✓ Confidence validation
- ✓ Guard rails
- ✓ Exception routing
- ✓ Data models
- ✓ API contracts

---

**Questions?** Check README.md or the full spec in `specs/06a-capability-spec-intake.md`.
