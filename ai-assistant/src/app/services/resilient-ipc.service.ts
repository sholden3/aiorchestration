/**
 * @fileoverview Resilient IPC service wrapper with automatic reconnection and error recovery
 * @author Alex Novak v2.0 - Frontend Integration Architect
 * @architecture Frontend - Resilient IPC communication layer with retry and reconnection
 * @business_logic Wraps IPC calls with retry logic, queuing, and automatic reconnection
 * @integration_points Electron IPC, backend services, WebSocket connections
 * @error_handling Exponential backoff, circuit breaker pattern, graceful degradation
 * @performance Message queuing during disconnects, <5s reconnection time
 */

import { Injectable, NgZone } from '@angular/core';
import { BehaviorSubject, Observable, Subject, throwError, timer, of } from 'rxjs';
import { 
  retry, 
  retryWhen, 
  delay, 
  take, 
  concatMap, 
  catchError,
  timeout,
  tap,
  map
} from 'rxjs/operators';

/**
 * Connection state enumeration
 * @enum {string}
 */
export enum ConnectionState {
  CONNECTED = 'connected',
  CONNECTING = 'connecting',
  DISCONNECTED = 'disconnected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

/**
 * IPC message structure for queuing
 * @interface IPCMessage
 */
export interface IPCMessage {
  id: string;
  channel: string;
  args: any[];
  timestamp: number;
  retryCount: number;
  resolver?: (value: any) => void;
  rejecter?: (error: any) => void;
}

/**
 * Retry configuration for IPC calls
 * @interface RetryConfig
 */
export interface RetryConfig {
  maxAttempts: number;
  initialDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
  timeout: number;
}

/**
 * Circuit breaker state for failure tracking
 * @interface CircuitBreakerState
 */
interface CircuitBreakerState {
  failures: number;
  lastFailureTime: number;
  state: 'closed' | 'open' | 'half-open';
  successCount: number;
}

/**
 * @class ResilientIPCService
 * @description Provides resilient IPC communication with automatic recovery
 * 
 * This service wraps all IPC communications with:
 * - Automatic reconnection with exponential backoff
 * - Message queuing during disconnections
 * - Circuit breaker pattern for failure protection
 * - Session recovery and state preservation
 * - Correlation ID tracking for debugging
 */
@Injectable({
  providedIn: 'root'
})
export class ResilientIPCService {
  /**
   * Observable connection state for UI binding
   */
  private connectionState$ = new BehaviorSubject<ConnectionState>(ConnectionState.DISCONNECTED);
  
  /**
   * Message queue for offline operations
   */
  private messageQueue: Map<string, IPCMessage> = new Map();
  
  /**
   * Circuit breaker state tracking
   */
  private circuitBreaker: CircuitBreakerState = {
    failures: 0,
    lastFailureTime: 0,
    state: 'closed',
    successCount: 0
  };
  
  /**
   * Default retry configuration
   */
  private defaultRetryConfig: RetryConfig = {
    maxAttempts: 3,
    initialDelay: 1000,
    maxDelay: 30000,
    backoffMultiplier: 2,
    timeout: 30000
  };
  
  /**
   * WebSocket connection for real-time updates
   */
  private websocket: WebSocket | null = null;
  
  /**
   * Reconnection timer
   */
  private reconnectionTimer: any = null;
  
  /**
   * Session recovery data
   */
  private sessionData: Map<string, any> = new Map();
  
  /**
   * Correlation ID for request tracking
   */
  private correlationIdCounter = 0;
  
  /**
   * Session ID for recovery
   */
  private sessionId: string | null = null;
  
  /**
   * Reconnection attempt counter
   */
  private reconnectionAttempt = 0;
  
  /**
   * Maximum reconnection attempts
   */
  private readonly maxReconnectAttempts = 10;
  
  /**
   * Base delay for reconnection (ms)
   */
  private readonly reconnectBaseDelay = 1000;
  
  /**
   * Maximum delay for reconnection (ms)
   */
  private readonly reconnectMaxDelay = 30000;
  
  /**
   * Last successful connection timestamp
   */
  private lastSuccessfulConnection = 0;
  
