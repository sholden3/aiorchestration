# AI Orchestration System - Claude Code Documentation

## Project Overview
Advanced AI orchestration system with three-persona governance, intelligent caching, and multi-tenant support. Built with evidence-based development and zero-tolerance quality enforcement.

## Quick Start
```bash
cd ai-assistant/backend
python -m pytest -v  # Run all tests
python main.py       # Start backend service
```

## Three-Persona Governance Model

### 🤖 Dr. Sarah Chen - AI Integration
- Claude API optimization and integration
- Prompt engineering and persona management
- Token usage optimization

### ⚙️ Marcus Rodriguez - Systems Performance  
- Database architecture and caching
- Performance optimization
- Infrastructure reliability

### 🎨 Emily Watson - UX/Frontend
- Terminal interface design
- User experience optimization
- Accessibility features

## Development Protocols

### Evidence-Based Requirements
- NO assumptions without proof
- ALL metrics from actual execution
- EVERY claim requires evidence
- CROSS-VALIDATION mandatory

### Anti-Hallucination Rules
```bash
# Before any claim, execute:
python -m pytest --collect-only  # Verify tests exist
python -m pytest -v              # Run actual tests
grep -rn "TODO\|FIXME" .        # Check for incomplete code
```

## Architecture

### System Components
- **Orchestrator**: Multi-tenant agent coordination
- **Cache**: Three-tier (Hot/Warm/Cold) intelligent caching
- **Databases**: 7 specialized types for different data patterns
- **PTY Manager**: Terminal session management
- **Rules Engine**: Assumption prevention system

### Key Files
```
ai-assistant/backend/
├── orchestrator.py          # Main orchestration engine
├── cache_manager.py         # Three-tier cache implementation
├── persona_manager.py       # Three-persona management
├── claude_integration.py    # Claude CLI integration
├── database_manager.py      # PostgreSQL + mock fallback
├── test_orchestration.py    # Comprehensive test suite
└── config.py               # Three-persona configuration
```

## Testing Commands

### Run All Tests
```bash
python -m pytest -v
```

### Run Specific Test Categories
```bash
# AI Integration Tests (Dr. Sarah Chen)
python -m pytest test_orchestration.py::TestAIIntegration -v

# Performance Tests (Marcus Rodriguez)
python -m pytest test_orchestration.py::TestSystemsPerformance -v

# UX Tests (Emily Watson)
python -m pytest test_orchestration.py::TestUXFrontend -v

# Cross-Persona Orchestration Tests
python -m pytest test_orchestration.py::TestOrchestration -v
```

### Skip Known Failures
```bash
python -m pytest -v -k "not test_cache_hot_cold_tiers and not test_cache_database_integration and not test_complete_user_journey"
```

## Configuration

### Environment Variables
```bash
# Optional - falls back to config then CLI
ANTHROPIC_API_KEY=your_key

# Database (optional - uses mock if unavailable)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_orchestration
```

### Cascading Authentication
1. Check `ANTHROPIC_API_KEY` environment variable
2. Check `config.ai.anthropic_api_key`
3. Fall back to Claude CLI (requires Claude Code)

## Quality Standards

### Mandatory Validation
```bash
# Check for magic variables
grep -rn "localhost\|127.0.0.1\|hardcoded" --include="*.py" .

# Verify no pass statements
grep -rn "pass$" --include="*.py" .

# Check test coverage
python -m pytest --cov=. --cov-report=term-missing
```

### Performance Targets
- Cache hit rate: >90%
- Token reduction: >65%
- Response time: <500ms
- Test pass rate: >95%

## Common Issues & Solutions

### Issue: Tests failing with PersonaType error
```python
# Wrong:
PersonaType.SYSTEMS_PERFORMANCE

# Correct:
PersonaType.MARCUS_RODRIGUEZ
```

### Issue: Cache not evicting items
```python
# Solution: Check both size and count limits
if (self.current_hot_size + entry.size <= self.max_hot_size and 
    len(self.hot_cache) < MAX_HOT_ITEMS):
```

### Issue: Mock database missing methods
```python
# Add missing methods to MockConnection:
async def fetchrow(self, query, *args):
    return None
```

## Development Workflow

### 1. Pre-Implementation Validation
```bash
# Verify current state
python -m pytest --collect-only
grep -rn "TODO\|FIXME" .
```

### 2. Implementation with Evidence
- Write code with full implementation (no placeholders)
- Add comprehensive tests
- Document business logic

### 3. Post-Implementation Validation
```bash
# Run tests
python -m pytest -v

# Check quality
grep -rn "pass$\|NotImplemented" .

# Verify no magic variables
grep -rn "localhost\|hardcoded" .
```

## Governance Enforcement

### Cross-Persona Validation Required
Every change must be validated by all three personas:
- Sarah validates AI integration impact
- Marcus validates performance impact
- Emily validates user experience impact

### Evidence Requirements
- Performance claims need measurement tools
- Integration claims need API execution
- UX claims need interface testing

## Next Steps

### Priority Tasks
1. Fix remaining 3 test failures
2. Implement specialized cache strategies
3. Build frontend UI (currently only Electron shell)
4. Install pytest-cov for coverage metrics

### Long-term Goals
- Complete PostgreSQL integration
- Implement full frontend dashboard
- Add real-time metrics visualization
- Deploy production-ready system

---

**Remember**: This is an evidence-based project. No assumptions, no hallucinations, only proven facts.