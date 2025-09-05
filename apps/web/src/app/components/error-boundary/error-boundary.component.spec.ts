/**
 * @fileoverview Unit tests for ErrorBoundaryComponent
 * @author Maya Patel v2.0 - QA & Testing Lead
 * @architecture Testing - Unit test suite for error boundary component
 * @business_logic Validates error display, animations, user actions
 * @testing_strategy Component behavior, template rendering, user interactions
 * @coverage_target 90% code coverage for ErrorBoundaryComponent
 */

import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { ErrorBoundaryComponent } from './error-boundary.component';
import { ErrorBoundaryService, ErrorInfo, ErrorSeverity, ErrorCategory } from '../../services/error-boundary.service';
import { BehaviorSubject } from 'rxjs';

describe('ErrorBoundaryComponent', () => {
  let component: ErrorBoundaryComponent;
  let fixture: ComponentFixture<ErrorBoundaryComponent>;
  let errorService: jest.Mocked<ErrorBoundaryService>;
  let currentErrorSubject: BehaviorSubject<ErrorInfo | null>;

  const mockError: ErrorInfo = {
    id: 'err_123',
    timestamp: Date.now(),
    severity: ErrorSeverity.ERROR,
    category: ErrorCategory.NETWORK,
    message: 'Network connection failed',
    details: { code: 'NET_ERR' },
    stack: 'Error stack trace',
    component: 'TestComponent',
    recoverable: true,
    retryable: true,
    userActions: [
      {
        label: 'Retry',
        action: jest.fn(),
        icon: 'refresh',
        primary: true
      },
      {
        label: 'Dismiss',
        action: jest.fn(),
        icon: 'close'
      }
    ]
  };

  beforeEach(async () => {
    currentErrorSubject = new BehaviorSubject<ErrorInfo | null>(null);

    const errorServiceSpy = {
      getCurrentError: jest.fn().mockReturnValue(currentErrorSubject.asObservable()),
      clearError: jest.fn()
    };

    await TestBed.configureTestingModule({
      declarations: [ErrorBoundaryComponent],
      imports: [
        BrowserAnimationsModule,
        MatCardModule,
        MatIconModule,
        MatButtonModule,
        MatChipsModule,
        MatProgressBarModule,
        MatProgressSpinnerModule,
        MatTooltipModule
      ],
      providers: [
        { provide: ErrorBoundaryService, useValue: errorServiceSpy }
      ]
    }).compileComponents();

    errorService = TestBed.inject(ErrorBoundaryService) as jest.Mocked<ErrorBoundaryService>;
    fixture = TestBed.createComponent(ErrorBoundaryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should subscribe to error service', () => {
      expect(errorService.getCurrentError).toHaveBeenCalled();
    });

    it('should start with no error displayed', () => {
      expect(component.currentError).toBeNull();
      expect(component.detailsExpanded).toBe(false);
      expect(component.processingAction).toBe(false);
    });
  });

  describe('Error Display', () => {
    it('should display error when service emits', fakeAsync(() => {
      currentErrorSubject.next(mockError);
      tick();
      fixture.detectChanges();

      expect(component.currentError).toEqual(mockError);
      
      const errorCard = fixture.debugElement.query(By.css('.error-card'));
      expect(errorCard).toBeTruthy();
    }));

    it('should show correct severity icon', fakeAsync(() => {
      currentErrorSubject.next(mockError);
      tick();
      fixture.detectChanges();

      const icon = fixture.debugElement.query(By.css('mat-icon'));
      expect(icon.nativeElement.textContent.trim()).toBe('warning');
    }));

    it('should display error message', fakeAsync(() => {
      currentErrorSubject.next(mockError);
      tick();
      fixture.detectChanges();

      const message = fixture.debugElement.query(By.css('.error-message'));
      expect(message.nativeElement.textContent).toContain('Network connection failed');
    }));

    it('should show recovery status chips', fakeAsync(() => {
      currentErrorSubject.next(mockError);
      tick();
      fixture.detectChanges();

      const chips = fixture.debugElement.queryAll(By.css('mat-chip'));
      expect(chips.length).toBeGreaterThan(0);
      
      const recoverableChip = chips.find(chip => 
        chip.nativeElement.textContent.includes('Recoverable')
      );
      expect(recoverableChip).toBeTruthy();
    }));

    it('should apply correct CSS class for severity', fakeAsync(() => {
      const criticalError = { ...mockError, severity: ErrorSeverity.CRITICAL };
      currentErrorSubject.next(criticalError);
      tick();
      fixture.detectChanges();

      const errorCard = fixture.debugElement.query(By.css('.error-card'));
      expect(errorCard.nativeElement.classList.contains('error-critical')).toBe(true);
    }));
  });

  describe('User Actions', () => {
    beforeEach(fakeAsync(() => {
      currentErrorSubject.next(mockError);
      tick();
      fixture.detectChanges();
    }));

    it('should display action buttons', () => {
      const buttons = fixture.debugElement.queryAll(By.css('mat-card-actions button'));
      expect(buttons.length).toBe(2);
      expect(buttons[0].nativeElement.textContent).toContain('Retry');
      expect(buttons[1].nativeElement.textContent).toContain('Dismiss');
    });

    it('should execute action when clicked', fakeAsync(() => {
      const retryButton = fixture.debugElement.query(By.css('button[color="primary"]'));
      retryButton.nativeElement.click();
      tick();

      expect(mockError.userActions![0].action).toHaveBeenCalled();
    }));

    it('should show processing state during action', fakeAsync(() => {
      const action = mockError.userActions![0];
      (action.action as jest.Mock).mockReturnValue(
        new Promise(resolve => setTimeout(resolve, 100))
      );

      component.executeAction(action);
      fixture.detectChanges();

      expect(component.processingAction).toBe(true);
      
      const spinner = fixture.debugElement.query(By.css('mat-spinner'));
      expect(spinner).toBeTruthy();

      tick(100);
      expect(component.processingAction).toBe(false);
    }));

    it('should handle action errors gracefully', async () => {
      const action = mockError.userActions![0];
      (action.action as jest.Mock).mockImplementation(() => { throw new Error('Action failed'); });

      await component.executeAction(action);
      
      expect(component.processingAction).toBe(false);
    });
  });

  describe('Error Details', () => {
    beforeEach(fakeAsync(() => {
      currentErrorSubject.next(mockError);
      tick();
      fixture.detectChanges();
    }));

    it('should toggle details expansion', () => {
      expect(component.detailsExpanded).toBe(false);

      component.toggleDetails();
      expect(component.detailsExpanded).toBe(true);

      component.toggleDetails();
      expect(component.detailsExpanded).toBe(false);
    });

    it('should show details button when details available', () => {
      const detailsButton = fixture.debugElement.query(
        By.css('.error-details-toggle button')
      );
      expect(detailsButton).toBeTruthy();
      expect(detailsButton.nativeElement.textContent).toContain('Show Details');
    });

    it('should display error ID in details', () => {
      component.detailsExpanded = true;
      fixture.detectChanges();

      const errorId = fixture.debugElement.query(
        By.css('.error-details .detail-item')
      );
      expect(errorId.nativeElement.textContent).toContain('err_123');
    });

    it('should display stack trace when expanded', () => {
      component.detailsExpanded = true;
      fixture.detectChanges();

      const stackTrace = fixture.debugElement.query(By.css('.stack-trace'));
      expect(stackTrace.nativeElement.textContent).toContain('Error stack trace');
    });

    it('should copy error details to clipboard', () => {
      const clipboardSpy = {
        writeText: jest.fn().mockResolvedValue(undefined)
      };
      Object.defineProperty(navigator, 'clipboard', {
        value: clipboardSpy,
        configurable: true
      });

      component.copyErrorDetails();

      expect(clipboardSpy.writeText).toHaveBeenCalledWith(
        expect.stringContaining('err_123')
      );
    });
  });

  describe('Dismiss Functionality', () => {
    beforeEach(fakeAsync(() => {
      currentErrorSubject.next(mockError);
      tick();
      fixture.detectChanges();
    }));

    it('should dismiss error when dismiss called', () => {
      component.dismiss();

      expect(errorService.clearError).toHaveBeenCalled();
      expect(component.currentError).toBeNull();
    });

    it('should disable close button for critical errors', fakeAsync(() => {
      const criticalError = { ...mockError, severity: ErrorSeverity.CRITICAL };
      currentErrorSubject.next(criticalError);
      tick();
      fixture.detectChanges();

      const closeButton = fixture.debugElement.query(By.css('.close-button'));
      expect(closeButton.nativeElement.disabled).toBe(true);
    }));

    it('should enable close button for non-critical errors', () => {
      const closeButton = fixture.debugElement.query(By.css('.close-button'));
      expect(closeButton.nativeElement.disabled).toBe(false);
    });
  });

  describe('Auto-Dismiss', () => {
    it('should auto-dismiss warnings after 5 seconds', fakeAsync(() => {
      const warningError = { ...mockError, severity: ErrorSeverity.WARNING };
      currentErrorSubject.next(warningError);
      tick();
      fixture.detectChanges();

      expect(component.currentError).toBeTruthy();

      tick(5000);

      expect(errorService.clearError).toHaveBeenCalled();
      expect(component.currentError).toBeNull();
    }));

    it('should auto-dismiss info messages after 5 seconds', fakeAsync(() => {
      const infoError = { ...mockError, severity: ErrorSeverity.INFO };
      currentErrorSubject.next(infoError);
      tick();
      fixture.detectChanges();

      tick(5000);

      expect(errorService.clearError).toHaveBeenCalled();
    }));

    it('should not auto-dismiss errors', fakeAsync(() => {
      currentErrorSubject.next(mockError);
      tick();
      fixture.detectChanges();

      tick(5000);

      expect(errorService.clearError).not.toHaveBeenCalled();
      expect(component.currentError).toBeTruthy();
    }));

    it('should not auto-dismiss critical errors', fakeAsync(() => {
      const criticalError = { ...mockError, severity: ErrorSeverity.CRITICAL };
      currentErrorSubject.next(criticalError);
      tick();
      fixture.detectChanges();

      tick(5000);

      expect(errorService.clearError).not.toHaveBeenCalled();
    }));

    it('should clear timer when new error arrives', fakeAsync(() => {
      const warningError = { ...mockError, severity: ErrorSeverity.WARNING };
      currentErrorSubject.next(warningError);
      tick(2000);

      // New error arrives before auto-dismiss
      currentErrorSubject.next(mockError);
      tick(4000);

      // Original warning would have been dismissed by now, but was replaced
      expect(component.currentError).toEqual(mockError);
    }));
  });

  describe('Severity Helpers', () => {
    it('should return correct icon for severity', () => {
      expect(component.getSeverityIcon(ErrorSeverity.CRITICAL)).toBe('error');
      expect(component.getSeverityIcon(ErrorSeverity.ERROR)).toBe('warning');
      expect(component.getSeverityIcon(ErrorSeverity.WARNING)).toBe('info');
      expect(component.getSeverityIcon(ErrorSeverity.INFO)).toBe('info_outline');
    });

    it('should return correct CSS class for severity', () => {
      expect(component.getSeverityClass(ErrorSeverity.CRITICAL)).toBe('error-critical');
      expect(component.getSeverityClass(ErrorSeverity.ERROR)).toBe('error-error');
      expect(component.getSeverityClass(ErrorSeverity.WARNING)).toBe('error-warning');
      expect(component.getSeverityClass(ErrorSeverity.INFO)).toBe('error-info');
    });
  });

  describe('Time Formatting', () => {
    it('should format timestamp correctly', () => {
      const timestamp = new Date('2024-01-01T12:30:45').getTime();
      const formatted = component.formatTime(timestamp);
      
      expect(formatted).toContain(':30:');
    });
  });

  describe('Animations', () => {
    it('should animate slide in when error appears', fakeAsync(() => {
      currentErrorSubject.next(mockError);
      tick();
      fixture.detectChanges();

      const container = fixture.debugElement.query(By.css('.error-boundary-container'));
      expect(container).toBeTruthy();
      // Animation testing would require more complex setup
    }));

    it('should animate expand when details toggled', fakeAsync(() => {
      currentErrorSubject.next(mockError);
      tick();
      fixture.detectChanges();

      component.toggleDetails();
      fixture.detectChanges();
      tick(200); // Animation duration

      const details = fixture.debugElement.query(By.css('.error-details'));
      expect(details).toBeTruthy();
    }));
  });

  describe('Component Cleanup', () => {
    it('should clear timer on destroy', fakeAsync(() => {
      const warningError = { ...mockError, severity: ErrorSeverity.WARNING };
      currentErrorSubject.next(warningError);
      tick();

      spyOn(window, 'clearTimeout');
      fixture.destroy();

      expect(window.clearTimeout).toHaveBeenCalled();
    }));

    it('should unsubscribe from error service', () => {
      const subscription = (component as any).destroy$;
      spyOn(subscription, 'next');
      spyOn(subscription, 'complete');

      fixture.destroy();

      expect(subscription.next).toHaveBeenCalled();
      expect(subscription.complete).toHaveBeenCalled();
    });
  });
});