/**
 * @fileoverview Unit tests for ErrorBoundaryService
 * @author Maya Patel v2.0 - QA & Testing Lead
 * @architecture Testing - Unit test suite for error boundary service
 * @business_logic Validates error handling, categorization, recovery actions
 * @testing_strategy Comprehensive coverage of error scenarios, statistics tracking
 * @coverage_target 95% code coverage for ErrorBoundaryService
 */

import { TestBed } from '@angular/core/testing';
import { NgZone } from '@angular/core';
import { 
  ErrorBoundaryService, 
  ErrorSeverity, 
  ErrorCategory,
  ErrorInfo 
} from './error-boundary.service';

describe('ErrorBoundaryService', () => {
  let service: ErrorBoundaryService;
  let ngZone: NgZone;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ErrorBoundaryService]
    });
    service = TestBed.inject(ErrorBoundaryService);
    ngZone = TestBed.inject(NgZone);
  });

  afterEach(() => {
    service.resetStatistics();
  });

  describe('Service Initialization', () => {
    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should initialize with empty error state', (done) => {
      service.getCurrentError().subscribe(error => {
        expect(error).toBeNull();
        done();
      });
    });

    it('should initialize with zero statistics', () => {
      const stats = service.getStatistics();
      expect(stats.totalErrors).toBe(0);
      expect(stats.criticalErrors).toBe(0);
      expect(stats.errorRate).toBe(0);
    });
  });

  describe('Error Handling', () => {
    it('should handle and categorize a network error', (done) => {
      const networkError = new Error('Failed to fetch');
      networkError.name = 'NetworkError';

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo).toBeDefined();
        expect(errorInfo.category).toBe(ErrorCategory.NETWORK);
        expect(errorInfo.severity).toBe(ErrorSeverity.ERROR);
        expect(errorInfo.retryable).toBe(true);
        done();
      });

      service.handleError(networkError);
    });

    it('should handle IPC errors correctly', (done) => {
      const ipcError = new Error('IPC channel not available');

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.category).toBe(ErrorCategory.IPC);
        expect(errorInfo.message).toContain('Communication with the application failed');
        expect(errorInfo.recoverable).toBe(true);
        done();
      });

      service.handleError(ipcError);
    });

    it('should handle validation errors', (done) => {
      const validationError = new Error('Invalid input data');
      validationError.name = 'ValidationError';

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.category).toBe(ErrorCategory.VALIDATION);
        expect(errorInfo.severity).toBe(ErrorSeverity.WARNING);
        expect(errorInfo.recoverable).toBe(false);
        done();
      });

      service.handleError(validationError);
    });

    it('should handle permission errors as critical', (done) => {
      const permissionError = new Error('Permission denied');
      (permissionError as any).code = 'PERMISSION_DENIED';

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.category).toBe(ErrorCategory.PERMISSION);
        expect(errorInfo.severity).toBe(ErrorSeverity.CRITICAL);
        expect(errorInfo.retryable).toBe(false);
        done();
      });

      service.handleError(permissionError);
    });

    it('should handle timeout errors', (done) => {
      const timeoutError = new Error('Operation timed out');

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.category).toBe(ErrorCategory.TIMEOUT);
        expect(errorInfo.retryable).toBe(true);
        expect(errorInfo.message).toContain('took too long');
        done();
      });

      service.handleError(timeoutError);
    });

    it('should handle unknown errors', (done) => {
      const unknownError = new Error('Something went wrong');

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.category).toBe(ErrorCategory.UNKNOWN);
        expect(errorInfo.severity).toBe(ErrorSeverity.ERROR);
        done();
      });

      service.handleError(unknownError);
    });
  });

  describe('User Actions Generation', () => {
    it('should generate retry action for retryable errors', (done) => {
      const retryableError = new Error('Network error');

      service.getErrors().subscribe(errorInfo => {
        const retryAction = errorInfo.userActions?.find(a => a.label === 'Retry');
        expect(retryAction).toBeDefined();
        expect(retryAction?.primary).toBe(true);
        expect(retryAction?.icon).toBe('refresh');
        done();
      });

      service.handleError(retryableError);
    });

    it('should generate reload action for IPC errors', (done) => {
      const ipcError = new Error('IPC communication failed');

      service.getErrors().subscribe(errorInfo => {
        const reloadAction = errorInfo.userActions?.find(a => a.label === 'Reload Application');
        expect(reloadAction).toBeDefined();
        expect(reloadAction?.icon).toBe('restart_alt');
        done();
      });

      service.handleError(ipcError);
    });

    it('should always include dismiss action', (done) => {
      const anyError = new Error('Any error');

      service.getErrors().subscribe(errorInfo => {
        const dismissAction = errorInfo.userActions?.find(a => a.label === 'Dismiss');
        expect(dismissAction).toBeDefined();
        expect(dismissAction?.icon).toBe('close');
        done();
      });

      service.handleError(anyError);
    });
  });

  describe('Error State Management', () => {
    it('should set current error for critical errors', (done) => {
      const criticalError = new Error('Critical failure');
      (criticalError as any).code = 'PERMISSION_DENIED';

      service.getCurrentError().pipe().subscribe(error => {
        if (error) {
          expect(error.severity).toBe(ErrorSeverity.CRITICAL);
          done();
        }
      });

      service.handleError(criticalError);
    });

    it('should set current error for error severity', (done) => {
      const regularError = new Error('Regular error');

      service.getCurrentError().pipe().subscribe(error => {
        if (error) {
          expect(error.severity).toBe(ErrorSeverity.ERROR);
          done();
        }
      });

      service.handleError(regularError);
    });

    it('should not set current error for warnings', (done) => {
      const warningError = new Error('Validation warning');
      warningError.name = 'ValidationError';

      let errorSet = false;
      service.getCurrentError().subscribe(error => {
        if (error && error.severity === ErrorSeverity.WARNING) {
          errorSet = true;
        }
      });

      service.handleError(warningError);

      setTimeout(() => {
        expect(errorSet).toBe(false);
        done();
      }, 100);
    });

    it('should clear current error', (done) => {
      const error = new Error('Test error');
      service.handleError(error);

      service.clearError();

      service.getCurrentError().subscribe(currentError => {
        expect(currentError).toBeNull();
        done();
      });
    });
  });

  describe('Statistics Tracking', () => {
    it('should track total error count', () => {
      service.handleError(new Error('Error 1'));
      service.handleError(new Error('Error 2'));
      service.handleError(new Error('Error 3'));

      const stats = service.getStatistics();
      expect(stats.totalErrors).toBe(3);
    });

    it('should track errors by category', () => {
      service.handleError(new Error('Network error'));
      service.handleError(new Error('Network timeout'));
      service.handleError(new Error('IPC failed'));

      const stats = service.getStatistics();
      expect(stats.errorsByCategory.get(ErrorCategory.NETWORK)).toBe(2);
      expect(stats.errorsByCategory.get(ErrorCategory.IPC)).toBe(1);
    });

    it('should track errors by severity', () => {
      const criticalError = new Error('Critical');
      (criticalError as any).code = 'PERMISSION_DENIED';
      
      const validationError = new Error('Invalid');
      validationError.name = 'ValidationError';

      service.handleError(criticalError);
      service.handleError(validationError);
      service.handleError(new Error('Regular'));

      const stats = service.getStatistics();
      expect(stats.errorsBySeverity.get(ErrorSeverity.CRITICAL)).toBe(1);
      expect(stats.errorsBySeverity.get(ErrorSeverity.WARNING)).toBe(1);
      expect(stats.errorsBySeverity.get(ErrorSeverity.ERROR)).toBe(1);
    });

    it('should track critical error count separately', () => {
      const critical1 = new Error('Critical 1');
      (critical1 as any).code = 'PERMISSION_DENIED';
      
      const critical2 = new Error('Critical 2');
      critical2.name = 'SecurityError';

      service.handleError(critical1);
      service.handleError(critical2);
      service.handleError(new Error('Regular'));

      const stats = service.getStatistics();
      expect(stats.criticalErrors).toBe(2);
    });

    it('should track last error', () => {
      const firstError = new Error('First');
      const lastError = new Error('Last');

      service.handleError(firstError);
      service.handleError(lastError);

      const stats = service.getStatistics();
      expect(stats.lastError?.message).toContain('Last');
    });

    it('should reset statistics', () => {
      service.handleError(new Error('Error 1'));
      service.handleError(new Error('Error 2'));

      service.resetStatistics();

      const stats = service.getStatistics();
      expect(stats.totalErrors).toBe(0);
      expect(stats.criticalErrors).toBe(0);
      expect(stats.errorsByCategory.size).toBe(0);
      expect(stats.errorsBySeverity.size).toBe(0);
    });
  });

  describe('Error Details Extraction', () => {
    it('should extract stack trace', (done) => {
      const errorWithStack = new Error('Test error');
      errorWithStack.stack = 'Error: Test error\n    at TestFunction';

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.stack).toContain('TestFunction');
        done();
      });

      service.handleError(errorWithStack);
    });

    it('should extract error details', (done) => {
      const detailedError: any = new Error('Detailed error');
      detailedError.code = 'ERR_001';
      detailedError.status = 404;
      detailedError.statusText = 'Not Found';

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.details.code).toBe('ERR_001');
        expect(errorInfo.details.status).toBe(404);
        expect(errorInfo.details.statusText).toBe('Not Found');
        done();
      });

      service.handleError(detailedError);
    });

    it('should generate unique error IDs', (done) => {
      const errorIds: string[] = [];

      service.getErrors().subscribe(errorInfo => {
        errorIds.push(errorInfo.id);
        
        if (errorIds.length === 2) {
          expect(errorIds[0]).not.toBe(errorIds[1]);
          expect(errorIds[0]).toMatch(/^err_/);
          expect(errorIds[1]).toMatch(/^err_/);
          done();
        }
      });

      service.handleError(new Error('Error 1'));
      service.handleError(new Error('Error 2'));
    });

    it('should include timestamp', (done) => {
      const beforeTime = Date.now();

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.timestamp).toBeGreaterThanOrEqual(beforeTime);
        expect(errorInfo.timestamp).toBeLessThanOrEqual(Date.now());
        done();
      });

      service.handleError(new Error('Test'));
    });
  });

  describe('User Message Translation', () => {
    it('should translate network errors to user-friendly message', (done) => {
      const networkError = new Error('Failed to fetch');

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.message).toContain('Unable to connect to the server');
        expect(errorInfo.message).toContain('check your internet connection');
        done();
      });

      service.handleError(networkError);
    });

    it('should translate IPC errors', (done) => {
      const ipcError = new Error('ipcRenderer is not defined');

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.message).toContain('Communication with the application failed');
        expect(errorInfo.message).toContain('restart the application');
        done();
      });

      service.handleError(ipcError);
    });

    it('should translate timeout errors', (done) => {
      const timeoutError = new Error('Request timeout after 30000ms');

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.message).toContain('took too long to complete');
        expect(errorInfo.message).toContain('try again');
        done();
      });

      service.handleError(timeoutError);
    });

    it('should translate permission errors', (done) => {
      const permissionError = new Error('Unauthorized access');

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.message).toContain('do not have permission');
        done();
      });

      service.handleError(permissionError);
    });

    it('should use custom user message if provided', (done) => {
      const customError: any = new Error('Technical error');
      customError.userMessage = 'Please contact support';

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.message).toBe('Please contact support');
        done();
      });

      service.handleError(customError);
    });

    it('should truncate very long messages', (done) => {
      const longMessage = 'A'.repeat(250);
      const longError = new Error(longMessage);

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.message.length).toBeLessThanOrEqual(203);
        expect(errorInfo.message).toContain('...');
        done();
      });

      service.handleError(longError);
    });
  });

  describe('Error Recovery Classification', () => {
    it('should mark network errors as recoverable', (done) => {
      const networkError = new Error('Network failure');

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.recoverable).toBe(true);
        expect(errorInfo.retryable).toBe(true);
        done();
      });

      service.handleError(networkError);
    });

    it('should mark IPC errors as recoverable', (done) => {
      const ipcError = new Error('IPC channel closed');

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.recoverable).toBe(true);
        expect(errorInfo.retryable).toBe(true);
        done();
      });

      service.handleError(ipcError);
    });

    it('should mark validation errors as non-recoverable', (done) => {
      const validationError = new Error('Invalid email format');
      validationError.name = 'ValidationError';

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.recoverable).toBe(false);
        expect(errorInfo.retryable).toBe(false);
        done();
      });

      service.handleError(validationError);
    });

    it('should mark permission errors as non-recoverable', (done) => {
      const permissionError = new Error('Access denied');
      (permissionError as any).status = 401;

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.recoverable).toBe(false);
        expect(errorInfo.retryable).toBe(false);
        done();
      });

      service.handleError(permissionError);
    });

    it('should mark timeout errors as retryable', (done) => {
      const timeoutError = new Error('Connection timeout');

      service.getErrors().subscribe(errorInfo => {
        expect(errorInfo.recoverable).toBe(true);
        expect(errorInfo.retryable).toBe(true);
        done();
      });

      service.handleError(timeoutError);
    });
  });
});