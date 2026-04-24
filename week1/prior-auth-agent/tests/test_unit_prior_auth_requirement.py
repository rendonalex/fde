"""
Unit Test 1: Prior-Auth Requirement Determination

Tests Step 1 of decision logic per Claude.md Section 3 and
edge-cases-and-testing.md Test 1.

Pass Criteria: 100% accuracy on 50 test cases
"""
import pytest
from datetime import datetime, timedelta

from app.models.prior_auth_check import CheckStatus, PriorAuthStatus
from tests.conftest import create_prior_auth_check


@pytest.mark.unit
@pytest.mark.asyncio
class TestPriorAuthRequirement:
    """Test prior-auth requirement determination logic."""

    async def test_procedure_requires_prior_auth(self, decision_engine, mock_insurance_adapter):
        """Test procedure that requires prior-auth (CPT 70553 - MRI)."""
        check = create_prior_auth_check(procedure_code="70553")
        mock_insurance_adapter.check_prior_auth_requirement.return_value = {
            "prior_auth_required": True
        }

        result = await decision_engine.step1_determine_requirement(check, {})

        assert result["exit"] is False  # Continue to Step 2
        assert check.prior_auth_required is True
        assert check.status == CheckStatus.CHECKING  # FIX: Should remain in CHECKING state

    async def test_procedure_does_not_require_prior_auth(self, decision_engine, mock_insurance_adapter):
        """Test procedure that does NOT require prior-auth (CPT 99213 - office visit)."""
        check = create_prior_auth_check(procedure_code="99213")
        mock_insurance_adapter.check_prior_auth_requirement.return_value = {
            "prior_auth_required": False
        }

        result = await decision_engine.step1_determine_requirement(check, {})

        assert result["exit"] is True  # Exit early
        assert check.prior_auth_required is False
        assert check.status == CheckStatus.COMPLETED
        assert "does not require prior-authorization" in check.confidence_rationale

    async def test_no_procedure_codes(self, decision_engine):
        """Test appointment with no procedure codes (routine visit)."""
        check = create_prior_auth_check(procedure_code="")

        result = await decision_engine.step1_determine_requirement(check, {})

        assert result["exit"] is True
        assert check.prior_auth_required is False
        assert check.status == CheckStatus.COMPLETED
        assert "No procedures scheduled" in check.confidence_rationale

    async def test_unknown_procedure_code(self, decision_engine, mock_insurance_adapter):
        """Test procedure code not in insurance requirements database."""
        check = create_prior_auth_check(procedure_code="99999")
        mock_insurance_adapter.check_prior_auth_requirement.return_value = {
            "prior_auth_required": None  # Unknown
        }

        result = await decision_engine.step1_determine_requirement(check, {})

        assert result["exit"] is True
        assert check.status == CheckStatus.ESCALATED
        assert "Cannot determine if prior-auth required" in check.escalation_reason

    async def test_insurance_database_error(self, decision_engine, mock_insurance_adapter):
        """Test error when querying insurance requirements database."""
        check = create_prior_auth_check(procedure_code="70553")
        mock_insurance_adapter.check_prior_auth_requirement.side_effect = Exception("Database timeout")

        result = await decision_engine.step1_determine_requirement(check, {})

        assert result["exit"] is True
        assert check.status == CheckStatus.ESCALATED
        assert "Insurance requirements database error" in check.escalation_reason

    async def test_imaging_procedures_require_prior_auth(self, decision_engine, mock_insurance_adapter):
        """Test common imaging procedures that require prior-auth."""
        imaging_codes = ["70553", "70551", "72148", "73721", "74177"]  # Various MRI/CT codes

        for cpt_code in imaging_codes:
            check = create_prior_auth_check(procedure_code=cpt_code)
            mock_insurance_adapter.check_prior_auth_requirement.return_value = {
                "prior_auth_required": True
            }

            result = await decision_engine.step1_determine_requirement(check, {})

            assert check.prior_auth_required is True
            assert result["exit"] is False

    async def test_office_visits_do_not_require_prior_auth(self, decision_engine, mock_insurance_adapter):
        """Test office visit codes that typically don't require prior-auth."""
        office_visit_codes = ["99213", "99214", "99203", "99204"]

        for cpt_code in office_visit_codes:
            check = create_prior_auth_check(procedure_code=cpt_code)
            mock_insurance_adapter.check_prior_auth_requirement.return_value = {
                "prior_auth_required": False
            }

            result = await decision_engine.step1_determine_requirement(check, {})

            assert check.prior_auth_required is False
            assert result["exit"] is True
            assert check.status == CheckStatus.COMPLETED

    async def test_surgical_procedures_require_prior_auth(self, decision_engine, mock_insurance_adapter):
        """Test surgical procedures that require prior-auth."""
        surgical_codes = ["27447", "29881", "63030"]  # Joint replacement, arthroscopy, laminectomy

        for cpt_code in surgical_codes:
            check = create_prior_auth_check(procedure_code=cpt_code)
            mock_insurance_adapter.check_prior_auth_requirement.return_value = {
                "prior_auth_required": True
            }

            result = await decision_engine.step1_determine_requirement(check, {})

            assert check.prior_auth_required is True
            assert result["exit"] is False

    async def test_lab_work_does_not_require_prior_auth(self, decision_engine, mock_insurance_adapter):
        """Test lab work codes that don't require prior-auth."""
        lab_codes = ["80053", "85025", "80061"]  # Metabolic panel, CBC, lipid panel

        for cpt_code in lab_codes:
            check = create_prior_auth_check(procedure_code=cpt_code)
            mock_insurance_adapter.check_prior_auth_requirement.return_value = {
                "prior_auth_required": False
            }

            result = await decision_engine.step1_determine_requirement(check, {})

            assert check.prior_auth_required is False
            assert check.status == CheckStatus.COMPLETED

    async def test_whitespace_only_procedure_code(self, decision_engine):
        """Test procedure code with only whitespace."""
        check = create_prior_auth_check(procedure_code="   ")

        result = await decision_engine.step1_determine_requirement(check, {})

        assert result["exit"] is True
        assert check.prior_auth_required is False
        assert check.status == CheckStatus.COMPLETED
