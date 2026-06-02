"""
ADR-1: AE Intake & Data Extraction Agent

Fully agentic intake and extraction agent that:
1. Receives heterogeneous AE reports (text, JSON, VTT)
2. Extracts structured data per ICH E2D standards
3. Generates per-field confidence scores with span-level citations
4. Routes to ADR-2 triage (AUTO_COMPLETE) or HITL validation (HUMAN_REQUIRED)
5. Complies with FDA May 2026 Guidance (source documents, model version tracking)
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from anthropic import Anthropic

from .models import (
    AECasePackage, Patient, SuspectDrug, AEDescription, Temporal,
    ConcomitantMed, MedicalHistory, SpanCitation, SourceDocument,
    ExtractionStatus, validate_extraction_complete
)
from .mock_apis import (
    MockRxNormAPI, MockMedDRAAPI, MockPVCaseManagementAPI,
    generate_source_document
)
from .utils import (
    estimate_confidence_from_context, find_span_in_text,
    parse_ambiguous_date, validate_date_consistency,
    classify_report_format, extract_received_timestamp,
    normalize_product_name
)


# Model version for FDA Requirement 1
MODEL_VERSION = "ADR-1 v1.0"


class ADR1IntakeAgent:
    """
    ADR-1 Intake and Data Extraction Agent.

    Handles heterogeneous AE reports, extracts structured data with confidence scoring,
    and routes cases based on extraction quality.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        rxnorm_api: Optional[MockRxNormAPI] = None,
        meddra_api: Optional[MockMedDRAAPI] = None,
        pv_api: Optional[MockPVCaseManagementAPI] = None,
        simulate_failures: bool = False
    ):
        """
        Initialize ADR-1 agent.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            rxnorm_api: RxNorm API instance (mock or real)
            meddra_api: MedDRA API instance (mock or real)
            pv_api: PV Case Management API instance (mock or real)
            simulate_failures: If True, APIs simulate occasional failures
        """
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

        # Initialize mock APIs
        self.rxnorm_api = rxnorm_api or MockRxNormAPI(simulate_failures=simulate_failures)
        self.meddra_api = meddra_api or MockMedDRAAPI(simulate_failures=simulate_failures)
        self.pv_api = pv_api or MockPVCaseManagementAPI(simulate_failures=simulate_failures)

        self.simulate_failures = simulate_failures

    def process_report(self, filename: str, content: str) -> Dict[str, Any]:
        """
        Process a single AE report through full extraction pipeline.

        Args:
            filename: Source filename
            content: Report content (text, JSON, or VTT)

        Returns:
            Dictionary with:
                - case_package: AECasePackage (Pydantic model)
                - extraction_log: Detailed extraction steps and decisions
                - routing_decision: Where case should go next
        """
        log = []
        log.append(f"[ADR-1] Processing report: {filename}")

        # Step 1: Classify format
        format_type = classify_report_format(filename, content)
        log.append(f"[ADR-1] Format classified: {format_type}")

        # Step 2: Extract received_at timestamp
        received_at = extract_received_timestamp(content, filename)
        log.append(f"[ADR-1] Receipt timestamp: {received_at}")

        # Step 3: Generate source document metadata (FDA Requirement 1)
        source_doc = generate_source_document(filename, content, received_at)
        log.append(f"[ADR-1] Source document SHA-256: {source_doc['sha256_hash'][:16]}...")

        # Step 4: Extract structured data using Claude
        log.append("[ADR-1] Calling Claude API for extraction...")
        extraction_result = self._extract_with_claude(content, format_type, received_at)

        if extraction_result["status"] == "error":
            log.append(f"[ADR-1] Extraction failed: {extraction_result['error']}")
            return {
                "case_package": None,
                "extraction_log": log,
                "routing_decision": "EXCEPTION_NOTE",
                "error": extraction_result["error"]
            }

        extracted_data = extraction_result["data"]
        log.append("[ADR-1] Extraction complete")

        # Step 5: Normalize drug names via RxNorm
        if extracted_data.get("suspect_drug", {}).get("name"):
            drug_name = extracted_data["suspect_drug"]["name"]
            rxnorm_response = self.rxnorm_api.lookup_rxcui(drug_name)

            if rxnorm_response.status_code == 200:
                rxcui = rxnorm_response.data["idGroup"]["rxnormId"][0]
                extracted_data["suspect_drug"]["rxnorm_code"] = rxcui
                log.append(f"[ADR-1] RxNorm lookup: {drug_name} -> RxCUI {rxcui}")
            else:
                extracted_data["suspect_drug"]["rxnorm_code"] = None
                log.append(f"[ADR-1] RxNorm lookup failed: {rxnorm_response.error_message}")

        # Step 6: Code AE terms via MedDRA
        if extracted_data.get("ae_description", {}).get("narrative"):
            ae_narrative = extracted_data["ae_description"]["narrative"]
            # Extract key AE terms for MedDRA lookup
            ae_terms = self._extract_ae_terms(ae_narrative)

            if ae_terms:
                meddra_response = self.meddra_api.search_preferred_term(ae_terms[0])

                if meddra_response.status_code == 200:
                    extracted_data["ae_description"]["meddra_pt"] = meddra_response.data["preferred_term"]
                    extracted_data["ae_description"]["meddra_code"] = meddra_response.data["meddra_code"]
                    log.append(f"[ADR-1] MedDRA coding: {ae_terms[0]} -> {meddra_response.data['preferred_term']} ({meddra_response.data['meddra_code']})")
                else:
                    extracted_data["ae_description"]["meddra_pt"] = None
                    extracted_data["ae_description"]["meddra_code"] = None
                    log.append(f"[ADR-1] MedDRA lookup failed: {meddra_response.error_message}")

        # Step 7: Validate scope (marketed products only)
        drug_name = extracted_data.get("suspect_drug", {}).get("name", "")
        product = normalize_product_name(drug_name)

        if not product:
            log.append(f"[ADR-1] Out-of-scope product: {drug_name} -> EXCEPTION_NOTE")
            extracted_data["extraction_status"] = ExtractionStatus.EXCEPTION_NOTE
        else:
            log.append(f"[ADR-1] In-scope product: {product}")

        # Step 8: Check for duplicate cases
        if extracted_data.get("extraction_status") != ExtractionStatus.EXCEPTION_NOTE:
            # Convert age to string for duplicate search
            patient_age = extracted_data.get("patient", {}).get("age")
            patient_identifier = str(patient_age) if patient_age else None

            duplicate_check = self.pv_api.search_duplicates(
                patient_name=patient_identifier,  # Using age as simplified identifier
                drug_name=drug_name,
                ae_term=ae_narrative[:50] if ae_narrative else None
            )

            if duplicate_check.status_code == 200 and duplicate_check.data["total_count"] > 0:
                matches = duplicate_check.data["matches"]
                high_confidence_match = any(m["fuzzy_match_score"] >= 0.8 for m in matches)

                if high_confidence_match:
                    log.append(f"[ADR-1] High-confidence duplicate detected -> PENDING_DUPLICATE")
                    extracted_data["extraction_status"] = ExtractionStatus.PENDING_DUPLICATE

        # Step 9: Build AECasePackage
        try:
            case_package = self._build_case_package(
                extracted_data,
                source_doc,
                received_at,
                format_type
            )
            log.append(f"[ADR-1] AECasePackage created: {case_package.case_id}")

            # Step 10: Determine routing based on extraction status
            routing = self._determine_routing(case_package, log)

            # Step 11: Write to PV system if AUTO_COMPLETE
            if routing == "ADR-2" and case_package.extraction_status == ExtractionStatus.AUTO_COMPLETE:
                write_response = self.pv_api.write_case(case_package.model_dump(mode='json'))

                if write_response.status_code in [200, 201]:
                    log.append(f"[ADR-1] Case written to PV system: {write_response.data['status']}")
                else:
                    log.append(f"[ADR-1] PV API write failed: {write_response.error_message}")
                    routing = "BUFFER_LOCAL"

            return {
                "case_package": case_package,
                "extraction_log": log,
                "routing_decision": routing,
                "error": None
            }

        except Exception as e:
            log.append(f"[ADR-1] Error building case package: {str(e)}")
            return {
                "case_package": None,
                "extraction_log": log,
                "routing_decision": "EXCEPTION_NOTE",
                "error": str(e)
            }

    def _extract_with_claude(
        self,
        content: str,
        format_type: str,
        received_at: str
    ) -> Dict[str, Any]:
        """
        Extract structured data from report using Claude API.

        Returns:
            {
                "status": "success" | "error",
                "data": extracted_data_dict,
                "error": error_message (if status == "error")
            }
        """
        system_prompt = self._build_system_prompt()

        user_message = f"""Extract structured adverse event data from this {format_type} report:

---
{content}
---

Receipt timestamp: {received_at}

Extract all ICH E2D required fields with per-field confidence scores (0.0-1.0).
Generate span citations linking each extracted value to source text location (character indices).

Output valid JSON matching the schema in your system prompt.
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",  # Claude Sonnet 4.6
                max_tokens=4096,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Extract JSON from response
            response_text = response.content[0].text

            # Try to parse JSON (may be wrapped in markdown code blocks)
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try direct parsing
                json_str = response_text.strip()

            extracted_data = json.loads(json_str)

            return {
                "status": "success",
                "data": extracted_data,
                "error": None
            }

        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "data": None,
                "error": f"Failed to parse JSON from Claude response: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "error": f"Claude API error: {str(e)}"
            }

    def _build_system_prompt(self) -> str:
        """
        Build system prompt for Claude extraction.

        Includes:
        - Role and purpose
        - ICH E2D schema
        - Confidence scoring rules
        - Few-shot examples
        - Output schema with FDA fields
        """
        return """You are an adverse event intake and extraction agent for Helix Therapeutics pharmacovigilance system.

