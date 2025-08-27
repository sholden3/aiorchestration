/**
 * @fileoverview Centralized configuration for Electron application
 * @author Alex Novak v3.0 - 2025-01-27
 * @purpose FIX C3: Centralized configuration to prevent mismatches
 * @governance Configuration management for consistent behavior
 */

module.exports = {
  backend: {
    // FIX C3: Ensure consistent port configuration
    port: process.env.BACKEND_PORT || 8000,
    host: process.env.BACKEND_HOST || '127.0.0.1',
    protocol: 'http',
    
    // Startup configuration
    startup: {
      maxRetries: 3,
      retryDelay: 2000,  // Base delay, will use exponential backoff
      healthCheckTimeout: 5000,
      startupTimeout: 30000
    },
    
    // API endpoints
    endpoints: {
      health: '/health',
      ai: '/ai/execute',
      metrics: '/metrics/cache',
      persona: '/persona/suggest',
      websocket: '/ws'
    }
  },
  
  ipc: {
    // IPC communication settings
    timeout: 10000,
    maxMessageSize: 10 * 1024 * 1024,  // 10MB
    
    // Security settings
    security: {
      validateMessages: true,
      maxChannels: 50,
      rateLimit: 100  // Max messages per minute per channel
    }
  },
  
  pty: {
    // Terminal settings
    maxSessions: 10,
    defaultShell: process.platform === 'win32' 
      ? process.env.COMSPEC || 'powershell.exe'
      : process.env.SHELL || '/bin/bash',
    defaultCols: 80,
    defaultRows: 30,
    
    // Terminal resource limits
    limits: {
      maxOutputBuffer: 1024 * 1024,  // 1MB per terminal
      maxIdleTime: 300000  // 5 minutes idle timeout
    }
  },
  
  window: {
    // Main window configuration
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    
    // Development settings
    dev: {
      openDevTools: false,
      reloadOnChange: true
    }
  },
  
  // Logging configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    file: process.env.LOG_FILE || './logs/electron.log',
    maxSize: 10 * 1024 * 1024,  // 10MB
    maxFiles: 5,
    
    // Include correlation IDs in all logs
    includeCorrelationId: true
  },
  
  // Performance monitoring
  monitoring: {
    enabled: process.env.ENABLE_MONITORING !== 'false',
    metricsInterval: 60000,  // Collect metrics every minute
    
    // Thresholds for alerts
    thresholds: {
      memoryUsage: 1024 * 1024 * 1024,  // 1GB
      cpuUsage: 80,  // 80% CPU
      responseTime: 1000  // 1 second
    }
  },
  
  // Get backend URL helper
  getBackendUrl(endpoint = '') {
    const config = module.exports;
    return `${config.backend.protocol}://${config.backend.host}:${config.backend.port}${endpoint}`;
  },
  
  // Validate configuration
  validate() {
    const config = module.exports;
    const errors = [];
    
    // Validate port
    if (config.backend.port < 1 || config.backend.port > 65535) {
      errors.push(`Invalid port: ${config.backend.port}`);
    }
    
    // Validate required environment
    if (!['win32', 'darwin', 'linux'].includes(process.platform)) {
      errors.push(`Unsupported platform: ${process.platform}`);
    }
    
    // Validate Python availability (will be checked at runtime)
    
    if (errors.length > 0) {
      console.error('Configuration errors:', errors);
      return false;
    }
    
    return true;
  }
};

// Self-validate on load
if (!module.exports.validate()) {
  console.warn('Configuration validation failed - using defaults');
}