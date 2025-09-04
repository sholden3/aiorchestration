# AI Development Assistant Documentation

**Project Name:** AI Orchestration Platform
**Version:** 2.1
**Last Updated:** September 3, 2025
**Project Status:** 🟢 OPERATIONAL - Documentation Standards Implemented

## Project Overview

AI Development Assistant platform with extreme governance enforcement for code quality and documentation standards. This document serves as the master instruction guide for AI assistants working on this codebase.

## Quick Start

### Prerequisites
- Node.js 18+ (Frontend & Electron)
- Python 3.10+ (Backend & Validators)
- PostgreSQL 14+ (Optional - SQLite fallback)
- Redis 7+ (Optional - in-memory fallback)
- Git 2.0+ (Version control & hooks)

### Installation
```bash
# Clone repository
git clone https://github.com/sholden3/aiorchestration.git
cd aiorchestration

# Backend setup
cd ai-assistant/backend
pip install -r requirements.txt
python main.py  # Runs on http://localhost:8000

# Frontend setup
cd ../
npm install
npm start  # Angular on http://localhost:4200
```

### First Run
```bash
# Verify governance is active
git add .
git commit -m "Test commit"  # Should trigger validation

# Run tests
pytest tests/unit/governance/test_*_validator.py -xvs
npm test
```

## Architecture Overview

Multi-tier application with Angular frontend, Python FastAPI backend, optional PostgreSQL/Redis, and extreme governance enforcement through pre-commit hooks and validators.

### Key Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | Angular 17 + TypeScript | User interface and interaction |
| Backend | Python FastAPI | API server and business logic |
| Desktop | Electron | Native desktop application |
| Database | PostgreSQL/SQLite | Data persistence |
| Cache | Redis/In-memory | Performance optimization |
| Governance | Python validators | Code & doc quality enforcement |

## Core Features

### 🛡️ Governance System
- **95% minimum compliance** requirement
- **Progressive enforcement** (warnings → blocks)
- **No bypass mechanisms** - zero tolerance
- **Config-driven rules** in governance/config.yaml
- **Comprehensive audit logging**

### 📝 Documentation Validation (NEW - Sept 3, 2025)
- **Markdown validator** with 85% test coverage
- **Code documentation validator** with 93% test coverage
- **Language-specific rules** for Python/TypeScript/JavaScript
- **27/27 tests passing**
- **Integrated into pre-commit hooks**

### 🧪 Testing Strategy
- **5-Layer Architecture**: Unit → Integration → Contract → E2E → Chaos
- **Coverage Standards**: 85% backend, 80% frontend
- **Validator Coverage**: Doc 85%, Code 93%
- **No simplification without approval**

## Project Structure
```
aiorchestration/
├── ai-assistant/          # Main application
│   ├── src/              # Angular frontend
│   ├── backend/          # FastAPI backend
│   └── electron/         # Desktop wrapper
├── governance/           # Governance system
│   ├── validators/       # Doc & code validators
│   ├── hooks/           # Pre-commit enforcement
│   └── config.yaml      # Rules configuration
├── .docs-metadata/      # Documentation standards
│   ├── validation-rules.yaml
│   ├── code-formats.yaml
│   └── format-templates/
├── tests/               # Comprehensive test suite
├── docs/                # Project documentation
├── claude/              # AI-specific configs
├── temp/               # Development workspace
└── project.yaml        # Project metadata
```

## Getting Started for Developers

### Development Workflow
1. **Check current tasks** in [TRACKER.md](./TRACKER.md)
2. **Follow governance rules** - 95% compliance required
3. **Write tests first** - TDD approach encouraged
4. **Document everything** - validators will check
5. **Clean temp directory** before commits

### Development Commands
```bash
# Start development
npm run dev              # Angular dev server
python main.py          # FastAPI backend
npm run electron        # Desktop app

# Testing
pytest tests/ -xvs      # Python tests
npm test               # JavaScript tests
pytest tests/unit/governance/  # Validator tests

# Validation
python -m governance.validators.doc_validator README.md
python -m governance.validators.code_doc_validator main.py

# Governance
git commit             # Triggers all validators
```

## Documentation Structure

### Core Documents
- [**STATUS.md**](./STATUS.md) - Real-time system health & metrics
- [**TRACKER.md**](./TRACKER.md) - Phase tracking & progress
- [**DECISIONS.md**](./DECISIONS.md) - Architectural decisions log
- [**README.md**](./README.md) - Project overview (100% validated)

### Architecture Documentation
- [System Architecture](./docs/architecture/) - Design patterns & decisions
- [API Contracts](./docs/architecture/api-contracts.md) - Endpoint specifications
- [Database Schema](./docs/architecture/database.md) - Data models

### Testing Documentation
- [Testing Strategy](./docs/testing/testing-strategy.md) - Comprehensive approach
- [Test Results](./docs/testing/) - Coverage reports
- [Validator Tests](./tests/unit/governance/) - 27/27 passing

### Governance Documentation
- [Governance Config](./governance/config.yaml) - Rules & settings
- [Validation Rules](./.docs-metadata/validation-rules.yaml) - Doc standards
- [Code Formats](./.docs-metadata/code-formats.yaml) - Code doc standards