Your job: Extract structured data from heterogeneous AE reports per ICH E2D standards, generate per-field confidence scores, and flag low-confidence extractions for human validation.

## EXTRACTION SCHEMA (ICH E2D Required Fields)

Extract these fields:

**Patient Demographics:**
- age (years, integer, optional)
- sex (REQUIRED: must be "M", "F", or "Unknown" - never null. If not stated, use "Unknown")
- weight (kg, float, optional)
- race (when reported, optional)
- confidence (0.0-1.0)

**Suspect Drug:**
- name (generic preferred, brand acceptable)
- dose (with unit, e.g., "150 mg")
- route (e.g., "oral", "IV", "subcutaneous")
- indication (why patient taking drug)
- confidence (0.0-1.0)

**AE Description:**
- narrative (free-text description)
- onset_date (ISO date format YYYY-MM-DD, estimate if needed)
- outcome (recovered/recovering/not_recovered/fatal/unknown)
- confidence (0.0-1.0)

**Temporal Relationships:**
- drug_start_date (ISO date YYYY-MM-DD)
- ae_onset_date (ISO date YYYY-MM-DD)
- outcome_date (ISO date YYYY-MM-DD, optional)
- date_estimated (boolean: true if any date was estimated from ambiguous text like "a few weeks ago")
- confidence (0.0-1.0)

