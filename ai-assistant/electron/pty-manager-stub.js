/**
 * Temporary PTY Manager Stub
 * This is a placeholder implementation that allows the app to run without node-pty
 * Replace this with the real implementation once node-pty is installed
 */

const { EventEmitter } = require('events');

class PTYManager extends EventEmitter {
  constructor() {
    super();
    this.sessions = new Map();
    console.log('PTY Manager initialized (stub mode - no real PTY functionality)');
  }

  createSession(sessionId, shell = 'cmd.exe', cwd = process.cwd()) {
    console.log(`Creating mock PTY session: ${sessionId}`);
    
    // Create a mock session
    const session = {
      id: sessionId,
      shell,
      cwd,
      output: [],
      isAlive: true,
      created: Date.now(),
      lastActivity: Date.now()
    };
    
    this.sessions.set(sessionId, session);
    
    // Emit a welcome message
    setTimeout(() => {
      const welcomeMsg = `Mock Terminal Session (${shell})\nPTY functionality will be available once node-pty is installed.\n`;
      session.output.push({
        data: welcomeMsg,
        timestamp: Date.now()
      });
      this.emit(`data-${sessionId}`, welcomeMsg);
    }, 100);
    
    return session;
  }

  writeToSession(sessionId, data) {
    const session = this.sessions.get(sessionId);
    if (!session) {
      console.error(`Session ${sessionId} not found`);
      return;
    }
    
    session.lastActivity = Date.now();
    
    // Echo the input back (mock behavior)
    const response = `> ${data}\nMock response: Command received but not executed (PTY not available)\n`;
    session.output.push({
      data: response,
      timestamp: Date.now()
    });
    this.emit(`data-${sessionId}`, response);
  }

  resizeSession(sessionId, cols, rows) {
    console.log(`Resize session ${sessionId}: ${cols}x${rows} (no-op in stub mode)`);
  }

  killSession(sessionId) {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.isAlive = false;
      this.sessions.delete(sessionId);
      this.emit(`exit-${sessionId}`, 0);
      console.log(`Killed mock session: ${sessionId}`);
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
      outputLines: s.output.length
    }));
  }

  getSessionOutput(sessionId, fromIndex = 0) {
    const session = this.sessions.get(sessionId);
    if (!session) return [];
    return session.output.slice(fromIndex);
  }

  checkSessionHealth() {
    console.log(`Health check: ${this.sessions.size} mock sessions active`);
  }
  
  persistSessions() {
    // No-op in stub mode
  }
  
  loadPersistedSessions() {
    // No-op in stub mode
  }
}

module.exports = PTYManager;