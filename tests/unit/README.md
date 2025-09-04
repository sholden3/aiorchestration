# Unit Tests

## Purpose
Unit tests for individual components and functions across the codebase.

## Contents
- `governance/` - Tests for governance system components
  - `test_doc_validator.py` - Document validator tests
  - `test_code_doc_validator.py` - Code documentation validator tests
  - `test_domain_validators.py` - Domain-specific validator tests
  - `test_correlation_tracker.py` - Correlation tracker tests
  - `test_enhanced_governance_engine.py` - Governance engine tests
  - `test_exemptions.py` - Exemption system tests
  - `test_runtime_governance.py` - Runtime governance tests
  - `test_smart_rules.py` - Smart rule system tests

## Dependencies
- pytest for test execution
- pytest-cov for coverage reporting
- unittest.mock for mocking
- Python 3.8+

## Testing
Run all unit tests:
```bash
pytest tests/unit/ -v
```

Run with coverage:
```bash
pytest tests/unit/ --cov=governance --cov-report=html
```

## Maintenance
- Add tests when new features are added
- Maintain 85%+ coverage for backend
- Update tests when implementations change
- Review and remove obsolete tests quarterly