  /**
   * Message queue for WebSocket
   */
  private wsMessageQueue: any[] = [];

  constructor(private ngZone: NgZone) {
    this.initializeConnection();
    this.setupWindowListeners();
    this.startHealthCheck();
  }

  /**
   * Get current connection state
   * @returns Observable of connection state
   */
  public getConnectionState(): Observable<ConnectionState> {
    return this.connectionState$.asObservable();
  }

  /**
   * Check if currently connected
   * @returns true if connected
   */
  public isConnected(): boolean {
    return this.connectionState$.value === ConnectionState.CONNECTED;
  }

  /**
   * Invoke IPC method with resilience
   * @param channel IPC channel name
   * @param args Arguments to pass
   * @returns Promise with response
   * 
   * @example
   * const result = await ipcService.invoke('get-data', { id: 123 });
   */
  public async invoke<T = any>(channel: string, ...args: any[]): Promise<T> {
    const correlationId = this.generateCorrelationId();
    
    console.log(`[ResilientIPC] Invoking ${channel} with correlation ID: ${correlationId}`);
    
    // Check circuit breaker
    if (this.circuitBreaker.state === 'open') {
      const timeSinceFailure = Date.now() - this.circuitBreaker.lastFailureTime;
      if (timeSinceFailure < 30000) { // 30 second cooldown
        console.warn('[ResilientIPC] Circuit breaker OPEN, rejecting call');
        throw new Error('Service temporarily unavailable - circuit breaker open');
      } else {
        // Try half-open state
        this.circuitBreaker.state = 'half-open';
        console.log('[ResilientIPC] Circuit breaker entering HALF-OPEN state');
      }
    }
    
    // Create message
    const message: IPCMessage = {
      id: correlationId,
      channel,
      args,
      timestamp: Date.now(),
      retryCount: 0
    };
    
    // If disconnected, queue the message
    if (!this.isConnected()) {
      console.log('[ResilientIPC] Not connected, queueing message');
      return this.queueMessage(message);
    }
    
    // Try to execute with retry logic
    return this.executeWithRetry(message);
  }

  /**
   * Send one-way message without expecting response
   * @param channel IPC channel name
   * @param args Arguments to send
   */
  public send(channel: string, ...args: any[]): void {
    if (!window.electron?.ipcRenderer) {
      console.error('[ResilientIPC] IPC not available');
      return;
    }
    
    try {
      window.electron.ipcRenderer.send(channel, ...args);
    } catch (error) {
      console.error('[ResilientIPC] Send error:', error);
      this.handleConnectionError(error);
    }
  }

  /**
   * Subscribe to IPC channel
   * @param channel Channel to subscribe to
   * @returns Observable of channel messages
   */
  public on<T = any>(channel: string): Observable<T> {
    const subject = new Subject<T>();
    
    if (!window.electron?.ipcRenderer) {
      console.error('[ResilientIPC] IPC not available');
      return subject.asObservable();
    }
    
    const listener = (_event: any, ...args: any[]) => {
      this.ngZone.run(() => {
        subject.next(args.length === 1 ? args[0] : args as any);
      });
    };
    
    window.electron.ipcRenderer.on(channel, listener);
    
    // Return observable with cleanup
    return new Observable(observer => {
      const subscription = subject.subscribe(observer);
      
      return () => {
        subscription.unsubscribe();
        window.electron?.ipcRenderer?.removeListener(channel, listener);
      };
    });
  }

  /**
   * Initialize connection to backend
   * @private
   */
  private initializeConnection(): void {
    this.connectionState$.next(ConnectionState.CONNECTING);
    
    // Check if IPC is available
    if (!window.electron?.ipcRenderer) {
      console.error('[ResilientIPC] Electron IPC not available');
      this.connectionState$.next(ConnectionState.ERROR);
      return;
    }
    
    // Test connection with health check
    this.performHealthCheck().then(
      () => {
        console.log('[ResilientIPC] Connection established');
        this.connectionState$.next(ConnectionState.CONNECTED);
        this.onConnectionEstablished();
      },
      (error) => {
        console.error('[ResilientIPC] Initial connection failed:', error);
        this.connectionState$.next(ConnectionState.DISCONNECTED);
        this.scheduleReconnection();
      }
    );
  }

