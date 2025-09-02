# C3: Process Coordination Configuration Error - Implementation

**Issue**: Port mismatch and lack of robust startup coordination between Electron and Python backend  
**Severity**: CRITICAL  
**Owner**: Alex Novak v3.0  
**Date**: 2025-01-27 (Phase 3 Day 1)  

---

## Implementation Plan

### 1. Enhanced Process Coordination in Electron

```javascript
// electron/main.js - Replace startPythonBackend method (line 101)

async startPythonBackend() {
  /**
   * FIX C3: Robust backend startup with retry and health verification
   * Alex Novak v3.0 - 3AM Test compliant process coordination
   * Correlation IDs for debugging startup issues
   */
  const correlationId = `backend-startup-${Date.now()}`;
  console.log(`[${correlationId}] Starting backend coordination`);
  
  // Configuration with proper defaults
  const config = {
    port: this.backendPort || 8000,
    host: '127.0.0.1',
    maxRetries: 3,
    retryDelay: 2000,
    healthCheckTimeout: 5000,
    startupTimeout: 30000
  };
  
  // First, check if backend is already running
  const isRunning = await this.checkBackendRunning(config);
  if (isRunning) {
    console.log(`[${correlationId}] Backend already running on port ${config.port}`);
    this.notifyBackendStatus('connected', config.port);
    return true;
  }
  
  // Attempt to start backend with retries
  for (let attempt = 1; attempt <= config.maxRetries; attempt++) {
    console.log(`[${correlationId}] Startup attempt ${attempt}/${config.maxRetries}`);
    
    try {
      // Start the backend process
      const started = await this.launchBackendProcess(config, correlationId);
      if (!started) {
        throw new Error('Failed to launch backend process');
      }
      
      // Wait for backend to be healthy
      const healthy = await this.waitForBackendHealth(config, correlationId);
      if (healthy) {
        console.log(`[${correlationId}] Backend started successfully on attempt ${attempt}`);
        this.notifyBackendStatus('connected', config.port);
        return true;
      }
      
    } catch (error) {
      console.error(`[${correlationId}] Attempt ${attempt} failed:`, error.message);
      
      // Kill failed process before retry
      if (this.pythonBackend) {
        this.pythonBackend.kill();
        this.pythonBackend = null;
      }
      
      // Wait before retry with exponential backoff
      if (attempt < config.maxRetries) {
        const delay = config.retryDelay * Math.pow(2, attempt - 1);
        console.log(`[${correlationId}] Waiting ${delay}ms before retry`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  // All attempts failed
  console.error(`[${correlationId}] Failed to start backend after ${config.maxRetries} attempts`);
  this.notifyBackendStatus('failed', null);
  this.showBackendErrorDialog(correlationId);
  return false;
}

async checkBackendRunning(config) {
  /**
   * Check if backend is already running on the configured port
   */
  try {
    const response = await fetch(`http://${config.host}:${config.port}/health`, {
      method: 'GET',
      timeout: 2000
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('Backend health check response:', data);
      return true;
    }
  } catch (error) {
    // Backend not running or not responding
    return false;
  }
  return false;
}

async launchBackendProcess(config, correlationId) {
  /**
   * Launch the Python backend process with proper configuration
   */
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const backendPath = path.join(__dirname, '..', 'backend', 'main.py');
  
  // Verify backend script exists
  const fs = require('fs');
  if (!fs.existsSync(backendPath)) {
    console.error(`[${correlationId}] Backend script not found at: ${backendPath}`);
    return false;
  }
  
  console.log(`[${correlationId}] Launching backend: ${pythonPath} ${backendPath}`);
  
  // Start the process with explicit configuration
  this.pythonBackend = spawn(pythonPath, [
    backendPath,
    '--port', config.port.toString(),
    '--host', config.host,
    '--correlation-id', correlationId
  ], {
    cwd: path.join(__dirname, '..', 'backend'),
    env: {
      ...process.env,
      PYTHONUNBUFFERED: '1',
      BACKEND_PORT: config.port.toString(),
      BACKEND_HOST: config.host,
      ELECTRON_RUN: 'true'
    },
    shell: false,
    windowsHide: true
  });
  
  // Handle process output
  this.pythonBackend.stdout.on('data', (data) => {
    console.log(`[${correlationId}] Backend stdout:`, data.toString().trim());
  });
  
  this.pythonBackend.stderr.on('data', (data) => {
    console.error(`[${correlationId}] Backend stderr:`, data.toString().trim());
  });
  
  this.pythonBackend.on('error', (error) => {
    console.error(`[${correlationId}] Backend process error:`, error);
  });
  
  this.pythonBackend.on('exit', (code, signal) => {
    console.log(`[${correlationId}] Backend process exited with code ${code}, signal ${signal}`);
    this.pythonBackend = null;
    this.notifyBackendStatus('disconnected', null);
  });
  
  return true;
}

