"""Simplified EDI 837 parser for demonstration."""

import json
from typing import Any, Union

from ..models import ExtractedField, ExtractionResult, IntakeChannel


class EDI837Parser:
    """Simplified EDI 837P/I parser."""

    def parse(self, edi_content: Union[str, dict]) -> ExtractionResult:
        """
        Parse EDI 837 transaction.

        For demo purposes, accepts either:
        - Raw EDI string (we'll do basic parsing)
        - Pre-parsed dict (for testing)
        """
        if isinstance(edi_content, str):
            # Try to parse as JSON first (test format)
            try:
                data = json.loads(edi_content)
                return self._parse_dict(data)
            except json.JSONDecodeError:
                # Real EDI parsing would go here
                raise ValueError("Raw EDI parsing not implemented in demo")
        else:
            return self._parse_dict(edi_content)

    def _parse_dict(self, data: dict[str, Any]) -> ExtractionResult:
        """Parse from dict format."""
        # Detect transaction type
        intake_channel = IntakeChannel(
            data.get("intake_channel", "EDI_837P")
        )

        # Extract fields (EDI has implicit confidence 1.0)
        extracted_fields = {}
        for field_name, value in data.get("fields", {}).items():
            extracted_fields[field_name] = ExtractedField(value=value, confidence=1.0)

        return ExtractionResult(
            source_format=data.get("source_format", "EDI_837P"),
            source_claim_ref=data.get("source_claim_ref", "UNKNOWN"),
            intake_channel=intake_channel,
            extracted_fields=extracted_fields,
        )
