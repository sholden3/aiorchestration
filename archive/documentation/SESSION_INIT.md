# AUTO-INJECTED SESSION CONTEXT
## AI Orchestration System - Development Environment

Welcome! You are now working on the **AI Orchestration System** that unifies three projects:
- `cache_optimizer_project/` - Backend caching and optimization
- `UltimateClaude/` - AI persona orchestration
- `ClaudeUI/` - Electron/Angular frontend

---

## 🚨 ACTIVE PROJECT RULES (ENFORCED)

1. **No Silent Assumptions** - All business logic must be explicitly validated
2. **Performance Boundaries** - Operations must complete within: 
   - API calls: <500ms (P95)
   - Cache operations: <10ms (hot), <100ms (cold)
   - Memory usage: <2GB steady state
3. **Cache Invalidation** - Every cache write must define invalidation conditions
4. **Multi-Tenancy Isolation** - No cross-tenant data access ever
5. **AI Error Handling** - Every Claude call needs fallback behavior

---

## 📊 CURRENT IMPLEMENTATION STATUS

### Phase Progress
- ✅ Phase 1: Foundation Architecture - **PLANNING**
- ⏳ Phase 2: Cache System Optimization - **NOT STARTED**
- ⏳ Phase 3: AI Integration & Personas - **NOT STARTED**
- ⏳ Phase 4: Frontend/PTY Integration - **NOT STARTED**
- ⏳ Phase 5: Testing & Validation - **NOT STARTED**
- ⏳ Phase 6: Production Hardening - **NOT STARTED**

### Critical Issues Requiring Immediate Attention
1. **No connection pooling** - Database will crash under load
2. **Mock PTY implementation** - Terminal doesn't actually work
3. **Unverified token savings** - Claims 70-90% but never measured
4. **Memory leaks** - Cache grows unbounded
5. **No Claude integration** - All AI calls are mocked

---

## 🎭 AVAILABLE PERSONAS

### Dr. Sarah Chen - AI/Claude Integration
- **Expertise**: Claude API, token optimization, assumption elimination
- **Trigger**: AI integration, Claude hooks, persona management
- **Current Focus**: Implement real Claude integration with fallbacks

### Marcus Rodriguez - Python Systems & Performance
- **Expertise**: Caching, database optimization, performance tuning
- **Trigger**: Cache, performance, database, optimization
- **Current Focus**: Fix connection pooling and cache invalidation

### Emily Watson - Angular/PTY/UX
- **Expertise**: Frontend, PTY integration, user experience
- **Trigger**: UI, frontend, terminal, PTY, UX
- **Current Focus**: Replace mock PTY with real implementation

---

## 🗺️ QUICK FILE NAVIGATION

### Most Important Files to Know
```
cache_optimizer_project/
  src/cache/dual_cache_production.py     # Lines 79-150: Cache core logic (needs simplification)
  src/database/database_manager.py       # Lines 1-50: Missing connection pooling!
  src/claude_enhanced_integration.py     # Lines 62-100: Token savings calculation

UltimateClaude/
  persona_orchestrator.py                # Lines 301-400: Persona activation (not implemented)

ClaudeUI/
  electron-main.js                       # Lines 73-120: Mock PTY (needs real implementation)
  src/app/app.module.ts                  # Lines 1-44: 44 Material imports (only need 5)
```

### Where to Make Changes
| Task | File | Section |
|------|------|---------|
| Add connection pooling | `database_manager.py` | Lines 1-50 |
| Implement real PTY | `electron-main.js` | Lines 73-120 |
| Simplify cache | `dual_cache_production.py` | Entire file |
| Real Claude integration | `claude_enhanced_integration.py` | Lines 62-300 |
| Reduce UI complexity | `app.module.ts` | Lines 1-44 |

---

## 📋 AVAILABLE COMMANDS

### Project Status Commands
- `check-assumptions` - Validate all business logic assumptions
- `check-performance` - Run performance benchmarks
- `check-rules` - Verify rule compliance
- `show-metrics` - Display current system metrics

### Documentation Commands
- `show-roadmap` - Display implementation roadmap
- `show-files` - Show file mapping index
- `show-testing` - Display testing framework
- `show-improvements` - Show design improvements

### Development Commands
```bash
# Backend (Python)
cd cache_optimizer_project
python -m pytest tests/           # Run tests
python scripts/orchestrator.py    # Use cache-aware operations

# Frontend (Angular/Electron)
cd ClaudeUI
npm run electron:serve            # Development mode
npm test                          # Run tests

# Personas
cd UltimateClaude
python persona_orchestrator.py    # Test persona system
```

---

## ⚠️ CRITICAL ASSUMPTIONS TO VALIDATE

