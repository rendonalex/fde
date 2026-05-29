# ADR-4 Implementation Notes

## Classification Approach: LLM + Codebook

This implementation follows the **Jupyter notebook approach**: the LLM receives the clinical criteria codebook via the system prompt and performs reasoning to classify claims.

### How It Works

1. **System Prompt Construction** (§6.3 of spec)
   - Clinical criteria codebook embedded in system prompt
   - 6-step classification procedure defined
   - Few-shot examples included
   - Mode (SHADOW/LIVE), threshold, and guardrails specified

2. **Classification Flow**
   ```
   Claim Data → LLM (with codebook in context) → Structured JSON Response
   ```

3. **LLM Reasoning** (example from your Jupyter notebook)
   ```
   "Step 1 — Indicators present: ICD-10 code J20.9 (acute bronchitis), 
    CPT code 96413 (chemotherapy administration)...
    
    Step 2 — CPT 96413 matches CC-003 (Oncology)...
    
    Step 4 — Confidence 0.72: exact CPT match to CC-003, but ICD-10 
    diagnosis (J20.9) is acute bronchitis, which is inconsistent with 
    typical oncology chemotherapy indication. This mismatch lowers 
    confidence slightly..."
   ```

### Why LLM + Codebook (Not Just Pattern Matching)?

**Clinical Reasoning**: The LLM can detect:
- **Code mismatches**: Bronchitis (J20.9) + Chemotherapy (96413) = suspicious
- **Clinical appropriateness**: Routine diagnosis with complex procedure
- **Context-aware confidence**: Adjusts confidence based on clinical logic

**Pattern matching alone** would just see "96413 matches CC-003" without the clinical judgment.

## LLM-Only Implementation

The agent uses **LLM-based classification exclusively** (Jupyter notebook approach):

**Usage:**
```python
agent = TriageAgent(mode="SHADOW", confidence_threshold=0.70)
result = agent.classify(claim)
```

**Requires:**
- `ANTHROPIC_API_KEY` environment variable
- Anthropic API access (Claude Sonnet 4.6 or Claude Opus 4.7)

**Advantages:**
- ✅ **Excellent at structured reasoning** - Claude excels at multi-step procedures
- ✅ Clinical reasoning and context awareness
- ✅ Handles ambiguous cases gracefully
- ✅ Detects code mismatches (e.g., bronchitis + chemo)
- ✅ Nuanced confidence scoring
- ✅ Matches spec §6.3 design exactly
- ✅ Same approach as Jupyter notebook
- ✅ **Native Anthropic integration** - using Claude Code with Claude API

**Considerations:**
- API key required
- Claude Sonnet 4.6: ~$0.015-0.045 per claim (3M in, 4M out @ $3/$15 per MTok)
- Claude Opus 4.7: ~$0.075-0.225 per claim (higher accuracy, higher cost)
- Network latency (~2-5 seconds per claim)
- Set temperature=0.0 for consistency

## API Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/classify \
  -H "Content-Type: application/json" \
  -d '{ "claim_id": "...", "icd10_codes": [...], ... }'
