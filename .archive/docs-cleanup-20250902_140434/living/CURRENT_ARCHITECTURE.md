---
governance:
  correlation_id: CorrelationContext(correlation_id='c97b0a58-4020-4eb8-a91c-1b5d8ffbc6f2', parent_correlation_id=None, session_id=None, user='Steven Holden', operation_type='git.pre_commit', operation_name='pre_commit_validation', start_time=datetime.datetime(2025, 8, 29, 18, 52, 4, 328681), end_time=None, status=<OperationStatus.IN_PROGRESS: 'in_progress'>, metadata={'user': 'Steven Holden', 'branch': 'main', 'files': ['governance-config/governance-rules.yml', 'governance/scripts/integrated_pre_commit_hook.py', 'governance/validators/domain_validators.py']}, debug_trace=['[2025-08-29T18:52:04.328681] Correlation created for git.pre_commit:pre_commit_validation'], events=[], errors=[], warnings=[], checkpoints={}, metrics={})
  P25-08-29T18:50:54.647971Z
  P25-09-05T18:50:54.647971Z
  validation_schema: v1.0
  auto_sections: [component_status, integration_health, performance_metrics]
  manual_sections: [architecture_decisions, risk_assessment]
  phase_group: PHOENIX_RISING
  phase_number: 1
---

# Current System Architecture
<!-- LIVING DOCUMENT - MUST REMAIN CURRENT -->

## Overview
This document reflects the **actual current state** of the system architecture, not the intended or planned state. It is automatically validated and must be updated whenever architectural changes are made.

## Component Status
<!-- AUTO-GENERATED - DO NOT EDIT -->
Last scan: 2025-08-29T15:35:33Z
Total components: 15
Active: 12
Mocked: 3
Deprecated: 0
<!-- END AUTO-GENERATED -->

## System Components

### Backend Services (Python/FastAPI)
| Component | Status | Mock/Real | Version | Last Updated | Notes |
|-----------|--------|-----------|---------|--------------|-------|
| FastAPI Server | ✅ Active | Real | 2.0 | 2025-08-29 | Port 8000, async |
| Cache Manager | ✅ Active | Real | 1.5 | 2025-08-29 | Two-tier (hot/warm) |
| WebSocket Manager | ✅ Active | Real | 1.0 | 2025-08-28 | Needs connection limits |
| Database Manager | ✅ Active | Mock/Real | 1.2 | 2025-08-29 | PostgreSQL with fallback |
| Agent Terminal Manager | ⚠️ Active | Mock | 0.5 | 2025-08-27 | Returns simulated responses |
| Persona Manager | ✅ Active | Real | 1.0 | 2025-08-28 | 3 personas active |
| Orchestration Service | ✅ Active | Real | 1.1 | 2025-08-29 | Coordinates all services |
| Governance System | ✅ Active | Real | 1.0 | 2025-08-29 | Pre-commit hooks active |

### Frontend Services (Angular/Electron)
| Component | Status | Mock/Real | Version | Last Updated | Notes |
|-----------|--------|-----------|---------|--------------|-------|
| Angular App | ✅ Active | Real | 17.0 | 2025-08-29 | Material Design UI |
| Electron Wrapper | ✅ Active | Real | 1.0 | 2025-08-28 | Desktop application |
| IPC Service | ✅ Active | Real | 1.2 | 2025-08-29 | 58% test coverage |
| Terminal Service | ⚠️ Active | Partial | 1.1 | 2025-08-29 | Memory leak fixed, 12% tests pass |
| WebSocket Service | ✅ Active | Real | 1.0 | 2025-08-27 | Real-time updates |
| Dashboard Component | ✅ Active | Real | 1.0 | 2025-08-27 | Metrics visualization |

### Infrastructure Services
| Component | Status | Mock/Real | Version | Last Updated | Notes |
|-----------|--------|-----------|---------|--------------|-------|
| PostgreSQL | ⚠️ Optional | Real | 14+ | 2025-08-27 | Falls back to mock if unavailable |
| Git Hooks | ✅ Active | Real | 1.0 | 2025-08-29 | Integrated governance |
| CI/CD Pipeline | ❌ Planned | - | - | - | GitHub Actions planned |
| Monitoring | ❌ Planned | - | - | - | Prometheus/Grafana planned |