async waitForBackendHealth(config, correlationId) {
  /**
   * Wait for backend to become healthy with timeout
   */
  const startTime = Date.now();
  const checkInterval = 500;
  
  while (Date.now() - startTime < config.startupTimeout) {
    const healthy = await this.checkBackendHealth(config, correlationId);
    if (healthy) {
      return true;
    }
    
    await new Promise(resolve => setTimeout(resolve, checkInterval));
  }
  
  console.error(`[${correlationId}] Backend health check timeout after ${config.startupTimeout}ms`);
  return false;
}

async checkBackendHealth(config, correlationId) {
  /**
   * Comprehensive health check with detailed status
   */
  try {
    const response = await fetch(`http://${config.host}:${config.port}/health`, {
      method: 'GET',
      headers: {
        'X-Correlation-ID': correlationId || 'health-check'
      },
      timeout: config.healthCheckTimeout || 5000
    });
    
    if (response.ok) {
      const data = await response.json();
      
      // Verify all required services are running
      const requiredServices = ['cache', 'websocket', 'database'];
      const allHealthy = requiredServices.every(service => 
        data.services && data.services[service] === 'healthy'
      );
      
      if (allHealthy) {
        console.log(`[${correlationId}] All backend services healthy`);
        return true;
      } else {
        console.warn(`[${correlationId}] Some services unhealthy:`, data.services);
        return false;
      }
    }
  } catch (error) {
    console.error(`[${correlationId}] Health check failed:`, error.message);
    return false;
  }
  return false;
}

notifyBackendStatus(status, port) {
  /**
   * Notify renderer process of backend status changes
   */
  if (this.mainWindow && !this.mainWindow.isDestroyed()) {
    this.mainWindow.webContents.send('backend-status', { 
      status, 
      port,
      timestamp: Date.now()
    });
  }
  
  // Update tray icon if available
  if (this.tray) {
    const tooltip = status === 'connected' 
      ? `Backend connected on port ${port}` 
      : 'Backend disconnected';
    this.tray.setToolTip(tooltip);
  }
}

showBackendErrorDialog(correlationId) {
  /**
   * Show user-friendly error dialog when backend fails to start
   */
  dialog.showErrorBox(
    'Backend Startup Failed',
    `The AI Assistant backend failed to start.\n\n` +
    `Correlation ID: ${correlationId}\n\n` +
    `Please check:\n` +
    `1. Python 3.10+ is installed\n` +
    `2. Required packages are installed (pip install -r requirements.txt)\n` +
    `3. Port ${this.backendPort} is not in use\n` +
    `4. Antivirus is not blocking the backend\n\n` +
    `Check the console for detailed error messages.`
  );
}
```

### 2. Add Configuration File for Consistency

```javascript
// electron/config.js - NEW FILE

module.exports = {
  backend: {
    port: 8000,
    host: '127.0.0.1',
    protocol: 'http',
    endpoints: {
      health: '/health',
      ai: '/ai/execute',
      metrics: '/metrics/cache',
      persona: '/persona/suggest'
    }
  },
  
  startup: {
    maxRetries: 3,
    retryDelay: 2000,
    healthCheckTimeout: 5000,
    startupTimeout: 30000
  },
  
  ipc: {
    timeout: 10000,
    maxMessageSize: 10 * 1024 * 1024 // 10MB
  },
  
  pty: {
    maxSessions: 10,
    defaultShell: process.platform === 'win32' ? 'powershell.exe' : '/bin/bash',
    cols: 80,
    rows: 30
  }
};
```

### 3. Update Backend to Accept Configuration

```python
# backend/main.py - Update startup to accept port configuration

import argparse
import os
import sys
import logging
from fastapi import FastAPI
import uvicorn

