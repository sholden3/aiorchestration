/**
 * @fileoverview Extended test suite for TerminalService - achieving 80%+ coverage
 * @author Priya Sharma v1.0 - 2025-08-29
 * @architecture Frontend - Extended test coverage for TerminalService
 * @responsibility Test all terminal operations, error handling, mock mode
 * @dependencies Angular testing, TestBed, RxJS testing
 * @integration_points TerminalService, WebSocket events, IPC communication
 * @testing_strategy Comprehensive unit tests for all methods and edge cases
 * @governance Test coverage requirements for Phase 2 completion
 * 
 * Business Logic Summary:
 * - Test terminal session creation and management
 * - Test input/output handling
 * - Test resize operations
 * - Test error handling and fallbacks
 * - Test mock mode for non-Electron environments
 * - Test WebSocket event handling
 * - Test session lifecycle
 * 
 * Architecture Integration:
 * - Validates terminal service functionality
 * - Tests IPC communication patterns
 * - Ensures proper error handling
 * - Tests both Electron and mock modes
 */

import { TestBed, fakeAsync, tick, flush } from '@angular/core/testing';
import { NgZone } from '@angular/core';
import { TerminalService, TerminalOutput, TerminalSession } from './terminal.service';
import { TerminalManagerService } from './terminal-manager.service';
import { IPCService } from './ipc.service';
import { IPCErrorBoundaryService } from './ipc-error-boundary.service';
import { of, throwError } from 'rxjs';

