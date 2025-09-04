# Backend Service

> Python FastAPI backend providing REST API, WebSocket connections, and business logic for the AI Assistant

**Parent Project:** AI Orchestration Platform | [**📖 Main Docs**](../../CLAUDE.md) | [**🏗️ Architecture**](../../docs/architecture/backend.md)

## Overview

The backend service is the core processing engine of the AI Orchestration Platform, built with Python FastAPI. It provides RESTful APIs, WebSocket connections for real-time communication, database management with circuit breaker patterns, and integration with the governance system for code quality and compliance enforcement.

### Key Features
- High-performance async REST API with FastAPI
- Real-time WebSocket communication for live updates
- Two-tier caching system (Redis + in-memory)
- Circuit breaker pattern for database resilience
- Comprehensive governance integration
- PostgreSQL with SQLite fallback

## Structure

```
backend/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── database_service.py  # Database connections with circuit breaker
├── cache_manager.py     # Two-tier caching implementation
├── websocket_manager.py # WebSocket connection management
├── orchestrator.py      # Service coordination layer
├── api_endpoints.py     # REST API endpoints
├── models/              # Database and Pydantic models
├── tests/              # Test suite
└── requirements.txt    # Python dependencies
```

## Quick Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ (optional, SQLite fallback available)
- Redis 7+ (optional, in-memory fallback available)

### Installation
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run application
python main.py
```

## Development

### Local Development
```bash
# Run with auto-reload
uvicorn main:app --reload --port 8000

# Run with debug logging
python main.py --debug

# Run with custom config
python main.py --config config.dev.yaml
```

### Testing
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests  
pytest tests/integration/ -v

# Coverage report
pytest --cov=. --cov-report=html --cov-fail-under=85
```

### Building
```bash
# Development build
pip install -e .

# Production build
python setup.py bdist_wheel
```

## Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///./app.db` |
| `REDIS_URL` | Redis connection string | `memory://` |
| `API_PORT` | API server port | `8000` |
| `WEBSOCKET_PORT` | WebSocket port | `8001` |
| `CIRCUIT_BREAKER_THRESHOLD` | Failure threshold | `5` |
| `CACHE_TTL` | Cache time-to-live (seconds) | `300` |

### Configuration Files
- `config.yaml` - Main configuration file
- `governance/config.yaml` - Governance rules
- `.env` - Environment-specific settings

## API/Interface

### Key Endpoints
- **POST /api/chat** - Process chat messages
- **GET /api/status** - System health status
- **POST /api/validate** - Code validation
- **GET /api/metrics** - Performance metrics
- **WebSocket /ws** - Real-time updates

### Integration Points
- **Frontend:** REST API and WebSocket connections
- **Database:** PostgreSQL with automatic fallback to SQLite
- **Cache:** Redis with automatic fallback to in-memory
- **Governance:** Pre-commit validation hooks
- **Monitoring:** Prometheus metrics export

## Troubleshooting

### Common Issues
1. **Database Connection Failures**
   - **Symptom:** Circuit breaker open, requests failing
   - **Solution:** Check PostgreSQL status, fallback to SQLite active

2. **High Memory Usage** 
   - **Symptom:** Memory consumption over 2GB
   - **Solution:** Reduce cache TTL, check for WebSocket leaks

3. **Slow API Response**
   - **Symptom:** Response time >500ms
   - **Solution:** Check cache hit rate, optimize database queries

### Debugging
```bash
# Debug mode with verbose logging
python main.py --log-level DEBUG

# Check logs
tail -f logs/backend.log

# Monitor circuit breaker
python -m backend.monitor_circuit_breaker

# Profile performance
python -m cProfile -o profile.stats main.py
```

## Related Documentation

- [**Architecture**](../../docs/architecture/backend.md) - Detailed backend design
- [**Testing**](../../docs/testing/unit-tests.md) - Testing documentation  
- [**API Docs**](../../docs/architecture/api-contracts.md) - API specifications
- [**Database Schema**](../../docs/architecture/database.md) - Database design

---

**Component Owner:** Dr. Sarah Chen | **Last Updated:** Sept 3, 2025 | **Status:** ✅ Operational