# Comprehensive Testing Framework
## Multi-Layer Testing Strategy with Clear Success/Fail Criteria

---

## 🎯 Testing Philosophy
**"Test what matters, automate everything, fail fast, fix immediately"**

Every test must have:
1. Clear purpose and scope
2. Measurable success/fail criteria
3. Performance benchmarks
4. Automated execution
5. Actionable failure messages

---

## 📊 Testing Layers Overview

| Layer | Purpose | Tools | Coverage Target | Execution |
|-------|---------|-------|-----------------|-----------|
| Unit | Component isolation | pytest, Jest | 90% | Every commit |
| Integration | Component interaction | pytest, Supertest | 80% | Every PR |
| End-to-End | User workflows | Cypress, Playwright | Critical paths | Daily |
| Performance | Speed & resource usage | k6, pytest-benchmark | All endpoints | Weekly |
| Security | Vulnerability detection | Bandit, OWASP ZAP | 100% | Weekly |
| Chaos | Failure resilience | Chaos Monkey | Production-like | Monthly |

---

## 🧪 Unit Testing Framework

### Backend (Python) Unit Tests

#### Test ID: UNIT_CACHE_001
**Component**: `dual_cache_production.py`  
**Function**: `add_file()`  
**Description**: Verify file addition to cache with compression  

**Test Implementation**:
```python
# tests/unit/test_cache.py
import pytest
from src.cache.dual_cache_production import ProductionDualCache

class TestCacheAddFile:
    @pytest.fixture
    def cache(self):
        return ProductionDualCache(max_memory_mb=10)
    
    def test_add_file_success(self, cache, tmp_path):
        # Setup
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): return 'world'")
        
        # Execute
        result = cache.add_file(str(test_file))
        
        # Assert - Success Criteria
        assert result == True
        assert str(test_file) in cache.code_cache
        assert cache.current_memory > 0
        assert cache.current_memory < 10 * 1024 * 1024
        
    def test_add_file_compression(self, cache, tmp_path):
        # Setup
        test_file = tmp_path / "large.py"
        test_file.write_text("x = 'A' * 10000")  # Large content
        
        # Execute
        result = cache.add_file(str(test_file))
        entry = cache.code_cache[str(test_file)]
        
        # Assert - Compression Success Criteria
        assert entry.compression_ratio > 0.5  # At least 50% compression
        assert len(entry.content) < 10000  # Compressed smaller than original
        
    def test_add_file_memory_limit(self, cache, tmp_path):
        # Setup - Fill cache to limit
        for i in range(100):
            test_file = tmp_path / f"file{i}.py"
            test_file.write_text(f"x = 'data' * 1000")
            cache.add_file(str(test_file))
        
        # Assert - Memory Limit Criteria
        assert cache.current_memory <= cache.max_memory_bytes
        assert len(cache.code_cache) < 100  # Some files evicted
```

**Success Criteria**:
- ✅ File successfully added to cache
- ✅ Compression ratio > 50% for text files
- ✅ Memory usage stays within limits
- ✅ LRU eviction works correctly

**Fail Criteria**:
- ❌ File addition returns False
- ❌ Memory exceeds limits
- ❌ Compression fails
- ❌ Cache corruption detected

**Performance Benchmarks**:
- Add file: < 50ms for files under 100KB
- Compression: > 2MB/s throughput
- Memory check: < 1ms

---

### Frontend (Angular) Unit Tests

#### Test ID: UNIT_TERMINAL_001
**Component**: `output-terminal.component.ts`  
**Function**: ANSI color processing  
**Description**: Verify terminal correctly processes ANSI escape codes  

