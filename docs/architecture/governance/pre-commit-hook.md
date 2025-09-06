# Pre-commit Hook Architecture

**Component:** Git Pre-commit Hook  
**Version:** 2.0.0  
**Last Updated:** 2025-01-10  
**Reviewed By:** Governance Team  
**Status:** OPERATIONAL - Modular System Active  

## Overview

The pre-commit hook system provides extreme governance validation for all git commits. The architecture uses a clean delegation pattern with the actual git hook being a simple dispatcher to the comprehensive governance validation system.

## Architecture Design

### Three-Layer Architecture

```
.git/hooks/pre-commit (Git Layer)
    ↓ delegates to
tools/hooks/pre-commit (Dispatcher Layer)  
    ↓ executes
libs/governance/hooks/pre-commit.py (Governance Layer)
    ↓ orchestrates
libs/governance/hooks/validators/* (Validator Modules)
```

### Component Responsibilities

#### 1. Git Hook Layer (.git/hooks/pre-commit)
- Symbolic link or copy of tools/hooks/pre-commit
- Installed during project setup
- Provides git integration point
- Never modified directly

#### 2. Dispatcher Layer (tools/hooks/pre-commit)
- Simple Python script (~80 lines)
- Handles git integration cleanly
- Provides process isolation
- Enforces no-bypass policy
- Manages timeouts and errors

#### 3. Governance Layer (libs/governance/hooks/pre-commit.py)
- Modular validator system
- Configuration-driven validation
- Comprehensive rule enforcement
- Backward compatible with legacy systems
- Falls back to monolithic implementation if needed

#### 4. Validator Modules (libs/governance/hooks/validators/*)
- Individual validation components
- Single responsibility per validator
- Independently testable
- Extensible architecture

## Key Features

### 🏗️ Clean Architecture
- **Simple Delegation**: Git hook only handles git integration
- **Process Isolation**: Governance runs in its own subprocess
- **Path Resolution**: Dynamically finds the governance hook
- **Error Boundaries**: Clear separation between git and governance errors

### 🛡️ Robust Error Handling
- **No Bypass Policy**: Immediately blocks any bypass attempts
- **Timeout Protection**: 5-minute timeout prevents infinite hangs
- **Keyboard Interrupt**: Graceful handling of user interruption
- **File Validation**: Checks that governance hook exists before execution
- **Exit Code Propagation**: Maintains git's expected exit behavior

### 🚀 User Experience
- **Clear Messaging**: Users see exactly what's happening
- **Real-time Output**: No capture allows streaming output from governance
- **Professional Formatting**: Clean status messages with emojis
- **Informative Errors**: Helpful error messages for debugging

### 🔧 Maintainability Benefits
- **Version Controlled Logic**: Main governance logic stays in hooks
- **Easy Updates**: Update governance without touching git hooks
- **Testable**: Can test governance logic independently
- **Portable**: Works across different environments and setups

## Installation

### Automatic Installation (Recommended)

```bash
# Run the setup script
python tools/scripts/install_git_hooks.py

# Or use make command
make install-hooks
```

### Manual Installation

```bash
# Unix/Linux/Mac
ln -sf ../../tools/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Windows
copy tools\hooks\pre-commit .git\hooks\pre-commit
```

### Verification

```bash
# Test the hook is installed
ls -la .git/hooks/pre-commit

# Test governance is working
git add .
git commit -m "Test commit"
```

## Configuration

### Governance Configuration
Located at `config/governance/rules.yaml`:

```yaml
enforcement:
  compliance_minimum: 95
  mode: strict  # strict, progressive, warning
  
validators:
  enabled:
    - readme
    - code_doc
    - naming
    - file_creation
    - test_coverage
    - code_quality
```

### Validator Control
Enable/disable specific validators:

```yaml
validators:
  readme:
    enabled: true
    required_score: 85
    
  code_doc:
    enabled: true
    min_coverage: 85
```

## Validator Modules

### Available Validators

| Validator | Purpose | Configuration Key |
|-----------|---------|-------------------|
| `readme_validator` | Ensures README files exist | `validators.readme` |
| `code_doc_validator` | Validates code documentation | `validators.code_doc` |
| `naming_validator` | Enforces naming conventions | `validators.naming` |
| `file_creation_validator` | Controls file creation | `validators.file_creation` |
| `test_coverage_validator` | Ensures test coverage | `validators.test_coverage` |
| `code_quality_validator` | Checks code quality | `validators.code_quality` |

### Adding New Validators

