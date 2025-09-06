# Architecture Documentation

> Comprehensive system architecture documentation for the AI Development Assistant

**Parent Project:** AI Development Assistant | [**📖 Main Docs**](../../CLAUDE.md) | [**🏗️ Architecture Overview**](../../docs/architecture/)

## Overview

This directory contains detailed architectural documentation for all system components of the AI Development Assistant. The documentation follows a structured approach with separate documents for each major architectural domain, providing comprehensive coverage of the system design, security considerations, and integration patterns.

### Key Features
- **Multi-layer Architecture**: Frontend (Angular/Electron), Backend (FastAPI/Python), Database (PostgreSQL/SQLite)
- **Security-by-Design**: Comprehensive security architecture with defense-in-depth principles
- **Real-time Communication**: WebSocket integration for live updates and terminal operations
- **Circuit Breaker Patterns**: Resilient system design with automated failover mechanisms
- **Component Isolation**: Modular design with clear separation of concerns

## Structure

```
architecture/
├── README.md               # This overview document
├── api-contracts.md        # API specifications and data contracts
├── backend.md             # Backend architecture (FastAPI, Python services)
├── database.md            # Database design (PostgreSQL, SQLite, caching)
├── frontend.md            # Frontend architecture (Angular, Electron, UI)
└── security.md            # Security architecture and threat model
```

## Quick Setup

### Prerequisites
- Node.js 18+ (for frontend development)
- Python 3.10+ (for backend services)
- PostgreSQL 14+ (optional, SQLite fallback available)

### Installation
```bash
# Setup backend
cd apps/api
pip install -r requirements.txt

# Setup frontend
cd ../
npm install

# Run full stack
npm run dev
```

## Development

### Local Development
```bash
# Start backend only
npm run backend

# Start frontend only (with hot reload)
npm run electron:serve

# Start both (development mode)
npm run dev
```

### Testing
```bash
# Backend tests
cd apps/api
pytest

# Frontend tests
npm run test

# Integration tests
npm run test:ci
```

### Building
```bash
# Development build
npm run build

# Production build for Electron
npm run build:electron

# Package desktop application
npm run package
```

## Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENVIRONMENT` | Application environment (development/production) | `development` |
| `SYSTEMS_DB_HOST` | Database host | `localhost` |
| `SYSTEMS_DB_PORT` | Database port | `5432` |
| `SYSTEMS_BACKEND_PORT` | Backend API port | `8000` |
| `AI_ANTHROPIC_API_KEY` | Anthropic API key (optional) | `None` |

### Configuration Files
- `apps/api/config.py` - Backend configuration with persona-based settings
- `apps/web/apps/web/src/environments/environment.ts` - Frontend environment configuration
- `apps/package.json` - Application metadata and scripts

## API/Interface

### Key Architecture Components
- **Backend APIs** - RESTful APIs for rules, practices, templates, and system management
- **WebSocket Services** - Real-time communication for terminal operations and status updates
- **IPC Layer** - Electron inter-process communication for desktop integration
- **Database Layer** - PostgreSQL with SQLite fallback and two-tier caching

### Integration Points
- **Frontend ↔ Backend:** HTTP REST APIs with WebSocket real-time updates
- **Backend ↔ Database:** AsyncPG connection pooling with circuit breaker protection
- **Electron ↔ Angular:** Secure IPC communication with process isolation
- **External APIs:** Optional Claude AI integration with secure credential management

## Troubleshooting

### Common Issues
1. **Database Connection Failures**
   - **Symptom:** Circuit breaker open, fallback to mock data
   - **Solution:** Verify PostgreSQL service is running, check connection configuration in config.py

2. **Terminal Service Memory Leaks**
   - **Symptom:** Increasing memory usage, slow performance
   - **Solution:** Component-scoped terminal services are implemented (C1 fix), restart application if needed

3. **WebSocket Connection Issues**
   - **Symptom:** Real-time updates not working, connection timeouts
   - **Solution:** Check backend WebSocket endpoints, verify CORS configuration

### Debugging
```bash
# Backend debug mode
cd apps/api
python -m debugpy --wait-for-client --listen 5678 main.py

# Frontend debug (Electron DevTools)
npm run electron:dev

# View application logs
# Windows: %APPDATA%/AI Development Assistant/logs
# macOS: ~/Library/Logs/AI Development Assistant
# Linux: ~/.config/AI Development Assistant/logs
```

## Architecture Patterns

### Design Patterns Used
- **Circuit Breaker**: Resilient database connections with automatic fallback
- **Observer Pattern**: RxJS-based state management and real-time updates  
- **Repository Pattern**: Data access abstraction with mock/real implementations
- **Service Layer**: Clean separation between UI components and business logic
- **Command Pattern**: Terminal operations and system commands

### Security Architecture
- **Defense in Depth**: Multiple security layers from frontend to database
- **Zero Trust**: No implicit trust, verify every request and connection
- **Principle of Least Privilege**: Minimal access rights for all components
- **Secure by Design**: Security requirements integrated into development lifecycle

## Related Documentation

- [**Backend Architecture**](./backend.md) - FastAPI services, caching, and performance optimization
- [**Frontend Architecture**](./frontend.md) - Angular/Electron application structure and components  
- [**Database Architecture**](./database.md) - PostgreSQL schema, indexing, and data management
- [**Security Architecture**](./security.md) - Comprehensive security model and threat mitigation
- [**API Contracts**](./api-contracts.md) - API specifications and data schemas
- [**System Documentation**](../../CLAUDE.md) - Complete project overview and governance

---

**Component Owner:** Alex Novak (Frontend) & Dr. Sarah Chen (Backend) | **Last Updated:** January 2025 | **Status:** Active Development