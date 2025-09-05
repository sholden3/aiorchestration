/**
 * Universal PTY Fallback System
 * Provides terminal functionality with multiple fallback layers
 * Priority: node-pty > Windows native > child_process > mock
 */

const { EventEmitter } = require('events');
const { spawn } = require('child_process');
const os = require('os');
const path = require('path');

class UniversalPTYManager extends EventEmitter {
  constructor() {
    super();
    this.implementation = null;
    this.sessions = new Map();
    this.initializeImplementation();
  }

  initializeImplementation() {
    console.log('Initializing PTY system...');
    
    // Try 1: node-pty (best option if available)
    try {
      const pty = require('node-pty');
      this.implementation = 'node-pty';
      this.PTYClass = NodePTYWrapper;
      console.log('✓ Using node-pty (full PTY support)');
      return;
    } catch (e) {
      console.log('✗ node-pty not available:', e.message);
    }

    // Try 2: Windows native terminal (good for Windows)
    if (os.platform() === 'win32') {
      try {
        this.implementation = 'windows-native';
        this.PTYClass = WindowsNativePTY;
        console.log('✓ Using Windows native terminal');
        return;
      } catch (e) {
        console.log('✗ Windows native failed:', e.message);
      }
    }

    // Try 3: Basic child_process (works everywhere)
    try {
      this.implementation = 'child-process';
      this.PTYClass = ChildProcessPTY;
      console.log('✓ Using child_process fallback');
      return;
    } catch (e) {
      console.log('✗ Child process failed:', e.message);
    }

    // Try 4: Mock implementation (last resort)
    this.implementation = 'mock';
    this.PTYClass = MockPTY;
    console.log('⚠ Using mock PTY (no real terminal functionality)');
  }

  createSession(sessionId, shell = null, cwd = null) {
    try {
      const ptyInstance = new this.PTYClass(shell, [], { cwd });
      
      const session = {
        id: sessionId,
        pty: ptyInstance,
        shell: ptyInstance.shell || shell,
        cwd: cwd || process.cwd(),
        output: [],
        created: Date.now(),
        lastActivity: Date.now(),
        implementation: this.implementation
      };

      // Forward events
      ptyInstance.on('data', (data) => {
        session.lastActivity = Date.now();
        session.output.push({ data, timestamp: Date.now() });
        if (session.output.length > 10000) {
          session.output = session.output.slice(-10000);
        }
        this.emit(`data-${sessionId}`, data);
      });

      ptyInstance.on('exit', (code) => {
        this.emit(`exit-${sessionId}`, code);
        this.sessions.delete(sessionId);
      });

      this.sessions.set(sessionId, session);
      console.log(`Created ${this.implementation} session: ${sessionId}`);
      return sessionId;
    } catch (error) {
      console.error('Failed to create session:', error);
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
    if (session && session.pty && session.pty.resize) {
      session.pty.resize(cols, rows);
    }
  }

  killSession(sessionId) {
    const session = this.sessions.get(sessionId);
    if (session && session.pty) {
      if (session.pty.kill) {
        session.pty.kill();
      } else if (session.pty.destroy) {
        session.pty.destroy();
      }
      this.sessions.delete(sessionId);
    }
  }

  killAllSessions() {
    for (const [sessionId] of this.sessions) {
      this.killSession(sessionId);
    }
  }

  getActiveSessions() {
    return Array.from(this.sessions.values()).map(s => ({
      id: s.id,
      shell: s.shell,
      cwd: s.cwd,
      created: s.created,
      lastActivity: s.lastActivity,
      outputLines: s.output.length,
      implementation: s.implementation
    }));
  }

  getSessionOutput(sessionId, fromIndex = 0) {
    const session = this.sessions.get(sessionId);
    return session ? session.output.slice(fromIndex) : [];
  }

  checkSessionHealth() {
    const now = Date.now();
    const timeout = 30 * 60 * 1000;
    for (const [sessionId, session] of this.sessions) {
      if (now - session.lastActivity > timeout) {
        console.log(`Session ${sessionId} inactive, cleaning up`);
        this.killSession(sessionId);
      }
    }
  }

  getImplementation() {
    return this.implementation;
  }

  // Compatibility methods
  persistSessions() {}
  loadPersistedSessions() {}
}

// Implementation 1: node-pty wrapper
class NodePTYWrapper extends EventEmitter {
  constructor(shell, args, options) {
    super();
    const pty = require('node-pty');
    
    this.shell = shell || (os.platform() === 'win32' ? 'powershell.exe' : 'bash');
    this.pty = pty.spawn(this.shell, args, {
      name: 'xterm-256color',
      cols: options.cols || 80,
      rows: options.rows || 24,
      cwd: options.cwd || process.cwd(),
      env: process.env
    });

    this.pty.onData((data) => this.emit('data', data));
    this.pty.onExit(({ exitCode }) => this.emit('exit', exitCode));
  }