These assumptions are currently UNVALIDATED and could cause system failure:

1. **Database Response Times**: SQLite completes queries <50ms (95th percentile)
2. **Memory Usage**: App stays under 2GB during normal operation
3. **Claude API**: 99% uptime with <30 second response time
4. **Token Savings**: Cache reduces tokens by 40-60%
5. **PTY Stability**: Terminal sessions stable for 8+ hours on Windows
6. **Cache Hit Rate**: 85% for hot cache operations

---

## 🔧 DEVELOPMENT PROTOCOLS

### Before Making Changes
1. Check `FILE_MAPPING_INDEX.md` for file locations and dependencies
2. Review `BUSINESS_RULES_ASSUMPTIONS.md` for constraints
3. Validate assumptions that could affect your changes

### When Implementing
1. Follow the phase plan in `IMPLEMENTATION_ROADMAP.md`
2. Add tests according to `TESTING_FRAMEWORK.md`
3. Consider improvements from `DESIGN_IMPROVEMENTS.md`

### After Implementation
1. Run all relevant tests
2. Update metrics and validate assumptions
3. Document any new assumptions or rules

---

## 🚀 IMMEDIATE PRIORITIES (Week 1)

Based on the three-persona analysis, these need immediate attention:

1. **[CRITICAL]** Implement database connection pooling
   - File: `src/database/database_manager.py`
   - Risk: System will crash under any real load
   
2. **[CRITICAL]** Add memory limits to cache
   - File: `src/cache/dual_cache_production.py`
   - Risk: Out of memory errors within hours

3. **[HIGH]** Replace mock PTY with real implementation
   - File: `ClaudeUI/electron-main.js`
   - Risk: Core functionality doesn't work

4. **[HIGH]** Implement real Claude API integration
   - File: `src/claude_enhanced_integration.py`
   - Risk: No actual AI functionality

5. **[MEDIUM]** Remove unused Angular Material modules
   - File: `ClaudeUI/src/app/app.module.ts`
   - Risk: 8MB bundle size slows everything

---

## 📊 CURRENT METRICS (BASELINE)

```
Performance Metrics:
- Response Time (P95): Unknown (not measured)
- Memory Usage: Growing unbounded
- Cache Hit Rate: Unknown (claims 85% unverified)
- Token Savings: Claimed 70-90% (unverified)
- Bundle Size: 8MB (target: 2MB)
- Error Rate: Unknown (no monitoring)

Code Quality:
- Test Coverage: ~30% (target: 90%)
- Type Safety: Partial (many any types)
- Documentation: Sparse
- Technical Debt: High

System Health:
- Database Connections: No pooling (will exhaust)
- Memory Leaks: Confirmed in cache
- Error Recovery: None
- Monitoring: None
```

---

## 🎯 SUCCESS CRITERIA

You're successful when:
1. ✅ All tests pass (90% coverage)
2. ✅ Performance meets targets (<500ms P95)
3. ✅ Memory stays under 2GB
4. ✅ Cache hit rate >85% (measured, not claimed)
5. ✅ Real PTY and Claude integration working
6. ✅ No silent failures or unvalidated assumptions

---

## 💡 TIPS FOR THIS SESSION

1. **Use the File Mapping** - Don't waste time searching for files
2. **Check Assumptions** - Many current assumptions are wrong
3. **Test Everything** - The existing code has hidden bugs
4. **Measure, Don't Assume** - Verify all performance claims
5. **Simple > Complex** - The 3-tier cache should be 2-tier

---

## 🔗 RELATED DOCUMENTATION

All documentation is in the project root:
- `IMPLEMENTATION_ROADMAP.md` - Detailed phase plan
- `FILE_MAPPING_INDEX.md` - Complete file navigation
- `BUSINESS_RULES_ASSUMPTIONS.md` - Rules and validations
- `TESTING_FRAMEWORK.md` - Testing requirements
- `DESIGN_IMPROVEMENTS.md` - Architecture improvements

---

## 🤝 COLLABORATION NOTES

The three personas (Sarah, Marcus, Emily) have identified these integration points:
- Cache → UI: Performance metrics need dashboard
- AI → Backend: Token optimization requires cache integration  
- Frontend → Backend: WebSocket needed for real-time updates

---

*This context is auto-injected when Claude Code starts in this directory. It provides everything needed for immediate productivity. Type 'show-roadmap' to see the full implementation plan.*

---

**SESSION INITIALIZED** - Ready for AI Orchestration System development
**Current Directory**: ClaudeResearchAndDevelopment/
**Active Rules**: 5 critical rules enforced
**Available Personas**: 3 expert personas ready
**Documentation**: 5 comprehensive guides loaded

Type any command or start developing. All context is loaded and ready.