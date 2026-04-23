"""Mock adapter for athenahealth EHR API [per Claude.md A39]."""
from datetime import datetime, timedelta, time
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AthenaHealthAdapter:
    """
    Mock adapter for athenahealth EHR API.

    In production, this would use OAuth 2.0 and make real API calls.
    For development, returns mock data [per Claude.md specs/integration-guide.md].
    """

    def __init__(self, api_url: str, client_id: str, client_secret: str):
        self.api_url = api_url
        self.client_id = client_id
        self.client_secret = client_secret
        logger.info(f"Initialized AthenaHealthAdapter (mock) with URL: {api_url}")

    async def get_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get appointment details from EHR.

        Mock implementation returns sample data for testing.
        """
        logger.info(f"Fetching appointment {appointment_id} from athenahealth (mock)")

        # Mock data - in production would call real API
        mock_appointments = {
            "APT-2024-001": {
                "appointment_id": "APT-2024-001",
                "patient_id": "PAT-12345",
                "scheduled_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "scheduled_time": "10:00:00",
                "appointment_type": "imaging",
                "procedure_codes": ["70553"],  # MRI Brain with Contrast
                "procedure_descriptions": ["MRI Brain with Contrast"],
                "insurance_policy_id": "INS-POL-67890",
                "appointment_status": "SCHEDULED",
            },
            "APT-2024-002": {
                "appointment_id": "APT-2024-002",
                "patient_id": "PAT-67890",
                "scheduled_date": (datetime.now() + timedelta(days=5)).isoformat(),
                "scheduled_time": "14:30:00",
                "appointment_type": "imaging",
                "procedure_codes": ["72148"],  # MRI Lumbar Spine
                "procedure_descriptions": ["MRI Lumbar Spine"],
                "insurance_policy_id": "INS-POL-11111",
                "appointment_status": "SCHEDULED",
            },
            "APT-2024-003": {
                "appointment_id": "APT-2024-003",
                "patient_id": "PAT-99999",
                "scheduled_date": (datetime.now() + timedelta(days=2)).isoformat(),
                "scheduled_time": "09:00:00",
                "appointment_type": "office_visit",
                "procedure_codes": ["99214"],  # Office visit (doesn't need prior-auth)
                "procedure_descriptions": ["Established Patient Office Visit"],
                "insurance_policy_id": "INS-POL-22222",
                "appointment_status": "SCHEDULED",
            },
            "APT-2024-005": {
                "appointment_id": "APT-2024-005",
                "patient_id": "PAT-99999",
                "scheduled_date": (datetime.now() + timedelta(days=4)).isoformat(),
                "scheduled_time": "11:00:00",
                "appointment_type": "office_visit",
                "procedure_codes": ["99213"],  # Office visit (doesn't need prior-auth)
                "procedure_descriptions": ["Office Visit Level 3"],
                "insurance_policy_id": "INS-POL-22222",
                "appointment_status": "SCHEDULED",
            },
        }

        return mock_appointments.get(appointment_id)

    async def write_verification_note(
        self, appointment_id: str, verification_data: Dict[str, Any]
    ) -> bool:
        """
        Write prior-auth verification note to EHR.

        Mock implementation logs the data without actual write.
        """
        logger.info(
            f"Writing verification note to appointment {appointment_id} (mock): {verification_data}"
        )
        # In production, would POST to athenahealth API
        return True

    async def update_prior_auth_flag(self, appointment_id: str, verified: bool) -> bool:
        """
        Update prior-auth verification flag in EHR.

        Mock implementation logs the update.
        """
        logger.info(f"Updating prior-auth verified flag for {appointment_id}: {verified} (mock)")
        # In production, would PUT to athenahealth API
        return True
