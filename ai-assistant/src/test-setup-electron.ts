// src/test-setup-electron.ts - Enhanced version (v2) with realistic backend simulation
// Approved by: Alex Novak & Dr. Sarah Chen
// Date: 2025-08-26
// Related Issues: Phase 1 Enhanced Test Implementation

import { BehaviorSubject, Subject } from 'rxjs';

// Sarah's requirement: Realistic backend resource state tracking
export interface BackendResourceState {
  websocketConnections: number;
  maxConnections: number;
  databaseMaintenance: boolean;
  cacheCircuitBreakerOpen: boolean;
  cpuUsage: number;
  memoryUsage: number;
  activeTransactions: number;
  queuedRequests: number;
}

// Alex's requirement: Burst load metrics tracking  
export interface BurstLoadMetrics {
  callsReceived: number;
  callsProcessed: number;
  callsRejected: number;
  averageLatency: number;
  peakLatency: number;
  resourceExhaustionEvents: number;
}

// Enhanced Electron API mock with realistic backend behavior
export class RealisticElectronAPI {
  private backendState: BackendResourceState = {
    websocketConnections: 0,
    maxConnections: 1000,
    databaseMaintenance: false,
    cacheCircuitBreakerOpen: false,
    cpuUsage: 20,
    memoryUsage: 30,
    activeTransactions: 0,
    queuedRequests: 0
  };
  
  private burstMetrics: BurstLoadMetrics = {
    callsReceived: 0,
    callsProcessed: 0,
    callsRejected: 0,
    averageLatency: 0,
    peakLatency: 0,
    resourceExhaustionEvents: 0
  };
  
  private latencies: number[] = [];
  private backpressureSubject = new Subject<{ type: string; severity: number }>();
  private _activePtys = new Set<string>();
  private _ptyCount = 0;
  private _maxPtyProcesses = 10;
  
  // Main IPC invoke with realistic backend simulation
  invoke = jest.fn().mockImplementation(async (channel: string, data?: any) => {
    const startTime = Date.now();
    this.burstMetrics.callsReceived++;
    
    // Check for resource exhaustion (Sarah's requirement)
    if (this.isResourceExhausted()) {
      this.burstMetrics.resourceExhaustionEvents++;
      this.burstMetrics.callsRejected++;
      
      this.backpressureSubject.next({ 
        type: 'resource_exhaustion', 
        severity: this.calculateBackpressureSeverity() 
      });
      
      const error = new Error(`Backend resource exhaustion: CPU ${this.backendState.cpuUsage}%, Memory ${this.backendState.memoryUsage}%`);
      (error as any).name = 'ResourceExhaustionError';
      throw error;
    }
    
    // Database maintenance delays (Sarah's 15-second scenario)
    if (this.backendState.databaseMaintenance && channel.includes('database')) {
      await this.simulateMaintenanceDelay();
    }
    
    // WebSocket connection management
    if (channel === 'websocket-connect') {
      if (this.backendState.websocketConnections >= this.backendState.maxConnections) {
        this.burstMetrics.callsRejected++;
        const error = new Error('WebSocket connection limit exceeded');
        (error as any).name = 'ConnectionLimitError';
        throw error;
      }
      this.backendState.websocketConnections++;
      this.backendState.memoryUsage += 2; // 2MB per connection (negotiated)
    }
    
    // Cache circuit breaker simulation
    if (channel.includes('cache') && this.backendState.cacheCircuitBreakerOpen) {
      await new Promise(resolve => setTimeout(resolve, 500)); // Cache miss penalty
      this.backendState.activeTransactions++;
    }
    
    // Dynamic processing delay based on load
    const processingDelay = this.calculateProcessingDelay(channel);
    await new Promise(resolve => setTimeout(resolve, processingDelay));
    
    // Track metrics
    const latency = Date.now() - startTime;
    this.trackLatency(latency);
    this.burstMetrics.callsProcessed++;
    
    return { 
      success: true, 
      data: data || {},
      channel,
      metrics: {
        latency,
        backendLoad: this.getBackendLoad(),
        queueDepth: this.backendState.queuedRequests
      }
    };
  });
  
  // IPC send mock
  send = jest.fn();
  
