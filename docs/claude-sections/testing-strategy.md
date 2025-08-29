# 🧪 TESTING STRATEGY & GOVERNANCE (MANDATORY)

## Hybrid Testing Approach (ENFORCED)
As decided in [testing-strategy-unit-vs-integration.md](../decisions/testing-strategy-unit-vs-integration.md):

### Testing Requirements
1. **Unit Tests**: Fast, focused tests for immediate feedback
2. **Integration Tests**: Comprehensive validation with all dependencies
3. **Contract Tests**: API behavior and backward compatibility
4. **No Simplification Without Approval**: NEVER simplify tests without persona discussion and user approval

### Approval Requirements (CRITICAL)
⚠️ **MANDATORY**: The following actions require explicit user approval:
- Simplifying any testing approach
- Skipping integration tests in favor of unit tests only
- Removing or reducing test coverage
- Changing established testing patterns
- Making any architectural decisions that affect testing

### Testing Decision Process
1. **Identify Issue**: Problem with current testing approach
2. **Persona Discussion**: All relevant personas discuss pros/cons
3. **Document Decision**: Create decision document with all perspectives
4. **Wait for Approval**: DO NOT proceed without explicit user confirmation
5. **Implement**: Only after approval is received

### 5-Layer Testing Architecture
```
Layer 1: Unit Tests (Immediate feedback)
Layer 2: Integration Tests (Component boundaries)
Layer 3: Contract Tests (API contracts)
Layer 4: End-to-End Tests (User workflows)
Layer 5: Chaos Tests (Failure scenarios)
```

### Test Coverage Requirements
- Critical Fixes (C1-C3): 100% coverage required
- High Priority (H1-H3): 90% coverage required
- New Features: 80% coverage required
- Bug Fixes: Must include regression tests

## TESTING STRATEGY (ORCHESTRATED)

### Backend Testing (Sarah's Domain)
```bash
# Unit Tests - Business Logic Validation
python -m pytest backend/test_cache_manager.py -v
python -m pytest backend/test_websocket_manager.py -v
python -m pytest backend/test_orchestrator.py -v

# Integration Tests - System Boundaries
python -m pytest backend/test_database_integration.py -v
python -m pytest backend/test_api_endpoints.py -v

# Performance Tests - Resource Limits
python -m pytest backend/test_cache_performance.py -v
python -m pytest backend/test_websocket_load.py -v
```

### Frontend Testing (Alex's Domain)
```bash
# Unit Tests - Component Logic
ng test --watch=false --browsers=ChromeHeadless

# Integration Tests - Service Communication  
ng e2e

# Memory Leak Tests - Resource Cleanup
npm run test:memory-leaks

# IPC Tests - Electron Communication
npm run test:ipc-boundaries
```

### Cross-Integration Testing (Both Architects)
```bash
# End-to-End System Tests
npm run test:e2e:full-system

# Failure Mode Tests
npm run test:failure-scenarios

# Performance Integration Tests  
npm run test:performance:integrated
```

## Testing Coverage Requirements

### Minimum Test Coverage Standards
- **Backend**: 85% line coverage, 90% for critical modules
- **Frontend**: 80% line coverage, 85% for services
- **Integration**: 100% coverage of cross-system boundaries
- **Failure Scenarios**: All identified failure modes must have tests

### Required Test Categories
```bash
# Backend (Sarah's Domain)
python -m pytest tests/ --cov=. --cov-fail-under=85
python -m pytest tests/integration/ -v  
python -m pytest tests/test_failure_modes.py -v

# Frontend (Alex's Domain)
ng test --watch=false --code-coverage
ng e2e --suite=critical-path
npm run test:memory-leaks

# Cross-System (Both Architects)
npm run test:electron-backend-coordination
npm run test:websocket-integration
npm run test:failure-cascades
```

## Testing Commands

### Frontend Testing (Alex's Domain)
```bash
cd ai-assistant
npm test                              # Run all tests
npm test -- --testPathPattern=ipc     # Run specific test file pattern
npm test -- --testNamePattern="should handle"  # Run specific test by name
npm test -- --coverage                # Generate coverage report
npm test -- --passWithNoTests         # Run even if no tests found
```

