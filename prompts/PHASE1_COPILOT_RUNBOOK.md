# Phase 1: GitHub Copilot Implementation Runbook

## Overview
This runbook guides you through using GitHub Copilot to implement the Phase 1 validator plugin architecture. Each file has been pre-created with a detailed prompt at the top.

## Prerequisites
- [ ] GitHub Copilot is installed and active
- [ ] You're in the project root directory
- [ ] Python 3.10+ environment is active
- [ ] Required packages installed: `pip install pyyaml jsonschema watchdog msgpack pytest pytest-cov pytest-asyncio`

## Implementation Order and Steps

### Step 1: IValidatorPlugin Base Interface (base.py)
**File:** `libs/governance/plugins/base.py`

1. Open the file in your IDE
2. The prompt is already at the top of the file
3. Place cursor after the TODO comment
4. Start typing: `from abc import ABC, abstractmethod`
5. Let Copilot generate the implementation
6. Review the generated code for:
   - [ ] All required dataclasses (PluginMetadata, PluginHealth, ValidationResult)
   - [ ] Both enums (PluginState, ValidationMode)
   - [ ] IValidatorPlugin abstract class with all methods
   - [ ] Proper type hints throughout
   - [ ] Logging setup
7. Save the file

**Validation Checklist:**
- [ ] Abstract methods defined with @abstractmethod
- [ ] All dataclasses use @dataclass decorator
- [ ] Type hints for all parameters and returns
- [ ] Docstrings for all public methods
- [ ] No hardcoded values

### Step 2: Plugin Registry (registry.py)
**File:** `libs/governance/plugins/registry.py`

1. Open the file in your IDE
2. The prompt is already at the top
3. Place cursor after the TODO comment
4. Start typing: `import threading`
5. Then type: `class PluginRegistry:`
6. Let Copilot complete the singleton implementation
7. Review for:
   - [ ] Singleton pattern correctly implemented
   - [ ] Thread-safe with locks
   - [ ] Dynamic import using importlib
   - [ ] Dependency resolution logic
   - [ ] Version compatibility checking

**Validation Checklist:**
- [ ] _instance class variable for singleton
- [ ] __new__ method for singleton pattern
- [ ] threading.Lock() used for thread safety
- [ ] importlib.import_module for dynamic loading
- [ ] Proper error handling for imports

### Step 3: Lifecycle Manager (lifecycle.py)
**File:** `libs/governance/plugins/lifecycle.py`

1. Open the file
2. Place cursor after the TODO comment
3. Start typing: `from enum import Enum`
4. Then: `class PluginLifecycleManager:`
5. Let Copilot generate the state machine
6. Review for:
   - [ ] State transition validation
   - [ ] Health monitoring setup
   - [ ] Auto-restart with backoff
   - [ ] Event emission system
   - [ ] Resource cleanup

**Validation Checklist:**
- [ ] State machine rules enforced
- [ ] Asyncio tasks for health monitoring
- [ ] Exponential backoff implemented
- [ ] Event handlers support
- [ ] Proper cleanup in teardown

### Step 4: Configuration Loader (config.py)
**File:** `libs/governance/plugins/config.py`

1. Open the file
2. Place cursor after the TODO comment
3. Start typing: `import yaml`
4. Then: `class ConfigurationLoader:`
5. Let Copilot implement the loader
6. Review for:
   - [ ] YAML and JSON support
   - [ ] Schema validation with jsonschema
   - [ ] Environment variable loading
   - [ ] Hot-reload with watchdog
   - [ ] Config merging logic

**Validation Checklist:**
- [ ] File format detection
- [ ] jsonschema validation
- [ ] watchdog Observer for file monitoring
- [ ] Proper merge strategy
- [ ] Encryption placeholder

### Step 5: Message Bus (messaging.py)
**File:** `libs/governance/plugins/messaging.py`

1. Open the file
2. Place cursor after the TODO comment
3. Start typing: `import asyncio`
4. Then: `@dataclass` for Message class
5. Then: `class PluginMessageBus:`
6. Let Copilot complete the implementation
7. Review for:
   - [ ] Pub/sub implementation
   - [ ] Request/response pattern
   - [ ] Priority queue usage
   - [ ] Circuit breaker logic
   - [ ] Message serialization

**Validation Checklist:**
- [ ] asyncio.Queue for message queuing
- [ ] Priority handling (heapq or similar)
- [ ] Circuit breaker state machine
- [ ] MessagePack serialization
- [ ] Dead letter queue