  // PTY operations (Alex's terminal requirements)
  createPty = jest.fn().mockImplementation((options = {}) => {
    if (this.backendState.cpuUsage > 80) {
      throw new Error('System overload - cannot create new PTY process');
    }
    
    if (this._ptyCount >= this._maxPtyProcesses) {
      throw new Error('Maximum PTY processes exceeded');
    }
    
    const ptyId = `pty-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    this._ptyCount++;
    this._activePtys.add(ptyId);
    this.backendState.cpuUsage += 5;
    this.backendState.memoryUsage += 10;
    
    return ptyId;
  });
  
  killPty = jest.fn().mockImplementation((ptyId: string) => {
    if (this._activePtys.has(ptyId)) {
      this._activePtys.delete(ptyId);
      this._ptyCount--;
      this.backendState.cpuUsage = Math.max(20, this.backendState.cpuUsage - 5);
      this.backendState.memoryUsage = Math.max(30, this.backendState.memoryUsage - 10);
    }
    return true;
  });
  
  writeToPty = jest.fn().mockImplementation((ptyId: string, data: string) => {
    if (!this._activePtys.has(ptyId)) {
      throw new Error(`PTY ${ptyId} not found`);
    }
    return true;
  });
  
  resizePty = jest.fn().mockImplementation((ptyId: string, cols: number, rows: number) => {
    if (!this._activePtys.has(ptyId)) {
      throw new Error(`PTY ${ptyId} not found`);
    }
    return true;
  });
  
  onPtyData = jest.fn().mockImplementation((callback: (event: any, data: any) => void) => {
    setTimeout(() => {
      callback({}, { ptyId: 'mock-pty', data: 'Mock terminal output\r\n' });
    }, 100);
    return () => {}; // Unsubscribe function
  });
  
  onPtyExit = jest.fn().mockImplementation((callback: (event: any, data: any) => void) => {
    return () => {}; // Unsubscribe function
  });
  
  // System operations
  getSystemInfo = jest.fn().mockResolvedValue({
    platform: 'linux',
    arch: 'x64',
    nodeVersion: '18.17.0',
    electronVersion: '28.0.0'
  });
  
  // File operations
  selectDirectory = jest.fn().mockResolvedValue('/mock/directory/path');
  selectFile = jest.fn().mockResolvedValue('/mock/file/path.txt');
  readFile = jest.fn().mockResolvedValue('Mock file contents');
  writeFile = jest.fn().mockResolvedValue(true);
  
  // Window operations
  minimizeWindow = jest.fn();
  maximizeWindow = jest.fn();
  closeWindow = jest.fn();
  isMaximized = jest.fn().mockReturnValue(false);
  
  // Private helper methods
  private isResourceExhausted(): boolean {
    return (
      this.backendState.cpuUsage > 90 ||
      this.backendState.memoryUsage > 85 ||
      this.backendState.websocketConnections >= this.backendState.maxConnections * 0.95 ||
      this.backendState.activeTransactions > 100 ||
      this.backendState.queuedRequests > 50
    );
  }
  
  private calculateBackpressureSeverity(): number {
    const factors = [
      this.backendState.cpuUsage / 100,
      this.backendState.memoryUsage / 100,
      this.backendState.websocketConnections / this.backendState.maxConnections,
      Math.min(this.backendState.activeTransactions / 100, 1),
      Math.min(this.backendState.queuedRequests / 50, 1)
    ];
    return Math.max(...factors);
  }
  
  private async simulateMaintenanceDelay(): Promise<void> {
    // Sarah's 15-second maintenance window
    const delays = [3000, 5000, 4000, 3000];
    for (const delay of delays) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  private calculateProcessingDelay(channel: string): number {
    const baseDelay = 10;
    const loadFactor = (this.backendState.cpuUsage / 100) * 50;
    const queueFactor = Math.min(this.backendState.queuedRequests * 2, 100);
    
    const channelDelays: Record<string, number> = {
      'database': 100,
      'cache': 20,
      'websocket': 30,
      'compute-heavy': 200
    };
    
    const channelDelay = Object.entries(channelDelays)
      .find(([key]) => channel.includes(key))?.[1] || 0;
    
    return baseDelay + loadFactor + queueFactor + channelDelay;
  }
  
  private trackLatency(latency: number): void {
    this.latencies.push(latency);
    if (this.latencies.length > 100) {
      this.latencies.shift();
    }
    
    this.burstMetrics.averageLatency = 
      this.latencies.reduce((a, b) => a + b, 0) / this.latencies.length;
    this.burstMetrics.peakLatency = Math.max(this.burstMetrics.peakLatency, latency);
  }
  
  private getBackendLoad(): number {
    return (
      this.backendState.cpuUsage * 0.3 +
      this.backendState.memoryUsage * 0.3 +
      (this.backendState.websocketConnections / this.backendState.maxConnections) * 100 * 0.2 +
      Math.min(this.backendState.activeTransactions, 100) * 0.1 +
      Math.min(this.backendState.queuedRequests / 10, 100) * 0.1
    );
  }
  
  // Test control methods for scenarios
  simulateDatabaseMaintenance(): void { 
    this.backendState.databaseMaintenance = true;
  }
  
  simulateConnectionExhaustion(): void { 
    this.backendState.websocketConnections = this.backendState.maxConnections;
  }
  
  simulateCacheFailure(): void { 
    this.backendState.cacheCircuitBreakerOpen = true;
  }
  
  simulateHighLoad(): void {
    this.backendState.cpuUsage = 85;
    this.backendState.memoryUsage = 75;
    this.backendState.activeTransactions = 80;
    this.backendState.queuedRequests = 30;
  }
  
  // Alex's burst load simulation requirement
  async simulateBurstLoad(callCount: number = 25, delayMs: number = 20): Promise<BurstLoadMetrics> {
    this.burstMetrics = {
      callsReceived: 0,
      callsProcessed: 0,
      callsRejected: 0,
      averageLatency: 0,
      peakLatency: 0,
      resourceExhaustionEvents: 0
    };
    
    const results = [];
    for (let i = 0; i < callCount; i++) {
      try {
        const result = await this.invoke(`burst-call-${i}`, { index: i });
        results.push({ success: true, result });
      } catch (error: any) {
        results.push({ success: false, error: error.message });
      }
      
      if (delayMs > 0) {
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
    
    return this.burstMetrics;
  }
  
  // State management
  resetBackendState(): void {
    this.backendState = {
      websocketConnections: 0,
      maxConnections: 1000,
      databaseMaintenance: false,
      cacheCircuitBreakerOpen: false,
      cpuUsage: 20,
      memoryUsage: 30,
      activeTransactions: 0,
      queuedRequests: 0
    };
    
    this.burstMetrics = {
      callsReceived: 0,
      callsProcessed: 0,
      callsRejected: 0,
      averageLatency: 0,
      peakLatency: 0,
      resourceExhaustionEvents: 0
    };
    
    this.latencies = [];
    this._ptyCount = 0;
    this._activePtys.clear();
  }
  
  // Observable getters
  getBackpressureObservable(): Subject<{ type: string; severity: number }> {
    return this.backpressureSubject;
  }
  
  getResourceState(): BackendResourceState {
    return { ...this.backendState };
  }
  
  getBurstMetrics(): BurstLoadMetrics {
    return { ...this.burstMetrics };
  }
  
  // Backward compatibility with v1 tests (Alex's requirement)
  _resetState(): void {
    this.resetBackendState();
  }
  
  _setFailureRate(rate: number): void {
    // Map failure rate to resource exhaustion
    if (rate >= 1.0) {
      // 100% failure - simulate complete resource exhaustion
      this.backendState.cpuUsage = 95;
      this.backendState.memoryUsage = 90;
    } else if (rate > 0) {
      // Partial failure - proportional resource usage
      this.backendState.cpuUsage = 20 + (rate * 70);
      this.backendState.memoryUsage = 30 + (rate * 55);
    } else {
      // No failures - normal resource state
      this.backendState.cpuUsage = 20;
      this.backendState.memoryUsage = 30;
    }
  }
}

// Create and export the enhanced mock
export const mockElectronAPI = new RealisticElectronAPI();

// Set up global window object (both global.window and window)
const windowMock = {
  ...((global as any).window || {}),
  electronAPI: mockElectronAPI,
  require: jest.fn(),
  process: {
    platform: 'linux',
    versions: { electron: '28.0.0', node: '18.17.0' }
  }
};

// Set on both global.window and window for jsdom compatibility
(global as any).window = windowMock;

// Also set directly on global for tests that check window directly
if (typeof window !== 'undefined') {
  Object.assign(window, windowMock);
}

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
(global as any).localStorage = localStorageMock;

// Mock WebSocket
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

// Reset state between tests
afterEach(() => {
  mockElectronAPI.resetBackendState();
  localStorageMock.getItem.mockClear();
  localStorageMock.setItem.mockClear();
  localStorageMock.removeItem.mockClear();
  localStorageMock.clear.mockClear();
});

// Export for use in tests
export { MockWebSocket, localStorageMock };