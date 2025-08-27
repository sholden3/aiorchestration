/**
 * FIX H2: IPC Error Boundary Service with Circuit Breaker
 * Architecture: Alex Novak
 * Pattern: Defensive IPC handling with graceful degradation
 */
import { Injectable, NgZone } from '@angular/core';
import { Subject, Observable, of, throwError } from 'rxjs';
import { timeout, catchError, retry, tap } from 'rxjs/operators';

// Circuit breaker states
enum CircuitState {
  CLOSED = 'closed',
  OPEN = 'open',
  HALF_OPEN = 'half_open'
}

// IPC Error types
export enum IPCErrorType {
  TIMEOUT = 'TIMEOUT',
  CIRCUIT_OPEN = 'CIRCUIT_OPEN',
  CONNECTION_FAILED = 'CONNECTION_FAILED',
  INVALID_RESPONSE = 'INVALID_RESPONSE',
  UNKNOWN = 'UNKNOWN'
}

export class IPCError extends Error {
  constructor(
    message: string,
    public type: IPCErrorType,
    public channel?: string,
    public correlationId?: string,
    public originalError?: any
  ) {
    super(message);
    this.name = 'IPCError';
  }
}

interface IPCOptions {
  timeout?: number;
  retries?: number;
  fallbackValue?: any;
  skipCircuitBreaker?: boolean;
}

interface CircuitBreakerConfig {
  failureThreshold: number;
  recoveryTime: number;
  monitoringWindow: number;
}

class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount = 0;
  private successCount = 0;
  private lastFailureTime = 0;
  private totalOpens = 0;
  
  constructor(private config: CircuitBreakerConfig) {}
  
  isOpen(): boolean {
    // Check if we should transition to HALF_OPEN
    if (this.state === CircuitState.OPEN) {
      const timeSinceLastFailure = Date.now() - this.lastFailureTime;
      if (timeSinceLastFailure >= this.config.recoveryTime) {
        this.state = CircuitState.HALF_OPEN;
        this.successCount = 0;
        console.log('Circuit breaker transitioning to HALF_OPEN');
      }
    }
    return this.state === CircuitState.OPEN;
  }
  
  recordSuccess(): void {
    if (this.state === CircuitState.HALF_OPEN) {
      this.successCount++;
      // Need 3 successful calls to close circuit
      if (this.successCount >= 3) {
        this.state = CircuitState.CLOSED;
        this.failureCount = 0;
        console.log('Circuit breaker CLOSED after recovery');
      }
    } else if (this.state === CircuitState.CLOSED) {
      // Reset failure count on success
      if (this.failureCount > 0) {
        this.failureCount--;
      }
    }
  }
  
  recordFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    
    if (this.state !== CircuitState.OPEN && 
        this.failureCount >= this.config.failureThreshold) {
      this.state = CircuitState.OPEN;
      this.totalOpens++;
      console.warn(`Circuit breaker OPEN after ${this.failureCount} failures`);
    }
  }
  
  getStatus(): any {
    return {
      state: this.state,
      failureCount: this.failureCount,
      successCount: this.successCount,
      totalOpens: this.totalOpens,
      isHealthy: this.state === CircuitState.CLOSED
    };
  }
  
  reset(): void {
    this.state = CircuitState.CLOSED;
    this.failureCount = 0;
    this.successCount = 0;
  }
}

export interface IPCMetrics {
  totalCalls: number;
  successfulCalls: number;
  failedCalls: number;
  timeouts: number;
  circuitBreakerTrips: number;
  averageResponseTime: number;
  errorsByType: Map<IPCErrorType, number>;
  errorsByChannel: Map<string, number>;
}

/**
 * FIX H2: IPC Error Boundary Service
 * Provides defensive error handling for all IPC operations
 */
