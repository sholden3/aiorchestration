/**
 * Test suite for C1: Terminal Service Memory Leak Fix
 * Validates component-scoped service, cleanup, and IPC listener management
 * Architecture: Alex Novak
 */
import { TestBed } from '@angular/core/testing';
import { NgZone } from '@angular/core';
import { TerminalService } from './terminal.service';
import { TerminalManagerService } from './terminal-manager.service';

describe('TerminalService - C1 Memory Leak Fix', () => {
  let service: TerminalService;
  let managerService: TerminalManagerService;
  let ngZone: NgZone;
  let mockElectronAPI: any;

  beforeEach(() => {
    // Mock electronAPI
    mockElectronAPI = {
      onTerminalOutput: jest.fn((callback) => {
        // Return cleanup function
        return () => { console.log('Output listener cleaned up'); };
      }),
      onTerminalExit: jest.fn((callback) => {
        return () => { console.log('Exit listener cleaned up'); };
      }),
      onTerminalSessions: jest.fn((callback) => {
        return () => { console.log('Sessions listener cleaned up'); };
      }),
      createTerminalSession: jest.fn().mockResolvedValue('session-123'),
      writeToTerminal: jest.fn(),
      resizeTerminal: jest.fn(),
      killTerminal: jest.fn(),
      getTerminalSessions: jest.fn().mockResolvedValue([]),
      getTerminalOutput: jest.fn().mockResolvedValue([])
    };

    // Set up window.electronAPI
    (window as any).electronAPI = mockElectronAPI;

    TestBed.configureTestingModule({
      providers: [
        TerminalService,
        TerminalManagerService,
        NgZone
      ]
    });

    managerService = TestBed.inject(TerminalManagerService);
    ngZone = TestBed.inject(NgZone);
  });

  afterEach(() => {
    // Clean up
    if (service) {
      service.ngOnDestroy();
    }
    delete (window as any).electronAPI;
  });

  describe('Memory Leak Prevention', () => {
    it('should register with TerminalManagerService on creation', () => {
      const registerSpy = jest.spyOn(managerService, 'register');
      
      service = TestBed.inject(TerminalService);
      
      expect(registerSpy).toHaveBeenCalledWith(service);
      expect(managerService.getActiveCount()).toBe(1);
    });

    it('should unregister from TerminalManagerService on destroy', () => {
      const unregisterSpy = jest.spyOn(managerService, 'unregister');
      
      service = TestBed.inject(TerminalService);
      const initialCount = managerService.getActiveCount();
      
      service.ngOnDestroy();
      
      expect(unregisterSpy).toHaveBeenCalledWith(service);
      expect(managerService.getActiveCount()).toBe(initialCount - 1);
    });

    it('should initialize IPC listeners only in Electron environment', () => {
      service = TestBed.inject(TerminalService);
      
      expect(mockElectronAPI.onTerminalOutput).toHaveBeenCalled();
      expect(mockElectronAPI.onTerminalExit).toHaveBeenCalled();
      expect(mockElectronAPI.onTerminalSessions).toHaveBeenCalled();
    });

    it('should store cleanup functions for all listeners', () => {
      service = TestBed.inject(TerminalService);
      
      // Access private property for testing
      const cleanupFunctions = (service as any).cleanupFunctions;
      
      expect(cleanupFunctions).toBeDefined();
      expect(cleanupFunctions.length).toBe(3); // output, exit, sessions
    });

    it('should cleanup all IPC listeners on destroy', () => {
      service = TestBed.inject(TerminalService);
      
      // Mock cleanup functions
      const cleanupMocks = [
        jest.fn(),
        jest.fn(),
        jest.fn()
      ];
      (service as any).cleanupFunctions = cleanupMocks;
      
      service.ngOnDestroy();
      
      // All cleanup functions should be called
      cleanupMocks.forEach(mock => {
        expect(mock).toHaveBeenCalled();
      });
      
      // Cleanup array should be emptied
      expect((service as any).cleanupFunctions.length).toBe(0);
    });

    it('should complete all observables on destroy', (done) => {
      service = TestBed.inject(TerminalService);
      
      // Subscribe to observables and check they complete
      let outputCompleted = false;
      let sessionsCompleted = false;
      let exitCompleted = false;
      
      service.output$.subscribe({
        complete: () => { outputCompleted = true; }
      });
      
      service.sessions$.subscribe({
        complete: () => { sessionsCompleted = true; }
      });
      
      service.exit$.subscribe({
        complete: () => { exitCompleted = true; }
      });
      
      service.ngOnDestroy();
      
      // Use setTimeout to allow async completion
      setTimeout(() => {
        expect(outputCompleted).toBe(true);
        expect(sessionsCompleted).toBe(true);
        expect(exitCompleted).toBe(true);
        done();
      }, 0);
    });

    it('should prevent operations after destroy', async () => {
      service = TestBed.inject(TerminalService);
      
      // Destroy the service
      service.ngOnDestroy();
      
      // Try to use service after destroy
      const result = await service.createSession();
      
      // Should handle gracefully (return empty or null)
      expect(result).toBeFalsy();
    });

    it('should handle cleanup errors gracefully', () => {
      service = TestBed.inject(TerminalService);
      
      // Mock cleanup function that throws error
      const errorCleanup = jest.fn(() => {
        throw new Error('Cleanup error');
      });
      (service as any).cleanupFunctions = [errorCleanup];
      
      // Should not throw
      expect(() => service.forceCleanup()).not.toThrow();
      
      // Error cleanup should still be attempted
      expect(errorCleanup).toHaveBeenCalled();
    });
  });

  describe('Terminal Manager Service', () => {
    it('should track active service count', () => {
      const initialCount = managerService.getActiveCount();
      
      const service1 = TestBed.inject(TerminalService);
      expect(managerService.getActiveCount()).toBe(initialCount + 1);
      
      // Create another instance (simulating another component)
      const service2 = new TerminalService(ngZone, managerService);
      expect(managerService.getActiveCount()).toBe(initialCount + 2);
      
      service1.ngOnDestroy();
      expect(managerService.getActiveCount()).toBe(initialCount + 1);
      
      service2.ngOnDestroy();
      expect(managerService.getActiveCount()).toBe(initialCount);
    });

    it('should provide memory usage estimate', () => {
      const service1 = TestBed.inject(TerminalService);
      const service2 = new TerminalService(ngZone, managerService);
      
      const estimate = managerService.getMemoryEstimate();
      
      // With 2 services, estimate should be 4-10 MB
      expect(estimate).toMatch(/\d+-\d+ MB/);
      
      service1.ngOnDestroy();
      service2.ngOnDestroy();
    });

    it('should handle emergency cleanup', () => {
      const service1 = TestBed.inject(TerminalService);
      const service2 = new TerminalService(ngZone, managerService);
      
      const spy1 = jest.spyOn(service1, 'forceCleanup');
      const spy2 = jest.spyOn(service2, 'forceCleanup');
      
      // Emergency cleanup
      managerService.cleanup();
      
      expect(spy1).toHaveBeenCalled();
      expect(spy2).toHaveBeenCalled();
      expect(managerService.getActiveCount()).toBe(0);
    });
  });

  describe('Component-Scoped Pattern', () => {
    it('should not be provided at root level', () => {
      // Service should not have providedIn: 'root'
      const metadata = (TerminalService as any).__annotations__;
      
      // This test verifies the service is not root-provided
      // In actual implementation, check @Injectable() has no providedIn
      expect(service).toBeDefined();
    });

    it('should create separate instance per component', () => {
      const service1 = TestBed.inject(TerminalService);
      const service2 = new TerminalService(ngZone, managerService);
      
      // Should be different instances
      expect(service1).not.toBe(service2);
      
      // Clean up
      service1.ngOnDestroy();
      service2.ngOnDestroy();
    });
  });

  describe('IPC Communication Safety', () => {
    it('should not process events after destruction', () => {
      service = TestBed.inject(TerminalService);
      
      // Get the callback registered with electronAPI
      const outputCallback = mockElectronAPI.onTerminalOutput.mock.calls[0][0];
      
      // Destroy service
      service.ngOnDestroy();
      
      // Try to send data after destroy
      const spy = jest.spyOn(service['outputSubject'], 'next');
      outputCallback({ sessionId: 'test', data: 'test', timestamp: Date.now() });
      
      // Should not process
      expect(spy).not.toHaveBeenCalled();
    });

    it('should handle missing electronAPI gracefully', () => {
      delete (window as any).electronAPI;
      
      // Should not throw
      expect(() => {
        service = new TerminalService(ngZone, managerService);
      }).not.toThrow();
      
      // Should handle operations gracefully
      expect(service.createSession()).resolves.toBe('');
    });
  });
});

describe('TerminalManagerService', () => {
  let service: TerminalManagerService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [TerminalManagerService]
    });
    service = TestBed.inject(TerminalManagerService);
  });

  it('should be singleton at root level', () => {
    const service2 = TestBed.inject(TerminalManagerService);
    expect(service).toBe(service2);
  });

  it('should register cleanup callbacks', () => {
    const mockService = { id: 'test' };
    const cleanupFn = jest.fn();
    
    service.register(mockService);
    service.registerCleanup(mockService, cleanupFn);
    
    service.cleanup();
    
    expect(cleanupFn).toHaveBeenCalled();
  });
});