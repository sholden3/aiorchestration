# Governance Core Components

## Purpose
Core governance engine and supporting components for enforcing project standards.

## Contents
- `engine.py` - Main governance engine implementation
- `enhanced_governance_engine.py` - Enhanced version with progressive enforcement
- `session_manager.py` - Session management for governance operations
- `context.py` - Governance context management
- `correlation_tracker.py` - Track correlations between governance events
- `exceptions.py` - Custom exceptions for governance system
- `result.py` - Result objects for governance checks
- `todo_tracker.py` - Track and enforce TODO/FIXME standards
- `governance_monitor.py` - Real-time governance monitoring
- `governance_reporter.py` - Generate governance reports
- `runtime_governance.py` - Runtime governance enforcement
- `exemption_manager.py` - Manage validation exemptions

## Dependencies
- PyYAML for configuration parsing
- Python 3.8+ with type hints
- pathlib for file operations
- datetime for timestamps
- json for audit logs

## Testing
- Unit tests in `tests/unit/governance/`
- Integration tests in `tests/integration/governance/`
- Test coverage target: 85%

## Maintenance
- Review exemptions monthly
- Update engine when new rules are added
- Monitor performance metrics
- Archive old session data quarterly