## Current Status

### Active Development Phase
**Phase:** 1.6 - Documentation Updates
**Start Date:** September 3, 2025
**Target Completion:** September 4, 2025
**Progress:** 90% Complete

### Recent Achievements
- [x] Implemented documentation validation system (85% coverage)
- [x] Implemented code documentation validators (93% coverage)
- [x] Fixed heading hierarchy detection in validators
- [x] Achieved 100% validation score on README.md
- [x] Created central project.yaml configuration
- [x] All 27 validator tests passing

### In Progress
- [ ] Complete CLAUDE.md update (90% complete)
- [ ] Validate all documentation files
- [ ] Clear temp directory

### Next Milestones
1. **Hook Integration** (Sept 4-10)
2. **MCP Intelligence** (Sept 11-17)
3. **Production Readiness** (Sept 18-30)

## Team & Responsibilities

### Core Team
- **Owner:** Steven Holden (@sholden3) - Project leadership
- **Alex Novak:** Frontend & Integration Architect - Angular, Electron, TypeScript
- **Dr. Sarah Chen:** Backend & Infrastructure Architect - Python, FastAPI, Database

### Specialist Contributors
- **Isabella Martinez:** Documentation Standards
- **Marcus Thompson:** Quality Assurance
- **David Park:** Developer Experience
- **Wei Chen:** Performance Optimization
- **Raj Patel:** Security Architecture

## Contributing

### How to Contribute
1. Read [governance rules](./governance/config.yaml) - 95% compliance required
2. Check [current tasks](./TRACKER.md) for work items
3. Follow pre-commit validation workflow
4. Ensure temp/ directory is clean before commits
5. All code must have proper documentation (enforced!)

### Code Standards
- **Python:** Google docstring format, type hints required
- **TypeScript:** JSDoc comments, strict typing
- **Testing:** Minimum 85% coverage for new code
- **Documentation:** Must pass validators (score >70%)

## Support & Communication

### Internal Communication
- **GitHub Issues:** [https://github.com/sholden3/aiorchestration/issues](https://github.com/sholden3/aiorchestration/issues)
- **Documentation:** This file and linked resources
- **Governance Contact:** governance@system.local

### Issue Tracking
- **Bugs:** Create issue with 'bug' label
- **Features:** Create issue with 'enhancement' label
- **Documentation:** Create issue with 'documentation' label

## Security & Compliance

### Security Practices
- No hardcoded credentials (enforced by governance)
- All secrets in environment variables
- Security pattern detection in pre-commit
- Audit logging for all governance actions

### Compliance Requirements
- 95% minimum governance score
- All commits must pass validation
- No bypass mechanisms allowed
- Progressive enforcement for new rules

## Performance Benchmarks

### Current Performance Metrics
- **API Response Time:** ~120ms (Target: <100ms)
- **Hook Response Time:** Pending (Target: <50ms)
- **Validation Time:** <100ms per file (Target: Met ✅)
- **Test Execution:** <2 minutes (Target: Met ✅)

### Scalability Targets
- **Concurrent Users:** 1000+
- **Requests/Second:** 5000+
- **Database Connections:** 100 pooled

## Critical Governance Requirements

### ⚠️ MANDATORY RULES FOR AI ASSISTANTS

1. **NEVER proceed with architectural decisions without explicit approval**
2. **Session Management:** Follow start/end validation protocols
3. **Archival Rules:** All file replacements must follow strict procedures
4. **Cross-Validation:** Both core architects must approve changes
5. **Documentation Validation:** All docs must score >70%
6. **Code Documentation:** Language-specific standards enforced
7. **Test Coverage:** Maintain minimum coverage requirements
8. **No Simplification:** Testing changes require user approval

### Definition of Done
- [ ] Code written and documented
- [ ] Tests written and passing (>85% coverage)
- [ ] Documentation updated and validated
- [ ] Governance validation passing (>95% score)
- [ ] Temp directory clean
- [ ] Peer review completed
- [ ] Integration tests passing

## License & Legal

**License:** MIT License
**Copyright:** © 2025 AI Orchestration Team (Steven Holden). All rights reserved.
**Repository:** [https://github.com/sholden3/aiorchestration](https://github.com/sholden3/aiorchestration)

## Change Log

### Recent Changes
- **v2.1** (Sept 3, 2025): Documentation validation system implemented
- **v2.0** (Sept 2, 2025): Extreme governance system deployed
- **v1.9** (Sept 1, 2025): Archive recovery completed
- **v1.8** (Aug 31, 2025): Config-driven architecture

---

**Last Review:** September 3, 2025
**Next Review:** September 10, 2025
**Document Owner:** Steven Holden
**Reviewers:** Alex Novak, Dr. Sarah Chen

For detailed information on specific aspects of the project, please refer to the [Documentation Index](./DOCUMENTATION_INDEX.md).

---

*"The best architecture is code that works perfectly, fails gracefully, documents itself completely, and teaches the next developer exactly why every decision was made—especially when they're debugging it during a production crisis."*