**Concomitant Medications:** (array)
- name
- dose (optional)
- route (optional)
- confidence (0.0-1.0)

**Medical History:** (optional)
- narrative (free-text)
- confidence (0.0-1.0)

**Span Citations:** (for each extracted field)
- field_name: { "value": "extracted_value", "source_span": "start_char-end_char" }

## CONFIDENCE SCORING RULES

**High Confidence (0.85-0.95):**
- Explicit field labels present ("Patient:", "Suspect Drug:")
- Unambiguous structured data (JSON, clear formatting)
- Exact values with no interpretation needed

**Medium Confidence (0.70-0.84):**
- Implicit extraction from narrative text
- Some ambiguity but reasonable inference
- Estimated dates with clear context

**Low Confidence (0.50-0.69):**
- Highly ambiguous or conflicting information
- Multiple possible interpretations
- Missing critical context

**Thresholds:**
- Required fields confidence < 0.85 → set extraction_status: "HUMAN_REQUIRED"
- Concomitant meds confidence < 0.80 → set extraction_status: "HUMAN_REQUIRED"
- Optional fields confidence < 0.70 → log but do not block
- All required fields confidence >= 0.85 → set extraction_status: "AUTO_COMPLETE"

## EXTRACTION STATUS VALUES (use exactly these strings)

