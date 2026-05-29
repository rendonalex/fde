# Claims Pipeline Demo

Two-agent pipeline: **ADR-1 (Intake)** → **ADR-4 (Clinical Content Triage)**

## Prerequisites

```bash
pip install anthropic jupyter
export ANTHROPIC_API_KEY=sk-ant-...
```

## Run

```bash
cd capstone/demo
jupyter notebook claims_pipeline.ipynb
```

Then open the notebook in your browser.

## Files

| File | Purpose |
|------|---------|
| `claims_pipeline.ipynb` | The notebook — run this |
| `preprocessors.py` | IDP field mappers for all 10 supported input formats |
| `prompts.py` | System prompts for ADR-1 and ADR-4 |
| `../test-data/criteria-codebook-mock.json` | 25-provision criteria codebook (co-developed with Dr. Webb) |

## Supported input formats

| Format | Extension | Folder | Notes |
|--------|-----------|--------|-------|
| Portal JSON | `.json` | `portal-json/` | Clean structured data, high confidence |
| FHIR R4 JSON | `.json` | `fhir-r4-json/` | Claim resource; `member_dob` / `plan_id` absent |
| EDI 837P | `.edi` | `edi-837p/` | Professional; confidence omitted (binary fidelity) |
| EDI 837I | `.edi` | `edi-837i/` | Institutional; auto-detected from ST segment |
| CMS-1500 OCR | `.txt` | `cms1500-ocr/` | OCR artifacts, lower confidence |
| CMS-1500 paper PDF | `.pdf` | `cms1500-paper/` | pdfplumber extracts text (simulates OCR service) |
| Email | `.eml` | `email/` | MIME; X-headers preferred over body regex |
| Fax PDF | `.pdf` | `fax/` | pdfplumber + cover sheet regex |
| Fax email | `.txt` | `fax-email/` | Plain RFC 5322; same body parser as email |
| Exception note | `.txt` / `.pdf` | `exception-notes/` | Not a claim; outputs `routing_action` instead of `extraction_status` |

## Cells

| Cell | What it does |
|------|-------------|
| 1 — Config | Set `CLAIM_FILE` and `CODEBOOK_PATH`; verify API key |
| 2 — ADR-1 Step 1: IDP Extraction | Format-specific parsers extract fields and assign per-field confidence scores — no LLM involved; this is the IDP pipeline component of ADR-1 |
| 3 — ADR-1 Step 2: LLM Validation | Claude validates field completeness, applies confidence thresholds, and outputs the NormalizedClaimRecord |
| 4 — Gate check | Print routing decision: HUMAN_REVIEW stops here; AUTO_COMPLETE continues |
| 5 — ADR-4 Triage | (AUTO_COMPLETE only) Call the triage agent; display FAST_PATH / CLINICAL_PATH + reasoning |

## Switching claim files

Change `CLAIM_FILE` in Cell 1 and re-run all cells:

```python
# Portal JSON — clean structured data, high confidence
CLAIM_FILE = "../mock-data/portal-json/CLM-2026-1001201.json"

# EDI 837P — deterministic parse, confidence omitted (binary fidelity), AUTO_COMPLETE if well-formed
CLAIM_FILE = "../mock-data/edi-837p/CLM-2026-1000001.edi"

# EDI 837I — same as 837P; auto-detected from ST segment; claim_type = INSTITUTIONAL
CLAIM_FILE = "../mock-data/edi-837i/CLM-2026-1001001.edi"

# CMS-1500 OCR text — OCR artifacts, lower confidence, may trigger HUMAN_REQUIRED
CLAIM_FILE = "../mock-data/cms1500-ocr/CLM-2026-1001601.txt"

# CMS-1500 paper PDF — pdfplumber extracts text (simulates OCR service); higher confidence than OCR
CLAIM_FILE = "../mock-data/cms1500-paper/CLM-2026-1001601.pdf"

# Email submission — parsed via stdlib email module; X-headers preferred over body regex
CLAIM_FILE = "../mock-data/email/CLM-2026-1001901.eml"

# Fax PDF — pdfplumber + cover sheet regex; lower confidence for fax artifacts
CLAIM_FILE = "../mock-data/fax/CLM-2026-1001931.pdf"

# Fax email (plain text) — RFC 5322 without MIME; same body parser as email
CLAIM_FILE = "../mock-data/fax-email/CLM-2026-1001901.txt"

# FHIR R4 JSON — Claim resource; member_dob and plan_id absent (not in Claim resource)
CLAIM_FILE = "../mock-data/fhir-r4-json/CLM-2026-1001801.json"

# Exception note (text) — not a claim; outputs routing_action instead of extraction_status
CLAIM_FILE = "../mock-data/exception-notes/CLM-2026-1001961.txt"
```

## What is mocked

| Component | Demo | Production |
|-----------|------|-----------|
| IDP pipeline | Python field mappers + simulated confidence scores | Real OCR/NLP service |
| CMS | In-memory (output printed to notebook) | Real CMS API |
| SLA queue | Not implemented | Application layer assigns after agent returns |
| Duplicate check | Not implemented | CMS read API query |

The agents (Claude API calls) are real — not mocked.

## Model

Default model: `claude-haiku-4-5-20251001` (fast, low cost for demo).  
Change `MODEL` in Cell 1 to use `claude-sonnet-4-6` for higher-quality reasoning traces.
