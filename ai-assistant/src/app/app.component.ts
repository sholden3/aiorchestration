import { Component, OnInit, OnDestroy } from '@angular/core';
import { OrchestrationService, OrchestrationStatus } from './services/orchestration.service';
import { TerminalManagerService } from './services/terminal-manager.service';
import { TerminalService } from './services/terminal.service';
import { Subscription, interval } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, OnDestroy {
  systemStatus: OrchestrationStatus | null = null;
  private statusSubscription?: Subscription;
  private refreshSubscription?: Subscription;

  constructor(
    private orchestrationService: OrchestrationService,
    private terminalManager: TerminalManagerService
  ) {}

  ngOnInit(): void {
    this.loadSystemStatus();
    this.refreshSubscription = interval(5000).subscribe(() => this.loadSystemStatus());
    
    // FIX C1: Initialize 3AM debugging utilities
    TerminalService.attachGlobalDebugHook(this.terminalManager);
    console.log('🔧 Terminal service debugging enabled - Use window.getTerminalDebugInfo() in DevTools');
  }

  ngOnDestroy(): void {
    this.statusSubscription?.unsubscribe();
    this.refreshSubscription?.unsubscribe();
    
    // FIX C1: Emergency cleanup on app shutdown
    // Ensures all terminal service instances are properly cleaned up
    console.log('App shutdown - cleaning up terminal services');
    this.terminalManager.cleanup();
  }

  private loadSystemStatus(): void {
    this.statusSubscription = this.orchestrationService.getStatus().subscribe({
      next: (status) => this.systemStatus = status,
      error: (error) => console.error('Failed to load status:', error)
    });
  }
}