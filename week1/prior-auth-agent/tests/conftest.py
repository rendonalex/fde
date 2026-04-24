"""
Shared pytest fixtures and test configuration.

Provides common test data, mock adapters, and fixtures for all test suites.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.prior_auth_check import (
    PriorAuthCheck,
    CheckStatus,
    PriorAuthStatus,
    AIRecommendation,
    ConfidenceScore,
)
from app.services.decision_engine import PriorAuthDecisionEngine
from app.services.fuzzy_matcher import FuzzyMatcher
from app.adapters import AthenaHealthAdapter, PriorAuthDBAdapter, InsuranceRequirementsAdapter


# ==================== Database Fixtures ====================

@pytest.fixture(scope="function")
def test_db_engine():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create database session for testing."""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.close()


# ==================== Mock Adapters ====================

@pytest.fixture
def mock_athena_adapter():
    """Mock athenahealth EHR adapter."""
    adapter = AsyncMock(spec=AthenaHealthAdapter)

    # Default successful responses
    adapter.get_appointment.return_value = {
        "appointment_id": "APT-12345",
        "patient_id": "PAT-12345",
        "scheduled_date": (datetime.now() + timedelta(days=2)).isoformat(),
        "procedure_codes": ["70553"],
        "procedure_descriptions": ["MRI Brain with Contrast"],
        "insurance_policy_id": "INS-POL-67890",
    }

    adapter.write_verification_note.return_value = {"success": True}

    return adapter


@pytest.fixture
def mock_prior_auth_adapter():
    """Mock Prior-Auth Database adapter."""
    adapter = AsyncMock(spec=PriorAuthDBAdapter)

    # Default: return valid prior-auth
    adapter.query_prior_auths.return_value = [
        {
            "prior_auth_id": "PA-2024-001",
            "patient_id": "PAT-12345",
            "insurance_policy_id": "INS-POL-67890",
            "approval_number": "AUTH987654",
            "approval_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "expiration_date": (datetime.now() + timedelta(days=45)).isoformat(),
            "approval_status": "ACTIVE",
            "approved_cpt_codes": ["70553"],
            "approved_service_description": "MRI Brain with Contrast",
            "service_category": "imaging",
            "approved_units": 2,
            "units_used": 0,
        }
    ]

    return adapter


@pytest.fixture
def mock_insurance_adapter():
    """Mock Insurance Requirements Database adapter."""
    adapter = AsyncMock(spec=InsuranceRequirementsAdapter)

    # Default: prior-auth required
    adapter.check_prior_auth_requirement.return_value = {
        "prior_auth_required": True,
        "insurance_policy_id": "INS-POL-67890",
        "procedure_code": "70553",
    }

    return adapter


@pytest.fixture
def decision_engine(mock_athena_adapter, mock_prior_auth_adapter, mock_insurance_adapter):
    """Create decision engine with mock adapters."""
    return PriorAuthDecisionEngine(
        athena_adapter=mock_athena_adapter,
        prior_auth_adapter=mock_prior_auth_adapter,
        insurance_adapter=mock_insurance_adapter,
    )


# ==================== Test Data Fixtures ====================

@pytest.fixture
def valid_prior_auth_check():
    """Create a basic PriorAuthCheck for testing."""
    return PriorAuthCheck(
        check_id="PAC-20240424-PAT12345-APT12345",
        patient_id="PAT-12345",
        appointment_id="APT-12345",
        scheduled_date=datetime.now() + timedelta(days=2),
        procedure_code="70553",
        procedure_description="MRI Brain with Contrast",
        insurance_policy_id="INS-POL-67890",
        status=CheckStatus.PENDING_CHECK,
    )


@pytest.fixture
def appointment_data():
    """Standard appointment data for testing."""
    return {
        "appointment_id": "APT-12345",
        "patient_id": "PAT-12345",
        "scheduled_date": (datetime.now() + timedelta(days=2)).isoformat(),
        "procedure_codes": ["70553"],
        "procedure_descriptions": ["MRI Brain with Contrast"],
        "insurance_policy_id": "INS-POL-67890",
    }


