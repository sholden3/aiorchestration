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
const fs = require('fs');

// Import BackendManager for automatic backend startup
const BackendManager = require('./backend-manager');

// Load app configuration from centralized JSON
function loadAppConfig() {
  const configPath = path.join(__dirname, '../../config/app.config.json');
  const envConfigPath = path.join(__dirname, `../../config/app.config.${process.env.NODE_ENV || 'development'}.json`);
  
  let appConfig = {};
  
  // Load base config
  if (fs.existsSync(configPath)) {
    appConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }
  
  // Merge with environment-specific config
  if (fs.existsSync(envConfigPath)) {
    const envConfig = JSON.parse(fs.readFileSync(envConfigPath, 'utf8'));
    appConfig = { ...appConfig, ...envConfig };
  }
  
  return appConfig;
}

const appConfig = loadAppConfig();

// Use universal PTY fallback system that automatically selects best implementation
const PTYManager = require('./pty-fallback-system');
console.log('PTY system initialized');

class AIAssistantApp {
  constructor() {
    this.mainWindow = null;
    this.pythonBackend = null;
    this.backendManager = new BackendManager(); // Use BackendManager for backend lifecycle
    this.ptyManager = new PTYManager();
    this.isDev = process.argv.includes('--dev');
    this.appConfig = appConfig; // Use loaded app config
    this.backendPort = null; // Will be set by BackendManager
    
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
      // Use BackendManager to auto-start backend with port discovery
      this.startPythonBackend();
      this.setupIPC();
      this.setupPTYHandlers();
      // Start periodic health checks
      this.startHealthMonitoring();
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
     * Use BackendManager for automatic backend startup with port discovery
     * Features: Port discovery, health checks, graceful shutdown
     */
    
    console.log('Starting backend using BackendManager...');
    
    try {
      // Start backend - BackendManager will handle port discovery
      this.backendPort = await this.backendManager.start();
      console.log(`Backend started on port ${this.backendPort}`);
      
      // Update app config with discovered port
      this.appConfig.backend.port = this.backendPort;
      
      // Notify renderer of backend status
      this.notifyBackendStatus('connected', this.backendPort);
      
      // Set up shutdown handler
      this.backendManager.onShutdown(async () => {
        console.log('Backend shutdown initiated');
        this.notifyBackendStatus('disconnected', null);
      });
      
      return true;
      
    } catch (error) {
      console.error('Failed to start backend:', error);
      this.notifyBackendStatus('failed', null);
      this.showBackendErrorDialog(`backend-${Date.now()}`);
      return false;
    }
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
      `3. No available ports in range 8000-9000\n` +
      `4. Antivirus blocking the backend\n\n` +
      `Correlation ID: ${correlationId}\n\n` +
      `Check the console (Ctrl+Shift+I) for detailed error messages.`
    );
  }

  startHealthMonitoring() {
    /**
     * Monitor backend health and restart if necessary
     */
    setInterval(async () => {
      const status = this.backendManager.getStatus();
      
      if (status.isRunning && status.port) {
        // Check if backend is actually healthy
        const healthy = await status.healthy;
        if (!healthy) {
          console.warn('Backend health check failed, attempting restart...');
          try {
            this.backendPort = await this.backendManager.restart();
            this.notifyBackendStatus('reconnected', this.backendPort);
          } catch (error) {
            console.error('Failed to restart backend:', error);
            this.notifyBackendStatus('failed', null);
          }
        }
      }
    }, 30000); // Check every 30 seconds
  }


  setupIPC() {
    /**
     * Business Context: Inter-process communication for frontend-backend interaction
     * Security: Validate all IPC messages
     * Performance: Async handlers for non-blocking operations
     */
    
    // Configuration Handler
    ipcMain.handle('get-config', async () => {
      return this.appConfig;
    });
    
    // Environment check
    ipcMain.handle('get-environment', async () => {
      return {
        isDevelopment: this.isDev,
        environment: this.appConfig.app?.environment || 'development'
      };
    });
    
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
     * Error Handling: BackendManager handles graceful shutdown
     */
    console.log('Cleaning up...');
    
    // Kill all PTY sessions
    this.ptyManager.killAllSessions();
    
    // Use BackendManager for clean backend shutdown
    if (this.backendManager) {
      console.log('Stopping backend via BackendManager...');
      this.backendManager.cleanup().catch(error => {
        console.error('Backend cleanup error:', error);
      });
    }
  }
}

// Global error handlers to prevent crashes
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  // Log to file for debugging
  const errorLog = `[${new Date().toISOString()}] Uncaught Exception: ${error.stack}\n`;
  try {
    const logPath = path.join(app.getPath('userData'), 'error.log');
    fs.appendFileSync(logPath, errorLog);
  } catch (e) {
    // Ignore logging errors
  }
  
  // Don't exit on EPIPE errors
  if (error.code === 'EPIPE') {
    console.log('Ignoring EPIPE error - likely backend shutdown');
    return;
  }
  
  // For other critical errors, show dialog and exit
  if (app.isReady()) {
    dialog.showErrorBox('Critical Error', error.message);
  }
  app.quit();
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Log to file for debugging
  const errorLog = `[${new Date().toISOString()}] Unhandled Rejection: ${reason}\n`;
  try {
    const logPath = path.join(app.getPath('userData'), 'error.log');
    fs.appendFileSync(logPath, errorLog);
  } catch (e) {
    // Ignore logging errors
  }
});

// Start the application
new AIAssistantApp();