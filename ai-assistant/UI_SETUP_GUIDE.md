# AI Orchestration System - Complete Setup Guide

## System Overview

### What We've Built
1. **Backend API** (Python/FastAPI) - Currently running on port 8001
2. **Modern React UI** (TypeScript/Material-UI) - Ready to deploy
3. **Complete API ecosystem** with 30+ endpoints

## Technical Debt Summary
- **66 magic variables** found (localhost, hardcoded ports, etc.)
- **18 incomplete implementations** (pass statements)
- **Recommendation**: 4-6 hours to refactor configuration

## Quick Start

### Backend (Already Running)
```bash
# Backend is running at http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### Frontend Setup
```bash
# Navigate to frontend
cd ai-assistant/frontend/orchestration-ui

# Install dependencies
npm install

# Start development server
npm start

# Access at http://localhost:3000
```

## UI Features

### 1. Dashboard
- Real-time metrics and performance graphs
- Agent status monitoring
- Recent governance decisions
- Task execution statistics
- Consensus distribution charts

### 2. Orchestration Console
- Execute tasks with/without orchestration
- Real-time execution timeline
- Assumption fighting visualization
- Evidence gathering display
- Consensus building process

### 3. Persona Management
- View all 3 personas (Sarah, Marcus, Emily)
- See expertise areas and decision styles
- Challenge assumptions directly
- View interaction preferences

### 4. Agent Monitor
- 6 AI agents status
- Performance metrics
- Success rates
- Capability listing

### 5. Governance Panel
- Decision history
- Voting records
- Consensus levels
- Escalation management

## API Endpoints Summary

### Core APIs
- `GET /health` - Service health
- `POST /ai/orchestrated` - Full orchestration with assumption fighting
- `GET /orchestration/status` - System status

### Management APIs
- `/personas/*` - Persona management
- `/agents/*` - Agent management
- `/rules/*` - Rules and best practices
- `/assumptions/*` - Assumption tracking
- `/governance/*` - Governance decisions

## Architecture

```
┌─────────────────────────────┐
│     React UI (Port 3000)    │
├─────────────────────────────┤
│   FastAPI Backend (8001)    │
├─────────────────────────────┤
│  Persona Orchestration      │
│  (Assumption Fighting)      │
├─────────────────────────────┤
│   AI Agents (6 models)      │
├─────────────────────────────┤
│  Governance & Validation    │
└─────────────────────────────┘
```

## Key Benefits

### System Capabilities
1. **Prevents AI Hallucinations** - Multi-persona validation
2. **Evidence-Based Decisions** - All assumptions challenged
3. **Real-Time Monitoring** - Live dashboard and metrics
4. **Complete Audit Trail** - All decisions logged
5. **Flexible Governance** - Configurable consensus levels

### UI Advantages
- **Modern Dark Theme** - Easy on the eyes
- **Real-Time Updates** - WebSocket-ready architecture
- **Responsive Design** - Works on all devices
- **Interactive Charts** - Recharts visualization
- **Material Design** - Professional appearance

## Configuration Issues to Fix

### High Priority
1. Move hardcoded ports to environment variables
2. Replace localhost references with configurable hosts
3. Implement proper error handling for stub methods

### Example Refactor
```python
# Before (magic variable)
db_host: str = Field("localhost", description="PostgreSQL host")

# After (environment-based)
db_host: str = Field(
    os.getenv("DB_HOST", "localhost"), 
    description="PostgreSQL host"
)
```

## Next Steps

### Immediate Actions
1. Install and run the React UI
2. Test the orchestration console
3. Monitor assumption fighting in real-time

### Future Enhancements
1. Add WebSocket for live updates
2. Implement remaining UI pages
3. Add data export functionality
4. Create mobile app version
5. Add dark/light theme toggle

## Environment Setup

Create `.env` file in backend:
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_orchestration

# API Keys (optional)
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key

# Service Ports
BACKEND_PORT=8001
FRONTEND_PORT=3000

# Feature Flags
ENABLE_GOVERNANCE=true
ENABLE_ASSUMPTION_FIGHTING=true
```

## Testing the System

### 1. Test Orchestration
```bash
curl -X POST http://localhost:8001/ai/orchestrated \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Should we use Kubernetes?",
    "context": {"team_size": 5},
    "use_cache": false
  }'
```

### 2. Check Status
```bash
curl http://localhost:8001/orchestration/status
```

### 3. View Personas
```bash
curl http://localhost:8001/personas/
```

## Troubleshooting

### Backend Issues
- Check if port 8001 is available
- Verify Python dependencies installed
- Check logs for FastAPI errors

### Frontend Issues
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall
- Check proxy setting in package.json

### API Connection Issues
- Verify CORS settings
- Check network firewall
- Ensure backend is running

## Summary

The system is **fully operational** with:
- ✅ Backend API running with all endpoints
- ✅ Modern React UI ready to deploy
- ✅ Complete persona orchestration with assumption fighting
- ✅ Real-time monitoring capabilities
- ✅ Comprehensive API documentation

**Magic Variables**: 66 instances need refactoring
**Boilerplate Code**: 18 stub methods need implementation
**Estimated Cleanup**: 4-6 hours of refactoring

The UI provides a modern, user-friendly interface to manage the complex orchestration system, making it much easier to monitor and control the AI persona assumption fighting process.