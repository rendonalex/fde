"""Mock IDP extraction pipeline."""

import json
from typing import Any, Union

from ..models import ExtractedField, ExtractionResult, IntakeChannel


class MockIDPPipeline:
    """Mock Intelligent Document Processing pipeline."""

    async def extract_from_pdf(self, pdf_content: Union[bytes, dict]) -> ExtractionResult:
        """
        Extract fields from PDF claim.

        For demo, accepts pre-parsed dict with confidence scores.
        """
        if isinstance(pdf_content, bytes):
            raise NotImplementedError("Real PDF extraction not implemented in demo")

        return self._parse_extraction(pdf_content, IntakeChannel.CMS1500_PDF)

    async def extract_from_ocr_text(self, ocr_text: Union[str, dict]) -> ExtractionResult:
        """Extract from pre-OCR'd text."""
        if isinstance(ocr_text, str):
            raise NotImplementedError("Real OCR parsing not implemented in demo")

        return self._parse_extraction(ocr_text, IntakeChannel.CMS1500_OCR_TEXT)

    async def extract_from_json(self, json_data: dict, channel: IntakeChannel) -> ExtractionResult:
        """Extract from JSON (portal, FHIR, email)."""
        return self._parse_extraction(json_data, channel)

    def _parse_extraction(self, data: dict[str, Any], channel: IntakeChannel) -> ExtractionResult:
        """Parse extraction result from dict."""
        extracted_fields = {}
        fields_data = data.get("extracted_fields", {})

        for field_name, field_data in fields_data.items():
            if isinstance(field_data, dict) and "value" in field_data:
                # Already in ExtractedField format
                extracted_fields[field_name] = ExtractedField(**field_data)
            else:
                # Simple value with default confidence
                extracted_fields[field_name] = ExtractedField(value=field_data, confidence=0.85)

        return ExtractionResult(
            source_format=data.get("source_format", "PDF"),
            source_claim_ref=data.get("source_claim_ref", "UNKNOWN"),
            intake_channel=channel,
            extracted_fields=extracted_fields,
            rfc5322_headers=data.get("rfc5322_headers"),
        )
