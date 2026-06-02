# Quick Start Guide for Coaches

**Helix Therapeutics Pharmacovigilance AI System**  
**ADR-1 Intake + ADR-2 Triage Pipeline**

---

## Prerequisites

- **Python 3.9 or higher**
- **Anthropic API key** (required for Claude)

---

## Installation (5 minutes)

### Step 1: Extract Package

```bash
# Extract the zip file
unzip fde-adr-pipeline.zip
cd g-week5
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set API Key

```bash
# macOS/Linux
export ANTHROPIC_API_KEY="your-api-key-here"

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your-api-key-here"
```

---

## Run Demos (2 minutes each)

### Demo 1: Single Case Test (ADR-1 → ADR-2)

```bash
python3 test_adr2.py
```

**What it does:**
- Processes one adverse event report through full pipeline
- Shows extraction (ADR-1) and classification (ADR-2) results
- Displays seriousness, expectedness, reportability
- Saves results to `test_adr2_results.json`

---

### Demo 2: Full Test Suite (4 scenarios)

```bash
python3 test_adr2_suite.py
```

**What it does:**
- Runs 4 test cases with validation:
  - HP-01: Happy path (expected, non-serious)
  - EC-01: Edge case (serious + unexpected → 15-day expedited)
  - FM-01: Failure mode (ambiguous seriousness → MSO review)
  - HITL-01: Low confidence → HITL queue
- Shows pass/fail for each validation criterion
- Tests full routing logic

**Expected output:**
```
✅ PASSED: HP-01: Happy Path (Expected, Non-Serious)
✅ PASSED: EC-01: Edge Case (Serious + Unexpected)
✅ PASSED: FM-01: Failure Mode (Ambiguous Seriousness)
✅ PASSED: HITL-01: ADR-1 HITL Routing (Low Confidence)

Total: 4/4 tests passed
🎉 ALL TESTS PASSED
```

---

### Demo 3: Batch Processing (Workflow Orchestrator)

```bash
python3 workflow/orchestrator.py
```

**What it does:**
- Processes all test files in `mock-data/test-adr2/`
- Routes cases through ADR-1 → ADR-2 pipeline
- Generates summary statistics:
  - Success rates
  - Routing distribution (ADR-2, HITL, duplicates)
  - Reportability breakdown (15-day expedited, periodic, non-reportable)
  - MSO deep review queue
  - Signal detections
- Saves full results to `workflow_results.json`

**Expected output:**
```
**Total Cases Processed:** 5
**ADR-1 Success Rate:** 100%
**Routing:** 3 to ADR-2, 1 to HITL, 1 duplicate
**Reportability:** 1 expedited (15-day), 1 periodic, 1 non-reportable
**MSO Deep Review Required:** 2 cases
```

---

### Demo 4: Run Individual Test

```bash
python3 test_single.py EC-01
```

**Available tests:**
- `HP-01` - Happy path
- `EC-01` - Edge case (serious + unexpected)
- `FM-01` - Failure mode (ambiguous)
- `HITL-01` - HITL routing test

---

## Key Files to Review

### Documentation
- **README.md** - Complete system documentation
- **AGENT_BUILD_SUMMARY.md** - Technical build summary
- **deliverables/05a-capability-spec-intake.md** - ADR-1 specification
- **deliverables/05b-capability-spec-triage.md** - ADR-2 specification
- **deliverables/10-amendments-post-build.md** - Post-build amendments

### Test Data
- **mock-data/test-adr2/** - 4 test cases with expected outcomes
- **mock-data/product-information/** - RSI files (Tezarimab, Solivian, Phaedora)
- **mock-data/hcp-reports/** - Healthcare professional reports
- **mock-data/patient-reports/** - Patient webforms

### Code
- **agents/adr1_intake.py** - ADR-1 intake agent (~550 lines)
- **agents/adr2_triage.py** - ADR-2 triage agent (~400 lines)
- **agents/models.py** - Entity models (~600 lines)
- **workflow/orchestrator.py** - Pipeline orchestrator (~350 lines)

---

## Understanding the Output

### ADR-1 Output (Intake)

```python
{
  "patient": {"age": 62, "sex": "F", "confidence": 0.95},
  "suspect_drug": {"name": "tezarimab", "dose": "500 mg IV", "confidence": 0.95},
  "ae_description": {"narrative": "severe DILI...", "confidence": 0.90},
  "extraction_status": "AUTO_COMPLETE",
  "routing_decision": "ADR-2"
}
```

**Routing Logic:**
- `AUTO_COMPLETE` → Goes to ADR-2
- `HUMAN_REQUIRED` → Goes to HITL queue (confidence <0.85)
- `PENDING_DUPLICATE` → Manual duplicate review
- `EXCEPTION_NOTE` → Exception queue (out-of-scope)

---

### ADR-2 Output (Triage)

```python
{
  "seriousness": {
    "serious": true,
    "criteria_matched": ["hospitalization"],
    "confidence": 0.90
  },
  "expectedness": {
    "unexpected": true,
    "rsi_match": "none",  # Novel AE (not in RSI)
    "confidence": 0.95
  },
  "reportability": {
    "recommendation": "15_DAY_EXPEDITED",  # Serious + unexpected
    "jurisdictions": ["FDA"],
    "confidence": 0.90
  },
  "mso_flags": {
    "deep_review_required": true,
    "reason": ["novel_ae_term"]
  }
}
```

**Reportability Logic:**
- **Serious + Unexpected** → `15_DAY_EXPEDITED` (FDA 21 CFR 314.80)
- **Serious + Expected** → `PERIODIC` (quarterly report)
- **Non-serious** → `NON_REPORTABLE`

**MSO Deep Review Triggers:**
- Novel AE term (not in product RSI)
- Ambiguous seriousness (confidence <0.70)
- Signal detected (3-cases-in-90-days pattern)

---

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
```bash
# Make sure you exported the API key
export ANTHROPIC_API_KEY="your-key-here"

