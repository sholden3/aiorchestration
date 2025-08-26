import { Component, Input, Output, EventEmitter } from '@angular/core';
import { OrchestrationStatus } from '../../services/orchestration.service';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html',
  styleUrls: ['./toolbar.component.scss']
})
export class ToolbarComponent {
  @Input() systemStatus: OrchestrationStatus | null = null;
  @Output() toggleDrawer = new EventEmitter<void>();

  onToggleDrawer(): void {
    this.toggleDrawer.emit();
  }
}