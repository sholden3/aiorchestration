# Test Suite

## Purpose
Comprehensive test suite for all system components following 5-layer testing architecture.

## Contents
- `backend/` - Python backend tests
  - `unit/` - Unit tests
  - `integration/` - Integration tests
- `frontend/` - Angular/TypeScript tests
  - `unit/` - Component tests
  - `integration/` - Service integration tests
  - `e2e/` - End-to-end tests
- `electron/` - Electron-specific tests

## Dependencies
- pytest for Python tests
- Jest for JavaScript/TypeScript tests
- Selenium for E2E tests
- Mock libraries for isolation

## Testing
- Run all: `pytest && npm test`
- Coverage requirement: 85% backend, 80% frontend
- All tests must pass before commit

## Maintenance
- Add tests for every new feature
- Update tests when code changes
- Remove obsolete tests
- Maintain test documentation