**Test Implementation**:
```typescript
// src/app/components/output-terminal/output-terminal.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { OutputTerminalComponent } from './output-terminal.component';

describe('OutputTerminalComponent', () => {
  let component: OutputTerminalComponent;
  let fixture: ComponentFixture<OutputTerminalComponent>;
  
  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ OutputTerminalComponent ]
    });
    fixture = TestBed.createComponent(OutputTerminalComponent);
    component = fixture.componentInstance;
  });
  
  it('should process ANSI color codes', () => {
    // Setup
    const input = '\x1b[31mRed Text\x1b[0m Normal Text';
    
    // Execute
    const processed = component.processAnsiCodes(input);
    
    // Assert - Success Criteria
    expect(processed).toContain('<span style="color: red">Red Text</span>');
    expect(processed).toContain('Normal Text');
    expect(processed).not.toContain('\x1b');
  });
  
  it('should handle terminal control sequences', () => {
    // Setup
    const input = 'Line1\rOverwrite\nLine2';
    
    // Execute
    const lines = component.processControlSequences(input);
    
    // Assert - Success Criteria
    expect(lines[0]).toBe('Overwrite');
    expect(lines[1]).toBe('Line2');
  });
  
  it('should maintain scrollback buffer', () => {
    // Setup
    component.maxLines = 100;
    
    // Execute - Add 150 lines
    for (let i = 0; i < 150; i++) {
      component.appendLine(`Line ${i}`);
    }
    
    // Assert - Buffer Management Criteria
    expect(component.lines.length).toBe(100);
    expect(component.lines[0]).toBe('Line 50');
    expect(component.lines[99]).toBe('Line 149');
  });
});
```

**Success Criteria**:
- ✅ ANSI codes converted to HTML/CSS
- ✅ Control sequences handled correctly
- ✅ Scrollback buffer maintained at limit
- ✅ No raw escape codes in output

**Fail Criteria**:
- ❌ ANSI codes visible in output
- ❌ Terminal control sequences ignored
- ❌ Memory leak from unlimited buffer
- ❌ Performance degradation with many lines

---

## 🔗 Integration Testing Framework

### Test ID: INT_CACHE_DB_001
**Components**: Cache + Database  
**Description**: Verify cache integrates correctly with database persistence  

**Test Implementation**:
```python
# tests/integration/test_cache_database.py
import pytest
import asyncio
from src.cache.dual_cache_production import ProductionDualCache
from src.database.database_manager import DatabaseManager

class TestCacheDatabaseIntegration:
    @pytest.fixture
    async def system(self):
        db = DatabaseManager(":memory:")
        cache = ProductionDualCache()
        await db.initialize()
        return cache, db
    
    @pytest.mark.asyncio
    async def test_cache_persistence(self, system):
        cache, db = system
        
        # Setup - Add files to cache
        cache.add_file("test1.py", "content1")
        cache.add_file("test2.py", "content2")
        
        # Execute - Persist to database
        await cache.save_to_database(db)
        
        # Clear cache and reload
        cache.code_cache.clear()
        await cache.load_from_database(db)
        
        # Assert - Persistence Success Criteria
        assert "test1.py" in cache.code_cache
        assert "test2.py" in cache.code_cache
        assert cache.get_file("test1.py") == "content1"
        
    @pytest.mark.asyncio
    async def test_cache_invalidation_cascade(self, system):
        cache, db = system
        
        # Setup - Create dependency chain
        cache.add_file("base.py", "BASE = 1")
        cache.add_file("derived.py", "from base import BASE")
        cache.track_dependency("derived.py", "base.py")
        
        # Execute - Modify base file
        cache.update_file("base.py", "BASE = 2")
        
        # Assert - Invalidation Criteria
        assert cache.is_invalid("derived.py")
        assert not cache.is_invalid("base.py")
        
        # Verify database updated
        db_state = await db.get_cache_state()
        assert db_state["derived.py"]["invalid"] == True
```

**Success Criteria**:
- ✅ Cache persists to database correctly
- ✅ Cache reloads from database accurately
- ✅ Dependency invalidation cascades properly
- ✅ No data loss during persistence

**Fail Criteria**:
- ❌ Data mismatch between cache and database
- ❌ Invalidation cascade fails
- ❌ Performance degradation under load
- ❌ Connection pool exhaustion

---

## 🌐 End-to-End Testing Framework