1. Create validator class in `libs/governance/hooks/validators/`:
```python
from .base import ValidatorInterface, ValidationResult

class CustomValidator(ValidatorInterface):
    def validate(self) -> ValidationResult:
        # Implementation
        pass
```

2. Register in orchestrator configuration
3. Add configuration options to rules.yaml
4. Write tests in test_validators.py

## Error Handling

### Common Issues and Solutions

#### Hook Not Triggering
```bash
# Check installation
ls -la .git/hooks/pre-commit

# Reinstall
python tools/scripts/install_git_hooks.py
```

#### Governance System Not Found
```bash
# Verify governance files exist
ls libs/governance/hooks/pre-commit.py

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Validation Timeout
```bash
# Run governance directly to debug
python libs/governance/hooks/pre-commit.py

# Check for infinite loops in validators
python -m libs.governance.hooks.validators.test_validators
```

## Bypass Prevention

The system implements multiple layers of bypass prevention:

1. **Environment Check**: Blocks `GOVERNANCE_BYPASS` environment variable
2. **Direct Execution Block**: Cannot run validators with bypass flags
3. **No Skip Options**: No command-line flags to skip validation
4. **Audit Logging**: All attempts logged for security review

## Performance Considerations

### Optimization Strategies
- Validators run only on changed files
- Configuration cached during execution
- Early exit on critical failures (fail-fast mode)
- Parallel validation possible (future enhancement)

### Performance Metrics
- Typical execution: 2-5 seconds
- Large commits: 10-30 seconds
- Timeout threshold: 5 minutes
- Target performance: <10 seconds for 95% of commits

## Testing

### Unit Tests
```bash
# Test individual validators
python -m pytest libs/governance/hooks/validators/test_validators.py

# Test specific validator
python -m pytest libs/governance/hooks/validators/test_validators.py::TestReadmeValidator
```

### Integration Tests
```bash
# Test full hook flow
python tools/tests/test_git_hooks.py

# Test with sample commit
git add test_file.py
GIT_HOOK_TEST=1 .git/hooks/pre-commit
```

### Manual Testing
```bash
# Create test commit
echo "test" > test.txt
git add test.txt
git commit -m "Test governance"
```

## Troubleshooting

### Debug Mode
```bash
# Enable verbose output
export GOVERNANCE_DEBUG=1
git commit -m "Debug test"
```

### Check Validator Status
```python
# Run orchestrator directly
from libs.governance.hooks.validators.orchestrator import ValidatorOrchestrator
orchestrator = ValidatorOrchestrator()
results = orchestrator.run_all_validators()
print(results)
```

### Reset Hook
```bash
# Remove and reinstall
rm .git/hooks/pre-commit
python tools/scripts/install_git_hooks.py
```

## Migration from Legacy System

### Backward Compatibility
The new system maintains 100% backward compatibility:
- Same configuration format
- Same validation rules
- Same scoring system
- Same user interface

### Migration Steps
1. Update repository to latest version
2. Run `python tools/scripts/install_git_hooks.py`
3. Verify with test commit
4. No configuration changes needed

## Security Considerations

### Threat Model
- **Bypass Attempts**: Blocked at multiple levels
- **Code Injection**: Validators run in restricted context
- **Path Traversal**: All paths validated and sandboxed
- **Timeout Attacks**: 5-minute maximum execution time

### Audit Trail
All validation attempts are logged to:
- `.governance/audit/extreme_governance_YYYYMMDD.jsonl`
- Includes timestamp, user, files, violations, scores

## Future Enhancements

### Planned Features
1. **Parallel Validation**: Run independent validators concurrently
2. **Incremental Validation**: Cache results for unchanged files
3. **Smart Suggestions**: AI-powered fix recommendations
4. **Custom Validators**: Plugin architecture for project-specific rules
5. **Performance Dashboard**: Real-time metrics and trends

### Version Roadmap
- **v2.1**: Parallel validation support
- **v2.2**: Incremental validation with caching
- **v3.0**: AI-powered suggestions
- **v3.1**: Plugin architecture
- **v4.0**: Cloud-based governance service

## References

- [Governance Architecture](./README.md)
- [Validator System Documentation](../../../libs/governance/hooks/validators/README.md)
- [Configuration Guide](../../../config/governance/README.md)
- [CLAUDE.md](../../../CLAUDE.md)

---

**Document Owner:** Governance Team  
**Next Review:** Monthly  
**Support:** governance@system.local  

*"Clean architecture, robust validation, zero bypasses."*