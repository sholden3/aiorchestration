# Phase 2.5 Execution Prompts - Day 1 Implementation

**Date**: 2025-01-27  
**Phase**: 2.5 - Test Implementation & Framework Validation  
**Governance**: Dynamic Persona Orchestration Framework v2.2  
**Session Validators**: Alex Novak v3.0 & Dr. Sarah Chen v1.2  

---

## 🎯 MASTER PROMPT FOR ORCHESTRATED IMPLEMENTATION

```
[ORCHESTRATED IMPLEMENTATION REQUEST - PHASE 2.5 DAY 1]

Session Initialization:
- Core Architects: Alex Novak v3.0 & Dr. Sarah Chen v1.2
- Specialist Pool: Sam Martinez v3.2.0, Riley Thompson v1.1, Quinn Roberts v1.1, Dr. Avery Chen v1.0
- Governance Framework: Active with full validation
- Decision Tracking: DECISIONS.md ready for updates
- Assumption Log: assumption-discovery-log.md ready for discoveries

Primary Objectives for Day 1:
1. Setup CI/CD pipeline with GitHub Actions (Riley Thompson lead)
2. Implement cache manager unit tests with circuit breaker (Sam Martinez & Sarah Chen)
3. Fix terminal service memory leak C1 (Alex Novak)
4. Apply documentation standards to all new code (Quinn Roberts)
5. Map hook integration points as discovered (Dr. Avery Chen)

Requirements:
- Document EVERY assumption that proves incorrect
- Mark ALL hook integration points with comments
- Apply comprehensive documentation headers to ALL files
- Track test coverage metrics continuously
- Update assumption-discovery-log.md in real-time

Success Criteria:
- CI/CD pipeline runs successfully
- At least 2 critical services have unit tests
- Memory leak C1 fixed and tested
- All code meets documentation standards
- Assumption log has at least 3 entries

Validation Gates:
- Sarah's Three Questions applied to all implementations
- Alex's 3 AM Test for all critical paths
- Sam's observability markers in all tests
- Quinn's documentation score >90
- Avery's hook points clearly marked
```

---

## 👤 INDIVIDUAL PERSONA EXECUTION PROMPTS

### 🔧 Riley Thompson v1.1 - CI/CD Pipeline Lead

```
[SPECIALIST INVOCATION - RILEY THOMPSON v1.1]

Task: Implement GitHub Actions CI/CD Pipeline for Phase 2.5

Context:
- Project has ZERO automated testing currently
- Need quality gates to prevent regression
- Must enforce documentation standards
- Should run on every commit and PR

Specific Requirements:
1. Create .github/workflows/ci.yml with:
   - Frontend testing with Jest (npm test)
   - Backend testing with pytest
   - Coverage reporting for both
   - Documentation validation (validate-code-documentation.sh)
   - Specialist decision validation (validate-specialist-decisions.sh)
   - Security scanning (npm audit, pip-audit)

2. Setup build matrix:
   - Node.js 18+ for frontend
   - Python 3.10+ for backend
   - Ubuntu latest for runner

3. Add quality gates:
   - Frontend coverage must be >40% (initial, target 80%)
   - Backend coverage must be >40% (initial, target 80%)
   - Documentation score must be >90
   - No high/critical security vulnerabilities

4. Create status badges for README

Deliverables:
- [ ] Working GitHub Actions workflow file
- [ ] Successful pipeline run
- [ ] Coverage reports generated
- [ ] Status badges in README
- [ ] Document any discovered assumptions

Hook Points to Mark:
- Pre-test validation hooks
- Coverage threshold enforcement
- Security scan integration
- Documentation validation

Remember: "Infrastructure should exist before planning castles on it"
```

### 🧪 Sam Martinez v3.2.0 - Testing Implementation Lead