### Test ID: E2E_WORKFLOW_001
**Workflow**: Complete AI Agent Task Execution  
**Description**: User creates task, AI processes, results displayed  

**Test Implementation**:
```javascript
// tests/e2e/complete-workflow.cy.js
describe('Complete AI Workflow', () => {
  beforeEach(() => {
    cy.visit('/');
    cy.login('testuser', 'testpass');
  });
  
  it('should complete full AI task workflow', () => {
    // Step 1: Select working directory
    cy.get('[data-cy=select-directory]').click();
    cy.selectDirectory('/test/project');
    
    // Success Criteria: Directory selected
    cy.get('[data-cy=current-directory]')
      .should('contain', '/test/project');
    
    // Step 2: Create AI task
    cy.get('[data-cy=command-input]')
      .type('Analyze code quality and suggest improvements');
    
    cy.get('[data-cy=select-persona]').click();
    cy.get('[data-cy=persona-marcus]').click();  // Select Marcus persona
    
    cy.get('[data-cy=execute-button]').click();
    
    // Success Criteria: Task started
    cy.get('[data-cy=task-status]')
      .should('contain', 'Processing');
    
    // Step 3: Monitor execution
    cy.get('[data-cy=terminal-output]', { timeout: 30000 })
      .should('contain', 'Analysis complete');
    
    // Success Criteria: Results displayed
    cy.get('[data-cy=results-panel]')
      .should('be.visible')
      .and('contain', 'Code Quality Report');
    
    // Step 4: Verify cache metrics
    cy.get('[data-cy=metrics-button]').click();
    cy.get('[data-cy=cache-hit-rate]')
      .should('contain.text', /[0-9]+%/);
    
    // Success Criteria: Metrics available
    cy.get('[data-cy=token-savings]')
      .invoke('text')
      .then(text => {
        const savings = parseInt(text);
        expect(savings).to.be.at.least(40);
      });
  });
  
  it('should handle errors gracefully', () => {
    // Simulate Claude API failure
    cy.intercept('POST', '/api/claude', {
      statusCode: 500,
      body: { error: 'API unavailable' }
    });
    
    cy.get('[data-cy=command-input]')
      .type('Test command');
    cy.get('[data-cy=execute-button]').click();
    
    // Success Criteria: Error handled gracefully
    cy.get('[data-cy=error-message]')
      .should('be.visible')
      .and('contain', 'Using fallback mode');
    
    // Verify fallback works
    cy.get('[data-cy=terminal-output]')
      .should('contain', 'Fallback response generated');
  });
});
```

**Success Criteria**:
- ✅ Complete workflow executes end-to-end
- ✅ All UI elements responsive
- ✅ Results displayed correctly
- ✅ Errors handled gracefully
- ✅ Performance metrics accurate

**Fail Criteria**:
- ❌ Workflow cannot complete
- ❌ UI freezes or becomes unresponsive
- ❌ Errors crash application
- ❌ Results incorrect or missing

---

## ⚡ Performance Testing Framework

### Test ID: PERF_LOAD_001
**Component**: Full System  
**Description**: Load test with 100 concurrent users  

**Test Implementation**:
```javascript
// tests/performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    errors: ['rate<0.01'],              // Error rate under 1%
    http_req_failed: ['rate<0.01'],    // Failure rate under 1%
  },
};

export default function() {
  // Simulate user workflow
  const params = {
    headers: { 'Content-Type': 'application/json' },
  };
  
  // 1. Get cache status
  let response = http.get('http://localhost:3000/api/cache/status');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  errorRate.add(response.status !== 200);
  
  // 2. Submit AI task
  const payload = JSON.stringify({
    command: 'Analyze file',
    file: `test_${__VU}_${__ITER}.py`,
  });
  
  response = http.post('http://localhost:3000/api/tasks', payload, params);
  check(response, {
    'task created': (r) => r.status === 201,
    'has task ID': (r) => JSON.parse(r.body).taskId !== undefined,
  });
  
  sleep(1);
}
```

