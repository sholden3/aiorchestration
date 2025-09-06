# Testing Strategy

**Last Updated:** 2025-09-03  
**Reviewed By:** Sam Martinez (QA Lead) & Both Architects  
**Next Review:** 2025-10-01  

## Overview
The AI Orchestration Platform follows a comprehensive 5-layer testing strategy emphasizing both unit and integration tests. Our approach requires explicit approval for any testing simplification and enforces strict coverage requirements for all critical functionality.

## Testing Philosophy
### Quality Gates
- **Pre-commit Validation:** All tests must pass before commit
- **Coverage Requirements:** 85% Python, 80% TypeScript/JavaScript
- **Integration Validation:** All component boundaries must be tested
- **Performance Baselines:** Response times must meet SLA requirements

### Testing Principles
- **Tests Reveal Truth:** Documentation claims must match actual implementation
- **No Simplification Without Approval:** Testing changes require architect discussion
- **Fast Feedback:** Unit tests provide immediate feedback during development
- **Comprehensive Validation:** Integration tests verify real-world scenarios
- **Regression Prevention:** Every bug fix must include regression tests

## Test Categories
### Unit Tests
**Purpose:** Test individual functions and components in isolation
**Scope:** Single function/method/component without external dependencies
**Tools:** Pytest (Python), Jest (TypeScript/JavaScript)
**Target Coverage:** 85% for Python, 80% for TypeScript

### Integration Tests
**Purpose:** Verify component interactions and system boundaries
**Scope:** Multiple components working together with real dependencies
**Tools:** Pytest with async support, Jest with TestBed
**Target Coverage:** 100% of component boundaries

### Contract Tests
**Purpose:** Ensure API contracts and backward compatibility
**Scope:** API endpoints, data models, service interfaces
**Tools:** Pact, OpenAPI validation
**Target Coverage:** All public APIs and service boundaries

### End-to-End Tests
**Purpose:** Validate complete user workflows
**Scope:** Full application stack from UI to database
**Tools:** Cypress, Playwright
**Target Coverage:** Critical user paths (login, core features)

### Performance Tests
**Purpose:** Ensure system meets performance requirements
**Scope:** API response times, database queries, UI rendering
**Tools:** K6, Apache JMeter, Lighthouse
**Frequency:** Weekly automated runs, before major releases

### Security Tests
**Purpose:** Identify vulnerabilities and security issues
**Scope:** Authentication, authorization, data protection, injection attacks
**Tools:** OWASP ZAP, Snyk, npm audit
**Frequency:** Daily dependency scans, weekly security sweeps

## MCP Testing Strategy

### MCP Governance Server Testing
**Purpose:** Validate MCP server functionality and governance decisions  
**Scope:** Server initialization, persona consultation, decision caching  
**Tools:** Pytest with async support, unittest.mock for personas  
**Target Coverage:** 90% minimum (critical infrastructure)  

#### Key Test Areas
1. **Server Initialization**
   - Port discovery and allocation
   - Configuration loading and validation
   - Database connection establishment
   - Persona manager initialization

2. **Governance Consultation**
   - Single persona decisions
   - Multi-persona consensus
   - Context validation
   - Decision caching and retrieval

3. **Hook Bridge Integration**
   - PreToolUse validation
   - UserPromptSubmit checking
   - PostToolUse verification
   - Error handling and recovery

#### Test Implementation
```python
# tests/unit/mcp/test_governance_server.py
async def test_server_initialization():
    """Test MCP server starts correctly."""
    server = GovernanceMCPServer()
    await server.initialize()
    assert server.port in range(8001, 8101)
    assert server.personas_loaded == 12

async def test_persona_consultation():
    """Test persona decision making."""
    server = GovernanceMCPServer()
    context = {"tool": "Write", "path": "critical.py"}
    decision = await server.consult_governance(context)
    assert decision.approved in [True, False]
    assert decision.confidence > 0.0

async def test_hook_validation():
    """Test Claude Code hook integration."""
    bridge = ClaudeCodeHookBridge()
    hook_data = {"tool": "Edit", "params": {...}}
    can_proceed, message = await bridge.pre_tool_validation(hook_data)
    assert isinstance(can_proceed, bool)
    assert isinstance(message, str)
```

### MCP Integration Testing
**Purpose:** Validate end-to-end MCP workflows  
**Scope:** Full request cycle from hook to decision  
**Tools:** Pytest, httpx for HTTP testing, WebSocket test client  
**Target Coverage:** All critical paths  

#### Integration Test Scenarios
1. **Happy Path Flow**
   ```python
   async def test_mcp_happy_path():
       # 1. Hook receives request
       # 2. Bridge forwards to MCP
       # 3. MCP consults personas
       # 4. Decision returned
       # 5. Hook allows/blocks operation
   ```

2. **Circuit Breaker Testing**
   ```python
   async def test_circuit_breaker_resilience():
       # 1. Simulate failures
       # 2. Verify circuit opens
       # 3. Test fail-open behavior
       # 4. Verify recovery
   ```

3. **Performance Under Load**
   ```python
   async def test_concurrent_consultations():
       # 1. Send 100 concurrent requests
       # 2. Verify all complete < 5s
       # 3. Check cache hit rate > 80%
       # 4. Validate no data corruption
   ```

### MCP Test Data Management
- **Mock Personas:** Use test personas with predictable behaviors
- **Test Contexts:** Predefined contexts for consistent testing
- **Cache Seeding:** Pre-populate cache for performance tests
- **Database Fixtures:** Test database with known state

