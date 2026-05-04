"""
Test suite for PA Chase Timing Agent
Demonstrates core functionality with mock data
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import date, timedelta
from src import PatternLibrary, ChaseEngine, PriorAuthorization, PAStatus, ActionType
from data.mock_pa_data import generate_sample_pas


def test_pattern_library():
    """Test pattern library initialization and retrieval"""
    print("\n=== TEST 1: Pattern Library ===")
    library = PatternLibrary()

    # Test pattern retrieval
    humana = library.get_pattern("Humana")
    print(f"Humana SLA: {humana.sla_days} days (confidence: {humana.confidence.value})")
    print(f"  Notes: {humana.notes}")

    aetna = library.get_pattern("Aetna")
    print(f"\nAetna SLA: {aetna.sla_days} days (confidence: {aetna.confidence.value})")
    print(f"  Predictable: {aetna.is_predictable}")

    # Test predictable vs unpredictable insurers
    predictable = library.get_predictable_insurers()
    unpredictable = library.get_unpredictable_insurers()
    print(f"\nPredictable insurers: {predictable}")
    print(f"Unpredictable insurers (escalate): {unpredictable}")

    # Test denial pattern matching
    denial = library.find_denial_pattern(
        "Wellpath", "Colonoscopy", "Prior authorization denied - medical necessity not established"
    )
    if denial:
        print(f"\nDenial pattern match found:")
        print(f"  Workaround: {denial.workaround_suggestion}")
        print(f"  Occurrence count: {denial.occurrence_count}")


def test_chase_engine_recommendations():
    """Test chase engine recommendation logic"""
    print("\n=== TEST 2: Chase Engine Recommendations ===")

    library = PatternLibrary()
    engine = ChaseEngine(library)

    # Generate sample PAs
    pas = generate_sample_pas(base_date=date.today())

    for pa in pas:
        print(f"\n--- PA: {pa.pa_id} ({pa.patient_name}) ---")
        print(f"Insurer: {pa.insurer}, Procedure: {pa.procedure_type}")
        print(f"Submitted: {pa.submission_date}, Procedure date: {pa.procedure_date}")
        print(f"Status: {pa.status.value}")

        # Generate recommendation
        recommendation = engine.generate_recommendation(pa, current_date=date.today())

        print(f"\nRECOMMENDATION:")
        print(f"  Action: {recommendation.action.value}")
        print(f"  Rationale: {recommendation.rationale}")
        print(f"  Confidence: {recommendation.confidence.value}")
        if recommendation.recommended_chase_date:
            print(f"  Chase date: {recommendation.recommended_chase_date}")
        if recommendation.escalation_reason:
            print(f"  Escalation reason: {recommendation.escalation_reason}")


def test_anomaly_detection():
    """Test anomaly detection for timing deviations"""
    print("\n=== TEST 3: Anomaly Detection ===")

    library = PatternLibrary()
    engine = ChaseEngine(library)

    # Test PA: Humana colonoscopy (expected 6 days)
    pa = PriorAuthorization(
        pa_id="PA-ANOMALY-TEST",
        patient_id="PT-TEST",
        patient_name="Test Patient",
        insurer="Humana",
        procedure_type="Colonoscopy",
        procedure_date=date.today() + timedelta(days=1),
        submission_date=date.today() - timedelta(days=10),
        status=PAStatus.APPROVED,
        approval_date=date.today()
    )

    # Scenario 1: Approved in 10 days (expected 6) → anomaly
    anomaly = engine.detect_anomaly(pa, actual_approval_date=date.today())
    if anomaly:
        print(f"Anomaly detected: {anomaly}")
    else:
        print("No anomaly (expected)")

    # Scenario 2: Approved in 5 days (expected 6) → anomaly (early)
    early_approval = pa.submission_date + timedelta(days=5)
    anomaly2 = engine.detect_anomaly(pa, actual_approval_date=early_approval)
    if anomaly2:
        print(f"Anomaly detected (early): {anomaly2}")


def test_dana_correction_learning():
    """Test Dana correction processing"""
    print("\n=== TEST 4: Dana Correction Learning ===")

    library = PatternLibrary()
    engine = ChaseEngine(library)

    # Simulate Dana's correction
    agent_recommended = date.today()
    dana_corrected = date.today() + timedelta(days=2)  # Dana pushes 2 days later

    result = engine.process_dana_correction(
        pa_id="PA-2026-001",
        agent_recommended=agent_recommended,
        dana_corrected=dana_corrected,
        insurer="Humana"
    )

    print(f"Dana correction logged: {result}")


def test_json_output():
    """Test JSON serialization of recommendations"""
    print("\n=== TEST 5: JSON Output Format ===")

    library = PatternLibrary()
    engine = ChaseEngine(library)

    # Generate sample PA
    pa = PriorAuthorization(
        pa_id="PA-JSON-TEST",
        patient_id="PT-12345",
        patient_name="John Doe",
        insurer="Humana",
        procedure_type="Colonoscopy",
        procedure_date=date.today() + timedelta(days=3),
        submission_date=date.today() - timedelta(days=6),
        status=PAStatus.PENDING
    )

    recommendation = engine.generate_recommendation(pa, current_date=date.today())

    import json
    print(json.dumps(recommendation.to_json(), indent=2))


if __name__ == "__main__":
    print("=" * 60)
    print("PA CHASE TIMING AGENT - TEST SUITE")
    print("=" * 60)

    test_pattern_library()
    test_chase_engine_recommendations()
    test_anomaly_detection()
    test_dana_correction_learning()
    test_json_output()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)