```
[SPECIALIST INVOCATION - SAM MARTINEZ v3.2.0]

Task: Implement Unit Tests for Critical Services

Context:
- Current test coverage: 0% (UNACCEPTABLE!)
- Need foundation for 5-layer testing architecture
- Focus on Layer 1 (Unit Tests) today
- Must include observability from the start

Specific Requirements:
1. Backend - Cache Manager Tests (backend/tests/test_cache_manager.py):
   - Test two-tier cache operations
   - Validate circuit breaker triggers at 3 failures
   - Test cache eviction policies
   - Verify TTL enforcement
   - Test concurrent access patterns
   - Include performance baselines

2. Frontend - IPC Service Tests (src/app/services/ipc.service.spec.ts):
   - Test channel whitelisting
   - Validate error boundaries
   - Test retry logic
   - Verify security patterns
   - Test message queuing
   - Include memory leak detection

Test Pattern to Follow:
```python
@pytest.mark.unit
@pytest.mark.observability
async def test_cache_circuit_breaker_opens_after_failures():
    """
    @specialist Sam Martinez v3.2.0 - 2025-01-27
    @validates Circuit breaker from backend-architecture.md
    @assumption 3 failures in 60 seconds triggers open state
    @hook_point Governance can monitor circuit state changes
    @discovered_assumption [Document what you find]
    """
    # Arrange
    cache = CacheManager()
    observability = TestObservability()
    
    # Act - Force 3 failures
    for _ in range(3):
        with pytest.raises(CacheException):
            await cache.get("force_failure_key")
    
    # Assert
    assert cache.circuit_breaker.state == CircuitState.OPEN
    assert observability.metric("circuit.opened") == 1
    
    # Document assumption discovery
    # ASSUMPTION DISCOVERED: Circuit breaker needs cooldown period
```

Deliverables:
- [ ] Cache manager tests with >80% coverage
- [ ] IPC service tests with >80% coverage  
- [ ] Performance baselines documented
- [ ] All assumptions logged
- [ ] Observability points marked

Remember: "A test that exists beats perfect test documentation every time!"
```

### 🛡️ Dr. Sarah Chen v1.2 - Backend Implementation

```
[SPECIALIST INVOCATION - DR. SARAH CHEN v1.2]

Task: Implement Circuit Breaker and Defensive Patterns

Context:
- Cache manager has no failure protection (C2)
- WebSocket manager has no resource limits (H1)
- Need defensive patterns throughout

Three Questions Framework:
1. What breaks first? Cache disk I/O operations
2. How do we know? Through circuit breaker state monitoring
3. What's Plan B? Fallback to memory-only cache

Specific Requirements:
1. Circuit Breaker Implementation (backend/cache_manager.py):
```python
class CircuitBreaker:
    """
    @specialist Dr. Sarah Chen v1.2 - 2025-01-27
    @implements Defensive pattern per backend-architecture.md
    @assumption 3 failures in 60s = open, 30s cooldown
    @hook_point AI governance monitors state transitions
    """
    def __init__(self):
        self.failure_threshold = 3
        self.timeout_duration = 60  # seconds
        self.cooldown_period = 30   # seconds
        self.failure_times = []
        self.state = CircuitState.CLOSED
        self.last_open_time = None
```

2. Resource Limits (backend/websocket_manager.py):
```python
class WebSocketManager:
    """
    @specialist Dr. Sarah Chen v1.2 - 2025-01-27  
    @fixes H1: WebSocket Resource Exhaustion
    @assumption Max 100 connections, 5 min timeout
    @hook_point Governance enforces connection policies
    """
    MAX_CONNECTIONS = 100
    CONNECTION_TIMEOUT = 300
    
    async def accept_connection(self, websocket):
        if len(self.connections) >= self.MAX_CONNECTIONS:
            await self.reject_with_backpressure(websocket)
            return
```

Deliverables:
- [ ] Circuit breaker fully implemented
- [ ] Resource limits enforced
- [ ] Fallback mechanisms tested
- [ ] Monitoring points added
- [ ] Three Questions answered for each component

Remember: "What breaks first? How do we know? What's Plan B?"
```

### 🔧 Alex Novak v3.0 - Frontend Implementation

