# LLM Edge-Case Claims

Three claims designed to test scenarios where an LLM adds value over a rules engine.

---

## CLM-2026-9001.json — Prior auth required but empty auth number

**Format:** Portal JSON  
**Scenario:** The claim has `prior_auth_number: ""` (empty string). The preprocessor infers `prior_auth_required = true` because the field is present (not null). A rules engine that checks `prior_auth_number == null` would incorrectly pass this claim as AUTO_COMPLETE. The LLM recognizes that an empty string is not a valid auth number and should route HUMAN_REQUIRED.

| What a rules engine does | What the LLM does |
|---|---|
| `prior_auth_number != null` → passes → AUTO_COMPLETE | Empty string = effectively missing → HUMAN_REQUIRED |

Expected ADR-1 output: **HUMAN_REQUIRED** (prior_auth_number flagged)  
ADR-4: not called

---

## CLM-2026-9002.txt — OCR artifacts: incomplete ICD-10 + truncated CPT

**Format:** CMS-1500 OCR  
**Scenario:** Two OCR artifacts introduced by the scanner:
- ICD-10 `J06.9` scanned as `J06 .9` (space before decimal) → preprocessor extracts `J06` (category code only, not a billable subcategory)
- CPT `99210` scanned as `9921 0` (digit split by space) → preprocessor extracts `9921` (4-digit truncation)

Both extracted values pass the 0.80 confidence threshold because they are present. A rules engine has no way to know `J06` is incomplete or `9921` is truncated — it just checks presence and threshold. The LLM has medical knowledge and can recognize that `J06` without a decimal subcategory is a category header, not a billable code, and that `9921` is not a valid 5-digit CPT code.

| What a rules engine does | What the LLM does |
|---|---|
| Fields present, confidence 0.80 ≥ threshold 0.80 → AUTO_COMPLETE | Recognizes `J06` and `9921` are malformed → HUMAN_REQUIRED |

Expected ADR-1 output: **HUMAN_REQUIRED** (icd10_codes and/or cpt_codes flagged)  
ADR-4: not called

---

## CLM-2026-9003.json — Clinical implausibility: chemotherapy CPT + respiratory diagnosis

**Format:** Portal JSON  
**Scenario:** CPT `96413` (chemotherapy infusion — an oncology procedure) is billed against ICD-10 `J20.9` (acute bronchitis — a respiratory infection, not cancer). All required fields are present and all confidence scores are high (0.96–0.99). A rules engine and ADR-1 both route this AUTO_COMPLETE — there are no extraction problems. The clinical mismatch is caught by ADR-4, which matches CPT `96413` against provision CC-003 (Oncology) and routes CLINICAL_PATH.

| What a rules engine does | What ADR-4 LLM does |
|---|---|
| All fields present → AUTO_COMPLETE, no further check | CPT 96413 hits CC-019 (Biologic/Specialty Drug codebook provision) → CLINICAL_PATH |

Expected ADR-1 output: **AUTO_COMPLETE**  
Expected ADR-4 output: **CLINICAL_PATH** (CC-019 — Biologic and Specialty Drug Administration)
