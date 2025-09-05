/**
 * Business Context: Secure bridge between renderer and main process
 * Security: Context isolation with controlled API exposure
 * Architecture Pattern: Facade pattern for IPC communication
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to communicate
// with the main process without exposing the entire Electron API
contextBridge.exposeInMainWorld('electronAPI', {
  // Configuration
  getConfig: () => ipcRenderer.invoke('get-config'),
  getEnvironment: () => ipcRenderer.invoke('get-environment'),
  
  // AI Operations
  executeAITask: (task) => ipcRenderer.invoke('execute-ai-task', task),
  getCacheMetrics: () => ipcRenderer.invoke('get-cache-metrics'),
  suggestPersona: (description) => ipcRenderer.invoke('suggest-persona', description),
  
  // Terminal Operations - Using the exact same channel names as main.js
  createTerminalSession: (options) => {
    return new Promise((resolve, reject) => {
      const { sessionId } = options;
      
      // Set up one-time listener for response
      ipcRenderer.once(`terminal-session-created-${sessionId}`, (event, result) => {
        if (result.error) {
          reject(new Error(result.error));
        } else {
          resolve(result.sessionId);
        }
      });
      
      // Send the request
      ipcRenderer.send('create-terminal-session', options);
    });
  },
  
  writeToTerminal: (sessionId, data) => {
    ipcRenderer.send('terminal-write', { sessionId, data });
  },
  
  resizeTerminal: (sessionId, cols, rows) => {
    ipcRenderer.send('terminal-resize', { sessionId, cols, rows });
  },
  
  killTerminal: (sessionId) => {
    ipcRenderer.send('terminal-kill', { sessionId });
  },
  
  getTerminalSessions: () => {
    return new Promise((resolve) => {
      ipcRenderer.once('terminal-sessions-list', (event, sessions) => {
        resolve(sessions);
      });
      ipcRenderer.send('get-terminal-sessions');
    });
  },
  
  getTerminalOutput: (sessionId, fromIndex) => {
    return new Promise((resolve) => {
      ipcRenderer.once(`terminal-output-${sessionId}`, (event, output) => {
        resolve(output);
      });
      ipcRenderer.send('get-terminal-output', { sessionId, fromIndex });
    });
  },
  
  // Terminal Event Listeners
  onTerminalOutput: (callback) => {
    const listener = (event, data) => callback(data);
    ipcRenderer.on('terminal-output', listener);
    // Return cleanup function
    return () => ipcRenderer.removeListener('terminal-output', listener);
  },
  
  onTerminalExit: (callback) => {
    const listener = (event, data) => callback(data);
    ipcRenderer.on('terminal-exit', listener);
    // Return cleanup function
    return () => ipcRenderer.removeListener('terminal-exit', listener);
  },
  
  onTerminalSessions: (callback) => {
    const listener = (event, sessions) => callback(sessions);
    ipcRenderer.on('terminal-sessions', listener);
    // Return cleanup function
    return () => ipcRenderer.removeListener('terminal-sessions', listener);
  },
  
  // Backend Events
  onBackendReady: (callback) => {
    ipcRenderer.on('backend-ready', (event, ready) => callback(ready));
  },
  
  onBackendLog: (callback) => {
    ipcRenderer.on('backend-log', (event, log) => callback(log));
  },
  
  onBackendError: (callback) => {
    ipcRenderer.on('backend-error', (event, error) => callback(error));
  },
  
  // File System Operations
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  
  // External Links
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  
  // App Info
  getVersion: () => ipcRenderer.invoke('get-app-version'),
  getPlatform: () => process.platform,
  
  // Remove all listeners (cleanup)
  removeAllListeners: () => {
    ipcRenderer.removeAllListeners();
  }
});