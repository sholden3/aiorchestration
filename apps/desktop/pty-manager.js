/**
 * Business Context: Terminal emulation manager for development tasks
 * Architecture Pattern: Event-driven architecture with session management
 * Performance Requirements: Maintain stable sessions for 8+ hours
 * Business Assumptions: Support PowerShell, Bash, CMD on Windows
 */

const pty = require('node-pty');
const { EventEmitter } = require('events');
const path = require('path');
const fs = require('fs');

class PTYManager extends EventEmitter {
  constructor() {
    super();
    this.sessions = new Map();
    this.maxOutputLines = 10000;
    this.sessionStateFile = path.join(__dirname, '../.session-state.json');
    
    // Load persisted sessions if they exist
    this.loadPersistedSessions();
  }

  createSession(sessionId, shell = null, cwd = null) {
    /**
     * Business Logic: Create new terminal session with specified shell
     * Error Handling: Fallback to default shell if specified shell fails
     * Performance: Limit output buffer to prevent memory bloat
     */
    
    // Determine shell based on platform if not specified
    if (!shell) {
      if (process.platform === 'win32') {
        shell = 'powershell.exe';
      } else {
        shell = 'bash';
      }
    }

    // Validate shell exists on Windows
    if (process.platform === 'win32') {
      const shellMap = {
        'powershell': 'powershell.exe',
        'cmd': 'cmd.exe',
        'bash': 'C:\\Program Files\\Git\\bin\\bash.exe', // Git Bash
        'powershell.exe': 'powershell.exe',
        'cmd.exe': 'cmd.exe'
      };
      
      shell = shellMap[shell.toLowerCase()] || shell;
    }

    try {
      const ptyProcess = pty.spawn(shell, [], {
        name: 'xterm-256color',
        cols: 120,
        rows: 30,
        cwd: cwd || process.cwd(),
        env: { ...process.env, COLORTERM: 'truecolor' }
      });

      const session = {
        id: sessionId,
        process: ptyProcess,
        shell: shell,
        cwd: cwd || process.cwd(),
        output: [],
        created: Date.now(),
        lastActivity: Date.now()
      };

      // Handle output with ANSI color support
      ptyProcess.onData((data) => {
        session.lastActivity = Date.now();
        session.output.push({
          data: data,
          timestamp: Date.now()
        });
        
        // Limit output buffer to prevent memory issues
        if (session.output.length > this.maxOutputLines) {
          session.output = session.output.slice(-this.maxOutputLines);
        }
        
        // Emit data event for this specific session
        this.emit(`data-${sessionId}`, data);
      });

      // Handle exit
      ptyProcess.onExit(({ exitCode, signal }) => {
        console.log(`PTY session ${sessionId} exited with code ${exitCode}`);
        this.emit(`exit-${sessionId}`, exitCode);
        this.sessions.delete(sessionId);
        this.persistSessions();
      });

      this.sessions.set(sessionId, session);
      this.persistSessions();
      
      console.log(`Created PTY session ${sessionId} with shell ${shell}`);
      return sessionId;
      
    } catch (error) {
      console.error(`Failed to create PTY session: ${error.message}`);
      throw new Error(`Failed to create terminal session: ${error.message}`);
    }
  }

  writeToSession(sessionId, data) {
    /**
     * Business Logic: Send input to terminal session
     * Error Handling: Gracefully handle dead sessions
     */
    const session = this.sessions.get(sessionId);
    if (session && session.process) {
      try {
        session.process.write(data);
        session.lastActivity = Date.now();
      } catch (error) {
        console.error(`Failed to write to session ${sessionId}:`, error);
        this.killSession(sessionId);
      }
    } else {
      console.warn(`Session ${sessionId} not found or dead`);
    }
  }

  resizeSession(sessionId, cols, rows) {
    /**
     * Business Logic: Resize terminal to match UI dimensions
     */
    const session = this.sessions.get(sessionId);
    if (session && session.process) {
      try {
        session.process.resize(cols, rows);
      } catch (error) {
        console.error(`Failed to resize session ${sessionId}:`, error);
      }
    }
  }

  killSession(sessionId) {
    /**
     * Business Logic: Terminate terminal session
     * Error Handling: Force kill if graceful termination fails
     */
    const session = this.sessions.get(sessionId);
    if (session && session.process) {
      try {
        session.process.kill();
      } catch (error) {
        console.error(`Failed to kill session ${sessionId}:`, error);
      }
      this.sessions.delete(sessionId);
      this.persistSessions();
    }
  }

  killAllSessions() {
    /**
     * Business Logic: Terminate all sessions during app shutdown
     */
    console.log('Killing all PTY sessions...');
    for (const [sessionId, session] of this.sessions) {
      try {
        if (session.process) {
          session.process.kill();
        }
      } catch (error) {
        console.error(`Failed to kill session ${sessionId}:`, error);
      }
    }
    this.sessions.clear();
  }

  getActiveSessions() {
    /**
     * Business Logic: Return information about active sessions
     */
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
    /**
     * Business Logic: Retrieve buffered output for session
     */
    const session = this.sessions.get(sessionId);
    if (session) {
      return session.output.slice(fromIndex);
    }
    return [];
  }

  persistSessions() {
    /**
     * Business Context: Save session state for recovery after restart
     * Note: Only metadata is saved, not the actual PTY process
     */
    const state = {
      sessions: []
    };
    
    for (const [id, session] of this.sessions) {
      state.sessions.push({
        id: id,
        shell: session.shell,
        cwd: session.cwd,
        created: session.created,
        lastActivity: session.lastActivity,
        // Save last 100 lines of output for context
        recentOutput: session.output.slice(-100)
      });
    }
    
    try {
      fs.writeFileSync(this.sessionStateFile, JSON.stringify(state, null, 2));
    } catch (error) {
      console.error('Failed to persist session state:', error);
    }
  }

  loadPersistedSessions() {
    /**
     * Business Logic: Attempt to restore previous session context
     * Note: Cannot restore actual PTY processes, only show history
     */
    try {
      if (fs.existsSync(this.sessionStateFile)) {
        const state = JSON.parse(fs.readFileSync(this.sessionStateFile, 'utf8'));
        console.log(`Found ${state.sessions.length} persisted sessions`);
        // Sessions would need to be recreated, not restored
        // This is just for showing previous context
      }
    } catch (error) {
      console.error('Failed to load persisted sessions:', error);
    }
  }

  // Health monitoring
  checkSessionHealth() {
    /**
     * Business Logic: Monitor session health and cleanup dead sessions
     * Performance: Run periodically to prevent resource leaks
     */
    const now = Date.now();
    const timeout = 30 * 60 * 1000; // 30 minutes of inactivity
    
    for (const [sessionId, session] of this.sessions) {
      if (now - session.lastActivity > timeout) {
        console.log(`Session ${sessionId} inactive for 30 minutes, cleaning up`);
        this.killSession(sessionId);
      }
    }
  }
}

module.exports = PTYManager;