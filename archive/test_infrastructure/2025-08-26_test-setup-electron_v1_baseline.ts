// src/test-setup-electron.ts - Alex's Electron-specific mocks
import { BehaviorSubject } from 'rxjs';

// Comprehensive Electron API mock with realistic failure scenarios
const mockElectronAPI = {
  // IPC operations with circuit breaker simulation
  invoke: jest.fn().mockImplementation(async (channel: string, data?: any) => {
    // Simulate realistic IPC failures
    if (mockElectronAPI._failureRate > Math.random()) {
      const error = new Error(`IPC failed: ${channel}`);
      (error as any).name = 'IPCError';
      throw error;
    }
    
    // Simulate network delays
    await new Promise(resolve => setTimeout(resolve, Math.random() * 10));
    
    return { success: true, data, channel };
  }),
  
  send: jest.fn(),
  
  // PTY operations with resource tracking
  createPty: jest.fn().mockImplementation((options = {}) => {
    if (mockElectronAPI._ptyCount >= mockElectronAPI._maxPtyProcesses) {
      throw new Error('Maximum PTY processes exceeded');
    }
    
    const ptyId = `mock-pty-${Date.now()}-${Math.random()}`;
    mockElectronAPI._ptyCount++;
    mockElectronAPI._activePtys.add(ptyId);
    
    return ptyId;
  }),
  
  killPty: jest.fn().mockImplementation((ptyId: string) => {
    if (mockElectronAPI._activePtys.has(ptyId)) {
      mockElectronAPI._activePtys.delete(ptyId);
      mockElectronAPI._ptyCount--;
    }
    return true;
  }),
  
  writeToPty: jest.fn().mockImplementation((ptyId: string, data: string) => {
    if (!mockElectronAPI._activePtys.has(ptyId)) {
      throw new Error(`PTY ${ptyId} not found`);
    }
    return true;
  }),
  
  resizePty: jest.fn().mockImplementation((ptyId: string, cols: number, rows: number) => {
    if (!mockElectronAPI._activePtys.has(ptyId)) {
      throw new Error(`PTY ${ptyId} not found`);
    }
    return true;
  }),
  
  onPtyData: jest.fn().mockImplementation((callback: (event: any, data: any) => void) => {
    // Simulate some PTY output
    setTimeout(() => {
      callback({}, { ptyId: 'mock-pty', data: 'Mock terminal output\r\n' });
    }, 100);
    return () => {}; // Return unsubscribe function
  }),
  
  onPtyExit: jest.fn().mockImplementation((callback: (event: any, data: any) => void) => {
    return () => {}; // Return unsubscribe function
  }),
  
  // System information
  getSystemInfo: jest.fn().mockResolvedValue({
    platform: 'linux',
    arch: 'x64',
    nodeVersion: '18.17.0',
    electronVersion: '28.0.0'
  }),
  
  // File operations
  selectDirectory: jest.fn().mockResolvedValue('/mock/directory/path'),
  selectFile: jest.fn().mockResolvedValue('/mock/file/path.txt'),
  readFile: jest.fn().mockResolvedValue('Mock file contents'),
  writeFile: jest.fn().mockResolvedValue(true),
  
  // Window operations
  minimizeWindow: jest.fn(),
  maximizeWindow: jest.fn(),
  closeWindow: jest.fn(),
  isMaximized: jest.fn().mockReturnValue(false),
  
  // Internal state for testing (Sarah's monitoring approach)
  _ptyCount: 0,
  _maxPtyProcesses: 10,
  _activePtys: new Set<string>(),
  _failureRate: 0.01, // 1% failure rate by default
  
  // Test utilities
  _resetState: () => {
    mockElectronAPI._ptyCount = 0;
    mockElectronAPI._activePtys.clear();
    mockElectronAPI._failureRate = 0.01;
    jest.clearAllMocks();
  },
  
  _setFailureRate: (rate: number) => {
    mockElectronAPI._failureRate = Math.max(0, Math.min(1, rate));
  },
  
  _simulatePtyOutput: (ptyId: string, data: string) => {
    if (mockElectronAPI._activePtys.has(ptyId)) {
      const listeners = (mockElectronAPI.onPtyData as jest.Mock).mock.calls;
      listeners.forEach(([callback]) => {
        callback({}, { ptyId, data });
      });
    }
  }
};

// Global Electron mocks
(global as any).window = {
  ...((global as any).window || {}),
  electronAPI: mockElectronAPI,
  require: jest.fn(),
  process: {
    platform: 'linux',
    versions: { electron: '28.0.0', node: '18.17.0' }
  }
};

// Mock localStorage for tests
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
(global as any).localStorage = localStorageMock;

// Mock WebSocket for real-time features
class MockWebSocket {
  url: string;
  readyState: number = 1; // OPEN
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  
  constructor(url: string) {
    this.url = url;
    setTimeout(() => {
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 10);
  }
  
  send(data: string | ArrayBuffer | Blob) {
    // Mock send
  }
  
  close() {
    this.readyState = 3; // CLOSED
    if (this.onclose) {
      this.onclose(new CloseEvent('close'));
    }
  }
}
(global as any).WebSocket = MockWebSocket;

// Reset Electron state between tests
afterEach(() => {
  mockElectronAPI._resetState();
  localStorageMock.getItem.mockClear();
  localStorageMock.setItem.mockClear();
  localStorageMock.removeItem.mockClear();
  localStorageMock.clear.mockClear();
});

// Export for use in specific tests
export { mockElectronAPI, MockWebSocket, localStorageMock };