## Integration Points

### Critical Integrations
1. **Frontend ↔ Backend**: REST API on port 8000, WebSocket for real-time
2. **Backend ↔ Database**: PostgreSQL with asyncpg, mock fallback
3. **Frontend ↔ Electron**: IPC bridge with context isolation
4. **Git ↔ Governance**: Pre-commit hooks validate all changes
5. **Cache ↔ Services**: All services use centralized cache manager

### Integration Health
<!-- AUTO-GENERATED - DO NOT EDIT -->
| Integration | Status | Latency | Error Rate | Last Check |
|-------------|--------|---------|------------|------------|
| REST API | ✅ Healthy | 45ms | 0.1% | 2025-08-29T15:35:00Z |
| WebSocket | ✅ Healthy | 5ms | 0.0% | 2025-08-29T15:35:00Z |
| Database | ⚠️ Degraded | 120ms | 2.5% | 2025-08-29T15:35:00Z |
| Cache | ✅ Healthy | 2ms | 0.0% | 2025-08-29T15:35:00Z |
| IPC | ✅ Healthy | 10ms | 0.5% | 2025-08-29T15:35:00Z |
<!-- END AUTO-GENERATED -->

## Performance Metrics
<!-- AUTO-GENERATED - DO NOT EDIT -->
- API Response Time (p95): 487ms
- Cache Hit Rate: 91.2%
- WebSocket Messages/sec: 127
- Memory Usage: 512MB (backend), 256MB (frontend)
- CPU Usage: 15% average, 45% peak
<!-- END AUTO-GENERATED -->

## Architecture Decisions
<!-- MANUAL - REQUIRES REVIEW -->

### Recent Changes
1. **2025-08-29**: Converted Terminal Service from module singleton to component-scoped (C1 fix)
2. **2025-08-29**: Added governance system with pre-commit hooks
3. **2025-08-28**: Implemented two-tier cache system
4. **2025-08-27**: Added WebSocket manager for real-time updates

### Current Architectural Patterns
- **Backend**: Async FastAPI with dependency injection
- **Frontend**: Component-based Angular with lazy loading
- **IPC**: Context bridge pattern for security
- **Caching**: Two-tier (hot/warm) with LRU eviction
- **Governance**: Hook-based validation with exemptions

## Risk Assessment
<!-- MANUAL - REQUIRES REVIEW -->

### High Risk Areas
1. **WebSocket Connection Limits**: Not enforced, could exhaust resources (H1)
2. **Terminal Integration**: Currently mocked, no real PTY connection
3. **Database Race Condition**: Initialization not fully thread-safe (H3)

### Technical Debt
1. **Mock Implementations**: Agent Terminal Manager, partial Terminal Service
2. **Test Coverage**: IPC at 58%, Terminal at 12%
3. **Missing Features**: CI/CD pipeline, monitoring, real AI integration

## Dependencies

### External Dependencies
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+ (optional)
- Git 2.0+

### Key Package Versions
- FastAPI: 0.104.0
- Angular: 17.0.0
- Electron: 27.0.0
- asyncpg: 0.29.0

## Deployment Architecture

### Current Deployment
- **Development**: Local development environment
- **Testing**: Local with mock services
- **Production**: Not deployed

### Future Deployment Plan
- **Development**: Docker Compose
- **Staging**: Kubernetes on AWS EKS
- **Production**: Multi-region Kubernetes with CDN

---

## Validation Checklist
- [ ] All components listed with current status
- [ ] Mock vs Real clearly indicated
- [ ] Integration points documented
- [ ] Performance metrics current (within 24 hours)
- [ ] Risk assessment updated
- [ ] Technical debt tracked

---

*This is a living document. It must be updated whenever architectural changes are made.*
*Stale information in this document is a governance violation.*