@pytest.fixture
def valid_prior_auth_record():
    """Standard valid prior-auth record."""
    return {
        "prior_auth_id": "PA-2024-001",
        "patient_id": "PAT-12345",
        "insurance_policy_id": "INS-POL-67890",
        "approval_number": "AUTH987654",
        "approval_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "expiration_date": (datetime.now() + timedelta(days=45)).isoformat(),
        "approval_status": "ACTIVE",
        "approved_cpt_codes": ["70553"],
        "approved_service_description": "MRI Brain with Contrast",
        "service_category": "imaging",
        "approved_units": 2,
        "units_used": 0,
    }


@pytest.fixture
def expired_prior_auth_record():
    """Prior-auth record that is expired."""
    return {
        "prior_auth_id": "PA-2024-002",
        "patient_id": "PAT-12345",
        "insurance_policy_id": "INS-POL-67890",
        "approval_number": "AUTH111222",
        "approval_date": (datetime.now() - timedelta(days=90)).isoformat(),
        "expiration_date": (datetime.now() - timedelta(days=10)).isoformat(),  # Expired
        "approval_status": "ACTIVE",
        "approved_cpt_codes": ["70553"],
        "approved_service_description": "MRI Brain with Contrast",
        "service_category": "imaging",
    }


@pytest.fixture
def expiring_soon_prior_auth_record():
    """Prior-auth record expiring within 7 days."""
    return {
        "prior_auth_id": "PA-2024-003",
        "patient_id": "PAT-12345",
        "insurance_policy_id": "INS-POL-67890",
        "approval_number": "AUTH333444",
        "approval_date": (datetime.now() - timedelta(days=60)).isoformat(),
        "expiration_date": (datetime.now() + timedelta(days=5)).isoformat(),  # 5 days
        "approval_status": "ACTIVE",
        "approved_cpt_codes": ["70553"],
        "approved_service_description": "MRI Brain with Contrast",
        "service_category": "imaging",
    }


@pytest.fixture
def same_day_expiration_prior_auth_record():
    """Prior-auth record expiring on appointment day."""
    scheduled_date = datetime.now() + timedelta(days=2)
    return {
        "prior_auth_id": "PA-2024-004",
        "patient_id": "PAT-12345",
        "insurance_policy_id": "INS-POL-67890",
        "approval_number": "AUTH555666",
        "approval_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "expiration_date": scheduled_date.isoformat(),  # Same day as appointment
        "approval_status": "ACTIVE",
        "approved_cpt_codes": ["70553"],
        "approved_service_description": "MRI Brain with Contrast",
        "service_category": "imaging",
    }


# ==================== Fuzzy Matcher Fixture ====================

@pytest.fixture
def fuzzy_matcher():
    """Create fuzzy matcher with standard threshold."""
    return FuzzyMatcher(threshold=0.8)


# ==================== Pytest Configuration ====================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit-level tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "edge_case: Edge case tests")
    config.addinivalue_line("markers", "functional: Functional requirement tests")
    config.addinivalue_line("markers", "slow: Tests that take significant time")


# ==================== Helper Functions ====================

def create_prior_auth_check(**kwargs):
    """Helper to create PriorAuthCheck with defaults."""
    defaults = {
        "check_id": f"PAC-{datetime.now().strftime('%Y%m%d%H%M%S')}-TEST",
        "patient_id": "PAT-12345",
        "appointment_id": "APT-12345",
        "scheduled_date": datetime.now() + timedelta(days=2),
        "procedure_code": "70553",
        "procedure_description": "MRI Brain with Contrast",
        "insurance_policy_id": "INS-POL-67890",
        "status": CheckStatus.CHECKING,  # FIX Phase 4: Default to CHECKING to allow valid transitions
        "created_at": datetime.utcnow(),  # FIX Phase 1: Explicitly set timestamp
        "last_updated_at": datetime.utcnow(),  # FIX Phase 1: Explicitly set timestamp
    }
    defaults.update(kwargs)
    return PriorAuthCheck(**defaults)


def assert_state_transition_valid(check, expected_status):
    """Helper to assert state transition occurred correctly."""
    assert check.status == expected_status
    assert check.last_updated_at is not None
