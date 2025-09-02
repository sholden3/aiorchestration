# Audit Logs

## Purpose
Immutable audit trail of all governance decisions and enforcement actions.

## Contents
JSONL format audit logs with timestamps, actors, and decisions.

## Dependencies
- Written by governance hooks
- Read by compliance reports

## Testing
- Log integrity validation
- Retention policy enforcement

## Maintenance
- Rotate after 365 days
- Archive to cold storage
- Never delete without backup