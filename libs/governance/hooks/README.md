# Governance Hooks Documentation

## Purpose
Pre-commit and post-commit hooks for enforcing extreme governance standards with zero tolerance across documentation and code.

## Quick Setup

### 1. Install Prerequisites
```bash
# Install pre-commit framework
pip install pre-commit

# Install validation dependencies
pip install pyyaml markdown requests

# Install pre-commit hooks
pre-commit install
```

### 2. Manual Validation Commands
```bash
# Validate specific documentation files
python -m governance.validators.doc_validator <file>

# Validate code documentation
python -m governance.validators.code_doc_validator <file>

# Run all validators
python governance/hooks/pre-commit.py

# Check specific file types
python governance/hooks/pre-commit.py --pattern "*.md"
```

## Contents
- `pre-commit.py` - Main governance enforcement hook
- `claude_code_governance_hook.py` - Claude Code integration
- `governance_hook.sh` - Unix/Linux/macOS platform hook
- `governance_hook.bat` - Windows platform hook
- `__init__.py` - Package initialization
- `README.md` - This documentation file

## Hook Components

### Pre-commit Hook (`pre-commit.py`)
- **Purpose**: Main enforcement hook with config-driven rules
- **Features**:
  - Documentation validation (markdown files)
  - Code documentation validation (Python/TypeScript/JavaScript)
  - Configuration-driven rule enforcement
  - Progressive enforcement based on timeline
  - Detailed error reporting with fix suggestions

### Claude Code Governance Hook (`claude_code_governance_hook.py`)
- **Purpose**: Integration with Claude Code for governance
- **Features**:
  - AI-assisted governance checks
  - Documentation quality assessment
  - Code review automation

### Platform-Specific Hooks
- `governance_hook.sh` - Unix/Linux/macOS
- `governance_hook.bat` - Windows

## Configuration

### Main Configuration Files
- `governance/config.yaml` - Governance settings and thresholds
- `.docs-metadata/validation-rules.yaml` - Document validation rules
- `.docs-metadata/code-formats.yaml` - Code documentation standards

### Validation Thresholds
```yaml
# From governance/config.yaml
validation:
  documentation_threshold: 85  # Minimum documentation score
  test_coverage_target: 85     # Minimum test coverage
  code_documentation: 70        # Minimum code doc score
```

## Manual Validation

### Validate Documentation
```bash
# Single file
python -m governance.validators.doc_validator STATUS.md

# Multiple files  
python -m governance.validators.doc_validator *.md

# With specific metadata
python -m governance.validators.doc_validator --metadata .docs-metadata/STATUS.meta.yaml STATUS.md
```

### Validate Code Documentation
```bash
# Python files
python -m governance.validators.code_doc_validator backend/**/*.py

# TypeScript files
python -m governance.validators.code_doc_validator frontend/**/*.ts

# All supported files
python -m governance.validators.code_doc_validator --all
```

## Common Validation Errors

### Documentation Errors

#### Missing Required Section
```
❌ Missing required section 'Overview' in docs/architecture/backend.md
```
**Fix**: Add the missing section with proper header level.

#### Unfilled Placeholder
```  
❌ Required placeholder [DATE] not filled in STATUS.md
```
**Fix**: Replace `[DATE]` with actual date in YYYY-MM-DD format.

#### Invalid Format
```
❌ Placeholder [PERCENTAGE] format invalid: '85' should be '85%'
```
**Fix**: Ensure format matches the required pattern.

### Code Documentation Errors

#### Missing Module Docstring
```
❌ Missing module docstring in backend/main.py
```
**Fix**: Add module docstring at file start.

#### Missing Method Documentation
```
❌ Public method 'process_data' missing docstring
```
**Fix**: Add docstring following the configured style (Google/NumPy/Sphinx).

## Troubleshooting

### Pre-commit Hooks Not Running
```bash
# Reinstall hooks
pre-commit clean
pre-commit install

# Check configuration
pre-commit validate-config

# Run manually
pre-commit run --all-files
```

### Validation Script Errors
```bash
# Check Python dependencies
pip install -r requirements.txt

# Verify metadata files
python -c "import yaml; yaml.safe_load(open('.docs-metadata/code-formats.yaml'))"

# Check validator imports
python -c "from governance.validators import doc_validator"
```

### Hook Bypass (Emergency Only)
```bash
# Skip validation for emergency fix
git commit -m "Emergency fix" --no-verify

# Note: This is logged and requires justification
```

## Integration with CI/CD

### GitHub Actions
```yaml
- name: Run Governance Hooks
  run: |
    pip install pyyaml markdown requests
    python governance/hooks/pre-commit.py
```

### GitLab CI
```yaml
governance:
  script:
    - pip install pyyaml markdown requests
    - python governance/hooks/pre-commit.py
```

## Dependencies
- Python 3.8+
- PyYAML for configuration parsing
- markdown for markdown parsing
- requests for external validation
- Git hooks system

## Testing
- Tested on every commit attempt
- No bypass allowed without justification
- All violations logged for review

## Maintenance
- Update when `config.yaml` changes
- Review violations weekly
- Never add bypass mechanisms without approval
- Keep validation rules synchronized with templates

## Best Practices

### For Developers
1. ✅ Run validation locally before pushing
2. ✅ Fix all critical violations immediately
3. ✅ Document code as you write it
4. ✅ Keep documentation synchronized with code

### For Maintainers
1. ✅ Review hook performance monthly
2. ✅ Update rules based on team feedback
3. ✅ Monitor false positive rates
4. ✅ Keep error messages helpful and actionable

## Support
- Check `governance/README.md` for overall governance documentation
- Review `.docs-metadata/` for validation rule configurations
- See `tests/unit/governance/` for validator test examples