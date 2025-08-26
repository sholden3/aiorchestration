import { Component, OnInit, OnDestroy } from '@angular/core';
import { OrchestrationService, OrchestrationStatus } from './services/orchestration.service';
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

  constructor(private orchestrationService: OrchestrationService) {}

  ngOnInit(): void {
    this.loadSystemStatus();
    this.refreshSubscription = interval(5000).subscribe(() => this.loadSystemStatus());
  }

  ngOnDestroy(): void {
    this.statusSubscription?.unsubscribe();
    this.refreshSubscription?.unsubscribe();
  }

  private loadSystemStatus(): void {
    this.statusSubscription = this.orchestrationService.getStatus().subscribe({
      next: (status) => this.systemStatus = status,
      error: (error) => console.error('Failed to load status:', error)
    });
  }
}