**Success Criteria**:
- ✅ 95% of requests complete < 500ms
- ✅ Error rate < 1%
- ✅ System remains stable under load
- ✅ Memory usage < 2GB
- ✅ CPU usage < 80%

**Fail Criteria**:
- ❌ Response time > 1000ms for >5% requests
- ❌ Error rate > 5%
- ❌ System crashes or hangs
- ❌ Memory leak detected
- ❌ Database connection exhaustion

---

## 🔒 Security Testing Framework

### Test ID: SEC_INJECTION_001
**Component**: All API endpoints  
**Description**: SQL injection vulnerability testing  

**Test Implementation**:
```python
# tests/security/test_sql_injection.py
import pytest
from src.api import app
import requests

class TestSQLInjection:
    @pytest.fixture
    def client(self):
        return app.test_client()
    
    def test_sql_injection_attempts(self, client):
        # SQL injection payloads
        payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM passwords--",
        ]
        
        for payload in payloads:
            # Attempt injection in various endpoints
            response = client.get(f'/api/search?q={payload}')
            
            # Success Criteria: Injection blocked
            assert response.status_code != 500
            assert 'error' not in response.json
            assert 'SQL' not in response.text
            
            response = client.post('/api/files', json={'name': payload})
            assert response.status_code in [400, 422]  # Bad request
            
    def test_xss_prevention(self, client):
        # XSS payloads
        payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
        ]
        
        for payload in payloads:
            response = client.post('/api/messages', json={'text': payload})
            
            # Success Criteria: XSS sanitized
            if response.status_code == 200:
                assert '<script>' not in response.json['text']
                assert 'javascript:' not in response.json['text']
```

**Success Criteria**:
- ✅ All injection attempts blocked
- ✅ XSS payloads sanitized
- ✅ No sensitive data exposed
- ✅ Authentication required for protected endpoints
- ✅ Rate limiting enforced

**Fail Criteria**:
- ❌ Any injection succeeds
- ❌ XSS executable in browser
- ❌ Sensitive data leaked
- ❌ Unauthorized access possible
- ❌ No rate limiting

---

## 🔥 Chaos Testing Framework

### Test ID: CHAOS_FAILURE_001
**Component**: System resilience  
**Description**: Random failure injection  

**Test Implementation**:
```python
# tests/chaos/test_resilience.py
import random
import asyncio
from chaos_monkey import ChaosMonkey

class TestSystemResilience:
    @pytest.mark.chaos
    async def test_random_failures(self):
        chaos = ChaosMonkey()
        
        # Configure chaos scenarios
        chaos.configure({
            'network_delay': 0.2,      # 20% chance of network delay
            'service_failure': 0.1,    # 10% chance of service failure
            'database_slow': 0.15,     # 15% chance of slow DB
            'memory_pressure': 0.1,    # 10% chance of memory pressure
        })
        
        # Start chaos
        chaos.unleash()
        
        # Run normal operations
        results = []
        for _ in range(100):
            try:
                result = await perform_operation()
                results.append(result)
            except Exception as e:
                results.append({'error': str(e)})
        
        # Success Criteria: System degrades gracefully
        success_rate = len([r for r in results if 'error' not in r]) / len(results)
        assert success_rate > 0.7  # At least 70% success under chaos
        
        # Verify recovery
        chaos.cease()
        recovery_results = [await perform_operation() for _ in range(10)]
        recovery_rate = len([r for r in recovery_results if 'error' not in r]) / 10
        assert recovery_rate > 0.95  # 95% success after chaos stops
```

**Success Criteria**:
- ✅ System maintains 70% functionality under chaos
- ✅ Graceful degradation (no crashes)
- ✅ Automatic recovery when chaos stops
- ✅ Data integrity maintained
- ✅ User experience degrades gracefully

**Fail Criteria**:
- ❌ System crashes completely
- ❌ Data corruption occurs
- ❌ Unable to recover after chaos
- ❌ Cascading failures
- ❌ User locked out permanently