### Backend Testing (Sarah's Domain)  
```bash
cd ai-assistant/backend
python -m pytest                      # Run all backend tests
python -m pytest -v                   # Verbose output
python -m pytest --cov=.              # With coverage
python -m pytest -k "test_cache"      # Run specific tests
```

### Integration Testing
```bash
npm run test:integration              # Cross-system tests
```

## Discovered Patterns & Mandatory Rules

### Architectural Patterns (Both Architects Validated)

#### Pattern 1: Consistent Error Handling
**Problem**: Mixed throw/null returns make service unpredictable  
**Solution**: Services must EITHER always throw OR always return null, never both  
**Implementation**:
```typescript
// CORRECT: Consistent throwing pattern
if (!fallbackValue) throw error;
return fallbackValue;

// WRONG: Mixed behavior
if (!fallbackValue) return null;  // Sometimes null
if (circuitOpen) throw error;     // Sometimes throw
```
**Enforced By**: Both architects in code review

#### Pattern 2: Mock-Service Contract Alignment
**Problem**: Service expects channel methods, mock provides invoke pattern  
**Solution**: Services must support both patterns for compatibility  
**Implementation**:
```typescript
// Support both patterns
if (typeof electronAPI.invoke === 'function') {
  return electronAPI.invoke(channel, data);
} else if (typeof electronAPI[channel] === 'function') {
  return electronAPI[channel](data);
}
```
**Enforced By**: Alex (frontend integration)

#### Pattern 3: Test Environment Consistency
**Problem**: window vs global.window inconsistency in Jest  
**Solution**: Always set both in test setup  
**Implementation**:
```typescript
// In test setup files
(global as any).window = windowMock;
if (typeof window !== 'undefined') {
  Object.assign(window, windowMock);
}
```
**Enforced By**: Sarah (test infrastructure)

### Business Rules (Updated from Testing Discoveries)

1. **Test-Driven Validation**: All fix claims must be validated by passing tests
2. **No Silent Failures**: Services must either succeed, use fallback, or throw - never silently fail
3. **Backward Compatibility**: New mocks must maintain compatibility with existing tests
4. **Cross-Domain Impact**: Frontend changes must consider backend timing, backend changes must consider frontend UX

### Coding Rules (Enforced in Review)

#### Frontend Rules (Alex's Domain)
- All IPC calls must be wrapped in error boundaries
- Component services must handle cleanup in ngOnDestroy
- Mock compatibility must be tested for both invoke and channel patterns
- Window globals must be set consistently in tests

#### Backend Rules (Sarah's Domain)
- Circuit breakers must have consistent open/closed behavior
- Resource limits must be enforced with clear error messages
- Timeout values must account for maintenance windows
- All async operations must have proper cleanup

### Testing Rules (Mandatory)

1. **Test Independence**: Each test must control its own environment
2. **Error Expectations**: Tests must validate specific error types, not just "any error"
3. **Mock State Reset**: Always reset mock state between tests
4. **Dependency Injection**: Use TestBed.inject, not direct instantiation

## Definition of "Done" for Fixes

A fix is only considered DONE when ALL of the following are met:

### Code Complete
- [ ] Implementation matches fix specification
- [ ] Error handling follows consistent patterns
- [ ] Resource cleanup verified
- [ ] No magic numbers or hardcoded values

### Testing Complete
- [ ] Unit tests pass with >90% coverage of fix
- [ ] Integration tests validate cross-system behavior
- [ ] Edge cases explicitly tested
- [ ] Performance benchmarks met

### Review Complete
- [ ] Alex approved (frontend/integration aspects)
- [ ] Sarah approved (backend/system aspects)
- [ ] No outstanding review comments
- [ ] Patterns documented if new ones discovered

### Validation Complete
- [ ] Manual testing in development environment
- [ ] No memory leaks detected
- [ ] No performance regressions
- [ ] Monitoring/logging adequate

**Enforcement**: No fix moves from "Partial" to "Complete" without all checkboxes checked.