import { Component, OnInit, OnDestroy } from '@angular/core';
import { RulesService, Rule, BestPractice, Template, Statistics } from '../../services/rules.service';
import { OrchestrationService, OrchestrationStatus } from '../../services/orchestration.service';
import { WebSocketService } from '../../services/websocket.service';
import { interval, Subscription } from 'rxjs';
import { switchMap } from 'rxjs/operators';

export interface Project {
  name: string;
  percentage: number;
  status: string;
  phase: string;
}

export interface Update {
  icon: string;
  title: string;
  description: string;
  time: string;
  color: string;
}

// BUSINESS LOGIC: Dashboard displays real-time data from backend
// ASSUMPTION: Backend APIs are running and accessible
// VALIDATION: Handle loading states and errors gracefully

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  currentPage = 'Dashboard';
  
  // Projects data
  projects: Project[] = [
    { name: 'Customer Support AI', percentage: 78, status: 'Implementation Phase - Testing in progress', phase: 'implementation' },
    { name: 'Data Processing Pipeline', percentage: 45, status: 'Development Phase - API integration', phase: 'development' },
    { name: 'Predictive Analytics Model', percentage: 92, status: 'Deployment Phase - Final validation', phase: 'deployment' },
    { name: 'Voice Recognition System', percentage: 23, status: 'Planning Phase - Requirements gathering', phase: 'planning' }
  ];
  
  // Updates
  updates: Update[] = [
    { 
      icon: 'system_update', 
      title: 'Version 2.4.1 Available', 
      description: 'New AI model integration and improved performance monitoring capabilities.',
      time: '2 hours ago',
      color: '#4ecdc4'
    },
    { 
      icon: 'new_releases', 
      title: 'Enhanced Templates Released', 
      description: '10 new project templates for common AI orchestration patterns now available.',
      time: '1 day ago',
      color: '#667eea'
    },
    { 
      icon: 'security', 
      title: 'Security Patch Applied', 
      description: 'Enhanced governance controls and audit logging improvements.',
      time: '3 days ago',
      color: '#764ba2'
    }
  ];
  
  // Data properties
  rules: Rule[] = [];
  bestPractices: BestPractice[] = [];
  templates: Template[] = [];
  
  // Statistics
  rulesStats: Statistics | null = null;
  practicesStats: Statistics | null = null;
  templatesStats: Statistics | null = null;
  
  // UI state
  loading = {
    rules: false,
    practices: false,
    templates: false
  };
  
  errors = {
    rules: '',
    practices: '',
    templates: ''
  };
  
  // Filter state
  selectedCategory = '';
  categories: string[] = [];
  
  // Orchestration status
  orchestrationStatus: OrchestrationStatus | null = null;
  healthStatus: any = null;
  cacheMetrics: any = null;
  performanceMetrics: any = null;
  
  // Subscriptions
  private statusPolling?: Subscription;
  private metricsPolling?: Subscription;
  private wsOrchestration?: Subscription;
  private wsCacheMetrics?: Subscription;
  private wsConnection?: Subscription;
  
  // WebSocket status
  isWebSocketConnected = false;
  lastWebSocketUpdate?: Date;
  
  constructor(
    private rulesService: RulesService,
    private orchestrationService: OrchestrationService,
    private webSocketService: WebSocketService
  ) {}
  
  ngOnInit(): void {
    this.loadAllData();
    this.loadCategories();
    this.connectWebSocket();
    this.loadInitialMetrics();
    // Only use polling as fallback if WebSocket fails
    setTimeout(() => {
      if (!this.isWebSocketConnected) {
        this.startPolling();
      }
    }, 3000);
  }
  
  ngOnDestroy(): void {
    this.statusPolling?.unsubscribe();
    this.metricsPolling?.unsubscribe();
    this.wsOrchestration?.unsubscribe();
    this.wsCacheMetrics?.unsubscribe();
    this.wsConnection?.unsubscribe();
    this.webSocketService.disconnect();
  }
  
  loadAllData(): void {
    this.loadRules();
    this.loadBestPractices();
    this.loadTemplates();
    this.loadStatistics();
  }
  
  loadRules(): void {
    this.loading.rules = true;
    this.errors.rules = '';
    
    this.rulesService.getRules(this.selectedCategory).subscribe({
      next: (response) => {
        if (response.success && response.rules) {
          this.rules = response.rules;
        }
        this.loading.rules = false;
      },
      error: (error) => {
        this.errors.rules = 'Failed to load rules';
        this.loading.rules = false;
        console.error('Error loading rules:', error);
      }
    });
  }
  
  loadBestPractices(): void {
    this.loading.practices = true;
    this.errors.practices = '';
    
    this.rulesService.getBestPractices(this.selectedCategory).subscribe({
      next: (response) => {
        if (response.success && response.practices) {
          this.bestPractices = response.practices;
          // Sort by priority
          this.bestPractices.sort((a, b) => {
            const priorityOrder = ['P0-CRITICAL', 'P1-HIGH', 'P2-MEDIUM', 'P3-LOW'];
            const aIndex = priorityOrder.indexOf(a.priority || 'P3-LOW');
            const bIndex = priorityOrder.indexOf(b.priority || 'P3-LOW');
            return aIndex - bIndex;
          });
        }
        this.loading.practices = false;
      },
      error: (error) => {
        this.errors.practices = 'Failed to load best practices';
        this.loading.practices = false;
        console.error('Error loading best practices:', error);
      }
    });
  }
  
  loadTemplates(): void {
    this.loading.templates = true;
    this.errors.templates = '';
    
    this.rulesService.getTemplates(this.selectedCategory).subscribe({
      next: (response) => {
        if (response.success && response.templates) {
          this.templates = response.templates;
        }
        this.loading.templates = false;
      },
      error: (error) => {
        this.errors.templates = 'Failed to load templates';
        this.loading.templates = false;
        console.error('Error loading templates:', error);
      }
    });
  }
  
  loadStatistics(): void {
    this.rulesService.getRulesStats().subscribe({
      next: (response) => {
        if (response.success && response.data) {
          this.rulesStats = response.data;
        }
      },
      error: (error) => console.error('Error loading rules stats:', error)
    });
    
    this.rulesService.getPracticesStats().subscribe({
      next: (response) => {
        if (response.success && response.data) {
          this.practicesStats = response.data;
        }
      },
      error: (error) => console.error('Error loading practices stats:', error)
    });
    
    this.rulesService.getTemplatesStats().subscribe({
      next: (response) => {
        if (response.success && response.data) {
          this.templatesStats = response.data;
        }
      },
      error: (error) => console.error('Error loading templates stats:', error)
    });
  }
  
  loadCategories(): void {
    this.rulesService.getCategories().subscribe({
      next: (categories) => {
        this.categories = categories;
      },
      error: (error) => console.error('Error loading categories:', error)
    });
  }
  
  onCategoryChange(): void {
    this.loadAllData();
  }
  
  getPriorityClass(priority: string | undefined): string {
    switch(priority) {
      case 'P0-CRITICAL': return 'priority-critical';
      case 'P1-HIGH': return 'priority-high';
      case 'P2-MEDIUM': return 'priority-medium';
      case 'P3-LOW': return 'priority-low';
      default: return '';
    }
  }
  
  getSeverityClass(severity: string): string {
    switch(severity) {
      case 'critical': return 'severity-critical';
      case 'high': return 'severity-high';
      case 'medium': return 'severity-medium';
      case 'low': return 'severity-low';
      default: return '';
    }
  }
  
  private startPolling(): void {
    // Poll orchestration status every 5 seconds
    this.statusPolling = interval(5000).pipe(
      switchMap(() => this.orchestrationService.getStatus())
    ).subscribe({
      next: (status) => {
        this.orchestrationStatus = status;
        this.updateProjectsFromStatus(status);
      },
      error: (error) => console.error('Error polling status:', error)
    });
    
    // Poll metrics every 10 seconds
    this.metricsPolling = interval(10000).pipe(
      switchMap(() => this.orchestrationService.getCacheMetrics())
    ).subscribe({
      next: (metrics) => {
        this.cacheMetrics = metrics;
      },
      error: (error) => console.error('Error polling cache metrics:', error)
    });
  }
  
  private loadInitialMetrics(): void {
    // Load health status
    this.orchestrationService.getHealth().subscribe({
      next: (health) => {
        this.healthStatus = health;
      },
      error: (error) => console.error('Error loading health:', error)
    });
    
    // Load orchestration status
    this.orchestrationService.getStatus().subscribe({
      next: (status) => {
        this.orchestrationStatus = status;
        this.updateProjectsFromStatus(status);
      },
      error: (error) => console.error('Error loading orchestration status:', error)
    });
    
    // Load cache metrics
    this.orchestrationService.getCacheMetrics().subscribe({
      next: (metrics) => {
        this.cacheMetrics = metrics;
      },
      error: (error) => console.error('Error loading cache metrics:', error)
    });
    
    // Load performance metrics
    this.orchestrationService.getPerformanceMetrics().subscribe({
      next: (metrics) => {
        this.performanceMetrics = metrics;
      },
      error: (error) => console.error('Error loading performance metrics:', error)
    });
  }
  
  private updateProjectsFromStatus(status: OrchestrationStatus): void {
    // Update project percentages based on task completion
    if (status.tasks && status.tasks.completed > 0) {
      const completionRate = (status.tasks.completed / 
        (status.tasks.completed + status.tasks.active + status.tasks.queued)) * 100;
      
      // Update first project as example of live data
      if (this.projects.length > 0) {
        this.projects[0].percentage = Math.round(completionRate);
        this.projects[0].status = `Active tasks: ${status.tasks.active}, Completed: ${status.tasks.completed}`;
      }
    }
    
    // Update updates array with real metrics
    if (this.cacheMetrics) {
      this.updates[0] = {
        icon: 'memory',
        title: `Cache Hit Rate: ${Math.round(this.cacheMetrics.hit_rate * 100)}%`,
        description: `${this.cacheMetrics.tokens_saved} tokens saved, ${this.cacheMetrics.cache_hits} cache hits`,
        time: 'Live',
        color: '#4ecdc4'
      };
    }
    
    if (status.performance) {
      this.updates[1] = {
        icon: 'speed',
        title: `Avg Response Time: ${Math.round(status.performance.average_response_time)}ms`,
        description: `Success rate: ${Math.round(status.performance.overall_success_rate * 100)}%`,
        time: 'Live',
        color: '#667eea'
      };
    }
  }
  
  private connectWebSocket(): void {
    // Connect to WebSocket
    this.webSocketService.connect();
    
    // Subscribe to connection status
    this.wsConnection = this.webSocketService.connectionStatus$.subscribe(connected => {
      this.isWebSocketConnected = connected;
      if (connected) {
        console.log('WebSocket connected - stopping polling');
        // Stop polling when WebSocket is connected
        this.statusPolling?.unsubscribe();
        this.metricsPolling?.unsubscribe();
      }
    });
    
    // Subscribe to orchestration updates
    this.wsOrchestration = this.webSocketService.orchestrationUpdates$.subscribe(update => {
      this.lastWebSocketUpdate = new Date();
      if (update.data) {
        this.orchestrationStatus = update.data;
        this.updateProjectsFromStatus(update.data);
      }
    });
    
    // Subscribe to cache metrics updates
    this.wsCacheMetrics = this.webSocketService.cacheMetricsUpdates$.subscribe(update => {
      this.lastWebSocketUpdate = new Date();
      if (update.data) {
        this.cacheMetrics = update.data;
        // Update the first update card with real-time cache info
        if (this.updates.length > 0) {
          this.updates[0] = {
            icon: 'memory',
            title: `Cache Hit Rate: ${Math.round((update.data.hit_rate || 0) * 100)}%`,
            description: `${update.data.tokens_saved || 0} tokens saved, ${update.data.cache_hits || 0} cache hits`,
            time: 'Real-time',
            color: '#4ecdc4'
          };
        }
      }
    });
    
    // Subscribe to task updates for live notifications
    this.webSocketService.taskUpdates$.subscribe(update => {
      console.log('Task update:', update);
      // Could show toast notifications for task completions
    });
    
    // Subscribe to persona decisions for governance visibility
    this.webSocketService.personaDecisions$.subscribe(decision => {
      console.log('Persona decision:', decision);
      // Could display persona decisions in a feed
    });
    
    // Subscribe to assumption validations
    this.webSocketService.assumptionValidations$.subscribe(validation => {
      console.log('Assumption validation:', validation);
      // Could show assumption challenges in real-time
    });
  }
}