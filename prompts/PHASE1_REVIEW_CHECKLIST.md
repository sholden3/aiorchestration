# Phase 1 Review & Organization Checklist

## Current Status
GitHub Copilot has successfully implemented the core plugin architecture. Now we need to review, organize, and standardize the output.

## Issues Found

### 1. Test File Organization
**Problem**: Tests are scattered across multiple directories
- `tests/governance/test_plugin_*.py`
- `tests/governance/plugins/test_*.py`
- `tests/unit/test_plugin_*.py`
- Multiple versions of same test (test_plugin_base.py, test_plugin_base_enhanced.py, test_plugin_base_simple.py)

**Solution**: Consolidate all plugin tests into `tests/unit/governance/plugins/`

### 2. Configuration Files
**Status**: ✅ Created
- `config/governance/plugin_registry.yaml` ✅
- `config/governance/lifecycle.yaml` ✅
- `config/governance/validators.yaml` ❌ (Missing - needs creation)

### 3. Import Issues
**Potential Problems**:
- Absolute vs relative imports
- Missing __init__.py files in test directories
- Module path issues

## Review Tasks

### Step 1: Test Consolidation
```bash
# Create proper test structure
mkdir -p tests/unit/governance/plugins

# Move all plugin tests to correct location
mv tests/governance/test_plugin_*.py tests/unit/governance/plugins/
mv tests/governance/plugins/*.py tests/unit/governance/plugins/
mv tests/unit/test_plugin_*.py tests/unit/governance/plugins/

# Remove duplicates
# Keep only the most comprehensive version of each test
```

### Step 2: Create Missing Configuration
```yaml
# config/governance/validators.yaml
validators:
  security_validator:
    enabled: true
    plugin: SecurityValidatorPlugin
    version: "1.0.0"
    config:
      scan_secrets: true
      check_dependencies: true
      severity_threshold: "HIGH"
      source: "config/security_rules.yaml"
      database: "sqlite:///validators.db"
    hooks:
      - pre-commit
      - PreToolUse
    priority: 100
    
  code_quality_validator:
    enabled: true
    plugin: CodeQualityValidatorPlugin
    version: "1.0.0"
    config:
      min_coverage: 85
      max_complexity: 10
      source: "config/quality_rules.yaml"
    hooks:
      - pre-commit
      - PostToolUse
    priority: 90

  documentation_validator:
    enabled: true
    plugin: DocumentationValidatorPlugin
    version: "1.0.0"
    config:
      min_score: 70
      check_headers: true
      check_examples: true
    hooks:
      - pre-commit
      - PrePromptGeneration
    priority: 80
```

### Step 3: Test Organization Review

For each test file, ensure:
- [ ] Proper imports from `libs.governance.plugins`
- [ ] Uses pytest fixtures appropriately
- [ ] Has async test support where needed
- [ ] Follows naming convention: `test_<component>.py`
- [ ] No duplicate test implementations

**Expected test files**:
- `test_base.py` - Tests for IValidatorPlugin and BaseValidatorPlugin
- `test_registry.py` - Tests for PluginRegistry
- `test_lifecycle.py` - Tests for PluginLifecycleManager
- `test_config.py` - Tests for ConfigurationLoader
- `test_messaging.py` - Tests for PluginMessageBus
- `test_integration.py` - Integration tests for the whole system

### Step 4: Code Quality Checks

For each implementation file:
- [ ] Type hints on all functions
- [ ] Docstrings on all public methods
- [ ] No hardcoded values
- [ ] Error handling implemented
- [ ] Logging statements present
- [ ] Thread safety where needed

### Step 5: Import Path Verification
```python
# Test that all imports work correctly
python -c "from libs.governance.plugins import IValidatorPlugin"
python -c "from libs.governance.plugins.registry import PluginRegistry"
python -c "from libs.governance.plugins.lifecycle import PluginLifecycleManager"
python -c "from libs.governance.plugins.config import ConfigurationLoader"
python -c "from libs.governance.plugins.messaging import PluginMessageBus"
```

### Step 6: Test Coverage Verification
```bash
# Run tests with coverage
pytest tests/unit/governance/plugins/ --cov=libs/governance/plugins --cov-report=term-missing

# Should achieve >85% coverage
```

## GitHub Copilot Enhancement Tips

For future prompts to GitHub Copilot, include:

### 1. Explicit File Locations
```python
"""
Create test file at: tests/unit/governance/plugins/test_base.py
Import from: libs.governance.plugins.base
"""
```

### 2. Configuration File Paths
```yaml
# Create at: config/governance/validators.yaml
# Reference in code as: Path("config/governance/validators.yaml")
```

### 3. Test Structure Template
```python
"""
Test template:
- Location: tests/unit/governance/plugins/
- Naming: test_<component>.py
- Fixtures: Create in conftest.py
- Async: Use pytest-asyncio
- Coverage: Aim for >90% per module
"""
```

### 4. Import Convention
```python
"""
Import convention:
- Absolute imports for libs: from libs.governance.plugins import X
- Relative imports within package: from .base import Y
- Test imports: from libs.governance.plugins.base import IValidatorPlugin
"""
```

## Validation Script

Create `validate_phase1.py`:
```python
#!/usr/bin/env python
"""Validate Phase 1 implementation."""

import sys
from pathlib import Path

def validate_structure():
    """Validate directory structure."""
    required_files = [
        "libs/governance/plugins/__init__.py",
        "libs/governance/plugins/base.py",
        "libs/governance/plugins/registry.py",
        "libs/governance/plugins/lifecycle.py",
        "libs/governance/plugins/config.py",
        "libs/governance/plugins/messaging.py",
        "config/governance/validators.yaml",
        "config/governance/plugin_registry.yaml",
        "config/governance/lifecycle.yaml",
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print("❌ Missing files:")
        for f in missing:
            print(f"  - {f}")
        return False
    
    print("✅ All required files present")
    return True

def validate_imports():
    """Validate all imports work."""
    try:
        from libs.governance.plugins import IValidatorPlugin
        from libs.governance.plugins.registry import PluginRegistry
        from libs.governance.plugins.lifecycle import PluginLifecycleManager
        from libs.governance.plugins.config import ConfigurationLoader
        from libs.governance.plugins.messaging import PluginMessageBus
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def validate_tests():
    """Check test files exist."""
    test_dir = Path("tests/unit/governance/plugins")
    if not test_dir.exists():
        print(f"❌ Test directory missing: {test_dir}")
        return False
    
    test_files = list(test_dir.glob("test_*.py"))
    if len(test_files) < 5:
        print(f"❌ Expected at least 5 test files, found {len(test_files)}")
        return False
    
    print(f"✅ Found {len(test_files)} test files")
    return True

if __name__ == "__main__":
    results = [
        validate_structure(),
        validate_imports(),
        validate_tests()
    ]
    
    if all(results):
        print("\n✅ Phase 1 validation PASSED")
        sys.exit(0)
    else:
        print("\n❌ Phase 1 validation FAILED")
        sys.exit(1)
```

## Next Steps

1. **Run test consolidation commands**
2. **Create missing validators.yaml**
3. **Remove duplicate test files**
4. **Run validation script**
5. **Check test coverage**
6. **Update tracking documents**
7. **Create completion summary**

## Completion Criteria

- [ ] All tests in `tests/unit/governance/plugins/`
- [ ] No duplicate test files
- [ ] All config files present
- [ ] All imports working
- [ ] Test coverage >85%
- [ ] Validation script passes
- [ ] No hardcoded values in code
- [ ] Documentation complete