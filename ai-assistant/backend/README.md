# Backend Service

## Purpose
Python FastAPI backend providing REST API, WebSocket connections, and business logic for the AI Assistant.

## Contents
- Core Python modules for API endpoints
- Database service with circuit breaker pattern
- WebSocket manager for real-time updates
- Configuration management
- Persona and governance integration

## Dependencies
- FastAPI framework
- asyncpg for PostgreSQL
- WebSocket support
- PyYAML for configuration
- Circuit breaker for resilience

## Testing
- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`
- Coverage requirement: 85% minimum

## Maintenance
- Monitor circuit breaker status
- Review API performance metrics
- Update dependencies quarterly
- Database connection pool tuning