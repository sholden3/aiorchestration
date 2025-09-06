# Backend Architecture

**Last Updated:** 2025-09-03  
**Reviewed By:** Dr. Sarah Chen  
**Next Review:** 2025-10-01  

## Overview
The backend architecture is built on Python FastAPI, emphasizing high performance, asynchronous operations, and robust error handling. The design prioritizes scalability, maintainability, and governance compliance while providing real-time capabilities through WebSockets.

## Technology Stack
### Runtime Environment
- **Language:** Python 3.10+
- **Framework:** FastAPI 0.104+
- **Server:** Uvicorn ASGI server
- **Package Manager:** pip/poetry

### Core Dependencies
- **Database ORM:** SQLAlchemy 2.0 with async support
- **Authentication:** PyJWT for token management
- **Validation:** Pydantic for data validation
- **Testing:** Pytest with async support
- **Documentation:** Auto-generated OpenAPI/Swagger

### Infrastructure
- **Containerization:** Docker with multi-stage builds
- **Process Manager:** Systemd/Supervisor
- **Reverse Proxy:** Nginx for static files
- **Load Balancer:** HAProxy for horizontal scaling

## Service Architecture
### Architectural Approach
Modular monolith with service-oriented design. Chosen for initial simplicity with clear boundaries for future microservices extraction if needed. Each module is self-contained with its own models, services, and endpoints.

### Core Services
- **API Service:** RESTful endpoints and request handling
- **WebSocket Service:** Real-time bidirectional communication
- **Validation Service:** Code and documentation validation
- **Cache Service:** Two-tier caching (Redis + in-memory)
- **Database Service:** Connection management with circuit breaker
- **Orchestrator Service:** Service coordination and workflow management
- **Governance Service:** Compliance checking and enforcement
- **MCP Governance Server:** Proactive governance consultation via Model Context Protocol
- **Hook Bridge Service:** Claude Code hook integration for pre-execution validation
- **Port Discovery Service:** Dynamic port allocation and service discovery

## Design Patterns
### Applied Patterns
- **Circuit Breaker:** Database connection resilience
- **Repository Pattern:** Data access abstraction
- **Service Layer:** Business logic encapsulation
- **Dependency Injection:** FastAPI's built-in DI
- **Observer Pattern:** WebSocket event broadcasting
- **Strategy Pattern:** Multiple cache/database backends

### Architectural Principles
- Separation of concerns with clear module boundaries
- Async-first design for maximum concurrency
- Fail-fast with comprehensive error handling
- Configuration-driven behavior
- Immutable infrastructure mindset

## File Structure
```
apps/api/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── models/                # Database and Pydantic models
│   ├── __init__.py
│   ├── user.py
│   ├── chat.py
│   └── validation.py
├── services/              # Business logic services
│   ├── __init__.py
│   ├── api_service.py
│   ├── websocket_service.py
│   ├── cache_service.py
│   └── database_service.py
├── endpoints/             # API route handlers
│   ├── __init__.py
│   ├── auth.py
│   ├── chat.py
│   └── validation.py
├── middleware/            # Request/response middleware
│   ├── __init__.py
│   ├── auth.py
│   ├── cors.py
│   └── logging.py
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── circuit_breaker.py
│   └── validators.py
├── mcp/                   # MCP governance integration
│   ├── __init__.py
│   ├── governance_server.py    # MCP server implementation
│   ├── claude_code_hook_bridge.py  # Hook bridge
│   ├── hook_handlers.py        # Hook entry points
│   ├── mcp_http_server.py      # HTTP interface
│   ├── port_integration.py     # Port discovery
│   ├── config_loader.py        # Configuration management
│   ├── database_schema.sql     # MCP database schema
│   └── enterprise_managed_settings.json
├── migrations/            # Database migrations
│   └── alembic/
└── tests/                # Test suites
    ├── unit/
    └── integration/
```

## Performance Considerations
### Scalability
- Horizontal scaling with load balancer
- Connection pooling for database (100 connections)
- Redis cluster support for distributed caching
- Background task queue with Celery (planned)

### Optimization
- Query optimization with proper indexing
- Response caching with 5-minute TTL
- Static file serving via CDN/Nginx
- Database query result caching
- Lazy loading for large datasets
- Pagination for list endpoints

