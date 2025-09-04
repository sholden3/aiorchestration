# Testing Documentation

> Comprehensive testing strategy and documentation for the AI Development Assistant

**Parent Project:** AI Development Assistant | [**📖 Main Docs**](../../CLAUDE.md) | [**🏗️ Architecture**](../architecture/README.md)

## Overview

Complete testing documentation covering unit tests, integration tests, and test execution strategies for the AI Development Assistant project. This documentation provides detailed guidance on test implementation, coverage analysis, and maintenance procedures.

### Key Features
- 5-layer testing architecture (Unit → Integration → Contract → E2E → Chaos)
- Comprehensive coverage tracking with real metrics
- Critical fix validation and regression prevention
- Governance compliance testing with 95%+ scores

## Structure

```
testing/
├── testing-strategy.md    # Master testing strategy and 5-layer architecture
├── unit-tests.md         # Detailed unit test documentation and metrics
├── README.md            # This overview document
└── coverage/            # Generated coverage reports (HTML format)
```

## Quick Setup

### Prerequisites
- Node.js 18+ (Frontend testing with Jest)
- Python 3.10+ (Backend testing with Pytest)
- Angular CLI 17+ (Component testing)
- Electron (IPC testing environment)

### Installation
```bash
# Frontend test setup
cd ai-assistant
npm install
npm run test:clear-cache

# Backend test setup  
cd ..
pip install pytest pytest-cov pytest-asyncio

# Run all tests
npm run test:ci && python -m pytest
```

## Development

### Local Development
```bash
# Frontend development testing
npm run test:watch          # Watch mode for development
npm run test:debug         # Debug mode with heap usage
npm run test:single        # Run specific test pattern

# Backend development testing
pytest -v                  # Verbose unit tests
pytest -m "unit"          # Run only unit tests
pytest --lf               # Run last failed tests
```

### Testing
```bash
# Unit tests
npm test                   # Frontend unit tests (Jest)
pytest tests/unit/         # Backend unit tests

# Integration tests  
npm run test:electron      # Electron IPC integration
pytest tests/integration/ # Backend integration tests

# Coverage
npm run test:coverage      # Frontend coverage report
pytest --cov=. --cov-report=html  # Backend coverage report
```

### Building
```bash
# Development build
npm run build              # Angular build for testing
python -m pytest --collect-only  # Validate test discovery

# Production build
npm run build:electron     # Production Electron build
pytest --co                # Collect and validate all tests
```

## Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `TESTING` | Enable testing mode | `false` |
| `GOVERNANCE_BYPASS` | Bypass governance in tests | `false` |
| `DATABASE_URL` | Test database URL | `sqlite:///:memory:` |
| `LOG_LEVEL` | Test logging level | `INFO` |

### Configuration Files
- `jest.config.js` - Frontend test configuration with Electron support
- `pytest.ini` - Backend test configuration with coverage settings
- `src/test-setup.ts` - Angular testing environment setup
- `src/test-setup-electron.ts` - Electron mocking and IPC test setup

## API/Interface

### Key Test Commands
- **`npm test`** - Run frontend unit tests with Jest
- **`pytest`** - Run backend tests with pytest
- **`npm run test:coverage`** - Generate detailed coverage reports

### Integration Points
- **Jest/Angular Integration:** Component and service testing with TestBed
- **Pytest/FastAPI Integration:** Backend API and database testing
- **Electron/IPC Testing:** Cross-process communication validation

## Current Status

### Test Coverage by Service
| Service | Coverage | Status | Target |
|---------|----------|---------|---------|
| IPC Service | 58% | 🟡 Improving | 90% |
| Terminal Service | 12% | 🔴 Critical | 80% |
| Governance Engine | 95% | ✅ Excellent | 95% |
| Error Boundary | 75% | 🟡 Good | 85% |

### Recent Test Results
- **Total Tests:** 89 (65 passing, 24 failing)
- **Execution Time:** 4.2 minutes average
- **Overall Coverage:** 45% (Target: 80%)
- **Governance Tests:** 27/27 passing (100%)

## Troubleshooting

### Common Issues
1. **Electron IPC Test Timeouts**
   - **Symptom:** Tests hang or timeout after 45 seconds
   - **Solution:** Ensure proper Electron mocks and forceExit configuration

2. **Terminal Service Test Failures** 
   - **Symptom:** Memory leak tests pass but production issues persist
   - **Solution:** Verify component-scoped service registration patterns

3. **Coverage Report Generation**
   - **Symptom:** HTML coverage reports not generated
   - **Solution:** Check write permissions in coverage/ directory

### Debugging
```bash
# Debug mode
npm run test:debug         # Frontend debugging with heap monitoring
pytest --pdb              # Backend debugging with Python debugger

# Logs
npm run test:memory        # Memory usage analysis
pytest -s                 # Show print statements and logs
```

## Related Documentation

- [**Testing Strategy**](./testing-strategy.md) - Comprehensive 5-layer testing approach
- [**Unit Tests**](./unit-tests.md) - Detailed unit test documentation and metrics  
- [**Architecture**](../architecture/README.md) - System design and integration points
- [**Critical Issues**](../../claude/claude-sections/critical-issues.md) - Issues requiring test validation

---

**Component Owner:** Alex Novak & Dr. Sarah Chen | **Last Updated:** September 3, 2025 | **Status:** Active Development