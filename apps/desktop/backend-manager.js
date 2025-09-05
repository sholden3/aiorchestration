/**
 * @fileoverview Backend Process Manager for Electron
 * @author Alex Novak - Frontend/Integration Architect
 * @description Manages Python backend process lifecycle
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const net = require('net');

class BackendManager {
  constructor() {
    this.backendProcess = null;
    this.backendPort = null;
    this.isStarting = false;
    this.isRunning = false;
    this.portFile = path.join(os.homedir(), '.ai_assistant', 'current_port.txt');
    this.stateFile = path.join(os.homedir(), '.ai_assistant', 'backend_state.json');
    this.pythonPath = this.findPython();
    this.backendPath = path.join(__dirname, '..', 'backend', 'main.py');
    this.startupTimeout = 30000; // 30 seconds
    this.healthCheckInterval = null;
    this.shutdownHandlers = [];
    this.debugMode = process.env.DEBUG_BACKEND === 'true';
    this.logBuffer = [];
    this.maxLogBufferSize = 100; // Keep last 100 log entries
  }

  /**
   * Find Python executable
   */
  findPython() {
    const possiblePaths = [
      'python',
      'python3',
      'python.exe',
      'python3.exe',
      path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python311', 'python.exe'),
      path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python310', 'python.exe'),
      '/usr/bin/python3',
      '/usr/local/bin/python3'
    ];

    for (const pythonPath of possiblePaths) {
      try {
        const result = require('child_process').execSync(`${pythonPath} --version`, { 
          encoding: 'utf8',
          stdio: 'pipe' 
        });
        if (result.includes('Python')) {
          console.log(`Found Python at: ${pythonPath}`);
          return pythonPath;
        }
      } catch (e) {
        // Try next path
      }
    }

    console.error('Python not found in PATH');
    return 'python';
  }

  /**
   * Check if a port is available
   */
  isPortAvailable(port) {
    return new Promise((resolve) => {
      const server = net.createServer();
      server.once('error', () => resolve(false));
      server.once('listening', () => {
        server.close();
        resolve(true);
      });
      server.listen(port, '127.0.0.1');
    });
  }

  /**
   * Find an available port
   */
  async findAvailablePort(preferredPort = 8000) {
    // Check preferred port first
    if (await this.isPortAvailable(preferredPort)) {
      return preferredPort;
    }

    // Scan range 8000-9000
    for (let port = 8000; port <= 9000; port++) {
      if (await this.isPortAvailable(port)) {
        return port;
      }
    }

    // Fallback to system-assigned port
    return new Promise((resolve) => {
      const server = net.createServer();
      server.listen(0, '127.0.0.1', () => {
        const port = server.address().port;
        server.close();
        resolve(port);
      });
    });
  }

  /**
   * Read port from file if exists
   */
  readPortFile() {
    try {
      if (fs.existsSync(this.portFile)) {
        const port = parseInt(fs.readFileSync(this.portFile, 'utf8').trim());
        if (!isNaN(port)) {
          return port;
        }
      }
    } catch (error) {
      console.error('Failed to read port file:', error);
    }
    return null;
  }

  /**
   * Write port to file
   */
  writePortFile(port) {
    try {
      const dir = path.dirname(this.portFile);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(this.portFile, port.toString());
      console.log(`Wrote port ${port} to ${this.portFile}`);
    } catch (error) {
      console.error('Failed to write port file:', error);
    }
  }

  /**
   * Save backend state
   */
  saveState() {
    try {
      const state = {
        port: this.backendPort,
        pid: this.backendProcess?.pid,
        isRunning: this.isRunning,
        timestamp: new Date().toISOString()
      };
      const dir = path.dirname(this.stateFile);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(this.stateFile, JSON.stringify(state, null, 2));
    } catch (error) {
      console.error('Failed to save backend state:', error);
    }
  }

  /**
   * Load backend state
   */
  loadState() {
    try {
      if (fs.existsSync(this.stateFile)) {
        return JSON.parse(fs.readFileSync(this.stateFile, 'utf8'));
      }
    } catch (error) {
      console.error('Failed to load backend state:', error);
    }
    return null;
  }

  /**
   * Start the backend process
   */
  async start() {
    if (this.isRunning || this.isStarting) {
      console.log('Backend already running or starting');
      return this.backendPort;
    }

    this.isStarting = true;

    try {
      // Check if backend is already running from previous session
      const existingPort = this.readPortFile();
      if (existingPort && await this.checkHealth(existingPort)) {
        console.log(`Backend already running on port ${existingPort}`);
        this.backendPort = existingPort;
        this.isRunning = true;
        this.isStarting = false;
        this.startHealthCheck();
        return existingPort;
      }

      // Find available port
      this.backendPort = await this.findAvailablePort(existingPort || 8000);
      console.log(`Starting backend on port ${this.backendPort}`);

      // Set environment variables
      const env = {
        ...process.env,
        APP_ENV: process.env.NODE_ENV || 'development',
        BACKEND_PORT: this.backendPort.toString()
      };

      // Start backend process
      this.backendProcess = spawn(this.pythonPath, [
        this.backendPath,
        '--port', this.backendPort.toString()
      ], {
        env,
        cwd: path.dirname(this.backendPath)
      });

      // Handle stdout with error protection and filtering
      this.backendProcess.stdout.on('data', (data) => {
        try {
          const output = data.toString().trim();
          if (output) {
            // Buffer logs for debugging
            this.addToLogBuffer(output);
            
            // Only log important messages to reduce console spam
            if (this.shouldLogOutput(output)) {
              console.log(`Backend: ${this.filterOutput(output)}`);
            }
          }
        } catch (e) {
          // Ignore pipe errors during shutdown
          if (e.code !== 'EPIPE') {
            console.error('Backend stdout error:', e.message);
          }
        }
      });

      // Handle stderr with error protection and filtering
      this.backendProcess.stderr.on('data', (data) => {
        try {
          const output = data.toString().trim();
          if (output) {
            // Buffer logs for debugging
            this.addToLogBuffer(`ERROR: ${output}`);
            
            // Filter out non-critical warnings to reduce console spam
            if (!this.isRoutineWarning(output)) {
              // Only show first line of error for readability
              const firstLine = output.split('\n')[0];
              if (firstLine.length > 200) {
                console.error(`Backend Error: ${firstLine.substring(0, 200)}...`);
              } else {
                console.error(`Backend Error: ${firstLine}`);
              }
            }
          }
        } catch (e) {
          // Ignore pipe errors during shutdown
          if (e.code !== 'EPIPE') {
            console.error('Backend stderr error:', e.message);
          }
        }
      });

      // Handle process errors
      this.backendProcess.on('error', (error) => {
        console.error('Backend process error:', error);
        this.isRunning = false;
        this.isStarting = false;
        this.backendProcess = null;
      });

      // Handle process exit
      this.backendProcess.on('exit', (code, signal) => {
        console.log(`Backend process exited with code ${code} and signal ${signal}`);
        this.isRunning = false;
        this.backendProcess = null;
        this.stopHealthCheck();
        this.saveState();
        if (this.onShutdownCallback) {
          this.onShutdownCallback();
        }
      });

      // Handle process close
      this.backendProcess.on('close', (code, signal) => {
        console.log(`Backend process closed with code ${code}, signal ${signal}`);
        if (this.backendProcess) {
          this.backendProcess = null;
        }
      });

      // Wait for backend to be ready
      await this.waitForBackend();

      // Write port to file for frontend
      this.writePortFile(this.backendPort);
      this.saveState();

      this.isRunning = true;
      this.isStarting = false;
      this.startHealthCheck();

      console.log(`Backend started successfully on port ${this.backendPort}`);
      return this.backendPort;

    } catch (error) {
      console.error('Failed to start backend:', error);
      this.isStarting = false;
      throw error;
    }
  }

  /**
   * Wait for backend to be ready
   */
  async waitForBackend() {
    const startTime = Date.now();
    
    while (Date.now() - startTime < this.startupTimeout) {
      if (await this.checkHealth(this.backendPort)) {
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    throw new Error('Backend startup timeout');
  }

  /**
   * Check backend health
   */
  async checkHealth(port) {
    if (!port) return false;

    try {
      const response = await fetch(`http://127.0.0.1:${port}/health`, {
        method: 'GET',
        timeout: 5000
      }).catch(() => null);

      return response?.ok === true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Start health check monitoring
   */
  startHealthCheck() {
    this.stopHealthCheck();
    
    this.healthCheckInterval = setInterval(async () => {
      if (this.isRunning && this.backendPort) {
        const healthy = await this.checkHealth(this.backendPort);
        if (!healthy) {
          console.warn('Backend health check failed');
          // Could implement auto-restart here
        }
      }
    }, 30000); // Check every 30 seconds
  }

  /**
   * Stop health check monitoring
   */
  stopHealthCheck() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }

  /**
   * Stop the backend process
   */
  async stop() {
    console.log('Stopping backend...');
    
    this.stopHealthCheck();

    if (this.backendProcess) {
      return new Promise((resolve) => {
        const timeout = setTimeout(() => {
          console.log('Graceful shutdown timeout, forcing kill');
          this.backendProcess.kill('SIGKILL');
          resolve();
        }, 10000);

        this.backendProcess.once('exit', () => {
          clearTimeout(timeout);
          console.log('Backend stopped gracefully');
          resolve();
        });

        // Try graceful shutdown first
        if (process.platform === 'win32') {
          // Windows doesn't support SIGTERM well, use taskkill
          const { exec } = require('child_process');
          exec(`taskkill /PID ${this.backendProcess.pid} /T /F`, (error) => {
            if (error) {
              console.error('Failed to kill process:', error);
            }
          });
        } else {
          this.backendProcess.kill('SIGTERM');
        }
      });
    }

    this.isRunning = false;
    this.backendProcess = null;
    this.saveState();
  }

  /**
   * Restart the backend
   */
  async restart() {
    await this.stop();
    await new Promise(resolve => setTimeout(resolve, 2000));
    return await this.start();
  }

  /**
   * Get backend status
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      isStarting: this.isStarting,
      port: this.backendPort,
      pid: this.backendProcess?.pid,
      healthy: this.backendPort ? this.checkHealth(this.backendPort) : false
    };
  }

  /**
   * Register shutdown handler
   */
  onShutdown(handler) {
    this.shutdownHandlers.push(handler);
  }

  /**
   * Clean shutdown
   */
  async cleanup() {
    console.log('Cleaning up backend manager...');
    
    // Run shutdown handlers
    for (const handler of this.shutdownHandlers) {
      try {
        await handler();
      } catch (error) {
        console.error('Shutdown handler error:', error);
      }
    }

    // Stop backend
    await this.stop();

    // Clean up files
    try {
      if (fs.existsSync(this.portFile)) {
        fs.unlinkSync(this.portFile);
      }
    } catch (error) {
      console.error('Failed to clean up port file:', error);
    }
  }

  /**
   * Determine if output should be logged to console
   */
  shouldLogOutput(output) {
    // Always log in debug mode
    if (this.debugMode) return true;
    
    // Skip JSON structured logs
    if (output.startsWith('{') && output.includes('"timestamp"')) {
      return false;
    }
    
    // Skip routine INFO logs
    if (output.includes('INFO:') || output.includes('[INFO]')) {
      return false;
    }
    
    // Log important messages
    if (output.includes('ERROR') || 
        output.includes('CRITICAL') ||
        output.includes('started on port') ||
        output.includes('shutdown') ||
        output.includes('failed')) {
      return true;
    }
    
    // Log startup messages
    if (output.includes('Uvicorn running') || 
        output.includes('Application startup')) {
      return true;
    }
    
    return false;
  }

  /**
   * Filter output for cleaner display
   */
  filterOutput(output) {
    // Remove excessive whitespace
    output = output.replace(/\s+/g, ' ').trim();
    
    // Truncate very long lines
    if (output.length > 500) {
      return output.substring(0, 500) + '...';
    }
    
    return output;
  }

  /**
   * Check if stderr output is a routine warning
   */
  isRoutineWarning(output) {
    const routineWarnings = [
      'UserWarning:',
      'RuntimeWarning: coroutine',
      'pydantic',
      'protected_namespaces',
      'tracemalloc',
      'DeprecationWarning',
      'Governance module',
      'INFO',
      'Configuration loaded'
    ];
    
    return routineWarnings.some(warning => output.includes(warning));
  }

  /**
   * Add output to log buffer for debugging
   */
  addToLogBuffer(output) {
    this.logBuffer.push({
      timestamp: new Date().toISOString(),
      message: output
    });
    
    // Keep buffer size limited
    if (this.logBuffer.length > this.maxLogBufferSize) {
      this.logBuffer.shift();
    }
  }

  /**
   * Get recent logs for debugging
   */
  getRecentLogs() {
    return this.logBuffer;
  }
}

module.exports = BackendManager;