"""Mock adapter for Prior-Auth Database API [per Claude.md A36]."""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PriorAuthDBAdapter:
    """
    Mock adapter for Prior-Authorization Database API.

    In production, this would query the actual PostgreSQL database
    or third-party API (e.g., Availity, Change Healthcare).
    """

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        logger.info(f"Initialized PriorAuthDBAdapter (mock) with URL: {api_url}")

    async def query_prior_auths(
        self,
        patient_id: str,
        insurance_policy_id: str,
        scheduled_date: datetime,
    ) -> List[Dict[str, Any]]:
        """
        Query prior-auth database for active prior-authorizations.

        Returns matching prior-auth records per Claude.md Step 2 logic.
        """
        logger.info(
            f"Querying prior-auths for patient {patient_id}, policy {insurance_policy_id} (mock)"
        )

        # Mock data - different scenarios for testing
        mock_database = {
            ("PAT-12345", "INS-POL-67890"): [
                {
                    "prior_auth_id": "PA-2024-001",
                    "patient_id": "PAT-12345",
                    "insurance_policy_id": "INS-POL-67890",
                    "approval_number": "AUTH987654",
                    "approval_date": (datetime.now() - timedelta(days=30)).isoformat(),
                    "expiration_date": (datetime.now() + timedelta(days=45)).isoformat(),
                    "approval_status": "ACTIVE",
                    "approved_cpt_codes": ["70553", "70551"],  # MRI procedures
                    "approved_service_description": "MRI Brain with or without Contrast",
                    "service_category": "imaging",
                    "approved_units": 2,
                    "units_used": 0,
                    "source_system": "prior_auth_db",
                }
            ],
            ("PAT-67890", "INS-POL-11111"): [
                {
                    "prior_auth_id": "PA-2024-002",
                    "patient_id": "PAT-67890",
                    "insurance_policy_id": "INS-POL-11111",
                    "approval_number": "AUTH555123",
                    "approval_date": (datetime.now() - timedelta(days=60)).isoformat(),
                    "expiration_date": (datetime.now() + timedelta(days=2)).isoformat(),  # Expiring soon!
                    "approval_status": "ACTIVE",
                    "approved_cpt_codes": ["72148"],  # MRI Lumbar Spine
                    "approved_service_description": "MRI Spine",
                    "service_category": "imaging",
                    "approved_units": 1,
                    "units_used": 0,
                    "source_system": "prior_auth_db",
                }
            ],
            # PAT-99999 has no prior-auth (testing MISSING scenario)
        }

        key = (patient_id, insurance_policy_id)
        return mock_database.get(key, [])

    async def get_prior_auth_by_id(self, prior_auth_id: str) -> Optional[Dict[str, Any]]:
        """Get specific prior-auth record by ID."""
        logger.info(f"Fetching prior-auth {prior_auth_id} (mock)")

        mock_records = {
            "PA-2024-001": {
                "prior_auth_id": "PA-2024-001",
                "patient_id": "PAT-12345",
                "insurance_policy_id": "INS-POL-67890",
                "approval_number": "AUTH987654",
                "approval_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "expiration_date": (datetime.now() + timedelta(days=45)).isoformat(),
                "approval_status": "ACTIVE",
                "approved_cpt_codes": ["70553", "70551"],
                "approved_service_description": "MRI Brain with or without Contrast",
                "service_category": "imaging",
                "approved_units": 2,
                "units_used": 0,
                "source_system": "prior_auth_db",
            },
            "PA-2024-002": {
                "prior_auth_id": "PA-2024-002",
                "patient_id": "PAT-67890",
                "insurance_policy_id": "INS-POL-11111",
                "approval_number": "AUTH555123",
                "approval_date": (datetime.now() - timedelta(days=60)).isoformat(),
                "expiration_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "approval_status": "ACTIVE",
                "approved_cpt_codes": ["72148"],
                "approved_service_description": "MRI Spine",
                "service_category": "imaging",
                "approved_units": 1,
                "units_used": 0,
                "source_system": "prior_auth_db",
            },
        }

        return mock_records.get(prior_auth_id)
