"""
Clinical criteria codebook loader and matching logic.
Per specs/06b-capability-spec-triage.md Section 9.2 and Section 6.3.
"""

import json
import os
from typing import List, Tuple, Optional
from datetime import datetime
from .models import ClinicalCodebook, CriteriaCodebookEntry


class CodebookLoader:
    """Loads and validates clinical criteria codebook."""

    def __init__(self, codebook_path: str):
        self.codebook_path = codebook_path
        self.codebook: Optional[ClinicalCodebook] = None
        self.provisions: List[CriteriaCodebookEntry] = []

    def load(self) -> ClinicalCodebook:
        """
        Load codebook from JSON file.
        Validates effective dates and approval status.
        """
        if not os.path.exists(self.codebook_path):
            raise FileNotFoundError(f"Codebook not found: {self.codebook_path}")

        with open(self.codebook_path, "r") as f:
            data = json.load(f)

        self.codebook = ClinicalCodebook(**data)

        # Filter to active provisions only (effective_date <= today, retired_date is None or > today)
        today = datetime.now().date()
        self.provisions = []

        for provision in self.codebook.provisions:
            effective_date = datetime.strptime(provision.effective_date, "%Y-%m-%d").date()
            retired_date = None
            if provision.retired_date:
                retired_date = datetime.strptime(provision.retired_date, "%Y-%m-%d").date()

            # Include if effective and not retired
            if effective_date <= today and (retired_date is None or retired_date > today):
                self.provisions.append(provision)

        if len(self.provisions) == 0:
            raise ValueError("No active provisions in codebook")

        return self.codebook

    def match_claim(
        self,
        icd10_codes: List[str],
        cpt_codes: List[str],
        prior_auth_required: bool
    ) -> Tuple[List[str], List[str]]:
        """
        Match claim indicators against codebook provisions.

        Returns:
            Tuple of (matched_provision_ids, clinical_indicators_detected)
        """
        matched_provisions = []
        clinical_indicators = []

        # Build indicator list
        for code in icd10_codes:
            clinical_indicators.append(f"ICD-10: {code}")

        for code in cpt_codes:
            clinical_indicators.append(f"CPT: {code}")

        if prior_auth_required:
            clinical_indicators.append("Prior Auth: Required")

        # Check each provision
        for provision in self.provisions:
            matched = False

            # Check prior auth trigger
            if provision.trigger_prior_auth_required and prior_auth_required:
                matched = True

            # Check ICD-10 patterns
            if not matched and provision.trigger_icd10_patterns:
                for icd10_code in icd10_codes:
                    for pattern in provision.trigger_icd10_patterns:
                        if icd10_code.startswith(pattern):
                            matched = True
                            break
                    if matched:
                        break

            # Check CPT patterns
            if not matched and provision.trigger_cpt_patterns:
                for cpt_code in cpt_codes:
                    for pattern in provision.trigger_cpt_patterns:
                        if cpt_code.startswith(pattern):
                            matched = True
                            break
                    if matched:
                        break

            if matched:
                matched_provisions.append(provision.provision_id)

        return matched_provisions, clinical_indicators

    def compute_confidence(
        self,
        matched_provisions: List[str],
        icd10_codes: List[str],
        cpt_codes: List[str]
    ) -> float:
        """
        Compute classification confidence.

        High confidence (0.9-1.0): Exact match to specific provision.
        Medium confidence (0.7-0.9): Broad prefix match.
        Low confidence (0.0-0.7): Very broad match or no match.
        """
        if not matched_provisions:
            # No provisions matched
            return 1.0  # High confidence FAST_PATH (no clinical indicators)

        # Clinical path detected — assess match specificity
        # Check for very broad patterns (single-character prefixes)
        has_broad_match = False
        has_specific_match = False

        for provision_id in matched_provisions:
            provision = next((p for p in self.provisions if p.provision_id == provision_id), None)
            if not provision:
                continue

            # Check if any ICD-10 pattern is single character
            for pattern in provision.trigger_icd10_patterns:
                if len(pattern) == 1 or len(pattern) == 2:
                    has_broad_match = True
                else:
                    has_specific_match = True

            # Check if any CPT pattern is single character
            for pattern in provision.trigger_cpt_patterns:
                if len(pattern) == 1 or len(pattern) == 2:
                    has_broad_match = True
                else:
                    has_specific_match = True

        # Confidence scoring
        if has_specific_match and not has_broad_match:
            return 0.95  # High confidence — specific match

        if has_specific_match and has_broad_match:
            return 0.85  # Medium-high — mix of specific and broad

        if has_broad_match:
            return 0.75  # Medium — broad prefix match only

        # Prior auth only (no code patterns)
        if len(matched_provisions) == 1:
            provision = next((p for p in self.provisions if p.provision_id == matched_provisions[0]), None)
            if provision and provision.trigger_prior_auth_required:
                return 0.88  # High confidence for prior auth trigger

        return 0.80  # Default medium confidence


# Global codebook instance
_codebook_loader: Optional[CodebookLoader] = None


def get_codebook_loader(codebook_path: str = None) -> CodebookLoader:
    """Get or initialize codebook loader singleton."""
    global _codebook_loader

    if _codebook_loader is None:
        if codebook_path is None:
            # Default path
            default_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config",
                "criteria-codebook.json"
            )
            codebook_path = default_path

        _codebook_loader = CodebookLoader(codebook_path)
        _codebook_loader.load()

    return _codebook_loader
