/**
 * @fileoverview Error boundary component for displaying and handling errors
 * @author Alex Novak v2.0 - Frontend Integration Architect
 * @architecture Frontend - Error display and recovery UI component
 * @business_logic Displays errors with appropriate severity, provides recovery actions
 * @integration_points ErrorBoundaryService, Material Design components
 * @error_handling User-friendly error display, recovery actions, error dismissal
 * @performance Debounced error display, automatic dismissal for non-critical errors
 */

import { Component, OnInit, OnDestroy, Input, Output, EventEmitter } from '@angular/core';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { 
  ErrorBoundaryService, 
  ErrorInfo, 
  ErrorSeverity,
  ErrorAction 
} from '../../services/error-boundary.service';

/**
 * @class ErrorBoundaryComponent
 * @description Component for displaying errors with recovery actions
 * 
 * This component provides:
 * - Animated error display with severity-based styling
 * - Recovery action buttons
 * - Automatic dismissal for non-critical errors
 * - Error details expansion
 * - Connection status indicator
 */
@Component({
  selector: 'app-error-boundary',
  templateUrl: './error-boundary.component.html',
  styleUrls: ['./error-boundary.component.scss'],
  animations: [
    trigger('slideIn', [
      transition(':enter', [
        style({ transform: 'translateY(-100%)', opacity: 0 }),
        animate('300ms ease-out', style({ transform: 'translateY(0)', opacity: 1 }))
      ]),
      transition(':leave', [
        animate('300ms ease-in', style({ transform: 'translateY(-100%)', opacity: 0 }))
      ])
    ]),
    trigger('expand', [
      state('collapsed', style({ height: '0', opacity: 0 })),
      state('expanded', style({ height: '*', opacity: 1 })),
      transition('collapsed <=> expanded', animate('200ms ease-in-out'))
    ])
  ]
})
export class ErrorBoundaryComponent implements OnInit, OnDestroy {
  /**
   * Current error to display
   */
  currentError: ErrorInfo | null = null;
  
  /**
   * Whether error details are expanded
   */
  detailsExpanded = false;
  
  /**
   * Auto-dismiss timer
   */
  private dismissTimer: any;
  
  /**
   * Component destruction subject
   */
  private destroy$ = new Subject<void>();
  
  /**
   * Error severity enum for template
   */
  ErrorSeverity = ErrorSeverity;
  
  /**
   * Processing state for actions
   */
  processingAction = false;

  constructor(private errorBoundaryService: ErrorBoundaryService) {}

  /**
   * Component initialization
   */
  ngOnInit(): void {
    // Subscribe to current error
    this.errorBoundaryService.getCurrentError()
      .pipe(takeUntil(this.destroy$))
      .subscribe(error => {
        this.handleNewError(error);
      });
  }

  /**
   * Component destruction
   */
  ngOnDestroy(): void {
    this.clearDismissTimer();
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Handle new error display
   * @param error Error to display
   * @private
   */
  private handleNewError(error: ErrorInfo | null): void {
    this.clearDismissTimer();
    this.currentError = error;
    this.detailsExpanded = false;
    this.processingAction = false;
    
    if (error && error.severity !== ErrorSeverity.CRITICAL && 
        error.severity !== ErrorSeverity.ERROR) {
      // Auto-dismiss warnings and info after 5 seconds
      this.dismissTimer = setTimeout(() => {
        this.dismiss();
      }, 5000);
    }
  }

  /**
   * Get icon for error severity
   * @param severity Error severity
   * @returns Material icon name
   */
  getSeverityIcon(severity: ErrorSeverity): string {
    switch (severity) {
      case ErrorSeverity.CRITICAL:
        return 'error';
      case ErrorSeverity.ERROR:
        return 'warning';
      case ErrorSeverity.WARNING:
        return 'info';
      case ErrorSeverity.INFO:
        return 'info_outline';
      default:
        return 'info';
    }
  }

  /**
   * Get CSS class for error severity
   * @param severity Error severity
   * @returns CSS class name
   */
  getSeverityClass(severity: ErrorSeverity): string {
    return `error-${severity}`;
  }

  /**
   * Toggle error details expansion
   */
  toggleDetails(): void {
    this.detailsExpanded = !this.detailsExpanded;
  }

  /**
   * Execute error recovery action
   * @param action Action to execute
   */
  async executeAction(action: ErrorAction): Promise<void> {
    this.processingAction = true;
    
    try {
      const result = action.action();
      if (result instanceof Promise) {
        await result;
      }
    } catch (error) {
      console.error('Failed to execute error action:', error);
    } finally {
      this.processingAction = false;
    }
  }

  /**
   * Dismiss current error
   */
  dismiss(): void {
    this.clearDismissTimer();
    this.errorBoundaryService.clearError();
    this.currentError = null;
  }

  /**
   * Clear auto-dismiss timer
   * @private
   */
  private clearDismissTimer(): void {
    if (this.dismissTimer) {
      clearTimeout(this.dismissTimer);
      this.dismissTimer = null;
    }
  }

  /**
   * Copy error details to clipboard
   */
  copyErrorDetails(): void {
    if (!this.currentError) return;
    
    const details = JSON.stringify({
      id: this.currentError.id,
      timestamp: new Date(this.currentError.timestamp).toISOString(),
      severity: this.currentError.severity,
      category: this.currentError.category,
      message: this.currentError.message,
      details: this.currentError.details,
      stack: this.currentError.stack
    }, null, 2);
    
    navigator.clipboard.writeText(details).then(
      () => console.log('Error details copied to clipboard'),
      (err) => console.error('Failed to copy error details:', err)
    );
  }

  /**
   * Format timestamp for display
   * @param timestamp Timestamp in milliseconds
   * @returns Formatted time string
   */
  formatTime(timestamp: number): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  }
}