- "AUTO_COMPLETE" - all required fields have confidence >= 0.85
- "HUMAN_REQUIRED" - any required field has confidence < 0.85 (needs case processor re-key)
- "PENDING_DUPLICATE" - duplicate case detected (system sets this, not agent)
- "EXCEPTION_NOTE" - out-of-scope product or unprocessable report
- "REPORTER_FOLLOWUP" - missing minimum required information (no patient AND no drug)

## GUARDRAILS

- If no patient identifier AND no suspect drug → extraction_status: "REPORTER_FOLLOWUP"
- If out-of-scope product (not Solivian/Tezarimab/Phaedora) → extraction_status: "EXCEPTION_NOTE"
- If any required field confidence < 0.85 → extraction_status: "HUMAN_REQUIRED"
- If ambiguous date ("a few weeks ago") → estimate date, set date_estimated: true
- Always generate span citations for required fields

## OUTPUT SCHEMA

CRITICAL: Output ONLY valid JSON. No markdown code blocks, no explanations, just the JSON object.

IMPORTANT:
- sex field is REQUIRED and must be "M", "F", or "Unknown" (never null)
- If sex is not stated in the report, use "Unknown"
- All dates must be ISO format YYYY-MM-DD (e.g., "2026-05-09")

{
  "patient": {
    "age": 54,
    "sex": "F",
    "weight": 71.0,
    "race": null,
    "confidence": 0.92
  },
  "suspect_drug": {
    "name": "tezarimab",
    "dose": "600 mg IV",
    "route": "intravenous",
    "indication": "multiple sclerosis",
    "confidence": 0.95
  },
  "ae_description": {
    "narrative": "severe headache with photophobia and visual disturbances",
    "onset_date": "2026-05-09",
    "outcome": "recovered",
    "confidence": 0.89
  },
  "temporal": {
    "drug_start_date": "2026-01-15",
    "ae_onset_date": "2026-05-09",
    "outcome_date": "2026-05-12",
    "date_estimated": false,
    "confidence": 0.87
  },
  "concomitant_meds": [
    { "name": "vitamin D3", "dose": "2000 IU daily", "route": "oral", "confidence": 0.85 }
  ],
  "medical_history": {
    "narrative": "Hashimoto's thyroiditis, stable on levothyroxine >5 years",
    "confidence": 0.80
  },
  "span_citations": {
    "patient.age": { "value": "54", "source_span": "215-217" },
    "suspect_drug.name": { "value": "TEZARIMAB", "source_span": "320-329" },
    "ae_description.narrative": { "value": "severe headache with photophobia", "source_span": "450-485" }
  },
  "extraction_status": "AUTO_COMPLETE"
}

