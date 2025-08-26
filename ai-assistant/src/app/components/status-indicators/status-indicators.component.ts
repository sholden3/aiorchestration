import { Component, Input } from '@angular/core';
import { OrchestrationStatus } from '../../services/orchestration.service';

@Component({
  selector: 'app-status-indicators',
  templateUrl: './status-indicators.component.html',
  styleUrls: ['./status-indicators.component.scss']
})
export class StatusIndicatorsComponent {
  @Input() systemStatus: OrchestrationStatus | null = null;

  getSystemTooltip(): string {
    if (!this.systemStatus) {
      return 'System status unknown';
    }
    if (this.systemStatus.is_running) {
      return `System running - ${this.systemStatus.tasks?.active || 0} active tasks`;
    }
    return 'System is stopped';
  }
}