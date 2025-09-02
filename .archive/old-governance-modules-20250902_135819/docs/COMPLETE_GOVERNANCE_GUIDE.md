# Complete AI Governance System Guide
**Version**: 2.0  
**Status**: Fully Integrated  
**Phase**: Advisory Mode (Phase 2)  
**Last Updated**: 2025-01-30  

---

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Configuration](#configuration)
4. [Installation & Setup](#installation--setup)
5. [Usage Guide](#usage-guide)
6. [Monitoring & Dashboards](#monitoring--dashboards)
7. [Exemption Management](#exemption-management)
8. [Testing & Validation](#testing--validation)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

---

## 🎯 System Overview

The AI Governance System is a comprehensive framework that enforces code quality, security, and best practices across the entire development lifecycle. It integrates with git hooks, CI/CD pipelines, and provides real-time monitoring of all governance activities.

### Key Features
- **Magic Variable Detection**: Identifies and flags hardcoded values
- **Boilerplate Detection**: Finds repetitive code patterns
- **Domain-Specific Validation**: Database, cache, frontend, API, security checks
- **Test Execution Tracking**: Monitors when tests were last run
- **Dependency Analysis**: Identifies downstream impacts of changes
- **Smart Exemptions**: Context-aware rule relaxation
- **Hallucination Detection**: Identifies potential AI-generated inaccuracies
- **Real-time Monitoring**: Dashboard and metrics tracking

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                     Git Pre-Commit Hook                      │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  Integrated Governance   │
        │        Orchestrator      │
        └────────────┬────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼────┐    ┌────▼────┐    ┌────▼────┐
│Enhanced │    │ Domain  │    │ Smart   │
│  Engine │    │Validators│    │  Rules  │
└─────────┘    └─────────┘    └─────────┘
     │               │               │
     └───────────────┼───────────────┘
                     │
        ┌────────────▼────────────┐
        │   Governance Monitor    │
        │   (Dashboard & Metrics) │
        └─────────────────────────┘
```

---

## 🔧 Core Components

### 1. Enhanced Governance Engine
**Location**: `governance/core/enhanced_governance_engine.py`

Provides core detection capabilities:
- **MagicVariableDetector**: Finds hardcoded numbers and strings
- **TestExecutionTracker**: Tracks when tests were last run
- **BoilerplateDetector**: Identifies repetitive code patterns
- **DownstreamDependencyAnalyzer**: Maps file dependencies

### 2. Domain Validators
**Location**: `governance/validators/domain_validators.py`

Specialized validators for different domains:
- **DatabaseValidator**: SQL injection, N+1 queries, connection pooling
- **CacheValidator**: TTL settings, invalidation strategies, key naming
- **FrontendValidator**: XSS vulnerabilities, performance issues, accessibility
- **APIValidator**: Rate limiting, versioning, authentication
- **SecurityValidator**: Hardcoded secrets, weak cryptography, input validation

### 3. Smart Rules Engine
**Location**: `governance/rules/smart_rules.py`

Intelligent pattern matching with exemptions:
- Context-aware dangerous pattern detection
- Secret detection with false positive mitigation
- Performance anti-pattern identification
- Architecture violation detection

### 4. Integrated Pre-Commit Hook
**Location**: `governance/scripts/integrated_pre_commit_hook.py`

Main orchestrator for git operations:
- Stages file analysis
- Runs all validators
- Analyzes dependencies
- Generates comprehensive reports
- Enforces phase-appropriate blocking

### 5. Governance Monitor
**Location**: `governance/core/governance_monitor.py`

Real-time monitoring and dashboards:
- Event tracking and logging
- Metrics collection
- Dashboard generation
- Performance analysis
- Exemption usage tracking

---

## ⚙️ Configuration

### Main Configuration Files

#### 1. Exemptions Configuration
**File**: `governance-config/exemptions.yml`

```yaml
magic_number_exemptions:
  allowed_contexts:
    - name: "HTTP Status Codes"
      patterns:
        - "status.*200"
        - "response.*404"
        
file_exemptions:
  - path: "**/test_*.py"
    reason: "Test files need specific values"
```

#### 2. Hallucination Patterns
**File**: `governance-config/hallucination-patterns.yml`

```yaml
patterns:
  critical:
    - name: "future_date_claim"
      pattern: '\b20[3-9]\d\s+(?:study|research)'
      severity: CRITICAL
```

#### 3. Phase Configuration
The system operates in three phases:

| Phase | Name | Enforcement | Description |
|-------|------|-------------|-------------|
| 1 | Learning | 10% | Minimal enforcement, gathering data |
| 2 | Advisory | 50% | **Current phase** - Warnings but allows commits |
| 3 | Enforcement | 90% | Blocks commits for violations |

---

## 🚀 Installation & Setup

### Prerequisites
```bash
# Python 3.8+
python --version

# Required packages
pip install pyyaml pytest coverage
```

### Installation Steps

#### 1. Clone or Navigate to Repository
```bash
cd /path/to/your/project
```

#### 2. Install Governance Framework
```bash
# Install Python dependencies
pip install -r governance/requirements.txt

# Create governance directories
mkdir -p .governance/metrics
mkdir -p governance-config
```

#### 3. Install Git Hooks
```bash
python governance/scripts/install_git_hooks.py
```

Or manually:
```bash
#!/bin/bash
# .git/hooks/pre-commit
python governance/scripts/integrated_pre_commit_hook.py
```

#### 4. Verify Installation
```bash
python governance/scripts/validate_governance.py
```

Expected output:
```
🚀 GOVERNANCE SYSTEM VALIDATION
==================================================
✅ Enhanced Governance Engine: PASSED
✅ Domain Validators: PASSED
✅ Smart Rules Engine: PASSED
✅ Integrated Pre-Commit Hook: PASSED
✅ Governance Monitoring: PASSED
✅ Exemption Configuration: PASSED
✅ Git Hook Installation: PASSED
✅ Test Coverage Check: PASSED

🎉 GOVERNANCE SYSTEM FULLY OPERATIONAL
```

---

## 📖 Usage Guide

### Basic Usage

#### 1. Normal Development Flow
The governance system runs automatically on git commit:

```bash
# Make changes
edit src/my_file.py

# Stage changes
git add src/my_file.py

# Commit - governance runs automatically
git commit -m "feat: Add new feature"
```

#### 2. Viewing Governance Output
```
========================================================================
🔍 GOVERNANCE CHECK REPORT - GOV-20250130-143022-abc123
========================================================================

📊 Governance Phase: 2 (Advisory)

📈 Statistics:
  • Files checked: 3
  • Files with issues: 1
  • Total issues found: 2

🎯 Issues by Severity:
  🟡 Medium: 2

📝 Issues by File:
  📄 src/my_file.py:
    🟡 [magic_variable] Hardcoded value: 99999
       Line 42
       💡 Extract to configuration or constant

🚦 Governance Decision:
  ✅ COMMIT ALLOWED - Running in advisory mode
     (Issues detected but not blocking in current phase)
```

#### 3. Bypassing Governance (Emergency)
```bash
# Skip governance checks
SKIP_GOVERNANCE=true git commit -m "emergency: Fix production"

# Or use --no-verify
git commit --no-verify -m "emergency: Fix production"
```

### Advanced Usage

#### 1. Running Specific Validators
```python
from governance.validators.domain_validators import DatabaseValidator

validator = DatabaseValidator()
result = validator.validate(code_content, "myfile.py")

for issue in result.issues:
    print(f"{issue['severity']}: {issue['message']}")
```

#### 2. Checking Test Freshness
```python
from governance.core.enhanced_governance_engine import TestExecutionTracker

tracker = TestExecutionTracker()
status = tracker.check_test_freshness()

if status['days_since_run'] > 7:
    print("Tests are stale - run them!")
```

#### 3. Analyzing Dependencies
```python
from governance.core.enhanced_governance_engine import DownstreamDependencyAnalyzer

analyzer = DownstreamDependencyAnalyzer()
deps = analyzer.analyze_file("src/core/engine.py")

print(f"This file affects: {deps['dependents']}")
print(f"Tests to run: {deps['affected_tests']}")
```

---

## 📊 Monitoring & Dashboards

### Governance Dashboard
Run the monitoring dashboard:

```bash
python -m governance.core.governance_monitor
```

Output:
```
🎯 GOVERNANCE MONITORING DASHBOARD
========================================================================
Generated: 2025-01-30 14:30:22

📊 Last 24 Hours Activity:
  Total Events: 42
  🔴 CRITICAL: 0
  🟠 ERROR: 2
  🟡 WARNING: 8
  ℹ️ INFO: 32

🧪 Test Execution (Last 7 Days):
  Total Runs: 15
  Pass Rate: 87.3%
  Average Duration: 4.32s
  Daily Trend:
    2025-01-28: ████████ 82.1%
    2025-01-29: █████████ 91.5%
    2025-01-30: ████████ 87.3%

🚫 Commit Blocks (Last 30 Days):
  Total Blocked: 3
  Top Reasons:
    • Missing documentation: 2
    • Security violation: 1

💚 System Health:
  Overall Status: ✅ Healthy (90/100)
```

### Metrics Export
Export metrics for analysis:

```bash
python -m governance.core.governance_monitor --export metrics.json
```

### Real-time Monitoring
Watch governance events in real-time:

```bash
tail -f .governance/governance_activity_*.log
```

---

## 🔖 Exemption Management

### Adding Exemptions

#### 1. File-Level Exemptions
Edit `governance-config/exemptions.yml`:

```yaml
file_exemptions:
  - path: "legacy/old_module.py"
    patterns: ["eval", "exec"]
    reason: "Legacy code - scheduled for removal Q2 2025"
    expires: "2025-06-30"
    reviewed_by: ["sarah_chen", "alex_novak"]
```

#### 2. Context-Based Exemptions
```yaml
context_exemptions:
  - context: "test_"
    patterns: ["hardcoded_password", "admin123"]
    reason: "Test fixtures need predictable values"
```

#### 3. Temporary Exemptions
```yaml
temporary_exemptions:
  - path: "src/experimental/*.py"
    patterns: ["*"]
    reason: "Experimental feature - relaxed rules"
    expires: "2025-02-15"
    ticket: "JIRA-1234"
```

### Reviewing Exemptions
```bash
# Check exemption usage
python -c "
from governance.core.governance_monitor import GovernanceMonitor
monitor = GovernanceMonitor()
stats = monitor.get_exemption_stats(30)
print(f'Total exemptions used: {stats['total_exemptions']}')
"
```

---

## 🧪 Testing & Validation

### Running Governance Tests
```bash
# Run all governance tests
python -m pytest governance/tests/ -v

# Run specific test category
python -m pytest governance/tests/test_domain_validators.py -v

# Run with coverage
python -m pytest governance/tests/ --cov=governance --cov-report=html
```

### Validation Script
```bash
# Validate entire governance system
python governance/scripts/validate_governance.py

# Quick test of components
python governance/scripts/quick_test.py
```

### Integration Testing
```bash
# Test with sample files
echo "timeout = 99999" > test.py
python governance/scripts/integrated_pre_commit_hook.py --files test.py
rm test.py
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Governance checks not running"
**Solution**: Verify hook installation
```bash
ls -la .git/hooks/pre-commit
cat .git/hooks/pre-commit | head -5
```

#### 2. "Too many false positives"
**Solution**: Add appropriate exemptions
```yaml
# governance-config/exemptions.yml
magic_number_exemptions:
  file_exemptions:
    - path: "config/*.py"
      reason: "Configuration files define constants"
```

#### 3. "Tests marked as stale incorrectly"
**Solution**: Update test execution tracking
```bash
# Record test execution
python -c "
from governance.core.enhanced_governance_engine import TestExecutionTracker
tracker = TestExecutionTracker()
tracker.record_test_execution('all', datetime.now())
"
```

#### 4. "Performance issues with large commits"
**Solution**: Adjust file limits
```python
# In integrated_pre_commit_hook.py
MAX_FILES_TO_CHECK = 50  # Limit number of files
```

### Debug Mode
Enable verbose output:
```bash
GOVERNANCE_DEBUG=true git commit -m "test"
```

### Logs Location
- Governance events: `.governance/governance_activity_*.log`
- Metrics database: `.governance/metrics.db`
- Validation reports: `.governance/validation_report.json`

---

## 📚 API Reference

### Core Classes

#### GovernanceEngine
```python
from governance.core.enhanced_governance_engine import EnhancedGovernanceEngine

engine = EnhancedGovernanceEngine(repo_root=Path.cwd(), phase=2)
result = engine.check_file(file_path)
```

#### MagicVariableDetector
```python
from governance.core.enhanced_governance_engine import MagicVariableDetector

detector = MagicVariableDetector()
issues = detector.detect(code_content, file_path)
```

#### IntegratedPreCommitHook
```python
from governance.scripts.integrated_pre_commit_hook import IntegratedPreCommitHook

hook = IntegratedPreCommitHook(phase=2)
allow_commit, report = hook.run()
```

### Event Types
```python
from governance.core.governance_monitor import GovernanceMonitor

monitor = GovernanceMonitor()
monitor.record_event(
    event_type="custom_check",
    severity="WARNING",
    file_path="src/file.py",
    message="Custom validation failed",
    metadata={"details": "..."}
)
```

---

## 🚦 Phase Progression

### Current: Phase 2 (Advisory)
- Issues are reported but don't block commits
- Gathering metrics for rule refinement
- Building exemption patterns

### Moving to Phase 3 (Enforcement)
When ready to enforce stricter rules:

```python
# Update phase in integrated_pre_commit_hook.py
hook = IntegratedPreCommitHook(phase=3)
```

### Phase 3 Changes
- Critical/High severity issues block commits
- Stricter documentation requirements
- Performance checks enforced
- Test coverage requirements

---

## 📈 Metrics & KPIs

### Key Metrics Tracked
1. **Governance Events**: All validation activities
2. **Test Execution**: Frequency and results
3. **Commit Blocks**: Reasons and frequency
4. **Exemption Usage**: Patterns and trends
5. **Code Coverage**: Current coverage levels

### Accessing Metrics
```python
from governance.core.governance_monitor import GovernanceMonitor

monitor = GovernanceMonitor()
metrics = monitor.export_metrics()

print(f"Recent events: {len(metrics['recent_events'])}")
print(f"Test pass rate: {metrics['test_metrics']['pass_rate']}%")
print(f"Exemptions used: {metrics['exemption_usage']['total_exemptions']}")
```

---

## 🔄 Continuous Improvement

### Adding New Validators
1. Create validator class in `governance/validators/`
2. Implement `validate()` method
3. Add to `integrated_pre_commit_hook.py`
4. Write tests in `governance/tests/`

### Updating Patterns
1. Edit configuration files in `governance-config/`
2. Test with sample code
3. Monitor false positive rate
4. Adjust confidence scores

### Feedback Loop
1. Collect metrics weekly
2. Review false positives
3. Update exemptions
4. Refine patterns
5. Progress phases gradually

---

## 📞 Support & Contact

### Getting Help
- Check this guide first
- Review logs in `.governance/`
- Run validation script
- Check exemption configuration

### Reporting Issues
When reporting governance issues, include:
1. Governance phase (1, 2, or 3)
2. Error message from report
3. File type being validated
4. Relevant exemptions configured

### Contributing
To contribute to the governance system:
1. Add tests for new features
2. Update documentation
3. Follow existing patterns
4. Maintain backward compatibility

---

*Last Updated: 2025-01-30 by Governance Team*  
*Version: 2.0 - Full Integration with Smart Exemptions*