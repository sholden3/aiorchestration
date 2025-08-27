/**
 * Business Context: Desktop application entry point for AI Development Assistant
 * Architecture Pattern: Main/Renderer process separation with IPC communication
 * Business Assumptions: Single user, Windows-only, local execution
 * Performance Requirements: <100ms IPC response time, stable PTY sessions
 */

const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// FIX C3: Load centralized configuration
const config = require('./config');

// Use universal PTY fallback system that automatically selects best implementation
const PTYManager = require('./pty-fallback-system');
console.log('PTY system initialized');

class AIAssistantApp {
  constructor() {
    this.mainWindow = null;
    this.pythonBackend = null;
    this.ptyManager = new PTYManager();
    this.isDev = process.argv.includes('--dev');
    this.backendPort = config.backend.port; // FIX C3: Use centralized config
    
    this.initializeApp();
  }

  initializeApp() {
    /**
     * Business Logic: Initialize desktop application with all core services
     * Error Handling: Graceful shutdown if initialization fails
     */
    
    // Single instance lock
    const gotTheLock = app.requestSingleInstanceLock();
    if (!gotTheLock) {
      app.quit();
      return;
    }

    app.whenReady().then(() => {
      this.createWindow();
      // FIX C3: Always attempt to start or connect to backend on correct port
      this.startPythonBackend();
      // Health check will verify if backend is running
      setTimeout(() => this.checkBackendHealth(), 2000);
      this.setupIPC();
      this.setupPTYHandlers();
    });

    app.on('window-all-closed', () => {
      this.cleanup();
      app.quit();
    });

    app.on('second-instance', () => {
      if (this.mainWindow) {
        if (this.mainWindow.isMinimized()) this.mainWindow.restore();
        this.mainWindow.focus();
      }
    });
  }

  createWindow() {
    /**
     * Business Context: Create main application window with security best practices
     * Performance: Preload script for secure context isolation
     */
    this.mainWindow = new BrowserWindow({
      width: 1600,
      height: 900,
      minWidth: 1200,
      minHeight: 700,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js'),
        webSecurity: !this.isDev
      },
      title: 'AI Development Assistant',
      icon: path.join(__dirname, '../assets/icon.ico'),
      show: false
    });

