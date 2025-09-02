# AI Assistant Application

## Purpose
Main application combining Angular frontend with Python FastAPI backend and Electron desktop wrapper.

## Contents
- `src/` - Angular frontend source code
- `backend/` - Python FastAPI backend
- `electron/` - Electron main process and IPC
- `dist/` - Build output (git-ignored)
- Configuration files for Angular, TypeScript, and packaging

## Dependencies
- Angular 17+ with Material Design
- Python FastAPI with WebSocket support
- Electron for desktop deployment
- Node.js and npm for build tools
- PostgreSQL for data persistence (optional)

## Testing
- Frontend: `npm test`
- Backend: `pytest backend/tests/`
- E2E: `npm run e2e`
- Build: `npm run build`

## Maintenance
- Update dependencies monthly
- Security patches immediately
- Performance monitoring
- Regular refactoring for clean code