describe('TerminalService - Extended Coverage', () => {
  let service: TerminalService;
  let managerService: TerminalManagerService;
  let ngZone: NgZone;
  let ipcService: IPCService;
  let mockElectronAPI: any;

  beforeEach(() => {
    // Create comprehensive mock electronAPI
    mockElectronAPI = {
      onTerminalOutput: jest.fn((callback) => {
        // Store callback for triggering later
        mockElectronAPI._outputCallback = callback;
        return () => { /* cleanup */ };
      }),
      onTerminalExit: jest.fn((callback) => {
        mockElectronAPI._exitCallback = callback;
        return () => { /* cleanup */ };
      }),
      onTerminalSessions: jest.fn((callback) => {
        mockElectronAPI._sessionsCallback = callback;
        return () => { /* cleanup */ };
      }),
      createTerminalSession: jest.fn().mockResolvedValue('session-123'),
      writeToTerminal: jest.fn(),
      resizeTerminal: jest.fn(),
      killTerminal: jest.fn(),
      getTerminalSessions: jest.fn().mockResolvedValue([]),
      getTerminalOutput: jest.fn().mockResolvedValue([])
    };

    (window as any).electronAPI = mockElectronAPI;

    TestBed.configureTestingModule({
      providers: [
        TerminalService,
        TerminalManagerService,
        IPCService,
        IPCErrorBoundaryService
      ]
    });

    managerService = TestBed.inject(TerminalManagerService);
    ngZone = TestBed.inject(NgZone);
    ipcService = TestBed.inject(IPCService);
    service = TestBed.inject(TerminalService);
  });

  afterEach(() => {
    if (service && !service['isDestroyed']) {
      service.ngOnDestroy();
    }
    delete (window as any).electronAPI;
  });

  describe('Session Creation', () => {
    it('should create session with default parameters', async () => {
      const sessionId = await service.createSession();
      
      expect(sessionId).toMatch(/session-\d+/);
      expect(ipcService.safeInvoke).toHaveBeenCalledWith(
        'create-terminal-session',
        expect.objectContaining({
          sessionId: expect.stringMatching(/session-\d+/)
        }),
        expect.any(Object)
      );
    });

    it('should create session with custom shell and cwd', async () => {
      const sessionId = await service.createSessionWithId('custom-id', 'powershell', '/custom/path');
      
      expect(sessionId).toBe('session-123');
      expect(ipcService.safeInvoke).toHaveBeenCalledWith(
        'create-terminal-session',
        expect.objectContaining({
          sessionId: 'custom-id',
          shell: 'powershell',
          cwd: '/custom/path'
        }),
        expect.any(Object)
      );
    });

    it('should handle session creation failure', async () => {
      jest.spyOn(ipcService, 'safeInvoke').mockRejectedValueOnce(new Error('Creation failed'));
      
      await expect(service.createSession()).rejects.toThrow('Creation failed');
    });

    it('should return sessionId when IPC returns null', async () => {
      jest.spyOn(ipcService, 'safeInvoke').mockResolvedValueOnce(null);
      
      const sessionId = await service.createSessionWithId('test-id');
      expect(sessionId).toBe('test-id');
    });
  });

  describe('Session Operations', () => {
    beforeEach(() => {
      // Reset mock for clean state
      jest.spyOn(ipcService, 'safeInvoke').mockResolvedValue(undefined);
    });

    it('should write to session', async () => {
      service.writeToSession('session-123', 'test command');
      
      expect(ipcService.safeInvoke).toHaveBeenCalledWith(
        'terminal-write',
        expect.objectContaining({
          sessionId: 'session-123',
          data: 'test command'
        })
      );
    });

    it('should handle write errors gracefully', async () => {
      jest.spyOn(ipcService, 'safeInvoke').mockRejectedValueOnce(new Error('Write failed'));
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      service.writeToSession('session-123', 'test');
      
      // Wait for async operation
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Failed to write to terminal'),
        expect.any(Error)
      );
      
      consoleSpy.mockRestore();
    });

    it('should resize session with valid dimensions', () => {
      service.resizeSession('session-123', 120, 40);
      
      expect(ipcService.safeInvoke).toHaveBeenCalledWith(
        'terminal-resize',
        expect.objectContaining({
          sessionId: 'session-123',
          cols: 120,
          rows: 40
        })
      );
    });

    it('should handle resize errors gracefully', async () => {
      jest.spyOn(ipcService, 'safeInvoke').mockRejectedValueOnce(new Error('Resize failed'));
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      service.resizeSession('session-123', 80, 24);
      
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Failed to resize terminal'),
        expect.any(Error)
      );
      
      consoleSpy.mockRestore();
    });

    it('should kill session', () => {
      service.killSession('session-123');
      
      expect(ipcService.safeInvoke).toHaveBeenCalledWith(
        'terminal-kill',
        expect.objectContaining({
          sessionId: 'session-123'
        })
      );
    });

    it('should handle kill errors gracefully', async () => {
      jest.spyOn(ipcService, 'safeInvoke').mockRejectedValueOnce(new Error('Kill failed'));
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      service.killSession('session-123');
      
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Failed to kill terminal'),
        expect.any(Error)
      );
      
      consoleSpy.mockRestore();
    });
  });

  describe('Session Query Operations', () => {
    it('should get active sessions', async () => {
      const mockSessions: TerminalSession[] = [
        {
          id: 'session-1',
          shell: 'bash',
          cwd: '/home',
          created: Date.now(),
          lastActivity: Date.now(),
          outputLines: 100
        }
      ];
      
      jest.spyOn(ipcService, 'safeInvoke').mockResolvedValueOnce(mockSessions);
      
      const sessions = await service.getActiveSessions();
      
      expect(sessions).toEqual(mockSessions);
      expect(ipcService.safeInvoke).toHaveBeenCalledWith(
        'get-terminal-sessions',
        {},
        expect.objectContaining({
          timeout: 5000,
          fallbackValue: []
        })
      );
    });

    it('should return empty array on getActiveSessions error', async () => {
      jest.spyOn(ipcService, 'safeInvoke').mockRejectedValueOnce(new Error('Failed'));
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      const sessions = await service.getActiveSessions();
      
      expect(sessions).toEqual([]);
      expect(consoleSpy).toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });

    it('should get session output', async () => {
      const mockOutput = [
        { data: 'line 1', timestamp: Date.now() },
        { data: 'line 2', timestamp: Date.now() }
      ];
      
      jest.spyOn(ipcService, 'safeInvoke').mockResolvedValueOnce(mockOutput);
      
      const output = await service.getSessionOutput('session-123', 10);
      
      expect(output).toEqual(mockOutput);
      expect(ipcService.safeInvoke).toHaveBeenCalledWith(
        'get-terminal-output',
        expect.objectContaining({
          sessionId: 'session-123',
          fromIndex: 10
        }),
        expect.any(Object)
      );
    });

    it('should return empty array on getSessionOutput error', async () => {
      jest.spyOn(ipcService, 'safeInvoke').mockRejectedValueOnce(new Error('Failed'));
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      const output = await service.getSessionOutput('session-123');
      
      expect(output).toEqual([]);
      expect(consoleSpy).toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });
  });

  describe('Event Handling', () => {
    it('should handle terminal output events', (done) => {
      const outputData: TerminalOutput = {
        sessionId: 'session-123',
        data: 'Terminal output\r\n',
        timestamp: Date.now()
      };

      service.output$.subscribe(output => {
        expect(output).toEqual(outputData);
        done();
      });

      // Trigger the output callback
      ngZone.run(() => {
        mockElectronAPI._outputCallback(outputData);
      });
    });

    it('should handle terminal exit events', (done) => {
      const exitData = {
        sessionId: 'session-123',
        exitCode: 0
      };

      service.exit$.subscribe(exit => {
        expect(exit).toEqual(exitData);
        done();
      });

      // Trigger the exit callback
      ngZone.run(() => {
        mockElectronAPI._exitCallback(exitData);
      });
    });

    it('should handle sessions update events', (done) => {
      const sessionsData: TerminalSession[] = [
        {
          id: 'session-1',
          shell: 'bash',
          cwd: '/home',
          created: Date.now(),
          lastActivity: Date.now(),
          outputLines: 50
        }
      ];

      service.sessions$.subscribe(sessions => {
        expect(sessions).toEqual(sessionsData);
        done();
      });

      // Trigger the sessions callback
      ngZone.run(() => {
        mockElectronAPI._sessionsCallback(sessionsData);
      });
    });

    it('should not process events after destroy', () => {
      const outputSpy = jest.spyOn(service['outputSubject'], 'next');
      
      // Destroy the service
      service.ngOnDestroy();
      
      // Try to trigger output event
      mockElectronAPI._outputCallback({
        sessionId: 'test',
        data: 'test',
        timestamp: Date.now()
      });
      
      // Should not be called
      expect(outputSpy).not.toHaveBeenCalled();
    });
  });

  describe('Mock Mode (Non-Electron)', () => {
    let mockService: TerminalService;

    beforeEach(() => {
      // Remove electronAPI to test mock mode
      delete (window as any).electronAPI;
      
      // Create service without Electron
      mockService = new TerminalService(ngZone, managerService, ipcService);
    });

    afterEach(() => {
      if (mockService) {
        mockService.ngOnDestroy();
      }
    });

    it('should create mock session', async () => {
      const sessionId = await mockService.createSession();
      
      expect(sessionId).toMatch(/session-\d+/);
    });

    it('should emit mock output after session creation', (done) => {
      mockService.output$.subscribe(output => {
        expect(output.data).toContain('Mock Mode');
        done();
      });

      mockService.createSession();
    });

    it('should handle write in mock mode', (done) => {
      const sessionId = 'test-session';
      
      mockService.output$.subscribe(output => {
        if (output.data.includes('Mock output')) {
          expect(output.sessionId).toBe(sessionId);
          expect(output.data).toContain('test command');
          done();
        }
      });

      mockService.writeToSession(sessionId, 'test command');
    });

    it('should handle resize in mock mode', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      mockService.resizeSession('test', 80, 24);
      
      expect(consoleSpy).toHaveBeenCalledWith(
        'Mock terminal resize:',
        expect.objectContaining({ cols: 80, rows: 24 })
      );
      
      consoleSpy.mockRestore();
    });

    it('should handle kill in mock mode', (done) => {
      mockService.exit$.subscribe(exit => {
        expect(exit.sessionId).toBe('test');
        expect(exit.exitCode).toBe(0);
        done();
      });

      mockService.killSession('test');
    });

    it('should return empty array for getActiveSessions in mock mode', async () => {
      const sessions = await mockService.getActiveSessions();
      expect(sessions).toEqual([]);
    });

    it('should return empty array for getSessionOutput in mock mode', async () => {
      const output = await mockService.getSessionOutput('test');
      expect(output).toEqual([]);
    });
  });

  describe('Debug Utilities', () => {
    it('should provide debug information', () => {
      const debugInfo = service.getDebugInfo();
      
      expect(debugInfo).toHaveProperty('instanceId');
      expect(debugInfo).toHaveProperty('createdAt');
      expect(debugInfo).toHaveProperty('createdAtISO');
      expect(debugInfo).toHaveProperty('lifeTimeMs');
      expect(debugInfo).toHaveProperty('isDestroyed', false);
      expect(debugInfo).toHaveProperty('activeListeners');
      expect(debugInfo).toHaveProperty('memoryRisk');
    });

    it('should show memory risk based on state', () => {
      const debugInfo = service.getDebugInfo();
      expect(debugInfo.memoryRisk).toBe('POTENTIAL_LEAK');
      
      service.ngOnDestroy();
      
      const destroyedDebugInfo = service.getDebugInfo();
      expect(destroyedDebugInfo.memoryRisk).toBe('NO_RISK');
    });

    it('should attach global debug hook', () => {
      TerminalService.attachGlobalDebugHook(managerService);
      
      expect((window as any).getTerminalDebugInfo).toBeDefined();
      
      const globalDebugInfo = (window as any).getTerminalDebugInfo();
      
      expect(globalDebugInfo).toHaveProperty('totalServices');
      expect(globalDebugInfo).toHaveProperty('activeServices');
      expect(globalDebugInfo).toHaveProperty('destroyedServices');
      expect(globalDebugInfo).toHaveProperty('potentialLeaks');
      expect(globalDebugInfo).toHaveProperty('services');
      
      // Cleanup
      delete (window as any).getTerminalDebugInfo;
    });
  });

  describe('Error Handling', () => {
    it('should handle missing electronAPI gracefully', () => {
      delete (window as any).electronAPI;
      
      const newService = new TerminalService(ngZone, managerService, ipcService);
      
      expect(newService).toBeDefined();
      expect(newService['cleanupFunctions']).toHaveLength(0);
      
      newService.ngOnDestroy();
    });

    it('should handle IPC service errors in operations', async () => {
      jest.spyOn(ipcService, 'safeInvoke').mockRejectedValue(new Error('IPC Error'));
      
      await expect(service.createSession()).rejects.toThrow('IPC Error');
    });

    it('should continue cleanup even if observables throw', () => {
      // Make output subject throw on complete
      jest.spyOn(service['outputSubject'], 'complete').mockImplementation(() => {
        throw new Error('Complete error');
      });
      
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      // Should not throw
      expect(() => service.ngOnDestroy()).not.toThrow();
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error completing observables'),
        expect.any(Error)
      );
      
      consoleSpy.mockRestore();
    });

    it('should handle manager unregister errors', () => {
      jest.spyOn(managerService, 'unregister').mockImplementation(() => {
        throw new Error('Unregister error');
      });
      
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      service.forceCleanup();
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error unregistering from manager'),
        expect.any(Error)
      );
      
      consoleSpy.mockRestore();
    });
  });

  describe('NgZone Integration', () => {
    it('should run output events in NgZone', () => {
      const ngZoneSpy = jest.spyOn(ngZone, 'run');
      
      mockElectronAPI._outputCallback({
        sessionId: 'test',
        data: 'test',
        timestamp: Date.now()
      });
      
      expect(ngZoneSpy).toHaveBeenCalled();
    });

    it('should run exit events in NgZone', () => {
      const ngZoneSpy = jest.spyOn(ngZone, 'run');
      
      mockElectronAPI._exitCallback({
        sessionId: 'test',
        exitCode: 0
      });
      
      expect(ngZoneSpy).toHaveBeenCalled();
    });

    it('should run sessions events in NgZone', () => {
      const ngZoneSpy = jest.spyOn(ngZone, 'run');
      
      mockElectronAPI._sessionsCallback([]);
      
      expect(ngZoneSpy).toHaveBeenCalled();
    });
  });

  describe('Lifecycle Management', () => {
    it('should track creation timestamp', () => {
      const now = Date.now();
      expect(service['createdAt']).toBeCloseTo(now, -3); // Within 1000ms
    });

    it('should generate unique instance ID', () => {
      const service2 = new TerminalService(ngZone, managerService, ipcService);
      
      expect(service['instanceId']).toBeDefined();
      expect(service2['instanceId']).toBeDefined();
      expect(service['instanceId']).not.toBe(service2['instanceId']);
      
      service2.ngOnDestroy();
    });

    it('should log lifecycle events', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      const newService = new TerminalService(ngZone, managerService, ipcService);
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('TerminalService initializing')
      );
      
      newService.ngOnDestroy();
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Terminal service cleanup complete')
      );
      
      consoleSpy.mockRestore();
    });

    it('should report cleanup metrics', () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      service.forceCleanup();
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Cleanup summary')
      );
      
      consoleSpy.mockRestore();
    });
  });
});