# Verify it's set
echo $ANTHROPIC_API_KEY
```

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
# Install dependencies
pip install -r requirements.txt
```

### "No such file or directory"
```bash
# Make sure you're in the project root
cd g-week5
ls  # Should see: agents/ workflow/ mock-data/ README.md
```

### Test Failures
- Check test file headers for expected outcomes
- Review confidence thresholds (0.85 for ADR-1, 0.70 for ADR-2)
- Validate RSI files are present in `mock-data/product-information/`

---

## Next Steps After Demo

1. **Review Test Cases**: Look at test files in `mock-data/test-adr2/` to understand scenarios
2. **Check Results**: Open `workflow_results.json` to see full JSON output
3. **Read Specifications**: Review `deliverables/05a-capability-spec-intake.md` and `05b-capability-spec-triage.md`
4. **Explore Code**: Start with `workflow/orchestrator.py` to understand pipeline flow

---

## Architecture Overview

```
Raw AE Report (text, JSON, VTT, PDF)
    ↓
┌─────────────────────────────────────────┐
│ ADR-1: INTAKE & EXTRACTION              │
│ - Extract structured data (ICH E2D)     │
│ - Confidence scoring (per-field)        │
│ - RxNorm/MedDRA normalization          │
│ - Duplicate detection                   │
└─────────────────────────────────────────┘
    ↓
    ├─ Confidence ≥0.85 → AUTO_COMPLETE
    └─ Confidence <0.85 → HUMAN_REQUIRED → HITL Queue
    ↓
┌─────────────────────────────────────────┐
│ ADR-2: TRIAGE & CLASSIFICATION          │
│ - Seriousness (ICH E2A criteria)        │
│ - Expectedness (RSI matching)           │
│ - Reportability (FDA 21 CFR 314.80)     │
│ - Signal detection (3-in-90-days)       │
│ - MSO review flags                      │
└─────────────────────────────────────────┘
    ↓
    ├─ 15_DAY_EXPEDITED → FDA Reporting Queue
    ├─ PERIODIC → Quarterly Report
    ├─ MSO Deep Review → MSO Queue
    └─ NON_REPORTABLE → Close Case
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| **ADR-1 Success Rate** | 100% (5/5 test cases) |
| **Throughput** | 8-12 sec/case (vs. 40-45 min manual) |
| **Token Cost** | ~$0.10/case |
| **Autonomy** | 80% (4/5 passed ADR-1 without HITL) |
| **FDA Compliant** | ✅ All 5 FDA May 2026 requirements |

---

## Contact

For questions or issues:
- Review `README.md` for detailed documentation
- Check `AGENT_BUILD_SUMMARY.md` for technical details
- Review test file headers for expected classification outcomes

---

**Version:** 1.0  
**Last Updated:** 2026-06-01  
**Model:** Claude Sonnet 4.6
