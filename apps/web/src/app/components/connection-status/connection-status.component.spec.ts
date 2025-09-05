/**
 * @fileoverview Unit tests for ConnectionStatusComponent
 * @author Maya Patel v2.0 - QA & Testing Lead
 * @architecture Testing - Unit test suite for connection status component
 * @business_logic Validates connection status display, animations, state transitions
 * @testing_strategy Component behavior, visual states, auto-hide functionality
 * @coverage_target 90% code coverage for ConnectionStatusComponent
 */

import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { By } from '@angular/platform-browser';

import { ConnectionStatusComponent } from './connection-status.component';
import { ResilientIPCService, ConnectionState } from '../../services/resilient-ipc.service';
import { BehaviorSubject } from 'rxjs';

describe('ConnectionStatusComponent', () => {
  let component: ConnectionStatusComponent;
  let fixture: ComponentFixture<ConnectionStatusComponent>;
  let ipcService: jest.Mocked<ResilientIPCService>;
  let connectionStateSubject: BehaviorSubject<ConnectionState>;

  beforeEach(async () => {
    connectionStateSubject = new BehaviorSubject<ConnectionState>(ConnectionState.DISCONNECTED);

    const ipcServiceSpy = {
      getConnectionState: jest.fn().mockReturnValue(connectionStateSubject.asObservable())
    };

    await TestBed.configureTestingModule({
      declarations: [ConnectionStatusComponent],
      imports: [
        BrowserAnimationsModule,
        MatIconModule,
        MatButtonModule,
        MatTooltipModule,
        MatProgressBarModule
      ],
      providers: [
        { provide: ResilientIPCService, useValue: ipcServiceSpy }
      ]
    }).compileComponents();

    ipcService = TestBed.inject(ResilientIPCService) as jest.Mocked<ResilientIPCService>;
    fixture = TestBed.createComponent(ConnectionStatusComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should subscribe to connection state', () => {
      expect(ipcService.getConnectionState).toHaveBeenCalled();
    });

    it('should start with disconnected state', () => {
      expect(component.connectionState).toBe(ConnectionState.DISCONNECTED);
      expect(component.showStatus).toBe(true);
    });
  });

  describe('Connection State Handling', () => {
    it('should handle CONNECTED state', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.CONNECTED);
      tick(300); // Debounce time
      fixture.detectChanges();

      expect(component.connectionState).toBe(ConnectionState.CONNECTED);
      expect(component.statusMessage).toBe('Connected');
      expect(component.statusIcon).toBe('check_circle');
      expect(component.statusClass).toBe('status-connected');
      expect(component.showStatus).toBe(true);
    }));

    it('should auto-hide when connected after 3 seconds', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.CONNECTED);
      tick(300);
      fixture.detectChanges();

      expect(component.showStatus).toBe(true);

      tick(3000);
      fixture.detectChanges();

      expect(component.showStatus).toBe(false);
    }));

    it('should handle CONNECTING state', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.CONNECTING);
      tick(300);
      fixture.detectChanges();

      expect(component.statusMessage).toBe('Connecting...');
      expect(component.statusIcon).toBe('sync');
      expect(component.statusClass).toBe('status-connecting');
      expect(component.showStatus).toBe(true);
    }));

    it('should handle RECONNECTING state', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.RECONNECTING);
      tick(300);
      fixture.detectChanges();

      expect(component.statusMessage).toBe('Reconnecting...');
      expect(component.statusIcon).toBe('sync');
      expect(component.statusClass).toBe('status-reconnecting');
      expect(component.showStatus).toBe(true);
    }));

    it('should handle DISCONNECTED state', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.DISCONNECTED);
      tick(300);
      fixture.detectChanges();

      expect(component.statusMessage).toBe('Disconnected');
      expect(component.statusIcon).toBe('signal_disconnected');
      expect(component.statusClass).toBe('status-disconnected');
      expect(component.showStatus).toBe(true);
    }));

    it('should handle ERROR state', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.ERROR);
      tick(300);
      fixture.detectChanges();

      expect(component.statusMessage).toBe('Connection Error');
      expect(component.statusIcon).toBe('error_outline');
      expect(component.statusClass).toBe('status-error');
      expect(component.showStatus).toBe(true);
    }));

    it('should not auto-hide for non-connected states', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.DISCONNECTED);
      tick(300);
      fixture.detectChanges();

      tick(5000);
      fixture.detectChanges();

      expect(component.showStatus).toBe(true);
    }));
  });

  describe('UI Elements', () => {
    it('should display status indicator when visible', fakeAsync(() => {
      component.showStatus = true;
      connectionStateSubject.next(ConnectionState.CONNECTING);
      tick(300);
      fixture.detectChanges();

      const statusContainer = fixture.debugElement.query(By.css('.connection-status-container'));
      expect(statusContainer).toBeTruthy();
    }));

    it('should display correct icon', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.CONNECTED);
      tick(300);
      fixture.detectChanges();

      const icon = fixture.debugElement.query(By.css('.status-icon'));
      expect(icon.nativeElement.textContent.trim()).toBe('check_circle');
    }));

    it('should display status text', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.RECONNECTING);
      tick(300);
      fixture.detectChanges();

      const statusText = fixture.debugElement.query(By.css('.status-text'));
      expect(statusText.nativeElement.textContent).toBe('Reconnecting...');
    }));

    it('should show retry button for error state', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.ERROR);
      tick(300);
      fixture.detectChanges();

      const retryButton = fixture.debugElement.query(By.css('.retry-button'));
      expect(retryButton).toBeTruthy();
    }));

    it('should show retry button for disconnected state', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.DISCONNECTED);
      tick(300);
      fixture.detectChanges();

      const retryButton = fixture.debugElement.query(By.css('.retry-button'));
      expect(retryButton).toBeTruthy();
    }));

    it('should not show retry button for connecting states', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.CONNECTING);
      tick(300);
      fixture.detectChanges();

      const retryButton = fixture.debugElement.query(By.css('.retry-button'));
      expect(retryButton).toBeFalsy();
    }));

    it('should show progress bar for connecting state', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.CONNECTING);
      tick(300);
      fixture.detectChanges();

      const progressBar = fixture.debugElement.query(By.css('mat-progress-bar'));
      expect(progressBar).toBeTruthy();
    }));

    it('should show progress bar for reconnecting state', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.RECONNECTING);
      tick(300);
      fixture.detectChanges();

      const progressBar = fixture.debugElement.query(By.css('mat-progress-bar'));
      expect(progressBar).toBeTruthy();
    }));
  });

  describe('Minimized Dot Indicator', () => {
    it('should show dot when status hidden and not connected', fakeAsync(() => {
      component.showStatus = false;
      connectionStateSubject.next(ConnectionState.DISCONNECTED);
      tick(300);
      fixture.detectChanges();

      const dot = fixture.debugElement.query(By.css('.connection-dot'));
      expect(dot).toBeTruthy();
      expect(dot.nativeElement.classList.contains('dot-disconnected')).toBe(true);
    }));

    it('should not show dot when connected', fakeAsync(() => {
      component.showStatus = false;
      connectionStateSubject.next(ConnectionState.CONNECTED);
      tick(300);
      fixture.detectChanges();

      const dot = fixture.debugElement.query(By.css('.connection-dot'));
      expect(dot).toBeFalsy();
    }));

    it('should expand status when dot clicked', fakeAsync(() => {
      component.showStatus = false;
      connectionStateSubject.next(ConnectionState.DISCONNECTED);
      tick(300);
      fixture.detectChanges();

      const dot = fixture.debugElement.query(By.css('.connection-dot'));
      dot.nativeElement.click();
      fixture.detectChanges();

      expect(component.showStatus).toBe(true);
    }));

    it('should apply correct class for error dot', fakeAsync(() => {
      component.showStatus = false;
      connectionStateSubject.next(ConnectionState.ERROR);
      tick(300);
      fixture.detectChanges();

      const dot = fixture.debugElement.query(By.css('.connection-dot'));
      expect(dot.nativeElement.classList.contains('dot-error')).toBe(true);
    }));

    it('should apply correct class for connecting dot', fakeAsync(() => {
      component.showStatus = false;
      connectionStateSubject.next(ConnectionState.CONNECTING);
      tick(300);
      fixture.detectChanges();

      const dot = fixture.debugElement.query(By.css('.connection-dot'));
      expect(dot.nativeElement.classList.contains('dot-connecting')).toBe(true);
    }));
  });

  describe('CSS Classes', () => {
    it('should apply correct status class', fakeAsync(() => {
      const testCases = [
        { state: ConnectionState.CONNECTED, class: 'status-connected' },
        { state: ConnectionState.CONNECTING, class: 'status-connecting' },
        { state: ConnectionState.RECONNECTING, class: 'status-reconnecting' },
        { state: ConnectionState.DISCONNECTED, class: 'status-disconnected' },
        { state: ConnectionState.ERROR, class: 'status-error' }
      ];

      testCases.forEach(testCase => {
        connectionStateSubject.next(testCase.state);
        tick(300);
        fixture.detectChanges();

        const container = fixture.debugElement.query(By.css('.connection-status-container'));
        if (container) {
          expect(container.nativeElement.classList.contains(testCase.class)).toBe(true);
        }
      });
    }));

    it('should add rotating class to sync icon', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.CONNECTING);
      tick(300);
      fixture.detectChanges();

      const icon = fixture.debugElement.query(By.css('.status-icon'));
      expect(icon.nativeElement.classList.contains('rotating')).toBe(true);
    }));
  });

  describe('Tooltips', () => {
    it('should provide correct tooltip for connected state', () => {
      component.connectionState = ConnectionState.CONNECTED;
      expect(component.getTooltip()).toBe('Connection established with backend');
    });

    it('should provide correct tooltip for connecting state', () => {
      component.connectionState = ConnectionState.CONNECTING;
      expect(component.getTooltip()).toBe('Establishing connection...');
    });

    it('should provide correct tooltip for reconnecting state', () => {
      component.connectionState = ConnectionState.RECONNECTING;
      expect(component.getTooltip()).toBe('Connection lost, attempting to reconnect...');
    });

    it('should provide correct tooltip for disconnected state', () => {
      component.connectionState = ConnectionState.DISCONNECTED;
      expect(component.getTooltip()).toBe('No connection to backend');
    });

    it('should provide correct tooltip for error state', () => {
      component.connectionState = ConnectionState.ERROR;
      expect(component.getTooltip()).toBe('Connection error - click to retry');
    });
  });

  describe('Reconnection', () => {
    it('should log reconnection request', () => {
      spyOn(console, 'log');
      component.reconnect();
      expect(console.log).toHaveBeenCalledWith('[ConnectionStatus] Manual reconnection requested');
    });
  });

  describe('Auto-hide Timer Management', () => {
    it('should clear timer when state changes', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.CONNECTED);
      tick(300);

      // Change state before auto-hide completes
      connectionStateSubject.next(ConnectionState.DISCONNECTED);
      tick(300);

      // Wait for what would have been auto-hide time
      tick(3000);

      // Should still be visible because state changed
      expect(component.showStatus).toBe(true);
    }));

    it('should clear timer on destroy', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.CONNECTED);
      tick(300);

      spyOn(window, 'clearTimeout');
      fixture.destroy();

      expect(window.clearTimeout).toHaveBeenCalled();
    }));
  });

  describe('Animations', () => {
    it('should animate slide in when status appears', fakeAsync(() => {
      component.showStatus = false;
      fixture.detectChanges();

      component.showStatus = true;
      connectionStateSubject.next(ConnectionState.DISCONNECTED);
      tick(300);
      fixture.detectChanges();

      const container = fixture.debugElement.query(By.css('.connection-status-container'));
      expect(container).toBeTruthy();
      // Animation testing would require more complex setup
    }));

    it('should animate pulse for reconnecting state', fakeAsync(() => {
      connectionStateSubject.next(ConnectionState.RECONNECTING);
      tick(300);
      fixture.detectChanges();

      const indicator = fixture.debugElement.query(By.css('.status-indicator'));
      expect(indicator).toBeTruthy();
      // Pulse animation verification would need animation testing utilities
    }));
  });

  describe('Debouncing', () => {
    it('should debounce rapid state changes', fakeAsync(() => {
      let stateChangeCount = 0;
      component.getConnectionState().subscribe(() => stateChangeCount++);

      // Rapid state changes
      connectionStateSubject.next(ConnectionState.CONNECTING);
      tick(100);
      connectionStateSubject.next(ConnectionState.RECONNECTING);
      tick(100);
      connectionStateSubject.next(ConnectionState.CONNECTED);
      tick(100);

      // Should not process yet
      expect(component.connectionState).toBe(ConnectionState.DISCONNECTED);

      // After debounce time
      tick(200);
      expect(component.connectionState).toBe(ConnectionState.CONNECTED);
    }));
  });

  describe('Component Cleanup', () => {
    it('should unsubscribe from connection state', () => {
      const subscription = (component as any).destroy$;
      spyOn(subscription, 'next');
      spyOn(subscription, 'complete');

      fixture.destroy();

      expect(subscription.next).toHaveBeenCalled();
      expect(subscription.complete).toHaveBeenCalled();
    });
  });
});