```
[SPECIALIST INVOCATION - ALEX NOVAK v3.0]

Task: Fix Memory Leaks and Implement Error Boundaries

Context:
- Terminal service has critical memory leak (C1)
- IPC services missing error boundaries (H2)
- Need 3 AM debugging capability

3 AM Test Requirements:
- Can I debug this at 3 AM without calling anyone?
- Are all integration points documented?
- Is cleanup properly verified?

Specific Requirements:
1. Fix Terminal Service Memory Leak (src/app/services/terminal.service.ts):
```typescript
/**
 * @specialist Alex Novak v3.0 - 2025-01-27
 * @fixes C1: Terminal Service Memory Leak
 * @assumption Listeners must be explicitly cleaned
 * @hook_point Terminal lifecycle monitoring
 */
export class TerminalService implements OnDestroy {
  private listeners: Map<string, Function> = new Map();
  private subscriptions: Subscription[] = [];
  
  ngOnDestroy(): void {
    // Critical: Clean up all listeners
    this.listeners.forEach((listener, event) => {
      this.electronAPI.removeListener(event, listener);
    });
    this.listeners.clear();
    
    // Clean up all subscriptions
    this.subscriptions.forEach(sub => sub.unsubscribe());
    
    // Verify cleanup (3 AM debugging aid)
    console.debug('[TerminalService] Cleanup complete:', {
      listenersCleared: this.listeners.size === 0,
      subscriptionsCleared: this.subscriptions.length === 0
    });
  }
}
```

2. IPC Error Boundaries (src/app/services/ipc.service.ts):
```typescript
/**
 * @specialist Alex Novak v3.0 - 2025-01-27
 * @fixes H2: IPC Error Boundaries
 * @assumption All IPC calls need defensive handling
 * @hook_point Governance validates IPC operations
 */
async safeInvoke<T>(channel: string, data?: any): Promise<T | null> {
  const correlationId = this.generateCorrelationId();
  
  try {
    // Validate channel against whitelist
    if (!this.isChannelWhitelisted(channel)) {
      throw new SecurityError(`Channel not whitelisted: ${channel}`);
    }
    
    // Add timeout wrapper
    return await this.withTimeout(
      this.electronAPI.invoke(channel, { ...data, correlationId }),
      5000,
      `IPC timeout: ${channel}`
    );
  } catch (error) {
    this.logError(error, channel, correlationId);
    
    // Graceful degradation
    return this.getFallbackResponse<T>(channel);
  }
}
```

Deliverables:
- [ ] Memory leak C1 fixed and tested
- [ ] Error boundaries implemented
- [ ] 3 AM debugging aids added
- [ ] Integration points documented
- [ ] Cleanup verification in place

Remember: "If I get paged at 3 AM, do I have enough info to fix it?"
```

### 📋 Quinn Roberts v1.1 - Documentation Standards

```
[SPECIALIST INVOCATION - QUINN ROBERTS v1.1]

Task: Apply Documentation Standards to All Code

Context:
- Code being written today needs comprehensive documentation
- Must track assumptions as they're discovered
- Documentation must serve the code

Documentation Requirements for EVERY file:
```typescript
/**
 * @fileoverview [Concise description - what and why]
 * @author [Specialist Name] v[Version] - [Date]
 * @architecture [Component: Frontend/Backend/Integration]
 * @references [Architecture docs this implements]
 * @fixes [Issue numbers being addressed]
 * @testing_strategy [How this should be tested]
 * @governance [Which framework applies]
 * @assumptions
 *   - [List each assumption made]
 *   - [Will be updated as discovered wrong]
 * @hook_points
 *   - [Where governance can intercept]
 *   - [Where monitoring can observe]
 * @discovered_issues
 *   - [Track what we found during implementation]
 */
```

Validation Checklist:
- [ ] Every file has complete header
- [ ] Every class has documentation
- [ ] Every public method has JSDoc/docstring
- [ ] Every assumption is marked
- [ ] Every hook point is identified
- [ ] Business logic has inline comments

Assumption Tracking:
- Update assumption-discovery-log.md immediately
- Mark code where assumption was discovered
- Link assumption to affected components
- Note governance impact

Deliverables:
- [ ] All Day 1 code meets standards
- [ ] Documentation score >90 on all files
- [ ] Assumption log updated continuously
- [ ] Weekly report on documentation compliance

Remember: "Documentation must serve code, not the other way around"
```