    // Load the Angular app
    if (this.isDev) {
      this.mainWindow.loadURL('http://localhost:4200');
      this.mainWindow.webContents.openDevTools();
    } else {
      this.mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    }

    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow.show();
    });

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });
  }

  async startPythonBackend() {
    /**
     * FIX C3: Comprehensive backend coordination with retry logic
     * Alex Novak v3.0: Full process coordination with debugging
     * Features: Retry logic, correlation IDs, already-running detection
     */
    
    const correlationId = `startup-${Date.now()}`;
    console.log(`[${correlationId}] Starting backend coordination`);
    
    // Configuration from centralized config
    const backendConfig = {
      port: config.backend.port,
      host: config.backend.host,
      maxRetries: config.backend.startup.maxRetries,
      retryDelay: config.backend.startup.retryDelay,
      healthCheckTimeout: config.backend.startup.healthCheckTimeout,
      startupTimeout: config.backend.startup.startupTimeout
    };
    
    // First check if backend is already running
    if (await this.checkBackendRunning(backendConfig, correlationId)) {
      console.log(`[${correlationId}] Backend already running on port ${backendConfig.port}`);
      this.notifyBackendStatus('connected', backendConfig.port);
      return true;
    }
    
    // Attempt to start backend with retries
    for (let attempt = 1; attempt <= backendConfig.maxRetries; attempt++) {
      console.log(`[${correlationId}] Startup attempt ${attempt}/${backendConfig.maxRetries}`);
      
      try {
        // Start the backend process
        const started = await this.launchBackendProcess(backendConfig, correlationId, attempt);
        if (!started) {
          throw new Error('Failed to launch backend process');
        }
        
        // Wait for backend to be healthy
        const healthy = await this.waitForBackendHealth(backendConfig, correlationId);
        if (healthy) {
          console.log(`[${correlationId}] Backend started successfully on attempt ${attempt}`);
          this.notifyBackendStatus('connected', backendConfig.port);
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
        if (attempt < backendConfig.maxRetries) {
          const delay = backendConfig.retryDelay * Math.pow(2, attempt - 1);
          console.log(`[${correlationId}] Waiting ${delay}ms before retry`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    
    // All attempts failed
    console.error(`[${correlationId}] Failed to start backend after ${backendConfig.maxRetries} attempts`);
    this.notifyBackendStatus('failed', null);
    this.showBackendErrorDialog(correlationId);
    return false;
  }
  
  async checkBackendRunning(config, correlationId) {
    /**
     * Check if backend is already running on the configured port
     */
    try {
      const response = await fetch(`http://${config.host}:${config.port}/health`);
      if (response.ok) {
        const data = await response.json();
        console.log(`[${correlationId}] Backend health response:`, data);
        return true;
      }
    } catch (error) {
      // Backend not running or not responding
      return false;
    }
    return false;
  }
  
  async launchBackendProcess(config, correlationId, attempt) {
    /**
     * Launch the Python backend process with proper configuration
     */
    const fs = require('fs');
    const pythonCommands = process.platform === 'win32' 
      ? ['python', 'python3', 'py']  // Try multiple Python commands on Windows
      : ['python3', 'python'];
    
    const backendPath = path.join(__dirname, '../backend/main.py');
    
    // Verify backend script exists
    if (!fs.existsSync(backendPath)) {
      console.error(`[${correlationId}] Backend script not found at: ${backendPath}`);
      return false;
    }
    
    // Try different Python commands until one works
    for (const pythonCmd of pythonCommands) {
      try {
        console.log(`[${correlationId}] Trying ${pythonCmd} ${backendPath}`);
        
        this.pythonBackend = spawn(pythonCmd, [
          backendPath,
          '--port', config.port.toString(),
          '--host', config.host,
          '--correlation-id', correlationId
        ], {
          cwd: path.join(__dirname, '../backend'),
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
        
        // Set up event handlers
        this.pythonBackend.stdout.on('data', (data) => {
          console.log(`[${correlationId}] Backend stdout:`, data.toString().trim());
          if (this.mainWindow) {
            this.mainWindow.webContents.send('backend-log', data.toString());
          }
        });
        
        this.pythonBackend.stderr.on('data', (data) => {
          console.error(`[${correlationId}] Backend stderr:`, data.toString().trim());
          if (this.mainWindow) {
            this.mainWindow.webContents.send('backend-error', data.toString());
          }
        });
        
        this.pythonBackend.on('error', (error) => {
          console.error(`[${correlationId}] Backend process error:`, error);
        });
        
        this.pythonBackend.on('exit', (code, signal) => {
          console.log(`[${correlationId}] Backend exited with code ${code}, signal ${signal}`);
          this.pythonBackend = null;
          this.notifyBackendStatus('disconnected', null);
        });
        
        // If we got here, spawn succeeded
        console.log(`[${correlationId}] Backend process started with ${pythonCmd}`);
        return true;
        
      } catch (error) {
        console.log(`[${correlationId}] ${pythonCmd} failed:`, error.message);
        // Try next Python command
        continue;
      }
    }
    
    console.error(`[${correlationId}] No Python command worked`);
    return false;
  }
  
  async waitForBackendHealth(config, correlationId) {
    /**
     * Wait for backend to become healthy with timeout
     */
    const startTime = Date.now();
    const checkInterval = 500;
    
    while (Date.now() - startTime < config.startupTimeout) {
      try {
        const response = await fetch(`http://${config.host}:${config.port}/health`);
        if (response.ok) {
          const data = await response.json();
          console.log(`[${correlationId}] Backend healthy:`, data);
          return true;
        }
      } catch (error) {
        // Not ready yet, continue waiting
      }
      
      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }
    
    console.error(`[${correlationId}] Backend health check timeout after ${config.startupTimeout}ms`);
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
  }
  
  showBackendErrorDialog(correlationId) {
    /**
     * Show user-friendly error dialog when backend fails to start
     */
    dialog.showErrorBox(
      'Backend Startup Failed',
      `The AI Assistant backend failed to start.\n\n` +
      `Possible causes:\n` +
      `1. Python 3.10+ not installed\n` +
      `2. Required packages missing (pip install -r requirements.txt)\n` +
      `3. Port ${this.backendPort} already in use\n` +
      `4. Antivirus blocking the backend\n\n` +
      `Correlation ID: ${correlationId}\n\n` +
      `Check the console (Ctrl+Shift+I) for detailed error messages.`
    );
  }


  setupIPC() {
    /**
     * Business Context: Inter-process communication for frontend-backend interaction
     * Security: Validate all IPC messages
     * Performance: Async handlers for non-blocking operations
     */
    
    // AI Task Execution
    ipcMain.handle('execute-ai-task', async (event, task) => {
      try {
        const response = await fetch(`http://127.0.0.1:${this.backendPort}/ai/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(task)
        });
        
        if (!response.ok) {
          throw new Error(`Backend returned ${response.status}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error('AI task execution failed:', error);
        return {
          success: false,
          error: error.message,
          fallback: 'Backend communication error. Please check if the service is running.'
        };
      }
    });

    // Cache Metrics
    ipcMain.handle('get-cache-metrics', async () => {
      try {
        const response = await fetch(`http://127.0.0.1:${this.backendPort}/metrics/cache`);
        return await response.json();
      } catch (error) {
        console.error('Failed to get cache metrics:', error);
        return { hit_rate: 0, tokens_saved: 0, error: error.message };
      }
    });

    // Persona Management
    ipcMain.handle('suggest-persona', async (event, taskDescription) => {
      try {
        const response = await fetch(`http://127.0.0.1:${this.backendPort}/persona/suggest`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ description: taskDescription })
        });
        return await response.json();
      } catch (error) {
        console.error('Persona suggestion failed:', error);
        return { personas: [], error: error.message };
      }
    });

    // File Dialog
    ipcMain.handle('select-directory', async () => {
      const result = await dialog.showOpenDialog(this.mainWindow, {
        properties: ['openDirectory']
      });
      return result.canceled ? null : result.filePaths[0];
    });

    // Open External Link
    ipcMain.handle('open-external', async (event, url) => {
      shell.openExternal(url);
    });
  }

  setupPTYHandlers() {
    /**
     * Business Context: Terminal emulation for development tasks
     * Requirements: Support PowerShell, Bash, CMD with session persistence
     */
    
    // Create Terminal Session
    ipcMain.on('create-terminal-session', (event, options = {}) => {
      const { sessionId, shell, cwd } = options;
      
      console.log('IPC: Creating terminal session:', { sessionId, shell, cwd });
      
      try {
        const actualSessionId = this.ptyManager.createSession(sessionId, shell, cwd);
        console.log('IPC: Terminal session created successfully:', actualSessionId);
        
        // Forward PTY output to renderer
        this.ptyManager.on(`data-${sessionId}`, (data) => {
          console.log(`IPC: Sending terminal output for ${sessionId}, length: ${data.length}`);
          this.mainWindow.webContents.send('terminal-output', {
            sessionId,
            data,
            timestamp: Date.now()
          });
        });
        
        this.ptyManager.on(`exit-${sessionId}`, (exitCode) => {
          console.log(`IPC: Terminal session ${sessionId} exited with code:`, exitCode);
          this.mainWindow.webContents.send('terminal-exit', {
            sessionId,
            exitCode
          });
        });
        
        event.reply(`terminal-session-created-${sessionId}`, { 
          sessionId: actualSessionId,
          error: null 
        });
      } catch (error) {
        console.error('IPC: Failed to create terminal session:', error);
        event.reply(`terminal-session-created-${sessionId}`, { 
          error: error.message 
        });
      }
    });

    // Write to Terminal
    ipcMain.on('terminal-write', (event, options) => {
      const { sessionId, data } = options;
      this.ptyManager.writeToSession(sessionId, data);
    });

    // Resize Terminal
    ipcMain.on('terminal-resize', (event, options) => {
      const { sessionId, cols, rows } = options;
      this.ptyManager.resizeSession(sessionId, cols, rows);
    });

    // Kill Terminal Session
    ipcMain.on('terminal-kill', (event, options) => {
      const { sessionId } = options;
      this.ptyManager.killSession(sessionId);
    });

    // Get Active Sessions
    ipcMain.on('get-terminal-sessions', (event) => {
      const sessions = this.ptyManager.getActiveSessions();
      event.reply('terminal-sessions-list', sessions);
    });

    // Get Session Output
    ipcMain.on('get-terminal-output', (event, options) => {
      const { sessionId, fromIndex } = options;
      const output = this.ptyManager.getSessionOutput(sessionId, fromIndex);
      event.reply(`terminal-output-${sessionId}`, output);
    });
    
    // Periodic health check for sessions
    setInterval(() => {
      this.ptyManager.checkSessionHealth();
      const sessions = this.ptyManager.getActiveSessions();
      if (this.mainWindow) {
        this.mainWindow.webContents.send('terminal-sessions', sessions);
      }
    }, 30000);
  }

  cleanup() {
    /**
     * Business Logic: Clean shutdown of all services
     * Error Handling: Force kill if graceful shutdown fails
     */
    console.log('Cleaning up...');
    
    // Kill all PTY sessions
    this.ptyManager.killAllSessions();
    
    // Stop Python backend only if we started it
    if (this.pythonBackend) {
      console.log('Stopping Python backend...');
      this.pythonBackend.kill('SIGTERM');
      setTimeout(() => {
        if (this.pythonBackend && !this.pythonBackend.killed) {
          this.pythonBackend.kill('SIGKILL');
        }
      }, 5000);
    } else {
      console.log('Backend was externally managed, not stopping');
    }
  }
}

// Start the application
new AIAssistantApp();