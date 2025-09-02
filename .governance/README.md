# Governance Runtime

## Purpose
Runtime governance data including session management, audit logs, and correlations.

## Contents
- `audit/` - Audit logs of all governance decisions
- `session/` - Current and historical session data
- `logs/` - Governance execution logs
- `core/` - Core session management
- `config/` - Runtime configuration

## Dependencies
- Python governance system
- Git hooks
- Session management scripts

## Testing
Automated via governance hooks on each commit.

## Maintenance
- Audit logs rotate after 365 days
- Session files auto-expire after 8 hours
- Logs cleaned monthly