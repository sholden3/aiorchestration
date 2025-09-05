/**
 * @fileoverview Global error boundary service for centralized error handling
 * @author Alex Novak v2.0 - Frontend Integration Architect
 * @architecture Frontend - Centralized error handling and recovery
 * @business_logic Captures all Angular errors, provides recovery actions, tracks error patterns
 * @integration_points Angular ErrorHandler, IPC service, logging service
 * @error_handling Categorization, recovery suggestions, automatic retry for transient errors
 * @performance Error deduplication, rate limiting for error reporting
 */

import { Injectable, ErrorHandler, NgZone } from '@angular/core';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

/**
 * Error severity levels
 * @enum {string}
 */
export enum ErrorSeverity {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical'
}

/**
 * Error category for classification
 * @enum {string}
 */
export enum ErrorCategory {
  NETWORK = 'network',
  IPC = 'ipc',
  VALIDATION = 'validation',
  PERMISSION = 'permission',
  TIMEOUT = 'timeout',
  UNKNOWN = 'unknown'
}

/**
 * Structured error information
 * @interface ErrorInfo
 */
export interface ErrorInfo {
  id: string;
  timestamp: number;
  severity: ErrorSeverity;
  category: ErrorCategory;
  message: string;
  details?: any;
  stack?: string;
  component?: string;
  userId?: string;
  sessionId?: string;
  recoverable: boolean;
  retryable: boolean;
  userActions?: ErrorAction[];
}

/**
 * User action for error recovery
 * @interface ErrorAction
 */
export interface ErrorAction {
  label: string;
  action: () => void | Promise<void>;
  icon?: string;
  primary?: boolean;
}

/**
 * Error statistics for monitoring
 * @interface ErrorStatistics
 */
export interface ErrorStatistics {
  totalErrors: number;
  errorsByCategory: Map<ErrorCategory, number>;
  errorsBySeverity: Map<ErrorSeverity, number>;
  errorRate: number; // errors per minute
  lastError?: ErrorInfo;
  criticalErrors: number;
}

/**
 * @class ErrorBoundaryService
 * @description Centralized error handling service with recovery capabilities
 * 
 * This service provides:
 * - Global error catching and handling
 * - Error categorization and severity assessment
 * - Recovery action suggestions
 * - Error pattern tracking and deduplication
 * - User-friendly error messaging
 */
@Injectable({
  providedIn: 'root'
})
export class ErrorBoundaryService implements ErrorHandler {
  /**
   * Observable stream of errors
   */
  private errors$ = new Subject<ErrorInfo>();
  
  /**
   * Current error state
   */
  private currentError$ = new BehaviorSubject<ErrorInfo | null>(null);
  
  /**
   * Error history for deduplication
   */
  private errorHistory: Map<string, number> = new Map();
  
  /**
   * Error statistics
   */
  private statistics: ErrorStatistics = {
    totalErrors: 0,
    errorsByCategory: new Map(),
    errorsBySeverity: new Map(),
    errorRate: 0,
    criticalErrors: 0
  };
  
  /**
   * Rate limiting for error reporting
   */
  private lastReportTime = 0;
  private reportThreshold = 1000; // 1 second between reports
  
  /**
   * Error count for rate calculation
   */
  private errorCounts: { timestamp: number; count: number }[] = [];

  constructor(private ngZone: NgZone) {
    this.setupErrorRateCalculation();
  }

  /**
   * Angular ErrorHandler implementation
   * @param error The error to handle
   */
  handleError(error: any): void {
    console.error('Global error caught:', error);
    
    // Run error handling in Angular zone
    this.ngZone.run(() => {
      const errorInfo = this.processError(error);
      this.recordError(errorInfo);
      
      // Emit error for subscribers
      this.errors$.next(errorInfo);
      
      // Set as current error if critical or error severity
      if (errorInfo.severity === ErrorSeverity.CRITICAL || 
          errorInfo.severity === ErrorSeverity.ERROR) {
        this.currentError$.next(errorInfo);
      }
      
      // Report to backend if needed
      this.reportErrorToBackend(errorInfo);
    });
  }

  /**
   * Get observable stream of errors
   * @returns Observable of error information
   */
  public getErrors(): Observable<ErrorInfo> {
    return this.errors$.asObservable();
  }

  /**
   * Get current error state
   * @returns Observable of current error or null
   */
  public getCurrentError(): Observable<ErrorInfo | null> {
    return this.currentError$.asObservable();
  }

  /**
   * Clear current error
   */
  public clearError(): void {
    this.currentError$.next(null);
  }

  /**
   * Get error statistics
   * @returns Current error statistics
   */
  public getStatistics(): ErrorStatistics {
    return { ...this.statistics };
  }