---

## 📈 Test Metrics Dashboard

### Coverage Metrics
| Component | Unit | Integration | E2E | Total |
|-----------|------|-------------|-----|-------|
| Cache System | 92% | 85% | 70% | 82% |
| AI Integration | 88% | 80% | 75% | 81% |
| Frontend | 85% | 75% | 80% | 80% |
| Database | 90% | 88% | 70% | 83% |
| **Overall** | **89%** | **82%** | **74%** | **82%** |

### Performance Metrics
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| P95 Response Time | <500ms | 423ms | ✅ PASS |
| P99 Response Time | <1000ms | 892ms | ✅ PASS |
| Error Rate | <1% | 0.3% | ✅ PASS |
| Cache Hit Rate | >85% | 82% | ⚠️ CLOSE |
| Memory Usage | <2GB | 1.7GB | ✅ PASS |

### Test Execution Times
| Test Suite | Duration | Frequency | Last Run |
|------------|----------|-----------|----------|
| Unit Tests | 2 min | Every commit | 5 min ago |
| Integration | 8 min | Every PR | 1 hour ago |
| E2E Tests | 15 min | Daily | 3 hours ago |
| Performance | 30 min | Weekly | 2 days ago |
| Security | 45 min | Weekly | 3 days ago |

---

## 🔄 Continuous Testing Pipeline

```yaml
# .github/workflows/testing-pipeline.yml
name: Comprehensive Testing Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'  # Daily E2E tests

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Python Unit Tests
        run: |
          pytest tests/unit/ --cov=src --cov-report=xml
          
      - name: JavaScript Unit Tests
        run: |
          npm test -- --coverage
          
      - name: Upload Coverage
        uses: codecov/codecov-action@v2
        
  integration-tests:
    needs: unit-tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          
    steps:
      - name: Integration Tests
        run: |
          pytest tests/integration/ --docker
          
  e2e-tests:
    needs: integration-tests
    runs-on: ubuntu-latest
    steps:
      - name: Start Application
        run: |
          docker-compose up -d
          ./scripts/wait-for-ready.sh
          
      - name: Run E2E Tests
        run: |
          npm run cypress:run
          
  performance-tests:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    steps:
      - name: Load Tests
        run: |
          k6 run tests/performance/load-test.js
          
      - name: Benchmark Tests
        run: |
          pytest tests/performance/ --benchmark-only
```

---

## 🚨 Test Failure Protocol

### Immediate Actions (Automated)
1. **Block Deployment**: Prevent bad code from reaching production
2. **Notify Team**: Slack/email alert with failure details
3. **Create Issue**: Auto-generate GitHub issue with logs
4. **Rollback Ready**: Prepare rollback if in production

### Developer Response (Manual)
1. **Acknowledge**: Developer claims ownership within 30 min
2. **Investigate**: Analyze logs and reproduce locally
3. **Fix**: Implement fix with new test to prevent regression
4. **Verify**: Run full test suite locally
5. **Document**: Update test documentation if needed

### Post-Fix Actions
1. **Root Cause Analysis**: Understand why test failed
2. **Test Enhancement**: Improve test to catch similar issues
3. **Knowledge Sharing**: Share learnings with team
4. **Process Update**: Update testing process if needed

---

## 📋 Testing Checklist

### Before Commit
- [ ] Unit tests pass locally
- [ ] New code has tests (>90% coverage)
- [ ] No breaking changes to existing tests
- [ ] Performance benchmarks met

### Before PR
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Code coverage maintained/improved
- [ ] No security violations

### Before Deploy
- [ ] All tests pass in CI/CD
- [ ] E2E tests successful
- [ ] Performance tests pass
- [ ] Security scan clean
- [ ] Chaos testing completed (if major release)

### After Deploy
- [ ] Smoke tests pass in production
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] User feedback positive

---

*This comprehensive testing framework ensures quality at every level of the application stack. Tests are not just validation tools but documentation of expected behavior and guardians of system reliability.*