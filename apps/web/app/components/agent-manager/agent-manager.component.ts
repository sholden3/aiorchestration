import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ConfigService } from '../../services/config.service';
import { WebSocketService } from '../../services/websocket.service';
import { Subscription } from 'rxjs';

interface Agent {
  id: string;
  type: string;
  name: string;
  status: string;
  terminal_session: string;
  created_at: string;
  last_activity: string;
  tasks_completed: number;
  current_task: string | null;
}

interface AgentStatus {
  total: number;
  max_agents: number;
  by_status: {
    ready: number;
    busy: number;
    idle: number;
    error: number;
  };
  agents: Agent[];
}

@Component({
  selector: 'app-agent-manager',
  templateUrl: './agent-manager.component.html',
  styleUrls: ['./agent-manager.component.scss']
})
export class AgentManagerComponent implements OnInit, OnDestroy {
  agents: Agent[] = [];
  maxAgents = 6;
  isLoading = false;
  error = '';
  
  // Agent types
  agentTypes = [
    { value: 'claude_assistant', label: 'Claude Assistant', icon: 'smart_toy' },
    { value: 'code_reviewer', label: 'Code Reviewer (Dr. Sarah)', icon: 'code' },
    { value: 'performance', label: 'Performance Optimizer (Marcus)', icon: 'speed' },
    { value: 'ux_analyzer', label: 'UX Analyzer (Emily)', icon: 'design_services' },
    { value: 'security', label: 'Security Auditor', icon: 'security' },
    { value: 'test_generator', label: 'Test Generator', icon: 'bug_report' }
  ];
  
  // Claude terminal
  claudeConnected = false;
  claudeMessages: Array<{type: string, content: string, timestamp: Date}> = [];
  claudeInput = '';
  
  // WebSocket subscriptions
  private wsSubscription?: Subscription;
  private agentSpawnSub?: Subscription;
  private claudeOutputSub?: Subscription;
  
  // Selected agent for terminal view
  selectedAgent: Agent | null = null;
  agentTerminals: Map<string, Array<string>> = new Map();
  
  constructor(
    private http: HttpClient,
    private config: ConfigService,
    private wsService: WebSocketService
  ) {}
  
  ngOnInit(): void {
    this.loadAgents();
    this.connectWebSocket();
    this.checkClaudeStatus();
  }
  
  ngOnDestroy(): void {
    this.wsSubscription?.unsubscribe();
    this.agentSpawnSub?.unsubscribe();
    this.claudeOutputSub?.unsubscribe();
  }
  
  private connectWebSocket(): void {
    // Connect to WebSocket for real-time updates
    this.wsService.connect();
    
    // Listen for agent spawn events
    this.wsSubscription = this.wsService.messages$.subscribe(message => {
      if (message.type === 'agent_spawned') {
        this.loadAgents();
      }
    });
    
    // Listen for Claude output
    this.claudeOutputSub = this.wsService.messages$.subscribe(message => {
      if (message.type === 'claude_output') {
        const data = message.data as any;
        this.claudeMessages.push({
          type: 'claude',
          content: data.output,
          timestamp: new Date(data.timestamp)
        });
      }
    });
  }
  
  loadAgents(): void {
    const apiUrl = this.config.getApiUrl();
    this.http.get<any>(`${apiUrl}/agents/status`).subscribe({
      next: (response) => {
        this.agents = response.agents || [];
        this.maxAgents = response.max_concurrent_agents || 6;
      },
      error: (error) => {
        this.error = 'Failed to load agents';
        console.error('Error loading agents:', error);
      }
    });
  }
  
  spawnAgent(type: string): void {
    if (this.agents.length >= this.maxAgents) {
      this.error = `Maximum agent limit (${this.maxAgents}) reached`;
      return;
    }
    
    this.isLoading = true;
    this.error = '';
    
    const apiUrl = this.config.getApiUrl();
    this.http.post<any>(`${apiUrl}/agents/spawn`, { type }).subscribe({
      next: (response) => {
        if (response.success) {
          this.loadAgents();
          // Initialize terminal for new agent
          const agent = response.agent;
          this.agentTerminals.set(agent.id, [`Agent ${agent.name} spawned at ${agent.created_at}`]);
        } else {
          this.error = response.error || 'Failed to spawn agent';
        }
        this.isLoading = false;
      },
      error: (error) => {
        this.error = 'Failed to spawn agent';
        this.isLoading = false;
        console.error('Error spawning agent:', error);
      }
    });
  }
  