Be precise with span indices (0-indexed character positions in source text).
"""

    def _extract_ae_terms(self, narrative: str) -> list:
        """Extract key AE terms from narrative for MedDRA lookup"""
        # Simple keyword extraction (in production, use NER or better NLP)
        common_terms = [
            "elevated liver enzymes", "liver enzyme elevation", "hepatic enzyme increased",
            "drug-induced liver injury", "hepatotoxicity",
            "headache", "migraine", "visual disturbance", "blurred vision",
            "sweating", "excessive sweating", "hyperhidrosis",
            "palpitations", "heart racing", "tachycardia",
            "panic attack", "anxiety",
            "tremor", "shakiness",
            "nausea", "vomiting", "diarrhea",
            "fatigue", "weakness", "malaise",
            "rash", "pruritus", "itching",
            "dizziness", "vertigo",
            "insomnia", "sleep disturbance"
        ]

        narrative_lower = narrative.lower()

        # Sort by length (longest first) to match multi-word terms before single words
        common_terms.sort(key=len, reverse=True)
        found_terms = [term for term in common_terms if term in narrative_lower]

        return found_terms[:3] if found_terms else [narrative[:50]]  # Return up to 3 best matches

    def _build_case_package(
        self,
        extracted_data: Dict[str, Any],
        source_doc: Dict[str, Any],
        received_at: str,
        format_type: str
    ) -> AECasePackage:
        """Build AECasePackage from extracted data"""

        # Preprocess patient data: handle null sex field
        patient_data = extracted_data["patient"].copy()
        if patient_data.get("sex") is None:
            patient_data["sex"] = "Unknown"

        # Preprocess suspect_drug data: handle null dose field
        suspect_drug_data = extracted_data["suspect_drug"].copy()
        if suspect_drug_data.get("dose") is None:
            suspect_drug_data["dose"] = "unknown"

        # Build nested entities
        patient = Patient(**patient_data)
        suspect_drug = SuspectDrug(**suspect_drug_data)
        ae_description = AEDescription(**extracted_data["ae_description"])
        temporal = Temporal(**extracted_data["temporal"])

        concomitant_meds = [
            ConcomitantMed(**med) for med in extracted_data.get("concomitant_meds", [])
        ]

        medical_history = None
        if extracted_data.get("medical_history"):
            medical_history = MedicalHistory(**extracted_data["medical_history"])

        # Build span citations (skip invalid ones)
        span_citations = {}
        for field_name, citation_data in extracted_data.get("span_citations", {}).items():
            # Skip if value or source_span is None
            if citation_data.get("value") is None or citation_data.get("source_span") is None:
                continue
            try:
                span_citations[field_name] = SpanCitation(**citation_data)
            except Exception:
                # Skip malformed span citations
                continue

        # Determine extraction status
        extraction_status = extracted_data.get("extraction_status", ExtractionStatus.AUTO_COMPLETE)

        # Check confidence thresholds
        if patient.confidence < 0.85 or suspect_drug.confidence < 0.85 or \
           ae_description.confidence < 0.85 or temporal.confidence < 0.85:
            extraction_status = ExtractionStatus.HUMAN_REQUIRED

        if any(med.confidence < 0.80 for med in concomitant_meds):
            extraction_status = ExtractionStatus.HUMAN_REQUIRED

        # Build case package
        case_package = AECasePackage(
            received_at=received_at,
            format=format_type,
            extraction_status=extraction_status,
            patient=patient,
            suspect_drug=suspect_drug,
            ae_description=ae_description,
            temporal=temporal,
            concomitant_meds=concomitant_meds,
            medical_history=medical_history,
            span_citations=span_citations,
            source_documents=[SourceDocument(**source_doc)],
            model_version_adr1=MODEL_VERSION
        )

        return case_package

    def _determine_routing(self, case_package: AECasePackage, log: list) -> str:
        """
        Determine where case should be routed next.

        Returns:
            "ADR-2" | "HITL_QUEUE" | "EXCEPTION_QUEUE" | "REPORTER_FOLLOWUP" | "PENDING_DUPLICATE"
        """
        status = case_package.extraction_status

        if status == ExtractionStatus.AUTO_COMPLETE:
            log.append("[ADR-1] Routing: AUTO_COMPLETE -> ADR-2 for medical triage")
            return "ADR-2"

        elif status == ExtractionStatus.HUMAN_REQUIRED:
            log.append("[ADR-1] Routing: HUMAN_REQUIRED -> HITL validation queue")
            return "HITL_QUEUE"

        elif status == ExtractionStatus.PENDING_DUPLICATE:
            log.append("[ADR-1] Routing: PENDING_DUPLICATE -> Manual duplicate review")
            return "PENDING_DUPLICATE"

        elif status == ExtractionStatus.EXCEPTION_NOTE:
            log.append("[ADR-1] Routing: EXCEPTION_NOTE -> Exception queue (ops review)")
            return "EXCEPTION_QUEUE"

        elif status == ExtractionStatus.REPORTER_FOLLOWUP:
            log.append("[ADR-1] Routing: REPORTER_FOLLOWUP -> Follow-up queue (missing info)")
            return "REPORTER_FOLLOWUP"

        else:
            log.append(f"[ADR-1] Unknown status: {status} -> EXCEPTION_QUEUE")
            return "EXCEPTION_QUEUE"
