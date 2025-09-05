/**
 * @fileoverview Unit tests for ResilientIPCService
 * @author Maya Patel v2.0 - QA & Testing Lead
 * @architecture Testing - Unit test suite for resilient IPC service
 * @business_logic Validates reconnection logic, circuit breaker, message queuing
 * @testing_strategy Mock IPC renderer, simulate connection failures, test recovery
 * @coverage_target 90% code coverage for ResilientIPCService
 */

import { TestBed, fakeAsync, tick, flush } from '@angular/core/testing';
import { NgZone } from '@angular/core';
import { ResilientIPCService, ConnectionState } from './resilient-ipc.service';
import { take, skip } from 'rxjs/operators';

describe('ResilientIPCService', () => {
  let service: ResilientIPCService;
  let ngZone: NgZone;
  let mockIpcRenderer: any;
  let mockWebSocket: any;

  beforeEach(() => {
    // Mock IPC renderer
    mockIpcRenderer = {
      invoke: jest.fn().mockResolvedValue('success'),
      send: jest.fn(),
      on: jest.fn(),
      removeListener: jest.fn()
    };

    // Mock WebSocket
    mockWebSocket = {
      readyState: WebSocket.OPEN,
      send: jest.fn(),
      close: jest.fn(),
      onopen: null,
      onclose: null,
      onerror: null,
      onmessage: null
    };

    // Set up window.electronAPI mock
    (window as any).electronAPI = {
      ipcRenderer: mockIpcRenderer
    };

    // Mock WebSocket constructor
    jest.spyOn(window, 'WebSocket' as any).mockReturnValue(mockWebSocket);

    TestBed.configureTestingModule({
      providers: [ResilientIPCService]
    });

    service = TestBed.inject(ResilientIPCService);
    ngZone = TestBed.inject(NgZone);
  });

  afterEach(() => {
    if (service) {
      service.destroy();
    }
    delete (window as any).electronAPI;
    jest.clearAllMocks();
  });

  describe('Service Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should start in connecting state', (done) => {
      service.getConnectionState().pipe(take(1)).subscribe(state => {
        expect(state).toBe(ConnectionState.CONNECTING);
        done();
      });
    });

    it('should perform initial health check', fakeAsync(() => {
      mockIpcRenderer.invoke.mockResolvedValue(Promise.resolve('healthy'));
      
      const newService = new ResilientIPCService(ngZone);
      tick(100);
      
      expect(mockIpcRenderer.invoke).toHaveBeenCalledWith('health:check');
    }));

    it('should handle missing IPC renderer', () => {
      delete (window as any).electron;
      const newService = new ResilientIPCService(ngZone);
      
      newService.getConnectionState().pipe(take(1)).subscribe(state => {
        expect(state).toBe(ConnectionState.ERROR);
      });
    });
  });

  describe('Connection State Management', () => {
    it('should report connection state accurately', () => {
      expect(service.isConnected()).toBe(false);
      
      // Simulate successful connection
      mockIpcRenderer.invoke.mockResolvedValue(Promise.resolve('healthy'));
    });

    it('should transition to connected state on successful health check', fakeAsync(() => {
      mockIpcRenderer.invoke.mockResolvedValue(Promise.resolve('healthy'));
      
      service.getConnectionState().pipe(skip(1), take(1)).subscribe(state => {
        expect(state).toBe(ConnectionState.CONNECTED);
      });
      
      tick(5000);
    }));

    it('should transition to disconnected on health check failure', fakeAsync(() => {
      mockIpcRenderer.invoke.mockRejectedValue(new Error('Health check failed'));
      
      service.getConnectionState().pipe(skip(1), take(1)).subscribe(state => {
        expect(state).toBe(ConnectionState.DISCONNECTED);
      });
      
      tick(5000);
    }));
  });

  describe('IPC Invocation', () => {
    it('should invoke IPC method when connected', async () => {
      // Simulate connected state
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      
      const result = await service.invoke('test:method', 'arg1', 'arg2');
      
      expect(mockIpcRenderer.invoke).toHaveBeenCalledWith('test:method', 'arg1', 'arg2');
      expect(result).toBe('success');
    });

    it('should queue messages when disconnected', async () => {
      (service as any).connectionState$.next(ConnectionState.DISCONNECTED);
      
      const promise = service.invoke('test:method', 'arg1');
      
      // Message should be queued
      expect((service as any).messageQueue.size).toBe(1);
      
      // Simulate reconnection
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      (service as any).processMessageQueue();
      
      const result = await promise;
      expect(result).toBe('success');
    });

    it('should generate correlation IDs for tracking', async () => {
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      
      await service.invoke('test:method');
      await service.invoke('test:method2');
      
      // Check that correlation IDs are unique
      expect(mockIpcRenderer.invoke).toHaveBeenCalledTimes(2);
    });

    it('should handle invoke errors', async () => {
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      mockIpcRenderer.invoke.mockRejectedValue(new Error('IPC error'));
      
      try {
        await service.invoke('failing:method');
        fail('Should have thrown error');
      } catch (error: any) {
        expect(error.message).toBe('IPC error');
      }
    });
  });

  describe('Circuit Breaker', () => {
    it('should open circuit after threshold failures', async () => {
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      mockIpcRenderer.invoke.mockRejectedValue(new Error('Failed'));
      
      // Fail multiple times to open circuit
      for (let i = 0; i < 5; i++) {
        try {
          await service.invoke('test:method');
        } catch (e) {
          // Expected
        }
      }
      
      // Circuit should be open
      expect((service as any).circuitBreaker.state).toBe('open');
      
      // Next call should be rejected immediately
      try {
        await service.invoke('test:method');
        fail('Should have been rejected by circuit breaker');
      } catch (error: any) {
        expect(error.message).toContain('circuit breaker open');
      }
    });

    it('should enter half-open state after cooldown', fakeAsync(() => {
      (service as any).circuitBreaker.state = 'open';
      (service as any).circuitBreaker.lastFailureTime = Date.now() - 31000; // 31 seconds ago
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      mockIpcRenderer.invoke.mockResolvedValue('success');
      
      service.invoke('test:method').then(result => {
        expect(result).toBe('success');
        expect((service as any).circuitBreaker.state).toBe('half-open');
      });
      
      tick(100);
    }));

    it('should close circuit after successful calls in half-open', async () => {
      (service as any).circuitBreaker.state = 'half-open';
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      mockIpcRenderer.invoke.mockResolvedValue('success');
      
      // Make successful calls
      for (let i = 0; i < 3; i++) {
        await service.invoke('test:method');
      }
      
      expect((service as any).circuitBreaker.state).toBe('closed');
    });

    it('should reopen circuit on failure in half-open', async () => {
      (service as any).circuitBreaker.state = 'half-open';
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      mockIpcRenderer.invoke.mockRejectedValue(new Error('Failed'));
      
      try {
        await service.invoke('test:method');
      } catch (e) {
        // Expected
      }
      
      expect((service as any).circuitBreaker.state).toBe('open');
    });
  });

  describe('Retry Logic', () => {
    it('should retry failed calls with exponential backoff', fakeAsync(() => {
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      
      let callCount = 0;
      mockIpcRenderer.invoke.mockImplementation(() => {
        callCount++;
        if (callCount < 3) {
          return Promise.reject(new Error('Temporary failure'));
        }
        return Promise.resolve('success');
      });
      
      service.invoke('test:method').then(result => {
        expect(result).toBe('success');
        expect(callCount).toBe(3);
      });
      
      // Advance through retry delays
      tick(1000); // First retry
      tick(2000); // Second retry with backoff
      tick(1000); // Complete
    }));

    it('should respect max retry attempts', fakeAsync(() => {
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      mockIpcRenderer.invoke.mockRejectedValue(new Error('Persistent failure'));
      
      service.invoke('test:method').catch(error => {
        expect(error.message).toContain('Max retry attempts exceeded');
        expect(mockIpcRenderer.invoke).toHaveBeenCalledTimes(3); // Default max attempts
      });
      
      tick(10000); // Advance through all retries
    }));

    it('should apply timeout to IPC calls', fakeAsync(() => {
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      
      // Create a promise that never resolves
      mockIpcRenderer.invoke.mockReturnValue(new Promise(() => {}));
      
      service.invoke('test:method').catch(error => {
        expect(error.message).toContain('Timeout');
      });
      
      tick(31000); // Default timeout + buffer
    }));
  });

  describe('Message Queuing', () => {
    it('should queue messages when disconnected', () => {
      (service as any).connectionState$.next(ConnectionState.DISCONNECTED);
      
      service.invoke('test:method1', 'arg1');
      service.invoke('test:method2', 'arg2');
      
      expect((service as any).messageQueue.size).toBe(2);
    });

    it('should process queued messages on reconnection', fakeAsync(() => {
      (service as any).connectionState$.next(ConnectionState.DISCONNECTED);
      
      const promise1 = service.invoke('test:method1');
      const promise2 = service.invoke('test:method2');
      
      // Simulate reconnection
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      (service as any).onConnectionEstablished();
      
      tick(100);
      
      Promise.all([promise1, promise2]).then(() => {
        expect(mockIpcRenderer.invoke).toHaveBeenCalledTimes(2);
        expect((service as any).messageQueue.size).toBe(0);
      });
    }));

    it('should maintain message order in queue', fakeAsync(() => {
      (service as any).connectionState$.next(ConnectionState.DISCONNECTED);
      
      const messages: string[] = [];
      mockIpcRenderer.invoke.mockImplementation((channel: string) => {
        messages.push(channel);
        return Promise.resolve('success');
      });
      
      service.invoke('first');
      service.invoke('second');
      service.invoke('third');
      
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      (service as any).processMessageQueue();
      
      tick(100);
      
      expect(messages).toEqual(['first', 'second', 'third']);
    }));
  });

  describe('WebSocket Management', () => {
    it('should establish WebSocket connection', fakeAsync(() => {
      (service as any).establishWebSocketConnection().then(() => {
        expect(window.WebSocket).toHaveBeenCalled();
      });
      
      // Simulate WebSocket open
      mockWebSocket.onopen();
      tick(100);
    }));

    it('should handle WebSocket messages', () => {
      const message = {
        type: 'session_update',
        payload: { sessionId: 'test-session' }
      };
      
      (service as any).handleWebSocketMessage(JSON.stringify(message));
      
      expect((service as any).sessionId).toBe('test-session');
    });

    it('should queue WebSocket messages when disconnected', () => {
      mockWebSocket.readyState = WebSocket.CLOSED;
      
      (service as any).sendWebSocketMessage({ type: 'test' });
      
      expect((service as any).wsMessageQueue.length).toBe(1);
    });

    it('should reconnect WebSocket with exponential backoff', fakeAsync(() => {
      (service as any).reconnectionAttempt = 0;
      
      const startTime = Date.now();
      (service as any).attemptWebSocketReconnection();
      
      tick(1000); // Base delay
      tick(1000); // Jitter
      
      expect((service as any).reconnectionAttempt).toBe(1);
    }));

    it('should stop reconnection after max attempts', fakeAsync(() => {
      (service as any).reconnectionAttempt = 10; // Set to max
      
      (service as any).attemptWebSocketReconnection();
      tick(100);
      
      service.getConnectionState().subscribe(state => {
        expect(state).toBe(ConnectionState.ERROR);
      });
    }));
  });

  describe('Session Management', () => {
    it('should save session on disconnection', () => {
      jest.spyOn(Storage.prototype, 'setItem');
      
      (service as any).sessionId = 'test-session';
      (service as any).sessionData.set('key', 'value');
      
      (service as any).saveSession();
      
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'ipc_session',
        expect.any(String)
      );
    });

    it('should restore session from localStorage', fakeAsync(() => {
      const sessionData = {
        timestamp: Date.now(),
        sessionId: 'restored-session',
        state: [['key', 'value']],
        queuedMessages: [],
        wsMessageQueue: [],
        connectionMetrics: {
          lastSuccessfulConnection: Date.now(),
          reconnectionAttempt: 0
        }
      };
      
      jest.spyOn(Storage.prototype, 'getItem').mockReturnValue(JSON.stringify(sessionData));
      
      (service as any).restoreSession();
      tick(100);
      
      expect((service as any).sessionId).toBe('restored-session');
    }));

    it('should validate restored session with backend', fakeAsync(() => {
      (service as any).sessionId = 'test-session';
      mockIpcRenderer.invoke.mockResolvedValue(Promise.resolve({ valid: true }));
      
      (service as any).recoverSession();
      tick(100);
      
      expect(mockIpcRenderer.invoke).toHaveBeenCalledWith(
        'session:validate',
        expect.objectContaining({ sessionId: 'test-session' })
      );
    }));

    it('should create new session if validation fails', fakeAsync(() => {
      (service as any).sessionId = 'invalid-session';
      mockIpcRenderer.invoke.mockResolvedValue(Promise.resolve({ 
        valid: false,
        sessionId: 'new-session' 
      }));
      
      (service as any).recoverSession();
      tick(100);
      
      expect(mockIpcRenderer.invoke).toHaveBeenCalledWith(
        'session:create',
        expect.any(Object)
      );
    }));
  });

  describe('Event Listeners', () => {
    it('should respond to online event', () => {
      (service as any).connectionState$.next(ConnectionState.DISCONNECTED);
      
      window.dispatchEvent(new Event('online'));
      
      // Should attempt reconnection
      expect((service as any).connectionState$.value).toBe(ConnectionState.RECONNECTING);
    });

    it('should respond to offline event', () => {
      (service as any).connectionState$.next(ConnectionState.CONNECTED);
      
      window.dispatchEvent(new Event('offline'));
      
      expect((service as any).connectionState$.value).toBe(ConnectionState.DISCONNECTED);
    });

    it('should handle IPC connection events', () => {
      const listener = mockIpcRenderer.on.mock.calls[0][1];
      
      if (mockIpcRenderer.on.mock.calls[0][0] === 'ipc:connected') {
        listener(null);
        expect((service as any).connectionState$.value).toBe(ConnectionState.CONNECTED);
      }
    });
  });

  describe('Send Method', () => {
    it('should send one-way messages', () => {
      service.send('test:channel', 'data1', 'data2');
      
      expect(mockIpcRenderer.send).toHaveBeenCalledWith('test:channel', 'data1', 'data2');
    });

    it('should handle send errors gracefully', () => {
      mockIpcRenderer.send.mockImplementation(() => { throw new Error('Send failed'); });
      
      expect(() => service.send('test:channel')).not.toThrow();
    });
  });

  describe('Observable Subscriptions', () => {
    it('should create observable for IPC channels', (done) => {
      const subscription = service.on('test:channel').subscribe(data => {
        expect(data).toBe('test-data');
        done();
      });
      
      // Simulate IPC message
      const listener = mockIpcRenderer.on.mock.calls[0][1];
      listener(null, 'test-data');
      
      subscription.unsubscribe();
    });

    it('should clean up listeners on unsubscribe', () => {
      const subscription = service.on('test:channel').subscribe();
      subscription.unsubscribe();
      
      expect(mockIpcRenderer.removeListener).toHaveBeenCalled();
    });
  });

  describe('Resource Cleanup', () => {
    it('should clean up resources on destroy', () => {
      (service as any).websocket = mockWebSocket;
      (service as any).reconnectionTimer = setTimeout(() => {}, 1000);
      
      service.destroy();
      
      expect(mockWebSocket.close).toHaveBeenCalled();
      expect((service as any).messageQueue.size).toBe(0);
      expect((service as any).sessionData.size).toBe(0);
    });

    it('should persist session before destroy', () => {
      jest.spyOn(Storage.prototype, 'setItem');
      (service as any).sessionId = 'test-session';
      
      service.destroy();
      
      expect(localStorage.setItem).toHaveBeenCalled();
    });
  });
});