  write(data) {
    this.pty.write(data);
  }

  resize(cols, rows) {
    this.pty.resize(cols, rows);
  }

  kill() {
    this.pty.kill();
  }
}

// Implementation 2: Windows Native
class WindowsNativePTY extends EventEmitter {
  constructor(shell, args, options) {
    super();
    
    this.shell = shell || 'powershell.exe';
    this.process = spawn(this.shell, args, {
      cwd: options.cwd || process.cwd(),
      env: process.env,
      shell: false
    });

    this.process.stdout.on('data', (data) => {
      this.emit('data', data.toString());
    });

    this.process.stderr.on('data', (data) => {
      this.emit('data', data.toString());
    });

    this.process.on('exit', (code) => {
      this.emit('exit', code);
    });

    // Clear initial output for cleaner display
    if (this.shell.includes('powershell')) {
      setTimeout(() => this.write('cls\r\n'), 100);
    }
  }

  write(data) {
    if (this.process && this.process.stdin) {
      this.process.stdin.write(data.replace(/\n/g, '\r\n'));
    }
  }

  resize(cols, rows) {
    // Try to resize if PowerShell
    if (this.shell.includes('powershell')) {
      this.write(`$host.UI.RawUI.WindowSize = @{Width=${cols};Height=${rows}}\r\n`);
    }
  }

  kill() {
    if (this.process) {
      this.process.kill();
    }
  }
}

// Implementation 3: Basic child_process
class ChildProcessPTY extends EventEmitter {
  constructor(shell, args, options) {
    super();
    
    const isWin = os.platform() === 'win32';
    this.shell = shell || (isWin ? 'cmd.exe' : 'sh');
    
    this.process = spawn(this.shell, args, {
      cwd: options.cwd || process.cwd(),
      env: process.env,
      shell: true
    });

    this.process.stdout.on('data', (data) => {
      this.emit('data', data.toString());
    });

    this.process.stderr.on('data', (data) => {
      this.emit('data', data.toString());
    });

    this.process.on('exit', (code) => {
      this.emit('exit', code);
    });

    this.emit('data', `Connected to ${this.shell}\r\n`);
  }

  write(data) {
    if (this.process && this.process.stdin) {
      this.process.stdin.write(data);
    }
  }

  resize() {
    // Not supported in basic mode
  }

  kill() {
    if (this.process) {
      this.process.kill();
    }
  }
}

// Implementation 4: Mock PTY
class MockPTY extends EventEmitter {
  constructor(shell, args, options) {
    super();
    this.shell = shell || 'mock-shell';
    this.cwd = options.cwd || process.cwd();
    
    setTimeout(() => {
      this.emit('data', 
        `╔════════════════════════════════════════════════╗\r\n` +
        `║  Mock Terminal (No real shell access)         ║\r\n` +
        `║  Please install node-pty for full support     ║\r\n` +
        `╚════════════════════════════════════════════════╝\r\n` +
        `\r\n` +
        `Working directory: ${this.cwd}\r\n` +
        `> `
      );
    }, 100);
  }

  write(data) {
    // Echo back with mock response
    this.emit('data', data);
    
    if (data.trim()) {
      setTimeout(() => {
        this.emit('data', 
          `Mock output: Command "${data.trim()}" received but not executed\r\n> `
        );
      }, 100);
    }
  }

  resize() {}
  
  kill() {
    this.emit('exit', 0);
  }
}

module.exports = UniversalPTYManager;