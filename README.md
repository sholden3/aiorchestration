# Claude Research and Development

[![Build Status](https://img.shields.io/badge/build-passing-green)](https://github.com/sholden3/aiorchestration)
[![Governance](https://img.shields.io/badge/governance-95%25-brightgreen)](./governance/)
[![Test Coverage](https://img.shields.io/badge/validators-85--93%25-green)](./tests/)
[![Version](https://img.shields.io/badge/version-2.1-blue.svg)](./TRACKER.md)

> AI Development Assistant platform with extreme governance enforcement for code quality and documentation standards

[**📖 Full Documentation**](./CLAUDE.md) | [**📊 Current Status**](./STATUS.md) | [**📋 Task Tracker**](./TRACKER.md) | [**🎯 Decisions**](./DECISIONS.md)

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/sholden3/aiorchestration.git
cd aiorchestration

# Backend setup (Python FastAPI)
cd ai-assistant/backend
pip install -r requirements.txt
python main.py  # Runs on http://localhost:8000

# Frontend setup (Angular + Electron)
cd ai-assistant
npm install
npm start  # Angular on http://localhost:4200

# Run pre-commit hooks (governance)
git add .
git commit -m "Your message"  # Triggers validation
```

## 🏗️ Architecture

```
ClaudeResearchAndDevelopment/
├── ai-assistant/          # 🎯 Main application
│   ├── src/              # Angular frontend (TypeScript)
│   ├── backend/          # FastAPI backend (Python)
│   └── electron/         # Desktop app wrapper
├── governance/           # 🛡️ Extreme governance system
│   ├── validators/       # Doc & code validators (85-93% coverage)
│   ├── hooks/           # Pre-commit enforcement
│   └── config.yaml      # Governance configuration
├── .docs-metadata/      # 📐 Documentation standards
│   ├── validation-rules.yaml    # Markdown validation
│   └── code-formats.yaml       # Code doc standards
├── tests/               # 🧪 Test suites (27/27 passing)
├── docs/                # 📚 Project documentation
├── claude/              # 🤖 Claude-specific configs
└── temp/               # 🗂️ Development workspace
```

**Tech Stack:** Angular 17 • Python FastAPI • PostgreSQL • Redis • Electron • TypeScript • Jest • Pytest

## 📚 Documentation

| Document | Purpose | Status |
|----------|---------|--------|
| [**CLAUDE.md**](./CLAUDE.md) | 📖 Master AI instructions & requirements | ✅ Updated |
| [**STATUS.md**](./STATUS.md) | 📊 Real-time system health & metrics | ✅ Current |
| [**TRACKER.md**](./TRACKER.md) | 📋 Phase tracking & progress | ✅ Active |
| [**DECISIONS.md**](./DECISIONS.md) | 🎯 Architectural decisions log | ✅ Binding |
| [**Architecture Docs**](./docs/architecture/) | 🏗️ System design patterns | 📝 In Progress |
| [**Testing Strategy**](./docs/testing/) | 🧪 Test plans & coverage reports | ✅ 85%+ |

## 🛠️ Development

### Prerequisites
- Node.js 18+ (Frontend & Electron)
- Python 3.10+ (Backend & Validators)
- PostgreSQL 14+ (Optional - SQLite fallback)
- Redis 7+ (Optional - in-memory fallback)
- Git 2.0+ (Version control & hooks)

### Common Commands
```bash
# Development
npm run dev              # Start Angular dev server
python main.py          # Start FastAPI backend
npm run electron        # Launch Electron app

# Testing (85-93% coverage achieved for validators!)
pytest tests/ -xvs      # Run Python tests with coverage
npm test               # Run Angular/Jest tests
pytest tests/unit/governance/test_*_validator.py  # Run validator tests

# Governance & Quality
git commit             # Triggers pre-commit validation
python -m governance.validators.doc_validator README.md  # Validate docs
python -m governance.validators.code_doc_validator main.py  # Check code docs

# Production
npm run build          # Build Angular for production
docker-compose up      # Full stack deployment
```

### 🎉 Recent Achievements (Sept 3, 2025)

### Documentation Validation System ✅
- Implemented `governance/validators/doc_validator.py`
- 85% test coverage with 13 tests passing
- Progressive enforcement: warnings → blocks
- Integrated into pre-commit hooks

### Code Documentation Standards ✅
- Implemented `governance/validators/code_doc_validator.py`
- 93% test coverage with 14 tests passing
- Language-specific rules for Python/TypeScript/JavaScript
- Automatic docstring/JSDoc validation

### Contributing
1. Read [Governance Rules](./governance/config.yaml) - 95% compliance required!
2. Check [Current Tasks](./TRACKER.md) for work items
3. Follow development workflow with pre-commit validation
4. Ensure temp/ directory is clean before commits
5. All code must have proper documentation (enforced!)

## 📞 Support

- **📖 Documentation:** [Complete Guide](./CLAUDE.md)
- **🐛 Issues:** [GitHub Issues](https://github.com/sholden3/aiorchestration/issues)
- **💬 Discussions:** Use [Round-table Format](./temp/) for architectural decisions
- **🏛️ Governance:** Alex Novak (Frontend) & Dr. Sarah Chen (Backend)
- **📧 Contact:** governance@system.local

## 📄 License

MIT License

Copyright (c) 2025 AI Orchestration Team (Steven Holden)

---
**Project Status:** 🟢 OPERATIONAL | **Phase:** 1.6 Documentation Updates | **Last Updated:** Sept 3, 2025 | **[📑 Documentation Index](./DOCUMENTATION_INDEX.md)**