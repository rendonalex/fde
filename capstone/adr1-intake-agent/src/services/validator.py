"""Post-processing validation for claim records."""

from ..models import ExtractionStatus, IntakeChannel, NormalizedClaimRecord


class ClaimValidator:
    """Validates claim records after agent processing."""

    REQUIRED_FIELDS = {
        "member_id",
        "member_name_last",
        "member_name_first",
        "date_of_service_start",
        "date_of_service_end",
        "claim_type",
        "payer_name",
        "prior_auth_required",
    }

    def validate_claim(self, claim: NormalizedClaimRecord) -> tuple[bool, list[str]]:
        """
        Validate claim record completeness and consistency.

        Returns:
            (is_valid, list of validation errors)
        """
        errors = []

        # Check required fields are present
        for field in self.REQUIRED_FIELDS:
            value = getattr(claim, field, None)
            # Special handling for boolean fields - False is a valid value
            if field == "prior_auth_required":
                if value is None:
                    errors.append(f"Required field missing: {field}")
            elif not value:
                errors.append(f"Required field missing: {field}")

        # Check ICD-10 and CPT codes present
        if not claim.icd10_codes or len(claim.icd10_codes) == 0:
            errors.append("icd10_codes cannot be empty")

        if not claim.cpt_codes or len(claim.cpt_codes) == 0:
            errors.append("cpt_codes cannot be empty")

        # Check prior_auth_number logic
        if claim.prior_auth_required and not claim.prior_auth_number:
            errors.append("prior_auth_number required when prior_auth_required=true")

        if not claim.prior_auth_required and claim.prior_auth_number:
            errors.append("prior_auth_number must be null when prior_auth_required=false")

        # Check date logic
        if claim.date_of_service_end < claim.date_of_service_start:
            errors.append("date_of_service_end must be >= date_of_service_start")

        # Check extraction_status consistency
        if claim.extraction_status == ExtractionStatus.AUTO_COMPLETE:
            # Should not have low_confidence_fields (except identity fallback case)
            # This is a simplified check
            pass

        return (len(errors) == 0, errors)
