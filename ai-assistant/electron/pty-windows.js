/**
 * Windows PTY Alternative using child_process
 * This provides terminal functionality without requiring node-pty compilation
 */

const { spawn } = require('child_process');
const { EventEmitter } = require('events');
const path = require('path');
const os = require('os');

class WindowsPTY extends EventEmitter {
  constructor(shell, args = [], options = {}) {
    super();
    
    this.shell = shell || this.getDefaultShell();
    this.args = args;
    this.cwd = options.cwd || process.cwd();
    this.env = options.env || process.env;
    this.cols = options.cols || 80;
    this.rows = options.rows || 24;
    this.process = null;
    this.isAlive = false;
    
    this.spawn();
  }
  
  getDefaultShell() {
    // Prefer PowerShell Core, then Windows PowerShell, then CMD
    const shells = [
      'pwsh.exe',        // PowerShell Core
      'powershell.exe',  // Windows PowerShell
      'cmd.exe'          // Command Prompt
    ];
    
    // For now, use PowerShell as default
    return 'powershell.exe';
  }
  
  spawn() {
    try {
      // Spawn the shell process
      this.process = spawn(this.shell, this.args, {
        cwd: this.cwd,
        env: {
          ...this.env,
          TERM: 'xterm-256color',
          COLUMNS: this.cols,
          LINES: this.rows
        },
        shell: false,
        windowsHide: false
      });
      
      this.isAlive = true;
      
      // Handle stdout
      this.process.stdout.on('data', (data) => {
        this.emit('data', data.toString());
      });
      
      // Handle stderr
      this.process.stderr.on('data', (data) => {
        this.emit('data', data.toString());
      });
      
      // Handle exit
      this.process.on('exit', (code, signal) => {
        this.isAlive = false;
        this.emit('exit', { exitCode: code, signal });
      });
      
      // Handle errors
      this.process.on('error', (error) => {
        console.error('Process error:', error);
        this.emit('error', error);
      });
      
      // Send initial prompt for PowerShell
      if (this.shell.includes('powershell')) {
        // Clear the initial banner for cleaner output
        this.write('clear\r\n');
      }
      
    } catch (error) {
      console.error('Failed to spawn shell:', error);
      this.emit('error', error);
      throw error;
    }
  }
  
  write(data) {
    if (this.process && this.process.stdin && this.isAlive) {
      try {
        // Convert line endings for Windows
        const windowsData = data.replace(/\n/g, '\r\n');
        this.process.stdin.write(windowsData);
      } catch (error) {
        console.error('Write error:', error);
      }
    }
  }
  
  resize(cols, rows) {
    this.cols = cols;
    this.rows = rows;
    
    // On Windows, we can try to send a resize command
    if (this.shell.includes('powershell')) {
      this.write(`$host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size(${cols}, ${rows})\r\n`);
    }
  }
  
  kill(signal = 'SIGTERM') {
    if (this.process && this.isAlive) {
      try {
        // Windows doesn't support signals the same way
        // Use taskkill for forceful termination
        if (signal === 'SIGKILL' || signal === 9) {
          spawn('taskkill', ['/PID', this.process.pid, '/F']);
        } else {
          this.process.kill();
        }
      } catch (error) {
        console.error('Kill error:', error);
      }
    }
  }
  
  destroy() {
    this.kill();
    this.removeAllListeners();
  }
}

class WindowsPTYManager extends EventEmitter {
  constructor() {
    super();
    this.sessions = new Map();
    console.log('Windows PTY Manager initialized');
  }
  
  createSession(sessionId, shell = null, cwd = null) {
    console.log(`Creating Windows PTY session: ${sessionId}`);
    
    try {
      const pty = new WindowsPTY(shell, [], { cwd });
      
      const session = {
        id: sessionId,
        pty: pty,
        shell: pty.shell,
        cwd: cwd || process.cwd(),
        output: [],
        created: Date.now(),
        lastActivity: Date.now()
      };
      
      // Forward PTY events
      pty.on('data', (data) => {
        session.lastActivity = Date.now();
        session.output.push({
          data: data,
          timestamp: Date.now()
        });
        
        // Limit output buffer
        if (session.output.length > 10000) {
          session.output = session.output.slice(-10000);
        }
        
        this.emit(`data-${sessionId}`, data);
      });
      
      pty.on('exit', ({ exitCode }) => {
        console.log(`Session ${sessionId} exited with code ${exitCode}`);
        this.emit(`exit-${sessionId}`, exitCode);
        this.sessions.delete(sessionId);
      });
      
      this.sessions.set(sessionId, session);
      console.log(`Created session ${sessionId} with shell ${pty.shell}`);
      
      return sessionId;
      
    } catch (error) {
      console.error(`Failed to create session: ${error.message}`);
      throw error;
    }
  }
  
  writeToSession(sessionId, data) {
    const session = this.sessions.get(sessionId);
    if (session && session.pty) {
      session.pty.write(data);
      session.lastActivity = Date.now();
    }
  }
  
  resizeSession(sessionId, cols, rows) {
    const session = this.sessions.get(sessionId);
    if (session && session.pty) {
      session.pty.resize(cols, rows);
    }
  }
  
  killSession(sessionId) {
    const session = this.sessions.get(sessionId);
    if (session && session.pty) {
      session.pty.kill();
      this.sessions.delete(sessionId);
    }
  }
  
  killAllSessions() {
    console.log('Killing all Windows PTY sessions...');
    for (const [sessionId, session] of this.sessions) {
      if (session.pty) {
        session.pty.kill();
      }
    }
    this.sessions.clear();
  }
  
  getActiveSessions() {
    const sessions = [];
    for (const [id, session] of this.sessions) {
      sessions.push({
        id: id,
        shell: session.shell,
        cwd: session.cwd,
        created: session.created,
        lastActivity: session.lastActivity,
        outputLines: session.output.length
      });
    }
    return sessions;
  }
  
  getSessionOutput(sessionId, fromIndex = 0) {
    const session = this.sessions.get(sessionId);
    if (session) {
      return session.output.slice(fromIndex);
    }
    return [];
  }
  
  checkSessionHealth() {
    const now = Date.now();
    const timeout = 30 * 60 * 1000; // 30 minutes
    
    for (const [sessionId, session] of this.sessions) {
      if (now - session.lastActivity > timeout) {
        console.log(`Session ${sessionId} inactive, cleaning up`);
        this.killSession(sessionId);
      }
    }
  }
  
  // Compatibility methods for PTY manager interface
  persistSessions() {
    // No-op for now
  }
  
  loadPersistedSessions() {
    // No-op for now
  }
}

module.exports = WindowsPTYManager;