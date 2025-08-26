import { Component, OnInit } from '@angular/core';
import { OrchestrationService } from '../../services/orchestration.service';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'idle' | 'working' | 'error';
  lastTask: string;
  tasksCompleted: number;
  successRate: number;
}

interface Workflow {
  id: string;
  name: string;
  agents: string[];
  status: 'running' | 'completed' | 'failed';
  progress: number;
}

@Component({
  selector: 'app-orchestration',
  templateUrl: './orchestration.component.html',
  styleUrls: ['./orchestration.component.scss']
})
export class OrchestrationComponent implements OnInit {
  agents: Agent[] = [
    {
      id: '1',
      name: 'Dr. Sarah Chen',
      type: 'AI Integration',
      status: 'working',
      lastTask: 'Optimizing Claude API prompts',
      tasksCompleted: 342,
      successRate: 98.5
    },
    {
      id: '2',
      name: 'Marcus Rodriguez',
      type: 'Systems Performance',
      status: 'idle',
      lastTask: 'Cache optimization completed',
      tasksCompleted: 278,
      successRate: 99.2
    },
    {
      id: '3',
      name: 'Emily Watson',
      type: 'UX/Frontend',
      status: 'working',
      lastTask: 'Designing terminal interface',
      tasksCompleted: 195,
      successRate: 97.8
    }
  ];

  workflows: Workflow[] = [
    {
      id: '1',
      name: 'Full Stack Feature Development',
      agents: ['1', '2', '3'],
      status: 'running',
      progress: 67
    },
    {
      id: '2',
      name: 'Performance Optimization',
      agents: ['2'],
      status: 'completed',
      progress: 100
    }
  ];

  constructor(private orchestrationService: OrchestrationService) {}

  ngOnInit(): void {
    this.loadOrchestrationData();
  }

  loadOrchestrationData(): void {
    // Load from service
  }

  startWorkflow(): void {
    console.log('Starting new workflow');
  }

  getAgentStatusColor(status: string): string {
    switch(status) {
      case 'working': return 'primary';
      case 'idle': return 'accent';
      case 'error': return 'warn';
      default: return '';
    }
  }
}