## Testing Phase

### Step 6: Create Test Structure
```bash
mkdir -p tests/unit/governance/plugins
```

### Step 7: Create Test Files
For each component, create a test file:

1. **test_base.py**
   ```python
   """Test IValidatorPlugin base interface"""
   import pytest
   from libs.governance.plugins.base import IValidatorPlugin
   # Let Copilot generate tests
   ```

2. **test_registry.py**
   ```python
   """Test PluginRegistry singleton"""
   import pytest
   from libs.governance.plugins.registry import PluginRegistry
   # Let Copilot generate tests
   ```

3. **test_lifecycle.py**
   ```python
   """Test PluginLifecycleManager"""
   import pytest
   from libs.governance.plugins.lifecycle import PluginLifecycleManager
   # Let Copilot generate tests
   ```

4. **test_config.py**
   ```python
   """Test ConfigurationLoader"""
   import pytest
   from libs.governance.plugins.config import ConfigurationLoader
   # Let Copilot generate tests
   ```

5. **test_messaging.py**
   ```python
   """Test PluginMessageBus"""
   import pytest
   from libs.governance.plugins.messaging import PluginMessageBus
   # Let Copilot generate tests
   ```

### Step 8: Run Tests
```bash
# Run all plugin tests
pytest tests/unit/governance/plugins/ -xvs

# Check coverage
pytest tests/unit/governance/plugins/ --cov=libs/governance/plugins --cov-report=term-missing

# Coverage should be >85%
```

## Configuration Files

### Step 9: Create Config Files

1. **config/governance/validators.yaml**
   ```yaml
   # Let Copilot generate based on the template in MASTER_RUN file
   ```

2. **config/governance/plugin_registry.yaml**
   ```yaml
   # Let Copilot generate the registry configuration
   ```

## Validation Checklist

### Final Review Before Completion
- [ ] All 5 components implemented
- [ ] All tests written and passing
- [ ] Coverage >85% achieved
- [ ] No hardcoded values
- [ ] All methods documented
- [ ] Type hints everywhere
- [ ] Config files created
- [ ] No import errors
- [ ] Thread-safe where needed
- [ ] Async support working

## Common Issues and Solutions

### Issue: Copilot not generating complete code
**Solution:** 
- Break down the prompt into smaller chunks
- Start with class definition, then add methods one by one
- Use comments to guide Copilot

### Issue: Import errors
**Solution:**
- Ensure __init__.py files exist
- Check relative vs absolute imports
- Verify all dependencies installed

### Issue: Tests failing
**Solution:**
- Mock external dependencies
- Use pytest-asyncio for async tests
- Check fixture scope

### Issue: Low coverage
**Solution:**
- Add edge case tests
- Test error conditions
- Test all state transitions

## Completion Criteria

Before marking Phase 1 complete:
1. [ ] All components implemented
2. [ ] All tests passing
3. [ ] Coverage >85%
4. [ ] Documentation updated
5. [ ] Config files created
6. [ ] No TODOs remaining
7. [ ] Code reviewed for quality

## Next Steps

After completing Phase 1:
1. Update STATUS.md with completion
2. Update TRACKER.md with progress
3. Create PHASE_001_COMPLETION_SUMMARY.md
4. Commit with proper message format
5. Move to Phase 2 (validator plugin adapter)

## Tips for Using GitHub Copilot

1. **Be Specific:** Start with specific imports and class names
2. **Use Comments:** Add comments describing what you need
3. **Incremental:** Build piece by piece, don't expect everything at once
4. **Review:** Always review generated code for correctness
5. **Test:** Write tests immediately after implementation
6. **Iterate:** If first suggestion isn't perfect, try different approaches

## Command Reference

```bash
# Install dependencies
pip install pyyaml jsonschema watchdog msgpack pytest pytest-cov pytest-asyncio

# Run specific test
pytest tests/unit/governance/plugins/test_base.py -xvs

# Run with coverage
pytest tests/unit/governance/plugins/ --cov=libs/governance/plugins --cov-report=html

# Check for import issues
python -c "from libs.governance.plugins import IValidatorPlugin"

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/governance/validators.yaml'))"
```

---

**Remember:** The prompts at the top of each file contain all the requirements. Let Copilot do the heavy lifting, but always validate the output matches our governance standards from CLAUDE.md.