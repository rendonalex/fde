"""
Mock PA data generator for testing
Based on Artefact 5.1 format from scenario
"""
from datetime import date, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import PriorAuthorization, PAStatus


def generate_sample_pas(base_date: date = None) -> list[PriorAuthorization]:
    """
    Generate sample PA cases for testing.
    Mirrors Artefact 5.1 examples from Dana's Google Sheet.
    """
    if base_date is None:
        base_date = date.today()

    sample_pas = [
        # Case 1: Humana colonoscopy (submitted 6 days ago, should be ready to chase)
        PriorAuthorization(
            pa_id="PA-2026-001",
            patient_id="PT-12345",
            patient_name="John Smith",
            insurer="Humana",
            procedure_type="Colonoscopy",
            procedure_date=base_date + timedelta(days=3),
            submission_date=base_date - timedelta(days=6),
            status=PAStatus.PENDING,
            notes="Standard screening colonoscopy"
        ),

        # Case 2: UHC shoulder MRI (submitted 5 days ago, should wait 2 more days)
        PriorAuthorization(
            pa_id="PA-2026-002",
            patient_id="PT-67890",
            patient_name="Sarah Johnson",
            insurer="UnitedHealthcare Choice",
            procedure_type="MRI - Shoulder",
            procedure_date=base_date + timedelta(days=7),
            submission_date=base_date - timedelta(days=5),
            status=PAStatus.PENDING,
            notes="Chronic shoulder pain evaluation"
        ),

        # Case 3: Wellpath colonoscopy (DENIED - should trigger denial pattern match)
        PriorAuthorization(
            pa_id="PA-2026-003",
            patient_id="PT-11223",
            patient_name="Michael Brown",
            insurer="Wellpath",
            procedure_type="Colonoscopy",
            procedure_date=base_date + timedelta(days=10),
            submission_date=base_date - timedelta(days=8),
            status=PAStatus.DENIED,
            denial_reason="Prior authorization denied - medical necessity not established",
            notes="Medicaid managed care; first submission"
        ),

        # Case 4: Aetna cardiac stress test (should escalate - unpredictable insurer)
        PriorAuthorization(
            pa_id="PA-2026-004",
            patient_id="PT-44556",
            patient_name="Lisa Davis",
            insurer="Aetna",
            procedure_type="Cardiac Stress Test",
            procedure_date=base_date + timedelta(days=5),
            submission_date=base_date - timedelta(days=4),
            status=PAStatus.PENDING,
            notes="Chest pain evaluation"
        ),

        # Case 5: BCBS PPO imaging (submitted 3 days ago, should be ready to chase)
        PriorAuthorization(
            pa_id="PA-2026-005",
            patient_id="PT-77889",
            patient_name="Robert Wilson",
            insurer="BCBS PPO",
            procedure_type="CT Scan - Abdomen",
            procedure_date=base_date + timedelta(days=4),
            submission_date=base_date - timedelta(days=3),
            status=PAStatus.PENDING,
            notes="Abdominal pain workup"
        ),

        # Case 6: Medicare knee replacement (submitted 4 days ago, wait 1 more day)
        PriorAuthorization(
            pa_id="PA-2026-006",
            patient_id="PT-99001",
            patient_name="Barbara Martinez",
            insurer="Medicare",
            procedure_type="Knee Replacement Surgery",
            procedure_date=base_date + timedelta(days=14),
            submission_date=base_date - timedelta(days=4),
            status=PAStatus.PENDING,
            notes="Severe osteoarthritis; surgery scheduled"
        ),

        # Case 7: URGENT - Humana MRI, procedure in 2 days, PA still pending
        PriorAuthorization(
            pa_id="PA-2026-007",
            patient_id="PT-22334",
            patient_name="David Lee",
            insurer="Humana",
            procedure_type="MRI - Brain",
            procedure_date=base_date + timedelta(days=2),  # URGENT
            submission_date=base_date - timedelta(days=7),
            status=PAStatus.PENDING,
            notes="Neurological symptoms; urgent evaluation needed"
        ),

        # Case 8: Unknown insurer (should escalate)
        PriorAuthorization(
            pa_id="PA-2026-008",
            patient_id="PT-55667",
            patient_name="Jennifer Taylor",
            insurer="Cigna",  # Not in pattern library
            procedure_type="Physical Therapy",
            procedure_date=base_date + timedelta(days=6),
            submission_date=base_date - timedelta(days=3),
            status=PAStatus.PENDING,
            notes="New insurer; no historical pattern"
        ),
    ]

    return sample_pas


def generate_approved_pa_for_accuracy_test() -> PriorAuthorization:
    """
    Generate PA that was approved (for testing anomaly detection)
    """
    return PriorAuthorization(
        pa_id="PA-2026-999",
        patient_id="PT-99999",
        patient_name="Test Patient",
        insurer="Humana",
        procedure_type="Colonoscopy",
        procedure_date=date.today() + timedelta(days=1),
        submission_date=date.today() - timedelta(days=6),
        status=PAStatus.APPROVED,
        approval_date=date.today(),  # Approved today (6 days after submission = expected)
        notes="Test case for accuracy tracking"
    )


if __name__ == "__main__":
    # Test data generation
    pas = generate_sample_pas()
    print(f"Generated {len(pas)} sample PA cases:")
    for pa in pas:
        print(f"  - {pa.pa_id}: {pa.patient_name}, {pa.insurer}, {pa.procedure_type}, Status: {pa.status.value}")