## Error Handling
### Exception Hierarchy
- `BaseAPIException`: Root exception class
- `ValidationException`: Input validation errors
- `AuthenticationException`: Auth failures
- `AuthorizationException`: Permission denied
- `DatabaseException`: Database errors
- `CircuitBreakerException`: Circuit breaker open
- `ExternalServiceException`: Third-party failures

### Retry Logic
- Exponential backoff for transient failures
- Circuit breaker with 5-failure threshold
- Fallback to cache for read operations
- Graceful degradation for non-critical features

## Integration Points
### External APIs
- GitHub API for repository integration
- Claude API for AI capabilities (planned)
- Monitoring services (Prometheus/Grafana)
- Email service for notifications

### Internal Services
- WebSocket for real-time updates
- Redis pub/sub for event broadcasting
- PostgreSQL for persistent storage
- In-memory cache for hot data

## Security Architecture
### Authentication & Authorization
- JWT-based authentication with RS256
- Role-Based Access Control (RBAC)
- API key authentication for services
- Session management with Redis

### Data Protection
- TLS 1.3 for transport encryption
- AES-256 for data at rest
- PII field encryption in database
- Security headers (CORS, CSP, etc.)
- SQL injection prevention via ORM
- Input sanitization and validation

## Monitoring & Observability
### Logging
- Structured JSON logging
- Centralized log aggregation (ELK stack)
- 30-day retention policy
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Metrics
- Request/response times (P50, P95, P99)
- Error rates by endpoint
- Database query performance
- Cache hit/miss ratios
- WebSocket connection count
- Circuit breaker status

### Tracing
- OpenTelemetry integration
- Distributed request tracing
- Performance profiling
- Error tracking with Sentry

## Deployment Architecture
### Environments
- **Development:** Local Docker compose
- **Staging:** Kubernetes cluster (mirror of production)
- **Production:** Multi-region Kubernetes deployment
- **DR Site:** Standby environment for disaster recovery

### Container Strategy
- Multi-stage Docker builds for optimization
- Non-root user execution
- Security scanning with Trivy
- Image signing for supply chain security
- Alpine-based images for minimal footprint

## Migration Strategy
### Database Migrations
- Alembic for schema versioning
- Forward-only migrations
- Backup before migration
- Blue-green deployment for zero downtime

### Code Migrations
- Feature flags for gradual rollout
- API versioning for breaking changes
- Backward compatibility for 2 versions
- Canary deployments for risk mitigation

## Future Considerations
### Planned Improvements
- GraphQL endpoint addition
- gRPC for internal services
- Event sourcing for audit trail
- CQRS for read/write separation
- Service mesh implementation

### Scalability Roadmap
- Microservices extraction (Q2 2026)
- Kubernetes autoscaling
- Global CDN deployment
- Database sharding strategy
- Multi-region active-active setup

---

## MCP Governance Integration

### Overview
The MCP (Model Context Protocol) integration enables proactive governance consultation, allowing Claude Code to query governance decisions BEFORE executing operations rather than validating after execution.

### Key Components
- **Governance Server**: Core MCP server providing governance intelligence
- **Hook Bridge**: Integrates with Claude Code's native hooks (PreToolUse, UserPromptSubmit, PostToolUse)
- **HTTP Interface**: FastAPI server bridging hooks to MCP protocol
- **Port Discovery**: Dynamic port allocation preventing conflicts
- **Configuration Loader**: Hierarchical configuration with environment substitution

### Performance Characteristics
- Response time: <50ms with caching (85% cache hit rate)
- Concurrent consultations: 100+ tested
- Circuit breaker: 5-failure threshold
- Timeout: 5 seconds (configurable)

### Security Model
- Input validation and sanitization
- API key authentication for services
- Correlation ID tracking for audit
- Fail-open strategy with warnings

For detailed MCP documentation, see [MCP Architecture](./mcp/README.md)

## Change Log
| Date | Change | Author | Impact |
|------|--------|--------|--------|
| 2025-01-06 | Added MCP governance integration | Alex Novak & Dr. Sarah Chen | Major |
| 2025-01-06 | Updated file structure with MCP components | Emergency Remediation | Major |
| 2025-09-03 | Complete architecture documentation | Dr. Sarah Chen | Major |
| 2025-09-01 | Added circuit breaker pattern | Dr. Sarah Chen | Minor |
| 2025-08-30 | Initial backend design | Dr. Sarah Chen | Major |

## References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Async Best Practices](https://docs.python.org/3/library/asyncio.html)
- [12 Factor App](https://12factor.net/)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)