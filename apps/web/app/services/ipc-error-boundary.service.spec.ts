// ipc-error-boundary.service.spec.ts - Test for H2 IPC Error Boundary
import { TestBed } from '@angular/core/testing';
import { IPCErrorBoundaryService, IPCErrorType } from './ipc-error-boundary.service';
import { mockElectronAPI } from '../../../src/test-setup-electron';

describe('IPCErrorBoundaryService (H2 Fix Validation)', () => {
  let service: IPCErrorBoundaryService;
  
  beforeEach(() => {
    // Ensure window.electronAPI is available before creating service
    if (!(window as any).electronAPI) {
      (window as any).electronAPI = mockElectronAPI;
    }
    
    TestBed.configureTestingModule({});
    service = TestBed.inject(IPCErrorBoundaryService);
    
    // Reset Electron mock state
    mockElectronAPI._resetState();
  });
  
  describe('Circuit Breaker Functionality', () => {
    it('should create service instance', () => {
      expect(service).toBeTruthy();
    });
    
    it('should handle successful IPC calls', async () => {
      const result = await service.safeIPCInvoke<{ success: boolean; data: any; channel: string }>('test-channel', { data: 'test' });
      expect(result).toBeTruthy();
      expect(result?.success).toBe(true);
    });
    
    it('should handle IPC failures with fallback value', async () => {
      // Set high failure rate to trigger failures
      mockElectronAPI._setFailureRate(1.0); // 100% failure rate
      
      const fallbackValue = { fallback: true };
      const result = await service.safeIPCInvoke(
        'test-channel',
        { data: 'test' },
        { fallbackValue }
      );
      
      expect(result).toEqual(fallbackValue);
    });
    
    it('should track metrics correctly', async () => {
      // Make some successful calls
      mockElectronAPI._setFailureRate(0);
      await service.safeIPCInvoke('test-channel', {});
      await service.safeIPCInvoke('test-channel', {});
      
      // Make some failed calls
      mockElectronAPI._setFailureRate(1.0);
      await service.safeIPCInvoke('test-channel', {});
      
      const metrics = service.getMetrics();
      expect(metrics.totalCalls).toBeGreaterThanOrEqual(3);
      expect(metrics.successfulCalls).toBeGreaterThanOrEqual(2);
      expect(metrics.failedCalls).toBeGreaterThanOrEqual(1);
    });
    
    it('should detect when electronAPI is not available', async () => {
      // Temporarily remove electronAPI
      const originalAPI = (window as any).electronAPI;
      delete (window as any).electronAPI;
      
      // Create a new service instance without electronAPI
      const testService = TestBed.inject(IPCErrorBoundaryService);
      
      try {
        await testService.safeIPCInvoke('test-channel', {});
        fail('Should have thrown an error');
      } catch (error: any) {
        expect(error.name).toBe('IPCError');
        expect((error as any).type).toBe(IPCErrorType.CONNECTION_FAILED);
      } finally {
        // Restore electronAPI
        (window as any).electronAPI = originalAPI;
      }
    });
  });
  
  describe('Timeout Protection', () => {
    it('should timeout long-running IPC calls', async () => {
      // Mock a slow IPC call
      const originalInvoke = mockElectronAPI.invoke;
      mockElectronAPI.invoke = jest.fn().mockImplementation(async () => {
        await new Promise(resolve => setTimeout(resolve, 10000)); // 10 second delay
        return { success: true };
      });
      
      const result = await service.safeIPCInvoke(
        'test-channel',
        {},
        { timeout: 100 } // 100ms timeout
      );
      
      expect(result).toBeNull();
      
      // Restore original mock
      mockElectronAPI.invoke = originalInvoke;
    });
  });
  
  describe('Circuit Breaker State Management', () => {
    it('should open circuit after failure threshold', async () => {
      // Set 100% failure rate to trigger circuit breaker
      mockElectronAPI._setFailureRate(1.0);
      
      // Make multiple failed calls to trip the circuit
      for (let i = 0; i < 6; i++) {
        await service.safeIPCInvoke('test-channel', {});
      }
      
      // Circuit should now be open
      const status = service.getCircuitBreakerStatus();
      const channelStatus = Array.from(status.values()).find(s => s);
      
      expect(channelStatus).toBeDefined();
      if (channelStatus) {
        expect(channelStatus.failureCount).toBeGreaterThanOrEqual(5);
      }
    });
    
    it('should use fallback when circuit is open', async () => {
      // Trip the circuit breaker
      mockElectronAPI._setFailureRate(1.0);
      for (let i = 0; i < 6; i++) {
        await service.safeIPCInvoke('breaker-test-channel', {});
      }
      
      // Reset failure rate but circuit should still be open
      mockElectronAPI._setFailureRate(0);
      
      const fallback = { circuit: 'open' };
      const result = await service.safeIPCInvoke(
        'breaker-test-channel',
        {},
        { fallbackValue: fallback }
      );
      
      expect(result).toEqual(fallback);
    });
  });
  
  describe('Correlation ID Tracking', () => {
    it('should generate unique correlation IDs', async () => {
      const correlationIds = new Set<string>();
      
      // Mock to capture correlation IDs
      const originalInvoke = mockElectronAPI.invoke;
      mockElectronAPI.invoke = jest.fn().mockImplementation(async (channel, data) => {
        if (data?.correlationId) {
          correlationIds.add(data.correlationId);
        }
        return { success: true };
      });
      
      // Make multiple calls
      await Promise.all([
        service.safeIPCInvoke('test1', {}),
        service.safeIPCInvoke('test2', {}),
        service.safeIPCInvoke('test3', {})
      ]);
      
      // All correlation IDs should be unique
      expect(correlationIds.size).toBeGreaterThanOrEqual(3);
      
      // Restore original mock
      mockElectronAPI.invoke = originalInvoke;
    });
  });
  
  describe('Error Type Classification', () => {
    it('should correctly classify timeout errors', async () => {
      // Mock a timeout scenario
      const originalInvoke = mockElectronAPI.invoke;
      mockElectronAPI.invoke = jest.fn().mockImplementation(async () => {
        await new Promise(resolve => setTimeout(resolve, 10000));
        return { success: true };
      });
      
      await service.safeIPCInvoke('timeout-test', {}, { timeout: 50 });
      
      const metrics = service.getMetrics();
      expect(metrics.timeouts).toBeGreaterThan(0);
      
      // Restore original mock
      mockElectronAPI.invoke = originalInvoke;
    });
  });
  
  describe('Cleanup and Reset', () => {
    it('should reset all circuit breakers', () => {
      service.resetAllCircuitBreakers();
      const status = service.getCircuitBreakerStatus();
      
      status.forEach(breaker => {
        expect(breaker.state).toBe('closed');
        expect(breaker.failureCount).toBe(0);
      });
    });
    
    it('should reset metrics', () => {
      service.resetMetrics();
      const metrics = service.getMetrics();
      
      expect(metrics.totalCalls).toBe(0);
      expect(metrics.successfulCalls).toBe(0);
      expect(metrics.failedCalls).toBe(0);
      expect(metrics.timeouts).toBe(0);
    });
  });
});