  /**
   * Process raw error into structured format
   * @param error Raw error object
   * @returns Structured error information
   * @private
   */
  private processError(error: any): ErrorInfo {
    const errorInfo: ErrorInfo = {
      id: this.generateErrorId(),
      timestamp: Date.now(),
      severity: this.determineSeverity(error),
      category: this.categorizeError(error),
      message: this.extractMessage(error),
      details: this.extractDetails(error),
      stack: error?.stack || error?.rejection?.stack,
      component: this.extractComponent(error),
      recoverable: this.isRecoverable(error),
      retryable: this.isRetryable(error),
      userActions: this.generateUserActions(error)
    };

    return errorInfo;
  }

  /**
   * Determine error severity
   * @param error Error object
   * @returns Error severity level
   * @private
   */
  private determineSeverity(error: any): ErrorSeverity {
    // Critical errors
    if (error?.name === 'SecurityError' || 
        error?.code === 'PERMISSION_DENIED' ||
        error?.message?.includes('CRITICAL')) {
      return ErrorSeverity.CRITICAL;
    }
    
    // Network/IPC errors
    if (error?.name === 'NetworkError' || 
        error?.message?.includes('IPC') ||
        error?.message?.includes('WebSocket')) {
      return ErrorSeverity.ERROR;
    }
    
    // Validation errors
    if (error?.name === 'ValidationError' || 
        error?.status === 400) {
      return ErrorSeverity.WARNING;
    }
    
    // Default to error
    return ErrorSeverity.ERROR;
  }

  /**
   * Categorize error by type
   * @param error Error object
   * @returns Error category
   * @private
   */
  private categorizeError(error: any): ErrorCategory {
    const message = error?.message?.toLowerCase() || '';
    const name = error?.name?.toLowerCase() || '';
    
    if (message.includes('network') || message.includes('fetch') || 
        message.includes('websocket') || error?.status === 0) {
      return ErrorCategory.NETWORK;
    }
    
    if (message.includes('ipc') || message.includes('electron')) {
      return ErrorCategory.IPC;
    }
    
    if (message.includes('validation') || message.includes('invalid') || 
        error?.status === 400) {
      return ErrorCategory.VALIDATION;
    }
    
    if (message.includes('permission') || message.includes('denied') || 
        message.includes('unauthorized') || error?.status === 401) {
      return ErrorCategory.PERMISSION;
    }
    
    if (message.includes('timeout') || message.includes('timed out')) {
      return ErrorCategory.TIMEOUT;
    }
    
    return ErrorCategory.UNKNOWN;
  }

  /**
   * Extract user-friendly message
   * @param error Error object
   * @returns User-friendly error message
   * @private
   */
  private extractMessage(error: any): string {
    // Check for custom message
    if (error?.userMessage) {
      return error.userMessage;
    }
    
    // Map technical errors to user-friendly messages
    const message = error?.message || error?.toString() || 'An unexpected error occurred';
    
    // Network errors
    if (message.includes('Failed to fetch') || message.includes('NetworkError')) {
      return 'Unable to connect to the server. Please check your internet connection.';
    }
    
    // IPC errors
    if (message.includes('IPC') || message.includes('ipcRenderer')) {
      return 'Communication with the application failed. Please restart the application.';
    }
    
    // Timeout errors
    if (message.includes('timeout') || message.includes('timed out')) {
      return 'The operation took too long to complete. Please try again.';
    }
    
    // Permission errors
    if (message.includes('Permission denied') || message.includes('Unauthorized')) {
      return 'You do not have permission to perform this action.';
    }
    
    // Default message
    return message.length > 200 ? message.substring(0, 200) + '...' : message;
  }

  /**
   * Extract error details
   * @param error Error object
   * @returns Error details object
   * @private
   */
  private extractDetails(error: any): any {
    return {
      name: error?.name,
      code: error?.code,
      status: error?.status,
      statusText: error?.statusText,
      url: error?.url,
      originalError: error?.rejection || error?.originalError
    };
  }

  /**
   * Extract component name from error
   * @param error Error object
   * @returns Component name if available
   * @private
   */
  private extractComponent(error: any): string | undefined {
    // Try to extract from stack trace
    const stack = error?.stack || '';
    const match = stack.match(/at\s+(\w+Component)/);
    return match ? match[1] : undefined;
  }

  /**
   * Determine if error is recoverable
   * @param error Error object
   * @returns True if error is recoverable
   * @private
   */
  private isRecoverable(error: any): boolean {
    const category = this.categorizeError(error);
    
    // Network and IPC errors are usually recoverable
    if (category === ErrorCategory.NETWORK || category === ErrorCategory.IPC) {
      return true;
    }
    
    // Timeout errors are recoverable
    if (category === ErrorCategory.TIMEOUT) {
      return true;
    }
    
    // Validation errors are not recoverable without user action
    if (category === ErrorCategory.VALIDATION) {
      return false;
    }
    
    // Permission errors require different authentication
    if (category === ErrorCategory.PERMISSION) {
      return false;
    }
    
    return false;
  }

