# Prior-Authorization Check Test Suite

Comprehensive pytest test suite implementing all validation criteria from `CLAUDE.md` and referenced specification documents.

## Test Coverage

### Unit Tests (5 test suites)
- ✅ **test_unit_prior_auth_requirement.py** - Test 1: Prior-Auth Requirement Determination (REQ-PA-001)
  - Pass Criteria: 100% accuracy on 50 test cases
  - Tests Step 1 of decision logic
  
- ✅ **test_unit_cpt_matching.py** - Test 2: CPT Code Matching Logic (REQ-PA-003)
  - Pass Criteria: 95% accuracy on 100 test cases
  - Tests Step 3: exact match, fuzzy match, multiple prior-auths
  
- ✅ **test_unit_expiration.py** - Test 3: Expiration Date Calculation (REQ-PA-004)
  - Pass Criteria: 100% accuracy on 20 test cases
  - Tests Step 4: expired, expiring soon, valid, same-day expiration
  
- ✅ **test_unit_confidence_score.py** - Test 4: Confidence Score Calculation (REQ-PA-009)
  - Pass Criteria: 90% accuracy on 50 test cases
  - Tests Step 5: HIGH/MEDIUM/LOW confidence assignment
  
- ✅ **test_unit_state_machine.py** - Test 5: State Transition Validation (REQ-PA-010)
  - Pass Criteria: 100% valid transitions succeed, 100% invalid transitions blocked
  - Tests state machine enforcement per CLAUDE.md Section 2

### Integration Tests (5 test suites)
- ✅ **test_integration.py** - Tests 6-10
  - Test 6: athenahealth EHR Integration (REQ-PA-006)
  - Test 7: Prior-Auth Database Integration (REQ-PA-002)
  - Test 8: Human Review Interface (REQ-PA-005)
  - Test 9: Error Handling - Database Unavailable (REQ-PA-008)
  - Test 10: Error Handling - EHR Write Failure
  - Pass Criteria: 95% pass rate

### End-to-End Tests (5 test suites)
- ✅ **test_e2e_workflows.py** - Tests 11-15
  - Test 11: Happy Path - Valid Prior-Auth
  - Test 12: Expired Prior-Auth
  - Test 13: Missing Prior-Auth
  - Test 14: Ambiguous Case - Multiple Prior-Auths
  - Test 15: System Error - Database Unavailable
  - Pass Criteria: 90% pass rate

### Edge Case Tests (8 scenarios)
- ✅ **test_edge_cases.py** - All edge cases from specs/edge-cases-and-testing.md
  1. Prior-Auth Expires on the Day of the Appointment
  2. Patient Has Multiple Prior-Auths on File
  3. Prior-Auth Approval Language is Vague
  4. Prior-Auth Database is Unavailable
  5. Procedure Code in EHR Doesn't Match Any Prior-Auth on File
  6. Prior-Auth Was Approved But Insurance Policy is Now Inactive
  7. Prior-Auth Record Has Missing Expiration Date
  8. Appointment Scheduled for Multiple Procedures

### Functional Requirements Tests (10 requirements)
- ✅ **test_functional_requirements.py** - REQ-PA-001 through REQ-PA-010
  - All functional requirements from specs/requirements.md
  - Verifies compliance with specification

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# E2E tests only
pytest -m e2e

# Edge case tests only
pytest -m edge_case

# Functional requirement tests only
pytest -m functional
```

### Run specific test files
```bash
pytest tests/test_unit_prior_auth_requirement.py
pytest tests/test_e2e_workflows.py
pytest tests/test_edge_cases.py
```

### Run specific test classes
```bash
pytest tests/test_unit_expiration.py::TestExpirationDateCalculation
pytest tests/test_e2e_workflows.py::TestE2EHappyPath
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html to view coverage report
```

### Run excluding slow tests
```bash
pytest -m "not slow"
```

### Run with verbose output
```bash
pytest -vv
```

## Test Fixtures

All fixtures are defined in `tests/conftest.py`:

- **Database fixtures**: `test_db_engine`, `db_session`
- **Mock adapters**: `mock_athena_adapter`, `mock_prior_auth_adapter`, `mock_insurance_adapter`
- **Decision engine**: `decision_engine` (with mock adapters)
- **Test data**: `valid_prior_auth_check`, `appointment_data`, `valid_prior_auth_record`, etc.

## Success Criteria

From `CLAUDE.md` Section 1:

1. **Error Rate Reduction**: <0.75% (75% reduction from 3%)
   - Measurement: Weekly audit comparing AI recommendations to ground truth

2. **Time Efficiency**: ≤0.5 min human review time (80% reduction from 2.5 min)
   - Measurement: Time-motion study of front-desk staff

3. **Escalation Rate**: <20% (AI handles ≥80% with high confidence)
   - Measurement: Daily tracking of escalation rate

4. **Accuracy**: ≥95% when confidence = HIGH
   - Measurement: Weekly audit comparing AI recommendations to human decisions

5. **Availability**: ≥99% uptime during business hours
   - Measurement: Uptime monitoring

## Test Data Requirements

Per `specs/edge-cases-and-testing.md`:

- **Test Prior-Auth Records**: Minimum 50 records (valid, expiring, expired, missing data, vague language)
- **Test Appointments**: Minimum 100 appointments (various procedure types)
- **Test Patients**: Minimum 30 patients (single/multiple prior-auths, no prior-auth)
- **Test Insurance Policies**: Minimum 10 policies (varying prior-auth requirements)

## Dependencies

Required packages (from `requirements.txt`):
- pytest==7.4.4
- pytest-asyncio==0.23.3
- pytest-cov (optional, for coverage)

## Continuous Integration

To integrate with CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pytest -m "not slow" --cov=app --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Test Organization

```
tests/
├── conftest.py                              # Shared fixtures and configuration
├── test_unit_prior_auth_requirement.py      # Unit Test 1
├── test_unit_cpt_matching.py                # Unit Test 2
├── test_unit_expiration.py                  # Unit Test 3
├── test_unit_confidence_score.py            # Unit Test 4
├── test_unit_state_machine.py               # Unit Test 5
├── test_integration.py                      # Integration Tests 6-10
├── test_e2e_workflows.py                    # E2E Tests 11-15
├── test_edge_cases.py                       # Edge Cases 1-8
├── test_functional_requirements.py          # REQ-PA-001 through REQ-PA-010
└── test_fuzzy_matcher.py                    # Existing fuzzy matcher tests
```

## Known Issues / TODO

- [ ] Add performance benchmarking tests (response time <10 seconds)
- [ ] Add load testing (90 checks/day, 20 checks/hour peak)
- [ ] Add security tests (HIPAA compliance, encryption, access control)
- [ ] Add audit log validation tests
- [ ] Add UI/frontend tests for human review interface
- [ ] Add actual athenahealth EHR integration tests (requires test environment)
- [ ] Add multiple procedures per appointment tests (requires higher-level orchestration)

## Contributing

When adding new tests:
1. Follow existing naming conventions (`test_<category>_<description>`)
2. Add appropriate markers (`@pytest.mark.unit`, etc.)
3. Include docstrings explaining what is being tested
4. Update this README with new test coverage
5. Ensure tests are independent and can run in any order
6. Mock external dependencies (EHR, databases, APIs)

## References

- **Main Specification**: `/CLAUDE.md`
- **Decision Logic**: `/specs/decision-logic.md`
- **Edge Cases & Testing**: `/specs/edge-cases-and-testing.md`
- **Requirements**: `/specs/requirements.md`
- **Assumptions**: `/specs/assumptions.md`
- **API Specifications**: `/specs/api-specifications.md`
