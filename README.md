# Claude Research and Development

## Purpose
AI Development Assistant platform with extreme governance enforcement for code quality and documentation standards.

## Contents
- `ai-assistant/` - Main application (Angular frontend + Python backend)
- `governance/` - Extreme governance system configuration and hooks
- `docs/` - Project documentation and architecture decisions
- `tests/` - Unified test suite for all components
- `.governance/` - Session management and audit logs
- `TRACKER.md` - Current operation tracking
- `STATUS.md` - System status and inventory
- `DECISIONS.md` - Architectural decisions log
- `CLAUDE.md` - Project instructions and requirements

## Dependencies
- Node.js 18+ for frontend
- Python 3.8+ for backend
- PostgreSQL 14+ for database (optional)
- Git for version control
- Electron for desktop application

## Testing
Run tests with:
- Backend: `pytest tests/backend/`
- Frontend: `npm test`
- E2E: `npm run e2e`
- Governance: Hook automatically runs on commit

## Maintenance
- Weekly: Review audit logs in `.governance/audit/`
- Monthly: Update governance rules in `governance/config.yaml`
- Quarterly: Archive old operations and reports
- Always: Maintain 95% compliance score minimum