def parse_arguments():
    """
    FIX C3: Parse command line arguments for configuration
    """
    parser = argparse.ArgumentParser(description='AI Assistant Backend')
    parser.add_argument('--port', type=int, default=8000,
                      help='Port to run the backend on (default: 8000)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                      help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--correlation-id', type=str, default='',
                      help='Correlation ID for startup tracking')
    parser.add_argument('--reload', action='store_true',
                      help='Enable auto-reload for development')
    return parser.parse_args()

def setup_logging(correlation_id):
    """Configure logging with correlation ID"""
    log_format = f'[{correlation_id}] %(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format if correlation_id else logging.BASIC_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('backend.log')
        ]
    )
    return logging.getLogger(__name__)

if __name__ == "__main__":
    # FIX C3: Parse arguments and configure
    args = parse_arguments()
    logger = setup_logging(args.correlation_id)
    
    # Log startup configuration
    logger.info(f"Starting backend on {args.host}:{args.port}")
    logger.info(f"Correlation ID: {args.correlation_id}")
    logger.info(f"Environment: {os.getenv('ELECTRON_RUN', 'standalone')}")
    
    try:
        # Start the FastAPI application
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start backend: {e}")
        sys.exit(1)
```

### 4. Add Health Endpoint Enhancement

```python
# backend/main.py - Enhance health endpoint

@app.get("/health")
async def health_check(correlation_id: str = Header(None, alias="X-Correlation-ID")):
    """
    FIX C3: Comprehensive health check endpoint
    Returns detailed status of all services
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "correlation_id": correlation_id,
        "services": {},
        "metrics": {}
    }
    
    try:
        # Check cache service
        cache_healthy = await check_cache_health()
        health_status["services"]["cache"] = "healthy" if cache_healthy else "unhealthy"
        
        # Check WebSocket service
        ws_healthy = check_websocket_health()
        health_status["services"]["websocket"] = "healthy" if ws_healthy else "unhealthy"
        
        # Check database
        db_healthy = await check_database_health()
        health_status["services"]["database"] = "healthy" if db_healthy else "degraded"
        
        # Overall status
        all_healthy = all(
            status == "healthy" 
            for status in health_status["services"].values()
        )
        health_status["status"] = "healthy" if all_healthy else "degraded"
        
        # Add metrics
        health_status["metrics"] = {
            "uptime_seconds": get_uptime(),
            "memory_mb": get_memory_usage(),
            "active_connections": websocket_manager.connection_count
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    return health_status
```

---

## Testing

```javascript
// electron/tests/test-process-coordination.js

const { spawn } = require('child_process');
const fetch = require('node-fetch');

describe('Process Coordination Tests', () => {
  /**
   * FIX C3: Test robust startup coordination
   * Alex Novak v3.0 - 3AM Test validation
   */
  
  test('should start backend on correct port', async () => {
    const backend = spawn('python', ['backend/main.py', '--port', '8000']);
    
    // Wait for startup
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Check health
    const response = await fetch('http://127.0.0.1:8000/health');
    expect(response.ok).toBe(true);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
    
    backend.kill();
  });
  
  test('should retry on startup failure', async () => {
    // Mock backend that fails first time
    let attempts = 0;
    const mockBackend = {
      start: () => {
        attempts++;
        if (attempts < 2) {
          throw new Error('Startup failed');
        }
        return true;
      }
    };
    
    // Should retry and succeed
    const result = await startWithRetry(mockBackend, 3);
    expect(result).toBe(true);
    expect(attempts).toBe(2);
  });
  
  test('should detect already running backend', async () => {
    // Start backend manually
    const backend = spawn('python', ['backend/main.py']);
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Try to start again - should detect existing
    const app = new AIAssistantApp();
    const running = await app.checkBackendRunning({ port: 8000, host: '127.0.0.1' });
    expect(running).toBe(true);
    
    backend.kill();
  });
});
```

---

## Verification Steps

1. **Port Configuration**: Verify both Electron and Python use port 8000
2. **Startup Sequence**: Test startup with backend already running
3. **Retry Logic**: Kill backend and verify auto-restart
4. **Health Checks**: Confirm comprehensive health status
5. **Error Handling**: Test with Python not installed

---

## Success Criteria

✅ Electron and backend communicate on same port (8000)  
✅ Robust startup with automatic retry  
✅ Health checks verify all services  
✅ Clear error messages when startup fails  
✅ Correlation IDs for debugging startup issues  
✅ Graceful handling of already-running backend  

---

**Status**: IMPLEMENTATION READY  
**Estimated Time**: 1.5 hours  
**Risk**: LOW (configuration issue, not architectural)