from __future__ import annotations

from typing import Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    servicenow_instance: str = Field(..., description="e.g. your-org.service-now.com")
    servicenow_read_token: str
    servicenow_write_token: str
    anthropic_api_key: str
    system_service_token: str

    hitl_queue_url: str = "http://localhost:8001"
    event_bus_url: Optional[str] = None
    slack_webhook_url: Optional[str] = None

    poll_interval_seconds: int = 30
    poll_batch_size: int = 10
    confidence_threshold: float = 0.85
    llm_timeout_seconds: int = 30
    llm_unavailable_timeout_seconds: int = 60
    consecutive_failure_alert_threshold: int = 10
    dead_letter_alert_threshold: int = 10
    dead_letter_db_path: str = "dead_letter.db"
    dictionaries_path: str = "config/dictionaries.yaml"


class DomainConfig:
    def __init__(self, dictionaries_path: str) -> None:
        with open(dictionaries_path) as f:
            data = yaml.safe_load(f)

        self.specialty_codes: dict[str, list[str]] = {
            code: info.get("aliases", [])
            for code, info in data["specialty_codes"].items()
        }
        self.credential_codes: dict[str, list[str]] = {
            code: info.get("aliases", [])
            for code, info in data["credential_codes"].items()
        }
        self.hospital_locations: dict[str, list[str]] = {
            loc_id: info.get("aliases", [])
            for loc_id, info in data["hospital_locations"].items()
        }

    @property
    def valid_specialty_codes(self) -> set[str]:
        return set(self.specialty_codes.keys())

    @property
    def valid_credential_codes(self) -> set[str]:
        return set(self.credential_codes.keys())

    @property
    def valid_location_ids(self) -> set[str]:
        return set(self.hospital_locations.keys())