/**
 * Integration test suite for Terminal Service with real IPC
 */
describe('TerminalService - Integration Tests', () => {
  let service: TerminalService;
  let mockElectronAPI: any;

  beforeEach(() => {
    // Setup more realistic electronAPI mock
    mockElectronAPI = {
      onTerminalOutput: jest.fn((callback) => {
        // Simulate real output stream
        setTimeout(() => {
          callback({
            sessionId: 'session-123',
            data: 'Welcome to terminal\r\n$ ',
            timestamp: Date.now()
          });
        }, 10);
        return () => {};
      }),
      onTerminalExit: jest.fn((callback) => {
        return () => {};
      }),
      onTerminalSessions: jest.fn((callback) => {
        // Simulate session list update
        setTimeout(() => {
          callback([{
            id: 'session-123',
            shell: 'bash',
            cwd: '/home',
            created: Date.now(),
            lastActivity: Date.now(),
            outputLines: 1
          }]);
        }, 10);
        return () => {};
      }),
      createTerminalSession: jest.fn().mockImplementation(() => {
        return new Promise(resolve => {
          setTimeout(() => resolve('session-123'), 10);
        });
      }),
      writeToTerminal: jest.fn(),
      resizeTerminal: jest.fn(),
      killTerminal: jest.fn(),
      getTerminalSessions: jest.fn().mockResolvedValue([]),
      getTerminalOutput: jest.fn().mockResolvedValue([])
    };

    (window as any).electronAPI = mockElectronAPI;

    TestBed.configureTestingModule({
      providers: [
        TerminalService,
        TerminalManagerService,
        IPCService,
        IPCErrorBoundaryService
      ]
    });

    service = TestBed.inject(TerminalService);
  });

  afterEach(() => {
    if (service) {
      service.ngOnDestroy();
    }
    delete (window as any).electronAPI;
  });

  it('should handle full session lifecycle', fakeAsync(() => {
    let outputReceived = false;
    let sessionsReceived = false;

    // Subscribe to outputs
    service.output$.subscribe(output => {
      expect(output.data).toContain('Welcome');
      outputReceived = true;
    });

    service.sessions$.subscribe(sessions => {
      expect(sessions.length).toBeGreaterThan(0);
      sessionsReceived = true;
    });

    // Create session
    service.createSession().then(sessionId => {
      expect(sessionId).toBe('session-123');
    });

    // Wait for async operations
    tick(50);

    expect(outputReceived).toBe(true);
    expect(sessionsReceived).toBe(true);
  }));

  it('should handle rapid session operations', fakeAsync(() => {
    // Create session
    service.createSession();
    tick(20);

    // Rapid operations
    service.writeToSession('session-123', 'ls\n');
    service.writeToSession('session-123', 'pwd\n');
    service.writeToSession('session-123', 'echo test\n');
    service.resizeSession('session-123', 120, 40);
    service.resizeSession('session-123', 80, 24);

    tick(10);

    // Verify all operations were called
    expect(mockElectronAPI.writeToTerminal).toHaveBeenCalledTimes(3);
    expect(mockElectronAPI.resizeTerminal).toHaveBeenCalledTimes(2);
  }));
});

/**
 * Performance test suite
 */
describe('TerminalService - Performance Tests', () => {
  it('should handle 100 concurrent sessions efficiently', () => {
    const services: TerminalService[] = [];
    const startTime = Date.now();

    // Create 100 services
    for (let i = 0; i < 100; i++) {
      const service = new TerminalService(
        TestBed.inject(NgZone),
        TestBed.inject(TerminalManagerService),
        TestBed.inject(IPCService)
      );
      services.push(service);
    }

    const creationTime = Date.now() - startTime;
    expect(creationTime).toBeLessThan(1000); // Should create 100 services in under 1 second

    // Cleanup all services
    const cleanupStart = Date.now();
    services.forEach(s => s.ngOnDestroy());
    
    const cleanupTime = Date.now() - cleanupStart;
    expect(cleanupTime).toBeLessThan(500); // Should cleanup 100 services in under 500ms

    // Verify all cleaned up
    const manager = TestBed.inject(TerminalManagerService);
    expect(manager.getActiveCount()).toBe(0);
  });
});

// Export for test runner
export { };