  /**
   * Setup window event listeners for connection monitoring
   * @private
   */
  private setupWindowListeners(): void {
    // Listen for online/offline events
    window.addEventListener('online', () => {
      console.log('[ResilientIPC] Network online');
      if (!this.isConnected()) {
        this.attemptReconnection();
      }
    });
    
    window.addEventListener('offline', () => {
      console.log('[ResilientIPC] Network offline');
      this.connectionState$.next(ConnectionState.DISCONNECTED);
    });
    
    // Listen for IPC connection events
    this.on('ipc:connected').subscribe(() => {
      this.connectionState$.next(ConnectionState.CONNECTED);
      this.onConnectionEstablished();
    });
    
    this.on('ipc:disconnected').subscribe(() => {
      this.handleDisconnection();
    });
  }

  /**
   * Start periodic health checks
   * @private
   */
  private startHealthCheck(): void {
    // Health check every 30 seconds
    timer(30000, 30000).subscribe(() => {
      if (this.isConnected()) {
        this.performHealthCheck().catch(error => {
          console.warn('[ResilientIPC] Health check failed:', error);
          this.handleConnectionError(error);
        });
      }
    });
  }

  /**
   * Perform health check against backend
   * @private
   */
  private async performHealthCheck(): Promise<void> {
    if (!window.electron?.ipcRenderer) {
      throw new Error('IPC not available');
    }
    
    const timeout = 5000; // 5 second timeout for health check
    
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error('Health check timeout'));
      }, timeout);
      
      window.electron.ipcRenderer.invoke('health:check')
        .then(() => {
          clearTimeout(timer);
          resolve();
        })
        .catch(error => {
          clearTimeout(timer);
          reject(error);
        });
    });
  }

  /**
   * Execute IPC call with retry logic
   * @private
   */
  private async executeWithRetry<T>(message: IPCMessage): Promise<T> {
    const config = this.defaultRetryConfig;
    
    for (let attempt = 0; attempt < config.maxAttempts; attempt++) {
      try {
        // Add timeout to the IPC call
        const result = await Promise.race([
          this.executeIPCCall<T>(message.channel, ...message.args),
          this.createTimeout(config.timeout)
        ]);
        
        // Success - update circuit breaker
        this.onCallSuccess();
        
        return result as T;
        
      } catch (error) {
        console.warn(`[ResilientIPC] Attempt ${attempt + 1} failed:`, error);
        
        message.retryCount = attempt + 1;
        
        // Check if we should retry
        if (attempt < config.maxAttempts - 1) {
          const delay = this.calculateBackoffDelay(attempt, config);
          console.log(`[ResilientIPC] Retrying in ${delay}ms...`);
          await this.sleep(delay);
        } else {
          // Final failure - update circuit breaker
          this.onCallFailure();
          throw error;
        }
      }
    }
    
    throw new Error('Max retry attempts exceeded');
  }

  /**
   * Execute raw IPC call
   * @private
   */
  private async executeIPCCall<T>(channel: string, ...args: any[]): Promise<T> {
    if (!window.electron?.ipcRenderer) {
      throw new Error('IPC not available');
    }
    
    return window.electron.ipcRenderer.invoke(channel, ...args);
  }

  /**
   * Queue message for later delivery
   * @private
   */
  private queueMessage<T>(message: IPCMessage): Promise<T> {
    return new Promise((resolve, reject) => {
      message.resolver = resolve;
      message.rejecter = reject;
      
      this.messageQueue.set(message.id, message);
      console.log(`[ResilientIPC] Message queued: ${message.id}`);
      
      // Try to reconnect if not already attempting
      if (this.connectionState$.value === ConnectionState.DISCONNECTED) {
        this.attemptReconnection();
      }
    });
  }

  /**
   * Process queued messages after reconnection
   * @private
   */
  private async processMessageQueue(): Promise<void> {
    if (this.messageQueue.size === 0) return;
    
    console.log(`[ResilientIPC] Processing ${this.messageQueue.size} queued messages`);
    
    const messages = Array.from(this.messageQueue.values());
    this.messageQueue.clear();
    
    for (const message of messages) {
      try {
        const result = await this.executeWithRetry(message);
        if (message.resolver) {
          message.resolver(result);
        }
      } catch (error) {
        if (message.rejecter) {
          message.rejecter(error);
        }
      }
    }
  }

  /**
   * Handle successful connection establishment
   * @private
   */
  private onConnectionEstablished(): void {
    // Reset circuit breaker
    this.circuitBreaker = {
      failures: 0,
      lastFailureTime: 0,
      state: 'closed',
      successCount: 0
    };
    
    // Process queued messages
    this.processMessageQueue();
    
    // Restore session if needed
    this.restoreSession();
  }

  /**
   * Handle disconnection
   * @private
   */
  private handleDisconnection(): void {
    console.warn('[ResilientIPC] Disconnected from backend');
    this.connectionState$.next(ConnectionState.DISCONNECTED);
    
    // Save session data
    this.saveSession();
    
    // Schedule reconnection
    this.scheduleReconnection();
  }

  /**
   * Handle connection error
   * @private
   */
  private handleConnectionError(error: any): void {
    console.error('[ResilientIPC] Connection error:', error);
    
    if (this.connectionState$.value === ConnectionState.CONNECTED) {
      this.handleDisconnection();
    }
  }

  /**
   * Schedule reconnection attempt
   * @private
   */
  private scheduleReconnection(): void {
    if (this.reconnectionTimer) {
      return; // Already scheduled
    }
    
    const delay = this.calculateBackoffDelay(
      this.circuitBreaker.failures,
      this.defaultRetryConfig
    );
    
    console.log(`[ResilientIPC] Scheduling reconnection in ${delay}ms`);
    
    this.reconnectionTimer = setTimeout(() => {
      this.reconnectionTimer = null;
      this.attemptReconnection();
    }, delay);
  }

  /**
   * Attempt to reconnect
   * @private
   */
  private async attemptReconnection(): Promise<void> {
    if (this.connectionState$.value === ConnectionState.RECONNECTING) {
      return; // Already attempting
    }
    
    console.log('[ResilientIPC] Attempting reconnection...');
    this.connectionState$.next(ConnectionState.RECONNECTING);
    
    try {
      await this.performHealthCheck();
      
      console.log('[ResilientIPC] Reconnection successful');
      this.connectionState$.next(ConnectionState.CONNECTED);
      this.onConnectionEstablished();
      
    } catch (error) {
      console.error('[ResilientIPC] Reconnection failed:', error);
      this.connectionState$.next(ConnectionState.DISCONNECTED);
      this.circuitBreaker.failures++;
      this.scheduleReconnection();
    }
  }

  /**
   * Save session data for recovery
   * @private
   */
  private saveSession(): void {
    const sessionData = {
      timestamp: Date.now(),
      sessionId: this.sessionId,
      state: Array.from(this.sessionData.entries()),
      queuedMessages: Array.from(this.messageQueue.entries()).map(([id, msg]) => ({
        id,
        channel: msg.channel,
        args: msg.args,
        timestamp: msg.timestamp
      })),
      wsMessageQueue: this.wsMessageQueue,
      connectionMetrics: {
        lastSuccessfulConnection: this.lastSuccessfulConnection,
        reconnectionAttempt: this.reconnectionAttempt
      }
    };
    
    localStorage.setItem('ipc_session', JSON.stringify(sessionData));
    console.log('[ResilientIPC] Session saved with metrics');
  }

  /**
   * Restore session after reconnection
   * @private
   */
  private async restoreSession(): Promise<void> {
    const saved = localStorage.getItem('ipc_session');
    if (!saved) {
      // No saved session, try to recover from backend
      if (this.sessionId) {
        await this.recoverSession();
      }
      return;
    }
    
    try {
      const sessionData = JSON.parse(saved);
      
      // Check if session is recent (within 5 minutes)
      if (Date.now() - sessionData.timestamp < 300000) {
        // Restore session ID
        if (sessionData.sessionId) {
          this.sessionId = sessionData.sessionId;
        }
        
        // Restore state
        this.sessionData = new Map(sessionData.state);
        
        // Re-queue messages if very recent (within 30 seconds)
        if (Date.now() - sessionData.timestamp < 30000) {
          sessionData.queuedMessages.forEach((msg: any) => {
            if (!this.messageQueue.has(msg.id)) {
              this.messageQueue.set(msg.id, {
                ...msg,
                retryCount: 0
              });
            }
          });
        }
        
        console.log('[ResilientIPC] Session restored from localStorage');
        
        // Validate restored session with backend
        await this.recoverSession();
      }
      
      localStorage.removeItem('ipc_session');
    } catch (error) {
      console.error('[ResilientIPC] Failed to restore session:', error);
    }
  }

  /**
   * Update circuit breaker on successful call
   * @private
   */
  private onCallSuccess(): void {
    if (this.circuitBreaker.state === 'half-open') {
      this.circuitBreaker.successCount++;
      
      if (this.circuitBreaker.successCount >= 3) {
        console.log('[ResilientIPC] Circuit breaker CLOSED');
        this.circuitBreaker.state = 'closed';
        this.circuitBreaker.failures = 0;
        this.circuitBreaker.successCount = 0;
      }
    }
  }

  /**
   * Update circuit breaker on failed call
   * @private
   */
  private onCallFailure(): void {
    this.circuitBreaker.failures++;
    this.circuitBreaker.lastFailureTime = Date.now();
    
    if (this.circuitBreaker.state === 'half-open') {
      console.log('[ResilientIPC] Circuit breaker reopening to OPEN');
      this.circuitBreaker.state = 'open';
      this.circuitBreaker.successCount = 0;
    } else if (this.circuitBreaker.failures >= 5) {
      console.log('[ResilientIPC] Circuit breaker OPEN');
      this.circuitBreaker.state = 'open';
    }
  }

  /**
   * Calculate exponential backoff delay
   * @private
   */
  private calculateBackoffDelay(attempt: number, config: RetryConfig): number {
    const delay = Math.min(
      config.initialDelay * Math.pow(config.backoffMultiplier, attempt),
      config.maxDelay
    );
    
    // Add jitter (±10%)
    const jitter = delay * 0.1 * (Math.random() * 2 - 1);
    
    return Math.round(delay + jitter);
  }

  /**
   * Generate correlation ID for request tracking
   * @private
   */
  private generateCorrelationId(): string {
    return `ipc_${Date.now()}_${++this.correlationIdCounter}`;
  }

  /**
   * Create timeout promise
   * @private
   */
  private createTimeout(ms: number): Promise<never> {
    return new Promise((_, reject) => {
      setTimeout(() => reject(new Error(`Timeout after ${ms}ms`)), ms);
    });
  }

  /**
   * Sleep for specified milliseconds
   * @private
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Establish WebSocket connection with exponential backoff
   * @method establishWebSocketConnection
   * @returns {Promise<void>} Resolves when WebSocket is connected
   * @throws {Error} If WebSocket connection fails
   */
  private async establishWebSocketConnection(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // Check if WebSocket is already connected
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
          resolve();
          return;
        }

        // Close existing connection if any
        if (this.websocket) {
          this.websocket.close();
        }

        // Create new WebSocket connection
        const wsUrl = `ws://localhost:8000/ws${this.sessionId ? `?session_id=${this.sessionId}` : ''}`;
        this.websocket = new WebSocket(wsUrl);

        // Set up event handlers
        this.websocket.onopen = () => {
          console.log('[ResilientIPC] WebSocket connected', { url: wsUrl });
          this.reconnectionAttempt = 0;
          this.lastSuccessfulConnection = Date.now();
          resolve();
        };

        this.websocket.onerror = (error) => {
          console.error('[ResilientIPC] WebSocket error', error);
          reject(new Error('WebSocket connection failed'));
        };

        this.websocket.onclose = (event) => {
          console.warn('[ResilientIPC] WebSocket closed', {
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean
          });
          
          // Trigger reconnection if not already in progress
          if (this.connectionState$.value === ConnectionState.CONNECTED) {
            this.handleWebSocketDisconnection();
          }
        };

        this.websocket.onmessage = (event) => {
          this.handleWebSocketMessage(event.data);
        };

        // Set timeout for connection
        setTimeout(() => {
          if (this.websocket?.readyState !== WebSocket.OPEN) {
            this.websocket?.close();
            reject(new Error('WebSocket connection timeout'));
          }
        }, 5000);

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Handle WebSocket disconnection with automatic reconnection
   * @method handleWebSocketDisconnection
   * @private
   */
  private handleWebSocketDisconnection(): void {
    console.warn('[ResilientIPC] WebSocket disconnected, attempting reconnection');
    this.attemptWebSocketReconnection();
  }

  /**
   * Attempt WebSocket reconnection with exponential backoff
   * @method attemptWebSocketReconnection
   * @private
   */
  private async attemptWebSocketReconnection(): Promise<void> {
    if (this.reconnectionAttempt >= this.maxReconnectAttempts) {
      console.error('[ResilientIPC] Max WebSocket reconnection attempts exceeded');
      this.connectionState$.next(ConnectionState.ERROR);
      return;
    }

    this.reconnectionAttempt++;

    // Calculate exponential backoff with jitter
    const baseDelay = Math.min(
      this.reconnectBaseDelay * Math.pow(2, this.reconnectionAttempt - 1),
      this.reconnectMaxDelay
    );
    const jitter = Math.random() * 1000; // 0-1000ms jitter
    const delay = baseDelay + jitter;

    console.log('[ResilientIPC] WebSocket reconnection attempt', {
      attempt: this.reconnectionAttempt,
      delay: Math.round(delay),
      sessionId: this.sessionId
    });

    await this.sleep(delay);

    try {
      await this.establishWebSocketConnection();
      
      // Reconnection successful, process queued messages
      this.processWebSocketQueue();
      
    } catch (error) {
      console.error('[ResilientIPC] WebSocket reconnection failed', {
        error,
        attempt: this.reconnectionAttempt
      });

      // Schedule next reconnection attempt
      if (this.reconnectionAttempt < this.maxReconnectAttempts) {
        this.attemptWebSocketReconnection();
      }
    }
  }

  /**
   * Handle incoming WebSocket messages
   * @method handleWebSocketMessage
   * @param {string} data - Raw message data
   * @private
   */
  private handleWebSocketMessage(data: string): void {
    try {
      const message = JSON.parse(data);
      console.debug('[ResilientIPC] WebSocket message received', { type: message.type });
      
      this.ngZone.run(() => {
        // Handle different message types
        switch (message.type) {
          case 'session_update':
            this.handleSessionUpdate(message.payload);
            break;
          case 'health_status':
            this.handleHealthStatus(message.payload);
            break;
          case 'broadcast':
            this.handleBroadcast(message.payload);
            break;
          case 'error':
            this.handleServerError(message.payload);
            break;
          default:
            console.warn('[ResilientIPC] Unknown WebSocket message type', { type: message.type });
        }
      });
    } catch (error) {
      console.error('[ResilientIPC] Failed to process WebSocket message', { error, data });
    }
  }

  /**
   * Handle session update from server
   * @method handleSessionUpdate
   * @param {any} payload - Session update payload
   * @private
   */
  private handleSessionUpdate(payload: any): void {
    console.log('[ResilientIPC] Session update received', payload);
    
    if (payload.sessionId) {
      this.sessionId = payload.sessionId;
      this.sessionData.set('sessionId', payload.sessionId);
    }
    
    if (payload.data) {
      Object.entries(payload.data).forEach(([key, value]) => {
        this.sessionData.set(key, value);
      });
    }
  }

  /**
   * Handle health status update
   * @method handleHealthStatus
   * @param {any} payload - Health status payload
   * @private
   */
  private handleHealthStatus(payload: any): void {
    console.debug('[ResilientIPC] Health status received', payload);
    
    if (payload.healthy === false) {
      console.warn('[ResilientIPC] Backend reported unhealthy status');
      this.circuitBreaker.state = 'open';
      this.circuitBreaker.lastFailureTime = Date.now();
    }
  }

  /**
   * Handle broadcast message
   * @method handleBroadcast
   * @param {any} payload - Broadcast payload
   * @private
   */
  private handleBroadcast(payload: any): void {
    // Emit broadcast message to subscribers
    console.debug('[ResilientIPC] Broadcast received', { channel: payload.channel });
  }

  /**
   * Handle server error message
   * @method handleServerError
   * @param {any} payload - Error payload
   * @private
   */
  private handleServerError(payload: any): void {
    console.error('[ResilientIPC] Server error received', payload);
    
    if (payload.critical) {
      this.circuitBreaker.state = 'open';
      this.circuitBreaker.lastFailureTime = Date.now();
    }
  }

  /**
   * Send message via WebSocket with queuing
   * @method sendWebSocketMessage
   * @param {any} message - Message to send
   * @returns {Promise<void>} Resolves when message is sent
   * @private
   */
  private async sendWebSocketMessage(message: any): Promise<void> {
    if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
      console.log('[ResilientIPC] WebSocket not ready, queueing message');
      this.wsMessageQueue.push(message);
      
      // Attempt to establish connection
      if (!this.websocket || this.websocket.readyState === WebSocket.CLOSED) {
        this.attemptWebSocketReconnection();
      }
      return;
    }

    try {
      this.websocket.send(JSON.stringify(message));
      console.debug('[ResilientIPC] WebSocket message sent', { type: message.type });
    } catch (error) {
      console.error('[ResilientIPC] Failed to send WebSocket message', error);
      this.wsMessageQueue.push(message);
      this.handleWebSocketDisconnection();
    }
  }

  /**
   * Process queued WebSocket messages
   * @method processWebSocketQueue
   * @private
   */
  private processWebSocketQueue(): void {
    if (this.wsMessageQueue.length === 0) return;
    
    console.log('[ResilientIPC] Processing WebSocket queue', { count: this.wsMessageQueue.length });
    
    while (this.wsMessageQueue.length > 0 && 
           this.websocket?.readyState === WebSocket.OPEN) {
      const message = this.wsMessageQueue.shift();
      if (message) {
        this.sendWebSocketMessage(message);
      }
    }
  }

  /**
   * Create new session with backend
   * @method createNewSession
   * @returns {Promise<void>} Resolves when session is created
   * @private
   */
  private async createNewSession(): Promise<void> {
    try {
      const response = await this.invoke('session:create', {
        timestamp: Date.now(),
        metadata: {
          userAgent: navigator.userAgent,
          platform: navigator.platform
        }
      });
      
      if (response.sessionId) {
        this.sessionId = response.sessionId;
        this.sessionData.set('sessionId', response.sessionId);
        console.log('[ResilientIPC] New session created', { sessionId: this.sessionId });
      }
    } catch (error) {
      console.error('[ResilientIPC] Failed to create session', error);
    }
  }

  /**
   * Recover session after reconnection
   * @method recoverSession
   * @returns {Promise<void>} Resolves when session is recovered
   * @private
   */
  private async recoverSession(): Promise<void> {
    if (!this.sessionId) {
      console.log('[ResilientIPC] No session to recover, creating new session');
      await this.createNewSession();
      return;
    }

    try {
      // Validate session with backend
      const response = await this.invoke('session:validate', {
        sessionId: this.sessionId,
        timestamp: this.lastSuccessfulConnection
      });

      if (response.valid) {
        console.log('[ResilientIPC] Session recovered successfully', {
          sessionId: this.sessionId
        });
        
        // Restore any persisted state
        if (response.state) {
          Object.entries(response.state).forEach(([key, value]) => {
            this.sessionData.set(key, value);
          });
        }
      } else {
        // Session invalid, create new one
        console.warn('[ResilientIPC] Session invalid, creating new session');
        await this.createNewSession();
      }
    } catch (error) {
      console.error('[ResilientIPC] Session recovery failed', error);
      await this.createNewSession();
    }
  }

  /**
   * Clean up resources
   */
  public destroy(): void {
    if (this.reconnectionTimer) {
      clearTimeout(this.reconnectionTimer);
    }
    
    if (this.websocket) {
      this.websocket.close();
    }
    
    this.messageQueue.clear();
    this.sessionData.clear();
    this.wsMessageQueue = [];
  }
}