@Injectable({
  providedIn: 'root'
})
export class IPCErrorBoundaryService {
  private circuitBreakers = new Map<string, CircuitBreaker>();
  private metrics: IPCMetrics = {
    totalCalls: 0,
    successfulCalls: 0,
    failedCalls: 0,
    timeouts: 0,
    circuitBreakerTrips: 0,
    averageResponseTime: 0,
    errorsByType: new Map(),
    errorsByChannel: new Map()
  };
  
  private responseTimes: number[] = [];
  private maxResponseTimeSamples = 100;
  
  constructor(private ngZone: NgZone) {
    console.log('IPC Error Boundary Service initialized');
  }
  
  /**
   * Safe IPC invoke with comprehensive error handling
   * Alex's pattern: Never let IPC failures crash the renderer
   */
  async safeIPCInvoke<T>(
    channel: string,
    data?: any,
    options: IPCOptions = {}
  ): Promise<T | null> {
    const correlationId = this.generateCorrelationId();
    const startTime = Date.now();
    const timeoutMs = options.timeout || 5000;
    const retries = options.retries || 0;
    const fallbackValue = options.fallbackValue;
    
    this.metrics.totalCalls++;
    
    try {
      // Check if electronAPI is available
      if (!this.isElectronAvailable()) {
        throw new IPCError(
          'Electron API not available',
          IPCErrorType.CONNECTION_FAILED,
          channel,
          correlationId
        );
      }
      
      // Check circuit breaker unless explicitly skipped
      if (!options.skipCircuitBreaker) {
        const breaker = this.getCircuitBreaker(channel);
        if (breaker.isOpen()) {
          this.metrics.circuitBreakerTrips++;
          this.recordError(channel, IPCErrorType.CIRCUIT_OPEN);
          
          if (fallbackValue !== undefined) {
            console.warn(`Circuit breaker open for ${channel}, using fallback`);
            return fallbackValue;
          }
          
          throw new IPCError(
            `Circuit breaker open for ${channel}`,
            IPCErrorType.CIRCUIT_OPEN,
            channel,
            correlationId
          );
        }
      }
      
      // Prepare IPC call with timeout
      const ipcPromise = this.executeIPCCall<T>(channel, { ...data, correlationId });
      
      // Add timeout wrapper
      const timeoutPromise = new Promise<never>((_, reject) => {
        setTimeout(() => {
          reject(new IPCError(
            `IPC call timed out after ${timeoutMs}ms`,
            IPCErrorType.TIMEOUT,
            channel,
            correlationId
          ));
        }, timeoutMs);
      });
      
      // Race between IPC call and timeout
      const result = await Promise.race([ipcPromise, timeoutPromise]);
      
      // Record success
      const responseTime = Date.now() - startTime;
      this.recordSuccess(channel, responseTime);
      
      return result;
      
    } catch (error) {
      // Handle different error types
      if (error instanceof IPCError) {
        return this.handleIPCError(error, channel, fallbackValue);
      }
      
      // Convert unknown errors to IPCError
      const ipcError = new IPCError(
        error.message || 'Unknown IPC error',
        IPCErrorType.UNKNOWN,
        channel,
        correlationId,
        error
      );
      
      return this.handleIPCError(ipcError, channel, fallbackValue);
    }
  }
  