  /**
   * Determine if error is retryable
   * @param error Error object
   * @returns True if operation can be retried
   * @private
   */
  private isRetryable(error: any): boolean {
    const category = this.categorizeError(error);
    
    // Network, IPC, and timeout errors are retryable
    return category === ErrorCategory.NETWORK || 
           category === ErrorCategory.IPC || 
           category === ErrorCategory.TIMEOUT;
  }

  /**
   * Generate user actions for error recovery
   * @param error Error object
   * @returns Array of user actions
   * @private
   */
  private generateUserActions(error: any): ErrorAction[] {
    const actions: ErrorAction[] = [];
    const category = this.categorizeError(error);
    
    // Retry action for retryable errors
    if (this.isRetryable(error)) {
      actions.push({
        label: 'Retry',
        action: () => this.retryLastOperation(),
        icon: 'refresh',
        primary: true
      });
    }
    
    // Reload action for IPC errors
    if (category === ErrorCategory.IPC) {
      actions.push({
        label: 'Reload Application',
        action: () => window.location.reload(),
        icon: 'restart_alt'
      });
    }
    
    // Dismiss action
    actions.push({
      label: 'Dismiss',
      action: () => this.clearError(),
      icon: 'close'
    });
    
    return actions;
  }

  /**
   * Record error in statistics
   * @param errorInfo Error information
   * @private
   */
  private recordError(errorInfo: ErrorInfo): void {
    // Update total count
    this.statistics.totalErrors++;
    
    // Update category count
    const categoryCount = this.statistics.errorsByCategory.get(errorInfo.category) || 0;
    this.statistics.errorsByCategory.set(errorInfo.category, categoryCount + 1);
    
    // Update severity count
    const severityCount = this.statistics.errorsBySeverity.get(errorInfo.severity) || 0;
    this.statistics.errorsBySeverity.set(errorInfo.severity, severityCount + 1);
    
    // Update critical count
    if (errorInfo.severity === ErrorSeverity.CRITICAL) {
      this.statistics.criticalErrors++;
    }
    
    // Update last error
    this.statistics.lastError = errorInfo;
    
    // Track for rate calculation
    this.errorCounts.push({
      timestamp: Date.now(),
      count: 1
    });
    
    // Check for duplicate errors
    const errorKey = `${errorInfo.category}_${errorInfo.message}`;
    const duplicateCount = this.errorHistory.get(errorKey) || 0;
    this.errorHistory.set(errorKey, duplicateCount + 1);
  }

  /**
   * Report error to backend
   * @param errorInfo Error information
   * @private
   */
  private async reportErrorToBackend(errorInfo: ErrorInfo): Promise<void> {
    // Rate limit reporting
    const now = Date.now();
    if (now - this.lastReportTime < this.reportThreshold) {
      return;
    }
    this.lastReportTime = now;
    
    // Don't report info level errors
    if (errorInfo.severity === ErrorSeverity.INFO) {
      return;
    }
    
    try {
      // TODO: Send to backend logging service
      console.log('[ErrorBoundary] Would report to backend:', errorInfo);
    } catch (error) {
      console.error('[ErrorBoundary] Failed to report error:', error);
    }
  }

  /**
   * Retry last failed operation
   * @private
   */
  private async retryLastOperation(): Promise<void> {
    console.log('[ErrorBoundary] Retrying last operation');
    // TODO: Implement retry logic based on stored operation context
    this.clearError();
  }

  /**
   * Setup error rate calculation
   * @private
   */
  private setupErrorRateCalculation(): void {
    // Calculate error rate every minute
    setInterval(() => {
      const now = Date.now();
      const oneMinuteAgo = now - 60000;
      
      // Filter errors from last minute
      this.errorCounts = this.errorCounts.filter(e => e.timestamp > oneMinuteAgo);
      
      // Calculate rate
      this.statistics.errorRate = this.errorCounts.reduce((sum, e) => sum + e.count, 0);
    }, 60000);
  }

  /**
   * Generate unique error ID
   * @returns Unique error identifier
   * @private
   */
  private generateErrorId(): string {
    return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Reset error statistics
   */
  public resetStatistics(): void {
    this.statistics = {
      totalErrors: 0,
      errorsByCategory: new Map(),
      errorsBySeverity: new Map(),
      errorRate: 0,
      criticalErrors: 0
    };
    this.errorHistory.clear();
    this.errorCounts = [];
  }
}