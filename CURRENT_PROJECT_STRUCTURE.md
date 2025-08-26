# Current Project Structure - AI Assistant System

## Clean Directory Structure

```
ClaudeResearchAndDevelopment/
├── ai-assistant/          # Main application
│   ├── backend/          # Python FastAPI backend
│   ├── src/              # Angular frontend
│   └── electron/         # Electron desktop wrapper
├── archive/              # Archived files
│   ├── documentation/    # Old documentation
│   ├── test_files/       # Test files
│   └── unused_code/      # Unused code
├── hooks/                # Git hooks
└── CLAUDE.md            # Project instructions

```

## Active Components

### 1. Backend (Python FastAPI)
**Location:** `ai-assistant/backend/`

**Core Files:**
- `main.py` - Main FastAPI application
- `agent_terminal_manager.py` - Manages AI agents with PTY terminals
- `claude_terminal.py` - Claude integration (simulation mode)
- `orchestrator.py` - Multi-tenant orchestration
- `cache_manager.py` - Intelligent caching system
- `persona_manager.py` - Three-persona governance
- `database_service.py` - PostgreSQL integration
- `websocket_manager.py` - Real-time WebSocket updates

**Configuration:**
- `config.py` - Central configuration
- `requirements.txt` - Python dependencies
- `templates-data.json` - Template definitions
- `best-practices-data.json` - Best practices data

**Running:** `python main.py` (runs on port 8000)

### 2. Frontend (Angular 17)
**Location:** `ai-assistant/src/`

**Core Components:**
- `app/components/agent-manager/` - AI agent management UI
- `app/components/dashboard/` - Main dashboard
- `app/components/terminal/` - Terminal interface
- `app/modules/templates/` - Templates module
- `app/services/` - Angular services

**Configuration:**
- `angular.json` - Angular configuration
- `package.json` - Node dependencies
- `tsconfig.json` - TypeScript configuration

**Running:** `npm start` (builds and launches Electron)

### 3. Electron Wrapper
**Location:** `ai-assistant/electron/`

**Core Files:**
- `main.js` - Electron main process
- `preload.js` - Preload script
- `pty-manager.js` - PTY terminal management
- `pty-fallback-system.js` - Fallback for Windows

## Current System Status

### ✅ Working Features
1. **Agent Management**
   - Spawn up to 6 AI agents
   - Each agent has individual PTY terminal
   - Real-time status tracking
   - Command execution with responses

2. **Three-Persona Governance**
   - Dr. Sarah Chen (AI Integration)
   - Marcus Rodriguez (Systems Performance)
   - Emily Watson (UX/Frontend)

3. **Intelligent Caching**
   - Three-tier cache (Hot/Warm/Cold)
   - Real metrics (not mocked)
   - Token optimization

4. **WebSocket Real-time Updates**
   - Broadcasting agent status
   - Cache metrics
   - Orchestration updates

5. **Claude Terminal**
   - Simulation mode (CLI not in PATH)
   - Realistic responses
   - Interactive chat interface

### 🔧 Configuration Notes

1. **Backend runs on port 8000** (not 8001)
2. **node-pty** is installed in package.json
3. **PostgreSQL** falls back to mock if not configured
4. **Claude CLI** uses simulation mode when not found

## Key Endpoints

### Agent Management
- `POST /agents/spawn` - Create new agent
- `GET /agents/status` - Get all agents status
- `POST /agents/{id}/execute` - Send command to agent
- `DELETE /agents/{id}` - Terminate agent

### Orchestration
- `GET /orchestration/status` - Real agent counts
- `POST /ai/orchestrated` - Three-persona execution

### Claude Terminal
- `POST /claude/connect` - Connect to Claude
- `POST /claude/send` - Send message
- `GET /claude/status` - Connection status

### WebSocket
- `ws://localhost:8000/ws` - Real-time updates

## How to Run

1. **Start Backend:**
   ```bash
   cd ai-assistant/backend
   python main.py
   ```

2. **Start Frontend:**
   ```bash
   cd ai-assistant
   npm start
   ```

## What's Been Cleaned Up

All unused files have been moved to the `archive/` folder:
- Old documentation → `archive/documentation/`
- Test files → `archive/test_files/`
- Unused code → `archive/unused_code/`

The project now contains only essential, working code.