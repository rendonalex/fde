"""
API endpoint tests for shadow log store.
Per specs/06b-capability-spec-triage.md Section 8.2.
"""

import pytest
import os
import sys
from fastapi.testclient import TestClient
from datetime import datetime
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import init_db
from app.models import (
    NormalizedClaimRecord,
    RoutingDecisionRecord,
    ProcessorDecisionUpdate,
    RoutingDecision,
    ExtractionStatus,
    AgreementStatus
)

# Initialize database before creating client
init_db()

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self):
        """Test that health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestClassificationEndpoint:
    """Test classification endpoint."""

    def test_classify_routine_claim(self):
        """Test classifying a routine office visit claim via API endpoint."""
        claim = {
            "claim_id": str(uuid4()),
            "source_claim_ref": "TEST-001",
            "intake_channel": "CMS1500_PDF",
            "extraction_status": "AUTO_COMPLETE",
            "member_id": "M-12345",
            "icd10_codes": ["Z00.00"],
            "cpt_codes": ["99213"],
            "prior_auth_required": False,
            "prior_auth_number": None,
            "payer_id": "PY-001",
            "place_of_service": "11",
            "billed_amount": 185.00
        }

        response = client.post("/api/v1/classify", json=claim)
        assert response.status_code == 200

        data = response.json()
        assert data["routing_decision"] == "FAST_PATH"
        assert data["routing_mode"] == "SHADOW"
        assert "reasoning_trace" in data

    def test_classify_routine_claim_mocked(self, monkeypatch):
        """Test classification endpoint with mocked LLM (fast, no API key needed)."""
        from app.agent import TriageAgent
        from app.models import RoutingDecisionOutput, RoutingDecision, RoutingMode

        # Mock the _classify_with_llm method to return predictable result
        def mock_classify_llm(self, claim):
            return RoutingDecisionOutput(
                claim_id=claim.claim_id,
                source_claim_ref=claim.source_claim_ref,
                routing_decision=RoutingDecision.FAST_PATH,
                confidence=0.96,
                confidence_fallback=False,
                clinical_indicators_detected=["ICD-10: Z00.00", "CPT: 99213"],
                criteria_provisions_matched=[],
                reasoning_trace="Mocked reasoning trace",
                routing_mode=RoutingMode.SHADOW
            )

        monkeypatch.setattr(TriageAgent, "_classify_with_llm", mock_classify_llm)

        claim = {
            "claim_id": str(uuid4()),
            "source_claim_ref": "TEST-MOCK-001",
            "intake_channel": "CMS1500_PDF",
            "extraction_status": "AUTO_COMPLETE",
            "member_id": "M-MOCK-001",
            "icd10_codes": ["Z00.00"],
            "cpt_codes": ["99213"],
            "prior_auth_required": False,
            "prior_auth_number": None,
            "payer_id": "PY-001",
            "place_of_service": "11",
            "billed_amount": 185.00
        }

        response = client.post("/api/v1/classify", json=claim)
        assert response.status_code == 200

        data = response.json()
        assert data["routing_decision"] == "FAST_PATH"
        assert data["confidence"] == 0.96
        assert data["routing_mode"] == "SHADOW"

    def test_classify_rejects_non_auto_complete(self):
        """Test that classification rejects non-AUTO_COMPLETE claims."""
        claim = {
            "claim_id": str(uuid4()),
            "source_claim_ref": "TEST-002",
            "intake_channel": "CMS1500_PDF",
            "extraction_status": "HUMAN_REQUIRED",
            "member_id": "M-67890",
            "icd10_codes": ["Z00.00"],
            "cpt_codes": ["99213"],
            "prior_auth_required": False,
            "prior_auth_number": None,
            "payer_id": "PY-002",
            "place_of_service": "11",
            "billed_amount": 185.00
        }

        response = client.post("/api/v1/classify", json=claim)
        assert response.status_code == 400
        assert "extraction_status" in response.json()["detail"]


class TestShadowLogEndpoints:
    """Test shadow log store endpoints."""

    def test_create_shadow_log_entry(self):
        """Test creating a shadow log entry."""
        shadow_log_id = str(uuid4())
        claim_id = str(uuid4())

        record = {
            "shadow_log_id": shadow_log_id,
            "claim_id": claim_id,
            "agent_routing_decision": "FAST_PATH",
            "agent_confidence": 0.96,
            "agent_confidence_fallback": False,
            "clinical_indicators_detected": ["ICD-10: Z00.00", "CPT: 99213"],
            "criteria_provisions_matched": [],
            "reasoning_trace": "Test reasoning trace",
            "agent_version": "1.0.0",
            "logged_at": datetime.utcnow().isoformat() + "Z"
        }

        response = client.post("/api/v1/shadow-log", json=record)
        assert response.status_code == 201
        assert response.json()["shadow_log_id"] == shadow_log_id

    def test_duplicate_shadow_log_entry_rejected(self):
        """Test that duplicate shadow_log_id is rejected."""
        shadow_log_id = str(uuid4())
        claim_id = str(uuid4())

        record = {
            "shadow_log_id": shadow_log_id,
            "claim_id": claim_id,
            "agent_routing_decision": "FAST_PATH",
            "agent_confidence": 0.96,
            "agent_confidence_fallback": False,
            "clinical_indicators_detected": ["ICD-10: Z00.00"],
            "criteria_provisions_matched": [],
            "reasoning_trace": "Test",
            "agent_version": "1.0.0",
            "logged_at": datetime.utcnow().isoformat() + "Z"
        }

        # First insert
        response1 = client.post("/api/v1/shadow-log", json=record)
        assert response1.status_code == 201

        # Duplicate insert
        response2 = client.post("/api/v1/shadow-log", json=record)
        assert response2.status_code == 409

    def test_update_processor_decision(self):
        """Test updating shadow log with processor decision."""
        # Create entry
        shadow_log_id = str(uuid4())
        claim_id = str(uuid4())

        record = {
            "shadow_log_id": shadow_log_id,
            "claim_id": claim_id,
            "agent_routing_decision": "FAST_PATH",
            "agent_confidence": 0.96,
            "agent_confidence_fallback": False,
            "clinical_indicators_detected": ["ICD-10: Z00.00"],
            "criteria_provisions_matched": [],
            "reasoning_trace": "Test",
            "agent_version": "1.0.0",
            "logged_at": datetime.utcnow().isoformat() + "Z"
        }

        create_response = client.post("/api/v1/shadow-log", json=record)
        assert create_response.status_code == 201

        # Update with processor decision
        update = {
            "processor_routing_decision": "FAST_PATH",
            "processor_user_id": "processor_001",
            "processor_decided_at": datetime.utcnow().isoformat() + "Z"
        }

        update_response = client.put(
            f"/api/v1/shadow-log/{shadow_log_id}/processor-decision",
            json=update
        )
        assert update_response.status_code == 200
        assert update_response.json()["agreement"] == "AGREE"

    def test_update_processor_decision_disagreement(self):
        """Test processor decision that disagrees with agent."""
        # Create entry
        shadow_log_id = str(uuid4())
        claim_id = str(uuid4())

        record = {
            "shadow_log_id": shadow_log_id,
            "claim_id": claim_id,
            "agent_routing_decision": "FAST_PATH",
            "agent_confidence": 0.96,
            "agent_confidence_fallback": False,
            "clinical_indicators_detected": ["ICD-10: Z00.00"],
            "criteria_provisions_matched": [],
            "reasoning_trace": "Test",
            "agent_version": "1.0.0",
            "logged_at": datetime.utcnow().isoformat() + "Z"
        }

        create_response = client.post("/api/v1/shadow-log", json=record)
        assert create_response.status_code == 201

        # Update with disagreeing processor decision
        update = {
            "processor_routing_decision": "CLINICAL_PATH",
            "processor_user_id": "processor_002",
            "processor_decided_at": datetime.utcnow().isoformat() + "Z"
        }

        update_response = client.put(
            f"/api/v1/shadow-log/{shadow_log_id}/processor-decision",
            json=update
        )
        assert update_response.status_code == 200
        assert update_response.json()["agreement"] == "DISAGREE"

    def test_list_shadow_log_entries(self):
        """Test querying shadow log entries."""
        # Create multiple entries
        for i in range(3):
            shadow_log_id = str(uuid4())
            claim_id = str(uuid4())

            record = {
                "shadow_log_id": shadow_log_id,
                "claim_id": claim_id,
                "agent_routing_decision": "FAST_PATH" if i % 2 == 0 else "CLINICAL_PATH",
                "agent_confidence": 0.95,
                "agent_confidence_fallback": False,
                "clinical_indicators_detected": [f"Test indicator {i}"],
                "criteria_provisions_matched": [],
                "reasoning_trace": f"Test trace {i}",
                "agent_version": "1.0.0",
                "logged_at": datetime.utcnow().isoformat() + "Z"
            }

            client.post("/api/v1/shadow-log", json=record)

        # Query all
        response = client.get("/api/v1/shadow-log?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_get_shadow_log_metrics(self):
        """Test [A6] gate metrics endpoint."""
        response = client.get("/api/v1/shadow-log/metrics")
        assert response.status_code == 200

        data = response.json()
        assert "total_entries" in data
        assert "labeled_entries" in data
        assert "false_negative_count" in data
        assert "false_negative_rate" in data
        assert "gate_status" in data
        assert "wave_2_ready" in data

    def test_gate_metrics_with_false_negatives(self):
        """Test gate metrics calculation with false negatives."""
        # Create entry with false negative (agent=FAST, processor=CLINICAL)
        shadow_log_id = str(uuid4())
        claim_id = str(uuid4())

        record = {
            "shadow_log_id": shadow_log_id,
            "claim_id": claim_id,
            "agent_routing_decision": "FAST_PATH",
            "agent_confidence": 0.85,
            "agent_confidence_fallback": False,
            "clinical_indicators_detected": [],
            "criteria_provisions_matched": [],
            "reasoning_trace": "Test false negative",
            "agent_version": "1.0.0",
            "logged_at": datetime.utcnow().isoformat() + "Z"
        }

        client.post("/api/v1/shadow-log", json=record)

        # Update with processor decision (disagrees)
        update = {
            "processor_routing_decision": "CLINICAL_PATH",
            "processor_user_id": "processor_003",
            "processor_decided_at": datetime.utcnow().isoformat() + "Z"
        }

        client.put(f"/api/v1/shadow-log/{shadow_log_id}/processor-decision", json=update)

        # Check metrics
        response = client.get("/api/v1/shadow-log/metrics")
        assert response.status_code == 200

        data = response.json()
        assert data["false_negative_count"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