## Test Organization
### Directory Structure
```
project-root/
├── tests/                      # Root test directory
│   ├── unit/                   # Unit tests
│   │   ├── backend/           # Python unit tests
│   │   ├── frontend/          # TypeScript unit tests
│   │   ├── governance/        # Validator tests
│   │   └── mcp/              # MCP server tests
│   ├── integration/           # Integration tests
│   │   ├── api/              # API integration tests
│   │   ├── database/         # Database tests
│   │   ├── services/         # Service integration
│   │   └── mcp/              # MCP integration tests
│   ├── e2e/                   # End-to-end tests
│   ├── performance/           # Performance tests
│   └── security/             # Security tests
├── apps/
│   ├── apps/api/tests/         # Backend-specific tests
│   ├── apps/api/mcp/tests/     # MCP-specific tests
│   └── apps/web/src/app/**/*.spec.ts   # Angular component tests
└── libs/governance/tests/      # Governance-specific tests
```

### Test Naming Conventions
- **Unit Tests:** `test_<function_name>.py` or `<component>.spec.ts`
- **Integration Tests:** `test_integration_<feature>.py` or `<feature>.integration.spec.ts`
- **E2E Tests:** `<workflow>.e2e.spec.ts`
- **Performance Tests:** `perf_<scenario>.js`
- **Security Tests:** `security_<vulnerability>.py`

## Testing Tools & Framework
### Backend Testing Stack
- **Language:** Python 3.10+
- **Framework:** Pytest with async support
- **Assertions:** Built-in assert with pytest matchers
- **Mocking:** unittest.mock, pytest-mock
- **Coverage:** pytest-cov (target: 85%)
- **Database:** pytest-asyncio with test transactions
- **HTTP:** httpx for async API testing

### Frontend Testing Stack
- **Language:** TypeScript
- **Framework:** Jest 29+
- **Component Testing:** Angular TestBed
- **E2E Testing:** Cypress/Playwright
- **Visual Testing:** Percy (planned)
- **Coverage:** Jest coverage reporter (target: 80%)
- **Mocking:** Jest mocks, ng-mocks

## Coverage Requirements
### Critical Fixes (C1-C3)
- **Required Coverage:** 100%
- **Test Types:** Unit + Integration + E2E
- **Regression Tests:** Mandatory

### High Priority (H1-H3)
- **Required Coverage:** 90%
- **Test Types:** Unit + Integration
- **Performance Tests:** Required for H1 (WebSocket)

### New Features
- **Required Coverage:** 80%
- **Test Types:** Unit + Integration
- **Documentation:** Test documentation required

### Bug Fixes
- **Required Coverage:** Regression test mandatory
- **Test Types:** Unit test minimum
- **Verification:** Manual testing before merge

## Test Execution
### Local Development
```bash
# Python backend tests
pytest tests/unit/backend -v
pytest tests/integration --cov=backend

# TypeScript frontend tests
npm test
npm run test:coverage

# Governance validator tests
pytest tests/unit/governance -xvs
```

### CI/CD Pipeline
```yaml
test-pipeline:
  - lint-check
  - unit-tests (parallel)
  - integration-tests
  - coverage-check
  - security-scan
  - performance-baseline
```

### Pre-commit Hooks
```bash
# Automatically run on commit
- Python linting (black, flake8)
- TypeScript linting (eslint)
- Unit tests for changed files
- Coverage verification
```

## Test Data Management
### Test Database
- **Strategy:** Isolated test database per test run
- **Fixtures:** Pytest fixtures for common data
- **Cleanup:** Automatic rollback after each test
- **Seeds:** Standardized test data sets

### Mock Data
- **Factory Pattern:** Test data factories for consistency
- **Builders:** Flexible data builders for edge cases
- **Snapshots:** Jest snapshots for UI testing

## Performance Benchmarks
### API Response Times
- **P50:** <100ms
- **P95:** <500ms
- **P99:** <1000ms

### Database Queries
- **Simple Queries:** <10ms
- **Complex Queries:** <50ms
- **Batch Operations:** <200ms

### Frontend Metrics
- **First Contentful Paint:** <1s
- **Time to Interactive:** <2s
- **Bundle Size:** <500KB gzipped

## Continuous Improvement
### Test Metrics Tracking
- Coverage trends over time
- Test execution time optimization
- Flaky test identification and fixes
- False positive/negative rates

### Review Process
- Monthly test strategy review
- Quarterly tool evaluation
- Sprint retrospective test discussions
- Annual testing maturity assessment

## Approval Requirements
### ⚠️ MANDATORY: Testing changes require approval
The following require explicit architect approval:
- Simplifying any testing approach
- Skipping integration tests
- Reducing coverage requirements
- Changing test patterns
- Modifying test infrastructure

### Decision Process
1. Identify testing issue
2. Architect discussion (both required)
3. Document decision with rationale
4. Update DECISIONS.md
5. Implement only after approval

---

## Change Log
| Date | Change | Author | Impact |
|------|--------|--------|--------|
| 2025-09-03 | Complete testing strategy documentation | Sam Martinez | Major |
| 2025-09-02 | Added 5-layer testing architecture | Both Architects | High |
| 2025-09-01 | Established coverage requirements | Sam Martinez | Medium |

## References
- [Test Implementation Plan](#test-orchestration)
- [Unit Test Guide](./unit-tests.md)
- [Governance Testing](../../tests/unit/governance/)
- [Testing Decisions](../../DECISIONS.md)