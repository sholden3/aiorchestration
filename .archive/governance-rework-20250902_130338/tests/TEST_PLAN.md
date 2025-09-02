# Governance System Test Plan

**Created**: 2025-01-28  
**Phase**: 1.5b Complete - Testing Phase  
**Priority**: CRITICAL

## Test Coverage Requirements

### 1. Unit Tests (Immediate)

#### Hallucination Detection Tests
```python
# governance/tests/test_hallucination_detector.py
- Test pattern detection for each severity level
- Test false positive rate (<10%)
- Test performance (<500ms per file)
- Test file type filtering
- Test configuration loading
```

#### Exemption System Tests
```python
# governance/tests/test_exemptions.py
- Test file-specific exemptions
- Test class-specific exemptions
- Test context-based exemptions
- Test expiration dates
- Test multi-language support
```

#### Session Management Tests
```python
# governance/tests/test_session_manager.py
- Test session lifecycle
- Test architect approvals
- Test task management
- Test timeout handling
- Test persistence/recovery
```

#### TODO Tracker Tests
```python
# governance/tests/test_todo_tracker.py
- Test pattern detection
- Test age calculation
- Test overdue detection
- Test issue creation
- Test format validation
```

### 2. Integration Tests (This Week)

#### Pre-commit Hook Integration
```bash
# Test complete workflow
- Create test commits with various patterns
- Verify dangerous patterns blocked
- Verify exemptions work
- Verify hallucinations detected
- Measure total execution time
```

#### Cross-Component Tests
```python
# governance/tests/integration/test_full_pipeline.py
- SmartRules + Exemptions + Hallucination
- SessionManager + TodoTracker
- All validators together
- Performance under load
```

### 3. Performance Benchmarks (This Week)

#### Target Metrics
- Pre-commit hook: <2 seconds total
- Hallucination detection: <500ms per file
- Pattern matching: <100ms per file
- Exemption lookup: <10ms per check

#### Load Testing
- 100 files simultaneously
- Large files (>1MB)
- Complex nested structures
- Multiple languages

### 4. False Positive Analysis (Next 3 Days)

#### Measurement Process
1. Run on existing codebase
2. Log all detections
3. Manual review of each finding
4. Calculate false positive rate
5. Tune patterns if >10%

## Test Execution Order

### Day 1 (Today)
1. Create unit test files
2. Test hallucination detector
3. Test exemption system
4. Performance baseline

### Day 2
1. Test session management
2. Test TODO tracker
3. Integration tests
4. Pre-commit hook testing

### Day 3
1. False positive analysis
2. Performance optimization
3. Documentation updates
4. Final validation

## Success Criteria

### Phase 1.5b Complete When:
- [ ] All unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Performance targets met (<500ms)
- [ ] False positive rate <10%
- [ ] Pre-commit hook works end-to-end
- [ ] Documentation complete

## Test Commands

```bash
# Run all tests
python -m pytest governance/tests/ -v

# Run with coverage
python -m pytest governance/tests/ --cov=governance --cov-report=html

# Run performance tests
python governance/tests/benchmark_performance.py

# Test pre-commit hook
./governance/scripts/test_pre_commit.sh

# Measure false positives
python governance/tests/analyze_false_positives.py
```

## Risk Mitigation

### If Tests Fail:
1. Disable feature via config flag
2. Revert to previous version
3. Document issue in TECHNICAL_DEBT.md
4. Create fix plan

### If Performance Issues:
1. Reduce pattern count
2. Implement caching
3. Limit file size processing
4. Use multiprocessing

### If High False Positives:
1. Tune confidence thresholds
2. Add more exemptions
3. Refine patterns
4. Consider ML approach (Phase 3.5)