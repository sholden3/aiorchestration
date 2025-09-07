# GitHub Copilot Prompt: Fix Plugin Base Test Timing Issue

## Context
We have a test failure in `tests/unit/governance/plugins/test_plugin_base.py` where the `test_validate_async_mode` test is failing because `duration_ms` is returning 0.0 for very fast operations.

## Current Issue
```python
# Line 351 in test_plugin_base.py
assert result.duration_ms > 0  # FAILS when operation is too fast
```

The assertion fails because on fast systems, the async validation completes in less than 1 millisecond, resulting in duration_ms = 0.0.

## Governance Requirements
Our codebase follows strict governance protocols:
1. **Documentation Standards**: All functions must have proper docstrings
2. **Test Coverage**: Maintain >85% test coverage
3. **No TODOs**: Remove or resolve all TODO comments
4. **Line Length**: Maximum 120 characters per line
5. **Type Hints**: Use type hints for all function parameters and returns
6. **Error Handling**: Comprehensive error handling with proper logging
7. **Thread Safety**: Consider thread safety for shared resources

## Required Fix
Please fix the timing assertion in the `test_validate_async_mode` method by:

1. **Option A - Tolerance Approach**: Change the assertion to accept 0.0 as valid:
   ```python
   assert result.duration_ms >= 0  # Duration can be 0 for very fast operations
   ```

2. **Option B - Mock Approach**: Add a small delay or mock to ensure measurable time:
   ```python
   # Add to TestValidatorPlugin._perform_validation method
   await asyncio.sleep(0.001)  # Ensure measurable duration
   ```

3. **Option C - Precision Approach**: Use higher precision timing:
   ```python
   # Use time.perf_counter_ns() for nanosecond precision
   # Convert to milliseconds with higher precision
   ```

## Additional Fixes Needed

### 1. Fix PytestCollectionWarning (Line 196)
The test class `TestValidatorPlugin` has an `__init__` constructor which pytest doesn't like.
- Rename the class to avoid pytest collection (e.g., `MockValidatorPlugin`)
- OR move it outside the test class
- OR use `@pytest.mark.skip_collection` decorator

### 2. Fix ResourceWarning
Close the file handle in `libs\governance\core\engine.py:54`
- Ensure logging handlers are properly closed
- Use context managers where appropriate

## Expected Implementation

```python
@pytest.mark.asyncio
async def test_validate_async_mode(self):
    """Test validation in async mode with proper timing handling."""
    plugin = TestValidatorPlugin()  # Consider renaming to MockValidatorPlugin
    await plugin.initialize({"validation_mode": "async"})
    
    result = await plugin.validate({"test": "data"})
    
    assert result.success
    assert result.plugin_name == "test-validator"
    assert "Async validation passed" in result.messages
    # Fix: Accept 0.0 as valid for very fast operations
    assert result.duration_ms >= 0, "Duration should be non-negative"
    assert plugin.validation_calls[0][0] == "async"
```

## Test Best Practices
1. **Deterministic Tests**: Tests should not depend on system performance
2. **Clear Assertions**: Add descriptive messages to assertions
3. **Isolation**: Each test should be independent
4. **Mocking**: Mock external dependencies and time-sensitive operations
5. **Coverage**: Ensure edge cases are tested

## Validation Checklist
After making changes, ensure:
- [ ] All tests in test_plugin_base.py pass
- [ ] No new warnings are introduced
- [ ] Test coverage remains >85%
- [ ] All assertions have descriptive failure messages
- [ ] The fix works on both fast and slow systems
- [ ] Documentation is updated if behavior changes

## Run Tests
```bash
# Run the specific test
python -m pytest tests/unit/governance/plugins/test_plugin_base.py::TestBaseValidatorPlugin::test_validate_async_mode -xvs

# Run all plugin tests
python -m pytest tests/unit/governance/plugins/ -xvs

# Check coverage
python -m pytest tests/unit/governance/plugins/ --cov=libs.governance.plugins --cov-report=term-missing
```

## Notes
- The timing issue is common in async tests on fast systems
- Consider using `pytest-benchmark` for performance-related assertions
- The test should validate functionality, not performance
- If performance testing is needed, create separate benchmark tests

Please implement the most appropriate fix that maintains test reliability while following our governance standards.