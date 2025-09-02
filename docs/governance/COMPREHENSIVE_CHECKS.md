# Comprehensive Governance Checks

## Purpose
Complete quality gate system to prevent bad code, ensure testing, and maintain standards.

## Contents
This document describes all checks performed by the extreme governance system.

## Dependencies
- Python pytest with coverage
- Node.js/npm for JavaScript testing
- Git for version control

## Testing
All checks are config-driven and tested

## Maintenance
Update config.yaml to modify check behavior

---

## Implemented Checks

### 1. README Files ✅
- Every directory up to depth 2 must have README.md
- Specific parent directories always require READMEs
- Each README must contain required sections

### 2. Source Documentation ✅
Every source file must have:
- @description - What the file does
- @author - Who wrote it (persona)
- @version - Version number
- @dependencies - What it needs
- @exports - What it provides
- @testing - Test coverage percentage
- @last_review - Last review date

### 3. Naming Standards ✅
- Enforces standard file names (TRACKER.md, STATUS.md, etc.)
- Prevents non-standard variations

### 4. File Creation Rules ✅ NEW
**Allowed patterns:**
- Source files: *.py, *.ts, *.tsx, *.js, *.jsx
- Documentation: *.md
- Config: *.json, *.yaml, *.yml
- Scripts: *.sh, *.bat
- Tests: *.spec.*, *.test.*

**Forbidden patterns:**
- Temp files: *.tmp, *.bak
- Debug files: debug_*, test_*
- Log files: *.log
- Compiled: *.pyc, __pycache__

### 5. Test Coverage ✅ ENHANCED
- Every source file must have corresponding test file
- Pattern matching supports hyphens/underscores
- Config-driven patterns per file extension

### 6. Code Quality ✅ NEW
Blocks commits with:
- console.log() statements
- Debug print statements
- debugger; statements
- Unresolved TODO/FIXME/HACK comments
- Python pdb imports or breakpoints

### 7. Documentation Sync ✅ NEW
- Warns when >3 code files change without doc updates
- Ensures documentation stays current with code

### 8. Test Execution & Coverage ✅ NEW
**Python:**
- Runs pytest with coverage
- Enforces 85% minimum coverage
- Shows coverage gaps

**JavaScript/TypeScript:**
- Runs npm test with coverage
- Enforces 80% minimum coverage

### 9. Security Checks ✅
Blocks dangerous patterns:
- eval() and exec() usage
- shell=True in subprocess
- innerHTML and dangerouslySetInnerHTML
- Hardcoded passwords/tokens/secrets

### 10. No Bypass ✅
- Zero tolerance mode
- No environment variable bypasses
- No exceptions allowed

## Configuration

All checks are configured in `governance/config.yaml`:

```yaml
testing:
  minimum_coverage:
    python: 85
    typescript: 80
  execution_required: true  # Set to true to run tests
  fail_on_test_failure: true
  coverage_enforcement: true

file_creation:
  allowed_patterns: [...]
  forbidden_patterns: [...]
  
security:
  code_quality_patterns: [...]
  dangerous_patterns: [...]
```

## Usage

The hook runs automatically on every commit:

```bash
git commit -m "Your message"

# Output:
======================================================================
EXTREME GOVERNANCE ENFORCEMENT v2.0
======================================================================
[CHECK] README.md Files
[CHECK] Source Code Documentation  
[CHECK] Naming Standards
[CHECK] File Creation Rules
[CHECK] Test Coverage
[CHECK] Code Quality
[CHECK] Documentation Sync
[CHECK] Test Execution & Coverage
======================================================================
```

## Compliance Score

- 95% minimum required
- Penalties per violation type:
  - Critical: -20%
  - High: -10%
  - Medium: -5%
  - Low: -2%

## Emergency Override

There is NO override mechanism. To commit:
1. Fix all violations
2. Ensure tests pass
3. Meet coverage requirements
4. Update documentation
5. Remove debug code

This is extreme governance - no exceptions, no bypasses.