  /**
   * Execute the actual IPC call
   */
  private async executeIPCCall<T>(channel: string, data: any): Promise<T> {
    return new Promise((resolve, reject) => {
      try {
        // Access electronAPI through window
        const electronAPI = (window as any).electronAPI;
        
        if (!electronAPI) {
          reject(new Error(`Electron API not available`));
          return;
        }
        
        // Check if we have the invoke method (standard pattern)
        if (typeof electronAPI.invoke === 'function') {
          // Use standard invoke pattern
          electronAPI.invoke(channel, data)
            .then(resolve)
            .catch(reject);
        } 
        // Fallback to channel-specific method if it exists
        else if (typeof electronAPI[channel] === 'function') {
          electronAPI[channel](data)
            .then(resolve)
            .catch(reject);
        } 
        else {
          reject(new Error(`IPC channel ${channel} not available`));
        }
          
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Handle IPC errors with logging and metrics
   */
  private handleIPCError<T>(
    error: IPCError,
    channel: string,
    fallbackValue?: T
  ): T {
    // Log error details
    console.error(`IPC Error [${error.type}] on ${channel}:`, {
      message: error.message,
      correlationId: error.correlationId,
      originalError: error.originalError
    });
    
    // Record failure metrics
    this.recordError(channel, error.type);
    
    // Record circuit breaker failure
    const breaker = this.getCircuitBreaker(channel);
    breaker.recordFailure();
    
    // Use fallback if available
    if (fallbackValue !== undefined) {
      console.warn(`Using fallback value for ${channel}`);
      return fallbackValue;
    }
    
    // No fallback available - rethrow the error
    throw error;
  }
  
  /**
   * Get or create circuit breaker for channel
   */
  private getCircuitBreaker(channel: string): CircuitBreaker {
    if (!this.circuitBreakers.has(channel)) {
      this.circuitBreakers.set(channel, new CircuitBreaker({
        failureThreshold: 5,
        recoveryTime: 30000, // 30 seconds
        monitoringWindow: 60000 // 1 minute
      }));
    }
    return this.circuitBreakers.get(channel)!;
  }
  
  /**
   * Check if Electron API is available
   */
  private isElectronAvailable(): boolean {
    return typeof window !== 'undefined' && 
           !!(window as any).electronAPI;
  }
  
  /**
   * Generate correlation ID for request tracking
   */
  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * Record successful IPC call
   */
  private recordSuccess(channel: string, responseTime: number): void {
    this.metrics.successfulCalls++;
    
    // Update response time tracking
    this.responseTimes.push(responseTime);
    if (this.responseTimes.length > this.maxResponseTimeSamples) {
      this.responseTimes.shift();
    }
    
    // Calculate average response time
    const sum = this.responseTimes.reduce((a, b) => a + b, 0);
    this.metrics.averageResponseTime = sum / this.responseTimes.length;
    
    // Record circuit breaker success
    const breaker = this.getCircuitBreaker(channel);
    breaker.recordSuccess();
  }
  
  /**
   * Record IPC error
   */
  private recordError(channel: string, errorType: IPCErrorType): void {
    this.metrics.failedCalls++;
    
    // Track errors by type
    const currentCount = this.metrics.errorsByType.get(errorType) || 0;
    this.metrics.errorsByType.set(errorType, currentCount + 1);
    
    // Track errors by channel
    const channelCount = this.metrics.errorsByChannel.get(channel) || 0;
    this.metrics.errorsByChannel.set(channel, channelCount + 1);
    
    // Track specific error types
    if (errorType === IPCErrorType.TIMEOUT) {
      this.metrics.timeouts++;
    }
  }
  
  /**
   * Get current metrics
   */
  getMetrics(): IPCMetrics {
    return { ...this.metrics };
  }
  
  /**
   * Get circuit breaker status for all channels
   */
  getCircuitBreakerStatus(): Map<string, any> {
    const status = new Map<string, any>();
    this.circuitBreakers.forEach((breaker, channel) => {
      status.set(channel, breaker.getStatus());
    });
    return status;
  }
  
  /**
   * Reset all circuit breakers
   */
  resetAllCircuitBreakers(): void {
    this.circuitBreakers.forEach(breaker => breaker.reset());
    console.log('All circuit breakers reset');
  }
  
  /**
   * Reset metrics
   */
  resetMetrics(): void {
    this.metrics = {
      totalCalls: 0,
      successfulCalls: 0,
      failedCalls: 0,
      timeouts: 0,
      circuitBreakerTrips: 0,
      averageResponseTime: 0,
      errorsByType: new Map(),
      errorsByChannel: new Map()
    };
    this.responseTimes = [];
  }
}