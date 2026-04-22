"""Mock adapter for Insurance Requirements Database [per Claude.md A38]."""
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class InsuranceRequirementsAdapter:
    """
    Mock adapter for Insurance Requirements Database.

    Determines if a procedure requires prior-authorization per insurance policy.
    Falls back to hardcoded rules per Claude.md A38a if database unavailable.
    """

    def __init__(self, api_url: str):
        self.api_url = api_url
        logger.info(f"Initialized InsuranceRequirementsAdapter (mock) with URL: {api_url}")

    async def check_prior_auth_requirement(
        self, insurance_policy_id: str, procedure_code: str
    ) -> Dict[str, Any]:
        """
        Check if procedure requires prior-authorization.

        Returns:
            {
                "prior_auth_required": bool,
                "requirement_type": "always" | "sometimes" | "never",
                "notes": str
            }
        """
        logger.info(
            f"Checking prior-auth requirement for policy {insurance_policy_id}, "
            f"procedure {procedure_code} (mock)"
        )

        # Use hardcoded rules per Claude.md A38a
        cpt_num = int(procedure_code) if procedure_code.isdigit() else 0

        # Imaging procedures (CPT 70000-79999): Require prior-auth
        if 70000 <= cpt_num <= 79999:
            return {
                "prior_auth_required": True,
                "requirement_type": "always",
                "notes": "Imaging procedures require prior-authorization per policy",
            }

        # Surgical procedures (CPT 10000-69999): Require prior-auth
        if 10000 <= cpt_num <= 69999:
            return {
                "prior_auth_required": True,
                "requirement_type": "always",
                "notes": "Surgical procedures require prior-authorization per policy",
            }

        # Office visits (CPT 99201-99499): Do NOT require prior-auth
        if 99201 <= cpt_num <= 99499:
            return {
                "prior_auth_required": False,
                "requirement_type": "never",
                "notes": "Office visits do not require prior-authorization",
            }

        # Unknown CPT code - escalate
        logger.warning(f"Unknown CPT code {procedure_code}, cannot determine requirement")
        return {
            "prior_auth_required": None,
            "requirement_type": "unknown",
            "notes": f"Cannot determine prior-auth requirement for CPT {procedure_code}",
        }