  terminateAgent(agentId: string): void {
    const apiUrl = this.config.getApiUrl();
    this.http.delete<any>(`${apiUrl}/agents/${agentId}`).subscribe({
      next: () => {
        this.loadAgents();
        this.agentTerminals.delete(agentId);
        if (this.selectedAgent?.id === agentId) {
          this.selectedAgent = null;
        }
      },
      error: (error) => {
        this.error = 'Failed to terminate agent';
        console.error('Error terminating agent:', error);
      }
    });
  }
  
  selectAgent(agent: Agent): void {
    this.selectedAgent = agent;
    // Initialize terminal history if not exists
    if (!this.agentTerminals.has(agent.id)) {
      this.agentTerminals.set(agent.id, [`Terminal for ${agent.name}`]);
    }
  }
  
  sendToAgent(agentId: string, command: string): void {
    const apiUrl = this.config.getApiUrl();
    
    // Add command to terminal history immediately
    const history = this.agentTerminals.get(agentId) || [];
    history.push(`> ${command}`);
    this.agentTerminals.set(agentId, history);
    
    this.http.post<any>(`${apiUrl}/agents/${agentId}/execute`, { command }).subscribe({
      next: (response) => {
        const history = this.agentTerminals.get(agentId) || [];
        if (response.success && response.response) {
          // Show the actual response
          history.push(response.response);
        } else if (response.success) {
          // Fallback if no response provided
          history.push(`Command executed at ${response.timestamp || new Date().toISOString()}`);
        } else {
          // Show error
          history.push(`Error: ${response.error || 'Command failed'}`);
        }
        this.agentTerminals.set(agentId, history);
      },
      error: (error) => {
        const history = this.agentTerminals.get(agentId) || [];
        history.push(`Error: Failed to execute command - ${error.message || 'Unknown error'}`);
        this.agentTerminals.set(agentId, history);
        console.error('Error sending to agent:', error);
      }
    });
  }
  
  // Claude Terminal Methods
  connectClaude(): void {
    const apiUrl = this.config.getApiUrl();
    this.http.post<any>(`${apiUrl}/claude/connect`, {}).subscribe({
      next: (response) => {
        if (response.success) {
          this.claudeConnected = true;
          this.claudeMessages.push({
            type: 'system',
            content: response.message,
            timestamp: new Date()
          });
        }
      },
      error: (error) => {
        this.error = 'Failed to connect to Claude';
        console.error('Error connecting to Claude:', error);
      }
    });
  }
  
  sendToClaude(): void {
    if (!this.claudeInput.trim()) return;
    
    const message = this.claudeInput;
    this.claudeInput = '';
    
    // Add user message to chat
    this.claudeMessages.push({
      type: 'user',
      content: message,
      timestamp: new Date()
    });
    
    const apiUrl = this.config.getApiUrl();
    this.http.post<any>(`${apiUrl}/claude/send`, { message }).subscribe({
      next: (response) => {
        if (!response.success) {
          this.claudeMessages.push({
            type: 'error',
            content: response.error || 'Failed to send message',
            timestamp: new Date()
          });
        }
      },
      error: (error) => {
        console.error('Error sending to Claude:', error);
      }
    });
  }
  
  disconnectClaude(): void {
    const apiUrl = this.config.getApiUrl();
    this.http.post<any>(`${apiUrl}/claude/disconnect`, {}).subscribe({
      next: () => {
        this.claudeConnected = false;
        this.claudeMessages = [];
      },
      error: (error) => {
        console.error('Error disconnecting Claude:', error);
      }
    });
  }
  
  private checkClaudeStatus(): void {
    const apiUrl = this.config.getApiUrl();
    this.http.get<any>(`${apiUrl}/claude/status`).subscribe({
      next: (response) => {
        this.claudeConnected = response.is_connected;
      },
      error: (error) => {
        console.error('Error checking Claude status:', error);
      }
    });
  }
  
  getStatusColor(status: string): string {
    switch (status) {
      case 'ready': return 'primary';
      case 'busy': return 'warn';
      case 'idle': return 'accent';
      case 'error': return 'warn';
      default: return '';
    }
  }
  
  getStatusIcon(status: string): string {
    switch (status) {
      case 'ready': return 'check_circle';
      case 'busy': return 'pending';
      case 'idle': return 'schedule';
      case 'error': return 'error';
      default: return 'help';
    }
  }
}