```

## Example Output (LLM Mode)

```json
{
  "claim_id": "example-002",
  "source_claim_ref": "EDI-20260412-00417",
  "routing_decision": "CLINICAL_PATH",
  "confidence": 0.95,
  "confidence_fallback": false,
  "clinical_indicators_detected": [
    "ICD-10: C50.911",
    "ICD-10: Z79.899",
    "CPT: 96413",
    "CPT: 96415",
    "Prior Auth: Required"
  ],
  "criteria_provisions_matched": [
    "CC-003",
    "CC-001",
    "CC-006"
  ],
  "reasoning_trace": "Step 1 — Indicators present: ICD-10 codes C50.911 (malignant neoplasm, breast), Z79.899 (long-term drug therapy), CPT codes 96413 (chemotherapy IV infusion), 96415 (additional hour), prior_auth_required = true. Step 2 — ICD-10 C50.911 matches CC-003 (Oncology) trigger patterns (C0-C9 prefixes); Z79.899 matches CC-006 (Complex Chronic Disease); CPT 96413 and 96415 match CC-003 chemotherapy administration codes; prior_auth_required = true matches CC-001. Step 3 — Multiple provisions matched (CC-001, CC-003, CC-006); routing_decision = CLINICAL_PATH. Step 4 — Confidence 0.95: strong clinical coherence — breast cancer diagnosis with appropriate chemotherapy codes and prior authorization. All indicators align with oncology treatment protocol. Step 5 — 0.95 >= 0.70 threshold; no fallback needed. Step 6 — Final decision: CLINICAL_PATH, routing_mode = SHADOW.",
  "routing_mode": "SHADOW"
}
```

## Testing

**Run all tests:**
```bash
pytest tests/ -v
```

**Run example classification:**
```bash
# Requires ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY="sk-ant-..."
python3 example_classify.py
```

**Note:** Tests that call Claude are marked with `@pytest.mark.skip` to avoid requiring API keys in CI/CD. Remove the skip decorator to test with real Claude API calls.

## Deployment Considerations

### Production (Wave 1 Shadow Mode)
- Claude Sonnet 4.6 for all classifications (recommended)
- Monitor API costs (~$0.015-0.045 per claim with Sonnet)
- Set `temperature=0.0` for consistency
- Consider Claude Opus 4.7 for higher accuracy on complex cases
- Anthropic prompt caching reduces cost for repeated system prompts

### Testing / CI/CD
- Mock LLM responses for fast unit tests
- Use test API key for integration tests
- Most tests skip LLM calls by default (remove `@pytest.mark.skip` to enable)

### Wave 2 Live Mode
- Switch `ADR4_MODE=LIVE` after [A6] gate passes
- Keep LLM-based reasoning for clinical safety
- Monitor false-negative rate monthly (5% sample audit)

## Guard Rails

✅ **Shadow mode isolation**: Validates `routing_mode` matches agent `MODE`  
✅ **Precondition check**: Rejects claims with `extraction_status != AUTO_COMPLETE`  
✅ **Confidence fallback**: `confidence < 0.70` → override to `CLINICAL_PATH`  
✅ **Novel case guardrail**: Unmatched codes → `CLINICAL_PATH`, confidence=0.0  
✅ **Conservative default**: When in doubt, route to `CLINICAL_PATH`

## Cost Estimate (LLM Mode)

**Per classification:**
- System prompt: ~2,500 tokens (codebook + instructions)
- Claim data: ~200 tokens
- Response: ~300 tokens
- **Total: ~3,000 tokens per claim**

**At scale (1,667 claims/day per spec):**
- **Claude Sonnet 4.6** (recommended): ~$25-75/day = **$750-2,250/month**
  - Input: 2,700 tokens × $3/MTok = $0.0081 per claim
  - Output: 300 tokens × $15/MTok = $0.0045 per claim
  - Total: ~$0.013-0.045 per claim
  
- **Claude Opus 4.7** (higher accuracy): ~$125-375/day = **$3,750-11,250/month**
  - Input: 2,700 tokens × $15/MTok = $0.0405 per claim
  - Output: 300 tokens × $75/MTok = $0.0225 per claim
  - Total: ~$0.063-0.225 per claim

**Optimization:**
- Anthropic prompt caching: 50% cost reduction on cached system prompt
- Parallel processing: Process multiple claims concurrently
- Sonnet 4.6 recommended: Best accuracy/cost balance for this use case

## Next Steps

1. **Wave 1 Shadow Mode Deployment**
   - Deploy with LLM mode enabled
   - Collect 2,000+ labeled examples
   - Measure false-negative rate toward [A6] gate (<2%)

2. **Wave 2 Live Mode** (after gate passes)
   - Switch to `MODE=LIVE`
   - Enable CMS routing writes
   - Monthly physician audits (5% sample)

3. **Optimization**
   - Enable prompt caching for system prompt (Anthropic feature)
   - Fine-tune on labeled examples from Wave 1 if needed
   - Consider Claude Opus 4.7 for critical cases requiring highest accuracy
