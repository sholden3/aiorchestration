/**
 * @fileoverview Connection status indicator component
 * @author Alex Novak v2.0 - Frontend Integration Architect
 * @architecture Frontend - Connection status display component
 * @business_logic Displays real-time connection status with visual indicators
 * @integration_points ResilientIPCService, WebSocket status monitoring
 * @error_handling Connection state changes, reconnection progress
 * @performance Debounced status updates, minimal re-renders
 */

import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil, distinctUntilChanged, debounceTime } from 'rxjs/operators';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { ResilientIPCService, ConnectionState } from '../../services/resilient-ipc.service';

/**
 * @class ConnectionStatusComponent
 * @description Displays connection status with visual indicators
 * 
 * This component provides:
 * - Real-time connection status display
 * - Visual indicators for different states
 * - Reconnection progress indication
 * - Minimal, unobtrusive UI
 */
@Component({
  selector: 'app-connection-status',
  templateUrl: './connection-status.component.html',
  styleUrls: ['./connection-status.component.scss'],
  animations: [
    trigger('pulse', [
      state('reconnecting', style({ opacity: 1 })),
      transition('* => reconnecting', [
        animate('1s ease-in-out', style({ opacity: 0.3 })),
        animate('1s ease-in-out', style({ opacity: 1 }))
      ])
    ]),
    trigger('slideIn', [
      transition(':enter', [
        style({ transform: 'translateX(100%)', opacity: 0 }),
        animate('300ms ease-out', style({ transform: 'translateX(0)', opacity: 1 }))
      ]),
      transition(':leave', [
        animate('300ms ease-in', style({ transform: 'translateX(100%)', opacity: 0 }))
      ])
    ])
  ]
})
export class ConnectionStatusComponent implements OnInit, OnDestroy {
  /**
   * Current connection state
   */
  connectionState: ConnectionState = ConnectionState.DISCONNECTED;
  
  /**
   * Whether to show the status indicator
   */
  showStatus = false;
  
  /**
   * Status message to display
   */
  statusMessage = '';
  
  /**
   * Status icon to display
   */
  statusIcon = '';
  
  /**
   * CSS class for status styling
   */
  statusClass = '';
  
  /**
   * Auto-hide timer
   */
  private hideTimer: any;
  
  /**
   * Component destruction subject
   */
  private destroy$ = new Subject<void>();
  
  /**
   * Connection state enum for template
   */
  ConnectionState = ConnectionState;

  constructor(private ipcService: ResilientIPCService) {}

  /**
   * Component initialization
   */
  ngOnInit(): void {
    // Subscribe to connection state changes
    this.ipcService.getConnectionState()
      .pipe(
        takeUntil(this.destroy$),
        distinctUntilChanged(),
        debounceTime(300) // Debounce rapid state changes
      )
      .subscribe(state => {
        this.handleConnectionStateChange(state);
      });
  }

  /**
   * Component destruction
   */
  ngOnDestroy(): void {
    this.clearHideTimer();
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Handle connection state changes
   * @param state New connection state
   * @private
   */
  private handleConnectionStateChange(state: ConnectionState): void {
    this.connectionState = state;
    this.clearHideTimer();
    
    switch (state) {
      case ConnectionState.CONNECTED:
        this.statusMessage = 'Connected';
        this.statusIcon = 'check_circle';
        this.statusClass = 'status-connected';
        this.showStatus = true;
        // Auto-hide after 3 seconds when connected
        this.hideTimer = setTimeout(() => {
          this.showStatus = false;
        }, 3000);
        break;
        
      case ConnectionState.CONNECTING:
        this.statusMessage = 'Connecting...';
        this.statusIcon = 'sync';
        this.statusClass = 'status-connecting';
        this.showStatus = true;
        break;
        
      case ConnectionState.RECONNECTING:
        this.statusMessage = 'Reconnecting...';
        this.statusIcon = 'sync';
        this.statusClass = 'status-reconnecting';
        this.showStatus = true;
        break;
        
      case ConnectionState.DISCONNECTED:
        this.statusMessage = 'Disconnected';
        this.statusIcon = 'signal_disconnected';
        this.statusClass = 'status-disconnected';
        this.showStatus = true;
        break;
        
      case ConnectionState.ERROR:
        this.statusMessage = 'Connection Error';
        this.statusIcon = 'error_outline';
        this.statusClass = 'status-error';
        this.showStatus = true;
        break;
        
      default:
        this.showStatus = false;
    }
  }

  /**
   * Clear auto-hide timer
   * @private
   */
  private clearHideTimer(): void {
    if (this.hideTimer) {
      clearTimeout(this.hideTimer);
      this.hideTimer = null;
    }
  }

  /**
   * Manually trigger reconnection attempt
   */
  reconnect(): void {
    console.log('[ConnectionStatus] Manual reconnection requested');
    // The IPC service will handle reconnection automatically
    // This is just for user-initiated reconnection if needed
  }

  /**
   * Get tooltip text for current status
   * @returns Tooltip text
   */
  getTooltip(): string {
    switch (this.connectionState) {
      case ConnectionState.CONNECTED:
        return 'Connection established with backend';
      case ConnectionState.CONNECTING:
        return 'Establishing connection...';
      case ConnectionState.RECONNECTING:
        return 'Connection lost, attempting to reconnect...';
      case ConnectionState.DISCONNECTED:
        return 'No connection to backend';
      case ConnectionState.ERROR:
        return 'Connection error - click to retry';
      default:
        return '';
    }
  }
}