### 🤖 Dr. Avery Chen v1.0 - Hook Integration Mapping

```
[SPECIALIST INVOCATION - DR. AVERY CHEN v1.0]

Task: Map AI Governance Hook Points

Context:
- AI remains mocked but hooks must be identified
- Every integration point needs governance capability
- Prepare for Phase 3 AI integration

Hook Point Categories to Identify:
1. **Pre-execution Validation**
   - Token limit checking
   - Cost estimation
   - Rate limiting
   - Input sanitization

2. **Execution Monitoring**
   - Performance tracking
   - Resource usage
   - Error rates
   - Timeout management

3. **Post-execution Processing**
   - Output validation
   - Cost recording
   - Audit logging
   - Cleanup verification

Marking Pattern:
```typescript
/**
 * @hook_point CACHE_OPERATION
 * @governance_gate PRE_OPERATION_VALIDATION
 * @specialist Dr. Avery Chen v1.0
 * @monitors Performance, cost, resource usage
 * @validates Input size, rate limits, permissions
 */
async cacheGet(key: string): Promise<any> {
  // HOOK: Pre-operation validation
  const validation = await this.governanceGate?.validateCacheOperation({
    operation: 'GET',
    key,
    estimatedCost: 0.001
  });
  
  // HOOK: Operation monitoring
  const monitor = this.governanceGate?.startMonitoring('cache.get');
  
  try {
    const result = await this.cache.get(key);
    
    // HOOK: Result validation
    await this.governanceGate?.validateResult(result);
    
    return result;
  } finally {
    // HOOK: Cleanup and metrics
    monitor?.complete();
  }
}
```

Deliverables:
- [ ] Hook points mapped in all new code
- [ ] Governance integration plan updated
- [ ] Mock governance interfaces defined
- [ ] Hook testing strategy documented
- [ ] Integration readiness checklist

Remember: "Mock boundaries first, real AI after governance proven"
```

---

## 🚀 EXECUTION SEQUENCE FOR DAY 1

### Morning (First 4 Hours)
1. **Riley**: Create and test CI/CD pipeline
2. **Sam & Sarah**: Begin cache manager tests with circuit breaker
3. **Alex**: Start terminal service memory leak fix
4. **Quinn**: Review and apply documentation standards
5. **Avery**: Define hook point marking standards

### Afternoon (Next 4 Hours)
1. **Riley**: Ensure pipeline runs successfully, add badges
2. **Sam & Alex**: Begin IPC service tests with error boundaries
3. **Sarah**: Complete circuit breaker, start WebSocket limits
4. **Quinn**: Update assumption log with discoveries
5. **Avery**: Map hooks in implemented components

### End of Day Validation
```bash
# Run validation scripts
./validate-code-documentation.sh
./validate-specialist-decisions.sh

# Check coverage
npm run test:coverage
python -m pytest --cov

# Update assumption log
echo "Day 1 Discoveries:" >> assumption-discovery-log.md

# Verify CI/CD pipeline
git push origin feature/phase-2.5-day-1

# Review with architects
echo "Sarah: Do the Three Questions pass?"
echo "Alex: Does this pass the 3 AM test?"
```

---

## 📊 SUCCESS METRICS FOR DAY 1

### Must Achieve:
- [ ] CI/CD pipeline operational
- [ ] 2+ critical services have unit tests
- [ ] Memory leak C1 fixed
- [ ] Circuit breaker implemented
- [ ] 3+ assumptions documented
- [ ] All code has documentation headers

### Stretch Goals:
- [ ] Coverage >20% overall
- [ ] All H1-H3 issues addressed
- [ ] Performance baselines established
- [ ] Hook integration plan complete

---

## 🔄 CONTINUOUS VALIDATION

Throughout the day, continuously ask:
1. What assumptions are we discovering?
2. Where should governance hooks go?
3. What framework documentation needs updating?
4. Are we building the right foundation for Phase 3?

---

**Remember**: We're not just writing tests - we're validating our entire architectural framework through implementation. Every line of code is a test of our documentation's accuracy.

*"We can wax poetic all day long, but without actual implementation, we may have introduced an error in our logic."* - User Insight