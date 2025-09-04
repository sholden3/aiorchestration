# Integration Tests

## Purpose
Integration tests for testing interactions between multiple components.

## Contents
- `governance/` - Governance system integration tests
  - `test_integrated_hook.py` - Pre-commit hook integration tests

## Dependencies
- pytest for test execution
- pytest-cov for coverage reporting
- All component dependencies
- Python 3.8+

## Testing
Run all integration tests:
```bash
pytest tests/integration/ -v
```

Run with coverage:
```bash
pytest tests/integration/ --cov=governance --cov-report=html
```

## Maintenance
- Add integration tests when new features interact
- Test critical paths end-to-end
- Update tests when interfaces change
- Review test effectiveness quarterly