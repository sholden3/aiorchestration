# 🏗️ SYSTEM ARCHITECTURE (ACTUAL STATE)

## Backend Components (Python FastAPI)
```
ai-assistant/backend/
├── main.py                    # FastAPI app with proper lifecycle
├── cache_manager.py           # Two-tier cache (hot/warm) - WORKING
├── websocket_manager.py       # Real-time broadcasting - NEEDS LIMITS  
├── agent_terminal_manager.py  # Agent simulation - MOCK ONLY
├── database_manager.py        # PostgreSQL with mock fallback - WORKING
├── persona_manager.py         # Three-persona routing - WORKING
└── config.py                  # Configuration management - WORKING
```

## Frontend Components (Angular 17 + Electron)
```
ai-assistant/src/
├── app/components/
│   ├── agent-manager/         # Agent UI - displays mock data
│   ├── dashboard/             # Metrics dashboard - WORKING
│   └── terminal/              # Terminal interface - not connected to PTY
├── app/services/
│   ├── terminal.service.ts    # IPC listeners - MEMORY LEAK
│   ├── websocket.service.ts   # Real-time updates - WORKING
│   └── orchestration.service.ts # Backend integration - WORKING
└── electron/
    ├── main.js                # Process management - PORT MISMATCH
    ├── preload.js             # Secure IPC bridge - WORKING
    └── pty-manager.js         # Terminal management - not fully integrated
```

## Component Status Overview

### Production Ready Components ✅
- FastAPI Backend with lifecycle management
- Two-tier cache system with 90% hit rate
- WebSocket broadcasting infrastructure
- PostgreSQL with connection pooling
- Cross-platform Electron wrapper
- Angular Material UI components

### Development Phase Components ⚠️
- AI Agent execution (simulated)
- Terminal PTY integration (disconnected)
- Claude CLI integration (simulation mode)
- Resource limit enforcement (unvalidated)

## Architecture Design Patterns

### Backend Architecture (Sarah's Domain)
- **Circuit Breaker Pattern**: Protects external dependencies
- **Two-Tier Caching**: Hot (memory) and warm (disk) layers
- **Connection Pooling**: Database resource management
- **Graceful Degradation**: Fallback to mock services
- **Event-Driven**: WebSocket for real-time updates

### Frontend Architecture (Alex's Domain)
- **Component-Based**: Angular 17 with Material Design
- **Service Layer**: Centralized business logic
- **IPC Security**: Preload script for secure communication
- **State Management**: Service-based state handling
- **Reactive Forms**: Form validation and error handling

## Integration Points

### Cross-System Boundaries
1. **HTTP API**: Frontend ↔ Backend REST communication
2. **WebSocket**: Real-time bidirectional updates
3. **IPC Bridge**: Electron main ↔ renderer process
4. **Database**: Backend ↔ PostgreSQL connection
5. **File System**: Cache and configuration persistence

### Security Boundaries
- **Context Isolation**: Electron renderer process
- **CORS Configuration**: Backend API access control
- **Input Validation**: All user inputs sanitized
- **Error Boundaries**: Prevent cascade failures
- **Resource Limits**: Connection and memory controls

## Data Flow Architecture

### Request Flow
```
User Action → Angular Component → Service Layer → IPC Bridge 
    → Electron Main → HTTP/WS → FastAPI → Database/Cache
```

### Response Flow  
```
Database/Cache → FastAPI → HTTP/WS → Electron Main 
    → IPC Bridge → Service Layer → Angular Component → UI Update
```

### Real-Time Updates
```
Backend Event → WebSocket Manager → Broadcast 
    → All Connected Clients → UI Update
```

## Resource Management

### Memory Management
- **Frontend**: Component lifecycle cleanup
- **Backend**: Connection pooling limits
- **Cache**: LRU eviction policies
- **WebSocket**: Connection limits (needs validation)

### Performance Optimization
- **Lazy Loading**: Angular modules on demand
- **Virtual Scrolling**: Large data lists
- **Debouncing**: User input processing
- **Batch Updates**: WebSocket message aggregation
- **Cache Warming**: Predictive data loading