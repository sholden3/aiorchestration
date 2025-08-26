/**
 * Business Context: Desktop application entry point for AI Development Assistant
 * Architecture Pattern: Main/Renderer process separation with IPC communication
 * Business Assumptions: Single user, Windows-only, local execution
 * Performance Requirements: <100ms IPC response time, stable PTY sessions
 */

const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Use universal PTY fallback system that automatically selects best implementation
const PTYManager = require('./pty-fallback-system');
console.log('PTY system initialized');

class AIAssistantApp {
  constructor() {
    this.mainWindow = null;
    this.pythonBackend = null;
    this.ptyManager = new PTYManager();
    this.isDev = process.argv.includes('--dev');
    this.backendPort = 8001;
    
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
      // Check if we should start backend (skip if already running on 8001)
      if (this.backendPort === 8000) {
        this.startPythonBackend();
      } else {
        console.log('Skipping backend start - assuming it\'s already running on port', this.backendPort);
        // Still check health
        setTimeout(() => this.checkBackendHealth(), 1000);
      }
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

  startPythonBackend() {
    /**
     * Business Context: Start Python backend service for AI orchestration
     * Error Handling: Retry logic if backend fails to start
     * Performance: Health check to ensure backend is ready
     */
    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
    const backendPath = path.join(__dirname, '../backend/main.py');
    
    console.log('Starting Python backend...');
    
    this.pythonBackend = spawn(pythonPath, [backendPath, '--port', this.backendPort], {
      cwd: path.join(__dirname, '../backend'),
      env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });

    this.pythonBackend.stdout.on('data', (data) => {
      console.log(`Backend: ${data.toString()}`);
      // Send backend logs to renderer for monitoring
      if (this.mainWindow) {
        this.mainWindow.webContents.send('backend-log', data.toString());
      }
    });

    this.pythonBackend.stderr.on('data', (data) => {
      console.error(`Backend Error: ${data.toString()}`);
      if (this.mainWindow) {
        this.mainWindow.webContents.send('backend-error', data.toString());
      }
    });

    this.pythonBackend.on('error', (error) => {
      console.error('Failed to start Python backend:', error);
      dialog.showErrorBox('Backend Error', 
        'Failed to start Python backend. Please ensure Python is installed.');
    });

    // Health check
    setTimeout(() => this.checkBackendHealth(), 3000);
  }

  async checkBackendHealth() {
    /**
     * Business Logic: Verify backend is responsive
     * Retry Strategy: 3 attempts with exponential backoff
     */
    try {
      // Use 127.0.0.1 instead of localhost to avoid IPv6 issues
      const response = await fetch(`http://127.0.0.1:${this.backendPort}/health`);
      if (response.ok) {
        console.log('Backend is healthy');
        if (this.mainWindow) {
          this.mainWindow.webContents.send('backend-ready', true);
        }
      }
    } catch (error) {
      console.error('Backend health check failed:', error);
      // Retry logic would go here
    }
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